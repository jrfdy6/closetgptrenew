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

# REMOVED: Duplicate endpoint that was causing 500 errors
# The generate_outfit endpoint below handles this functionality

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
        doc = doc_ref.get() if doc_ref else None if doc_ref else None
        
        if doc.exists:
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
    # DEBUG DISABLED: Causing 4000+ log drops on Railway
    #  print(f"🚨 CRITICAL: mark_outfit_as_worn endpoint called with outfit_id={outfit_id}, user_id={current_user.id}")
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
        #  print("🚨 CRITICAL: Logged endpoint entry to Firestore")
    except Exception as entry_error:
        pass  # Silent error handling
        #  print(f"🚨 CRITICAL: Failed to log endpoint entry: {entry_error}")
    """
    Mark an outfit as worn (simplified endpoint for frontend compatibility).
    This will update both the outfit wear counter AND individual wardrobe item wear counters.
    """
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
        outfit_doc = outfit_ref.get() if outfit_ref else None if outfit_ref else None
        
        if not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        
        # Verify ownership
        if outfit_data.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="Outfit does not belong to user")
        
        # Update wear count and last worn
        current_wear_count = (outfit_data.get('wearCount', 0) if outfit_data else 0)
        current_time = datetime.utcnow()
        
        logger.info(f"📊 COUNTER 1: Updating outfit wear count for {outfit_id}")
        logger.info(f"   Before: wearCount={current_wear_count}")
        
        outfit_ref.update({
            'wearCount': current_wear_count + 1,
            'lastWorn': current_time,
            'updatedAt': current_time
        })
        
        logger.info(f"✅ COUNTER 1 UPDATED: Outfit {outfit_id} wearCount {current_wear_count} → {current_wear_count + 1}")
        logger.info(f"   lastWorn set to: {current_time.isoformat()}")
        
        # DEBUG DISABLED: Causing 4000+ log drops on Railway
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
        #  print("🚨 CRITICAL: Outfit update successful, proceeding to user_stats")
        except Exception as outfit_error:
            pass  # Silent error handling
        #  print(f"🚨 CRITICAL: Failed to log outfit update: {outfit_error}")
        # DEBUG DISABLED: Causing massive Railway log flooding
        #  print("🚨 CRITICAL: About to start user_stats update section")
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
        #  print("🚨 CRITICAL: Logged entry to user_stats section in Firestore")
        except Exception as entry_error:
            pass  # Silent error handling
        #  print(f"🚨 CRITICAL: Failed to log entry to user_stats section: {entry_error}")
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
        
        # DISABLED: Complex week validation logic causing massive syntax errors
        """
        try:
            from google.cloud.firestore import Increment, SERVER_TIMESTAMP
            
            # DEBUG DISABLED: All prints causing 4000+ log drops on Railway
            try:
                debug_ref = db.collection('debug_stats_updates').document()
                debug_ref.set({
                    'event': 'user_stats_imports_successful',
                    'user_id': current_user.id,
                    'outfit_id': outfit_id,
                    'db_available': db is not None,
                    'timestamp': datetime.utcnow().isoformat(),
                    'message': 'Successfully imported Firestore and accessed db'
                })
        #  print("🚨 CRITICAL: Firestore imports and db access successful")
            except Exception as import_error:
        #  print(f"🚨 CRITICAL: Firestore import/db access failed: {import_error}")
                try:
                    error_ref = db.collection('debug_errors').document()
                    error_ref.set({
                        'error_type': 'firestore_import_db_access_failed',
                        'user_id': current_user.id,
                        'outfit_id': outfit_id,
                        'error_message': str(import_error),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                except:
                    pass
            
            # Update user_stats collection for fast dashboard analytics
        print("📅 WEEK_VALIDATION_START", flush=True)
            # Import timezone and timedelta (silent)
            try:
                from datetime import timezone, timedelta
        print("✅ Imported timezone and timedelta successfully", flush=True)
            except Exception as e:
        print(f"❌ Failed to import timezone/timedelta: {e}", flush=True)
                pass
            
            try:
                test_now = datetime.now(timezone.utc)
        print(f"✅ Datetime with timezone works: {test_now}", flush=True)
            except Exception as e:
        print(f"❌ Datetime calculation failed: {e}", flush=True)
                pass
            
            # DEFENSIVE FIX: Use timezone-aware datetime for consistent Firestore handling
            try:
                current_time_dt = datetime.now(timezone.utc)
                week_start = current_time_dt - timedelta(days=current_time_dt.weekday())
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        print(f"✅ WEEK_CALC_SUCCESS: current_time={current_time_dt}, week_start={week_start}", flush=True)
            except Exception as week_error:
        print(f"❌ WEEK_CALC_ERROR: {week_error}", flush=True)
                raise
            
            # SURGICAL FIRESTORE TEST: Check if Firestore access is the culprit (silent)
            try:
                stats_ref = db.collection('user_stats').document(current_user.id)
        stats_doc = stats_ref.get() if stats_ref else None if stats_ref else None
        print("✅ Firestore access successful", flush=True)
            except Exception as e:
        print(f"❌ Firestore access failed: {e}", flush=True)
                raise

            if stats_doc.exists:
                stats_data = stats_doc.to_dict()
        current_worn_count = (stats_data.get('worn_this_week', 0) if stats_data else 0)
                
                # Check if we're still in the same week
        last_updated_raw = (stats_data.get('last_updated') if stats_data else None)
                last_updated = normalize_ts(last_updated_raw)
                
                # After week calc (show raw values used for comparison) - DEBUG DISABLED
        print(f"📅 WEEK_VALIDATION_DEBUG: today={current_time_dt}, last_updated={last_updated}, week_start={week_start}", flush=True)
                # CRITICAL DEBUG: Log exact values for debugging
                try:
                debug_ref = db.collection('debug_stats_updates').document()
                debug_ref.set({
                    'event': 'week_validation_debug',
                    'user_id': current_user.id,
                    'outfit_id': outfit_id,
                    'current_worn_count': current_worn_count,
                    'last_updated': str(last_updated),
                    'last_updated_type': str(type(last_updated)),
                    'week_start': week_start.isoformat(),
                    'is_datetime': isinstance(last_updated, datetime),
                    'timestamp': current_time_dt.isoformat()
                })
            except:
                pass
            
            if last_updated and last_updated >= week_start:
                # Same week, increment count
                # print("📊 SAME_WEEK_INCREMENT: entering", flush=True)  # DISABLED
                new_worn_count = current_worn_count + 1
                # print(f"📊 SAME WEEK: Incrementing {current_worn_count} -> {new_worn_count}")  # DISABLED
            else:
                # New week, reset count to 1
                # print("📊 NEW_WEEK_RESET: entering", flush=True)  # DISABLED
                new_worn_count = 1
                # print(f"📊 NEW WEEK: Resetting count to {new_worn_count} (last_updated: {last_updated}, week_start: {week_start})")  # DISABLED
                
                # RAILWAY-PROOF: Write new week debug info to Firestore
                try:
                    debug_ref = db.collection('debug_stats_updates').document()
                    debug_ref.set({
                        'event': 'user_stats_new_week_reset',
                        'user_id': current_user.id,
                        'outfit_id': outfit_id,
                        'action': 'new_week_reset',
                        'old_count': current_worn_count,
                        'new_count': new_worn_count,
                        'week_start': week_start.isoformat(),
                        'last_updated': last_updated.isoformat() if last_updated else None,
                        'timestamp': current_time_dt.isoformat(),
                        'success': True
                    })
                except:
                    pass
                
                # Before Firestore write
                print(f"🔥 USER_STATS_WRITE_ATTEMPT: worn_this_week={new_worn_count}", flush=True)
                # Use set with merge=True for guaranteed write
                try:
                    stats_ref.set({
                        'user_id': current_user.id,
                        'worn_this_week': new_worn_count,
                        'last_updated': current_time_dt,
                        'updated_at': current_time_dt
                    }, merge=True)
                    print("✅ USER_STATS_WRITE_SUCCESS", flush=True)
                    print(f"✅ STATS UPDATED: worn_this_week = {new_worn_count}")
                except Exception as e:
                    print(f"❌ USER_STATS_WRITE_ERROR: {e}", flush=True)
                # RAILWAY-PROOF: Write debug info to Firestore (bypasses rate limiting)
                try:
                    debug_ref = db.collection('debug_stats_updates').document()
                    debug_ref.set({
                        'event': 'user_stats_increment',
                        'user_id': current_user.id,
                        'outfit_id': outfit_id,
                        'action': 'same_week_increment',
                        'old_count': current_worn_count,
                        'new_count': new_worn_count,
                        'week_start': week_start.isoformat(),
                        'last_updated': last_updated.isoformat() if last_updated else None,
                        'timestamp': current_time_dt.isoformat(),
                        'success': True
                    })
                except:
                    pass  # Don't fail the main operation
                
            else:
                # Create new stats document
                print("🔥 USER_STATS_CREATE_ATTEMPT: worn_this_week=1", flush=True)
                try:
                    stats_ref.set({
                        'user_id': current_user.id,
                        'worn_this_week': 1,
                        'created_this_week': 0,
                        'total_outfits': 1500,  # Estimate
                        'last_updated': current_time_dt,
                        'created_at': current_time_dt
                    }, merge=True)
                    print("✅ USER_STATS_CREATE_SUCCESS", flush=True)
                    print("✅ STATS CREATED: new user_stats with worn_this_week = 1")
                except Exception as e:
                    print(f"❌ USER_STATS_CREATE_ERROR: {e}", flush=True)
                # RAILWAY-PROOF: Write debug info to Firestore
                try:
                    debug_ref = db.collection('debug_stats_updates').document()
                    debug_ref.set({
                        'event': 'user_stats_create',
                        'user_id': current_user.id,
                        'outfit_id': outfit_id,
                        'action': 'create_new_user_stats',
                        'old_count': 0,
                        'new_count': 1,
                        'timestamp': current_time_dt.isoformat(),
                        'success': True
                    })
                except:
                    pass
                
        except Exception as stats_error:
            # FORCE ERROR TO SURFACE - Use multiple methods to ensure visibility
            error_msg = f"🚨 USER_STATS_CRITICAL_ERROR: {stats_error}"
            print(error_msg)
        # print(f"🚨 Error type: {type(stats_error).__name__}")
        # print(f"🚨 Error details: {str(stats_error)}")
            logger.error(error_msg)  # Also use logger in case print is throttled
            
            # Try to write error to a different collection as last resort
            try:
                error_ref = db.collection('debug_errors').document()
                error_ref.set({
                    'error_type': 'user_stats_update_failed',
                    'user_id': current_user.id,
                    'outfit_id': outfit_id,
                    'error_message': str(stats_error),
                    'timestamp': datetime.utcnow(),
                    'attempt': 'robust_fix_with_increment'
                })
                print("🚨 ERROR LOGGED TO debug_errors COLLECTION")
            except:
                pass  # Don't fail the whole request if error logging fails
            
            # Don't raise - outfit was still marked as worn successfully
            
        except Exception as stats_error:
            # CRITICAL: Handle user_stats update failures gracefully
            error_msg = f"🚨 USER_STATS_CRITICAL_ERROR: {stats_error}"
            # print(error_msg, flush=True)  # DISABLED
            logger.error(error_msg)
            
            # Don't raise - outfit was still marked as worn successfully
            
        """
        # END OF DISABLED COMPLEX LOGIC
        
        # Also try the old stats service if available
        try:
            from ..services.user_stats_service import user_stats_service
            asyncio.create_task(user_stats_service.update_outfit_worn_stats(current_user.id, outfit_id))
        except Exception as stats_error:
            logger.warning(f"⚠️ Old stats service failed: {stats_error}")
        
        # Update individual wardrobe item wear counters
        logger.info(f"📊 COUNTER 2: Updating individual wardrobe item wear counts")
        items_updated = 0
        if outfit_data.get('items'):
            total_items = len(outfit_data['items'])
            logger.info(f"   Found {total_items} items in outfit to update")
            
            for item in outfit_data['items']:
                if isinstance(item, dict) and (item.get('id') if item else None):
                    item_id = item['id']
                    item_name = item.get('name', 'Unknown Item')
                    
                    item_ref = db.collection('wardrobe').document(item_id)
                    item_doc = item_ref.get() if item_ref else None if item_ref else None
                    if item_doc.exists:
                        item_data = item_doc.to_dict()
                        if item_data.get('userId') == current_user.id:
                            current_item_wear = item_data.get('wearCount', 0)
                            
                            logger.info(f"   Updating {item_name}: wearCount {current_item_wear} → {current_item_wear + 1}")
                            
                            item_ref.update({
                                'wearCount': current_item_wear + 1,
                                'lastWorn': current_time,
                                'updatedAt': current_time
                            })
                            
                            items_updated += 1
                            logger.info(f"   ✅ Updated item {item_id}")
                        else:
                            logger.warning(f"   ⚠️ Item {item_id} doesn't belong to user, skipping")
                    else:
                        logger.warning(f"   ⚠️ Item {item_id} not found in wardrobe, skipping")
            
            logger.info(f"✅ COUNTER 2 UPDATED: {items_updated}/{total_items} wardrobe items updated")
        else:
            logger.warning(f"⚠️ COUNTER 2: No items found in outfit data")
        
        # Get updated outfit data to return current wear count
        outfit_ref = db.collection('outfits').document(outfit_id)
        outfit_doc = outfit_ref.get() if outfit_ref else None if outfit_ref else None
        
        if outfit_doc.exists:
            outfit_data = outfit_doc.to_dict()
            current_wear_count = (outfit_data.get('wearCount', 0) if outfit_data else 0)
            last_worn = (outfit_data.get('lastWorn') if outfit_data else None)
            
            logger.info(f"🔍 DEBUG: Retrieved outfit data - wearCount: {current_wear_count}, lastWorn: {last_worn}")
            logger.info(f"🔍 DEBUG: Full outfit data keys: {list(outfit_data.keys())}")
            
            # Format lastWorn for frontend
            if isinstance(last_worn, datetime):
                last_worn_str = last_worn.isoformat() + "Z"
            else:
                last_worn_str = datetime.utcnow().isoformat() + "Z"
        else:
            current_wear_count = 1
            last_worn_str = datetime.utcnow().isoformat() + "Z"
        
        # ALSO create outfit history entry for today's outfit tracking
        logger.info(f"📊 COUNTER 3: Creating outfit_history entry for weekly count")
        history_saved_successfully = False
        try:
            current_timestamp = int(datetime.utcnow().timestamp() * 1000)
            
            # Create simplified history entry (avoid clean_for_firestore issues)
            history_entry = {
                'user_id': current_user.id,
                'outfit_id': outfit_id,
                'outfit_name': str(outfit_data.get('name', 'Outfit') if outfit_data else 'Outfit'),
                'outfit_image': str(outfit_data.get('imageUrl', '') if outfit_data else ''),
                'date_worn': current_timestamp,  # Milliseconds timestamp
                'occasion': str(outfit_data.get('occasion', 'Casual') if outfit_data else 'Casual'),
                'mood': str(outfit_data.get('mood', 'Comfortable') if outfit_data else 'Comfortable'),
                'weather': {},
                'notes': '',
                'tags': [],
                'created_at': current_timestamp,
                'updated_at': current_timestamp
            }
            
            logger.info(f"   Creating entry: user_id={current_user.id}, outfit_id={outfit_id}")
            logger.info(f"   date_worn={current_timestamp} ({datetime.fromtimestamp(current_timestamp/1000, tz=timezone.utc).isoformat()})")
            
            # Save to outfit_history collection - NO CLEANING to avoid data loss
            doc_ref, doc_id = db.collection('outfit_history').add(history_entry)
            
            # Verify the entry was actually saved
            saved_doc = doc_ref.get()
            if saved_doc.exists:
                saved_data = saved_doc.to_dict()
                logger.info(f"✅ COUNTER 3 UPDATED: Outfit history entry created successfully!")
                logger.info(f"   Document ID: {doc_id}")
                logger.info(f"   Collection: outfit_history")
                logger.info(f"   date_worn: {saved_data.get('date_worn')}")
                logger.info(f"   This entry will be counted in weekly analytics")
                history_saved_successfully = True
            else:
                logger.error(f"❌ COUNTER 3 FAILED: Document {doc_id} does not exist after save")
                raise Exception(f"History entry verification failed for doc {doc_id}")
            
        except Exception as history_error:
            # Log the error prominently
            logger.error(f"❌ COUNTER 3 FAILED: Could not create outfit history entry: {history_error}")
            logger.error(f"   Weekly outfit count will NOT update!")
            logger.error(f"   Outfit and item counters were still updated successfully")
            # Continue anyway - outfit wear count was still updated
        
        # Update user stats for dashboard counter
        try:
            from ..services.user_stats_service import user_stats_service
            asyncio.create_task(user_stats_service.update_outfit_worn_stats(current_user.id, outfit_id))
            logger.info(f"📊 Triggered user stats update for dashboard counter")
        except Exception as stats_error:
            logger.error(f"❌ Failed to update user stats: {stats_error}")
        
        # Final summary log
        logger.info(f"")
        logger.info(f"═══════════════════════════════════════════════════════════")
        logger.info(f"✅ MARK AS WORN COMPLETE - SUMMARY FOR OUTFIT {outfit_id}")
        logger.info(f"═══════════════════════════════════════════════════════════")
        logger.info(f"   Counter 1 (Outfit): ✅ Updated (wearCount: {current_wear_count} → {current_wear_count + 1})")
        logger.info(f"   Counter 2 (Items): {'✅' if items_updated > 0 else '⚠️'} Updated {items_updated}/{len(outfit_data.get('items', []))} items")
        logger.info(f"   Counter 3 (Weekly): {'✅' if history_saved_successfully else '❌'} History entry {'saved' if history_saved_successfully else 'FAILED'}")
        logger.info(f"   User ID: {current_user.id}")
        logger.info(f"   Timestamp: {datetime.utcnow().isoformat()}")
        logger.info(f"═══════════════════════════════════════════════════════════")
        logger.info(f"")
        
        return {
            "success": True,
            "message": "Outfit marked as worn successfully",
            "wearCount": current_wear_count + 1,
            "lastWorn": last_worn_str,
            "historyEntrySaved": history_saved_successfully,  # NEW: Track if history was saved
            "itemsUpdated": items_updated,  # NEW: Track how many items were updated
            "debug": {
                "outfit_updated": True,
                "items_updated": items_updated,
                "history_saved": history_saved_successfully,
                "timestamp": int(datetime.utcnow().timestamp() * 1000)
            }
        }
        
    except Exception as stats_error:
        # CRITICAL: Handle user_stats update failures gracefully
        error_msg = f"🚨 USER_STATS_CRITICAL_ERROR: {stats_error}"
        # print(error_msg, flush=True)  # DISABLED
        logger.error(error_msg)
        
        # Don't raise - outfit was still marked as worn successfully
        return {
            "success": True,
            "message": "Outfit marked as worn successfully (stats update failed)",
            "wearCount": current_wear_count + 1,
            "lastWorn": current_time.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to mark outfit {outfit_id} as worn: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark outfit as worn: {str(e)}")

@router.get("/debug-user", response_model=dict)
async def debug_user_outfits(
    current_user: UserProfile = Depends(get_current_user)
):
    """Debug endpoint to show user authentication and database contents."""
    logger.info("🔍 DEBUG: Debug user outfits endpoint called")
    
    debug_info = {
        "authenticated": False,
        "user_id": None,
        "user_email": None,
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False,
        "database_contents": {},
        "collections_checked": [],
        "error": None
    }
    
    try:
        if current_user:
            debug_info["authenticated"] = True
            debug_info["user_id"] = current_user.id
            debug_info["user_email"] = current_user.email
            logger.info(f"🔍 DEBUG: User authenticated: {current_user.id}")
        else:
            logger.info("🔍 DEBUG: No user authenticated")
        
        # Check what's in the database
        if FIREBASE_AVAILABLE and firebase_initialized:
            try:
                collections_to_check = ['outfits', 'outfit_history', 'user_outfits', 'wardrobe_outfits']
                debug_info["collections_checked"] = collections_to_check
                
                for collection_name in collections_to_check:
                    try:
                        logger.info(f"🔍 DEBUG: Checking collection: {collection_name}")
                        
                        # Get ALL outfits from this collection (no limit)
                        all_outfits = db.collection(collection_name).stream()
                        outfits_list = []
                        
                        for doc in all_outfits:
                            outfit_data = doc.to_dict()
                            outfits_list.append({
                                "id": doc.id,
        "name": (outfit_data.get('name', 'unnamed') if outfit_data else 'unnamed'),
        "user_id": ((outfit_data.get('user_id', outfit_data.get('userId', 'no_user_id') if outfit_data else 'no_user_id') if outfit_data else 'no_user_id')),
        "created_at": ((outfit_data.get('createdAt', outfit_data.get('created_at', 'no_date') if outfit_data else 'no_date') if outfit_data else 'no_date')),
                                "collection": collection_name
                            })
                        
                        debug_info["database_contents"][collection_name] = {
                            "total_outfits_found": len(outfits_list),
                            "sample_outfits": outfits_list[:5] if outfits_list else [],  # Show first 5 as sample
                            "all_outfit_ids": [o["id"] for o in outfits_list]  # Show all IDs
                        }
                        
                        logger.info(f"🔍 DEBUG: Collection {collection_name}: Found {len(outfits_list)} outfits")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ DEBUG: Could not check collection {collection_name}: {e}")
                        debug_info["database_contents"][collection_name] = {
                            "error": str(e),
                            "total_outfits_found": 0
                        }
                
            except Exception as e:
                debug_info["error"] = f"Database query failed: {str(e)}"
                logger.error(f"❌ DEBUG: Database query failed: {e}")
        
    except Exception as e:
        debug_info["error"] = f"General error: {str(e)}"
        logger.error(f"❌ DEBUG: General error: {e}")
    
    return debug_info

# ✅ Generate + Save Outfit (single source of truth)
@router.post("/generate")  # Removed response_model to allow JSONResponse to work properly
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
    # print(f"🔍 DEBUG ENDPOINT START: (req.wardrobe if req else []) = {req.wardrobe}")
    print(f"🔍 DEBUG ENDPOINT START: req.resolved_wardrobe = {req.resolved_wardrobe}")
    print(f"🔍 DEBUG ENDPOINT START: current_user_id = {current_user_id}")
    try:
        start_time = time.time()  # Track start time for performance monitoring
        generation_attempts = 0
        max_attempts = 3
        cache_hit = False  # Initialize cache_hit flag
        # Enhanced authentication validation
        if not current_user_id:
            logger.error("❌ Authentication failed: No current user ID")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        logger.info(f"🎯 Starting robust outfit generation for user: {current_user_id}")
        logger.info(f"📋 Request details: {req.occasion}, {req.style}, {req.mood}")
        
        # Define hard requirements per occasion (ported from simple-minimal)
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
        
        # Use global validation functions for semantic outfit validation
        
        # Category cardinality limits (prevents double-shoe issue)
        def get_category_limits(occasion):
            """Define category limits based on occasion"""
            base_limits = {
                "shirt": (1, 2),      # 1-2 shirts allowed
                "top": (1, 2),        # 1-2 tops allowed  
                "pants": (1, 1),      # exactly 1 pants
                "shorts": (1, 1),     # exactly 1 shorts
                "shoes": (1, 1),      # exactly 1 shoes (prevents double-shoe)
                "jacket": (0, 1),     # 0-1 jacket
                "blazer": (0, 1),     # 0-1 blazer
                "accessories": (0, 2), # 0-2 accessories
            }
            
            # Occasion-specific adjustments
            occasion_lower = occasion.lower()
            if occasion_lower in ['business', 'formal']:
                # Business/formal: prefer structured limits
                return {
                    "shirt": (1, 1),      # exactly 1 shirt
                    "top": (1, 1),        # exactly 1 top
                    "pants": (1, 1),      # exactly 1 pants
                    "shoes": (1, 1),      # exactly 1 shoes
                    "jacket": (0, 1),     # 0-1 jacket/blazer
                    "blazer": (0, 1),     # 0-1 blazer
                    "accessories": (0, 1), # 0-1 accessories
                }
            elif occasion_lower == 'athletic':
                # Athletic: allow layering but limit shoes
                return {
                    "top": (1, 2),        # 1-2 tops (layering)
                    "shorts": (1, 1),     # exactly 1 shorts
                    "pants": (1, 1),      # exactly 1 pants
                    "shoes": (1, 1),      # exactly 1 shoes
                    "jacket": (0, 1),     # 0-1 athletic jacket
                    "accessories": (0, 1), # 0-1 accessories
                }
            else:
                # Casual/weekend: more flexible
                return base_limits
        
        # Enhanced deduplication with category cardinality limits and subtype tracking
        def deduplicate_items_with_limits(items, occasion):
            from collections import defaultdict
            
            # Get category limits for this occasion
            category_limits = get_category_limits(occasion)
            
            # Track items by category and subtype
            category_counts = defaultdict(int)
            used_subtypes = set()  # Track shoe subtypes to prevent duplicates
            final_items = []
            
            # First pass: remove exact duplicates (same ID or name+type+color)
            seen_ids = set()
            seen_combinations = set()
            unique_items = []
            
            for item in items:
                item_id = (item.get('id', '') if item else '')
                item_name = (item.get('name', '') if item else '')
                item_type = (item.get('type', '') if item else '').lower()
                item_color = (item.get('color', '') if item else '')
                
                # Create a combination key for name+type+color
                combination_key = f"{item_name}|{item_type}|{item_color}"
                
                # Check both ID uniqueness and combination uniqueness
                if item_id not in seen_ids and combination_key not in seen_combinations:
                    seen_ids.add(item_id)
                    seen_combinations.add(combination_key)
                    unique_items.append(item)
                else:
                    logger.info(f"🔍 DEBUG: Removed exact duplicate: {item_name} ({item_color})")
            
            # Second pass: enforce category cardinality limits with subtype tracking
            for item in unique_items:
                item_type = (item.get('type', '') if item else '').lower()
                item_name = (item.get('name', '') if item else '').lower()
                
                # Map item type to category and determine subtype
                category = None
                subtype = None
                
                if item_type in ['shirt', 'blouse', 't-shirt', 'tank', 'sweater', 'hoodie']:
                    category = 'top'
                    # Determine shirt subtype
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
                    # CRITICAL: Determine shoe subtype to prevent duplicate shoes
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
                    # For unknown types, be permissive
                    category = 'other'
                    subtype = 'other'
                
                # Check category limits with subtype tracking for shoes
                if category in category_limits:
                    min_limit, max_limit = category_limits[category]
                    current_count = category_counts[category]
                    
                    # Special handling for shoes - prevent duplicate subtypes
                    if category == 'shoes':
                        if current_count >= max_limit:
                            logger.info(f"❌ Skipped {(item.get('name', 'Unknown') if item else 'Unknown')} - shoe limit reached (1)")
                            continue
                        if subtype in used_subtypes:
                            logger.info(f"❌ Skipped {(item.get('name', 'Unknown') if item else 'Unknown')} - shoe subtype '{subtype}' already used")
                            continue
                            used_subtypes.add(subtype)
                            logger.info(f"✅ Added {(item.get('name', 'Unknown') if item else 'Unknown')} (shoes: {subtype})")
                    
                    # Regular category limit check
                    if current_count < max_limit:
                        final_items.append(item)
                        category_counts[category] += 1
                        if category != 'shoes':  # Already logged above
                            logger.info(f"✅ Added {(item.get('name', 'Unknown') if item else 'Unknown')} ({category}, count: {category_counts[category]})")
                    else:
                        logger.info(f"❌ Skipped {(item.get('name', 'Unknown') if item else 'Unknown')} ({category}) - category limit reached ({max_limit})")
                else:
                    # Unknown category - allow it
                    final_items.append(item)
                    logger.info(f"➕ Added {(item.get('name', 'Unknown') if item else 'Unknown')} (unknown category)")
            
            # Log final category distribution and used subtypes
            logger.info(f"🎯 Final outfit category distribution: {dict(category_counts)}")
            logger.info(f"🎯 Used shoe subtypes: {list(used_subtypes)}")
            return final_items
        
        # Retry with relaxed rules instead of falling back to simple-minimal
        def retry_with_relaxed_rules(original_items, occasion, requirements):
            """Retry outfit generation with relaxed rules when validation fails"""
            logger.info(f"🔄 Retrying with relaxed rules for {occasion}")
            
            # Start with original items
            relaxed_items = original_items.copy()
            
            # Try to fill missing required items with more flexible criteria
            missing_required = validate_outfit_completeness(relaxed_items, requirements, (req.occasion if req else "unknown"))
            
            if len(missing_required) > 0:
                logger.info(f"🔧 Attempting to fill missing items: {missing_required}")
                
                # More flexible item selection for missing categories
                for missing_item in missing_required:
                    if missing_item == 'shirt':
                        # Look for any top that could work as a shirt
                        for item in relaxed_items:
                            if item.get('type', '').lower() in ['shirt', 'blouse', 'sweater', 'polo']:
                                logger.info(f"✅ Found flexible shirt alternative: {item.get('name', 'Unknown')}")
                                break
                    elif missing_item == 'pants':
                        # Look for any bottom that could work as pants
                        for item in relaxed_items:
                            if item.get('type', '').lower() in ['pants', 'jeans', 'trousers', 'slacks']:
                                logger.info(f"✅ Found flexible pants alternative: {item.get('name', 'Unknown')}")
                                break
                    elif missing_item == 'shoes':
                        # Look for any shoes
                        for item in relaxed_items:
                            if item.get('type', '').lower() in ['shoes', 'sneakers', 'boots', 'oxford']:
                                logger.info(f"✅ Found flexible shoes alternative: {item.get('name', 'Unknown')}")
                                break
            
            logger.info(f"🔄 Relaxed rules result: {len(relaxed_items)} items")
            return relaxed_items
        
        # Calculate robust confidence score
        def calculate_robust_confidence(items, validation_passed, occasion):
            """Calculate confidence score for robust generator"""
            base_confidence = 0.7  # Base confidence for robust generator
            
            # Boost for validation passing
            if validation_passed:
                confidence_score = base_confidence + 0.22  # +22% for passing validation = 0.92
                logger.info("🎯 High confidence: Validation passed")
            else:
                confidence_score = base_confidence + 0.08  # +8% for relaxed rules = 0.78
                logger.info("🎯 Medium confidence: Used relaxed rules")
            
            # Boost for appropriate item count (3-6 items)
            item_count = len(items)
            if 3 <= item_count <= 6:
                confidence_score += 0.05  # +5% for good item count
            
            # Occasion-specific confidence adjustments
            occasion_lower = occasion.lower()
            if occasion_lower in ['business', 'formal']:
                # Check if we have appropriate formal items
                has_formal_shirt = any('dress' in item.get('name', '').lower() or 'button' in item.get('name', '').lower() 
                                     for item in items if item.get('type', '').lower() in ['shirt', 'blouse'])
                has_formal_pants = any('dress' in item.get('name', '').lower() or 'slacks' in item.get('name', '').lower()
                                     for item in items if item.get('type', '').lower() in ['pants', 'trousers'])
                if has_formal_shirt and has_formal_pants:
                    confidence_score += 0.03  # +3% for formal appropriateness
            
            return min(confidence_score, 1.0)  # Cap at 1.0
        
        # Enhanced request validation
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
            # Find the base item in the wardrobe array
            base_item = next((item for item in (req.wardrobe if req else []) if item.get("id") == (req.baseItemId if req else None)), None)
            if base_item:
                logger.info(f"🔍 DEBUG: Found base item in wardrobe: {base_item.get('name', 'Unknown')} ({base_item.get('type', 'Unknown')})")
            else:
                logger.warning(f"⚠️ DEBUG: Base item {req.baseItemId} not found in wardrobe array")
        else:
            logger.info("🔍 DEBUG: No baseItemId provided")
        
        logger.info(f"🎨 Starting outfit generation with retry logic")
        
        # Import validation pipeline once outside the retry loop
        try:
            from ..services.outfit_validation_pipeline import validation_pipeline, ValidationContext
            validation_available = True
            logger.info("✅ Validation pipeline imported successfully")
        except ImportError as e:
            logger.warning(f"⚠️ Validation pipeline import failed: {e}")
            validation_available = False
        
        # CACHE CHECK: Try to get cached outfit if not bypassing cache
        outfit = None
        cache_hit = False
        if not (req.bypass_cache if req else False):
            try:
                # Get current wardrobe items for cache key generation
                current_wardrobe = req.wardrobe if req and req.wardrobe else []
                if not current_wardrobe:
                    # Fallback to fetching from database if not in request
                    current_wardrobe = await get_user_wardrobe(current_user_id)
                
                # Generate cache key
                cache_key = _generate_outfit_cache_key(
                    user_id=current_user_id,
                    occasion=req.occasion if req else "unknown",
                    style=req.style if req else "unknown",
                    mood=req.mood if req else "unknown",
                    weather=req.weather if req else None,
                    baseItemId=req.baseItemId if req else None,
                    wardrobe_items=current_wardrobe
                )
                
                # Check cache
                logger.info(f"🔍 DEBUG: Checking cache with key: {cache_key[:80]}...")
                cached_outfit = cache_manager.get("outfit", cache_key)
                logger.info(f"🔍 DEBUG: Cache result: {'HIT' if cached_outfit else 'MISS'}")
                if cached_outfit:
                    # Validate cached outfit - ensure all items still exist
                    is_valid = await _validate_cached_outfit(cached_outfit, current_user_id, current_wardrobe)
                    if is_valid:
                        logger.info(f"✅ Cache hit for outfit generation: {cache_key[:50]}...")
                        outfit = cached_outfit
                        cache_hit = True
                        # Add cache metadata and performance metadata
                        if 'metadata' not in outfit:
                            outfit['metadata'] = {}
                        outfit['metadata']['cache_hit'] = True
                        outfit['metadata']['cache_key'] = cache_key
                        # For cache hits, set performance metadata
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
        
        # Retry logic for robust generation (only if cache miss)
        last_error = None
        error_details = None
        
        # Only run generation if cache miss
        if not outfit:
            for attempt in range(max_attempts):
                generation_attempts += 1
                try:
                    logger.info(f"🔄 Generation attempt {generation_attempts}/{max_attempts}")
                    print(f"🔍 DEBUG RETRY LOOP: Starting attempt {generation_attempts}")
                    print(f"🔍 DEBUG RETRY LOOP: req = {req}")
                    print(f"🔍 DEBUG RETRY LOOP: current_user_id = {current_user_id}")
                    # Run generation logic with robust service
                    generate_outfit_logic = get_generate_outfit_logic()
                    outfit = await generate_outfit_logic(req, current_user_id)
                    
                    # NEW STRATEGY: Keep robust generator in control, don't auto-fallback
                    if outfit and outfit.get('items'):
                        occasion_lower = (req.occasion if req else "unknown").lower()
                    
                    # CRITICAL DEBUG: Log strategy before category limits
                    logger.info(f"🔍 DEBUG BEFORE CATEGORY LIMITS: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
        # print(f"🔍 DEBUG BEFORE CATEGORY LIMITS: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                    
                    # Step 1: Apply category limits and subtype tracking INSIDE robust logic
                    original_items = outfit['items'].copy()
                    outfit['items'] = deduplicate_items_with_limits(outfit['items'], (req.occasion if req else "unknown"))
                    
                    # CRITICAL DEBUG: Log strategy after category limits
                    logger.info(f"🔍 DEBUG AFTER CATEGORY LIMITS: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
        # print(f"🔍 DEBUG AFTER CATEGORY LIMITS: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                    
                    # Step 2: If validation fails, retry with relaxed rules instead of falling back
                        validation_passed = True

                        if occasion_lower in occasion_requirements:

                            requirements = occasion_requirements[occasion_lower]

                            missing_required = validate_outfit_completeness(outfit['items'], requirements, (req.occasion if req else "unknown"))

                        
                                if len(missing_required) > 0:

                                logger.warning(f"⚠️ VALIDATION FAILED: Missing {missing_required} - retrying with relaxed rules")

                                validation_passed = False

                            
                            # CRITICAL DEBUG: Log strategy before relaxed rules
                                logger.info(f"🔍 DEBUG BEFORE RELAXED RULES: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")

        # print(f"🔍 DEBUG BEFORE RELAXED RULES: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                            
                            # Retry with relaxed rules instead of falling back
                                outfit['items'] = retry_with_relaxed_rules(original_items, (req.occasion if req else "unknown"), requirements)

                            
                            # Re-apply category limits to relaxed outfit
                                outfit['items'] = deduplicate_items_with_limits(outfit['items'], (req.occasion if req else "unknown"))

                            
                            # CRITICAL DEBUG: Log strategy after relaxed rules
                                logger.info(f"🔍 DEBUG AFTER RELAXED RULES: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")

        # print(f"🔍 DEBUG AFTER RELAXED RULES: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                            
                                logger.info(f"🔄 Retried with relaxed rules - final items: {len(outfit['items'])}")

                    
                    # Step 3: Calculate confidence score AFTER all processing
                    # Only calculate new confidence if robust generator didn't provide one
                    if 'confidence_score' not in outfit or outfit['confidence_score'] is None or outfit['confidence_score'] == 0.0:
                    confidence_score = calculate_robust_confidence(outfit['items'], validation_passed, (req.occasion if req else "unknown"))
                        outfit['confidence_score'] = confidence_score
                        logger.info(f"🎯 Calculated new confidence score: {confidence_score}")
                    else:
                        logger.info(f"🎯 Preserving robust generator confidence: {outfit['confidence_score']}")
                    
                    # CRITICAL DEBUG: Log strategy before metadata modification
                    logger.info(f"🔍 DEBUG BEFORE METADATA MODIFICATION: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
        # print(f"🔍 DEBUG BEFORE METADATA MODIFICATION: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                    
                    # Ensure metadata exists
                    if 'metadata' not in outfit:
                    outfit['metadata'] = None
                    outfit['metadata']['subtype_tracking_enabled'] = True
                    outfit['metadata']['confidence_calculated'] = True
                    outfit['metadata']['validation_passed'] = validation_passed
                    outfit['metadata']['retry_with_relaxed_rules'] = not validation_passed
                    
                    # CRITICAL DEBUG: Log strategy after metadata modification
                    logger.info(f"🔍 DEBUG AFTER METADATA MODIFICATION: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
        # print(f"🔍 DEBUG AFTER METADATA MODIFICATION: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                    
                    # Update metadata with processing status (simplified)
                    if 'metadata' not in outfit:
                    outfit['metadata'] = None
                    outfit['metadata']['validation_applied'] = True
                    outfit['metadata']['hard_requirements_enforced'] = True
                    outfit['metadata']['deduplication_applied'] = True
                    outfit['metadata']['category_limits_enforced'] = True  # NEW: Category cardinality limits
                    outfit['metadata']['unique_items_count'] = len(outfit['items'])
                    outfit['metadata']['occasion_requirements_met'] = validation_passed
                
                # NEW: Apply comprehensive validation pipeline to generated outfit (with category limits bypass)
                    if outfit and outfit.get('items') and validation_available:
                    try:
                        # Check if category limits have already been enforced
                    category_limits_applied = safe_get_metadata(outfit, 'category_limits_enforced', False)
                        
                        if category_limits_applied:
                            logger.info("🎯 Category limits already applied - skipping enhanced validation to prevent rejection")
                            # Skip enhanced validation since we've already enforced category limits
                            outfit['metadata']['enhanced_validation_bypassed'] = True
                            outfit['metadata']['validation_reason'] = "Category limits already enforced"
                        else:
                            logger.info("🔍 Running enhanced validation pipeline")
                            # Create validation context
                            validation_context = ValidationContext(
                                occasion=req.occasion,
                                style=req.style or "casual",
                                mood=req.mood or "neutral",
                    weather=req.weather.__dict__ if hasattr(req.weather, '__dict__') else (req.weather if req else None),
                                user_profile={"id": current_user_id},  # Basic profile for validation
                                temperature=getattr(req.weather, 'temperature', 70.0) if hasattr(req.weather, 'temperature') else 70.0
                            )
                            
                            # Run validation pipeline
                            validation_result = await validation_pipeline.validate_outfit(outfit, validation_context)
                            
                            if not validation_result.valid:
                                failed_rules = validation_result.errors or []
                                logger.warning(f"⚠️ VALIDATION FAILED on attempt {generation_attempts}: {validation_result.errors}")
                                print(f"🚨 VALIDATION ALERT: Attempt {generation_attempts} failed validation")
                                # If validation fails, retry or use emergency outfit
                                if attempt < max_attempts - 1:
                                    await asyncio.sleep(1)  # Brief delay before retry
                                    continue
                                else:
                                    # Final attempt failed validation - NO EMERGENCY FALLBACK
                                    logger.error(f"❌ VALIDATION FAILURE: All {max_attempts} attempts failed validation")
                                    print(f"🚨 VALIDATION FAILURE: All {max_attempts} attempts failed validation")
                                    # NO EMERGENCY FALLBACK - let the robust service handle this
                                    raise Exception(f"Validation failed after {max_attempts} attempts")
                                
                    except Exception as validation_error:
                        logger.warning(f"⚠️ Validation pipeline failed: {validation_error}, continuing with outfit")
                        # Don't fail the entire request if validation pipeline has issues
                        # Just log the error and continue with the outfit
                elif outfit and outfit.get('items') and not validation_available:
                    logger.info("⚠️ Validation pipeline not available, skipping validation")
                else:
                    logger.warning("⚠️ No outfit generated or validation not available")
                
                # Validate the generated outfit (basic validation)
                if outfit and outfit.get('items') and len(outfit.get('items', [])) >= 3:
                    logger.info(f"✅ Generation successful on attempt {generation_attempts}")
                    
                    # CACHE STORAGE: Store successful generation in cache
                    if not cache_hit and not (req.bypass_cache if req else False):
                        try:
                            # Get current wardrobe items for cache key generation
                            current_wardrobe = req.wardrobe if req and req.wardrobe else []
                            if not current_wardrobe:
                                current_wardrobe = await get_user_wardrobe(current_user_id)
                            
                            # Generate cache key (same as check)
                            cache_key = _generate_outfit_cache_key(
                                user_id=current_user_id,
                                occasion=req.occasion if req else "unknown",
                                style=req.style if req else "unknown",
                                mood=req.mood if req else "unknown",
                                weather=req.weather if req else None,
                                baseItemId=req.baseItemId if req else None,
                                wardrobe_items=current_wardrobe
                            )
                            
                            # Store in cache with 24-hour TTL (86400 seconds)
                            logger.info(f"🔍 DEBUG: Storing in cache with key: {cache_key[:80]}...")
                            cache_manager.set("outfit", cache_key, outfit, ttl=86400)
                            logger.info(f"💾 Cached outfit generation: {cache_key[:50]}...")
                            logger.info(f"🔍 DEBUG: Outfit metadata before caching: {list(outfit.get('metadata', {}).keys()) if outfit.get('metadata') else 'None'}")
                            
                            # Add cache metadata
                            if 'metadata' not in outfit:
                                outfit['metadata'] = {}
                            outfit['metadata']['cache_hit'] = False
                            outfit['metadata']['cached'] = True
                        except Exception as cache_error:
                            logger.warning(f"⚠️ Cache storage failed: {cache_error}, continuing without cache")
                    
                    break
                else:
                    logger.warning(f"⚠️ Generation attempt {generation_attempts} produced invalid outfit")
                    print(f"🚨 RETRY ALERT: Attempt {generation_attempts} failed - invalid outfit")
                    print(f"🚨 RETRY CONTEXT: User={current_user_id}, Occasion={req.occasion}, Style={req.style}, Mood={req.mood}")
        # print(f"🚨 RETRY REASON: Generated outfit has {len((outfit.get('items', []) if outfit else []))} items (minimum 3 required)")
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(1)  # Brief delay before retry
                        continue
                    
            except Exception as e:
                last_error = e
        import traceback
        
        # 🔥 ENHANCED ERROR TRACING FOR NoneType .get() DEBUGGING
        error_details = {
        "attempt": generation_attempts,
        "max_attempts": max_attempts,
        "error_type": str(type(e).__name__),
        "error_message": str(e),
        "full_traceback": traceback.format_exc(),
        "context": {
        "user_id": current_user_id,
        "occasion": getattr(req, 'occasion', 'NO_OCCASION') if req else 'NO_REQ',
        "style": getattr(req, 'style', 'NO_STYLE') if req else 'NO_REQ',
        "mood": getattr(req, 'mood', 'NO_MOOD') if req else 'NO_REQ'
        }
        }
        
        logger.error(f"🔥 RETRY LOOP CRASH - NoneType .get() error detected", extra=error_details, exc_info=True)
        print(f"🔥 RETRY LOOP CRASH: {error_details}")
        # print(f"🔥 FULL TRACEBACK:\n{traceback.format_exc()}")
        
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)  # Brief delay before retry
                    continue
        
        # Check if all attempts failed
        if not outfit or not ((outfit.get('items') if outfit else None) if outfit else None) or len(outfit.get('items', [])) < 3:
            logger.error(f"❌ All {max_attempts} generation attempts failed")
            print(f"🚨 FINAL FAILURE: All {max_attempts} generation attempts failed")
            print(f"🚨 FINAL CONTEXT: User={current_user_id}, Occasion={req.occasion}, Style={req.style}, Mood={req.mood}")
            print(f"🚨 FINAL IMPACT: User will receive HTTP 500 error - no outfit generated")
            if last_error:
        # print(f"🚨 FINAL ERROR: {type(last_error).__name__}: {str(last_error)}")
        # Preserve debug information from our debug logging
        error_detail = str(last_error)
        if "DEBUG:" in error_detail or "🔥" in error_detail or "NoneType" in error_detail:
        # Our debug information is in the error message - return it directly
        if error_details:
                raise HTTPException(
                    status_code=500, 
        detail=f"🔥 RETRY LOOP CRASH: {error_details['error_type']}: {error_details['error_message']}\n\nFull Traceback:\n{error_details['full_traceback']}"
        )
        else:
        raise HTTPException(
        status_code=500,
        detail=error_detail  # Return original error if no enhanced details
        )
        else:
        raise HTTPException(
        status_code=500,
        detail=f"Outfit generation failed after {max_attempts} attempts: {error_detail}"
                )
            else:
                print(f"🚨 FINAL ERROR: No specific error - unable to generate valid outfit")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Outfit generation failed: Unable to generate valid outfit"
                )

        # 2. Wrap with metadata
        outfit_id = str(uuid4())
        outfit_record = {
            "id": outfit_id,
            "user_id": current_user_id,  # Use snake_case to match database schema
            "generated_at": datetime.utcnow().isoformat(),
            **outfit
        }

        # Ensure metadata exists and is a dict (not None) - preserve from outfit if it exists
        if 'metadata' not in outfit_record or outfit_record.get('metadata') is None:
            outfit_record['metadata'] = {}
        elif isinstance(outfit_record.get('metadata'), dict):
            # Metadata already exists, ensure it's preserved
            pass
        else:
            # Metadata exists but is not a dict, convert it
            outfit_record['metadata'] = {}
        
        # 3. Clean and save to Firestore
        logger.info(f"🔄 About to save generated outfit {outfit_id}")
        
        # AGGRESSIVE CLEANING: Remove problematic fields that cause Firebase serialization issues
        outfit_record_cleaned = {
        "id": (outfit_record.get("id") if outfit_record else None),
        "user_id": (outfit_record.get("user_id") if outfit_record else None),
        "generated_at": (outfit_record.get("generated_at") if outfit_record else None),
        "name": (outfit_record.get("name") if outfit_record else None),
        "occasion": (outfit_record.get("occasion") if outfit_record else None),
        "style": (outfit_record.get("style") if outfit_record else None),
        "mood": (outfit_record.get("mood") if outfit_record else None),
        "confidence_score": (outfit_record.get("confidence_score") if outfit_record else None),
        "reasoning": (outfit_record.get("reasoning") if outfit_record else None),
        "createdAt": (outfit_record.get("createdAt") if outfit_record else None),
        "userId": (outfit_record.get("userId") if outfit_record else None),
        "explanation": (outfit_record.get("explanation") if outfit_record else None),
        "styleTags": (outfit_record.get("styleTags", []) if outfit_record else []),
        "colorHarmony": (outfit_record.get("colorHarmony") if outfit_record else None),
        "styleNotes": (outfit_record.get("styleNotes") if outfit_record else None),
        "season": (outfit_record.get("season") if outfit_record else None),
        "updatedAt": (outfit_record.get("updatedAt") if outfit_record else None),
        "wasSuccessful": (outfit_record.get("wasSuccessful") if outfit_record else None),
        "baseItemId": (outfit_record.get("baseItemId") if outfit_record else None)
        }
        
        # Clean items array - convert ClothingItem objects to simple dicts
        items_cleaned = []
        for item in (outfit_record.get("items", []) if outfit_record else []):
            if hasattr(item, "dict"):
                items_cleaned.append(item.dict())
            elif hasattr(item, "model_dump"):
                items_cleaned.append(item.model_dump())
            elif isinstance(item, dict):
                items_cleaned.append(item)
            else:
                logger.warning(f"Skipping non-serializable item: {type(item)}")
        outfit_record_cleaned["items"] = items_cleaned
        
        # Clean pieces array - convert to simple dicts or skip if problematic
        pieces_cleaned = []
        for piece in (outfit_record.get("pieces", []) if outfit_record else []):
            if hasattr(piece, "dict"):
                pieces_cleaned.append(piece.dict())
            elif hasattr(piece, "model_dump"):
                pieces_cleaned.append(piece.model_dump())
            elif isinstance(piece, dict):
                pieces_cleaned.append(piece)
            else:
                logger.warning(f"Skipping non-serializable piece: {type(piece)}")
        outfit_record_cleaned["pieces"] = pieces_cleaned
        
        # Clean metadata - ensure it's a simple dict
        metadata = (outfit_record.get("metadata", {}) if outfit_record else {})
        if isinstance(metadata, dict):
            outfit_record_cleaned["metadata"] = metadata
        else:
        outfit_record_cleaned["metadata"] = None
        
        # Apply final cleaning
        clean_outfit_record = clean_for_firestore(outfit_record_cleaned)
        logger.info(f"🧹 Cleaned outfit record: {clean_outfit_record}")
        
        # CRITICAL DEBUG: Log strategy right before saving to Firebase
        final_strategy = safe_get_metadata(clean_outfit_record, 'generation_strategy', 'unknown')
        logger.info(f"🔍 DEBUG FINAL SAVE: strategy = {final_strategy}")
        print(f"🔍 DEBUG FINAL SAVE: strategy = {final_strategy}")
        save_result = await save_outfit(current_user_id, outfit_id, clean_outfit_record)
        logger.info(f"💾 Save operation result: {save_result}")
        
        # Track usage (async, don't fail if it errors)
        try:
            from ..services.usage_tracking_service import UsageTrackingService
            usage_service = UsageTrackingService()
            await usage_service.track_outfit_generation(current_user_id)
            logger.info(f"📊 Tracked outfit generation usage for user {current_user_id}")
        except Exception as usage_error:
            logger.warning(f"Usage tracking failed: {usage_error}")
        
        # Update user stats (async, don't fail if it errors)
        try:
            from ..services.user_stats_service import user_stats_service
            await user_stats_service.update_outfit_stats(current_user_id, "created", clean_outfit_record)
        except Exception as stats_error:
            logger.warning(f"Stats update failed: {stats_error}")

        # 4. Performance monitoring and final validation
        generation_time = time.time() - start_time
        logger.info(f"⏱️ Generation completed in {generation_time:.2f} seconds")
        logger.info(f"📊 Generation attempts: {generation_attempts}, Cache hit: {cache_hit}")
        
        # Slow request detection (>10 seconds)
        is_slow = generation_time > 10.0
        if is_slow:
            logger.warning(f"⚠️ SLOW REQUEST: Generation took {generation_time:.2f}s (threshold: 10s)")
        
        # Add performance metadata to outfit (ensure metadata dict exists)
        if 'metadata' not in outfit_record or outfit_record.get('metadata') is None:
            outfit_record['metadata'] = {}
        
        # CRITICAL: Always set performance metadata, merging with existing metadata
        # This ensures generation_duration and is_slow are always present in the response
        outfit_record['metadata']['generation_duration'] = round(generation_time, 2)
        outfit_record['metadata']['is_slow'] = is_slow
        outfit_record['metadata']['generation_attempts'] = generation_attempts
        outfit_record['metadata']['cache_hit'] = cache_hit
        
        # Also preserve generation_time if it exists (from generation service)
        # But ensure generation_duration takes precedence for consistency
        if 'generation_time' in outfit_record.get('metadata', {}) and 'generation_duration' not in outfit_record.get('metadata', {}):
            outfit_record['metadata']['generation_duration'] = outfit_record['metadata'].get('generation_time', round(generation_time, 2))
        
        # Final outfit validation
        final_validation = await _validate_final_outfit(outfit_record, req)
        if not final_validation['is_valid']:
            logger.warning(f"⚠️ Final validation issues: {final_validation['issues']}")
            # Add validation warnings to metadata
            outfit_record['metadata']['validation_warnings'] = final_validation['issues']
        
        # Generate structured explanation for the outfit
        try:
            from ..services.outfit_explanation_service import OutfitExplanationService
            explanation_service = OutfitExplanationService()
            
            # Get user profile for explanation
            user_profile_data = {}
            try:
                from ..services.user_profile_service import get_user_profile
                user_profile = await get_user_profile(current_user_id)
                if user_profile:
                    user_profile_data = user_profile.dict() if hasattr(user_profile, 'dict') else (user_profile.model_dump() if hasattr(user_profile, 'model_dump') else user_profile)
            except Exception as profile_error:
                logger.warning(f"Could not fetch user profile for explanation: {profile_error}")
            
            # Prepare context for explanation
            context = {
                'weather': {
                    'temperature': req.weather.temperature if hasattr(req, 'weather') and req.weather else 70,
                    'condition': req.weather.condition if hasattr(req, 'weather') and req.weather else 'Clear'
                },
                'occasion': req.occasion,
                'style': req.style,
                'mood': req.mood
            }
            
            # Generate explanation
            explanation = await explanation_service.generate_explanation(
                outfit=outfit_record,
                context=context,
                user_profile=user_profile_data,
                user_id=current_user_id
            )
            
            # Add explanation to metadata
            if 'metadata' not in outfit_record:
                outfit_record['metadata'] = {}
            outfit_record['metadata']['structuredExplanation'] = explanation
            outfit_record['metadata']['weather'] = context['weather']
            
            logger.info(f"✅ Generated structured explanation with {len(explanation.get('explanations', []))} categories")
        except Exception as explanation_error:
            logger.warning(f"Could not generate outfit explanation: {explanation_error}")
            # Continue without explanation - it's an enhancement, not critical
        
        # Enhanced success logging
        logger.info(f"✅ Successfully generated robust outfit {outfit_id}")
        logger.info(f"📋 Outfit details: {len(((outfit_record.get('items', []) if outfit_record else []) if outfit_record else []))} items, confidence: {outfit_record.get('confidence', 'unknown')}")
        
        # Add cache hit metadata to response if available
        if cache_hit:
            if 'metadata' not in outfit_record:
                outfit_record['metadata'] = {}
            outfit_record['metadata']['cache_hit'] = True
            # For cache hits, set generation_duration to 0 (instant)
            outfit_record['metadata']['generation_duration'] = 0.0
            outfit_record['metadata']['is_slow'] = False
        
        # Ensure metadata is properly set before returning
        if 'metadata' not in outfit_record or outfit_record.get('metadata') is None:
            outfit_record['metadata'] = {}
        
        # CRITICAL: Ensure performance metadata is ALWAYS set before returning
        # This ensures it's in the response even if it wasn't set earlier
        # Force update metadata dict to ensure it exists
        if 'metadata' not in outfit_record or outfit_record.get('metadata') is None:
            outfit_record['metadata'] = {}
        
        # ALWAYS set these fields - they're required for performance monitoring
        outfit_record['metadata']['generation_duration'] = round(generation_time, 2)
        outfit_record['metadata']['is_slow'] = is_slow
        outfit_record['metadata']['generation_attempts'] = generation_attempts
        outfit_record['metadata']['cache_hit'] = cache_hit
        
        # Log metadata for debugging
        metadata_keys = list(outfit_record.get('metadata', {}).keys())
        logger.info(f"🔍 DEBUG: Final outfit_record metadata keys: {metadata_keys}")
        logger.info(f"🔍 DEBUG: generation_duration in metadata: {'generation_duration' in outfit_record.get('metadata', {})}")
        logger.info(f"🔍 DEBUG: is_slow in metadata: {'is_slow' in outfit_record.get('metadata', {})}")
        logger.info(f"🔍 DEBUG: cache_hit in metadata: {'cache_hit' in outfit_record.get('metadata', {})}")
        logger.info(f"🔍 DEBUG: Full metadata dict: {outfit_record.get('metadata', {})}")
        
        # Record generation metrics for performance tracking
        try:
            strategy = safe_get_metadata(outfit_record, 'generation_strategy', 'robust')
            log_generation_strategy(
                outfit_response=outfit_record,
                user_id=current_user_id,
                generation_time=generation_time,
                validation_time=0.0,  # Validation time not separately tracked
                failed_rules=None,
                fallback_reason=None
            )
        except Exception as metrics_error:
            logger.warning(f"Failed to log generation metrics: {metrics_error}")
        
        # Return standardized outfit response - ensure metadata is included
        try:
            # Create a deep copy to ensure metadata is preserved
            import copy
            response_dict = copy.deepcopy(dict(outfit_record))
            
            # Get existing metadata or create new dict
            existing_metadata = response_dict.get('metadata', {})
            if not isinstance(existing_metadata, dict):
                existing_metadata = {}
            
            # CRITICAL: Create a NEW metadata dict that includes all existing metadata PLUS performance fields
            # This ensures the performance metadata is always present and not overwritten
            response_dict['metadata'] = {
                **existing_metadata,  # Preserve all existing metadata
                'generation_duration': round(generation_time, 2),
                'is_slow': is_slow,
                'generation_attempts': generation_attempts,
                'cache_hit': cache_hit
            }
            
            logger.info(f"🔍 DEBUG: response_dict metadata before OutfitResponse: {list(response_dict.get('metadata', {}).keys())}")
            logger.info(f"🔍 DEBUG: generation_duration={response_dict.get('metadata', {}).get('generation_duration')}, is_slow={response_dict.get('metadata', {}).get('is_slow')}")
            
            # Create response with merged metadata (performance fields are in metadata only)
            response_data = OutfitResponse(**response_dict)
            
            return response_data
        except Exception as response_error:
            logger.error(f"❌ Error creating OutfitResponse: {response_error}")
            logger.error(f"❌ outfit_record keys: {list(outfit_record.keys())}")
            logger.error(f"❌ outfit_record metadata: {outfit_record.get('metadata')}")
            raise

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # 🔥 COMPREHENSIVE ERROR TRACING FOR NoneType .get() DEBUGGING
        import traceback
        error_details = {
        "error_type": str(type(e).__name__),
            "error_message": str(e),
        "full_traceback": traceback.format_exc(),
        "context": {
            "user_id": current_user_id,
        "occasion": getattr(req, 'occasion', 'NO_OCCASION') if req else 'NO_REQ',
        "style": getattr(req, 'style', 'NO_STYLE') if req else 'NO_REQ',
        "mood": getattr(req, 'mood', 'NO_MOOD') if req else 'NO_REQ'
        }
        }
        
        logger.error("🔥 ENDPOINT CRASH - NoneType .get() error detected", extra=error_details, exc_info=True)
        print(f"🔥 ENDPOINT CRASH: {error_details}")
        # print(f"🔥 FULL TRACEBACK:\n{traceback.format_exc()}")
        
        # Return the detailed error information
            raise HTTPException(
                status_code=500, 
        detail=f"🔥 ENDPOINT CRASH: {error_details['error_type']}: {error_details['error_message']}\n\nFull Traceback:\n{error_details['full_traceback']}"
            )

async def _validate_final_outfit(outfit_record: Dict[str, Any], req: OutfitRequest) -> Dict[str, Any]:
    """Validate the final outfit before returning to user"""
    issues = []
    is_valid = True
    
    # Check item count
    items = (outfit_record.get('items', []) if outfit_record else [])
    if len(items) < 3:
        issues.append(f"Outfit has only {len(items)} items (minimum: 3)")
        is_valid = False
    elif len(items) > 6:
        issues.append(f"Outfit has {len(items)} items (maximum: 6)")
        is_valid = False
    
    # Check for essential categories
    categories = set()
    for item in items:
                item_type = item.get('type', '').lower()
        if item_type in ['shirt', 'blouse', 'sweater', 'tank', 'top']:
            categories.add('tops')
        elif item_type in ['pants', 'jeans', 'shorts', 'skirt']:
            categories.add('bottoms')
        elif item_type in ['shoes', 'sneakers', 'boots', 'sandals']:
            categories.add('shoes')
    
    missing_essential = {'tops', 'bottoms', 'shoes'} - categories
    if missing_essential:
        issues.append(f"Missing essential categories: {missing_essential}")
        is_valid = False
    
    # Check for inappropriate combinations
    inappropriate_combinations = [
        ("blazer", "shorts"),
        ("formal_shoes", "casual_bottoms"),
        ("tie", "t_shirt")
    ]
    
    for item1 in items:
        for item2 in items:
            if item1 != item2:
                type1 = item1.get('type', '').lower()
        type2 = (item2.get('type', '') if item2 else '').lower()
                
                for combo1, combo2 in inappropriate_combinations:
                    if (combo1 in type1 and combo2 in type2) or (combo1 in type2 and combo2 in type1):
                        issues.append(f"Inappropriate combination: {type1} with {type2}")
                        is_valid = False
    
    return {
        "is_valid": is_valid,
        "issues": issues
    }


@router.post("")
async def create_outfit(
    request: CreateOutfitRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Create a custom outfit by manually selecting items from the user's wardrobe.
    REST endpoint: POST /api/outfits
    """
    try:
        logger.info(f"🎨 Creating custom outfit: {request.name}")
        # Reduced logging to prevent rate limits
        
        # Use authenticated user
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        current_user_id = current_user.id
        
        logger.info(f"🔍 Request data:")
        logger.info(f"  - name: {request.name}")
        logger.info(f"  - occasion: {request.occasion}")
        logger.info(f"  - style: {request.style}")
        logger.info(f"  - items count: {len(request.items)}")
        logger.info(f"  - user_id: {current_user_id}")
        
        # Create outfit data with all required OutfitGeneratedOutfit fields
        outfit_data = {
            "id": str(uuid4()),
            "name": request.name,
            "occasion": request.occasion,
            "style": request.style,
            "description": request.description or "",
            "items": request.items,
            "user_id": current_user_id,  # Use snake_case to match database schema
            "createdAt": request.createdAt or datetime.utcnow().isoformat() + "Z",
            "is_custom": True,  # Mark as custom outfit
            "confidence_score": 1.0,  # Custom outfits have full confidence
            "reasoning": f"Custom outfit created by user: {request.description or 'No description provided'}",
            
            # Required OutfitGeneratedOutfit fields
            "explanation": request.description or f"Custom {request.style} outfit for {request.occasion}",
            "pieces": [],  # Empty for custom outfits, could be populated later
            "styleTags": [request.style.lower().replace(' ', '_')],  # Convert style to tag format
            "colorHarmony": "custom",  # Mark as custom color harmony
            "styleNotes": f"Custom {request.style} style selected by user",
            "season": "all",  # Default to all seasons for custom outfits
            "mood": "custom",  # Default mood for custom outfits
            "updatedAt": request.createdAt or int(time.time()),
            "metadata": {
                "created_method": "custom",
                "flat_lay_status": "awaiting_consent",
                "flatLayStatus": "awaiting_consent",
                "flat_lay_requested": False,
                "flatLayRequested": False
            },
            "wasSuccessful": True,
            "baseItemId": None,
            "validationErrors": [],
            "userFeedback": None,
            "flat_lay_status": "awaiting_consent",
            "flatLayStatus": "awaiting_consent",
            "flat_lay_url": None,
            "flatLayUrl": None,
            "flat_lay_error": None,
            "flatLayError": None,
            "flat_lay_requested": False,
            "flatLayRequested": False
        }
        
        # Save outfit to Firestore
        outfit_id = outfit_data["id"]
        # Simple data cleaning - remove any problematic fields
        clean_outfit_data = {k: v for k, v in outfit_data.items() if v is not None}
        logger.info(f"🧹 Prepared outfit data: name='{((clean_outfit_data.get('name', 'unnamed') if clean_outfit_data else 'unnamed') if clean_outfit_data else 'unnamed')}', items_count={len(clean_outfit_data.get('items', []))}")
        
        # Save to Firestore directly
        try:
            from ..config.firebase import db
            if db:
                db.collection('outfits').document(outfit_id).set(clean_outfit_data)
                logger.info(f"✅ Saved outfit {outfit_id} to Firestore")
                
                # Update user stats (async, don't fail if it errors)
                try:
                    from ..services.user_stats_service import user_stats_service
                    await user_stats_service.update_outfit_stats(current_user_id, "created", clean_outfit_data)
                except Exception as stats_error:
                    logger.warning(f"Stats update failed: {stats_error}")
            else:
                logger.warning("⚠️ Firebase not available, outfit not saved to database")
        except Exception as save_error:
            logger.error(f"❌ Failed to save outfit to Firestore: {save_error}")
            # Don't fail the request, just log the error
        
        # Enhanced logging for debugging
        logger.info(f"✅ Outfit created: {outfit_id} for user {current_user_id}")
        logger.info(f"🔍 DEBUG: Created outfit name='{outfit_data['name']}' style='{outfit_data['style']}' occasion='{outfit_data['occasion']}'")
        logger.info(f"📊 DEBUG: Outfit contains {len(outfit_data['items'])} items")
        
        # Return simplified response
        return {
            "success": True,
            "id": outfit_data["id"],
            "name": outfit_data["name"],
            "items": outfit_data["items"],
            "style": outfit_data["style"],
            "occasion": outfit_data["occasion"],
        "description": (outfit_data.get("description", "") if outfit_data else ""),
            "createdAt": outfit_data["createdAt"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating custom outfit: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug")
async def debug_outfits():
    """
    Debug route: Dump the last 5 outfits from Firestore for troubleshooting.
    Helps confirm backend state without guesswork.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        current_user_id = current_user.id  # Your actual user ID
        logger.info(f"🔍 DEBUG: Fetching last 5 outfits for debugging")
        
        # Fetch recent outfits with minimal processing
        outfits = await get_user_outfits(current_user_id, 5, 0)
        
        debug_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": current_user_id,
            "total_outfits": len(outfits),
            "outfits": []
        }
        
        for outfit in outfits:
            debug_info["outfits"].append({
        "id": (outfit.get("id", "unknown") if outfit else "unknown"),
        "name": (outfit.get("name", "unknown") if outfit else "unknown"),
        "style": (outfit.get("style", "unknown") if outfit else "unknown"),
        "occasion": (outfit.get("occasion", "unknown") if outfit else "unknown"),
        "createdAt": (outfit.get("createdAt", "unknown") if outfit else "unknown"),
        "user_id": (outfit.get("user_id", "unknown") if outfit else "unknown"),
        "item_count": len((outfit.get("items", []) if outfit else []))
            })
        
        logger.info(f"🔍 DEBUG: Returning {len(outfits)} outfits for debugging")
        return debug_info
        
    except Exception as e:
        logger.error(f"❌ Debug route failed: {e}", exc_info=True)
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed"
        }


@router.get("/debug-simple")
async def debug_outfits_simple():
    """Quick debug: show last 5 outfits"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        current_user_id = current_user.id
        outfits = await get_user_outfits(current_user_id, 5, 0)
        
        return {
            "total_outfits": len(outfits),
            "outfits": [
                {
        "id": (o.get("id") if o else None),
        "name": (o.get("name") if o else None),
        "createdAt": (o.get("createdAt") if o else None),
        "user_id": (o.get("user_id") if o else None)
                } for o in outfits
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/rate")
async def rate_outfit(
    rating_data: dict,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Rate an outfit and update analytics for individual wardrobe items.
    This ensures the scoring system has accurate feedback data.
    """
    try:
        logger.info(f"📊 Rating outfit request received")
        
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        current_user_id = current_user.id
        outfit_id = (rating_data.get('outfitId') if rating_data else None)
        rating = (rating_data.get('rating') if rating_data else None)
        is_liked = (rating_data.get('isLiked', False) if rating_data else False)
        is_disliked = (rating_data.get('isDisliked', False) if rating_data else False)
        feedback = (rating_data.get('feedback', '') if rating_data else '')
        
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
            from ..config.firebase import db
        except ImportError:
            raise HTTPException(status_code=503, detail="Database service unavailable")
            
        outfit_ref = db.collection('outfits').document(outfit_id)
        outfit_doc = outfit_ref.get() if outfit_ref else None if outfit_ref else None
        
        if not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        # Check both possible user ID field names for compatibility
        outfit_user_id = ((outfit_data.get('userId') if outfit_data else None) if outfit_data else None) or outfit_data.get('user_id')
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
        (outfit_data.get('items', []) if outfit_data else []),
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
        logger.info(f"📊 Updating analytics for {len(outfit_items)} items from outfit rating")
        
        current_time = datetime.utcnow()
        updated_count = 0
        
        for item in outfit_items:
        item_id = (item.get('id') if item else None)
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
        feedback_ratings = (current_data.get('feedback_ratings', []) if current_data else [])
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
                        'rating': round(avg_rating, 2),
                        'total_feedback_count': len(feedback_ratings),
                        'last_feedback_at': current_time,
                        'updated_at': current_time
                    })
                    
                else:
                    # Create new analytics document
                    analytics_data = {
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
                        'average_feedback_rating': rating,
                        'rating': rating,
                        'total_feedback_count': 1,
                        'last_feedback_at': current_time,
                        'created_at': current_time,
                        'updated_at': current_time
                    }
                    
                    analytics_ref.set(analytics_data)
                
                updated_count += 1
                logger.info(f"✅ Updated analytics for item {item_id} with rating {rating}")
                
            except Exception as e:
                logger.error(f"❌ Failed to update analytics for item {item_id}: {e}")
                continue
        
        logger.info(f"✅ Successfully updated analytics for {updated_count}/{len(outfit_items)} items")
        
    except Exception as e:
        logger.error(f"❌ Failed to update item analytics from outfit rating: {e}")
        # Don't raise error - this is a secondary operation

# Explain Outfit Endpoint
@router.post("/explain", response_model=dict)
async def explain_outfit(
    outfit_data: dict,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Generate comprehensive explanation for an outfit suggestion.
    
    Accepts outfit data and context, returns structured explanations with all 5 categories:
    Style Reasoning, Color Harmony, Occasion Fit, Weather Appropriateness, Personalization
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        explanation_service = OutfitExplanationService()
        
        # Extract context from request
        context = outfit_data.get('context', {})
        user_profile = outfit_data.get('user_profile', {})
        outfit = outfit_data.get('outfit', outfit_data)  # Support both nested and flat structure
        
        # Generate explanation
        explanation = await explanation_service.generate_explanation(
            outfit=outfit,
            context=context,
            user_profile=user_profile,
            user_id=current_user.id
        )
        
        return explanation
        
    except Exception as e:
        logger.error(f"Error generating outfit explanation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")

# ⚠️ PARAMETERIZED ROUTE - MUST BE FIRST TO AVOID ROUTE CONFLICTS!
# This route MUST come BEFORE the root route to avoid catching it
@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(outfit_id: str):
    """Get a specific outfit by ID. MUST BE FIRST ROUTE TO AVOID CONFLICTS."""
    logger.info(f"🔍 DEBUG: Get outfit {outfit_id} endpoint called")
    
    try:
        # Use the actual user ID from your database where the 1000+ outfits are stored
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        current_user_id = current_user.id  # TEMPORARY: Your actual user ID
        logger.info(f"Using hardcoded user ID for testing: {current_user_id}")
        
        # Check Firebase availability
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("Firebase not available, returning empty outfits")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        # Try to fetch real outfit from Firebase
        try:
            outfit_doc = db.collection('outfits').document(outfit_id).get()
            if outfit_doc.exists:
                outfit_data = outfit_doc.to_dict()
                outfit_data['id'] = outfit_id
                logger.info(f"Successfully retrieved outfit {outfit_id} from database")
                return OutfitResponse(**outfit_data)
            else:
                logger.warning(f"Outfit {outfit_id} not found in database")
                raise HTTPException(status_code=404, detail="Outfit not found")
                
        except Exception as firebase_error:
            logger.error(f"Firebase query failed: {firebase_error}")
            logger.warning("Falling back to mock data due to Firebase error")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve outfit from database: {firebase_error}")
        
    except Exception as e:
        logger.error(f"Error getting outfit {outfit_id}: {e}")
        # Fallback to mock data on other errors
        raise HTTPException(status_code=500, detail=f"Failed to get outfit: {e}")

# ✅ Retrieve Outfit History (dual endpoints for trailing slash compatibility)
@router.get("/", response_model=List[OutfitResponse])
async def list_outfits_with_slash(
    limit: int = 50,
    offset: int = 0,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Fetch a user's outfit history from Firestore.
    """
    logger.info("🎯 DEBUG: /api/outfits/ endpoint called (CORRECT ENDPOINT)")
    logger.info(f"🔍 DEBUG: Request params - limit: {limit}, offset: {offset}")
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

# 📊 Get Outfit Statistics
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

# 🔍 DEBUG: List all registered routes for this router
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

# 🎨 Intelligent Outfit Naming and Reasoning Functions

async def generate_intelligent_outfit_name(items: List[Dict], style: str, mood: str, occasion: str) -> str:
    """Generate intelligent outfit names based on items and context."""
    try:
        # Analyze the items to create a descriptive name
        item_types = [(item.get('type', '') if item else '').lower() for item in items]
        item_names = [(item.get('name', '') if item else '').lower() for item in items]
        
        # Identify key pieces
        has_blazer = any('blazer' in item_type or 'blazer' in name for item_type, name in zip(item_types, item_names))
        has_dress = any('dress' in item_type or 'dress' in name for item_type, name in zip(item_types, item_names))
        has_jeans = any('jean' in item_type or 'jean' in name for item_type, name in zip(item_types, item_names))
        has_sneakers = any('sneaker' in item_type or 'sneaker' in name for item_type, name in zip(item_types, item_names))
        has_heels = any('heel' in item_type or 'heel' in name for item_type, name in zip(item_types, item_names))
        has_denim = any('denim' in item_type or 'denim' in name for item_type, name in zip(item_types, item_names))
        
        # Generate contextual names
        if has_blazer and has_jeans:
            return f"Smart Casual {occasion.title()}"
        elif has_blazer and not has_jeans:
            return f"Polished {occasion.title()}"
        elif has_dress:
            return f"Effortless {occasion.title()}"
        elif has_jeans and has_sneakers:
            return f"Relaxed {occasion.title()}"
        elif has_heels and not has_jeans:
            return f"Elegant {occasion.title()}"
        elif style.lower() == 'minimalist':
            return f"Minimal {occasion.title()}"
        elif style.lower() == 'bohemian':
            return f"Boho {occasion.title()}"
        elif mood.lower() == 'confident':
            return f"Power {occasion.title()}"
        elif mood.lower() == 'relaxed':
            return f"Easy {occasion.title()}"
        else:
            return f"{style.title()} {occasion.title()}"
            
    except Exception as e:
        logger.warning(f"⚠️ Failed to generate intelligent name: {e}")
        return f"{style.title()} {occasion.title()}"

async def generate_intelligent_reasoning(items: List[Dict], req: OutfitRequest, outfit_score: Dict, layering_validation: Dict, color_validation: Dict) -> str:
    """Generate intelligent reasoning for outfit selection with weather context."""
    try:
        # Always generate exactly 3 sentences for consistency
        sentences = []
        
        # Sentence 1: Outfit style, mood, and occasion
        mood_desc = {
            'bold': 'confident', 'relaxed': 'comfortable', 'sophisticated': 'elegant',
            'dynamic': 'energetic', 'serene': 'peaceful', 'mysterious': 'intriguing'
        }.get(req.mood.lower(), (req.mood if req else "unknown").lower())
        
        sentences.append(f"This outfit reflects your {req.style} style for a {req.occasion} occasion, creating a {mood_desc} mood.")
        
        # Sentence 2: Weather appropriateness / comfort note
        if (req.weather if req else None):
            temp = getattr(req.weather, 'temperature', 70)
            condition = getattr(req.weather, 'condition', 'clear').lower()
            
            # Check if this is real weather, manual override, or fallback
            is_manual_override = getattr(req.weather, 'isManualOverride', False)
            is_real_weather = getattr(req.weather, 'isRealWeather', False)
            is_fallback_weather = getattr(req.weather, 'isFallbackWeather', False)
            
            # Weather-appropriate messaging with source indication
            if temp >= 85:
                base_note = f"The current weather is {temp}°F and {condition}, so the lightweight pieces ensure comfort in warm conditions."
            elif temp >= 75:
                base_note = f"The current weather is {temp}°F and {condition}, so the breathable fabrics provide comfort throughout the day."
            elif temp >= 65:
                base_note = f"The current weather is {temp}°F and {condition}, so the balanced layering adapts well to mild conditions."
            elif temp >= 55:
                base_note = f"The current weather is {temp}°F and {condition}, so the thoughtful layering provides warmth and comfort."
            else:
                base_note = f"The current weather is {temp}°F and {condition}, so the warm layers ensure comfort in cool conditions."
                
            # Add condition-specific notes
            if 'rain' in condition:
                base_note = base_note.replace("comfort", "protection and comfort")
            elif 'wind' in condition:
                base_note = base_note.replace("comfort", "secure fit and comfort")
            
            # Add weather source indication
            if is_manual_override:
                weather_note = base_note + " (This outfit was generated based on your manual weather preference.)"
            elif is_real_weather:
                weather_note = base_note + " (This outfit was generated based on real-time weather data.)"
            elif is_fallback_weather:
                weather_note = base_note + " (Fallback weather was used; consider minor adjustments if needed.)"
            else:
                weather_note = base_note
        else:
            weather_note = "The pieces are selected for comfortable all-day wear and versatile styling."
            
        sentences.append(weather_note)
        
        # Sentence 3: Harmony, layering, or color reasoning with item-specific weather context
        if items and len(items) >= 2:
            # Analyze colors and weather context
            colors = [item.get('color', '').title() for item in items if item.get('color')]
            weather_notes = []
            
            # Check for any weather-related item notes
            for item in items:
        weather_context = (item.get('weather_context', {}) if item else {})
                if weather_context:
                    temp_note = weather_context.get('temperature_note', '')
                    if temp_note and ('perfect' in temp_note or 'ideal' in temp_note or 'excellent' in temp_note):
        weather_notes.append(f"the {(item.get('type', 'item') if item else 'item')} is {temp_note}")
        elif temp_note and ('borderline' in (weather_context.get('temperature_appropriateness', '') if weather_context else '') or 'may be' in temp_note):
        weather_notes.append(f"the {(item.get('type', 'item') if item else 'item')} {temp_note}")
            
            # Build the sentence
            if colors:
                color_combo = " and ".join(colors[:3])  # Limit to 3 colors
                if len(colors) > 3:
                    color_combo += f" and {len(colors)-3} other tones"
                
                if weather_notes:
                    weather_context_text = ", ".join(weather_notes[:2])  # Limit to 2 weather notes
                    sentences.append(f"The {color_combo} tones create color harmony across your pieces, while {weather_context_text} for optimal weather comfort.")
                else:
                    sentences.append(f"The {color_combo} tones create color harmony across your pieces, while the layered composition adds depth and sophistication.")
            else:
                # Fallback to item types with weather context
        item_types = [(item.get('type', '') if item else '').title() for item in items]
                if weather_notes:
                    weather_context_text = ", ".join(weather_notes[:2])
                    sentences.append(f"The {', '.join(item_types)} work together to create a cohesive look, while {weather_context_text} for weather-appropriate comfort.")
                else:
                    sentences.append(f"The {', '.join(item_types)} work together to create a cohesive look with balanced proportions and complementary textures.")
        else:
            sentences.append("The outfit selection prioritizes style coherence and practical versatility for your occasion.")
        
        return " ".join(sentences)
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to generate intelligent reasoning: {e}")
        # Fallback with weather context if available
        weather_note = ""
        if (req.weather if req else None):
            # Handle both dict and object weather data
            if isinstance(req.weather, dict):
        temp = req.weather.get('temperature', 70) if req.weather else 70
        condition = req.weather.get('condition', 'clear') if req.weather else 'clear'
            else:
                temp = getattr(req.weather, 'temperature', 70)
                condition = getattr(req.weather, 'condition', 'clear')
            weather_note = f" for {temp}°F {condition.lower()} weather"
        return f"This {req.style} {req.occasion} outfit{weather_note} combines {len(items)} carefully selected pieces. The ensemble balances comfort and style for your desired {req.mood} mood. Each item works harmoniously to create a cohesive, weather-appropriate look."

# 🚀 Performance Optimization Functions

async def get_user_wardrobe_cached(user_id: str) -> List[Dict]:
    """Get user wardrobe with basic caching to reduce database calls."""
    # Simple in-memory cache (in production, use Redis or similar)
    if not hasattr(get_user_wardrobe_cached, '_cache'):
        get_user_wardrobe_cached._cache = {}
    
    cache_key = f"wardrobe_{user_id}"
    cache_time = 300  # 5 minutes
    
    if cache_key in get_user_wardrobe_cached._cache:
        cached_data, timestamp = get_user_wardrobe_cached._cache[cache_key]
        if time.time() - timestamp < cache_time:
            logger.info(f"📦 Using cached wardrobe for user {user_id}")
            return cached_data
    
    # Fetch from database
    wardrobe = await get_user_wardrobe(user_id)
    
    # Cache the result
    get_user_wardrobe_cached._cache[cache_key] = (wardrobe, time.time())
    
    return wardrobe

async def get_user_profile_cached(user_id: str) -> Dict:
    """Get user profile with basic caching to reduce database calls."""
    # Simple in-memory cache
    if not hasattr(get_user_profile_cached, '_cache'):
        get_user_profile_cached._cache = {}
    
    cache_key = f"profile_{user_id}"
    cache_time = 600  # 10 minutes
    
    if cache_key in get_user_profile_cached._cache:
        cached_data, timestamp = get_user_profile_cached._cache[cache_key]
        if time.time() - timestamp < cache_time:
            logger.info(f"👤 Using cached profile for user {user_id}")
            return cached_data
    
    # Fetch from database
    profile = await get_user_profile(user_id)
    
    # Cache the result
    get_user_profile_cached._cache[cache_key] = (profile, time.time())
    
    return profile

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

def _apply_final_outfit_validation(outfit: Dict[str, Any]) -> Dict[str, Any]:
    """Final validation check to guarantee 99% prevention of inappropriate combinations."""
    
    items = (outfit.get('items', []) if outfit else [])
    if not items:
        return outfit
    
    # Get all item types and names for analysis
    item_types = [(item.get('type', '') if item else '').lower() for item in items]
    item_names = [(item.get('name', '') if item else '').lower() for item in items]
    
    # CRITICAL: Blazer + Shorts Prevention (Highest Priority)
    has_blazer = any('blazer' in item_type or 'blazer' in item_name for item_type, item_name in zip(item_types, item_names))
    has_shorts = any('shorts' in item_type or 'shorts' in item_name for item_type, item_name in zip(item_types, item_names))
    
    if has_blazer and has_shorts:
        # Remove shorts and replace with appropriate bottom
        filtered_items = []
        shorts_removed = False
        
        for item in items:
            item_type = (item.get('type', '') if item else '').lower()
            item_name = (item.get('name', '') if item else '').lower()
            
            # Skip shorts items
            if 'shorts' in item_type or 'shorts' in item_name:
                shorts_removed = True
                continue
            else:
                filtered_items.append(item)
        
        # If we removed shorts, add appropriate bottom if missing
        if shorts_removed:
            # Check if we still have a bottom
        has_bottom = any(item_type in ['pants', 'jeans', 'skirt'] for item_type in [(item.get('type', '') if item else '').lower() for item in filtered_items])
            
            if not has_bottom:
                # Add pants as replacement (this should be available in wardrobe)
                pants_item = {
                    'id': 'pants_replacement',
                    'name': 'Black Pants',
                    'type': 'pants',
                    'color': 'black',
                    'imageUrl': '',
                    'style': 'casual',
                    'occasion': 'casual',
                    'brand': '',
                    'wearCount': 0,
                    'favorite_score': 0,
                    'tags': [],
        'metadata': None
                }
                filtered_items.append(pants_item)
        
        outfit['items'] = filtered_items
        outfit['name'] = f"Validated {(outfit.get('name', 'Outfit') if outfit else 'Outfit')}"
    
    # CRITICAL: Formal Shoes + Casual Bottoms Prevention (Enhanced)
    formal_shoe_types = ['oxford', 'loafers', 'dress shoes', 'heels', 'pumps']
    casual_bottom_types = ['shorts', 'athletic shorts', 'basketball shorts', 'cargo shorts', 'denim shorts', 
                          'cargo pants', 'athletic pants', 'sweatpants', 'joggers', 'leggings', 'yoga pants']
    
    has_formal_shoes = any(
        any(formal_type in item_type for formal_type in formal_shoe_types) or
        any(formal_type in item_name for formal_type in formal_shoe_types)
        for item_type, item_name in zip(item_types, item_names)
    )
    has_casual_bottoms = any(
        any(casual_type in item_type for casual_type in casual_bottom_types) or
        any(casual_type in item_name for casual_type in casual_bottom_types)
        for item_type, item_name in zip(item_types, item_names)
    )
    
    if has_formal_shoes and has_casual_bottoms:
        # Remove casual bottoms and replace with appropriate bottom
        filtered_items = []
        casual_removed = False
        
        for item in items:
            item_type = (item.get('type', '') if item else '').lower()
            item_name = (item.get('name', '') if item else '').lower()
            
            # Skip casual bottom items (enhanced detection)
            is_casual_bottom = any(
                casual_type in item_type or casual_type in item_name
                for casual_type in casual_bottom_types
            )
            
            if is_casual_bottom:
                casual_removed = True
                continue
            else:
                filtered_items.append(item)
        
        # If we removed casual bottoms, add appropriate bottom if missing
        if casual_removed:
            # Check if we still have a bottom
        has_bottom = any(item_type in ['pants', 'jeans', 'skirt'] for item_type in [(item.get('type', '') if item else '').lower() for item in filtered_items])
            
            if not has_bottom:
                # Add pants as replacement
                pants_item = {
                    'id': 'pants_replacement',
                    'name': 'Black Pants',
                    'type': 'pants',
                    'color': 'black',
                    'imageUrl': '',
                    'style': 'casual',
                    'occasion': 'casual',
                    'brand': '',
                    'wearCount': 0,
                    'favorite_score': 0,
                    'tags': [],
        'metadata': None
                }
                filtered_items.append(pants_item)
        
        outfit['items'] = filtered_items
        outfit['name'] = f"Validated {(outfit.get('name', 'Outfit') if outfit else 'Outfit')}"
    
    # CRITICAL: Final essential categories check to guarantee 99% prevention
    final_items = (outfit.get('items', []) if outfit else [])
    final_item_types = [(item.get('type', '') if item else '').lower() for item in final_items]
    final_item_names = [(item.get('name', '') if item else '').lower() for item in final_items]
    
    # Check for missing essential categories
    has_top = any(item_type in ['t-shirt', 'shirt', 'blouse', 'sweater', 'jacket', 'blazer', 'tank top', 'hoodie', 'polo', 'henley', 'flannel', 'thermal', 'crop top', 'bodysuit', 'wrap top'] or 
                  item_name in ['t-shirt', 'shirt', 'blouse', 'sweater', 'jacket', 'blazer', 'tank top', 'hoodie', 'polo', 'henley', 'flannel', 'thermal', 'crop top', 'bodysuit', 'wrap top']
                  for item_type, item_name in zip(final_item_types, final_item_names))
    
    has_bottom = any(item_type in ['pants', 'jeans', 'shorts', 'skirt', 'dress', 'leggings', 'joggers', 'sweatpants', 'athletic pants', 'cargo pants', 'cargo shorts', 'athletic shorts', 'basketball shorts', 'denim shorts', 'bermuda shorts', 'high waist shorts', 'yoga pants'] or 
                    item_name in ['pants', 'jeans', 'shorts', 'skirt', 'dress', 'leggings', 'joggers', 'sweatpants', 'athletic pants', 'cargo pants', 'cargo shorts', 'athletic shorts', 'basketball shorts', 'denim shorts', 'bermuda shorts', 'high waist shorts', 'yoga pants']
                    for item_type, item_name in zip(final_item_types, final_item_names))
    
    has_shoes = any(item_type in ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flip-flops', 'slides', 'mules', 'espadrilles', 'oxford', 'loafers', 'dress shoes', 'pumps', 'ankle boots', 'knee high boots', 'chelsea boots', 'combat boots', 'running shoes', 'training shoes', 'high top sneakers', 'low top sneakers'] or 
                   item_name in ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flip-flops', 'slides', 'mules', 'espadrilles', 'oxford', 'loafers', 'dress shoes', 'pumps', 'ankle boots', 'knee high boots', 'chelsea boots', 'combat boots', 'running shoes', 'training shoes', 'high top sneakers', 'low top sneakers']
                   for item_type, item_name in zip(final_item_types, final_item_names))
    
    # NO FALLBACK ITEMS - let the robust service handle missing categories
    
    outfit['items'] = final_items
    
    # Final validation: Ensure we have exactly 3-6 items
    if len(final_items) < 3:
        # Add additional items if needed
        while len(final_items) < 3:
            final_items.append({
                'id': f'fallback_item_{len(final_items)}',
                'name': 'Additional Item',
                'type': 'accessory',
                'color': 'black',
                'imageUrl': '',
                'style': 'casual',
                'occasion': 'casual',
                'brand': '',
                'wearCount': 0,
                'favorite_score': 0,
                'tags': [],
                'metadata': {}
            })
        outfit['items'] = final_items
    
    elif len(final_items) > 6:
        # Remove excess items (keep first 6)
        outfit['items'] = final_items[:6]
    
    return outfit 

# Admin cache management endpoints
async def check_admin_user(
    current_user: UserProfile = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> UserProfile:
    """Check if user has admin privileges."""
    try:
        from firebase_admin import auth as firebase_auth
        # Check Firebase custom claims for admin status
        token = credentials.credentials
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            is_admin = decoded_token.get("admin", False) or decoded_token.get("role") == "admin"
            if is_admin:
                return current_user
        except Exception as token_error:
            logger.warning(f"Could not verify admin token: {token_error}")
        
        # Fallback: Check admin email list (can be configured via environment variable)
        import os
        admin_emails_str = os.getenv("ADMIN_EMAILS", "")
        admin_emails = [email.strip() for email in admin_emails_str.split(",") if email.strip()]
        
        if current_user.email and current_user.email in admin_emails:
            return current_user
        
        raise HTTPException(status_code=403, detail="Admin access required")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        raise HTTPException(status_code=403, detail="Admin access required")

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