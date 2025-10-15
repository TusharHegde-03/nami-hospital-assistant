"""
Nami Hospital Assistant - Backend Server
FastAPI + MongoDB
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import routes
from routes import doctors, patients, appointments, medicines, robot, tasks
from routes.queries import router as queries_router
from routes.emergency import router as emergency_router  
from routes.confirm import router as confirm_router
from routes.notifications import router as notifications_router
from routes.logs import router as logs_router

# Import database utilities
from utils.db import init_database, close_database

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown"""
    # Startup
    logger.info("Starting Nami Hospital Assistant Backend...")
    await init_database()
    logger.info("✅ Database initialized and ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_database()
    logger.info("✅ Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="Nami Hospital Assistant API",
    description="Backend API for Nami, the AI-powered hospital assistant robot",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "Nami Hospital Assistant API",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "doctors": "active",
            "patients": "active",
            "appointments": "active",
            "medicines": "active",
            "robot": "active",
            "tasks": "active"
        }
    }


# LiveKit token generation endpoint
@app.get("/livekit/token")
async def generate_livekit_token(room: str, participant: str):
    """Generate LiveKit access token"""
    from livekit import api
    
    token = api.AccessToken(
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET")
    )
    
    token.with_identity(participant).with_name(participant).with_grants(
        api.VideoGrants(
            room_join=True,
            room=room,
        )
    )
    
    return {"token": token.to_jwt()}


# Include all route modules
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(medicines.router)
app.include_router(robot.router)
app.include_router(tasks.router)
app.include_router(queries_router)
app.include_router(emergency_router)
app.include_router(confirm_router)
app.include_router(notifications_router)
app.include_router(logs_router)


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 5000))
    
    logger.info(f"🚀 Starting server on http://localhost:{port}")
    logger.info(f"📚 API documentation available at http://localhost:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )