"""
Public diagnostics endpoints for ClosetGPT.
Provides public health and status information.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
import time
import os

router = APIRouter()

class ServiceStatus(BaseModel):
    """Service status information."""
    service: str
    status: str
    timestamp: float
    details: Dict[str, Any]

@(router.get("/") if router else None)
async def get_diagnostics_status():
    """Get diagnostics service status."""
    return {
        "status": "operational",
        "service": "public_diagnostics",
        "endpoints": ["/health", "/status", "/info"],
        "timestamp": time.time()
    }

@(router.get("/health") if router else None)
async def public_health_check():
    """Public health check endpoint."""
    return ServiceStatus(
        service="public_diagnostics",
        status="healthy",
        timestamp=time.time(),
        details={
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "production"),
            "uptime": time.time()
        }
    )

@(router.get("/status") if router else None)
async def get_public_status():
    """Get public service status."""
    return {
        "status": "operational",
        "services": {
            "api": "healthy",
            "weather": "healthy",
            "wardrobe": "healthy",
            "authentication": "healthy"
        },
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@(router.get("/info") if router else None)
async def get_service_info():
    """Get service information."""
    return {
        "name": "ClosetGPT API",
        "description": "AI-powered wardrobe management and outfit generation API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "features": [
            "weather integration",
            "wardrobe management",
            "outfit generation",
            "style analysis",
            "performance monitoring"
        ],
        "timestamp": time.time()
    } 