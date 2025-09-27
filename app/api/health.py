from fastapi import APIRouter
from datetime import datetime
import psutil
import os
from app.models.schemas import HealthCheck

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthCheck,
    summary="Health check",
    description="Check if the API service is healthy and running"
)
async def health_check():
    """Basic health check endpoint"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )

@router.get(
    "/status",
    summary="Service status",
    description="Get detailed status information about the service"
)
async def service_status():
    """Detailed service status information"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "status": "running",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "memory_usage_mb": round(memory_info.rss / 1024 / 1024, 2),
        "cpu_percent": process.cpu_percent(),
        "uptime_seconds": round(process.create_time()),
    }