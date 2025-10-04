"""
Diversity Analytics API endpoints
Provides insights into outfit diversity and rotation effectiveness.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import logging
from ..services.diversity_filter_service import diversity_filter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/diversity-analytics", tags=["diversity-analytics"])

@(router.get("/user/{user_id}") if router else None)
async def get_user_diversity_metrics(user_id: str) -> Dict[str, Any]:
    """Get diversity metrics for a specific user"""
    try:
        metrics = diversity_filter.get_diversity_metrics(user_id)
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "total_outfits": metrics.total_outfits,
                "unique_combinations": metrics.unique_combinations,
                "diversity_score": metrics.diversity_score,
                "similarity_threshold": metrics.similarity_threshold,
                "rotation_effectiveness": metrics.rotation_effectiveness,
                "recent_repetitions": metrics.recent_repetitions,
                "diversity_percentage": (metrics.unique_combinations / metrics.total_outfits * 100) if metrics.total_outfits > 0 else 100
            },
            "message": f"Diversity metrics retrieved for user {user_id}"
        }
    except Exception as e:
        logger.error(f"Error retrieving diversity metrics for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve diversity metrics: {str(e)}")

@(router.get("/user/{user_id}/suggestions") if router else None)
async def get_diversity_suggestions(user_id: str) -> Dict[str, Any]:
    """Get diversity improvement suggestions for a user"""
    try:
        metrics = diversity_filter.get_diversity_metrics(user_id)
        suggestions = []
        
        # Analyze diversity score
        if metrics.diversity_score < 0.7:
            suggestions.append({
                "type": "diversity",
                "priority": "high",
                "message": f"Diversity score is low ({metrics.diversity_score:.2f})",
                "recommendation": "Try more varied color combinations and item types"
            })
        
        # Analyze recent repetitions
        if metrics.recent_repetitions > 3:
            suggestions.append({
                "type": "repetition",
                "priority": "medium",
                "message": f"High repetition rate ({metrics.recent_repetitions} recent similar outfits)",
                "recommendation": "Explore different item combinations and styles"
            })
        
        # Analyze rotation effectiveness
        if metrics.rotation_effectiveness < 0.5:
            suggestions.append({
                "type": "rotation",
                "priority": "medium",
                "message": f"Low rotation effectiveness ({metrics.rotation_effectiveness:.2f})",
                "recommendation": "Use more items from your wardrobe rotation"
            })
        
        # Analyze unique combinations
        if metrics.total_outfits > 10 and metrics.unique_combinations / metrics.total_outfits < 0.8:
            suggestions.append({
                "type": "uniqueness",
                "priority": "low",
                "message": f"Only {metrics.unique_combinations}/{metrics.total_outfits} unique combinations",
                "recommendation": "Try different item pairings to increase variety"
            })
        
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "suggestions": suggestions,
                "metrics": {
                    "diversity_score": metrics.diversity_score,
                    "recent_repetitions": metrics.recent_repetitions,
                    "rotation_effectiveness": metrics.rotation_effectiveness
                }
            },
            "message": f"Diversity suggestions retrieved for user {user_id}"
        }
    except Exception as e:
        logger.error(f"Error retrieving diversity suggestions for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve diversity suggestions: {str(e)}")

@router.post("/user/{user_id}/reset")
async def reset_user_diversity(user_id: str) -> Dict[str, Any]:
    """Reset diversity tracking for a user"""
    try:
        diversity_filter.reset_user_diversity(user_id)
        return {
            "success": True,
            "message": f"Diversity tracking reset for user {user_id}"
        }
    except Exception as e:
        logger.error(f"Error resetting diversity tracking for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset diversity tracking: {str(e)}")

@(router.get("/user/{user_id}/items/suggest") if router else None)
async def suggest_diverse_items(
    user_id: str, 
    target_count: int = Query(default=3, ge=1, le=10)
) -> Dict[str, Any]:
    """Suggest diverse items for a user (placeholder - would need available items)"""
    try:
        # This would need to be integrated with wardrobe service
        # For now, return a placeholder response
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "suggested_count": target_count,
                "message": "Diversity suggestions require integration with wardrobe service"
            },
            "message": f"Diversity item suggestions for user {user_id}"
        }
    except Exception as e:
        logger.error(f"Error suggesting diverse items for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest diverse items: {str(e)}")

@(router.get("/health") if router else None)
async def health_check() -> Dict[str, Any]:
    """Health check for diversity analytics service"""
    try:
        # Check if service is responsive
        test_metrics = diversity_filter.get_diversity_metrics("test_user")
        return {
            "success": True,
            "status": "healthy",
            "message": "Diversity analytics service is healthy"
        }
    except Exception as e:
        logger.error(f"Diversity analytics health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "message": "Diversity analytics service is unhealthy"
        }
