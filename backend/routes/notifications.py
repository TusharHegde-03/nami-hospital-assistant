"""
Notification Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from models.notification import Notification
from utils.db import get_collection

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
async def list_notifications(
    recipient: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """List all notifications"""
    collection = get_collection("notifications")
    
    query = {}
    if recipient:
        query["recipient"] = {"$regex": recipient, "$options": "i"}
    if status:
        query["status"] = status
    
    cursor = collection.find(query).sort("timestamp", -1).limit(limit)
    notifications = await cursor.to_list(length=limit)
    
    for notif in notifications:
        notif["_id"] = str(notif["_id"])
    
    return notifications

@router.post("")
async def create_notification(notification: Notification):
    """Create a new notification"""
    collection = get_collection("notifications")
    
    notif_dict = notification.model_dump()
    result = await collection.insert_one(notif_dict)
    
    notif_dict["_id"] = str(result.inserted_id)
    return notif_dict


@router.patch("/{notification_id}/read")
async def mark_as_read(notification_id: str):
    """Mark notification as read"""
    from bson import ObjectId
    collection = get_collection("notifications")
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"status": "read", "read_at": datetime.utcnow()}}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid notification ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}