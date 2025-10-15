# patients.py - placeholder
"""
Patient Management Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from models.patient import Patient
from utils.db import get_collection

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("")
async def list_patients(
    room_number: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """List all patients with optional filters"""
    collection = get_collection("patients")
    
    query = {}
    if room_number:
        query["room_number"] = room_number
    if status:
        query["status"] = status
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    
    cursor = collection.find(query).limit(limit)
    patients = await cursor.to_list(length=limit)
    
    for patient in patients:
        patient["_id"] = str(patient["_id"])
    
    return patients


@router.get("/{patient_id}")
async def get_patient(patient_id: str):
    """Get a specific patient by ID"""
    from bson import ObjectId
    collection = get_collection("patients")
    
    try:
        patient = await collection.find_one({"_id": ObjectId(patient_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid patient ID")
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient["_id"] = str(patient["_id"])
    return patient


@router.post("")
async def create_patient(patient: Patient):
    """Create a new patient record"""
    collection = get_collection("patients")
    
    patient_dict = patient.model_dump()
    result = await collection.insert_one(patient_dict)
    
    patient_dict["_id"] = str(result.inserted_id)
    return patient_dict


@router.patch("/{patient_id}")
async def update_patient(patient_id: str, update_data: dict):
    """Update patient information"""
    from bson import ObjectId
    collection = get_collection("patients")
    
    update_data["updated_at"] = datetime.utcnow()
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(patient_id)},
            {"$set": update_data}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid patient ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {"message": "Patient updated successfully"}


@router.delete("/{patient_id}")
async def delete_patient(patient_id: str):
    """Delete a patient record"""
    from bson import ObjectId
    collection = get_collection("patients")
    
    try:
        result = await collection.delete_one({"_id": ObjectId(patient_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid patient ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {"message": "Patient deleted successfully"}