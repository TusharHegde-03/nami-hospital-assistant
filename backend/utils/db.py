# db.py - placeholder
"""
MongoDB Database Connection and Utilities
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Database configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "nami_hospital")

# Global database client
_client: Optional[AsyncIOMotorClient] = None
_db = None


def get_database():
    """Get database instance"""
    global _client, _db
    
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URI)
        _db = _client[MONGO_DB_NAME]
        logger.info(f"Connected to MongoDB: {MONGO_DB_NAME}")
    
    return _db


def get_collection(collection_name: str):
    """Get a specific collection"""
    db = get_database()
    return db[collection_name]


async def init_database():
    """Initialize database with indexes and constraints"""
    db = get_database()
    
    # Create indexes for better performance
    await db.doctors.create_index("name")
    await db.doctors.create_index("specialization")
    await db.patients.create_index("name")
    await db.patients.create_index("room_number")
    await db.appointments.create_index([("date", 1), ("time", 1)])
    await db.medicines.create_index("patient_name")
    await db.medicines.create_index("status")
    await db.robot_commands.create_index([("status", 1), ("timestamp", -1)])
    await db.tasks.create_index("status")
    await db.chatbot_logs.create_index("timestamp")
    await db.emergency_alerts.create_index([("status", 1), ("triggered_at", -1)])
    
    logger.info("Database indexes created successfully")


async def close_database():
    """Close database connection"""
    global _client
    if _client:
        _client.close()
        logger.info("Database connection closed")