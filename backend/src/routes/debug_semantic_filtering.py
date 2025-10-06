"""
Debug API endpoint for semantic filtering
========================================

Demonstrates how to use the new semantic filtering functionality.
This is for testing and debugging purposes.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional
import logging

from ..services.robust_outfit_generation_service import RobustOutfitGenerationService
from ..custom_types.generation_context import GenerationContext
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile
from ..config.feature_flags import feature_flags, is_semantic_match_enabled, is_debug_output_enabled

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/feature-flags")
async def get_feature_flags() -> Dict[str, Any]:
    """
    Get current feature flag status for debugging and monitoring.
    
    Usage:
    - GET /feature-flags
    """
    return {
        "success": True,
        "feature_flags": feature_flags.get_all_flags(),
        "semantic_match_enabled": is_semantic_match_enabled(),
        "debug_output_enabled": is_debug_output_enabled(),
        "message": "Feature flags status retrieved"
    }

@router.get("/debug-filter")
async def debug_semantic_filtering(
    user_id: str = Query(..., description="User ID"),
    occasion: str = Query("casual", description="Occasion"),
    style: str = Query("casual", description="Style"),
    mood: str = Query("relaxed", description="Mood"),
    semantic: bool = Query(False, description="Enable semantic filtering"),
    limit: int = Query(10, description="Limit number of results")
) -> Dict[str, Any]:
    """
    Debug endpoint to test semantic filtering functionality.
    
    Usage:
    - GET /debug-filter?user_id=123&occasion=formal&style=business&semantic=true
    - GET /debug-filter?user_id=123&occasion=casual&style=streetwear&semantic=false
    """
    
    try:
        # Initialize the robust service
        robust_service = RobustOutfitGenerationService()
        
        # Create a mock context for testing
        # In production, you'd fetch real user data
        context = GenerationContext(
            user_id=user_id,
            occasion=occasion,
            style=style,
            mood=mood,
            weather=WeatherData(
                temperature=72.0,
                condition="sunny",
                precipitation=0,
                wind_speed=5
            ),
            wardrobe=[],  # Would be populated with real wardrobe data
            user_profile=UserProfile(
                id=user_id,
                name="Test User",
                email="test@example.com",
                bodyType="average",
                createdAt=1234567890,
                updatedAt=1234567890
            )
        )
        
        # Test the filtering with both modes
        logger.info(f"🔍 Testing semantic filtering: semantic={semantic}")
        
        # Call the filtering function with semantic flag
        debug_result = await robust_service._filter_suitable_items_with_debug(
            context, 
            semantic_filtering=semantic
        )
        
        return {
            "success": True,
            "semantic_filtering": semantic,
            "feature_flags": {
                "semantic_match_enabled": is_semantic_match_enabled(),
                "debug_output_enabled": is_debug_output_enabled(),
                "all_flags": feature_flags.get_all_flags()
            },
            "context": {
                "occasion": occasion,
                "style": style,
                "mood": mood
            },
            "results": {
                "total_items": debug_result.get("total_items", 0),
                "valid_items": len(debug_result.get("valid_items", [])),
                "debug_analysis": debug_result.get("debug_analysis", [])[:limit]
            },
            "debug_output": debug_result.get("debug_output", {}),
            "message": f"Semantic filtering {'enabled' if semantic else 'disabled'}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in debug semantic filtering: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare-filtering")
async def compare_filtering_modes(
    user_id: str = Query(..., description="User ID"),
    occasion: str = Query("casual", description="Occasion"),
    style: str = Query("casual", description="Style"),
    mood: str = Query("relaxed", description="Mood")
) -> Dict[str, Any]:
    """
    Compare traditional vs semantic filtering results.
    
    Usage:
    - GET /compare-filtering?user_id=123&occasion=formal&style=business
    """
    
    try:
        robust_service = RobustOutfitGenerationService()
        
        # Create mock context
        context = GenerationContext(
            user_id=user_id,
            occasion=occasion,
            style=style,
            mood=mood,
            weather=WeatherData(
                temperature=72.0,
                condition="sunny",
                precipitation=0,
                wind_speed=5
            ),
            wardrobe=[],
            user_profile=UserProfile(
                id=user_id,
                name="Test User",
                email="test@example.com",
                bodyType="average",
                createdAt=1234567890,
                updatedAt=1234567890
            )
        )
        
        # Test both filtering modes
        traditional_result = await robust_service._filter_suitable_items_with_debug(
            context, 
            semantic_filtering=False
        )
        
        semantic_result = await robust_service._filter_suitable_items_with_debug(
            context, 
            semantic_filtering=True
        )
        
        return {
            "success": True,
            "context": {
                "occasion": occasion,
                "style": style,
                "mood": mood
            },
            "comparison": {
                "traditional": {
                    "valid_items": len(traditional_result.get("valid_items", [])),
                    "total_items": traditional_result.get("total_items", 0)
                },
                "semantic": {
                    "valid_items": len(semantic_result.get("valid_items", [])),
                    "total_items": semantic_result.get("total_items", 0)
                }
            },
            "improvement": {
                "additional_items": len(semantic_result.get("valid_items", [])) - len(traditional_result.get("valid_items", [])),
                "percentage_improvement": (
                    (len(semantic_result.get("valid_items", [])) - len(traditional_result.get("valid_items", []))) 
                    / max(len(traditional_result.get("valid_items", [])), 1) * 100
                )
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in compare filtering: {e}")
        raise HTTPException(status_code=500, detail=str(e))
