"""
Adaptive Tuning API endpoints
Provides access to adaptive tuning system for outfit generation parameters.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import logging
from ..services.adaptive_tuning_service import adaptive_tuning, PerformanceMetrics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/adaptive-tuning", tags=["adaptive-tuning"])

@router.get("/status")
async def get_tuning_status() -> Dict[str, Any]:
    """Get current tuning status and recommendations"""
    try:
        status = adaptive_tuning.get_tuning_status()
        return {
            "success": True,
            "data": status,
            "message": "Tuning status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error retrieving tuning status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tuning status: {str(e)}")

@router.get("/parameters")
async def get_current_parameters() -> Dict[str, Any]:
    """Get current parameter values"""
    try:
        parameters = adaptive_tuning.get_current_parameters()
        return {
            "success": True,
            "data": parameters,
            "message": "Current parameters retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error retrieving parameters: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve parameters: {str(e)}")

@router.get("/history")
async def get_parameter_history(hours: int = Query(default=24, ge=1, le=168)) -> Dict[str, Any]:
    """Get parameter history for the last N hours"""
    try:
        history = adaptive_tuning.get_parameter_history(hours)
        return {
            "success": True,
            "data": {
                "hours": hours,
                "history": history,
                "entries": len(history)
            },
            "message": f"Parameter history for last {hours} hours retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error retrieving parameter history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve parameter history: {str(e)}")

@router.post("/run")
async def run_adaptive_tuning() -> Dict[str, Any]:
    """Run adaptive tuning process"""
    try:
        result = adaptive_tuning.run_adaptive_tuning()
        return {
            "success": True,
            "data": result,
            "message": "Adaptive tuning completed successfully" if result.get('tuning_performed') else "No tuning performed"
        }
    except Exception as e:
        logger.error(f"Error running adaptive tuning: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run adaptive tuning: {str(e)}")

@router.post("/reset")
async def reset_parameters() -> Dict[str, Any]:
    """Reset all parameters to default values"""
    try:
        result = adaptive_tuning.reset_parameters_to_default()
        return {
            "success": True,
            "data": result,
            "message": f"Reset {result['reset_count']} parameters to default values"
        }
    except Exception as e:
        logger.error(f"Error resetting parameters: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset parameters: {str(e)}")

@router.post("/record-performance")
async def record_performance_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Record performance metrics for tuning analysis"""
    try:
        # Convert dict to PerformanceMetrics object
        perf_metrics = PerformanceMetrics(
            success_rate=(metrics.get('success_rate', 0.0) if metrics else 0.0),
            avg_confidence=(metrics.get('avg_confidence', 0.0) if metrics else 0.0),
            avg_generation_time=(metrics.get('avg_generation_time', 0.0) if metrics else 0.0),
            avg_validation_time=(metrics.get('avg_validation_time', 0.0) if metrics else 0.0),
            diversity_score=(metrics.get('diversity_score', 0.0) if metrics else 0.0),
            user_satisfaction=(metrics.get('user_satisfaction', 0.0) if metrics else 0.0),
            fallback_rate=(metrics.get('fallback_rate', 0.0) if metrics else 0.0),
            sample_size=(metrics.get('sample_size', 1) if metrics else 1),
            time_window_hours=(metrics.get('time_window_hours', 0) if metrics else 0)
        )
        
        adaptive_tuning.record_performance(perf_metrics)
        
        return {
            "success": True,
            "message": "Performance metrics recorded successfully"
        }
    except Exception as e:
        logger.error(f"Error recording performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record performance metrics: {str(e)}")

@router.get("/recommendations")
async def get_tuning_recommendations() -> Dict[str, Any]:
    """Get current tuning recommendations without applying them"""
    try:
        recommendations = adaptive_tuning.generate_tuning_recommendations()
        return {
            "success": True,
            "data": {
                "recommendations": [
                    {
                        "parameter": rec.parameter.value,
                        "current_value": rec.current_value,
                        "recommended_value": rec.recommended_value,
                        "adjustment_reason": rec.adjustment_reason,
                        "confidence": rec.confidence,
                        "expected_improvement": rec.expected_improvement,
                        "risk_level": rec.risk_level
                    }
                    for rec in recommendations
                ],
                "count": len(recommendations)
            },
            "message": f"Retrieved {len(recommendations)} tuning recommendations"
        }
    except Exception as e:
        logger.error(f"Error retrieving tuning recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tuning recommendations: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for adaptive tuning service"""
    try:
        # Check if service is responsive
        parameters = adaptive_tuning.get_current_parameters()
        return {
            "success": True,
            "status": "healthy",
            "data": {
                "parameters_loaded": len(parameters),
                "tuning_enabled": True
            },
            "message": "Adaptive tuning service is healthy"
        }
    except Exception as e:
        logger.error(f"Adaptive tuning health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "message": "Adaptive tuning service is unhealthy"
        }
