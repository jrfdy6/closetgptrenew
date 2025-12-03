"""
Production Monitoring Dashboard API Routes
Provides real-time monitoring data for production launch.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse

from ..auth.auth_service import get_current_user_id
from ..services.production_monitoring_service import (
    monitoring_service,
    OperationType,
    UserJourneyStep,
    ServiceLayer
)

router = APIRouter(tags=["monitoring"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def monitoring_health_check():
    """Health check for monitoring service."""
    return {
        "status": "healthy",
        "monitoring_enabled": monitoring_service.enabled,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/stats/summary")
async def get_monitoring_summary(
    time_window_minutes: int = Query(60, ge=1, le=1440),  # 1 min to 24 hours
):
    """
    Get comprehensive monitoring summary.
    
    Query params:
        time_window_minutes: Time window to analyze (default: 60, max: 1440)
    
    Returns:
        Complete monitoring stats including:
        - Success rates for all operations
        - Performance percentiles (p50, p95, p99)
        - Cache hit rates
        - Recent errors
        - User funnel stats
        - Service layer distribution
    """
    try:
        summary = await monitoring_service.get_summary_stats(time_window_minutes)
        return JSONResponse(content=summary)
    
    except Exception as e:
        logger.error(f"Error generating monitoring summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate monitoring summary: {str(e)}"
        )


@router.get("/stats/operations")
async def get_operation_stats(
    operation: Optional[OperationType] = Query(None),
    time_window_minutes: int = Query(60, ge=1, le=1440)
):
    """
    Get detailed stats for specific operation type.
    
    Query params:
        operation: Operation type to analyze (optional, shows all if not specified)
        time_window_minutes: Time window to analyze
    
    Returns:
        Detailed operation statistics
    """
    try:
        if operation:
            # Single operation stats
            success_rate = monitoring_service.get_success_rate(operation)
            p50 = monitoring_service.get_performance_percentile(operation, 50, time_window_minutes)
            p95 = monitoring_service.get_performance_percentile(operation, 95, time_window_minutes)
            p99 = monitoring_service.get_performance_percentile(operation, 99, time_window_minutes)
            
            stats = monitoring_service.metrics['success_rates'][operation]
            
            return {
                "operation": operation,
                "success_rate": success_rate,
                "total_operations": stats['success'] + stats['failure'],
                "successful": stats['success'],
                "failed": stats['failure'],
                "performance": {
                    "p50_ms": p50,
                    "p95_ms": p95,
                    "p99_ms": p99
                },
                "time_window_minutes": time_window_minutes
            }
        else:
            # All operations
            all_stats = {}
            for op in OperationType:
                success_rate = monitoring_service.get_success_rate(op)
                stats = monitoring_service.metrics['success_rates'][op]
                p95 = monitoring_service.get_performance_percentile(op, 95, time_window_minutes)
                
                all_stats[op] = {
                    "success_rate": success_rate,
                    "total_operations": stats['success'] + stats['failure'],
                    "p95_ms": p95
                }
            
            return {
                "operations": all_stats,
                "time_window_minutes": time_window_minutes
            }
    
    except Exception as e:
        logger.error(f"Error getting operation stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get operation stats: {str(e)}"
        )


@router.get("/stats/errors")
async def get_recent_errors(
    limit: int = Query(50, ge=1, le=500),
    operation: Optional[OperationType] = Query(None)
):
    """
    Get recent errors with full context.
    
    Query params:
        limit: Maximum number of errors to return (default: 50, max: 500)
        operation: Filter by operation type (optional)
    
    Returns:
        Recent errors with stack traces and context
    """
    try:
        errors = monitoring_service.metrics['errors']
        
        # Filter by operation if specified
        if operation:
            errors = [e for e in errors if e['operation'] == operation]
        
        # Get most recent errors
        recent_errors = errors[-limit:]
        
        return {
            "total_errors": len(errors),
            "returned_count": len(recent_errors),
            "errors": recent_errors,
            "operation_filter": operation
        }
    
    except Exception as e:
        logger.error(f"Error getting recent errors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent errors: {str(e)}"
        )


@router.get("/stats/user-funnel")
async def get_user_funnel():
    """
    Get user journey funnel statistics.
    
    Returns:
        Conversion rates for each funnel step
    """
    try:
        funnel_stats = monitoring_service.get_user_funnel_stats()
        
        return {
            "total_users": len(monitoring_service.metrics['user_journeys']),
            "funnel": funnel_stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting user funnel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user funnel: {str(e)}"
        )


@router.get("/stats/service-layers")
async def get_service_layer_stats():
    """
    Get service layer usage distribution.
    Shows which generation strategies are being used.
    
    Returns:
        Distribution of service layer usage with percentages
    """
    try:
        distribution = monitoring_service.get_service_layer_distribution()
        
        return {
            "distribution": distribution,
            "total_generations": sum(monitoring_service.metrics['service_layers'].values()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting service layer stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get service layer stats: {str(e)}"
        )


@router.get("/stats/cache")
async def get_cache_stats():
    """
    Get cache performance statistics.
    
    Returns:
        Cache hit/miss rates
    """
    try:
        hit_rate = monitoring_service.get_cache_hit_rate()
        stats = monitoring_service.metrics['cache_stats']
        
        return {
            "hit_rate_percent": hit_rate,
            "hits": stats['hits'],
            "misses": stats['misses'],
            "total_requests": stats['hits'] + stats['misses'],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.get("/stats/api-calls")
async def get_api_call_stats():
    """
    Get external API call statistics.
    
    Returns:
        API call counts by service
    """
    try:
        api_calls = monitoring_service.metrics['api_calls']
        
        return {
            "api_calls": dict(api_calls),
            "total_calls": sum(api_calls.values()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting API call stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API call stats: {str(e)}"
        )


@router.post("/track/user-journey")
async def track_user_journey_manual(
    step: UserJourneyStep,
    metadata: Optional[Dict[str, Any]] = None,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Manually track a user journey step.
    
    Body:
        step: Journey step to track
        metadata: Optional metadata
    
    Returns:
        Confirmation
    """
    try:
        await monitoring_service.track_user_journey(
            user_id=current_user_id,
            step=step,
            metadata=metadata
        )
        
        return {
            "success": True,
            "step": step,
            "user_id": current_user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error tracking user journey: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track user journey: {str(e)}"
        )


@router.get("/alerts")
async def get_alerts(
    limit: int = Query(20, ge=1, le=100),
    acknowledged: Optional[bool] = Query(None)
):
    """
    Get recent alerts.
    
    Query params:
        limit: Maximum number of alerts to return
        acknowledged: Filter by acknowledged status (optional)
    
    Returns:
        Recent alerts
    """
    try:
        db = monitoring_service.db
        if not db:
            return {
                "alerts": [],
                "message": "Firebase not available"
            }
        
        # Query alerts
        query = db.collection('alerts').order_by('timestamp', direction='DESCENDING').limit(limit)
        
        if acknowledged is not None:
            query = query.where('acknowledged', '==', acknowledged)
        
        alerts = []
        for doc in query.stream():
            alert_data = doc.to_dict()
            alert_data['id'] = doc.id
            alerts.append(alert_data)
        
        return {
            "alerts": alerts,
            "count": len(alerts),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """
    Mark an alert as acknowledged.
    
    Path params:
        alert_id: Alert document ID
    
    Returns:
        Confirmation
    """
    try:
        db = monitoring_service.db
        if not db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase not available"
            )
        
        # Update alert
        alert_ref = db.collection('alerts').document(alert_id)
        alert_ref.update({
            'acknowledged': True,
            'acknowledged_at': datetime.now(timezone.utc)
        })
        
        return {
            "success": True,
            "alert_id": alert_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )


@router.get("/dashboard")
async def get_monitoring_dashboard():
    """
    Get comprehensive dashboard data for frontend display.
    
    Returns:
        All monitoring data formatted for dashboard
    """
    try:
        # Get summary stats
        summary = await monitoring_service.get_summary_stats(60)
        
        # Get cache stats
        cache_stats = {
            "hit_rate_percent": monitoring_service.get_cache_hit_rate(),
            "hits": monitoring_service.metrics['cache_stats']['hits'],
            "misses": monitoring_service.metrics['cache_stats']['misses']
        }
        
        # Get service layer distribution
        service_layers = monitoring_service.get_service_layer_distribution()
        
        # Get user funnel
        funnel = monitoring_service.get_user_funnel_stats()
        
        # Key metrics for quick view
        outfit_success_rate = monitoring_service.get_success_rate(OperationType.OUTFIT_GENERATION)
        outfit_p95 = monitoring_service.get_performance_percentile(OperationType.OUTFIT_GENERATION, 95, 60)
        
        return {
            "overview": {
                "outfit_generation_success_rate": outfit_success_rate,
                "outfit_generation_p95_ms": outfit_p95,
                "cache_hit_rate": cache_stats['hit_rate_percent'],
                "total_operations": summary['total_operations'],
                "recent_errors": len(summary['recent_errors']),
            },
            "detailed_stats": summary,
            "cache": cache_stats,
            "service_layers": service_layers,
            "user_funnel": funnel,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard: {str(e)}"
        )

