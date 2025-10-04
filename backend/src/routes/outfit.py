from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from typing import List, Optional, Dict, Any
from ..custom_types.outfit import Outfit, OutfitGenerationRequest, OutfitGeneratedOutfit
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile
from pydantic import BaseModel
# Temporarily comment out service imports to test router loading
# from ..services.outfit_service import OutfitService
# from ..services.outfit_generation_service import OutfitGenerationService
from ..auth.auth_service import get_current_user, get_current_user_optional
import time
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/outfit")
# outfit_service = OutfitService()  # Comment out for now
# outfit_generation_service = OutfitGenerationService()

@router.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"🔍 DEBUG: Validation error occurred:")
    print(f"  - URL: {request.url}")
    print(f"  - Method: {request.method}")
    print(f"  - Errors: {exc.errors()}")
    print(f"  - Body: {await request.body()}")
    return HTTPException(status_code=422, detail=f"Validation error: {exc.errors()}")

class OutfitGenerationRequest(BaseModel):
    occasion: str
    weather: WeatherData  # Frontend now sends proper WeatherData
    wardrobe: List[ClothingItem]  # Frontend now sends proper ClothingItem objects
    user_profile: UserProfile  # Frontend now sends proper UserProfile
    likedOutfits: Optional[List[str]] = []
    trendingStyles: Optional[List[str]] = []
    preferences: Optional[Dict[str, Any]] = None
    outfitHistory: Optional[List[Dict[str, Any]]] = None
    randomSeed: Optional[float] = None
    season: Optional[str] = None
    style: Optional[str] = None
    mood: Optional[str] = None  # Add mood parameter
    baseItem: Optional[ClothingItem] = None  # Frontend now sends proper ClothingItem
    baseItemId: Optional[str] = None  # Add baseItemId parameter

class OutfitFeedbackRequest(BaseModel):
    liked: bool
    rating: int  # 1-5 scale
    comment: Optional[str] = None
    worn: Optional[bool] = None
    occasion_used: Optional[str] = None

class CreateOutfitRequest(BaseModel):
    name: str
    occasion: str
    style: str
    description: Optional[str] = None
    items: List[Dict[str, Any]]
    createdAt: Optional[int] = None

class UpdateOutfitRequest(BaseModel):
    name: str
    occasion: str
    style: str
    description: Optional[str] = None
    items: List[str]  # Changed to List[str] since frontend sends item IDs



@(router.get("/") if router else None)
async def get_outfits():
    """Simple test endpoint to verify outfit router loads"""
    return {"message": "Outfit router is working!", "status": "success"}

@(router.get("/{outfit_id}") if router else None)
async def get_outfit(outfit_id: str):
    """Simple test endpoint to get outfit by ID"""
    return {"message": f"Getting outfit {outfit_id}", "outfit_id": outfit_id}

@router.post("/generate")
async def generate_outfit(request: OutfitGenerationRequest):
    print(f"🔍 DEBUG: Backend generate_outfit called [SIMPLE ENDPOINT v1.0]")
    print(f"🔍 DEBUG: Request data:")
    print(f"  - occasion: {request.occasion}")
    print(f"  - mood: {request.mood}")
    print(f"  - style: {request.style}")
    print(f"  - wardrobe size: {len(request.wardrobe)}")
    print(f"  - baseItemId: {request.baseItemId if request.baseItemId else 'None'}")
    print(f"  - user_profile.id: {request.user_profile.id}")
    print(f"🔍 DEBUG: Weather data: temp={request.weather.temperature}, condition={request.weather.condition}")
    print(f"🔍 DEBUG: First wardrobe item: {request.wardrobe[0].name if request.wardrobe else 'None'}")
    
    # Simple mock response for now
    mock_outfit = {
        "id": str(uuid.uuid4()),
        "name": f"Mock {request.style} Outfit for {request.occasion}",
        "occasion": request.occasion,
        "style": request.style,
        "mood": request.mood,
        "confidence": 85.0,
        "weather": {
            "temperature": request.weather.temperature,
            "condition": request.weather.condition
        },
        "items": [
            {
                "id": "mock-item-1",
                "name": "Mock Shirt",
                "type": "shirt",
                "color": "blue",
                "imageUrl": "",
                "style": ["casual"],
                "occasion": ["casual"],
                "brand": "",
                "wearCount": 0,
                "favorite_score": 0.0,
                "tags": [],
                "metadata": {}
            },
            {
                "id": "mock-item-2", 
                "name": "Mock Pants",
                "type": "pants",
                "color": "black",
                "imageUrl": "",
                "style": ["casual"],
                "occasion": ["casual"],
                "brand": "",
                "wearCount": 0,
                "favorite_score": 0.0,
                "tags": [],
                "metadata": {}
            },
            {
                "id": "mock-item-3",
                "name": "Mock Shoes", 
                "type": "shoes",
                "color": "white",
                "imageUrl": "",
                "style": ["casual"],
                "occasion": ["casual"],
                "brand": "",
                "wearCount": 0,
                "favorite_score": 0.0,
                "tags": [],
                "metadata": {}
            }
        ],
        "reasoning": "Mock outfit for testing endpoint connectivity",
        "createdAt": int(time.time()),
        "userId": request.user_profile.id
    }
    
    print(f"✅ DEBUG: Mock outfit generated successfully")
    return mock_outfit

# MOVED TO OUTFITS.PY - Using unified REST structure
# @router.post("/create", response_model=OutfitGeneratedOutfit)
# async def create_outfit(
#     request: CreateOutfitRequest
# ):
#     """
#     Create a custom outfit by manually selecting items from the user's wardrobe.
#     MOVED TO: outfits.py as POST /api/outfits for unified REST structure
#     """
# OLD IMPLEMENTATION - MOVED TO outfits.py for unified REST structure
#     try:
#         print(f"🔍 DEBUG: Backend create_outfit called")
#         ...implementation moved to outfits.py...
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    pass  # Placeholder since function is moved

# @router.put("/{outfit_id}/update", response_model=OutfitGeneratedOutfit)
# async def update_outfit(
#     outfit_id: str,
#     request: UpdateOutfitRequest,
#     current_user: UserProfile = Depends(get_current_user_optional)
# ):
#     """
#     Update an existing outfit with new details and items.
#     """
#     try:
#         print(f"🔍 DEBUG: Backend update_outfit called")
#         print(f"🔍 DEBUG: Request data:")
#         print(f"  - outfit_id: {outfit_id}")
#         print(f"  - name: {request.name}")
#         print(f"  - occasion: {request.occasion}")
#         print(f"  - style: {request.style}")
#         print(f"  - items count: {len(request.items)}")
#         
#         # Handle case where current_user might be None
#         if current_user is None:
#             print(f"❌ DEBUG: Authentication failed - current_user is None")
#             raise HTTPException(status_code=401, detail="Authentication required")
#         
#         print(f"  - user_profile.id: {current_user.id}")
#         
#         # Update outfit data
#         outfit_data = {
#             "name": request.name,
#             "occasion": request.occasion,
#             "style": request.style,
#             "description": request.description or "",
#             "items": request.items,
#             "updatedAt": int(time.time()),
#             "is_edited": True  # Mark as edited
#         }
#         
#         # Save to database
#         result = await outfit_service.update_outfit(outfit_id, outfit_data, current_user.id)
#         
#         print(f"✅ DEBUG: update_outfit completed successfully")
#         print(f"🔍 DEBUG: Updated outfit id: {result.id}")
#         return result
#         
#     except Exception as e:
#         print(f"❌ DEBUG: Error in update_outfit: {str(e)}")
#         print(f"🔍 DEBUG: Exception type: {type(e)}")
#         import traceback
#         print(f"🔍 DEBUG: Full traceback: {traceback.format_exc()}")
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/{outfit_id}/feedback")
# async def submit_outfit_feedback(
#     outfit_id: str, 
#     feedback: OutfitFeedbackRequest,
#     current_user: UserProfile = Depends(get_current_user)
# ):
#     """
#     Submit feedback for a generated outfit.
#     
#     - liked: Whether the user liked the outfit
#     - rating: Rating from 1-5
#     - comment: Optional comment
#     - worn: Whether the user actually wore the outfit
#     - occasion_used: What occasion they wore it for
#     """
#     try:
#         # Validate rating
#         if feedback.rating < 1 or feedback.rating > 5:
#             raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
#         
#         # Prepare feedback data
#         feedback_data = {
#             "liked": feedback.liked,
#             "rating": feedback.rating,
#             "comment": feedback.comment or "",
#             "worn": feedback.worn,
#             "occasion_used": feedback.occasion_used,
#             "user_id": current_user.id,
#             "timestamp": int(time.time())
#         }
#         
#         # Update outfit with feedback
#         success = await outfit_service.update_outfit_feedback(outfit_id, feedback_data)
#         
#         if not success:
#             raise HTTPException(status_code=500, detail="Failed to save feedback")
#         
#         return {
#             "success": True,
#             "message": "Feedback submitted successfully",
#             "outfit_id": outfit_id
#         }
#         
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

# @(router.get("/{outfit_id}/feedback") if router else None)
# async def get_outfit_feedback(
#     outfit_id: str,
#     current_user: UserProfile = Depends(get_current_user)
# ):
#     """Get feedback for a specific outfit."""
#     try:
#         outfit = await outfit_service.get_outfit(outfit_id)
#         if not outfit:
#             raise HTTPException(status_code=404, detail="Outfit not found")
#         
#         return {
#             "outfit_id": outfit_id,
#             "feedback": outfit.userFeedback
#         }
#         
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

 