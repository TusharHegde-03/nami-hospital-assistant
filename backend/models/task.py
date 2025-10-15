# task.py - placeholder
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Task(BaseModel):
    title: str
    description: str
    assigned_to: Optional[str] = None
    priority: str = "medium"  # low, medium, high, urgent
    status: str = "pending"  # pending, in_progress, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None