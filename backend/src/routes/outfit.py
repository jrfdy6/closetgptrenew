from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from typing import List, Optional, Dict, Any
from ..custom_types.outfit import Outfit, OutfitGenerationRequest, OutfitGeneratedOutfit
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile
from pydantic import BaseModel
from ..services.outfit_service import OutfitService
from ..services.outfit_generation_service import OutfitGenerationService
from ..auth.auth_service import get_current_user, get_current_user_optional
import time
import uuid

router = APIRouter(prefix="/api/outfit")
outfit_service = OutfitService()
outfit_generation_service = OutfitGenerationService()

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
    weather: Dict[str, Any]  # Accept plain dict, convert internally
    wardrobe: List[Dict[str, Any]]  # Accept plain dicts, convert internally
    user_profile: Dict[str, Any]  # Accept plain dict, convert internally
    likedOutfits: Optional[List[str]] = []
    trendingStyles: Optional[List[str]] = []
    preferences: Optional[Dict[str, Any]] = None
    outfitHistory: Optional[List[Dict[str, Any]]] = None
    randomSeed: Optional[float] = None
    season: Optional[str] = None
    style: Optional[str] = None
    mood: Optional[str] = None  # Add mood parameter
    baseItem: Optional[Dict[str, Any]] = None  # Accept plain dict
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



@router.get("/", response_model=List[OutfitGeneratedOutfit])
async def get_outfits(current_user: UserProfile = Depends(get_current_user)):
    logger.info("🚨 DEBUG: /api/outfit/ endpoint called (NOT /api/outfits/)")
    try:
        logger.info(f"🔍 [outfit.py] Fetching outfits for user: {current_user.id}")
        result = await outfit_service.get_outfits_by_user(current_user.id)
        logger.info(f"✅ [outfit.py] Successfully retrieved {len(result)} outfits")
        return result
    except Exception as e:
        logger.error(f"❌ [outfit.py] Error fetching outfits: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{outfit_id}", response_model=OutfitGeneratedOutfit)
async def get_outfit(outfit_id: str):
    try:
        outfit = await outfit_service.get_outfit(outfit_id)
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit not found")
        return outfit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=OutfitGeneratedOutfit)
async def generate_outfit(request: OutfitGenerationRequest):
    print(f"🔍 DEBUG: Backend generate_outfit called [COHESIVE COMPOSITION v2.1 - FORCE DEPLOY]")
    print(f"🔍 DEBUG: Request data:")
    print(f"  - occasion: {request.occasion}")
    print(f"  - mood: {request.mood}")
    print(f"  - style: {request.style}")
    print(f"  - wardrobe size: {len(request.wardrobe)}")
    print(f"  - baseItemId: {request.baseItemId if request.baseItemId else 'None'}")
    print(f"  - user_profile.id: {request.user_profile.get('id', 'None')}")
    print(f"🔍 DEBUG: Weather data: temp={request.weather.get('temperature', 'None')}, condition={request.weather.get('condition', 'None')}")
    print(f"🔍 DEBUG: First wardrobe item: {request.wardrobe[0].get('name', 'None') if request.wardrobe else 'None'}")
    
    # Convert plain objects to Pydantic models with robust error handling
    try:
        # Convert weather dict to WeatherData
        print(f"🔍 DEBUG: Converting weather data: {request.weather}")
        weather_data = WeatherData(**request.weather)
        
        # Convert wardrobe dicts to ClothingItem objects
        wardrobe_items = []
        print(f"🔍 DEBUG: Converting {len(request.wardrobe)} wardrobe items")
        
        for i, item_dict in enumerate(request.wardrobe):
            try:
                # Create a copy to avoid modifying original
                item_copy = item_dict.copy()
                
                # Ensure required fields have defaults
                item_copy.setdefault('season', ['all'])
                item_copy.setdefault('tags', [])
                item_copy.setdefault('style', [])
                item_copy.setdefault('occasion', ['casual'])
                item_copy.setdefault('dominantColors', [])
                item_copy.setdefault('matchingColors', [])
                item_copy.setdefault('wearCount', 0)
                item_copy.setdefault('favorite_score', 0.0)
                item_copy.setdefault('createdAt', int(time.time() * 1000))
                item_copy.setdefault('updatedAt', int(time.time() * 1000))
                item_copy.setdefault('userId', request.user_profile.get('id', 'unknown'))
                item_copy.setdefault('imageUrl', '')
                item_copy.setdefault('subType', None)
                item_copy.setdefault('colorName', None)
                item_copy.setdefault('backgroundRemoved', None)
                item_copy.setdefault('embedding', None)
                item_copy.setdefault('metadata', {})
                
                # Handle type field - convert string to ClothingType enum if needed
                if 'type' in item_copy and isinstance(item_copy['type'], str):
                    # Try to convert string type to ClothingType enum
                    try:
                        from ..custom_types.wardrobe import ClothingType
                        item_copy['type'] = ClothingType(item_copy['type'].lower())
                    except ValueError:
                        # If conversion fails, use a default type
                        item_copy['type'] = ClothingType.OTHER
                
                # Handle style field - ensure it's a list
                if isinstance(item_copy.get('style'), str):
                    item_copy['style'] = [item_copy['style']]
                elif not isinstance(item_copy.get('style'), list):
                    item_copy['style'] = []
                
                # Handle occasion field - ensure it's a list
                if isinstance(item_copy.get('occasion'), str):
                    item_copy['occasion'] = [item_copy['occasion']]
                elif not isinstance(item_copy.get('occasion'), list):
                    item_copy['occasion'] = ['casual']
                
                print(f"🔍 DEBUG: Converting item {i+1}: {item_copy.get('name', 'Unknown')}")
                clothing_item = ClothingItem(**item_copy)
                wardrobe_items.append(clothing_item)
                
            except Exception as e:
                print(f"⚠️ DEBUG: Failed to convert wardrobe item {i+1} ({item_dict.get('name', 'Unknown')}): {e}")
                print(f"🔍 DEBUG: Item data: {item_dict}")
                # Skip invalid items but continue processing
                continue
        
        # Convert user_profile dict to UserProfile
        print(f"🔍 DEBUG: Converting user profile: {request.user_profile}")
        user_profile = UserProfile(**request.user_profile)
        
        print(f"🔍 DEBUG: Successfully converted {len(wardrobe_items)} wardrobe items and user profile")
        
    except Exception as e:
        print(f"❌ DEBUG: Failed to convert request data: {e}")
        import traceback
        print(f"🔍 DEBUG: Conversion error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=422, detail=f"Invalid request data format: {str(e)}")
    
    # Debug: Check if base item is in wardrobe
    if request.baseItemId:
        base_item_in_wardrobe = any(item.id == request.baseItemId for item in wardrobe_items)
        print(f"🔍 DEBUG: Base item {request.baseItemId} found in wardrobe: {base_item_in_wardrobe}")
        if base_item_in_wardrobe:
            base_item = next(item for item in wardrobe_items if item.id == request.baseItemId)
            print(f"🔍 DEBUG: Base item details: {base_item.name} ({base_item.type})")
    
    # NEW: More detailed debugging
    print(f"🔍 DEBUG: Wardrobe data details:")
    if wardrobe_items:
        print(f"  - First item: {wardrobe_items[0].name} ({wardrobe_items[0].type})")
        print(f"  - First item dominantColors: {len(wardrobe_items[0].dominantColors)}")
        print(f"  - First item matchingColors: {len(wardrobe_items[0].matchingColors)}")
        print(f"  - First item style: {wardrobe_items[0].style}")
        print(f"  - First item occasion: {wardrobe_items[0].occasion}")
    else:
        print(f"  - No wardrobe items received!")
    
    try:
        print(f"🔍 DEBUG: Calling outfit_generation_service.generate_outfit")
        result = await outfit_generation_service.generate_outfit(
            user_id=user_profile.id,
            wardrobe=wardrobe_items,
            occasion=request.occasion,
            weather=weather_data,
            user_profile=user_profile,
            style=request.style,
            mood=request.mood,
            base_item_id=request.baseItemId
        )
        print(f"✅ DEBUG: outfit_service.generate_outfit completed successfully")
        print(f"🔍 DEBUG: Generated outfit id: {result.id}")
        return result
    except Exception as e:
        print(f"❌ DEBUG: Error in generate_outfit: {str(e)}")
        print(f"🔍 DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"🔍 DEBUG: Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

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

@router.put("/{outfit_id}/update", response_model=OutfitGeneratedOutfit)
async def update_outfit(
    outfit_id: str,
    request: UpdateOutfitRequest,
    current_user: UserProfile = Depends(get_current_user_optional)
):
    """
    Update an existing outfit with new details and items.
    """
    try:
        print(f"🔍 DEBUG: Backend update_outfit called")
        print(f"🔍 DEBUG: Request data:")
        print(f"  - outfit_id: {outfit_id}")
        print(f"  - name: {request.name}")
        print(f"  - occasion: {request.occasion}")
        print(f"  - style: {request.style}")
        print(f"  - items count: {len(request.items)}")
        
        # Handle case where current_user might be None
        if current_user is None:
            print(f"❌ DEBUG: Authentication failed - current_user is None")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        print(f"  - user_profile.id: {current_user.id}")
        
        # Update outfit data
        outfit_data = {
            "name": request.name,
            "occasion": request.occasion,
            "style": request.style,
            "description": request.description or "",
            "items": request.items,
            "updatedAt": int(time.time()),
            "is_edited": True  # Mark as edited
        }
        
        # Save to database
        result = await outfit_service.update_outfit(outfit_id, outfit_data, current_user.id)
        
        print(f"✅ DEBUG: update_outfit completed successfully")
        print(f"🔍 DEBUG: Updated outfit id: {result.id}")
        return result
        
    except Exception as e:
        print(f"❌ DEBUG: Error in update_outfit: {str(e)}")
        print(f"🔍 DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"🔍 DEBUG: Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{outfit_id}/feedback")
async def submit_outfit_feedback(
    outfit_id: str, 
    feedback: OutfitFeedbackRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Submit feedback for a generated outfit.
    
    - liked: Whether the user liked the outfit
    - rating: Rating from 1-5
    - comment: Optional comment
    - worn: Whether the user actually wore the outfit
    - occasion_used: What occasion they wore it for
    """
    try:
        # Validate rating
        if feedback.rating < 1 or feedback.rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Prepare feedback data
        feedback_data = {
            "liked": feedback.liked,
            "rating": feedback.rating,
            "comment": feedback.comment or "",
            "worn": feedback.worn,
            "occasion_used": feedback.occasion_used,
            "user_id": current_user.id,
            "timestamp": int(time.time())
        }
        
        # Update outfit with feedback
        success = await outfit_service.update_outfit_feedback(outfit_id, feedback_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save feedback")
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "outfit_id": outfit_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.get("/{outfit_id}/feedback")
async def get_outfit_feedback(
    outfit_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Get feedback for a specific outfit."""
    try:
        outfit = await outfit_service.get_outfit(outfit_id)
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        return {
            "outfit_id": outfit_id,
            "feedback": outfit.userFeedback
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

 