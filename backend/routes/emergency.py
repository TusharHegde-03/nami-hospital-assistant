# emergency.py - placeholder
# backend/routes/emergency.py
"""
Emergency Alert Routes
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime

from models.emergency import EmergencyAlert
from utils.db import get_collection

router = APIRouter(prefix="/emergency", tags=["Emergency"])


@router.get("")
async def list_emergency_alerts(status: str = None):
    """List all emergency alerts"""
    collection = get_collection("emergency_alerts")
    
    query = {}
    if status:
        query["status"] = status
    
    cursor = collection.find(query).sort("triggered_at", -1).limit(50)
    alerts = await cursor.to_list(length=50)
    
    for alert in alerts:
        alert["_id"] = str(alert["_id"])
    
    return alerts


@router.post("")
async def trigger_emergency(alert: EmergencyAlert):
    """Trigger an emergency alert"""
    collection = get_collection("emergency_alerts")
    
    alert_dict = alert.model_dump()
    result = await collection.insert_one(alert_dict)
    
    # Also create notifications for staff
    notifications_collection = get_collection("notifications")
    await notifications_collection.insert_one({
        "recipient": "Emergency Team",
        "message": f"EMERGENCY: {alert.alert_type.upper()} at {alert.location}",
        "priority": "urgent",
        "status": "sent",
        "timestamp": datetime.utcnow()
    })
    
    alert_dict["_id"] = str(result.inserted_id)
    return alert_dict


@router.patch("/{alert_id}/resolve")
async def resolve_emergency(alert_id: str):
    """Resolve an emergency alert"""
    from bson import ObjectId
    collection = get_collection("emergency_alerts")
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": {"status": "resolved", "resolved_at": datetime.utcnow()}}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid alert ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Emergency resolved"}