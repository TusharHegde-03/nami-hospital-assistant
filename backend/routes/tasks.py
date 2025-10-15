# tasks.py - placeholder
"""
Task Management Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from models.task import Task
from utils.db import get_collection

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("")
async def list_tasks(
    status: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """List all tasks with optional filters"""
    collection = get_collection("tasks")
    
    query = {}
    if status:
        query["status"] = status
    if assigned_to:
        query["assigned_to"] = {"$regex": assigned_to, "$options": "i"}
    if priority:
        query["priority"] = priority
    
    cursor = collection.find(query).sort("created_at", -1).limit(limit)
    tasks = await cursor.to_list(length=limit)
    
    for task in tasks:
        task["_id"] = str(task["_id"])
    
    return tasks


@router.get("/{task_id}")
async def get_task(task_id: str):
    """Get a specific task by ID"""
    from bson import ObjectId
    collection = get_collection("tasks")
    
    try:
        task = await collection.find_one({"_id": ObjectId(task_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task["_id"] = str(task["_id"])
    return task


@router.post("")
async def create_task(task: Task):
    """Create a new task"""
    collection = get_collection("tasks")
    
    task_dict = task.model_dump()
    result = await collection.insert_one(task_dict)
    
    task_dict["_id"] = str(result.inserted_id)
    return task_dict


@router.patch("/{task_id}")
async def update_task(task_id: str, update_data: dict):
    """Update task information"""
    from bson import ObjectId
    collection = get_collection("tasks")
    
    update_data["updated_at"] = datetime.utcnow()
    
    try:
        result = await collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task updated successfully"}


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    from bson import ObjectId
    collection = get_collection("tasks")
    
    try:
        result = await collection.delete_one({"_id": ObjectId(task_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid task ID")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}