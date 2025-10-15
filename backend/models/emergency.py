# emergency.py - placeholder
"""Emergency Alert Data Model"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class EmergencyAlert(BaseModel):
    alert_type: str  # code_blue, code_red, fire, evacuation
    location: str
    details: Optional[str] = None
    status: str = "active"  # active, resolved, false_alarm
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    responders: Optional[list] = Field(default_factory=list)