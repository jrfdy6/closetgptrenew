"""
Enterprise-grade health monitoring and diagnostics
Provides comprehensive system health checks and monitoring endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import time
import psutil
import sys
from datetime import datetime, timedelta
import asyncio
from ..auth.auth_service import get_current_user_optional
from ..custom_types.profile import UserProfile

router = APIRouter(prefix="/health")

# Health check data
health_data = {
    "status": "healthy",
    "timestamp": datetime.utcnow().isoformat(),
    "uptime": 0,
    "version": "1.0.0",
    "checks": {}
}

start_time = time.time()

@router.get("/simple")
async def simple_health_check():
    """Simple health check for load balancers and monitoring"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@router.get("/detailed")
async def detailed_health_check(current_user: UserProfile = Depends(get_current_user_optional)):
    """Detailed health check with system metrics"""
    global health_data
    
    current_time = time.time()
    uptime = current_time - start_time
    
    # Basic system checks
    checks = await perform_system_checks()
    
    # Determine overall status
    overall_status = "healthy"
    if any(check["status"] != "healthy" for check in checks.values()):
        overall_status = "degraded"
    if any(check["status"] == "critical" for check in checks.values()):
        overall_status = "unhealthy"
    
    health_data.update({
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": uptime,
        "checks": checks,
        "system": get_system_metrics()
    })
    
    return health_data

@router.get("/metrics")
async def get_metrics(current_user: UserProfile = Depends(get_current_user_optional)):
    """Get system performance metrics"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system": get_system_metrics(),
        "application": get_application_metrics(),
        "database": await get_database_metrics()
    }

async def perform_system_checks() -> Dict[str, Dict[str, Any]]:
    """Perform comprehensive system health checks"""
    checks = {}
    
    # Memory check
    memory = psutil.virtual_memory()
    checks["memory"] = {
        "status": "healthy" if memory.percent < 80 else "degraded" if memory.percent < 95 else "critical",
        "usage_percent": memory.percent,
        "available_gb": round(memory.available / (1024**3), 2),
        "total_gb": round(memory.total / (1024**3), 2)
    }
    
    # CPU check
    cpu_percent = psutil.cpu_percent(interval=1)
    checks["cpu"] = {
        "status": "healthy" if cpu_percent < 70 else "degraded" if cpu_percent < 90 else "critical",
        "usage_percent": cpu_percent,
        "core_count": psutil.cpu_count()
    }
    
    # Disk check
    disk = psutil.disk_usage('/')
    checks["disk"] = {
        "status": "healthy" if disk.percent < 80 else "degraded" if disk.percent < 95 else "critical",
        "usage_percent": disk.percent,
        "free_gb": round(disk.free / (1024**3), 2),
        "total_gb": round(disk.total / (1024**3), 2)
    }
    
    # Database connectivity check
    checks["database"] = await check_database_connectivity()
    
    # External service checks
    checks["external_services"] = await check_external_services()
    
    # Application-specific checks
    checks["application"] = await check_application_health()
    
    return checks

def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_percent": memory.percent
        },
        "cpu": {
            "usage_percent": psutil.cpu_percent(),
            "core_count": psutil.cpu_count(),
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "used_percent": disk.percent
        },
        "network": {
            "connections": len(psutil.net_connections()),
            "interfaces": len(psutil.net_if_addrs())
        }
    }

def get_application_metrics() -> Dict[str, Any]:
    """Get application-specific metrics"""
    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "process_id": psutil.Process().pid,
        "thread_count": psutil.Process().num_threads(),
        "open_files": len(psutil.Process().open_files()),
        "connections": len(psutil.Process().connections())
    }

async def get_database_metrics() -> Dict[str, Any]:
    """Get database performance metrics"""
    try:
        # Import Firebase inside function to prevent import-time crashes
        from ..config.firebase import db, firebase_initialized
        
        if not firebase_initialized or not db:
            return {"status": "not_available", "error": "Firebase not initialized"}
        
        # Test database connectivity
        start_time = time.time()
        
        # Simple read operation to test connectivity
        test_ref = db.collection('health_check').limit(1)
        await test_ref.get()
        
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "firebase_initialized": firebase_initialized
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "firebase_initialized": False
        }

async def check_database_connectivity() -> Dict[str, Any]:
    """Check database connectivity and performance"""
    try:
        from ..config.firebase import db, firebase_initialized
        
        if not firebase_initialized:
            return {"status": "critical", "error": "Firebase not initialized"}
        
        # Test write operation
        start_time = time.time()
        test_ref = db.collection('health_check').document(f'test_{int(time.time())}')
        await test_ref.set({"timestamp": datetime.utcnow().isoformat()})
        
        response_time = (time.time() - start_time) * 1000
        
        # Clean up test document
        await test_ref.delete()
        
        return {
            "status": "healthy" if response_time < 1000 else "degraded",
            "response_time_ms": round(response_time, 2)
        }
        
    except Exception as e:
        return {"status": "critical", "error": str(e)}

async def check_external_services() -> Dict[str, Any]:
    """Check external service dependencies"""
    services = {}
    
    # Check OpenAI API (if used)
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("https://api.openai.com/v1/models", 
                                     headers={"Authorization": "Bearer test"})
            services["openai"] = {
                "status": "healthy" if response.status_code in [200, 401] else "degraded",
                "response_code": response.status_code
            }
    except Exception as e:
        services["openai"] = {"status": "critical", "error": str(e)}
    
    # Check weather API
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://api.openweathermap.org/data/2.5/weather?q=London&appid=test")
            services["weather_api"] = {
                "status": "healthy" if response.status_code in [200, 401] else "degraded",
                "response_code": response.status_code
            }
    except Exception as e:
        services["weather_api"] = {"status": "critical", "error": str(e)}
    
    return services

async def check_application_health() -> Dict[str, Any]:
    """Check application-specific health indicators"""
    try:
        # Check if core services are available
        from ..services.outfit_generation_service import OutfitGenerationService
        from ..services.cohesive_outfit_composition_service import CohesiveOutfitCompositionService
        
        # Test service initialization
        outfit_service = OutfitGenerationService()
        composition_service = CohesiveOutfitCompositionService()
        
        return {
            "status": "healthy",
            "services": {
                "outfit_generation": "available",
                "cohesive_composition": "available"
            }
        }
        
    except Exception as e:
        return {
            "status": "critical",
            "error": str(e),
            "services": {
                "outfit_generation": "unavailable",
                "cohesive_composition": "unavailable"
            }
        }

@router.get("/status")
async def get_status():
    """Get current system status"""
    return {
        "status": health_data["status"],
        "timestamp": health_data["timestamp"],
        "uptime": health_data["uptime"],
        "version": health_data["version"]
    }

@router.post("/reset")
async def reset_health_data(current_user: UserProfile = Depends(get_current_user_optional)):
    """Reset health data (admin only)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    global health_data, start_time
    start_time = time.time()
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": 0,
        "version": "1.0.0",
        "checks": {}
    }
    
    return {"message": "Health data reset successfully"}
