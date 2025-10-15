# doctor.py - placeholder
"""
Doctor Data Model
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Doctor(BaseModel):
    """Doctor model"""
    name: str
    specialization: str
    room_number: str
    phone: Optional[str] = None
    email: Optional[str] = None
    available: bool = True
    schedule: Optional[List[str]] = Field(default_factory=list)  # e.g., ["Mon", "Wed", "Fri"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Dr. Sarah Mehat",
                "specialization": "Cardiology",
                "room_number": "305",
                "phone": "+91-98765-43210",
                "email": "s.mehat@hospital.com",
                "available": True,
                "schedule": ["Mon", "Tue", "Wed", "Thu", "Fri"]
            }
        }