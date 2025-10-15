# doctors.py - placeholder
"""
Doctor Management Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from models.doctor import Doctor
from utils.db import get_collection

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("")
async def list_doctors(
    specialization: Optional[str] = Query(None),
    available: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """List all doctors with optional filters"""
    collection = get_collection("doctors")
    
    query = {}
    if specialization:
        query["specialization"] = {"$regex": specialization, "$options": "i"}
    if available == "true":
        query["available"] = True
    
    cursor = collection.find(query).limit(limit)
    doctors = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for doc in doctors:
        doc["_id"] = str(doc["_id"])
    
    return doctors


@router.get("/{doctor_id}")
async def get_doctor(doctor_id: str):
    """Get a specific doctor by ID"""
    from bson import ObjectId
    collection = get_collection("doctors")
    
    try:
        doctor = await collection.find_one({"_id": ObjectId(doctor_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid doctor ID")
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    doctor["_id"] = str(doctor["_id"])
    return doctor


@router.post("")
async def create_doctor(doctor: Doctor):
    """Create a new doctor"""
    collection = get_collection("doctors")
    
    doctor_dict = doctor.model_dump()
    result = await collection.insert_one(doctor_dict)
    
    doctor_dict["_id"] = str(result.inserted_id)
    return doctor_dict


@router.patch("/{doctor_id}")
async def update_doctor(doctor_id: str, update_data: dict):
    """Update doctor information"""
    from bson import ObjectId
    collection = get_collection("doctors")
    
    update_data["updated_at"] = datetime.utcnow()
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(doctor_id)},
            {"$set": update_data}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid doctor ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return {"message": "Doctor updated successfully"}


@router.delete("/{doctor_id}")
async def delete_doctor(doctor_id: str):
    """Delete a doctor"""
    from bson import ObjectId
    collection = get_collection("doctors")
    
    try:
        result = await collection.delete_one({"_id": ObjectId(doctor_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid doctor ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return {"message": "Doctor deleted successfully"}