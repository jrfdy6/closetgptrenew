"""
Outfit management endpoints (GET operations only).
Outfit generation is handled by /api/outfit/generate.
"""

import concurrent.futures
import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
import os

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from ..core.logging import get_logger
from ..config.firebase import db, firebase_initialized
from ..models.analytics_event import AnalyticsEvent
from ..services.analytics_service import log_analytics_event
from ..routes.auth import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["outfits"])
security = HTTPBearer()

# Track authentication failures to implement smart bypass
_auth_failure_count = 0
_last_auth_failure_time = None

async def resolve_item_ids_to_objects(items: List[Any], user_id: str) -> List[Dict[str, Any]]:
    """
    Resolve item IDs to actual item objects from the wardrobe collection.
    If an item is already a dictionary, return it as is.
    If an item is a string ID, fetch the item from the wardrobe collection.
    """
    resolved_items = []
    
    # If Firebase is not available, return mock items
    if not firebase_initialized:
        logger.warning("Firebase not available, returning mock items")
        for item in items:
            if isinstance(item, dict):
                resolved_items.append(item)
            else:
                resolved_items.append({
                    'id': str(item),
                    'name': 'Mock Item',
                    'type': 'shirt',
                    'imageUrl': None
                })
        return resolved_items
    
    for item in items:
        if isinstance(item, dict):
            # Item is already a complete object
            resolved_items.append(item)
        elif isinstance(item, str):
            # Item is an ID, need to fetch from wardrobe
            try:
                item_doc = db.collection('wardrobe').document(item).get()
                if item_doc.exists:
                    item_data = item_doc.to_dict()
                    # Add the ID to the item data
                    item_data['id'] = item
                    resolved_items.append(item_data)
                else:
                    logger.warning(f"Item {item} not found in wardrobe for user {user_id}")
                    # Add a placeholder item
                    resolved_items.append({
                        'id': item,
                        'name': 'Item not found',
                        'type': 'unknown',
                        'imageUrl': None
                    })
            except Exception as e:
                logger.error(f"Error fetching item {item}: {e}")
                # Add a placeholder item
                resolved_items.append({
                    'id': item,
                    'name': 'Error loading item',
                    'type': 'unknown',
                    'imageUrl': None
                })
        else:
            logger.warning(f"Unexpected item type: {type(item)} for item: {item}")
            # Add a placeholder item
            resolved_items.append({
                'id': str(item),
                'name': 'Invalid item',
                'type': 'unknown',
                'imageUrl': None
            })
    
    return resolved_items

class OutfitResponse(BaseModel):
    id: str
    name: str
    style: str
    mood: str
    items: List[dict]
    occasion: str
    confidence_score: float
    reasoning: str
    createdAt: datetime

class OutfitFeedback(BaseModel):
    outfit_id: str
    rating: int  # 1-5 scale
    feedback_type: str  # "like", "dislike", "comment"
    comment: Optional[str] = None

def _should_bypass_firestore():
    """Check if we should bypass Firestore due to known authentication issues."""
    global _auth_failure_count, _last_auth_failure_time
    
    # If we've had recent auth failures, bypass for a while
    if _last_auth_failure_time:
        time_since_failure = (datetime.utcnow() - _last_auth_failure_time).total_seconds()
        if time_since_failure < 300:  # 5 minutes
            logger.warning(f"Bypassing Firestore due to recent auth failures ({_auth_failure_count} failures)")
            return True
    
    # Only bypass if we've had multiple recent failures
    if _auth_failure_count > 3:
        logger.warning(f"Bypassing Firestore due to multiple auth failures ({_auth_failure_count} failures)")
        return True
    
    return False

def _mark_auth_failure():
    """Mark an authentication failure for smart bypass logic."""
    global _auth_failure_count, _last_auth_failure_time
    _auth_failure_count += 1
    _last_auth_failure_time = datetime.utcnow()
    logger.warning(f"Auth failure detected. Total failures: {_auth_failure_count}")

def _safe_firestore_query(query_func, timeout=3.0):
    """Execute a Firestore query with timeout and error handling."""
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(query_func)
            return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        logger.error("Firestore query timed out")
        _mark_auth_failure()
        raise
    except Exception as e:
        logger.error(f"Firestore query failed: {e}")
        _mark_auth_failure()
        raise

@router.get("/health", response_model=dict)
async def outfits_health_check():
    """Health check for outfits router."""
    logger.info("🔍 DEBUG: Outfits health check called")
    return {"status": "healthy", "router": "outfits"}

@router.get("/debug", response_model=dict)
async def outfits_debug():
    """Debug endpoint for outfits router."""
    logger.info("🔍 DEBUG: Outfits debug endpoint called")
    
    # Get Firebase project ID from environment
    project_id = os.environ.get("FIREBASE_PROJECT_ID", "NOT_SET")
    
    return {
        "status": "debug",
        "router": "outfits",
        "firebase_initialized": firebase_initialized,
        "bypass_enabled": _should_bypass_firestore(),
        "firebase_project_id": project_id,
        "environment": os.environ.get("ENVIRONMENT", "unknown")
    }

@router.get("/debug-fields", response_model=dict)
async def debug_outfit_fields():
    """Debug endpoint to check field names in outfits collection."""
    logger.info("🔍 DEBUG: Debug fields endpoint called")
    
    try:
        # Get a few outfits to check their field names
        outfit_docs = _safe_firestore_query(lambda: db.collection('outfits').limit(3).stream())
        outfit_docs_list = list(outfit_docs)
        
        field_info = []
        for doc in outfit_docs_list:
            outfit_data = doc.to_dict()
            field_info.append({
                "doc_id": doc.id,
                "fields": list(outfit_data.keys()),
                "user_id_field": outfit_data.get('user_id', 'NOT_FOUND'),
                "userId_field": outfit_data.get('userId', 'NOT_FOUND'),
                "user_field": outfit_data.get('user', 'NOT_FOUND'),
                "name": outfit_data.get('name', 'NO_NAME')
            })
        
        return {
            "status": "debug_fields",
            "outfits_checked": len(field_info),
            "field_info": field_info
        }
        
    except Exception as e:
        logger.error(f"🔍 DEBUG: Failed to debug fields: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/debug-user-filtering", response_model=dict)
async def debug_user_filtering(
    current_user_id: str = Depends(get_current_user_id)
):
    """Debug endpoint to show detailed user filtering information."""
    try:
        logger.info(f"🔍 DEBUG: Starting user filtering debug for user: {current_user_id}")
        logger.info(f"🔍 DEBUG: current_user_id type: {type(current_user_id)}")
        logger.info(f"🔍 DEBUG: current_user_id value: '{current_user_id}'")
        
        # Check if Firebase is initialized
        if not firebase_initialized:
            logger.warning("🔍 DEBUG: Firebase not available")
            return {"error": "Firebase not initialized"}
        
        # Check if we should bypass Firestore
        if _should_bypass_firestore():
            logger.warning("🔍 DEBUG: Bypassing Firestore due to authentication issues")
            return {"error": "Firestore bypassed due to authentication issues"}
        
        try:
            # Get all outfits for analysis using safe query
            all_outfits = _safe_firestore_query(lambda: db.collection('outfits').limit(50).stream())
            all_outfits_list = list(all_outfits)
            logger.info(f"🔍 DEBUG: Total outfits found: {len(all_outfits_list)}")
        except Exception as e:
            logger.error(f"🔍 DEBUG: Error getting outfits: {e}")
            return {"error": f"Failed to get outfits: {str(e)}"}
        
        debug_results = {
            "current_user_id": current_user_id,
            "current_user_id_type": str(type(current_user_id)),
            "total_outfits_analyzed": len(all_outfits_list),
            "outfits_with_direct_user_id_match": 0,
            "outfits_with_item_userId_match": 0,
            "outfits_with_no_match": 0,
            "detailed_analysis": []
        }
        
        for doc in all_outfits_list:
            try:
                outfit_data = doc.to_dict()
                outfit_id = doc.id
                
                logger.info(f"🔍 DEBUG: Analyzing outfit {outfit_id}")
                
                # Check direct user_id field
                outfit_user_id = outfit_data.get('user_id')
                outfit_userId = outfit_data.get('userId')
                
                logger.info(f"🔍 DEBUG: Outfit {outfit_id} - user_id: '{outfit_user_id}' (type: {type(outfit_user_id)})")
                logger.info(f"🔍 DEBUG: Outfit {outfit_id} - userId: '{outfit_userId}' (type: {type(outfit_userId)})")
                
                direct_match = False
                item_match = False
                
                # Check direct match
                if outfit_user_id == current_user_id:
                    logger.info(f"🔍 DEBUG: ✅ Direct match on user_id for outfit {outfit_id}")
                    direct_match = True
                    debug_results["outfits_with_direct_user_id_match"] += 1
                elif outfit_userId == current_user_id:
                    logger.info(f"🔍 DEBUG: ✅ Direct match on userId for outfit {outfit_id}")
                    direct_match = True
                    debug_results["outfits_with_direct_user_id_match"] += 1
                else:
                    logger.info(f"🔍 DEBUG: ❌ No direct match for outfit {outfit_id}")
                
                # Check items for userId
                items = outfit_data.get('items', [])
                logger.info(f"🔍 DEBUG: Outfit {outfit_id} has {len(items)} items")
                
                for i, item in enumerate(items):
                    if isinstance(item, dict):
                        item_userId = item.get('userId')
                        logger.info(f"🔍 DEBUG: Item {i} userId: '{item_userId}' (type: {type(item_userId)})")
                        
                        if item_userId == current_user_id:
                            logger.info(f"🔍 DEBUG: ✅ Item {i} userId matches current user")
                            item_match = True
                            break
                        else:
                            logger.info(f"🔍 DEBUG: ❌ Item {i} userId does not match")
                    elif isinstance(item, str):
                        logger.info(f"🔍 DEBUG: Item {i} is string ID: '{item}', checking wardrobe collection")
                        try:
                            item_doc = _safe_firestore_query(lambda: db.collection('wardrobe').document(item).get())
                            if item_doc.exists:
                                item_data = item_doc.to_dict()
                                item_userId = item_data.get('userId')
                                logger.info(f"🔍 DEBUG: Wardrobe item {item} userId: '{item_userId}' (type: {type(item_userId)})")
                                
                                if item_userId == current_user_id:
                                    logger.info(f"🔍 DEBUG: ✅ Wardrobe item {item} userId matches current user")
                                    item_match = True
                                    break
                                else:
                                    logger.info(f"🔍 DEBUG: ❌ Wardrobe item {item} userId does not match")
                            else:
                                logger.info(f"🔍 DEBUG: ⚠️ Wardrobe item {item} not found")
                        except Exception as e:
                            logger.warning(f"🔍 DEBUG: Error checking wardrobe item {item}: {e}")
                
                if not direct_match and not item_match:
                    debug_results["outfits_with_no_match"] += 1
                elif item_match:
                    debug_results["outfits_with_item_userId_match"] += 1
                
                # Add detailed analysis
                debug_results["detailed_analysis"].append({
                    "outfit_id": outfit_id,
                    "outfit_user_id": outfit_user_id,
                    "outfit_userId": outfit_userId,
                    "items_count": len(items),
                    "direct_match": direct_match,
                    "item_match": item_match,
                    "sample_items": items[:2] if items else []
                })
                
            except Exception as e:
                logger.error(f"🔍 DEBUG: Error processing outfit {doc.id if hasattr(doc, 'id') else 'unknown'}: {e}")
                continue
        
        logger.info(f"🔍 DEBUG: Final results - Direct matches: {debug_results['outfits_with_direct_user_id_match']}, Item matches: {debug_results['outfits_with_item_userId_match']}, No matches: {debug_results['outfits_with_no_match']}")
        
        return debug_results
        
    except Exception as e:
        logger.error(f"🔍 DEBUG: Error in debug_user_filtering: {e}")
        return {"error": str(e)}

@router.get("/debug-simple", response_model=dict)
async def debug_simple():
    """Simple debug endpoint without authentication."""
    try:
        logger.info("🔍 DEBUG: Simple debug endpoint called")
        
        # Check if Firebase is initialized
        if not firebase_initialized:
            logger.warning("🔍 DEBUG: Firebase not available")
            return {"error": "Firebase not initialized"}
        
        # Check if we should bypass Firestore
        if _should_bypass_firestore():
            logger.warning("🔍 DEBUG: Bypassing Firestore due to authentication issues")
            return {"error": "Firestore bypassed due to authentication issues"}
        
        try:
            # Test basic Firestore access without complex logic
            logger.info("🔍 DEBUG: Testing basic Firestore access...")
            
            # Try direct access first
            outfits_ref = db.collection('outfits')
            logger.info("🔍 DEBUG: Created outfits collection reference")
            
            # Get a few documents
            docs = outfits_ref.limit(5).stream()
            outfits_list = list(docs)
            logger.info(f"🔍 DEBUG: Retrieved {len(outfits_list)} outfits")
            
            simple_results = {
                "total_outfits": len(outfits_list),
                "outfits_with_user_id": 0,
                "outfits_with_userId": 0,
                "sample_outfits": []
            }
            
            for doc in outfits_list:
                try:
                    outfit_data = doc.to_dict()
                    outfit_id = doc.id
                    
                    has_user_id = 'user_id' in outfit_data
                    has_userId = 'userId' in outfit_data
                    
                    if has_user_id:
                        simple_results["outfits_with_user_id"] += 1
                    if has_userId:
                        simple_results["outfits_with_userId"] += 1
                    
                    simple_results["sample_outfits"].append({
                        "id": outfit_id,
                        "has_user_id": has_user_id,
                        "has_userId": has_userId,
                        "user_id_value": outfit_data.get('user_id'),
                        "userId_value": outfit_data.get('userId'),
                        "items_count": len(outfit_data.get('items', []))
                    })
                except Exception as e:
                    logger.error(f"🔍 DEBUG: Error processing outfit {doc.id}: {e}")
                    continue
            
            logger.info("🔍 DEBUG: Simple debug completed successfully")
            return simple_results
            
        except Exception as e:
            logger.error(f"🔍 DEBUG: Error in simple debug: {e}")
            return {"error": f"Failed to get outfits: {str(e)}"}
        
    except Exception as e:
        logger.error(f"🔍 DEBUG: Error in debug_simple: {e}")
        return {"error": str(e)}

@router.get("/debug-minimal", response_model=dict)
async def debug_minimal():
    """Minimal debug endpoint that just returns basic info."""
    try:
        logger.info("🔍 DEBUG: Minimal debug endpoint called")
        
        return {
            "status": "success",
            "message": "Minimal debug endpoint working",
            "firebase_initialized": firebase_initialized,
            "should_bypass_firestore": _should_bypass_firestore(),
            "db_object": str(db) if 'db' in globals() else "Not available"
        }
        
    except Exception as e:
        logger.error(f"🔍 DEBUG: Error in minimal debug: {e}")
        return {"error": str(e)}

@router.get("/test", response_model=List[OutfitResponse])
async def get_test_outfits():
    """Get test outfits without authentication (for testing)."""
    logger.info("🔍 DEBUG: Test endpoint called - returning limited test outfits")
    
    # Check if Firebase is initialized first
    if not firebase_initialized:
        logger.warning("🔍 DEBUG: Firebase not available, returning mock outfits")
        return _get_mock_outfits()
    
    # Check if we should bypass Firestore due to known authentication issues
    if _should_bypass_firestore():
        logger.warning("🔍 DEBUG: Bypassing Firestore due to authentication issues, returning mock outfits")
        return _get_mock_outfits()
    
    try:
        logger.info("🔍 DEBUG: Starting Firestore query for test outfits...")
        
        # Use a timeout for the Firestore query - LIMIT TO 10 OUTFITS ONLY
        outfit_docs = _safe_firestore_query(lambda: db.collection('outfits').limit(10).stream())
        
        logger.info("🔍 DEBUG: Firestore query completed successfully!")
        logger.info("🔍 DEBUG: Processing Firestore results...")
        outfits = []
        
        # Convert generator to list with timeout protection
        try:
            logger.info("🔍 DEBUG: Converting Firestore results to list...")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: list(outfit_docs))
                outfit_docs_list = future.result(timeout=3.0)  # 3 second timeout for conversion
            logger.info(f"🔍 DEBUG: Successfully converted {len(outfit_docs_list)} documents to list")
        except concurrent.futures.TimeoutError:
            logger.error("🔍 DEBUG: Document conversion timed out")
            logger.warning("🔍 DEBUG: Returning mock outfits due to document processing timeout")
            return _get_mock_outfits()
        
        for doc in outfit_docs_list:
            try:
                logger.info(f"🔍 DEBUG: Processing test outfit document: {doc.id}")
                outfit_data = doc.to_dict()
                
                # Resolve item IDs to actual item objects
                resolved_items = await resolve_item_ids_to_objects(outfit_data.get('items', []), "test_user")
                
                outfits.append(OutfitResponse(
                    id=doc.id,
                    name=outfit_data.get('name', ''),
                    style=outfit_data.get('style', ''),
                    mood=outfit_data.get('mood', ''),
                    items=resolved_items,
                    occasion=outfit_data.get('occasion', 'Casual'),
                    confidence_score=outfit_data.get('confidence_score', 0.0),
                    reasoning=outfit_data.get('reasoning', ''),
                    createdAt=outfit_data['createdAt']
                ))
            except Exception as e:
                logger.error(f"🔍 DEBUG: Error processing test document {doc.id}: {e}")
                continue  # Skip this document and continue with others
        
        logger.info(f"🔍 DEBUG: Successfully processed {len(outfits)} test outfits")
        logger.info("🔍 DEBUG: Returning test outfits (limited to 10)")
        return outfits
        
    except Exception as e:
        logger.error(f"🔍 DEBUG: Failed to get test outfits: {e}")
        logger.warning("🔍 DEBUG: Returning mock outfits due to Firestore error")
        return _get_mock_outfits()

def _get_mock_outfits():
    """Return mock outfits for testing."""
    mock_outfits = [
        {
            "id": "mock-outfit-1",
            "name": "Casual Summer Look",
            "style": "Casual",
            "mood": "Relaxed",
            "items": [
                {"id": "mock-item-1", "name": "Blue T-Shirt", "type": "shirt", "imageUrl": None},
                {"id": "mock-item-2", "name": "Jeans", "type": "pants", "imageUrl": None}
            ],
            "occasion": "Casual",
            "confidence_score": 0.85,
            "reasoning": "Perfect for a casual day out",
            "createdAt": datetime.utcnow()
        },
        {
            "id": "mock-outfit-2", 
            "name": "Business Casual",
            "style": "Business Casual",
            "mood": "Professional",
            "items": [
                {"id": "mock-item-3", "name": "White Shirt", "type": "shirt", "imageUrl": None},
                {"id": "mock-item-4", "name": "Khaki Pants", "type": "pants", "imageUrl": None}
            ],
            "occasion": "Business",
            "confidence_score": 0.92,
            "reasoning": "Professional yet comfortable",
            "createdAt": datetime.utcnow()
        }
    ]
    
    return [OutfitResponse(**outfit) for outfit in mock_outfits]

@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(
    outfit_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Get a specific outfit by ID."""
    try:
        outfit_doc = db.collection('outfits').document(outfit_id).get()
        
        if not outfit_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outfit not found"
            )
        
        outfit_data = outfit_doc.to_dict()
        
        # Resolve item IDs to actual item objects
        resolved_items = await resolve_item_ids_to_objects(outfit_data.get('items', []), current_user_id)
        
        return OutfitResponse(
            id=outfit_doc.id,
            name=outfit_data.get('name', ''),
            style=outfit_data.get('style', ''),
            mood=outfit_data.get('mood', ''),
            items=resolved_items,
            occasion=outfit_data.get('occasion', 'Casual'),
            confidence_score=outfit_data.get('confidence_score', 0.0),
            reasoning=outfit_data.get('reasoning', ''),
            createdAt=outfit_data['createdAt']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get outfit {outfit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get outfit"
        )

@router.get("/", response_model=List[OutfitResponse])
async def get_user_outfits(
    current_user_id: str = Depends(get_current_user_id),
    limit: Optional[int] = 1000,  # High limit to show most outfits, but prevent performance issues
    offset: int = 0
):
    """Get user's outfit history."""
    
    logger.info("🔍 DEBUG: ===== STARTING GET_USER_OUTFITS ENDPOINT =====")
    logger.info(f"🔍 DEBUG: Request received for user: {current_user_id}")
    logger.info(f"🔍 DEBUG: current_user_id type: {type(current_user_id)}")
    logger.info(f"🔍 DEBUG: current_user_id value: '{current_user_id}'")
    logger.info(f"🔍 DEBUG: current_user_id length: {len(current_user_id)}")
    logger.info(f"🔍 DEBUG: Limit parameter: {limit}")
    logger.info(f"🔍 DEBUG: Offset parameter: {offset}")
    
    # Check if Firebase is initialized first
    if not firebase_initialized:
        logger.warning("🔍 DEBUG: Firebase not available, returning mock outfits")
        return _get_mock_outfits()
    
    # Check if we should bypass Firestore due to known authentication issues
    if _should_bypass_firestore():
        logger.warning("🔍 DEBUG: Bypassing Firestore due to authentication issues, returning mock outfits")
        return _get_mock_outfits()
    
    try:
        logger.info("🔍 DEBUG: Starting Firestore query for user outfits...")
        
        # First try to get outfits with user_id field
        logger.info(f"🔍 DEBUG: Querying outfits with user_id == '{current_user_id}'")
        outfit_docs = _safe_firestore_query(lambda: db.collection('outfits').where('user_id', '==', current_user_id).limit(limit).offset(offset).stream())
        
        # If no outfits found, try getting all outfits and filter by items' userId
        outfit_docs_list = list(outfit_docs)
        logger.info(f"🔍 DEBUG: Found {len(outfit_docs_list)} outfits with user_id field")
        
        if not outfit_docs_list:
            logger.info("🔍 DEBUG: No outfits found with user_id field, trying to filter by items' userId")
            all_outfit_docs = _safe_firestore_query(lambda: db.collection('outfits').limit(1000).stream())
            outfit_docs_list = []
            
            # Debug: Log total outfits found
            all_outfits_count = 0
            for doc in all_outfit_docs:
                all_outfits_count += 1
            logger.info(f"🔍 DEBUG: Total outfits in database: {all_outfits_count}")
            
            # Reset iterator for processing
            all_outfit_docs = _safe_firestore_query(lambda: db.collection('outfits').limit(1000).stream())
            
            for doc in all_outfit_docs:
                outfit_data = doc.to_dict()
                items = outfit_data.get('items', [])
                match_found = False
                
                logger.info(f"🔍 DEBUG: Checking outfit {doc.id} with {len(items)} items")
                
                for item in items:
                    user_id_to_check = None
                    
                    if isinstance(item, dict):
                        user_id_to_check = item.get('userId')
                        logger.info(f"🔍 DEBUG: Item is dict, userId: '{user_id_to_check}' (type: {type(user_id_to_check)})")
                    elif isinstance(item, str):
                        logger.info(f"🔍 DEBUG: Item is string ID: '{item}', checking wardrobe collection")
                        try:
                            item_doc = db.collection('wardrobe').document(item).get()
                            if item_doc.exists:
                                item_data = item_doc.to_dict()
                                user_id_to_check = item_data.get('userId')
                                logger.info(f"🔍 DEBUG: Found wardrobe item, userId: '{user_id_to_check}' (type: {type(user_id_to_check)})")
                            else:
                                logger.info(f"🔍 DEBUG: Wardrobe item {item} not found")
                        except Exception as e:
                            logger.warning(f"Error checking item {item}: {e}")
                            continue
                    
                    # Debug: Log comparison details
                    if user_id_to_check is not None:
                        logger.info(f"🔍 DEBUG: Comparing '{user_id_to_check}' == '{current_user_id}' (result: {user_id_to_check == current_user_id})")
                        if user_id_to_check == current_user_id:
                            match_found = True
                            logger.info(f"🔍 DEBUG: ✅ Including outfit {doc.id} for user {current_user_id}")
                            outfit_docs_list.append(doc)
                            break
                        else:
                            logger.info(f"🔍 DEBUG: ❌ User ID mismatch for outfit {doc.id}")
                    else:
                        logger.info(f"🔍 DEBUG: ⚠️ No userId found for item in outfit {doc.id}")
                
                if not match_found:
                    logger.info(f"🔍 DEBUG: ❌ Excluding outfit {doc.id} for user {current_user_id} (no matching items)")
        
        logger.info("🔍 DEBUG: Firestore query completed successfully!")
        logger.info(f"🔍 DEBUG: Final outfit count after filtering: {len(outfit_docs_list)}")
        logger.info("🔍 DEBUG: Processing Firestore results...")
        outfits = []
        
        # outfit_docs_list is already populated above
        logger.info(f"🔍 DEBUG: Successfully found {len(outfit_docs_list)} outfits for user")
        
        for doc in outfit_docs_list:
            try:
                logger.info(f"🔍 DEBUG: Processing outfit document: {doc.id}")
                outfit_data = doc.to_dict()
                
                # Log outfit data for debugging
                logger.info(f"🔍 DEBUG: Outfit {doc.id} data keys: {list(outfit_data.keys())}")
                logger.info(f"🔍 DEBUG: Outfit {doc.id} user_id: {outfit_data.get('user_id')}")
                logger.info(f"🔍 DEBUG: Outfit {doc.id} userId: {outfit_data.get('userId')}")
                logger.info(f"🔍 DEBUG: Outfit {doc.id} items count: {len(outfit_data.get('items', []))}")
                
                # Resolve item IDs to actual item objects
                resolved_items = await resolve_item_ids_to_objects(outfit_data.get('items', []), current_user_id)
                
                outfits.append(OutfitResponse(
                    id=doc.id,
                    name=outfit_data.get('name', ''),
                    style=outfit_data.get('style', ''),
                    mood=outfit_data.get('mood', ''),
                    items=resolved_items,
                    occasion=outfit_data.get('occasion', 'Casual'),
                    confidence_score=outfit_data.get('confidence_score', 0.0),
                    reasoning=outfit_data.get('reasoning', ''),
                    createdAt=outfit_data['createdAt']
                ))
                
                logger.info(f"🔍 DEBUG: Successfully processed outfit {doc.id}")
            except Exception as e:
                logger.error(f"🔍 DEBUG: Error processing document {doc.id}: {e}")
                continue  # Skip this document and continue with others
        
        logger.info(f"🔍 DEBUG: Successfully processed {len(outfits)} outfits")
        logger.info("🔍 DEBUG: ===== GET_USER_OUTFITS ENDPOINT COMPLETED SUCCESSFULLY =====")
        return outfits
        
    except Exception as e:
        logger.error("🔍 DEBUG: ===== GET_USER_OUTFITS ENDPOINT FAILED =====")
        logger.error(f"🔍 DEBUG: Failed to get user outfits: {e}")
        logger.warning("🔍 DEBUG: Returning mock outfits due to Firestore error")
        return _get_mock_outfits()

@router.post("/feedback")
async def submit_outfit_feedback(
    feedback: OutfitFeedback,
    current_user_id: str = Depends(get_current_user_id)
):
    """Submit feedback for an outfit."""
    try:
        # Verify outfit exists and belongs to user
        outfit_doc = db.collection('outfits').document(feedback.outfit_id).get()
        
        if not outfit_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outfit not found"
            )
        
        outfit_data = outfit_doc.to_dict()
        if outfit_data['user_id'] != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Save feedback
        feedback_doc = {
            'outfit_id': feedback.outfit_id,
            'user_id': current_user_id,
            'rating': feedback.rating,
            'feedback_type': feedback.feedback_type,
            'comment': feedback.comment,
            'created_at': datetime.utcnow()
        }
        
        feedback_id = str(uuid.uuid4())
        db.collection('outfit_feedback').document(feedback_id).set(feedback_doc)
        
        # Update outfit with feedback
        outfit_ref = db.collection('outfits').document(feedback.outfit_id)
        outfit_ref.update({
            'last_feedback': feedback_doc,
            'updated_at': datetime.utcnow()
        })
        
        # Log analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            event_type="outfit_feedback_submitted",
            metadata={
                "outfit_id": feedback.outfit_id,
                "rating": feedback.rating,
                "feedback_type": feedback.feedback_type,
                "has_comment": bool(feedback.comment)
            }
        )
        
        await log_analytics_event(analytics_event)
        
        return {"status": "success", "message": "Feedback submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit outfit feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )

@router.delete("/{outfit_id}")
async def delete_outfit(
    outfit_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete an outfit."""
    try:
        # Verify outfit exists and belongs to user
        outfit_doc = db.collection('outfits').document(outfit_id).get()
        
        if not outfit_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outfit not found"
            )
        
        outfit_data = outfit_doc.to_dict()
        if outfit_data['user_id'] != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete the outfit
        db.collection('outfits').document(outfit_id).delete()
        
        return {"status": "success", "message": "Outfit deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete outfit {outfit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete outfit"
        ) 