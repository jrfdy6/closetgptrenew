"""
Generation Metrics API endpoints for monitoring outfit generation patterns.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from ..services.generation_metrics_service import generation_metrics

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/metrics/overview")
async def get_metrics_overview():
    """Get overview of generation metrics."""
    try:
        metrics = generation_metrics.get_strategy_metrics()
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error getting metrics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/breakdown")
async def get_metrics_breakdown():
    """Get detailed breakdown of strategy usage patterns."""
    try:
        breakdown = generation_metrics.get_strategy_breakdown()
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "breakdown": breakdown
        }
    except Exception as e:
        logger.error(f"Error getting metrics breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/fallback-analysis")
async def get_fallback_analysis():
    """Get analysis of fallback patterns and reasons."""
    try:
        analysis = generation_metrics.get_fallback_analysis()
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "fallback_analysis": analysis
        }
    except Exception as e:
        logger.error(f"Error getting fallback analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/hourly")
async def get_hourly_metrics(hours: int = 24):
    """Get hourly metrics for the last N hours."""
    try:
        if hours < 1 or hours > 168:  # Max 1 week
            raise HTTPException(status_code=400, detail="Hours must be between 1 and 168")
        
        hourly = generation_metrics.get_hourly_metrics(hours)
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "hours_requested": hours,
            "hourly_metrics": hourly
        }
    except Exception as e:
        logger.error(f"Error getting hourly metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get metrics in Prometheus format."""
    try:
        metrics = generation_metrics.get_strategy_metrics()
        fallback_analysis = generation_metrics.get_fallback_analysis()
        
        prometheus_lines = []
        
        # Strategy counts
        for strategy, count in metrics["strategy_counts"].items():
            prometheus_lines.append(f'outfit_generation_strategy{{strategy="{strategy}"}} {count}')
        
        # Success/failure rates
        prometheus_lines.append(f'outfit_generation_success_rate {metrics["success_rate"]:.2f}')
        prometheus_lines.append(f'outfit_generation_fallback_rate {metrics["fallback_rate"]:.2f}')
        
        # Failed rules
        for rule, count in metrics["failed_rules"].items():
            prometheus_lines.append(f'outfit_generation_failed_rule{{rule="{rule}"}} {count}')
        
        # Fallback reasons
        for reason, count in fallback_analysis["fallback_reasons"].items():
            prometheus_lines.append(f'outfit_generation_fallback_reason{{reason="{reason}"}} {count}')
        
        # Performance metrics
        for strategy, avg_time in metrics["avg_generation_times"].items():
            prometheus_lines.append(f'outfit_generation_avg_time_seconds{{strategy="{strategy}"}} {avg_time:.3f}')
        
        prometheus_output = "\n".join(prometheus_lines)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "format": "prometheus",
            "metrics": prometheus_output
        }
    except Exception as e:
        logger.error(f"Error getting Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/health")
async def get_metrics_health():
    """Health check for metrics service."""
    try:
        metrics = generation_metrics.get_strategy_metrics()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "total_generations": metrics["total_generations"],
            "success_rate": f"{metrics['success_rate']:.1f}%",
            "fallback_rate": f"{metrics['fallback_rate']:.1f}%"
        }
    except Exception as e:
        logger.error(f"Error checking metrics health: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.post("/metrics/reset")
async def reset_metrics():
    """Reset all metrics (useful for testing)."""
    try:
        generation_metrics.reset_metrics()
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": "All metrics have been reset"
        }
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
