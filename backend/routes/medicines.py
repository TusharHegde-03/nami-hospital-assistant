# medicines.py - placeholder
"""
Medicine Management Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from models.medicine import Medicine
from utils.db import get_collection

router = APIRouter(prefix="/medicines", tags=["Medicines"])


@router.get("")
async def list_medicines(
    patient_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """List all medicine records with optional filters"""
    collection = get_collection("medicines")
    
    query = {}
    if patient_name:
        query["patient_name"] = {"$regex": patient_name, "$options": "i"}
    if status:
        query["status"] = status
    
    cursor = collection.find(query).sort("assigned_at", -1).limit(limit)
    medicines = await cursor.to_list(length=limit)
    
    for med in medicines:
        med["_id"] = str(med["_id"])
    
    return medicines


@router.get("/{medicine_id}")
async def get_medicine(medicine_id: str):
    """Get a specific medicine record by ID"""
    from bson import ObjectId
    collection = get_collection("medicines")
    
    try:
        medicine = await collection.find_one({"_id": ObjectId(medicine_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid medicine ID")
    
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine record not found")
    
    medicine["_id"] = str(medicine["_id"])
    return medicine


@router.post("/assign")
async def assign_medicine(medicine: Medicine):
    """Assign medicine to a patient"""
    collection = get_collection("medicines")
    
    med_dict = medicine.model_dump()
    result = await collection.insert_one(med_dict)
    
    med_dict["_id"] = str(result.inserted_id)
    return med_dict


@router.post("/deliver")
async def mark_delivered(medicine_id: str):
    """Mark medicine as delivered"""
    from bson import ObjectId
    collection = get_collection("medicines")
    
    update_data = {
        "status": "delivered",
        "delivered_at": datetime.utcnow()
    }
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(medicine_id)},
            {"$set": update_data}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid medicine ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Medicine record not found")
    
    return {"message": "Medicine marked as delivered"}


@router.patch("/{medicine_id}")
async def update_medicine(medicine_id: str, update_data: dict):
    """Update medicine record"""
    from bson import ObjectId
    collection = get_collection("medicines")
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(medicine_id)},
            {"$set": update_data}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid medicine ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Medicine record not found")
    
    return {"message": "Medicine record updated successfully"}


@router.delete("/{medicine_id}")
async def delete_medicine(medicine_id: str):
    """Delete a medicine record"""
    from bson import ObjectId
    collection = get_collection("medicines")
    
    try:
        result = await collection.delete_one({"_id": ObjectId(medicine_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid medicine ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Medicine record not found")
    
    return {"message": "Medicine record deleted successfully"}