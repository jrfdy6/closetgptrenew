from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from ..custom_types.outfit import Outfit, OutfitGenerationRequest, OutfitGeneratedOutfit
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile
from pydantic import BaseModel
from ..services.outfit_service import OutfitService
from ..auth.auth_service import get_current_user, get_current_user_optional
import time
import uuid

router = APIRouter()
outfit_service = OutfitService()

class OutfitGenerationRequest(BaseModel):
    occasion: str
    weather: WeatherData
    wardrobe: List[ClothingItem]
    user_profile: UserProfile
    likedOutfits: List[str]
    trendingStyles: List[str]
    preferences: Optional[Dict[str, Any]] = None
    outfitHistory: Optional[List[Dict[str, Any]]] = None
    randomSeed: Optional[float] = None
    season: Optional[str] = None
    style: Optional[str] = None
    mood: Optional[str] = None  # Add mood parameter
    baseItem: Optional[ClothingItem] = None

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
    try:
        return await outfit_service.get_outfits_by_user(current_user.id)
    except Exception as e:
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
    print(f"🔍 DEBUG: Backend generate_outfit called")
    print(f"🔍 DEBUG: Request data:")
    print(f"  - occasion: {request.occasion}")
    print(f"  - mood: {request.mood}")
    print(f"  - style: {request.style}")
    print(f"  - wardrobe size: {len(request.wardrobe)}")
    print(f"  - baseItem: {request.baseItem.name if request.baseItem else 'None'}")
    print(f"  - user_profile.id: {request.user_profile.id}")
    
    # NEW: More detailed debugging
    print(f"🔍 DEBUG: Wardrobe data details:")
    if request.wardrobe:
        print(f"  - First item: {request.wardrobe[0].name} ({request.wardrobe[0].type})")
        print(f"  - First item dominantColors: {len(request.wardrobe[0].dominantColors)}")
        print(f"  - First item matchingColors: {len(request.wardrobe[0].matchingColors)}")
        print(f"  - First item style: {request.wardrobe[0].style}")
        print(f"  - First item occasion: {request.wardrobe[0].occasion}")
    else:
        print(f"  - No wardrobe items received!")
    
    try:
        print(f"🔍 DEBUG: Calling outfit_service.generate_outfit")
        result = await outfit_service.generate_outfit(
            occasion=request.occasion,
            weather=request.weather,
            wardrobe=request.wardrobe,
            user_profile=request.user_profile,
            likedOutfits=request.likedOutfits,
            trendingStyles=request.trendingStyles,
            preferences=request.preferences,
            outfitHistory=request.outfitHistory,
            randomSeed=request.randomSeed,
            season=request.season,
            style=request.style,
            mood=request.mood,  # Add mood parameter
            baseItem=request.baseItem
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

@router.post("/create", response_model=OutfitGeneratedOutfit)
async def create_outfit(
    request: CreateOutfitRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Create a custom outfit by manually selecting items from the user's wardrobe.
    """
    try:
        print(f"🔍 DEBUG: Backend create_outfit called")
        print(f"🔍 DEBUG: Request data:")
        print(f"  - name: {request.name}")
        print(f"  - occasion: {request.occasion}")
        print(f"  - style: {request.style}")
        print(f"  - items count: {len(request.items)}")
        print(f"  - user_profile.id: {current_user.id}")
        
        # Create outfit data
        outfit_data = {
            "id": str(uuid.uuid4()),
            "name": request.name,
            "occasion": request.occasion,
            "style": request.style,
            "description": request.description or "",
            "items": request.items,
            "user_id": current_user.id,
            "createdAt": request.createdAt or int(time.time()),
            "is_custom": True,  # Mark as custom outfit
            "confidence_score": 1.0,  # Custom outfits have full confidence
            "reasoning": f"Custom outfit created by user: {request.description or 'No description provided'}"
        }
        
        # Save to database
        result = await outfit_service.create_custom_outfit(outfit_data)
        
        print(f"✅ DEBUG: create_outfit completed successfully")
        print(f"🔍 DEBUG: Created outfit id: {result.id}")
        return result
        
    except Exception as e:
        print(f"❌ DEBUG: Error in create_outfit: {str(e)}")
        print(f"🔍 DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"🔍 DEBUG: Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

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

 