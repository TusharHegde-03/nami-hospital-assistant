# robot_command.py - placeholder
"""Robot Command Data Model"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class RobotCommand(BaseModel):
    intent: str  # navigation, delivery, medicine_delivery, robot_control
    action: str  # navigate, deliver, stop, resume, etc.
    target: str  # location, room number, etc.
    coordinates: Optional[Dict[str, float]] = None  # {"x": 10.5, "y": 20.3}
    details: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, confirmed, executing, completed, failed
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None