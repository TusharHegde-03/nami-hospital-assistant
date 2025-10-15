# confirm.py - placeholder
# backend/routes/confirm.py
"""
Confirmation Routes - Confirm or cancel pending items
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

from utils.db import get_collection

router = APIRouter(prefix="/confirm", tags=["Confirmation"])


class ConfirmRequest(BaseModel):
    item_type: str  # appointment, robot_command, task, medicine
    item_id: str
    action: str  # confirm or cancel


@router.post("")
async def confirm_action(request: ConfirmRequest):
    """Confirm or cancel a pending action"""
    
    collection_map = {
        "appointment": "appointments",
        "robot_command": "robot_commands",
        "task": "tasks",
        "medicine": "medicines"
    }
    
    if request.item_type not in collection_map:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    collection = get_collection(collection_map[request.item_type])
    
    try:
        item_id = ObjectId(request.item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    
    if request.action == "confirm":
        update_data = {"status": "confirmed"}
    elif request.action == "cancel":
        update_data = {"status": "cancelled"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await collection.update_one(
        {"_id": item_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": f"{request.item_type} {request.action}ed successfully"}


