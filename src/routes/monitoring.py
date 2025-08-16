"""
Monitoring and health check endpoints for ClosetGPT.
Provides health checks, metrics, and system status monitoring.
"""

import time
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from ..core.logging import get_logger, ErrorTracker
from ..config.firebase import db
from ..core.cache import cache_manager, cached

router = APIRouter()
logger = get_logger("monitoring")

# Global variables for tracking
start_time = time.time()
request_count = 0
error_count = 0
slow_request_count = 0

# Global metrics storage (in production, use Redis or similar)
system_metrics = {
    "start_time": datetime.utcnow(),
    "request_count": 0,
    "error_count": 0,
    "slow_requests": 0,
    "last_health_check": None
}

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    uptime = time.time() - start_time
    
    logger.info("Health check performed", extra={
        "extra_fields": {
            "status": "healthy",
            "uptime_seconds": uptime,
            "version": "1.0.0",
            "environment": "development"
        }
    })
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": round(uptime, 6),
        "version": "1.0.0",
        "environment": "development"
    }

@cached("metrics", ttl=30)  # Cache metrics for 30 seconds
async def get_system_metrics() -> Dict[str, Any]:
    """Get system metrics with caching for performance."""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": round(disk_percent, 1)
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0
        }

@cached("metrics", ttl=30)  # Cache request metrics for 30 seconds
async def get_request_metrics() -> Dict[str, Any]:
    """Get request metrics with caching for performance."""
    global request_count, error_count, slow_request_count
    
    # Calculate rates (requests per minute)
    uptime_minutes = (time.time() - start_time) / 60
    requests_per_minute = request_count / uptime_minutes if uptime_minutes > 0 else 0
    errors_per_minute = error_count / uptime_minutes if uptime_minutes > 0 else 0
    error_rate_percent = (error_count / request_count * 100) if request_count > 0 else 0
    
    return {
        "total": request_count,
        "rate_per_minute": round(requests_per_minute, 1),
        "errors": {
            "total": error_count,
            "rate_per_minute": round(errors_per_minute, 1),
            "error_rate_percent": round(error_rate_percent, 1)
        },
        "slow_requests": slow_request_count
    }

@router.get("/metrics")
async def get_metrics():
    """Get comprehensive system and application metrics."""
    try:
        # Get cached metrics
        system_metrics = await get_system_metrics()
        request_metrics = await get_request_metrics()
        
        uptime = time.time() - start_time
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": round(uptime, 6),
            "requests": request_metrics,
            "system": system_metrics
        }
        
        logger.info("Metrics collected", extra={
            "extra_fields": {
                "uptime_seconds": uptime,
                "request_count": request_metrics["total"],
                "error_rate": request_metrics["errors"]["error_rate_percent"]
            }
        })
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to collect metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to collect metrics"
        )

@cached("metrics", ttl=30)  # Cache readiness check for 30 seconds
async def check_system_readiness() -> Dict[str, Any]:
    """Check system readiness with caching for performance."""
    try:
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Define thresholds
        cpu_threshold = 90
        memory_threshold = 90
        disk_threshold = 90
        
        # Check if system is ready
        cpu_ready = cpu_percent < cpu_threshold
        memory_ready = memory.percent < memory_threshold
        disk_ready = (disk.used / disk.total * 100) < disk_threshold
        
        overall_ready = cpu_ready and memory_ready and disk_ready
        
        return {
            "ready": overall_ready,
            "checks": {
                "cpu": {
                    "ready": cpu_ready,
                    "value": cpu_percent,
                    "threshold": cpu_threshold
                },
                "memory": {
                    "ready": memory_ready,
                    "value": memory.percent,
                    "threshold": memory_threshold
                },
                "disk": {
                    "ready": disk_ready,
                    "value": round((disk.used / disk.total) * 100, 1),
                    "threshold": disk_threshold
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to check system readiness: {e}")
        return {
            "ready": False,
            "error": str(e)
        }

@router.get("/ready")
async def readiness_check():
    """Check if the system is ready to handle requests."""
    try:
        readiness = await check_system_readiness()
        
        if readiness.get("ready", False):
            logger.info("System readiness check passed")
            return readiness
        else:
            logger.warning("System readiness check failed", extra={
                "extra_fields": readiness
            })
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="System not ready"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Readiness check failed"
        )

@router.get("/status")
async def get_system_status():
    """Get comprehensive system status."""
    try:
        # Get all cached data
        system_metrics = await get_system_metrics()
        request_metrics = await get_request_metrics()
        readiness = await check_system_readiness()
        
        uptime = time.time() - start_time
        
        # Get cache statistics
        cache_stats = cache_manager.get_all_stats()
        
        status = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": round(uptime, 6),
            "version": "1.0.0",
            "environment": "development",
            "status": "healthy" if readiness.get("ready", False) else "degraded",
            "system": system_metrics,
            "requests": request_metrics,
            "readiness": readiness,
            "cache": cache_stats
        }
        
        logger.info("System status collected", extra={
            "extra_fields": {
                "status": status["status"],
                "uptime_seconds": uptime,
                "cache_hit_rate": sum(stats.get("hit_rate", 0) for stats in cache_stats.values()) / len(cache_stats) if cache_stats else 0
            }
        })
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system status"
        )

# Functions to update metrics (called by middleware)
def increment_request_count():
    """Increment the total request count."""
    global request_count
    try:
        request_count += 1
        # Also update the system_metrics dict
        system_metrics["request_count"] = request_count
    except Exception as e:
        logger.error(f"Failed to increment request count: {e}")

def increment_error_count():
    """Increment the error count."""
    global error_count
    try:
        error_count += 1
        # Also update the system_metrics dict
        system_metrics["error_count"] = error_count
    except Exception as e:
        logger.error(f"Failed to increment error count: {e}")

def increment_slow_request_count():
    """Increment the slow request count."""
    global slow_request_count
    try:
        slow_request_count += 1
        # Also update the system_metrics dict
        system_metrics["slow_requests"] = slow_request_count
    except Exception as e:
        logger.error(f"Failed to increment slow request count: {e}")

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics."""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database connectivity check
        db_status = "healthy"
        try:
            # Simple test query
            db.collection("test").limit(1).get()
        except Exception as e:
            db_status = "unhealthy"
            logger.error("Database health check failed", exc_info=True)
        
        # Overall health status
        overall_status = "healthy"
        if db_status == "unhealthy" or cpu_percent > 90 or memory.percent > 90:
            overall_status = "degraded"
        
        health_status = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": (datetime.utcnow() - system_metrics["start_time"]).total_seconds(),
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3)
            },
            "services": {
                "database": db_status
            },
            "metrics": {
                "total_requests": system_metrics["request_count"],
                "total_errors": system_metrics["error_count"],
                "slow_requests": system_metrics["slow_requests"]
            }
        }
        
        logger.info("Detailed health check performed", extra={
            "extra_fields": health_status
        })
        
        return health_status
        
    except Exception as e:
        logger.error("Detailed health check failed", exc_info=True)
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/metrics/errors")
async def get_error_metrics():
    """Get detailed error metrics."""
    try:
        # Get error tracker instance
        error_tracker = ErrorTracker(logger)
        error_summary = error_tracker.get_error_summary()
        
        # Add system error metrics
        error_metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_errors": system_metrics["error_count"],
            "error_summary": error_summary,
            "recent_errors": []  # In production, this would come from persistent storage
        }
        
        return error_metrics
        
    except Exception as e:
        logger.error("Failed to get error metrics", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve error metrics")

@router.post("/metrics/increment")
async def increment_metric(metric_name: str, value: int = 1):
    """Increment a metric (for internal use)."""
    try:
        if metric_name in system_metrics:
            system_metrics[metric_name] += value
        else:
            system_metrics[metric_name] = value
        
        logger.info(f"Metric incremented: {metric_name}", extra={
            "extra_fields": {
                "metric_name": metric_name,
                "value": value,
                "new_total": system_metrics[metric_name]
            }
        })
        
        return {"status": "success", "metric": metric_name, "value": system_metrics[metric_name]}
        
    except Exception as e:
        logger.error("Failed to increment metric", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to increment metric") 