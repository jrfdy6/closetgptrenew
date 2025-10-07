"""
Semantic Filtering Telemetry API Routes
Provides endpoints for monitoring semantic filtering performance
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging

from ..utils.semantic_telemetry import (
    get_semantic_telemetry_status,
    get_debug_reason_analytics,
    establish_telemetry_baseline,
    get_active_alerts,
    semantic_telemetry
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/semantic-telemetry", tags=["semantic-telemetry"])

@router.get("/status")
async def get_telemetry_status():
    """Get current semantic filtering telemetry status"""
    try:
        status = get_semantic_telemetry_status()
        return {
            "status": "success",
            "data": status,
            "timestamp": status.get("timestamp")
        }
    except Exception as e:
        logger.error(f"Error getting telemetry status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get telemetry status: {str(e)}")

@router.get("/debug-reasons")
async def get_debug_reasons():
    """Get debug rejection reason analytics"""
    try:
        analytics = get_debug_reason_analytics()
        return {
            "status": "success",
            "data": {
                "debug_reasons": analytics,
                "total_reasons": len(analytics)
            }
        }
    except Exception as e:
        logger.error(f"Error getting debug reasons: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get debug reasons: {str(e)}")

@router.get("/alerts")
async def get_alerts():
    """Get active alerts"""
    try:
        alerts = get_active_alerts()
        return {
            "status": "success",
            "data": {
                "alerts": alerts,
                "alert_count": len(alerts)
            }
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.post("/establish-baseline")
async def establish_baseline():
    """Establish telemetry baseline from current data"""
    try:
        establish_telemetry_baseline()
        return {
            "status": "success",
            "message": "Baseline established successfully"
        }
    except Exception as e:
        logger.error(f"Error establishing baseline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to establish baseline: {str(e)}")

@router.get("/health")
async def telemetry_health():
    """Health check for telemetry system"""
    try:
        status = get_semantic_telemetry_status()
        return {
            "status": "healthy",
            "telemetry_active": status.get("status") == "active",
            "total_requests": status.get("total_requests", 0),
            "active_alerts": status.get("active_alerts", 0)
        }
    except Exception as e:
        logger.error(f"Error checking telemetry health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get comprehensive metrics summary"""
    try:
        status = get_semantic_telemetry_status()
        debug_reasons = get_debug_reason_analytics()
        alerts = get_active_alerts()
        
        return {
            "status": "success",
            "data": {
                "system_metrics": status,
                "debug_analytics": {
                    "top_rejection_reasons": debug_reasons[:5],  # Top 5
                    "total_unique_reasons": len(debug_reasons)
                },
                "alerts": {
                    "active_alerts": alerts,
                    "alert_count": len(alerts)
                },
                "recommendations": _generate_recommendations(status, debug_reasons, alerts)
            }
        }
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics summary: {str(e)}")

def _generate_recommendations(status: Dict[str, Any], debug_reasons: List[Dict], alerts: List[str]) -> List[str]:
    """Generate recommendations based on current metrics"""
    recommendations = []
    
    # Check filter pass rate
    filter_pass_rate = status.get("current_filter_pass_rate", 0)
    if filter_pass_rate < 0.1:
        recommendations.append("🔧 Consider relaxing filtering criteria - very low pass rate")
    elif filter_pass_rate > 0.8:
        recommendations.append("🔧 Consider tightening filtering criteria - very high pass rate")
    
    # Check composition success rate
    composition_success_rate = status.get("current_composition_success_rate", 0)
    if composition_success_rate < 0.5:
        recommendations.append("🔧 Composition success rate is low - check outfit generation logic")
    
    # Check semantic vs traditional performance
    semantic_pass_rate = status.get("semantic_filter_pass_rate", 0)
    traditional_pass_rate = status.get("traditional_filter_pass_rate", 0)
    
    if semantic_pass_rate > 0 and traditional_pass_rate > 0:
        if semantic_pass_rate > traditional_pass_rate * 1.5:
            recommendations.append("📊 Semantic filtering is significantly more permissive - monitor quality")
        elif semantic_pass_rate < traditional_pass_rate * 0.5:
            recommendations.append("📊 Semantic filtering is more restrictive - check compatibility matrix")
    
    # Check top rejection reasons
    if debug_reasons:
        top_reason = debug_reasons[0]
        if top_reason["percentage"] > 50:
            recommendations.append(f"🔍 Top rejection reason '{top_reason['reason']}' accounts for {top_reason['percentage']:.1f}% - investigate")
    
    # Check alerts
    if alerts:
        recommendations.append(f"🚨 {len(alerts)} active alerts require attention")
    
    if not recommendations:
        recommendations.append("✅ System performing within normal parameters")
    
    return recommendations
