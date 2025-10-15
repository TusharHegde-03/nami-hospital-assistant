# queries.py - placeholder
"""
Query Handling Routes - Uses Gemini for general questions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from datetime import datetime

from utils.db import get_collection

router = APIRouter(prefix="/queries", tags=["Queries"])

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class QueryRequest(BaseModel):
    query: str


@router.post("")
async def handle_query(request: QueryRequest):
    """Handle general queries using Gemini AI"""
    
    # Hospital-specific context
    hospital_context = """
    You are answering questions for City General Hospital in Karnataka, India.
    
    Hospital Information:
    - Visiting Hours: 10 AM to 8 PM daily
    - ICU Visiting: 15 minutes per hour, immediate family only
    - Emergency: 24/7 available
    - Pharmacy: Open 24/7
    - Cafeteria: 7 AM to 10 PM
    - Location: New Delhi, India
    
    Answer questions clearly and professionally. Keep responses concise (2-3 sentences).
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(
            f"{hospital_context}\n\nQuestion: {request.query}\n\nAnswer:"
        )
        
        answer = response.text
        
        # Log the query
        logs_collection = get_collection("chatbot_logs")
        await logs_collection.insert_one({
            "query": request.query,
            "intent": "query",
            "action": "answer",
            "target": "general",
            "response": answer,
            "timestamp": datetime.utcnow()
        })
        
        return {"answer": answer}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/parse")
async def parse_intent(request: QueryRequest):
    """Parse intent from natural language"""
    from agent.prompts import INTENT_PARSER_PROMPT
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = INTENT_PARSER_PROMPT.format(query=request.query)
        
        response = model.generate_content(prompt)
        
        import json
        intent_data = json.loads(response.text)
        
        return intent_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent parsing failed: {str(e)}")