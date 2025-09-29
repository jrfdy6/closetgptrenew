"""
Strategy Analytics API endpoints
Provides real-time insights into outfit generation strategy usage and performance.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import logging
from ..services.strategy_analytics_service import strategy_analytics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/strategy-analytics", tags=["strategy-analytics"])

@router.get("/overview")
async def get_strategy_overview() -> Dict[str, Any]:
    """Get comprehensive strategy analytics overview"""
    try:
        analytics = strategy_analytics.get_strategy_analytics()
        return {
            "success": True,
            "data": analytics,
            "message": "Strategy analytics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error retrieving strategy analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve strategy analytics: {str(e)}")

@router.get("/strategy/{strategy_name}")
async def get_strategy_details(strategy_name: str) -> Dict[str, Any]:
    """Get detailed analytics for a specific strategy"""
    try:
        analytics = strategy_analytics.get_strategy_analytics(strategy_name)
        if "error" in analytics:
            raise HTTPException(status_code=404, detail=analytics["error"])
        
        return {
            "success": True,
            "data": analytics,
            "message": f"Strategy '{strategy_name}' analytics retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving strategy details for {strategy_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve strategy details: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_analytics(user_id: str) -> Dict[str, Any]:
    """Get analytics for a specific user"""
    try:
        analytics = strategy_analytics.get_user_analytics(user_id)
        if "error" in analytics:
            raise HTTPException(status_code=404, detail=analytics["error"])
        
        return {
            "success": True,
            "data": analytics,
            "message": f"User '{user_id}' analytics retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user analytics for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user analytics: {str(e)}")

@router.get("/recommendations")
async def get_performance_recommendations() -> Dict[str, Any]:
    """Get performance improvement recommendations"""
    try:
        recommendations = strategy_analytics.get_performance_recommendations()
        return {
            "success": True,
            "data": recommendations,
            "message": "Performance recommendations retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error retrieving performance recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve recommendations: {str(e)}")

@router.get("/export")
async def export_analytics_data() -> Dict[str, Any]:
    """Export all analytics data for external analysis"""
    try:
        data = strategy_analytics.export_analytics_data()
        return {
            "success": True,
            "data": data,
            "message": "Analytics data exported successfully"
        }
    except Exception as e:
        logger.error(f"Error exporting analytics data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export analytics data: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for strategy analytics service"""
    try:
        analytics = strategy_analytics.get_strategy_analytics()
        return {
            "success": True,
            "status": "healthy",
            "total_executions": analytics.get("total_executions", 0),
            "active_strategies": len(analytics.get("active_strategies", [])),
            "message": "Strategy analytics service is healthy"
        }
    except Exception as e:
        logger.error(f"Strategy analytics health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "message": "Strategy analytics service is unhealthy"
        }
