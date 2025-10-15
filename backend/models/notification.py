# notification.py - placeholder
"""Notification Data Model"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Notification(BaseModel):
    recipient: str  # staff name or department
    message: str
    priority: str = "normal"  # low, normal, high, urgent
    status: str = "sent"  # sent, read, archived
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None