# medicine.py - placeholder
"""Medicine Data Model"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Medicine(BaseModel):
    patient_name: str
    medicine_name: str
    dosage: str
    frequency: str
    room_number: Optional[str] = None
    status: str = "pending"  # pending, assigned, delivered
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None
