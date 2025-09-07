from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..services.analytics_service import (
    log_item_interaction,
    log_outfit_generation,
    log_outfit_feedback,
    get_user_favorites,
    get_favorite_by_type,
    ItemInteractionType
)
from ..routes.auth import get_current_user_id
from ..custom_types.wardrobe import ClothingItem

router = APIRouter(prefix="/api/item-analytics", tags=["item-analytics"])
logger = logging.getLogger(__name__)

class ItemInteractionRequest(BaseModel):
    item_id: str = Field(..., description="ID of the clothing item")
    interaction_type: ItemInteractionType = Field(..., description="Type of interaction")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context data")

class OutfitGenerationTrackingRequest(BaseModel):
    outfit_id: str = Field(..., description="ID of the generated outfit")
    item_ids: List[str] = Field(..., description="List of item IDs in the outfit")
    base_item_id: Optional[str] = Field(None, description="ID of the base item if any")

class OutfitFeedbackTrackingRequest(BaseModel):
    outfit_id: str = Field(..., description="ID of the outfit")
    feedback_rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_type: str = Field(..., description="Type of feedback (like, dislike, issue)")
    item_ids: List[str] = Field(..., description="List of item IDs in the outfit")

class ItemAnalyticsResponse(BaseModel):
    success: bool
    message: str
    analytics_id: Optional[str] = None

class FavoritesResponse(BaseModel):
    success: bool
    favorites: List[Dict[str, Any]]
    total_count: int

class ToggleFavoriteRequest(BaseModel):
    item_id: str = Field(..., description="ID of the clothing item to toggle favorite status")

class ToggleFavoriteResponse(BaseModel):
    success: bool
    message: str
    is_favorite: bool
    item_id: str

@router.post("/track-interaction", response_model=ItemAnalyticsResponse)
async def track_item_interaction(
    request: ItemInteractionRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Track a user interaction with an item."""
    try:
        analytics_id = log_item_interaction(
            user_id=current_user_id,
            item_id=request.item_id,
            interaction_type=request.interaction_type,
            metadata=request.metadata
        )
        
        return ItemAnalyticsResponse(
            success=True,
            message="Interaction tracked successfully",
            analytics_id=analytics_id
        )
        
    except Exception as e:
        logger.error(f"Error tracking item interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-outfit-generation", response_model=ItemAnalyticsResponse)
async def track_outfit_generation(
    request: OutfitGenerationTrackingRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Track when items are used in outfit generation."""
    try:
        # Get the actual ClothingItem objects from wardrobe
        from ..config.firebase import db
        
        items = []
        base_item = None
        
        for item_id in request.item_ids:
            item_ref = db.collection("wardrobe").document(item_id)
            item_doc = item_ref.get()
            
            if item_doc.exists:
                item_data = item_doc.to_dict()
                item_data['id'] = item_id
                clothing_item = ClothingItem(**item_data)
                items.append(clothing_item)
                
                if item_id == request.base_item_id:
                    base_item = clothing_item
        
        log_outfit_generation(
            user_id=current_user_id,
            outfit_id=request.outfit_id,
            items=items,
            base_item=base_item
        )
        
        return ItemAnalyticsResponse(
            success=True,
            message="Outfit generation tracked successfully"
        )
        
    except Exception as e:
        logger.error(f"Error tracking outfit generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track-outfit-feedback", response_model=ItemAnalyticsResponse)
async def track_outfit_feedback(
    request: OutfitFeedbackTrackingRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Track feedback for outfits and update item scores."""
    try:
        log_outfit_feedback(
            user_id=current_user_id,
            outfit_id=request.outfit_id,
            feedback_rating=request.feedback_rating,
            feedback_type=request.feedback_type,
            outfit_items=request.item_ids
        )
        
        return ItemAnalyticsResponse(
            success=True,
            message="Outfit feedback tracked successfully"
        )
        
    except Exception as e:
        logger.error(f"Error tracking outfit feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/favorites", response_model=FavoritesResponse)
async def get_user_favorites_endpoint(
    item_type: Optional[str] = None,
    limit: int = 10,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get user's favorite items, optionally filtered by type."""
    try:
        favorites = get_user_favorites(
            user_id=current_user_id,
            item_type=item_type,
            limit=limit
        )
        
        return FavoritesResponse(
            success=True,
            favorites=favorites,
            total_count=len(favorites)
        )
        
    except Exception as e:
        logger.error(f"Error getting user favorites: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/favorites/{item_type}", response_model=FavoritesResponse)
async def get_favorite_by_type_endpoint(
    item_type: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get the user's favorite item of a specific type."""
    try:
        logger.info(f"Favorites endpoint called for user_id={current_user_id}, item_type={item_type}")
        favorite = get_favorite_by_type(
            user_id=current_user_id,
            item_type=item_type
        )
        
        favorites = [favorite] if favorite else []
        logger.info(f"Favorites endpoint result: {len(favorites)} favorites found for user_id={current_user_id}, item_type={item_type}")
        
        return FavoritesResponse(
            success=True,
            favorites=favorites,
            total_count=len(favorites)
        )
        
    except Exception as e:
        logger.error(f"Error getting favorite by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/favorites/top/{item_type}", response_model=FavoritesResponse)
async def get_top_favorites_by_type_endpoint(
    item_type: str,
    limit: int = 3,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get the user's top favorite items of a specific type."""
    try:
        favorites = get_user_favorites(
            user_id=current_user_id,
            item_type=item_type,
            limit=limit
        )
        
        return FavoritesResponse(
            success=True,
            favorites=favorites,
            total_count=len(favorites)
        )
        
    except Exception as e:
        logger.error(f"Error getting top favorites by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-favorites/{item_type}", response_model=FavoritesResponse)
async def test_get_favorite_by_type_endpoint(
    item_type: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Test endpoint to get the user's favorite item of a specific type with authentication."""
    try:
        logger.info(f"Test endpoint called for user {current_user_id}, type {item_type}")
        favorite = get_favorite_by_type(
            user_id=current_user_id,
            item_type=item_type
        )
        
        favorites = [favorite] if favorite else []
        logger.info(f"Test endpoint result: {len(favorites)} favorites found")
        
        return FavoritesResponse(
            success=True,
            favorites=favorites,
            total_count=len(favorites)
        )
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/favorites/toggle", response_model=ToggleFavoriteResponse)
async def toggle_item_favorite(
    request: ToggleFavoriteRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Toggle the favorite status of an item."""
    try:
        from ..config.firebase import db
        
        # Get the item from Firestore
        item_ref = db.collection("wardrobe").document(request.item_id)
        item_doc = item_ref.get()
        
        if not item_doc.exists:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item_data = item_doc.to_dict()
        current_favorite = item_data.get('favorite', False)
        
        # Toggle the favorite status
        new_favorite_status = not current_favorite
        
        # Update the item in Firestore
        item_ref.update({
            'favorite': new_favorite_status,
            'updatedAt': datetime.now().timestamp()
        })
        
        # Log the interaction
        log_item_interaction(
            user_id=current_user_id,
            item_id=request.item_id,
            interaction_type=ItemInteractionType.FAVORITE_TOGGLE,
            metadata={'new_status': new_favorite_status}
        )
        
        logger.info(f"Toggled favorite for item {request.item_id} to {new_favorite_status}")
        
        return ToggleFavoriteResponse(
            success=True,
            message=f"Item {'favorited' if new_favorite_status else 'unfavorited'} successfully",
            is_favorite=new_favorite_status,
            item_id=request.item_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling item favorite: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 