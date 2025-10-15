# appointment.py - placeholder
"""Appointment Data Model"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Appointment(BaseModel):
    doctor_name: str
    patient_name: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    reason: Optional[str] = "General consultation"
    status: str = "scheduled"  # scheduled, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)