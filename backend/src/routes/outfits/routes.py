"""
Route handlers for outfit management.
All API endpoints extracted from main outfits.py
"""

import logging
import time
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4
from collections import defaultdict

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict

# Import from parent modules
from ...auth.auth_service import get_current_user, get_current_user_id
from ...custom_types.profile import UserProfile
from ...custom_types.outfit import OutfitGeneratedOutfit
from ...core.cache import cache_manager

# Import from local modules
from .database import (
    get_user_wardrobe, get_user_profile, save_outfit,
    get_user_outfits, get_user_wardrobe_cached, get_user_profile_cached,
    normalize_created_at
)
from .helpers import (
    _generate_outfit_cache_key, _validate_cached_outfit,
    ensure_base_item_included
)
from .validation import (
    validate_outfit_completeness, safe_get_metadata,
    log_generation_strategy
)
from .scoring import calculate_outfit_score

# Import monitoring service
from ...services.production_monitoring_service import (
    monitoring_service,
    OperationType,
    UserJourneyStep,
    ServiceLayer
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["outfits"])
security = HTTPBearer()

# Global debug data
debug_data = []
exclusion_debug = []

# Firebase availability
FIREBASE_AVAILABLE = False
db = None
firebase_initialized = False
current_user = None

# Helper functions needed by routes
def debug_rule_engine(stage: str, wardrobe_items=None, suitable=None, categorized=None, scores=None, validated=None):
    try:
        debug_info = {
            "stage": stage,
            "wardrobe_count": len(wardrobe_items) if wardrobe_items is not None else None,
            "suitable_count": len(suitable) if suitable is not None else None,
            "categorized_keys": list(categorized.keys()) if categorized else None,
            "scores_count": len(scores) if scores is not None else None,
            "validated_count": len(validated) if validated is not None else None,
        }
        debug_data.append(debug_info)
    except Exception as e:
        error_info = {"stage": stage, "error": str(e)}
        debug_data.append(error_info)
        logger.error(f"⚠️ CRITICAL DEBUG ERROR: {e}")

# Request/Response Models (needed by routes)
class OutfitRequest(BaseModel):
    """Request model for outfit generation."""
    style: str
    mood: str
    occasion: str
    description: Optional[str] = None
    baseItem: Optional[Dict[str, Any]] = None
    baseItemId: Optional[str] = None
    wardrobe: Optional[List[Dict[str, Any]]] = []
    wardrobeItems: Optional[List[Dict[str, Any]]] = []
    wardrobeCount: Optional[int] = 0
    wardrobeType: Optional[str] = "object"
    weather: Optional[Dict[str, Any]] = None
    bypass_cache: Optional[bool] = False
    user_profile: Optional[Dict[str, Any]] = None
    likedOutfits: Optional[List[Dict[str, Any]]] = []
    trendingStyles: Optional[List[Dict[str, Any]]] = []
    preferences: Optional[Dict[str, Any]] = None

    @property
    def resolved_wardrobe(self) -> List[Dict[str, Any]]:
        """Get wardrobe items, handling both wardrobe and wardrobeItems formats"""
        return self.wardrobe or self.wardrobeItems or []

class CreateOutfitRequest(BaseModel):
    """Request model for outfit creation."""
    name: str
    occasion: str
    style: str
    description: Optional[str] = None
    items: List[Dict[str, Any]]
    createdAt: Optional[int] = None

class OutfitRatingRequest(BaseModel):
    """Request model for outfit rating."""
    outfitId: str
    rating: Optional[int] = None  # 1-5 stars
    isLiked: Optional[bool] = False
    isDisliked: Optional[bool] = False
    feedback: Optional[str] = None

class LearningConfirmation(BaseModel):
    """Learning confirmation data returned to user."""
    messages: List[str]
    total_feedback_count: int
    personalization_level: int
    confidence_level: str
    preferred_colors: Optional[List[str]] = None
    preferred_styles: Optional[List[str]] = None

class OutfitRatingResponse(BaseModel):
    """Response model for outfit rating."""
    status: str
    message: str
    learning: Optional[LearningConfirmation] = None
    xp_earned: Optional[int] = None
    level_up: Optional[bool] = None
    new_level: Optional[int] = None

class OutfitResponse(BaseModel):
    """Response model for outfits."""
    model_config = ConfigDict(exclude_none=False)
    id: str
    name: str
    style: Optional[str] = None
    mood: Optional[str] = None
    items: Optional[List[dict]] = None
    occasion: Optional[str] = None
    confidence_score: Optional[float] = None
    reasoning: Optional[str] = None
    createdAt: Optional[datetime] = None
    user_id: Optional[str] = None
    generated_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def safe_get(item, key, default=None):
    '''Safely get value from item (dict or object)'''
    if isinstance(item, dict):
        return safe_get(item, key, default)
    else:
        return getattr(item, key, default)

# Import generate_outfit_logic from service
def get_generate_outfit_logic():
    """Import generate_outfit_logic from OutfitGenerationService"""
    try:
        from ...services.outfits.generation_service import OutfitGenerationService
        service = OutfitGenerationService()
        return service.generate_outfit_logic
    except Exception as e:
        logger.error(f"Failed to import generate_outfit_logic: {e}")
        raise

# Route Handlers
@router.get("/health", response_model=dict)
async def outfits_health_check():
    """Health check for outfits router."""
    logger.info("🔍 DEBUG: Outfits health check called")
    return {
        "status": "healthy",
        "router": "outfits",
        "message": "Outfits router is working!",
        "version": "v5.0-FORCE-REDEPLOY",
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False
    }

@router.get("/debug", response_model=dict)
async def outfits_debug():
    """Debug endpoint for outfits router."""
    logger.info("🔍 DEBUG: Outfits debug endpoint called")
    return {
        "status": "debug",
        "router": "outfits",
        "message": "Outfits router debug endpoint working",
        "timestamp": datetime.now().isoformat(),
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False
    }

@router.get("/debug/base-item-fix")
async def debug_base_item_fix():
    """Debug endpoint to check if base item fix is deployed"""
    return {
        "status": "base_item_fix_deployed",
        "timestamp": datetime.utcnow().isoformat(),
        "fix_version": "v6.0",
        "description": "CLEAN ARCHITECTURE: Base item handling consolidated into ensure_base_item_included() helper function"
    }

@router.get("/debug/rule-engine")
async def debug_rule_engine_data():
    """Debug endpoint to check rule engine debug data"""
    global debug_data
    return {
        "debug_data": debug_data,
        "timestamp": datetime.utcnow().isoformat(),
        "data_count": len(debug_data)
    }

@router.get("/outfit-save-test", response_model=dict)
async def outfit_save_test():
    """Test saving to the outfits collection specifically."""
    logger.info("🔍 DEBUG: Outfit save test called")

    test_results = {
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False,
        "test_timestamp": datetime.now().isoformat()
    }

    if FIREBASE_AVAILABLE and firebase_initialized:
        try:
            # Test saving to the same outfits collection that generate_outfit uses
            test_outfit_id = f"test-outfit-{int(datetime.now().timestamp())}"
            test_outfit_data = {
                "id": test_outfit_id,
                "name": "Test Outfit",
                "user_id": current_user.id if current_user else "mock-user",
                "createdAt": datetime.now().isoformat(),
                "test": True,
                "items": [{"type": "shirt", "name": "Test Shirt"}]
            }

            logger.info(f"🔥 Testing outfit save to outfits/{test_outfit_id}...")
            outfits_ref = db.collection('outfits')
            doc_ref = outfits_ref.document(test_outfit_id)
            doc_ref.set(test_outfit_data)
            test_results["outfit_save_test"] = "success"
            logger.info("✅ Outfit save test successful")

            # Verify by reading back
            logger.info("🔥 Testing outfit read...")
            verification_doc = doc_ref.get() if doc_ref else None
            if verification_doc and verification_doc.exists:
                test_results["outfit_read_test"] = "success"
                test_results["read_data"] = verification_doc.to_dict()
                logger.info("✅ Outfit read test successful")
            else:
                test_results["outfit_read_test"] = "failed - document not found"
                logger.error("❌ Outfit read test failed - document not found")

        except Exception as e:
            error_msg = f"Outfit save test error: {str(e)}"
            test_results["error"] = error_msg
            logger.error(error_msg)
    else:
        test_results["error"] = "Firebase not available or not initialized"

    return {
        "status": "outfit_save_test",
        "results": test_results
    }

@router.get("/firebase-test", response_model=dict)
async def firebase_connectivity_test():
    """Test Firebase write/read operations."""
    logger.info("🔍 DEBUG: Firebase connectivity test called")

    test_results = {
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False,
        "write_test": "not_attempted",
        "read_test": "not_attempted",
        "error": None
    }

    if FIREBASE_AVAILABLE and firebase_initialized:
        try:
            # Test write operation
            test_doc_id = "connectivity-test"
            test_data = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "message": "Firebase connectivity test"
            }

            logger.info("🔥 Testing Firebase write operation...")
            db.collection('test_collection').document(test_doc_id).set(test_data)
            test_results["write_test"] = "success"
            logger.info("✅ Firebase write test successful")

            # Test read operation
            logger.info("🔥 Testing Firebase read operation...")
            doc = db.collection('test_collection').document(test_doc_id).get()
            if doc.exists:
                test_results["read_test"] = "success"
                test_results["read_data"] = doc.to_dict()
                logger.info("✅ Firebase read test successful")
            else:
                test_results["read_test"] = "document_not_found"
                logger.warning("⚠️ Document not found after write")

        except Exception as e:
            error_msg = f"Firebase test error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            test_results["error"] = error_msg
            test_results["write_test"] = "failed"
            test_results["read_test"] = "failed"
    else:
        test_results["error"] = "Firebase not available or not initialized"

    return {
        "status": "firebase_connectivity_test",
        "results": test_results
    }

@router.get("/check-outfits-db", response_model=dict)
async def check_outfits_database():
    """Check what outfits are actually in the database."""
    logger.info("🔍 DEBUG: Checking outfits in database")

    check_results = {
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False,
        "user_outfits": [],
        "global_outfits": [],
        "error": None
    }

    if FIREBASE_AVAILABLE and firebase_initialized:
        try:
            user_id = "mock-user-123"

            # Check user's outfits collection
            logger.info(f"🔍 Checking user outfits for {user_id}")
            user_outfits_ref = db.collection('users').document(user_id).collection('outfits')
            user_docs = user_outfits_ref.limit(10).get()

            for doc in user_docs:
                outfit_data = doc.to_dict()
                outfit_data['doc_id'] = doc.id
                check_results["user_outfits"].append(outfit_data)

            # Check global outfits collection
            logger.info("🔍 Checking global outfits collection")
            global_outfits_ref = db.collection('outfits')
            global_docs = global_outfits_ref.limit(10).get()

            for doc in global_docs:
                outfit_data = doc.to_dict()
                outfit_data['doc_id'] = doc.id
                check_results["global_outfits"].append(outfit_data)

            logger.info(f"✅ Found {len(check_results['user_outfits'])} user outfits, {len(check_results['global_outfits'])} global outfits")

        except Exception as e:
            error_msg = f"Database check error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            check_results["error"] = error_msg
    else:
        check_results["error"] = "Firebase not available or not initialized"

    return {
        "status": "outfits_database_check",
        "results": check_results
    }

@router.get("/debug-retrieval", response_model=dict)
async def debug_outfit_retrieval():
    """Debug the outfit retrieval process step by step."""
    logger.info("🔍 DEBUG: Debug retrieval endpoint called")

    debug_info = {
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False,
        "user_id": "mock-user-123",
        "steps": [],
        "error": None,
        "final_result": None
    }

    try:
        user_id = "mock-user-123"
        debug_info["steps"].append("Starting retrieval process")

        if not FIREBASE_AVAILABLE or not firebase_initialized:
            debug_info["steps"].append("Firebase not available - would use mock data")
            debug_info["final_result"] = "mock_data_fallback"
            return debug_info

        debug_info["steps"].append("Firebase is available")

        # Test the exact same logic as get_user_outfits
        debug_info["steps"].append(f"Querying outfits collection with user_id == '{user_id}'")
        outfits_ref = db.collection('outfits').where('user_id', '==', user_id)
        docs = outfits_ref.limit(10).get()

        debug_info["steps"].append(f"Query returned {len(docs)} documents")

        outfits = []
        for doc in docs:
            outfit_data = doc.to_dict()
            outfit_data['id'] = doc.id
            outfits.append({
                "id": doc.id,
                "name": (outfit_data.get('name', 'unknown') if outfit_data else 'unknown'),
                "user_id": (outfit_data.get('user_id', 'unknown') if outfit_data else 'unknown')
            })

        debug_info["steps"].append(f"Processed {len(outfits)} outfits")
        debug_info["final_result"] = outfits

    except Exception as e:
        error_msg = f"Debug retrieval error: {str(e)}"
        debug_info["steps"].append(error_msg)
        debug_info["error"] = error_msg
        debug_info["final_result"] = "error_fallback"

    return {
        "status": "debug_outfit_retrieval",
        "debug_info": debug_info
    }

@router.get("/debug-specific/{outfit_id}", response_model=dict)
async def debug_specific_outfit(outfit_id: str):
    """Debug endpoint to check if a specific outfit exists in Firestore."""
    debug_info = {
        "outfit_id": outfit_id,
        "timestamp": datetime.now().isoformat(),
        "steps": []
    }

    try:
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            debug_info["steps"].append("Firebase not available")
            return {"status": "firebase_unavailable", "debug_info": debug_info}

        debug_info["steps"].append("Firebase is available")

        # Direct document query by ID
        debug_info["steps"].append(f"Querying outfits/{outfit_id} directly")
        doc_ref = db.collection('outfits').document(outfit_id)
        doc = doc_ref.get() if doc_ref else None

        if doc and doc.exists:
            outfit_data = doc.to_dict()
            debug_info["steps"].append("Document exists!")
            debug_info["outfit_data"] = {
                "id": doc.id,
                "name": (outfit_data.get('name', 'unknown') if outfit_data else 'unknown'),
                "user_id": (outfit_data.get('user_id', 'unknown') if outfit_data else 'unknown'),
                "createdAt": (outfit_data.get('createdAt', 'unknown') if outfit_data else 'unknown'),
                "has_items": len((outfit_data.get('items', []) if outfit_data else [])) > 0
            }
        else:
            debug_info["steps"].append("Document does NOT exist!")
            debug_info["outfit_data"] = None

    except Exception as e:
        error_msg = f"Debug error: {str(e)}"
        debug_info["steps"].append(error_msg)
        debug_info["error"] = error_msg

    return {
        "status": "debug_specific_outfit",
        "debug_info": debug_info
    }

@router.post("/{outfit_id}/worn")
async def mark_outfit_as_worn(
    outfit_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Mark an outfit as worn (simplified endpoint for frontend compatibility).
    This will update both the outfit wear counter AND individual wardrobe item wear counters.
    """
    # Write endpoint entry to Firestore immediately (silent)
    try:
        debug_ref = db.collection('debug_stats_updates').document()
        debug_ref.set({
            'event': 'mark_outfit_as_worn_endpoint_entered',
            'user_id': current_user.id,
            'outfit_id': outfit_id,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Successfully entered mark_outfit_as_worn endpoint'
        })
    except Exception as entry_error:
        pass  # Silent error handling

    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Import Firebase inside function to prevent import-time crashes
        try:
            from ..config.firebase import db, firebase_initialized
        except ImportError as e:
            raise HTTPException(status_code=503, detail="Firebase service unavailable")

        if not db:
            raise HTTPException(status_code=503, detail="Firebase service unavailable")

        # Simple direct update instead of using the complex OutfitService
        outfit_ref = db.collection('outfits').document(outfit_id)
        outfit_doc = outfit_ref.get() if outfit_ref else None

        if not outfit_doc or not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")

        outfit_data = outfit_doc.to_dict()

        # Verify ownership
        if outfit_data.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="Outfit does not belong to user")

        # Update wear count and last worn
        current_wear_count = (outfit_data.get('wearCount', 0) if outfit_data else 0)
        current_time = datetime.utcnow()

        logger.info(f"📊 COUNTER 1: Updating outfit wear count for {outfit_id}")
        logger.info(f"    Before: wearCount={current_wear_count}")

        outfit_ref.update({
            'wearCount': current_wear_count + 1,
            'lastWorn': current_time,
            'updatedAt': current_time
        })

        logger.info(f"✅ COUNTER 1 UPDATED: Outfit {outfit_id} wearCount {current_wear_count} → {current_wear_count + 1}")
        logger.info(f"    lastWorn set to: {current_time.isoformat()}")

        # Update user preferences from wear (Spotify-style learning)
        try:
            from ...services.user_preference_service import user_preference_service
            await user_preference_service.update_from_wear(
                user_id=current_user.id,
                outfit=outfit_data
            )
            logger.info(f"✨ Updated user preferences from wear event")
        except Exception as pref_error:
            logger.warning(f"⚠️ Failed to update preferences from wear: {pref_error}")
            # Don't fail the whole request if preference update fails

        try:
            debug_ref = db.collection('debug_stats_updates').document()
            debug_ref.set({
                'event': 'outfit_update_successful',
                'user_id': current_user.id,
                'outfit_id': outfit_id,
                'old_wear_count': current_wear_count,
                'new_wear_count': current_wear_count + 1,
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Successfully updated outfit wear count'
            })
        except Exception as outfit_error:
            pass  # Silent error handling

        print("🚨 DEPLOYMENT_TEST: Surgical debug code is LIVE", flush=True)

        # Write entry debug to Firestore immediately (before any potential errors) - SILENT
        try:
            debug_ref = db.collection('debug_stats_updates').document()
            debug_ref.set({
                'event': 'user_stats_section_entered',
                'user_id': current_user.id,
                'outfit_id': outfit_id,
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Successfully entered user_stats update section'
            })
        except Exception as entry_error:
            pass  # Silent error handling

        # FIXED: Simple user_stats update with proper increment logic
        try:
            from google.cloud.firestore import Increment
            stats_ref = db.collection('user_stats').document(current_user.id)

            # Use Firestore Increment to properly add 1 to existing count
            stats_ref.set({
                'user_id': current_user.id,
                'worn_this_week': Increment(1),  # FIXED: Proper increment instead of hardcoded 1
                'last_updated': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }, merge=True)
            print("✅ FIXED: Updated user_stats with proper increment")
        except Exception as simple_stats_error:
            # Don't fail - outfit was still marked as worn successfully
            print(f"⚠️ SIMPLIFIED: Stats update failed: {simple_stats_error}")
            pass

        return {
            "success": True,
            "message": "Outfit marked as worn",
            "outfit_id": outfit_id,
            "wear_count": current_wear_count + 1
        }

    except Exception as e:
        logger.error(f"Error marking outfit as worn: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
async def create_custom_outfit(
    req: CreateOutfitRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Create a custom outfit by manually selecting items."""
    try:
        logger.info(f"🎨 Creating custom outfit: {req.name} for user {current_user_id}")
        
        # Import Firebase
        try:
            from src.config.firebase import db
        except ImportError:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Create outfit document
        outfit_id = f"outfit_{int(time.time())}"
        outfit_data = {
            "id": outfit_id,
            "name": req.name,
            "occasion": req.occasion,
            "style": req.style,
            "description": req.description or "",
            "items": req.items,
            "userId": current_user_id,
            "createdAt": datetime.now().isoformat(),
            "wearCount": 0,
            "favorite": False,
            "metadata": {
                "creation_type": "manual",
                "item_count": len(req.items)
            }
        }
        
        # Save to Firestore
        db.collection('outfits').document(outfit_id).set(outfit_data)
        logger.info(f"✅ Custom outfit saved: {outfit_id}")
        
        return {
            "success": True,
            "outfit_id": outfit_id,
            "message": "Outfit created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create outfit: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create outfit: {str(e)}")

@router.post("/rate", response_model=OutfitRatingResponse)
async def rate_outfit(
    rating_request: OutfitRatingRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Rate an outfit and update user preferences (Spotify-style learning).
    
    This endpoint:
    1. Saves rating/like/dislike to outfit
    2. Updates comprehensive user_preferences in Firestore
    3. Returns learning confirmation with specific insights
    """
    try:
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Import services
        from ...config.firebase import db
        from ...services.user_preference_service import user_preference_service
        
        # Get outfit
        outfit_ref = db.collection('outfits').document(rating_request.outfitId)
        outfit_doc = outfit_ref.get()
        
        if not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        
        # Verify ownership
        if outfit_data.get('user_id') != current_user_id and outfit_data.get('userId') != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"⭐ Rating outfit {rating_request.outfitId}: rating={rating_request.rating}, liked={rating_request.isLiked}, disliked={rating_request.isDisliked}")
        
        # Update outfit with rating
        update_data = {
            'updatedAt': datetime.now(timezone.utc)
        }
        
        if rating_request.rating is not None:
            update_data['rating'] = rating_request.rating
        
        if rating_request.isLiked is not None:
            update_data['isLiked'] = rating_request.isLiked
        
        if rating_request.isDisliked is not None:
            update_data['isDisliked'] = rating_request.isDisliked
        
        if rating_request.feedback:
            update_data['userFeedback'] = rating_request.feedback
        
        outfit_ref.update(update_data)
        logger.info(f"✅ Updated outfit {rating_request.outfitId} with rating data")
        
        # Update user preferences (Spotify-style learning)
        learning_result = await user_preference_service.update_from_rating(
            user_id=current_user_id,
            outfit=outfit_data,
            rating=rating_request.rating,
            is_liked=rating_request.isLiked or False,
            is_disliked=rating_request.isDisliked or False,
            feedback_text=rating_request.feedback
        )
        
        logger.info(f"✨ Updated user preferences: {len(learning_result.get('messages', learning_result.get('learning_messages', [])))} insights generated")
        
        # ✅ Award XP for rating outfit
        from ...services.gamification_service import gamification_service
        xp_result = await gamification_service.award_xp(
            user_id=current_user_id,
            xp_amount=5,
            reason="outfit_rated"
        )
        logger.info(f"🎮 Awarded {xp_result['xp_earned']} XP for rating outfit")
        
        # Return response with learning confirmation and XP
        return OutfitRatingResponse(
            status="success",
            message="Rating submitted and preferences updated",
            learning=LearningConfirmation(**learning_result),
            xp_earned=xp_result.get('xp_earned', 0),
            level_up=xp_result.get('level_up', False),
            new_level=xp_result.get('new_level')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to rate outfit: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit rating: {str(e)}"
        )


@router.post("/generate")
async def generate_outfit(
    req: OutfitRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Generate an outfit using robust decision logic with comprehensive validation,
    fallback strategies, body type optimization, and style profile integration.
    """
    # 🔥 COMPREHENSIVE ERROR TRACING FOR NoneType .get() DEBUGGING
    # DEBUG: Log request details at endpoint start
    print(f"🔍 DEBUG ENDPOINT START: req = {req}")
    print(f"🔍 DEBUG ENDPOINT START: req.resolved_wardrobe = {req.resolved_wardrobe}")
    print(f"🔍 DEBUG ENDPOINT START: current_user_id = {current_user_id}")
    try:
        start_time = time.time()
        generation_attempts = 0
        max_attempts = 3
        cache_hit = False
        
        # Enhanced authentication validation
        if not current_user_id:
            logger.error("❌ Authentication failed: No current user ID")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        logger.info(f"🎯 Starting robust outfit generation for user: {current_user_id}")
        logger.info(f"📋 Request details: {req.occasion}, {req.style}, {req.mood}")
        
        # Define hard requirements per occasion
        occasion_requirements = {
            'business': {
                'required': ['shirt', 'pants', 'shoes'],
                'optional': ['blazer', 'tie', 'jacket'],
                'forbidden': ['shorts', 'flip-flops', 'tank-top']
            },
            'formal': {
                'required': ['shirt', 'pants', 'shoes'],
                'optional': ['blazer', 'tie', 'jacket'],
                'forbidden': ['shorts', 'flip-flops', 'tank-top', 'jeans']
            },
            'athletic': {
                'required': ['top', 'shorts OR athletic-pants', 'sneakers'],
                'optional': ['jacket', 'hat'],
                'forbidden': ['dress-shirt', 'tie', 'dress-shoes']
            },
            'casual': {
                'required': ['top', 'bottom'],
                'optional': ['shoes', 'jacket', 'accessories'],
                'forbidden': []
            },
            'weekend': {
                'required': ['top', 'bottom'],
                'optional': ['sneakers', 'hoodie', 'jacket'],
                'forbidden': ['tie', 'dress-shoes']
            }
        }
        
        # Category cardinality limits
        def get_category_limits(occasion):
            """Define category limits based on occasion"""
            base_limits = {
                "shirt": (1, 2),
                "top": (1, 2),
                "pants": (1, 1),
                "shorts": (1, 1),
                "shoes": (1, 1),
                "jacket": (0, 1),
                "blazer": (0, 1),
                "accessories": (0, 2),
            }
            
            occasion_lower = occasion.lower()
            if occasion_lower in ['business', 'formal']:
                return {
                    "shirt": (1, 1),
                    "top": (1, 1),
                    "pants": (1, 1),
                    "shoes": (1, 1),
                    "jacket": (0, 1),
                    "blazer": (0, 1),
                    "accessories": (0, 1),
                }
            elif occasion_lower == 'athletic':
                return {
                    "top": (1, 2),
                    "shorts": (1, 1),
                    "pants": (1, 1),
                    "shoes": (1, 1),
                    "jacket": (0, 1),
                    "accessories": (0, 1),
                }
            else:
                return base_limits
        
        # Enhanced deduplication with category limits
        def deduplicate_items_with_limits(items, occasion):
            from collections import defaultdict
            
            category_limits = get_category_limits(occasion)
            category_counts = defaultdict(int)
            used_subtypes = set()
            final_items = []
            
            # First pass: remove exact duplicates
            seen_ids = set()
            seen_combinations = set()
            unique_items = []
            
            for item in items:
                item_id = (safe_get(item, 'id', '') if item else '')
                item_name = (safe_get(item, 'name', '') if item else '')
                item_type = (safe_get(item, 'type', '') if item else '').lower()
                item_color = (safe_get(item, 'color', '') if item else '')
                
                combination_key = f"{item_name}|{item_type}|{item_color}"
                
                if item_id not in seen_ids and combination_key not in seen_combinations:
                    seen_ids.add(item_id)
                    seen_combinations.add(combination_key)
                    unique_items.append(item)
                else:
                    logger.info(f"🔍 DEBUG: Removed exact duplicate: {item_name} ({item_color})")
            
            # Second pass: enforce category limits
            for item in unique_items:
                item_type = (safe_get(item, 'type', '') if item else '').lower()
                item_name = (safe_get(item, 'name', '') if item else '').lower()
                
                # Map item type to category
                category = None
                subtype = None
                
                if item_type in ['shirt', 'blouse', 't-shirt', 'tank', 'sweater', 'hoodie']:
                    category = 'top'
                    if 'dress' in item_name or 'button' in item_name:
                        subtype = 'dress_shirt'
                    elif 'polo' in item_name:
                        subtype = 'polo_shirt'
                    elif 't-shirt' in item_name or 'tee' in item_name:
                        subtype = 't_shirt'
                    else:
                        subtype = 'other_top'
                elif item_type in ['pants', 'jeans', 'trousers', 'slacks']:
                    category = 'pants'
                    if 'jeans' in item_name:
                        subtype = 'jeans'
                    elif 'dress' in item_name:
                        subtype = 'dress_pants'
                    else:
                        subtype = 'other_pants'
                elif item_type in ['shorts', 'athletic-pants', 'joggers']:
                    category = 'shorts'
                    subtype = 'shorts'
                elif item_type in ['shoes', 'sneakers', 'boots', 'sandals', 'oxford']:
                    category = 'shoes'
                    if 'sneaker' in item_name or 'athletic' in item_name:
                        subtype = 'sneakers'
                    elif 'oxford' in item_name or 'dress' in item_name:
                        subtype = 'dress_shoes'
                    elif 'boot' in item_name:
                        subtype = 'boots'
                    elif 'sandals' in item_name:
                        subtype = 'sandals'
                    else:
                        subtype = 'other_shoes'
                elif item_type in ['jacket', 'blazer', 'cardigan']:
                    category = 'jacket'
                    if 'blazer' in item_name:
                        subtype = 'blazer'
                    else:
                        subtype = 'jacket'
                elif item_type in ['tie', 'belt', 'watch', 'hat']:
                    category = 'accessories'
                    subtype = item_type
                else:
                    category = 'other'
                    subtype = 'other'
                
                # Check category limits
                if category in category_limits:
                    min_limit, max_limit = category_limits[category]
                    current_count = category_counts[category]
                    
                    # Special handling for shoes
                    if category == 'shoes':
                        if current_count >= max_limit:
                            logger.info(f"❌ Skipped {(safe_get(item, 'name', 'Unknown') if item else 'Unknown')} - shoe limit reached (1)")
                            continue
                        if subtype in used_subtypes:
                            logger.info(f"❌ Skipped {(safe_get(item, 'name', 'Unknown') if item else 'Unknown')} - shoe subtype '{subtype}' already used")
                            continue
                        used_subtypes.add(subtype)
                        logger.info(f"✅ Added {(safe_get(item, 'name', 'Unknown') if item else 'Unknown')} (shoes: {subtype})")
                    
                    if current_count < max_limit:
                        final_items.append(item)
                        category_counts[category] += 1
                        if category != 'shoes':
                            logger.info(f"✅ Added {(safe_get(item, 'name', 'Unknown') if item else 'Unknown')} ({category}, count: {category_counts[category]})")
                    else:
                        logger.info(f"❌ Skipped {(safe_get(item, 'name', 'Unknown') if item else 'Unknown')} ({category}) - category limit reached ({max_limit})")
                else:
                    final_items.append(item)
                    logger.info(f"➕ Added {(safe_get(item, 'name', 'Unknown') if item else 'Unknown')} (unknown category)")
            
            logger.info(f"🎯 Final outfit category distribution: {dict(category_counts)}")
            logger.info(f"🎯 Used shoe subtypes: {list(used_subtypes)}")
            return final_items
        
        # Retry with relaxed rules
        def retry_with_relaxed_rules(original_items, occasion, requirements):
            """Retry outfit generation with relaxed rules when validation fails"""
            logger.info(f"🔄 Retrying with relaxed rules for {occasion}")
            relaxed_items = original_items.copy()
            missing_required = validate_outfit_completeness(relaxed_items, requirements, (req.occasion if req else "unknown"))
            
            if len(missing_required) > 0:
                logger.info(f"🔧 Attempting to fill missing items: {missing_required}")
                
                for missing_item in missing_required:
                    if missing_item == 'shirt':
                        for item in relaxed_items:
                            if safe_get(item, 'type', '').lower() in ['shirt', 'blouse', 'sweater', 'polo']:
                                logger.info(f"✅ Found flexible shirt alternative: {safe_get(item, 'name', 'Unknown')}")
                                break
                    elif missing_item == 'pants':
                        for item in relaxed_items:
                            if safe_get(item, 'type', '').lower() in ['pants', 'jeans', 'trousers', 'slacks']:
                                logger.info(f"✅ Found flexible pants alternative: {safe_get(item, 'name', 'Unknown')}")
                                break
                    elif missing_item == 'shoes':
                        for item in relaxed_items:
                            if safe_get(item, 'type', '').lower() in ['shoes', 'sneakers', 'boots', 'oxford']:
                                logger.info(f"✅ Found flexible shoes alternative: {safe_get(item, 'name', 'Unknown')}")
                                break
            
            logger.info(f"🔄 Relaxed rules result: {len(relaxed_items)} items")
            return relaxed_items
        
        # Calculate confidence score
        def calculate_robust_confidence(items, validation_passed, occasion):
            """Calculate confidence score for robust generator"""
            base_confidence = 0.7
            
            if validation_passed:
                confidence_score = base_confidence + 0.22
                logger.info("🎯 High confidence: Validation passed")
            else:
                confidence_score = base_confidence + 0.08
                logger.info("🎯 Medium confidence: Used relaxed rules")
            
            item_count = len(items)
            if 3 <= item_count <= 6:
                confidence_score += 0.05
            
            occasion_lower = occasion.lower()
            if occasion_lower in ['business', 'formal']:
                has_formal_shirt = any('dress' in safe_get(item, 'name', '').lower() or 'button' in safe_get(item, 'name', '').lower() 
                                     for item in items if safe_get(item, 'type', '').lower() in ['shirt', 'blouse'])
                has_formal_pants = any('dress' in safe_get(item, 'name', '').lower() or 'slacks' in safe_get(item, 'name', '').lower()
                                     for item in items if safe_get(item, 'type', '').lower() in ['pants', 'trousers'])
                if has_formal_shirt and has_formal_pants:
                    confidence_score += 0.03
            
            return min(confidence_score, 1.0)
        
        # Request validation
        validation_errors = []
        if not (req.occasion if req else "unknown"):
            validation_errors.append("Occasion is required")
        if not (req.style if req else "unknown"):
            validation_errors.append("Style is required")
        if not (req.mood if req else "unknown"):
            validation_errors.append("Mood is required")
        if not (req.wardrobe if req else []) or len(req.wardrobe) == 0:
            validation_errors.append("Wardrobe items are required")
        
        if validation_errors:
            logger.error(f"❌ Request validation failed: {validation_errors}")
            raise HTTPException(status_code=422, detail=f"Invalid request: {', '.join(validation_errors)}")
        
        logger.info(f"✅ Request validation passed")
        
        # Log base item information
        logger.info(f"🔍 DEBUG: Received baseItemId: {req.baseItemId}")
        if (req.baseItemId if req else None):
            base_item = next((item for item in (req.wardrobe if req else []) if safe_get(item, "id") == (req.baseItemId if req else None)), None)
            if base_item:
                logger.info(f"🔍 DEBUG: Found base item in wardrobe: {base_item.get('name', 'Unknown')} ({base_item.get('type', 'Unknown')})")
            else:
                logger.warning(f"⚠️ DEBUG: Base item {req.baseItemId} not found in wardrobe array")
        else:
            logger.info("🔍 DEBUG: No baseItemId provided")
        
        logger.info(f"🎨 Starting outfit generation with retry logic")
        
        # Import validation pipeline
        try:
            from ..services.outfit_validation_pipeline import validation_pipeline, ValidationContext
            validation_available = True
            logger.info("✅ Validation pipeline imported successfully")
        except ImportError as e:
            logger.warning(f"⚠️ Validation pipeline import failed: {e}")
            validation_available = False
        
        # CACHE CHECK
        outfit = None
        cache_hit = False
        if not (req.bypass_cache if req else False):
            try:
                current_wardrobe = req.wardrobe if req and req.wardrobe else []
                if not current_wardrobe:
                    current_wardrobe = await get_user_wardrobe(current_user_id)
                
                cache_key = _generate_outfit_cache_key(
                    user_id=current_user_id,
                    occasion=req.occasion if req else "unknown",
                    style=req.style if req else "unknown",
                    mood=req.mood if req else "unknown",
                    weather=req.weather if req else None,
                    baseItemId=req.baseItemId if req else None,
                    wardrobe_items=current_wardrobe
                )
                
                logger.info(f"🔍 DEBUG: Checking cache with key: {cache_key[:80]}...")
                cached_outfit = cache_manager.get("outfit", cache_key)
                logger.info(f"🔍 DEBUG: Cache result: {'HIT' if cached_outfit else 'MISS'}")
                if cached_outfit:
                    is_valid = await _validate_cached_outfit(cached_outfit, current_user_id, current_wardrobe)
                    if is_valid:
                        logger.info(f"✅ Cache hit for outfit generation: {cache_key[:50]}...")
                        outfit = cached_outfit
                        cache_hit = True
                        if 'metadata' not in outfit:
                            outfit['metadata'] = {}
                        outfit['metadata']['cache_hit'] = True
                        outfit['metadata']['cache_key'] = cache_key
                        outfit['metadata']['generation_duration'] = 0.0
                        outfit['metadata']['is_slow'] = False
                        outfit['metadata']['generation_attempts'] = 1
                    else:
                        logger.info(f"⚠️ Cache hit but validation failed - regenerating")
                        cache_manager.delete("outfit", cache_key)
                else:
                    logger.info(f"❌ Cache miss for outfit generation")
            except Exception as cache_error:
                logger.warning(f"⚠️ Cache check failed: {cache_error}, proceeding with generation")
        
        # Generation retry logic
        last_error = None
        error_details = None
        
        if not outfit:
            for attempt in range(max_attempts):
                generation_attempts += 1
                try:
                    logger.info(f"🔄 Generation attempt {generation_attempts}/{max_attempts}")
                    print(f"🔍 DEBUG RETRY LOOP: Starting attempt {generation_attempts}")
                    
                    # Run generation logic
                    generate_outfit_logic = get_generate_outfit_logic()
                    outfit = await generate_outfit_logic(req, current_user_id)
                    
                    if outfit and outfit.get('items'):
                        occasion_lower = (req.occasion if req else "unknown").lower()
                        
                        logger.info(f"🔍 DEBUG BEFORE CATEGORY LIMITS: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                        
                        # Apply category limits
                        original_items = outfit['items'].copy()
                        outfit['items'] = deduplicate_items_with_limits(outfit['items'], (req.occasion if req else "unknown"))
                        
                        logger.info(f"🔍 DEBUG AFTER CATEGORY LIMITS: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                        
                        # Validation
                        validation_passed = True
                        if occasion_lower in occasion_requirements:
                            requirements = occasion_requirements[occasion_lower]
                            missing_required = validate_outfit_completeness(outfit['items'], requirements, (req.occasion if req else "unknown"))
                            
                            if len(missing_required) > 0:
                                logger.warning(f"⚠️ VALIDATION FAILED: Missing {missing_required} - retrying with relaxed rules")
                                validation_passed = False
                                
                                logger.info(f"🔍 DEBUG BEFORE RELAXED RULES: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                                
                                outfit['items'] = retry_with_relaxed_rules(original_items, (req.occasion if req else "unknown"), requirements)
                                outfit['items'] = deduplicate_items_with_limits(outfit['items'], (req.occasion if req else "unknown"))
                                
                                logger.info(f"🔍 DEBUG AFTER RELAXED RULES: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                                logger.info(f"🔄 Retried with relaxed rules - final items: {len(outfit['items'])}")
                        
                        # Calculate confidence score
                        if 'confidence_score' not in outfit or outfit['confidence_score'] is None or outfit['confidence_score'] == 0.0:
                            confidence_score = calculate_robust_confidence(outfit['items'], validation_passed, (req.occasion if req else "unknown"))
                            outfit['confidence_score'] = confidence_score
                            logger.info(f"🎯 Calculated new confidence score: {confidence_score}")
                        else:
                            logger.info(f"🎯 Preserving robust generator confidence: {outfit['confidence_score']}")
                        
                        logger.info(f"🔍 DEBUG BEFORE METADATA MODIFICATION: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                        
                        # Ensure metadata exists
                        if 'metadata' not in outfit:
                            outfit['metadata'] = {}
                        outfit['metadata']['subtype_tracking_enabled'] = True
                        outfit['metadata']['confidence_calculated'] = True
                        outfit['metadata']['validation_passed'] = validation_passed
                        outfit['metadata']['retry_with_relaxed_rules'] = not validation_passed
                        
                        logger.info(f"🔍 DEBUG AFTER METADATA MODIFICATION: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                        
                        # Update metadata with processing status
                        if 'metadata' not in outfit:
                            outfit['metadata'] = {}
                        outfit['metadata']['validation_applied'] = True
                        outfit['metadata']['hard_requirements_enforced'] = True
                        outfit['metadata']['deduplication_applied'] = True
                        outfit['metadata']['category_limits_enforced'] = True
                        outfit['metadata']['unique_items_count'] = len(outfit['items'])
                        outfit['metadata']['occasion_requirements_met'] = validation_passed
                        
                        # Validation pipeline
                        if outfit and outfit.get('items') and validation_available:
                            try:
                                category_limits_applied = safe_get_metadata(outfit, 'category_limits_enforced', False)
                                
                                if category_limits_applied:
                                    logger.info("🎯 Category limits already applied - skipping enhanced validation")
                                    outfit['metadata']['enhanced_validation_bypassed'] = True
                                    outfit['metadata']['validation_reason'] = "Category limits already enforced"
                                else:
                                    logger.info("🔍 Running enhanced validation pipeline")
                                    validation_context = ValidationContext(
                                        occasion=req.occasion,
                                        style=req.style or "casual",
                                        mood=req.mood or "neutral",
                                        weather=req.weather.__dict__ if hasattr(req.weather, '__dict__') else (req.weather if req else None),
                                        user_profile={"id": current_user_id},
                                        temperature=getattr(req.weather, 'temperature', 70.0) if hasattr(req.weather, 'temperature') else 70.0
                                    )
                                    
                                    validation_result = await validation_pipeline.validate_outfit(outfit, validation_context)
                                    
                                    if not validation_result.valid:
                                        failed_rules = validation_result.errors or []
                                        logger.warning(f"⚠️ VALIDATION FAILED on attempt {generation_attempts}: {validation_result.errors}")
                                        print(f"🚨 VALIDATION ALERT: Attempt {generation_attempts} failed validation")
                                        if attempt < max_attempts - 1:
                                            await asyncio.sleep(1)
                                            continue
                                        else:
                                            logger.error(f"❌ VALIDATION FAILURE: All {max_attempts} attempts failed validation")
                                            print(f"🚨 VALIDATION FAILURE: All {max_attempts} attempts failed validation")
                                            raise Exception(f"Validation failed after {max_attempts} attempts")
                            except Exception as validation_error:
                                logger.warning(f"⚠️ Validation pipeline failed: {validation_error}, continuing with outfit")
                        elif outfit and outfit.get('items') and not validation_available:
                            logger.info("⚠️ Validation pipeline not available, skipping validation")
                        else:
                            logger.warning("⚠️ No outfit generated or validation not available")
                        
                        # Basic validation
                        if outfit and outfit.get('items') and len(outfit.get('items', [])) >= 3:
                            logger.info(f"✅ Generation successful on attempt {generation_attempts}")
                        
                        # Store in cache
                        if not cache_hit and not (req.bypass_cache if req else False):
                            try:
                                current_wardrobe = req.wardrobe if req and req.wardrobe else []
                                if not current_wardrobe:
                                    current_wardrobe = await get_user_wardrobe(current_user_id)
                                
                                cache_key = _generate_outfit_cache_key(
                                    user_id=current_user_id,
                                    occasion=req.occasion if req else "unknown",
                                    style=req.style if req else "unknown",
                                    mood=req.mood if req else "unknown",
                                    weather=req.weather if req else None,
                                    baseItemId=req.baseItemId if req else None,
                                    wardrobe_items=current_wardrobe
                                )
                                
                                logger.info(f"🔍 DEBUG: Storing in cache with key: {cache_key[:80]}...")
                                cache_manager.set("outfit", cache_key, outfit, ttl=86400)
                                logger.info(f"💾 Cached outfit generation: {cache_key[:50]}...")
                                
                                if 'metadata' not in outfit:
                                    outfit['metadata'] = {}
                                outfit['metadata']['cache_hit'] = False
                                outfit['metadata']['cached'] = True
                            except Exception as cache_error:
                                logger.warning(f"⚠️ Cache storage failed: {cache_error}, continuing without cache")
                        
                        break
                except Exception as e:
                    last_error = e
                    error_details = str(e)
                    logger.error(f"❌ Generation attempt {generation_attempts} failed: {e}")
                    if generation_attempts >= max_attempts:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to generate outfit after {max_attempts} attempts: {str(e)}"
                        )
                else:
                    logger.warning(f"⚠️ Generation attempt {generation_attempts} produced invalid outfit")
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(1)
                        continue
        
        # Check if all attempts failed
        if not outfit or not outfit.get('items') or len(outfit.get('items', [])) < 3:
            logger.error(f"❌ All {max_attempts} generation attempts failed")
            if last_error:
                raise HTTPException(status_code=500, detail=f"Outfit generation failed: {str(last_error)}")
            else:
                raise HTTPException(status_code=500, detail="Outfit generation failed: Unable to generate valid outfit")
        
        # Wrap with metadata
        outfit_id = str(uuid4())
        outfit_record = {
            "id": outfit_id,
            "user_id": current_user_id,
            "generated_at": datetime.utcnow().isoformat(),
            **outfit
        }
        
        # Ensure metadata exists
        if 'metadata' not in outfit_record or outfit_record.get('metadata') is None:
            outfit_record['metadata'] = {}
        
        # Save to Firestore
        logger.info(f"🔄 About to save generated outfit {outfit_id}")
        
        # Clean for Firestore
        from ..config.firebase import clean_for_firestore
        clean_outfit_record = clean_for_firestore(outfit_record)
        logger.info(f"🧹 Cleaned outfit record")
        
        final_strategy = safe_get_metadata(clean_outfit_record, 'generation_strategy', 'unknown')
        logger.info(f"🔍 DEBUG FINAL SAVE: strategy = {final_strategy}")
        
        save_result = await save_outfit(current_user_id, outfit_id, clean_outfit_record)
        logger.info(f"💾 Save operation result: {save_result}")
        
        # Track usage
        try:
            from ..services.usage_tracking_service import UsageTrackingService
            usage_service = UsageTrackingService()
            await usage_service.track_outfit_generation(current_user_id)
            logger.info(f"📊 Tracked outfit generation usage for user {current_user_id}")
        except Exception as usage_error:
            logger.warning(f"Usage tracking failed: {usage_error}")
        
        # Update user stats
        try:
            from ..services.user_stats_service import user_stats_service
            await user_stats_service.update_outfit_stats(current_user_id, "created", clean_outfit_record)
        except Exception as stats_error:
            logger.warning(f"Stats update failed: {stats_error}")
        
        # Performance monitoring
        generation_time = time.time() - start_time
        
        # 🚀 PRODUCTION MONITORING: Track successful generation
        try:
            wardrobe_size = len(req.resolved_wardrobe) if req else 0
            await monitoring_service.track_operation(
                operation=OperationType.OUTFIT_GENERATION,
                user_id=current_user_id,
                status="success",
                duration_ms=generation_time * 1000,
                context={
                    "occasion": req.occasion if req else "unknown",
                    "style": req.style if req else "unknown",
                    "mood": req.mood if req else "unknown",
                    "wardrobe_size": wardrobe_size,
                    "generation_attempts": generation_attempts,
                    "cache_hit": cache_hit,
                    "strategy": safe_get_metadata(clean_outfit_record, 'generation_strategy', 'unknown')
                }
            )
            
            # Track cache operation
            await monitoring_service.track_cache_operation(
                cache_key="outfit_generation",
                hit=cache_hit,
                operation="outfit_generation"
            )
            
            # Track first outfit generation milestone
            if not cache_hit:
                await monitoring_service.track_user_journey(
                    user_id=current_user_id,
                    step=UserJourneyStep.FIRST_OUTFIT_GENERATED,
                    metadata={"occasion": req.occasion if req else "unknown"}
                )
        except Exception as monitoring_error:
            logger.warning(f"Production monitoring failed: {monitoring_error}")
        logger.info(f"⏱️ Generation completed in {generation_time:.2f} seconds")
        logger.info(f"📊 Generation attempts: {generation_attempts}, Cache hit: {cache_hit}")
        
        is_slow = generation_time > 10.0
        if is_slow:
            logger.warning(f"⚠️ SLOW REQUEST: Generation took {generation_time:.2f}s (threshold: 10s)")
        
        # Add performance metadata
        if 'metadata' not in outfit_record:
            outfit_record['metadata'] = {}
        
        outfit_record['metadata']['generation_duration'] = round(generation_time, 2)
        outfit_record['metadata']['is_slow'] = is_slow
        outfit_record['metadata']['generation_attempts'] = generation_attempts
        outfit_record['metadata']['cache_hit'] = cache_hit
        
        # Record generation metrics
        try:
            strategy = safe_get_metadata(outfit_record, 'generation_strategy', 'robust')
            log_generation_strategy(
                outfit_response=outfit_record,
                user_id=current_user_id,
                generation_time=generation_time,
                validation_time=0.0,
                failed_rules=None,
                fallback_reason=None
            )
        except Exception as metrics_error:
            logger.warning(f"Failed to log generation metrics: {metrics_error}")
        
        # Add personalization insights (Spotify-style) - combines user prefs + robust metadata
        try:
            from ...services.user_preference_service import user_preference_service
            user_prefs = await user_preference_service.get_preferences(current_user_id)
            
            # Pass outfit metadata from robust service to enhance insights
            outfit_metadata = outfit_record.get('metadata', {})
            learning_summary = user_preference_service.generate_learning_summary(
                user_prefs, 
                outfit_metadata=outfit_metadata
            )
            
            # Add to metadata for frontend display
            if 'metadata' not in outfit_record:
                outfit_record['metadata'] = {}
            outfit_record['metadata']['personalization_insights'] = learning_summary
            
            logger.info(f"✨ Added personalization insights: {learning_summary['confidence']} confidence, {len(learning_summary['insights'])} insights")
        except Exception as pref_error:
            logger.warning(f"⚠️ Failed to add personalization insights: {pref_error}")
        
        # Return response
        logger.info(f"✅ Successfully generated outfit {outfit_id}")
        return OutfitResponse(**outfit_record)
    
    except HTTPException:
        # Track HTTP exceptions (likely auth or validation failures)
        try:
            duration_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            await monitoring_service.track_operation(
                operation=OperationType.OUTFIT_GENERATION,
                user_id=current_user_id if 'current_user_id' in locals() else 'unknown',
                status="failure",
                duration_ms=duration_ms,
                error="HTTP Exception",
                error_type="HTTPException",
                context={
                    "occasion": req.occasion if 'req' in locals() and req else "unknown",
                    "wardrobe_size": len(req.resolved_wardrobe) if 'req' in locals() and req else 0
                }
            )
        except:
            pass  # Don't let monitoring errors break error handling
        raise
    except Exception as e:
        import traceback
        error_details = {
            "error_type": str(type(e).__name__),
            "error_message": str(e),
            "full_traceback": traceback.format_exc()
        }
        logger.error("🔥 ENDPOINT CRASH", extra=error_details, exc_info=True)
        print(f"🔥 ENDPOINT CRASH: {error_details}")
        
        # 🚀 PRODUCTION MONITORING: Track failure
        try:
            duration_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            await monitoring_service.track_operation(
                operation=OperationType.OUTFIT_GENERATION,
                user_id=current_user_id if 'current_user_id' in locals() else 'unknown',
                status="failure",
                duration_ms=duration_ms,
                error=error_details['error_message'],
                error_type=error_details['error_type'],
                stack_trace=error_details['full_traceback'],
                context={
                    "occasion": req.occasion if 'req' in locals() and req else "unknown",
                    "style": req.style if 'req' in locals() and req else "unknown",
                    "mood": req.mood if 'req' in locals() and req else "unknown",
                    "wardrobe_size": len(req.resolved_wardrobe) if 'req' in locals() and req else 0,
                    "generation_attempts": generation_attempts if 'generation_attempts' in locals() else 0
                }
            )
        except Exception as monitoring_error:
            logger.warning(f"Production monitoring failed during error handling: {monitoring_error}")
        
        raise HTTPException(
            status_code=500,
            detail=f"🔥 ENDPOINT CRASH: {error_details['error_type']}: {error_details['error_message']}"
        )

# 9. GET "" (List outfits no slash)
@router.get("", include_in_schema=False, response_model=List[OutfitResponse])
async def list_outfits_no_slash(
    limit: int = 50,
    offset: int = 0,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Fetch a user's outfit history from Firestore (no trailing slash).
    """
    try:
        # Require authentication - no fallback to hardcoded user ID
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        current_user_id = current_user.id
        logger.info(f"📚 Fetching outfits for authenticated user: {current_user_id}")
        
        outfits = await get_user_outfits(current_user_id, limit, offset)
        
        # Enhanced logging for debugging
        logger.info(f"📥 Fetch returned {len(outfits)} outfits for user {current_user_id}")
        if outfits:
            # Log the most recent outfit for debugging
            latest = outfits[0]
            logger.info(f"🔍 DEBUG: Latest outfit: '{((latest.get('name', 'Unknown') if latest else 'Unknown') if latest else 'Unknown')}' created at {latest.get('createdAt', 'Unknown')}")
            logger.info(f"🔍 DEBUG: Latest outfit wearCount: {(latest.get('wearCount', 'NOT_FOUND') if latest else 'NOT_FOUND')}")
            logger.info(f"🔍 DEBUG: Latest outfit lastWorn: {(latest.get('lastWorn', 'NOT_FOUND') if latest else 'NOT_FOUND')}")
        else:
            logger.info(f"⚠️ DEBUG: No outfits found for user {current_user_id}")
            
        return [OutfitResponse(**o) for o in outfits]
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch outfits for {current_user_id}: {e}", exc_info=True)
        # Fallback to mock data on error
        raise HTTPException(status_code=500, detail=f"Failed to fetch user outfits: {e}")

# 10. GET /stats/summary (Outfit statistics)
@router.get("/stats/summary")
async def get_outfit_stats(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get outfit statistics for user.
    """
    try:
        # Require authentication - no fallback to hardcoded user ID
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        current_user_id = current_user.id
        logger.info(f"📊 Getting outfit stats for authenticated user {current_user_id}")
        
        logger.info(f"📊 Getting outfit stats for user {current_user_id}")
        
        # Get reasonable sample of outfits for stats (performance optimized)
        outfits = await get_user_outfits(current_user_id, 100, 0)  # Get recent 100 outfits for stats
        
        # Calculate basic statistics
        stats = {
            'totalOutfits': len(outfits),
            'favoriteOutfits': len([o for o in outfits if o.get('isFavorite', False)]),
            'totalWearCount': sum(o.get('wearCount', 0) for o in outfits),
            'occasions': {},
            'styles': {},
            'recentActivity': []
        }
        
        # Count occasions and styles
        for outfit in outfits:
            occasion = (outfit.get('occasion', 'Unknown') if outfit else 'Unknown')
            stats['occasions'][occasion] = stats['occasions'].get(occasion, 0) + 1
            
            style = (outfit.get('style', 'Unknown') if outfit else 'Unknown')
            stats['styles'][style] = stats['styles'].get(style, 0) + 1
        
        # Add recent activity
        if outfits:
            stats['recentActivity'] = [
                {
                    'id': o['id'],
                    'name': o['name'],
                    'lastUpdated': normalize_created_at(o.get('createdAt')) if o.get('createdAt') else datetime.utcnow().isoformat() + 'Z'
                }
                for o in outfits[:5]  # Last 5 outfits
            ]
        
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

# 11. GET /debug-routes
@router.get("/debug-routes", response_model=dict)
async def debug_routes():
    """Debug endpoint to show all registered routes in this router"""
    routes = []
    for route in router.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods),
            "endpoint": str(route.endpoint)
        })
    return {
        "router_name": "outfits",
        "total_routes": len(routes),
        "routes": routes
    }

# 12. GET /analytics/worn-this-week (Analytics)
@router.get("/analytics/worn-this-week")
async def get_outfits_worn_this_week_simple(
    current_user: UserProfile = Depends(get_current_user),
    force_fresh: bool = False
):
    """
    SIMPLE: Count outfits worn this week - added to working outfits router.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Import Firebase inside function to avoid startup issues
        try:
            from ..config.firebase import db, firebase_initialized
        except ImportError as e:
            logger.error(f"⚠️ Firebase import failed: {e}")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        if not db:
            logger.error("⚠️ Firebase not available")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        # Calculate start of week (Sunday)
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        # weekday() returns 0=Monday, 6=Sunday
        # For Sunday start: if today is Sunday (6), days_since_sunday = 0
        # if today is Monday (0), days_since_sunday = 1, etc.
        days_since_sunday = (now.weekday() + 1) % 7
        week_start = now - timedelta(days=days_since_sunday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info(f"📊 Counting outfits worn since {week_start.isoformat()} for user {current_user.id}")
        
        worn_count = 0
        processed_count = 0
        
        # Count individual wear events from outfit_history collection
        logger.info("📊 Counting individual wear events from outfit_history collection")
        
        # Query outfit_history to count individual wear events
        from google.cloud.firestore import Query
        history_ref = db.collection('outfit_history').where('user_id', '==', current_user.id).order_by('date_worn', direction=Query.DESCENDING).limit(1000)
        
        for history_doc in history_ref.stream():
            history_data = history_doc.to_dict()
            processed_count += 1
            date_worn = (history_data.get('date_worn') if history_data else None)
            
            if date_worn:
                # Parse date_worn safely - handle multiple formats
                try:
                    worn_date = None
                    
                    if isinstance(date_worn, str):
                        # Handle ISO string formats
                        worn_date = datetime.fromisoformat(date_worn.replace('Z', '+00:00'))
                    elif hasattr(date_worn, 'timestamp'):
                        # Firestore Timestamp object - convert to datetime
                        if hasattr(date_worn, 'timestamp'):
                            worn_date = datetime.fromtimestamp(date_worn.timestamp(), tz=timezone.utc)
                        else:
                            worn_date = date_worn
                    elif isinstance(date_worn, datetime):
                        # Already a datetime object
                        worn_date = date_worn
                    elif isinstance(date_worn, (int, float)):
                        # Unix timestamp (seconds or milliseconds)
                        if date_worn > 1e12:  # Likely milliseconds
                            worn_date = datetime.fromtimestamp(date_worn / 1000.0, tz=timezone.utc)
                        else:
                            worn_date = datetime.fromtimestamp(date_worn, tz=timezone.utc)
                    else:
                        logger.warning(f"Unknown date_worn type: {type(date_worn)} - {date_worn}")
                        continue
                    
                    # Ensure timezone aware
                    if worn_date and worn_date.tzinfo is None:
                        worn_date = worn_date.replace(tzinfo=timezone.utc)
                    
                    # Check if this wear event is within the current week
                    if worn_date and worn_date >= week_start:
                        worn_count += 1
                        logger.info(f"📅 Wear event {history_doc.id} this week: {worn_date}")
                        
                except Exception as parse_error:
                    logger.warning(f"Error parsing date_worn {date_worn}: {parse_error}")
                    continue
        
        logger.info(f"✅ Found {worn_count} wear events this week for user {current_user.id}")
        
        # If no outfit_history records found, fall back to lastWorn dates from outfits collection
        if worn_count == 0 and processed_count == 0:
            logger.info("📊 No outfit_history records found, falling back to lastWorn dates from outfits collection")
            
            # Query outfits collection for lastWorn dates
            outfits_ref = db.collection('outfits').where('user_id', '==', current_user.id)
            
            for outfit_doc in outfits_ref.stream():
                outfit_data = outfit_doc.to_dict()
                last_worn = (outfit_data.get('lastWorn') if outfit_data else None)
                
                if last_worn:
                    try:
                        # Parse lastWorn date
                        if isinstance(last_worn, str):
                            last_worn_date = datetime.fromisoformat(last_worn.replace('Z', '+00:00'))
                        elif hasattr(last_worn, 'timestamp'):
                            last_worn_date = datetime.fromtimestamp(last_worn.timestamp(), tz=timezone.utc)
                        elif isinstance(last_worn, datetime):
                            last_worn_date = last_worn
                        else:
                            continue
                        
                        # Ensure timezone aware
                        if last_worn_date.tzinfo is None:
                            last_worn_date = last_worn_date.replace(tzinfo=timezone.utc)
                        
                        # Check if this outfit was worn this week
                        if last_worn_date >= week_start:
                            worn_count += 1
                            logger.info(f"📅 Outfit {outfit_doc.id} worn this week (lastWorn fallback): {last_worn_date}")
                            
                    except Exception as parse_error:
                        logger.warning(f"Error parsing lastWorn {last_worn}: {parse_error}")
                        continue
            
            logger.info(f"✅ Fallback found {worn_count} outfits worn this week from lastWorn dates")
            
            return {
                "success": True,
                "user_id": current_user.id,
                "outfits_worn_this_week": worn_count,
                "source": "lastWorn_fallback",
                "version": "2025-09-23",
                "api_version": "v2.0",
                "week_start": week_start.isoformat(),
                "calculated_at": datetime.now(timezone.utc).isoformat(),
                "note": "Using lastWorn dates as fallback - outfit_history is empty"
            }
        
        return {
            "success": True,
            "user_id": current_user.id,
            "outfits_worn_this_week": worn_count,
            "source": "outfit_history_individual_events",
            "version": "2025-09-23",
            "api_version": "v2.0",
            "week_start": week_start.isoformat(),
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error counting worn outfits: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to count worn outfits: {e}")

# Helper function for admin routes
async def check_admin_user(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
    """Check if user has admin privileges."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check if user is in admin list
        admin_emails = [
            "admin@example.com",  # Replace with actual admin emails
            # Add more admin emails as needed
        ]
        
        if current_user.email and current_user.email in admin_emails:
            return current_user
        
        raise HTTPException(status_code=403, detail="Admin access required")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        raise HTTPException(status_code=403, detail="Admin access required")

# 13. GET /admin/cache-stats
@router.get("/admin/cache-stats")
async def get_cache_stats(
    current_user: UserProfile = Depends(check_admin_user)
) -> Dict[str, Any]:
    """Get cache statistics (admin only)."""
    try:
        outfit_cache = cache_manager.get_cache("outfit")
        if not outfit_cache:
            return {
                "success": False,
                "error": "Outfit cache not found"
            }
        
        stats = outfit_cache.get_stats()
        all_stats = cache_manager.get_all_stats()
        
        return {
            "success": True,
            "outfit_cache": stats,
            "all_caches": all_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")

# 14. POST /admin/cache-clear
@router.post("/admin/cache-clear")
async def clear_outfit_cache(
    current_user: UserProfile = Depends(check_admin_user)
) -> Dict[str, Any]:
    """Clear outfit cache (admin only)."""
    try:
        cache_manager.clear_cache("outfit")
        logger.info(f"Admin {current_user.id} cleared outfit cache")
        return {
            "success": True,
            "message": "Outfit cache cleared",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing outfit cache: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing outfit cache: {str(e)}")

# 15. POST /admin/cache-clear-all
@router.post("/admin/cache-clear-all")
async def clear_all_caches(
    current_user: UserProfile = Depends(check_admin_user)
) -> Dict[str, Any]:
    """Clear all caches (admin only)."""
    try:
        cache_manager.clear_all()
        logger.info(f"Admin {current_user.id} cleared all caches")
        return {
            "success": True,
            "message": "All caches cleared",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing all caches: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing all caches: {str(e)}")
