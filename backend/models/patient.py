"""
Patient Data Model
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Patient(BaseModel):
    """Patient model"""
    name: str
    age: int
    gender: str
    room_number: str
    blood_type: Optional[str] = None
    status: str = "admitted"  # admitted, discharged, critical
    admission_date: datetime = Field(default_factory=datetime.utcnow)
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    allergies: Optional[List[str]] = Field(default_factory=list)
    medical_conditions: Optional[List[str]] = Field(default_factory=list)
    assigned_doctor: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "age": 45,
                "gender": "Male",
                "room_number": "302",
                "blood_type": "O+",
                "status": "admitted",
                "phone": "+91-98765-12345",
                "allergies": ["Penicillin"],
                "medical_conditions": ["Diabetes", "Hypertension"],
                "assigned_doctor": "Dr. Sarah Mehat"
            }
        }