from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import logging
from datetime import datetime

# Import the established pattern components
from ..routes.auth import get_current_user_id
from ..core.exceptions import ValidationError
from ..services.outfit_service import OutfitService
from ..custom_types.outfit import OutfitCreate, OutfitUpdate, OutfitResponse, OutfitFilters

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/outfits", tags=["outfits"])

# ===== ROUTES: Handle HTTP requests/responses and basic validation =====

@router.get("/")
async def get_user_outfits(
    current_user_id: str = Depends(get_current_user_id),
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    occasion: Optional[str] = None,
    style: Optional[str] = None,
    mood: Optional[str] = None
):
    """
    Get user's outfits with pagination and filtering.
    Follows the same pattern as wardrobe service.
    """
    try:
        logger.info(f"📚 Fetching outfits for user {current_user_id}")
        
        # Apply filters
        filters = OutfitFilters(
            occasion=occasion,
            style=style,
            mood=mood,
            limit=limit,
            offset=offset
        )
        
        # Call service layer (business logic)
        outfits = await OutfitService.get_user_outfits(current_user_id, filters)
        
        # Transform to response format
        outfit_responses = [outfit.dict() for outfit in outfits]
        
        logger.info(f"✅ Successfully retrieved {len(outfit_responses)} outfits")
        
        return {
            "success": True,
            "data": outfit_responses,
            "total": len(outfit_responses),
            "limit": limit or 50,
            "offset": offset or 0,
            "message": f"Successfully retrieved {len(outfit_responses)} outfits"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch outfits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch outfits"
        )

@router.get("/{outfit_id}")
async def get_outfit(
    outfit_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific outfit by ID.
    Follows the same pattern as wardrobe service.
    """
    try:
        logger.info(f"🔍 Getting outfit {outfit_id} for user {current_user_id}")
        
        # Call service layer (business logic)
        outfit = await OutfitService.get_outfit_by_id(current_user_id, outfit_id)
        
        if not outfit:
            raise ValidationError(f"Outfit {outfit_id} not found")
        
        # Transform to response format
        outfit_response = outfit.dict()
        
        logger.info(f"✅ Successfully retrieved outfit {outfit_id}")
        
        return {
            "success": True,
            "data": outfit_response,
            "message": "Outfit retrieved successfully"
        }
        
    except ValidationError as e:
        logger.warning(f"⚠️ Outfit not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Failed to get outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get outfit"
        )

@router.post("/")
async def create_outfit(
    outfit_data: OutfitCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new outfit.
    Follows the same pattern as wardrobe service.
    """
    try:
        logger.info(f"🎨 Creating outfit for user {current_user_id}")
        
        # Call service layer (business logic)
        outfit = await OutfitService.create_outfit(current_user_id, outfit_data)
        
        # Transform to response format
        outfit_response = outfit.dict()
        
        logger.info(f"✅ Successfully created outfit {outfit.id}")
        
        return {
            "success": True,
            "data": outfit_response,
            "message": "Outfit created successfully"
        }
        
    except ValidationError as e:
        logger.warning(f"⚠️ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Failed to create outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create outfit"
        )

@router.put("/{outfit_id}")
async def update_outfit(
    outfit_id: str,
    outfit_data: OutfitUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update an existing outfit.
    Follows the same pattern as wardrobe service.
    """
    try:
        logger.info(f"🔄 Updating outfit {outfit_id} for user {current_user_id}")
        
        # Call service layer (business logic)
        outfit = await OutfitService.update_outfit(current_user_id, outfit_id, outfit_data)
        
        # Transform to response format
        outfit_response = outfit.dict()
        
        logger.info(f"✅ Successfully updated outfit {outfit_id}")
        
        return {
            "success": True,
            "data": outfit_response,
            "message": "Outfit updated successfully"
        }
        
    except ValidationError as e:
        logger.warning(f"⚠️ Outfit not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Failed to update outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update outfit"
        )

@router.delete("/{outfit_id}")
async def delete_outfit(
    outfit_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete an outfit.
    Follows the same pattern as wardrobe service.
    """
    try:
        logger.info(f"🗑️ Deleting outfit {outfit_id} for user {current_user_id}")
        
        # Call service layer (business logic)
        await OutfitService.delete_outfit(current_user_id, outfit_id)
        
        logger.info(f"✅ Successfully deleted outfit {outfit_id}")
        
        return {
            "success": True,
            "message": "Outfit deleted successfully"
        }
        
    except ValidationError as e:
        logger.warning(f"⚠️ Outfit not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Failed to delete outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete outfit"
        )

@router.post("/{outfit_id}/mark-worn")
async def mark_outfit_as_worn(
    outfit_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Mark an outfit as worn.
    Follows the same pattern as wardrobe service.
    """
    try:
        logger.info(f"👕 Marking outfit {outfit_id} as worn for user {current_user_id}")
        
        # Call service layer (business logic)
        await OutfitService.mark_outfit_as_worn(current_user_id, outfit_id)
        
        logger.info(f"✅ Successfully marked outfit {outfit_id} as worn")
        
        return {
            "success": True,
            "message": "Outfit marked as worn successfully"
        }
        
    except ValidationError as e:
        logger.warning(f"⚠️ Outfit not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Failed to mark outfit as worn: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark outfit as worn"
        )

@router.post("/{outfit_id}/toggle-favorite")
async def toggle_outfit_favorite(
    outfit_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Toggle outfit favorite status.
    Follows the same pattern as wardrobe service.
    """
    try:
        logger.info(f"❤️ Toggling favorite for outfit {outfit_id} for user {current_user_id}")
        
        # Call service layer (business logic)
        await OutfitService.toggle_outfit_favorite(current_user_id, outfit_id)
        
        logger.info(f"✅ Successfully toggled favorite for outfit {outfit_id}")
        
        return {
            "success": True,
            "message": "Outfit favorite status toggled successfully"
        }
        
    except ValidationError as e:
        logger.warning(f"⚠️ Outfit not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Failed to toggle outfit favorite: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle outfit favorite"
        )

@router.get("/stats/summary")
async def get_outfit_stats(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get outfit statistics for user.
    Follows the same pattern as wardrobe service.
    """
    try:
        logger.info(f"📊 Getting outfit stats for user {current_user_id}")
        
        # Call service layer (business logic)
        stats = await OutfitService.get_outfit_stats(current_user_id)
        
        logger.info(f"✅ Successfully retrieved outfit stats")
        
        return {
            "success": True,
            "data": stats,
            "message": "Outfit statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get outfit stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get outfit statistics"
        )

# ===== HEALTH AND DEBUG ENDPOINTS =====

@router.get("/health")
async def outfits_health_check():
    """Health check for outfits router."""
    return {
        "success": True,
        "message": "Outfits router is healthy",
        "data": {
            "router": "outfits",
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    }

@router.get("/debug")
async def outfits_debug():
    """Debug endpoint for outfits router."""
    return {
        "success": True,
        "message": "Outfits router debug endpoint working",
        "data": {
            "router": "outfits",
            "status": "debug",
            "timestamp": datetime.now().isoformat()
        }
    }
