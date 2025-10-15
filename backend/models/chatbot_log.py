# chatbot_log.py - placeholder
"""Chatbot Log Data Model"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ChatbotLog(BaseModel):
    query: str
    intent: str
    action: str
    target: str
    response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
