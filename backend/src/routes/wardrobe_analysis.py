from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from ..services.wardrobe_analysis_service import WardrobeAnalysisService
from ..auth.auth_service import get_current_user_id, get_current_user
from ..custom_types.profile import UserProfile
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
# Router loaded

router = APIRouter(tags=["wardrobe-analysis"])

@router.get("/gaps")
async def get_wardrobe_gaps(gender: str = None, current_user: UserProfile = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get comprehensive wardrobe gap analysis for the current user.
    
    This endpoint analyzes the user's wardrobe and identifies:
    - Missing essential items
    - Gaps in occasion coverage
    - Style diversity issues
    - Validation error patterns
    - Outfit generation failures
    
    Parameters:
    - gender: Optional gender filter ("male", "female", or None for unisex/all)
    
    Returns detailed analysis with prioritized recommendations.
    """
    try:
        print(f"🔍 Gaps Backend: Received gender parameter: {gender}")
        print(f"🔍 Gaps Backend: Current user: {current_user.id if current_user else 'None'}")
        print(f"🔍 Gaps Backend: Current user gender: {current_user.gender if current_user else 'None'}")
        
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # Use user's gender if not specified
        if not gender and current_user.gender:
            gender = current_user.gender
            print(f"🎯 Gaps Backend: Using user's gender from profile: {gender}")
        
        print(f"🎯 Gaps Backend: Final gender filter: {gender}")
            
        analysis_service = WardrobeAnalysisService()
        analysis = await analysis_service.get_wardrobe_gaps(current_user.id)
        
        # Try to get real trends directly with gender filtering
        try:
            from src.services.fashion_trends_service import FashionTrendsService
            trends_service = FashionTrendsService()
            print(f"🔍 Gaps Backend: Calling trends service with gender: {gender}")
            real_trends = await trends_service.get_trending_styles(gender)
            
            if real_trends and len(real_trends) > 0:
                print(f"✅ Gaps Backend: Successfully retrieved {len(real_trends)} real trends for gender: {gender or 'unisex'}")
                # Check if ballet flats are in the results
                ballet_flats_count = sum(1 for trend in real_trends if 'ballet' in trend.get('name', '').lower())
                print(f"🔍 Gaps Backend: Ballet flats in results: {ballet_flats_count}")
                analysis["trending_styles"] = real_trends
                analysis["gender_filter"] = gender
            else:
                print("⚠️ Gaps Backend: No real trends available, keeping fallback data")
        except Exception as e:
            print(f"❌ Gaps Backend: Error getting real trends: {e}")
            # Keep the fallback trends from the analysis service
        
        return {
            "success": True,
            "data": analysis,
            "message": "Wardrobe gap analysis completed successfully"
        }
    except Exception as e:
        print(f"❌ Gaps Backend: Error in wardrobe gap analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze wardrobe gaps"
        )

@router.get("/coverage")
async def get_wardrobe_coverage(current_user: UserProfile = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get wardrobe coverage metrics for the current user.
    
    Returns coverage percentages for:
    - Essential items
    - Occasion types
    - Style categories
    - Seasonal coverage
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        analysis_service = WardrobeAnalysisService()
        analysis = await analysis_service.get_wardrobe_gaps(current_user.id)
        
        return {
            "success": True,
            "data": {
                "coverage": analysis["coverage"],
                "total_items": len(analysis.get("gaps", [])),
                "high_priority_gaps": len([g for g in analysis.get("gaps", []) if g["severity"] == "high"]),
                "medium_priority_gaps": len([g for g in analysis.get("gaps", []) if g["severity"] == "medium"]),
                "low_priority_gaps": len([g for g in analysis.get("gaps", []) if g["severity"] == "low"])
            },
            "message": "Wardrobe coverage analysis completed successfully"
        }
    except Exception as e:
        print(f"Error in wardrobe coverage analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze wardrobe coverage"
        )

@router.get("/recommendations")
async def get_wardrobe_recommendations(current_user: UserProfile = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get personalized wardrobe recommendations for the current user.
    
    Returns:
    - Smart recommendations based on current wardrobe
    - Suggested items to add
    - Style and occasion improvements
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        analysis_service = WardrobeAnalysisService()
        analysis = await analysis_service.get_wardrobe_gaps(current_user.id)
        
        # Extract high-priority recommendations
        high_priority_gaps = [g for g in analysis.get("gaps", []) if g["severity"] == "high"]
        suggested_items = []
        
        for gap in high_priority_gaps[:5]:  # Top 5 high-priority gaps
            suggested_items.extend(gap.get("suggestedItems", []))
        
        # Remove duplicates
        suggested_items = list(set(suggested_items))
        
        return {
            "success": True,
            "data": {
                "recommendations": analysis.get("recommendations", []),
                "suggested_items": suggested_items,
                "priority_gaps": high_priority_gaps[:3],  # Top 3 gaps
                "total_gaps": len(analysis.get("gaps", []))
            },
            "message": "Wardrobe recommendations generated successfully"
        }
    except Exception as e:
        print(f"Error in wardrobe recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate wardrobe recommendations"
        )

@router.get("/validation-errors")
async def get_validation_errors(current_user: UserProfile = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get validation errors and outfit generation failures for the current user.
    
    Returns:
    - Recent validation errors
    - Outfit generation failures
    - Error patterns and trends
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        analysis_service = WardrobeAnalysisService()
        validation_errors = await analysis_service._get_validation_errors(current_user.id)
        outfit_history = await analysis_service._get_outfit_history(current_user.id)
        
        # Analyze error patterns
        error_patterns = analysis_service._analyze_error_patterns(validation_errors, outfit_history)
        
        return {
            "success": True,
            "data": {
                "validation_errors": validation_errors,
                "outfit_failures": [outfit for outfit in outfit_history if not outfit.get("success", True)],
                "error_patterns": error_patterns,
                "total_errors": len(validation_errors),
                "failure_rate": len([o for o in outfit_history if not o.get("success", True)]) / max(len(outfit_history), 1) * 100
            },
            "message": "Validation error analysis completed successfully"
        }
    except Exception as e:
        print(f"Error in validation error analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze validation errors"
        )

@router.get("/trending-styles")
async def get_trending_styles(gender: str = None, current_user: UserProfile = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current trending styles and fashion trends, optionally filtered by gender.
    
    Parameters:
    - gender: Optional gender filter ("male", "female", or None for unisex/all)
    
    Returns:
    - Trending style names and descriptions
    - Popularity scores
    - Key items for each trend
    - Color palettes
    """
    try:
        # Use user's gender if not specified
        if not gender and current_user and current_user.gender:
            gender = current_user.gender
        
        # Try to get real trends directly first
        try:
            from src.services.fashion_trends_service import FashionTrendsService
            
            trends_service = FashionTrendsService()
            trending_styles = await trends_service.get_trending_styles(gender)
            
            if trending_styles and len(trending_styles) > 0:
                print(f"✅ API: Successfully retrieved {len(trending_styles)} real trends for gender: {gender or 'unisex'}")
                return {
                    "success": True,
                    "data": {
                        "trending_styles": trending_styles,
                        "total_trends": len(trending_styles),
                        "gender_filter": gender,
                        "most_popular": max(trending_styles, key=lambda x: x.get("popularity", 0)) if trending_styles else None,
                        "message": f"Real trending styles retrieved successfully for {gender or 'all genders'}"
                    }
                }
            else:
                print("⚠️ API: No real trends available, using fallback data")
        except Exception as e:
            print(f"❌ API: Error getting real trends: {e}")
        
        # Fallback to curated trends if real trends fail
        fallback_trends = [
            {
                "name": "Coastal Grandmother",
                "description": "Sophisticated, relaxed style inspired by coastal living",
                "popularity": 85,
                "trend_direction": "increasing",
                "category": "lifestyle",
                "key_items": ["linen dresses", "straw hats", "neutral colors"],
                "colors": ["beige", "white", "navy", "sage"],
                "related_styles": ["minimalist", "elegant", "casual"],
                "last_updated": datetime.now().isoformat()
            },
            {
                "name": "Dark Academia",
                "description": "Intellectual, scholarly aesthetic with vintage elements",
                "popularity": 78,
                "trend_direction": "stable",
                "category": "academic",
                "key_items": ["blazers", "turtlenecks", "pleated skirts"],
                "colors": ["navy", "brown", "black", "cream"],
                "related_styles": ["vintage", "preppy", "intellectual"],
                "last_updated": datetime.now().isoformat()
            },
            {
                "name": "Y2K Revival",
                "description": "Early 2000s nostalgia with modern updates",
                "popularity": 72,
                "trend_direction": "increasing",
                "category": "nostalgic",
                "key_items": ["low-rise jeans", "crop tops", "platform shoes"],
                "colors": ["pink", "purple", "silver", "white"],
                "related_styles": ["retro", "playful", "trendy"],
                "last_updated": datetime.now().isoformat()
            }
        ]
        
        return {
            "success": True,
            "data": {
                "trending_styles": fallback_trends,
                "total_trends": len(fallback_trends),
                "gender_filter": gender,
                "most_popular": fallback_trends[0],
                "message": "Curated trending styles (real trends unavailable)"
            }
        }
        
    except Exception as e:
        print(f"Error getting trending styles: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve trending styles"
        )

@router.get("/wardrobe-stats")
async def get_wardrobe_stats(current_user_id: str = Depends(get_current_user_id)) -> Dict[str, Any]:
    """
    Get comprehensive wardrobe statistics for the current user.
    
    Returns:
    - Item type distribution
    - Color analysis
    - Style breakdown
    - Seasonal coverage
    - Brand preferences
    - Price analysis
    """
    try:
        if not current_user_id:
            raise HTTPException(status_code=400, detail="User not found")
            
        print(f"🔍 DEBUG: Getting wardrobe stats for user: {current_user_id}")
        analysis_service = WardrobeAnalysisService()
        wardrobe = await analysis_service._get_user_wardrobe(current_user_id)
        print(f"🔍 DEBUG: Retrieved {len(wardrobe)} wardrobe items for user: {current_user_id}")
        stats = analysis_service._get_wardrobe_stats(wardrobe)
        print(f"🔍 DEBUG: Generated stats: {stats}")
        
        return {
            "success": True,
            "data": stats,
            "message": "Wardrobe statistics retrieved successfully"
        }
    except Exception as e:
        print(f"Error getting wardrobe stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get wardrobe statistics"
        )

@router.post("/force-refresh-trends")
async def force_refresh_trends() -> Dict[str, Any]:
    """
    Force refresh fashion trends by bypassing the daily fetch check.
    This will fetch fresh data from Google Trends regardless of when it was last fetched.
    """
    try:
        from src.services.fashion_trends_service import FashionTrendsService
        
        print("🔄 Force refreshing fashion trends...")
        
        trends_service = FashionTrendsService()
        
        # Clear the fetch log to bypass the daily check
        try:
            today = datetime.now().date().isoformat()
            fetch_log_ref = trends_service.db.collection("fashion_trends_fetch_log").document(today)
            fetch_log_ref.delete()
            print(f"🗑️ Cleared fetch log for {today}")
        except Exception as e:
            print(f"⚠️ Warning: Could not clear fetch log: {e}")
        
        # Force fetch new trends
        result = await trends_service.fetch_and_store_trends()
        
        if result["status"] == "success":
            print(f"✅ Force refresh successful: {result['trends_fetched']} trends fetched")
            
            # Get the updated trends
            trending_styles = await trends_service.get_trending_styles()
            
            return {
                "success": True,
                "data": {
                    "trending_styles": trending_styles,
                    "total_trends": len(trending_styles),
                    "most_popular": max(trending_styles, key=lambda x: x["popularity"]) if trending_styles else None,
                    "refresh_timestamp": datetime.now().isoformat()
                },
                "message": f"Successfully refreshed {result['trends_fetched']} trends"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to refresh trends: {result.get('reason', 'Unknown error')}"
            }
            
    except Exception as e:
        print(f"❌ Error in force refresh: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to force refresh trends: {str(e)}"
        ) 