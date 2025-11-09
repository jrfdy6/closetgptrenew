"""
Main Hybrid Outfit Generation Router
====================================

This router integrates the proven personalization demo hybrid system
into the main app's /api/outfits endpoints. It provides both simple-minimal
and robust generation modes using the modular architecture that's already
working in the personalization demo.

Based on the successful personalization demo implementation.
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.utils.auth_utils import extract_uid_from_request
from src.auth.auth_service import get_current_user_id

from src.services.outfit_service import OutfitService
from src.core.exceptions import ValidationError, DatabaseError
from src.custom_types.outfit import OutfitUpdate

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    tags=["outfits-main-hybrid"]
)

# Security
security = HTTPBearer(auto_error=False)

# Import the proven personalization service with fallback
try:
    from src.routes.personalization_demo.personalization_service import PersonalizationService
    from src.routes.personalization_demo.models import (
        PersonalizationDemoRequest,
        PersonalizationDemoResponse
    )
    PERSONALIZATION_SERVICE_AVAILABLE = True
    logger.info("✅ Personalization service imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import personalization service: {e}")
    PERSONALIZATION_SERVICE_AVAILABLE = False
    
    # Create fallback classes
    class PersonalizationDemoRequest:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PersonalizationDemoResponse:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PersonalizationService:
        async def generate_personalized_outfit(self, request):
            return PersonalizationDemoResponse(
                id="fallback",
                name="Fallback Outfit",
                items=[],
                reasoning="Service unavailable - using fallback"
            )

# Initialize personalization service
if PERSONALIZATION_SERVICE_AVAILABLE:
    personalization_service = PersonalizationService()
else:
    personalization_service = None

outfit_service = OutfitService()

@router.get("/health")
async def health_check():
    """Health check for the main hybrid outfit generation system"""
    try:
        return {
            "status": "healthy",
            "main_outfit_generation_enabled": True,
            "available_generation_modes": ["simple-minimal", "robust"],
            "uses_hybrid_architecture": True,
            "personalization_service_available": PERSONALIZATION_SERVICE_AVAILABLE,
            "integration_status": "migrated_from_demo",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ Main outfit generation health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "main_outfit_generation_enabled": False
        }


@router.get("/{outfit_id}")
async def get_outfit_detail(
    outfit_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Retrieve a single outfit by ID for the authenticated user."""
    try:
        outfit = await outfit_service.get_outfit_by_id(current_user_id, outfit_id)
        if not outfit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outfit not found"
            )
        return {
            "success": True,
            "data": outfit.dict(),
            "message": "Outfit retrieved successfully"
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"❌ Failed to get outfit {outfit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve outfit"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error retrieving outfit {outfit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve outfit"
        )


@router.put("/{outfit_id}")
async def update_outfit_detail(
    outfit_id: str,
    payload: OutfitUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update an existing outfit."""
    try:
        updated = await outfit_service.update_outfit(current_user_id, outfit_id, payload)
        return {
            "success": True,
            "data": updated.dict(),
            "message": "Outfit updated successfully"
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"❌ Failed to update outfit {outfit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update outfit"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error updating outfit {outfit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update outfit"
        )


@router.post("/{outfit_id}/favorite")
async def toggle_outfit_favorite(
    outfit_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Toggle the favorite status of an outfit."""
    try:
        await outfit_service.toggle_outfit_favorite(current_user_id, outfit_id)
        return {
            "success": True,
            "message": "Outfit favorite status toggled successfully",
            "data": {"id": outfit_id}
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"❌ Failed to toggle favorite for outfit {outfit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle outfit favorite"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error toggling favorite for outfit {outfit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle outfit favorite"
        )

@router.post("/debug-filter")
async def debug_outfit_filtering(
    request: dict,
    req: Request
):
    """Debug endpoint to see why items are being filtered out during outfit generation."""
    try:
        if not PERSONALIZATION_SERVICE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Debug service is currently unavailable"
            )
        
        # ✅ FIX: Read semantic flag from POST body instead of query params
        # Query params were being stripped by Next.js proxy
        semantic = request.get('semantic', False)
        
        # Ensure it's a boolean
        if isinstance(semantic, str):
            semantic = semantic.lower() in ['true', '1', 'yes']
        
        logger.warning(f"🚀 DEBUG FILTER v6: semantic from body = {semantic} (type={type(semantic).__name__})")
        logger.warning(f"🔍 REQUEST BODY KEYS: {list(request.keys())}")
        
        # Extract user ID using robust authentication, with fallback for testing
        try:
            current_user_id = extract_uid_from_request(req)
        except HTTPException as auth_error:
            # For debug purposes, allow test mode with a fallback user ID
            logger.warning(f"🔍 DEBUG: Authentication failed, using test mode: {auth_error.detail}")
            current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # TEMPORARY: Use real user for debug
        
        logger.info(f"🔍 DEBUG FILTER: Request from user: {current_user_id}")
        logger.info(f"🔍 DEBUG FILTER: Request data: {request}")
        
        # TEMPORARY: Auto-fetch wardrobe if empty
        wardrobe_items = request.get("wardrobe", [])
        if len(wardrobe_items) == 0:
            logger.info(f"🔍 DEBUG FILTER: Wardrobe empty, fetching from Firebase...")
            try:
                from src.config.firebase import db
                docs = db.collection('wardrobe').where('userId', '==', current_user_id).stream()
                wardrobe_items = [doc.to_dict() for doc in docs]
                logger.info(f"✅ DEBUG FILTER: Fetched {len(wardrobe_items)} items from Firebase")
            except Exception as e:
                logger.error(f"❌ DEBUG FILTER: Failed to fetch wardrobe: {e}")
        
        # Create debug request
        demo_request = PersonalizationDemoRequest(
            occasion=request.get("occasion", "casual"),
            style=request.get("style", "casual"),
            mood=request.get("mood", "comfortable"),
            weather=request.get("weather"),
            wardrobe=wardrobe_items,
            user_profile=request.get("user_profile"),
            baseItemId=request.get("baseItemId"),
            generation_mode="debug"  # Special debug mode
        )
        
        # Get debug analysis from personalization service
        logger.warning(f"🔥 CALLING debug_outfit_filtering with semantic_filtering={semantic} (type={type(semantic).__name__})")
        debug_result = await personalization_service.debug_outfit_filtering(
            demo_request,
            current_user_id,
            semantic_filtering=semantic
        )
        
        logger.warning(f"✅ DEBUG FILTER: Analysis complete (semantic={semantic})")
        
        # Use enhanced debug output format
        try:
            from src.utils.enhanced_debug_output import format_final_debug_response
            
            enhanced_response = format_final_debug_response(
                outfits=[],  # No outfits generated in debug mode
                debug_analysis=debug_result.get('debug_analysis', []),
                semantic_mode=semantic,
                requested_style=demo_request.style,
                requested_occasion=demo_request.occasion,
                requested_mood=demo_request.mood,
                debug_output=debug_result.get('debug_output')
            )
            
            return {
                "success": True,
                **enhanced_response,
                "filters_applied": {
                    "occasion": demo_request.occasion,
                    "style": demo_request.style,
                    "mood": demo_request.mood,
                    "weather": demo_request.weather,
                    "semantic_mode": semantic
                },
                "timestamp": time.time(),
                "user_id": current_user_id
            }
        except ImportError:
            # Fallback to original format if enhanced output not available
            return {
                "success": True,
                "debug_analysis": debug_result,
                "filters_applied": {
                    "occasion": demo_request.occasion,
                    "style": demo_request.style,
                    "mood": demo_request.mood,
                    "weather": demo_request.weather,
                    "semantic_mode": semantic
                },
                "timestamp": time.time(),
                "user_id": current_user_id
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ DEBUG FILTER: Failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug analysis failed: {str(e)}"
        )

@router.post("/generate")
async def generate_outfit(
    request: dict,
    req: Request
):
    """
    Main outfit generation endpoint with hybrid architecture.
    
    Supports both simple-minimal and robust generation modes.
    Uses the proven personalization demo system under the hood.
    """
    try:
        if not PERSONALIZATION_SERVICE_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Outfit generation service is currently unavailable"
            )
        
        # Extract user ID using robust authentication
        current_user_id = extract_uid_from_request(req)
        
        logger.info(f"🎯 Main outfit generation request from user: {current_user_id}")
        logger.info(f"📋 Request data: {request}")
        
        # Extract generation mode from request, default to robust
        generation_mode = request.get("generation_mode", "robust")
        
        # Convert request to personalization demo format
        demo_request = PersonalizationDemoRequest(
            occasion=request.get("occasion", "casual"),
            style=request.get("style", "casual"),
            mood=request.get("mood", "comfortable"),
            weather=request.get("weather"),  # Changed from weather_data to weather
            wardrobe=request.get("wardrobe", []),  # CRITICAL: Pass wardrobe data
            user_profile=request.get("user_profile"),
            baseItemId=request.get("baseItemId"),
            generation_mode=generation_mode
        )
        
        # Generate outfit using the proven personalization service
        result = await personalization_service.generate_personalized_outfit(
            demo_request,
            current_user_id
        )
        
        logger.info(f"✅ Main outfit generation successful with mode: {generation_mode}")
        
        # Convert response to main app format
        # Set validation metadata based on actual outfit quality
        result_metadata = result.metadata if hasattr(result, 'metadata') else {}
        if isinstance(result_metadata, dict):
            # Get the actual items from the result
            result_items = result.items if hasattr(result, 'items') else []
            item_count = len(result_items)
            
            # Validation checks:
            # - Minimum 3 items required for a complete outfit
            # - Must have essential categories (tops, bottoms, shoes)
            min_items_met = item_count >= 3
            
            # Check for essential categories
            has_top = False
            has_bottom = False
            has_shoes = False
            for item in result_items:
                # Get the actual enum value, not the enum representation
                item_type_obj = getattr(item, 'type', None)
                if item_type_obj:
                    # Try to get .value for enums, otherwise convert to string
                    item_type = str(getattr(item_type_obj, 'value', item_type_obj)).lower()
                else:
                    item_type = ''
                
                if 'shirt' in item_type or 'top' in item_type or 'blouse' in item_type or 'sweater' in item_type or 'jacket' in item_type:
                    has_top = True
                elif 'pants' in item_type or 'bottom' in item_type or 'skirt' in item_type or 'shorts' in item_type or 'jeans' in item_type:
                    has_bottom = True
                elif 'shoe' in item_type or 'boot' in item_type or 'sneaker' in item_type or 'sandal' in item_type:
                    has_shoes = True
            
            essential_categories_met = has_top and has_bottom and has_shoes
            
            # Overall validation: passed if minimum items AND essential categories
            validation_passed = min_items_met and essential_categories_met
            
            # Set validation flags based on actual checks
            result_metadata['validation_applied'] = True  # We always apply validation
            result_metadata['occasion_requirements_met'] = validation_passed
            result_metadata['deduplication_applied'] = True  # Always applied in robust service
            
            # Add debug info
            if not validation_passed:
                logger.warning(f"⚠️ VALIDATION FAILED: items={item_count}, min_items_met={min_items_met}, "
                             f"has_top={has_top}, has_bottom={has_bottom}, has_shoes={has_shoes}")
                result_metadata['validation_failure_reason'] = {
                    'item_count': item_count,
                    'min_items_met': min_items_met,
                    'essential_categories_met': essential_categories_met,
                    'has_top': has_top,
                    'has_bottom': has_bottom,
                    'has_shoes': has_shoes
                }
        
        # Build response
        response = {
            "success": True,
            "id": result.id if hasattr(result, 'id') else f"outfit_{int(time.time())}",
            "name": result.name if hasattr(result, 'name') else f"{request.get('style', 'Unknown')} {request.get('occasion', 'Outfit')}",
            "items": result.items if hasattr(result, 'items') else [],
            "style": result.style if hasattr(result, 'style') else request.get('style', 'unknown'),
            "occasion": result.occasion if hasattr(result, 'occasion') else request.get('occasion', 'unknown'),
            "mood": result.mood if hasattr(result, 'mood') else request.get('mood', 'unknown'),
            "weather": result.weather if hasattr(result, 'weather') else {},
            "confidence_score": result.confidence_score if hasattr(result, 'confidence_score') else 0.8,
            "personalization_score": result.personalization_score if hasattr(result, 'personalization_score') else None,
            "personalization_applied": result.personalization_applied if hasattr(result, 'personalization_applied') else True,
            "generation_mode": generation_mode,
            "generation_strategy": result.generation_strategy if hasattr(result, 'generation_strategy') else "hybrid",
            "data_source": result.data_source if hasattr(result, 'data_source') else "main_hybrid",
            "metadata": result_metadata,
            "timestamp": time.time(),
            "user_id": current_user_id
        }
        
        # 🔥 CRITICAL FIX: Save outfit to Firestore for diversity tracking
        try:
            from src.config.firebase import db
            
            # Convert ClothingItem objects to dicts for Firestore storage
            items_for_firestore = []
            for item in response['items']:
                if hasattr(item, 'dict'):
                    items_for_firestore.append(item.dict())
                elif isinstance(item, dict):
                    items_for_firestore.append(item)
                else:
                    items_for_firestore.append({
                        'id': getattr(item, 'id', 'unknown'),
                        'name': getattr(item, 'name', 'unknown'),
                        'type': getattr(item, 'type', 'unknown')
                    })
            
            outfit_for_firestore = {
                'id': response['id'],
                'name': response['name'],
                'items': items_for_firestore,
                'style': response['style'],
                'occasion': response['occasion'],
                'mood': response['mood'],
                'user_id': current_user_id,
                'createdAt': int(time.time() * 1000),  # Firestore timestamp in milliseconds
                'generation_mode': generation_mode,
                'generation_strategy': response['generation_strategy'],
                'confidence_score': response['confidence_score'],
                'metadata': result_metadata
            }
            
            db.collection('outfits').document(response['id']).set(outfit_for_firestore)
            logger.info(f"✅ Saved outfit {response['id']} to Firestore for diversity tracking")
            
        except Exception as save_error:
            # Don't fail the request if save fails, just log it
            logger.error(f"⚠️ Failed to save outfit to Firestore: {save_error}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Main outfit generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Outfit generation failed: {str(e)}"
        )

@router.post("/generate-simple")
async def generate_simple_outfit(
    request: dict,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Simple outfit generation endpoint - forces simple-minimal mode.
    
    Convenience endpoint for clients that specifically want simple generation.
    """
    try:
        # Force simple-minimal mode
        request["generation_mode"] = "simple-minimal"
        
        # Use the main generate endpoint
        return await generate_outfit(request, current_user_id)
        
    except Exception as e:
        logger.error(f"❌ Simple outfit generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simple outfit generation failed: {str(e)}"
        )

@router.post("/generate-robust")
async def generate_robust_outfit(
    request: dict,
    req: Request
):
    """
    Robust outfit generation endpoint - forces robust mode.
    
    Convenience endpoint for clients that specifically want robust generation.
    """
    try:
        # Force robust mode
        request["generation_mode"] = "robust"
        
        # Use the main generate endpoint
        return await generate_outfit(request, req)
        
    except Exception as e:
        logger.error(f"❌ Robust outfit generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Robust outfit generation failed: {str(e)}"
        )

@router.get("/debug-user")
async def debug_user_info(
    req: Request
):
    """
    Debug endpoint to check user authentication and service availability.
    """
    try:
        # Extract user ID using robust authentication
        current_user_id = extract_uid_from_request(req)
        
        return {
            "user_id": current_user_id,
            "personalization_service_available": PERSONALIZATION_SERVICE_AVAILABLE,
            "timestamp": time.time(),
            "status": "debug_info_retrieved"
        }
    except Exception as e:
        logger.error(f"❌ Debug user info failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug info retrieval failed: {str(e)}"
        )

@router.get("/status")
async def generation_status():
    """
    Get the current status of the outfit generation system.
    """
    try:
        return {
            "system_status": "operational",
            "generation_modes": ["simple-minimal", "robust"],
            "personalization_enabled": True,
            "hybrid_architecture": True,
            "service_availability": {
                "personalization_service": PERSONALIZATION_SERVICE_AVAILABLE,
                "main_endpoints": True
            },
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return {
            "system_status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

@router.get("")
async def get_outfits(
    req: Request,
    limit: int = 50,
    offset: int = 0
):
    """
    Get outfit history for the authenticated user.
    
    This endpoint fetches previously generated outfits from the outfit history.
    """
    try:
        # Extract user ID using robust authentication
        current_user_id = extract_uid_from_request(req)
        
        logger.info(f"📋 Fetching outfits for user: {current_user_id} (limit={limit}, offset={offset})")
        
        # Import Firebase
        from src.config.firebase import db
        
        # Query outfits collection (generated outfits with items arrays)
        # Using user_id + createdAt (matches existing index)
        query = db.collection('outfits')\
            .where('user_id', '==', current_user_id)\
            .order_by('createdAt', direction='DESCENDING')\
            .limit(limit)
        
        if offset > 0:
            # Get the last document from the previous page for pagination
            prev_query = db.collection('outfits')\
                .where('user_id', '==', current_user_id)\
                .order_by('createdAt', direction='DESCENDING')\
                .limit(offset)
            prev_docs = list(prev_query.stream())
            if prev_docs:
                query = query.start_after(prev_docs[-1])
        
        # Fetch outfits
        docs = query.stream()
        outfits = []
        
        for doc in docs:
            outfit_data = doc.to_dict()
            outfit_data['id'] = doc.id
            outfits.append(outfit_data)
        
        logger.info(f"✅ Retrieved {len(outfits)} generated outfits for user {current_user_id}")
        
        return {
            "success": True,
            "outfits": outfits,
            "count": len(outfits),
            "limit": limit,
            "offset": offset,
            "user_id": current_user_id,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to fetch outfits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch outfits: {str(e)}"
        )

@router.post("/rate")
async def rate_outfit(
    rating_data: dict,
    req: Request
) -> Dict[str, Any]:
    """
    Rate an outfit and update analytics for individual wardrobe items.
    This ensures the scoring system has accurate feedback data.
    """
    try:
        logger.info(f"📊 Rating outfit request received")
        
        # Extract user ID using robust authentication
        current_user_id = extract_uid_from_request(req)
        
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        outfit_id = rating_data.get('outfitId') if rating_data else None
        rating = rating_data.get('rating') if rating_data else None
        is_liked = rating_data.get('isLiked', False) if rating_data else False
        is_disliked = rating_data.get('isDisliked', False) if rating_data else False
        feedback = rating_data.get('feedback', '') if rating_data else ''
        
        logger.info(f"⭐ Rating outfit {outfit_id} for user {current_user_id}: {rating} stars")
        
        # Allow rating with just like/dislike feedback, or with star rating
        if not outfit_id:
            raise HTTPException(status_code=400, detail="Missing outfit ID")
        
        # If rating is provided, validate it's between 1-5
        if rating is not None and (rating < 1 or rating > 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Require at least some feedback (rating, like, dislike, or text feedback)
        if not rating and not is_liked and not is_disliked and not feedback.strip():
            raise HTTPException(status_code=400, detail="At least one form of feedback is required (rating, like, dislike, or comment)")
        
        # Update outfit with rating data
        try:
            from src.config.firebase import db
        except ImportError:
            raise HTTPException(status_code=503, detail="Database service unavailable")
            
        outfit_ref = db.collection('outfits').document(outfit_id)
        outfit_doc = outfit_ref.get() if outfit_ref else None
        
        if not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        # Check both possible user ID field names for compatibility
        outfit_user_id = outfit_data.get('userId') if outfit_data else None
        if not outfit_user_id:
            outfit_user_id = outfit_data.get('user_id')
        
        if outfit_user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to rate this outfit")
        
        # Update outfit with rating
        outfit_ref.update({
            'rating': rating,
            'isLiked': is_liked,
            'isDisliked': is_disliked,
            'feedback': feedback,
            'ratedAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        })
        
        # Update analytics for individual wardrobe items
        await _update_item_analytics_from_outfit_rating(
            outfit_data.get('items', []) if outfit_data else [],
            current_user_id, 
            rating, 
            is_liked, 
            is_disliked, 
            feedback
        )
        
        logger.info(f"✅ Successfully rated outfit {outfit_id} and updated item analytics")
        
        return {
            "success": True,
            "message": "Outfit rated successfully",
            "outfit_id": outfit_id,
            "rating": rating
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to rate outfit: {e}")
        raise HTTPException(status_code=500, detail="Failed to rate outfit")

async def _update_item_analytics_from_outfit_rating(
    outfit_items: List[Dict], 
    user_id: str, 
    rating: int, 
    is_liked: bool, 
    is_disliked: bool, 
    feedback: str
) -> None:
    """
    Update analytics for individual wardrobe items based on outfit rating.
    This ensures the scoring system has accurate feedback data for each item.
    """
    try:
        from src.config.firebase import db
        
        logger.info(f"📊 Updating analytics for {len(outfit_items)} items from outfit rating")
        
        current_time = datetime.utcnow()
        updated_count = 0
        
        for item in outfit_items:
            item_id = item.get('id') if item else None
            if not item_id:
                continue
            
            try:
                # Check if analytics document exists for this item
                analytics_ref = db.collection('item_analytics').document(f"{user_id}_{item_id}")
                analytics_doc = analytics_ref.get() if analytics_ref else None
                
                if analytics_doc.exists:
                    # Update existing analytics
                    current_data = analytics_doc.to_dict()
                    
                    # Update feedback ratings
                    feedback_ratings = current_data.get('feedback_ratings', []) if current_data else []
                    feedback_ratings.append({
                        'rating': rating,
                        'outfit_rating': rating,
                        'is_liked': is_liked,
                        'is_disliked': is_disliked,
                        'feedback': feedback,
                        'timestamp': current_time
                    })
                    
                    # Calculate new average rating
                    total_rating = sum((fr.get('rating', 0) if fr else 0) for fr in feedback_ratings)
                    avg_rating = total_rating / len(feedback_ratings)
                    
                    analytics_ref.update({
                        'feedback_ratings': feedback_ratings,
                        'average_feedback_rating': round(avg_rating, 2),
                        'total_feedback_count': len(feedback_ratings),
                        'last_feedback_at': current_time,
                        'updatedAt': current_time
                    })
                    
                    updated_count += 1
                    logger.info(f"✅ Updated analytics for item {item_id}")
                else:
                    # Create new analytics document
                    analytics_ref.set({
                        'user_id': user_id,
                        'item_id': item_id,
                        'feedback_ratings': [{
                            'rating': rating,
                            'outfit_rating': rating,
                            'is_liked': is_liked,
                            'is_disliked': is_disliked,
                            'feedback': feedback,
                            'timestamp': current_time
                        }],
                        'average_feedback_rating': float(rating) if rating else 0.0,
                        'total_feedback_count': 1,
                        'last_feedback_at': current_time,
                        'createdAt': current_time,
                        'updatedAt': current_time
                    })
                    
                    updated_count += 1
                    logger.info(f"✅ Created analytics for item {item_id}")
                    
            except Exception as item_error:
                logger.error(f"❌ Failed to update analytics for item {item_id}: {item_error}")
                # Continue with other items even if one fails
                continue
        
        logger.info(f"✅ Successfully updated analytics for {updated_count}/{len(outfit_items)} items")
        
    except Exception as e:
        logger.error(f"❌ Failed to update item analytics: {e}")
        # Don't raise exception - analytics update is not critical for rating success


@router.post("")
async def create_outfit(
    request: dict,
    req: Request
) -> Dict[str, Any]:
    """
    Create a custom outfit by manually selecting items from the user's wardrobe.
    REST endpoint: POST /api/outfits
    """
    try:
        # Extract user ID using robust authentication
        current_user_id = extract_uid_from_request(req)
        
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Extract data from request
        name = request.get('name')
        occasion = request.get('occasion', 'Casual')
        style = request.get('style', 'Classic')
        description = request.get('description', '')
        items = request.get('items', [])
        
        if not name:
            raise HTTPException(status_code=400, detail="Outfit name is required")
        
        if not items or len(items) == 0:
            raise HTTPException(status_code=400, detail="At least one item is required")
        
        logger.info(f"🎨 Creating custom outfit: {name}")
        logger.info(f"  - occasion: {occasion}")
        logger.info(f"  - style: {style}")
        logger.info(f"  - items count: {len(items)}")
        logger.info(f"  - user_id: {current_user_id}")
        
        # Import here to avoid circular imports
        from uuid import uuid4
        
        # Normalize items to match OutfitItem schema expectations
        normalized_items = []
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                logger.warning(f"⚠️ Invalid item format at index {idx}: {item}")
                continue
            
            normalized = item.copy()
            
            normalized.setdefault("id", normalized.get("id") or normalized.get("itemId") or f"custom_item_{idx}")
            normalized.setdefault("name", normalized.get("name") or normalized.get("title") or "Unnamed Item")
            
            user_id_value = normalized.get("userId") or normalized.get("user_id") or current_user_id
            normalized["userId"] = user_id_value
            normalized["user_id"] = user_id_value
            
            # Derive type/subType/category information
            category_value = normalized.get("category") or normalized.get("type") or normalized.get("subType")
            if isinstance(category_value, str):
                normalized["category"] = category_value
            
            normalized["subType"] = normalized.get("subType") or category_value or "general"
            normalized["type"] = normalized.get("type") or category_value or normalized["subType"]
            
            # Ensure color and imagery fields exist
            normalized["color"] = normalized.get("color") or normalized.get("primaryColor") or "unknown"
            normalized["imageUrl"] = normalized.get("imageUrl") or normalized.get("image_url") or normalized.get("image") or ""
            if normalized.get("thumbnailUrl") is None and normalized.get("thumbnail_url"):
                normalized["thumbnailUrl"] = normalized.get("thumbnail_url")
            if normalized.get("backgroundRemovedUrl") is None and normalized.get("background_removed_url"):
                normalized["backgroundRemovedUrl"] = normalized.get("background_removed_url")
            
            # List fields required by OutfitItem schema
            style_value = normalized.get("style")
            if isinstance(style_value, str):
                normalized["style"] = [style_value]
            elif isinstance(style_value, list) and style_value:
                normalized["style"] = style_value
            else:
                normalized["style"] = ["casual"]
            
            occasion_value = normalized.get("occasion")
            if isinstance(occasion_value, str):
                normalized["occasion"] = [occasion_value]
            elif isinstance(occasion_value, list) and occasion_value:
                normalized["occasion"] = occasion_value
            else:
                normalized["occasion"] = [occasion or "Casual"]
            
            if normalized.get("dominantColors") is None or isinstance(normalized.get("dominantColors"), str):
                normalized["dominantColors"] = []
            if normalized.get("matchingColors") is None or isinstance(normalized.get("matchingColors"), str):
                normalized["matchingColors"] = []
            
            if normalized.get("metadata") is None:
                normalized["metadata"] = {}
            
            normalized_items.append(normalized)
        
        if not normalized_items:
            raise HTTPException(status_code=400, detail="Unable to process outfit items")
        
        # Create outfit data
        outfit_id = str(uuid4())
        from firebase_admin import firestore
        server_timestamp = firestore.SERVER_TIMESTAMP
        current_time_ms = int(time.time() * 1000)
        
        outfit_data = {
            "id": outfit_id,
            "name": name,
            "occasion": occasion,
            "style": style,
            "description": description,
            "items": normalized_items,
            "user_id": current_user_id,
            "createdAt": current_time_ms,
            "updatedAt": current_time_ms,
            "created_at": server_timestamp,
            "updated_at": server_timestamp,
            "is_custom": True,
            "confidence_score": 1.0,
            "reasoning": f"Custom outfit created by user: {description or 'No description provided'}",
            "explanation": description or f"Custom {style} outfit for {occasion}",
            "styleTags": [style.lower().replace(' ', '_') if style else 'custom_style'],
            "colorHarmony": "custom",
            "styleNotes": f"Custom {style} style selected by user" if style else "Custom outfit selected by user",
            "season": "all",
            "mood": "custom",
            "metadata": {"created_method": "custom"},
            "wasSuccessful": True,
            "wearCount": 0,
            "isFavorite": False
        }
        
        # Save to Firestore
        try:
            from src.config.firebase import db
            if db:
                db.collection('outfits').document(outfit_id).set(outfit_data)
                logger.info(f"✅ Saved outfit {outfit_id} to Firestore with {len(items)} items")
            else:
                logger.warning("⚠️ Firebase not available, outfit not saved to database")
                raise HTTPException(status_code=500, detail="Database not available")
        except Exception as save_error:
            logger.error(f"❌ Failed to save outfit to Firestore: {save_error}")
            raise HTTPException(status_code=500, detail=f"Failed to save outfit: {str(save_error)}")
        
        logger.info(f"✅ Outfit created: {outfit_id} for user {current_user_id}")
        
        # Return response
        return {
            "success": True,
            "id": outfit_data["id"],
            "name": outfit_data["name"],
            "items": normalized_items,
            "style": outfit_data["style"],
            "occasion": outfit_data["occasion"],
            "description": outfit_data.get("description", ""),
            "createdAt": current_time_ms,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating custom outfit: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{outfit_id}")
async def delete_outfit(
    outfit_id: str,
    req: Request
) -> Dict[str, Any]:
    """
    Delete an outfit.
    REST endpoint: DELETE /api/outfits/{outfit_id}
    """
    try:
        # Extract user ID using robust authentication
        current_user_id = extract_uid_from_request(req)
        
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        logger.info(f"🗑️ Deleting outfit: {outfit_id} for user {current_user_id}")
        
        # Get the outfit to verify ownership
        from src.config.firebase import db
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        outfit_ref = db.collection('outfits').document(outfit_id)
        outfit_doc = outfit_ref.get()
        
        if not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        
        # Verify the outfit belongs to the current user
        if outfit_data.get('user_id') != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this outfit")
        
        # Delete the outfit
        outfit_ref.delete()
        logger.info(f"✅ Deleted outfit {outfit_id} for user {current_user_id}")
        
        return {
            "success": True,
            "message": "Outfit deleted successfully",
            "id": outfit_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting outfit: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
