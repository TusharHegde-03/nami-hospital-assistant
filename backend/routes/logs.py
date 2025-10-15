"""
Chatbot Logs Routes
"""

from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from models.chatbot_log import ChatbotLog
from utils.db import get_collection

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("")
async def list_logs(
    intent: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500)
):
    """List chatbot logs"""
    collection = get_collection("chatbot_logs")
    
    query = {}
    if intent:
        query["intent"] = intent
    
    cursor = collection.find(query).sort("timestamp", -1).limit(limit)
    logs = await cursor.to_list(length=limit)
    
    for log in logs:
        log["_id"] = str(log["_id"])
    
    return logs


@router.post("")
async def create_log(log: ChatbotLog):
    """Create a new chatbot log entry"""
    collection = get_collection("chatbot_logs")
    
    log_dict = log.model_dump()
    result = await collection.insert_one(log_dict)
    
    log_dict["_id"] = str(result.inserted_id)
    return log_dict