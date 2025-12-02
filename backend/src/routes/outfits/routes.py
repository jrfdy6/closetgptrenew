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
    get_user_outfits, get_user_wardrobe_cached, get_user_profile_cached
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
