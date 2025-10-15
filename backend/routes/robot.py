# robot.py - placeholder
"""
Robot Command & Control Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from models.robot_command import RobotCommand
from utils.db import get_collection

router = APIRouter(prefix="/robot", tags=["Robot"])


@router.get("/status")
async def get_robot_status():
    """Get current robot status"""
    # This would normally query the actual robot
    # For now, return simulated status
    commands_collection = get_collection("robot_commands")
    
    # Get latest command
    latest_command = await commands_collection.find_one(
        {},
        sort=[("timestamp", -1)]
    )
    
    status = {
        "status": "idle",
        "location": "Lobby",
        "battery": 85,
        "current_task": None,
        "last_update": datetime.utcnow().isoformat()
    }
    
    if latest_command and latest_command.get("status") == "executing":
        status["status"] = "busy"
        status["current_task"] = latest_command.get("action")
        status["location"] = latest_command.get("target")
    
    return status


@router.get("/commands")
async def list_robot_commands(
    status: Optional[str] = Query(None),
    intent: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """List robot commands"""
    collection = get_collection("robot_commands")
    
    query = {}
    if status:
        query["status"] = status
    if intent:
        query["intent"] = intent
    
    cursor = collection.find(query).sort("timestamp", -1).limit(limit)
    commands = await cursor.to_list(length=limit)
    
    for cmd in commands:
        cmd["_id"] = str(cmd["_id"])
    
    return commands


@router.get("/commands/pending")
async def get_pending_commands():
    """Get all pending robot commands (for robot client to poll)"""
    collection = get_collection("robot_commands")
    
    cursor = collection.find({"status": {"$in": ["pending", "confirmed"]}}).sort("timestamp", 1)
    commands = await cursor.to_list(length=100)
    
    for cmd in commands:
        cmd["_id"] = str(cmd["_id"])
    
    return commands


@router.post("/commands")
async def create_robot_command(command: RobotCommand):
    """Create a new robot command"""
    collection = get_collection("robot_commands")
    
    cmd_dict = command.model_dump()
    result = await collection.insert_one(cmd_dict)
    
    cmd_dict["_id"] = str(result.inserted_id)
    return cmd_dict


@router.patch("/commands/{command_id}")
async def update_robot_command(command_id: str, update_data: dict):
    """Update robot command status"""
    from bson import ObjectId
    collection = get_collection("robot_commands")
    
    # Add completed timestamp if status is completed
    if update_data.get("status") == "completed":
        update_data["completed_at"] = datetime.utcnow()
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(command_id)},
            {"$set": update_data}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid command ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Command not found")
    
    return {"message": "Command updated successfully"}


@router.post("/commands/{command_id}/execute")
async def execute_command(command_id: str):
    """Mark command as executing"""
    from bson import ObjectId
    collection = get_collection("robot_commands")
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(command_id)},
            {"$set": {"status": "executing"}}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid command ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Command not found")
    
    return {"message": "Command execution started"}


@router.post("/commands/{command_id}/complete")
async def complete_command(command_id: str, success: bool = True, error_message: Optional[str] = None):
    """Mark command as completed or failed"""
    from bson import ObjectId
    collection = get_collection("robot_commands")
    
    update_data = {
        "status": "completed" if success else "failed",
        "completed_at": datetime.utcnow()
    }
    
    if error_message:
        update_data["error_message"] = error_message
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(command_id)},
            {"$set": update_data}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid command ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Command not found")
    
    return {"message": "Command completed"}


@router.delete("/commands/{command_id}")
async def delete_robot_command(command_id: str):
    """Delete a robot command"""
    from bson import ObjectId
    collection = get_collection("robot_commands")
    
    try:
        result = await collection.delete_one({"_id": ObjectId(command_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid command ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Command not found")
    
    return {"message": "Command deleted successfully"}