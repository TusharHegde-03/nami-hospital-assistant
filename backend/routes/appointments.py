# appointments.py - placeholder
"""
Appointment Management Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from models.appointment import Appointment
from utils.db import get_collection

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("")
async def list_appointments(
    doctor_name: Optional[str] = Query(None),
    patient_name: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """List all appointments with optional filters"""
    collection = get_collection("appointments")
    
    query = {}
    if doctor_name:
        query["doctor_name"] = {"$regex": doctor_name, "$options": "i"}
    if patient_name:
        query["patient_name"] = {"$regex": patient_name, "$options": "i"}
    if date:
        query["date"] = date
    if status:
        query["status"] = status
    
    cursor = collection.find(query).sort("date", 1).sort("time", 1).limit(limit)
    appointments = await cursor.to_list(length=limit)
    
    for appt in appointments:
        appt["_id"] = str(appt["_id"])
    
    return appointments


@router.get("/{appointment_id}")
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID"""
    from bson import ObjectId
    collection = get_collection("appointments")
    
    try:
        appointment = await collection.find_one({"_id": ObjectId(appointment_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid appointment ID")
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment["_id"] = str(appointment["_id"])
    return appointment


@router.post("")
async def create_appointment(appointment: Appointment):
    """Create a new appointment"""
    collection = get_collection("appointments")
    
    # Check for conflicts
    existing = await collection.find_one({
        "doctor_name": appointment.doctor_name,
        "date": appointment.date,
        "time": appointment.time,
        "status": {"$ne": "cancelled"}
    })
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Dr. {appointment.doctor_name} already has an appointment at {appointment.time} on {appointment.date}"
        )
    
    appt_dict = appointment.model_dump()
    result = await collection.insert_one(appt_dict)
    
    appt_dict["_id"] = str(result.inserted_id)
    return appt_dict


@router.patch("/{appointment_id}")
async def update_appointment(appointment_id: str, update_data: dict):
    """Update appointment details"""
    from bson import ObjectId
    collection = get_collection("appointments")
    
    update_data["updated_at"] = datetime.utcnow()
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(appointment_id)},
            {"$set": update_data}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid appointment ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {"message": "Appointment updated successfully"}


@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: str):
    """Delete an appointment"""
    from bson import ObjectId
    collection = get_collection("appointments")
    
    try:
        result = await collection.delete_one({"_id": ObjectId(appointment_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid appointment ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {"message": "Appointment deleted successfully"}