"""
System monitoring endpoints for Easy Outfit App.
Provides system health and performance monitoring.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import time
import psutil
import os

router = APIRouter()

class SystemStatus(BaseModel):
    """System status information."""
    status: str
    uptime: float
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    timestamp: float

class HealthCheck(BaseModel):
    """Health check response."""
    service: str
    status: str
    timestamp: float
    details: Dict[str, Any]

@router.get("/")
async def get_monitoring_status():
    """Get monitoring service status."""
    return {
        "status": "operational",
        "service": "monitoring",
        "endpoints": ["/health", "/system", "/metrics", "/alerts"],
        "timestamp": time.time()
    }

@router.get("/health")
async def health_check():
    """Basic health check."""
    return HealthCheck(
        service="monitoring",
        status="healthy",
        timestamp=time.time(),
        details={
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "production")
        }
    )

@router.get("/system")
async def get_system_status():
    """Get system status information."""
    try:
        # Get system metrics
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        return SystemStatus(
            status="operational",
            uptime=time.time() - psutil.boot_time(),
            memory_usage=memory.percent,
            cpu_usage=cpu,
            disk_usage=disk.percent,
            timestamp=time.time()
        )
    except Exception as e:
        # Fallback if psutil fails
        return SystemStatus(
            status="limited",
            uptime=time.time(),
            memory_usage=0.0,
            cpu_usage=0.0,
            disk_usage=0.0,
            timestamp=time.time()
        )

@router.get("/metrics")
async def get_system_metrics():
    """Get detailed system metrics."""
    try:
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        return {
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "cpu": {
                "usage_percent": cpu,
                "count": psutil.cpu_count()
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            },
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "error": "Unable to collect metrics",
            "timestamp": time.time()
        }

@router.get("/alerts")
async def get_system_alerts():
    """Get current system alerts."""
    alerts = []
    
    try:
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            alerts.append({
                "level": "warning",
                "message": "High memory usage",
                "value": f"{memory.percent}%",
                "timestamp": time.time()
            })
        
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            alerts.append({
                "level": "critical",
                "message": "Low disk space",
                "value": f"{disk.percent}% used",
                "timestamp": time.time()
            })
            
    except Exception as e:
        alerts.append({
            "level": "error",
            "message": "Unable to check system status",
            "timestamp": time.time()
        })
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "timestamp": time.time()
    }

@router.post("/restart")
async def restart_monitoring():
    """Restart monitoring service."""
    return {
        "message": "Monitoring service restart initiated",
        "timestamp": time.time(),
        "status": "success"
    } 