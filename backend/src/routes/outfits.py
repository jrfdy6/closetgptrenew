"""
Outfit management endpoints - Single canonical generator with bulletproof consistency.
All outfits are generated and saved through the same pipeline.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["outfits"]
)
security = HTTPBearer()

# Firebase imports with graceful fallback
try:
    from ..config.firebase import db, firebase_initialized
    from ..auth.auth_service import get_current_user_optional
    from ..custom_types.profile import UserProfile
    FIREBASE_AVAILABLE = True
    logger.info("✅ Firebase modules imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Firebase import failed: {e}")
    FIREBASE_AVAILABLE = False
    db = None
    firebase_initialized = False
    # Create a mock get_current_user_optional function
    def get_current_user_optional():
        return None
else:
    try:
        from firebase_admin import firestore
        db = firestore.client()
        firebase_initialized = True
        FIREBASE_AVAILABLE = True
        logger.info("✅ Firebase successfully imported and initialized")
    except Exception as e:
        logger.error(f"❌ Firebase import error: {e}")
        FIREBASE_AVAILABLE = False
        db = None
        firebase_initialized = False
        # Create a mock get_current_user_optional function
        def get_current_user_optional():
            return None

# Simplified mock data function for fallback
# async def get_mock_outfits() -> List[Dict[str, Any]]:
#     """Return mock outfit data for testing."""
#     return [
#         {
#             "id": "mock-outfit-1",
#             "name": "Casual Summer Look",
#             "style": "casual",
#             "mood": "relaxed",
#             "items": [
#                 {"id": "item-1", "name": "Blue T-Shirt", "type": "shirt", "imageUrl": None},
#                 {"id": "item-2", "name": "Jeans", "type": "pants", "imageUrl": None}
#             ],
#             "occasion": "casual",
#             "confidence_score": 0.85,
#             "reasoning": "Perfect for a relaxed summer day",
#             "createdAt": datetime.now().isoformat(),
#             "user_id": None,
#             "generated_at": None
#         },
#         {
#             "id": "mock-outfit-2",
#             "name": "Business Casual",
#             "style": "business",
#             "mood": "professional",
#             "items": [
#                 {"id": "item-3", "name": "White Button-Up", "type": "shirt", "imageUrl": None},
#                 {"id": "item-4", "name": "Khaki Pants", "type": "pants", "imageUrl": None}
#             ],
#             "occasion": "business",
#             "confidence_score": 0.9,
#             "reasoning": "Professional yet comfortable",
#             "createdAt": datetime.now().isoformat(),
#             "user_id": None,
#             "generated_at": None
#         }
#     ]

class OutfitRequest(BaseModel):
    """Request model for outfit generation."""
    style: str
    mood: str
    occasion: str
    description: Optional[str] = None

class OutfitResponse(BaseModel):
    """Response model for outfits."""
    id: str
    name: str
    style: Optional[str] = None
    mood: Optional[str] = None
    items: Optional[List[dict]] = None
    occasion: Optional[str] = None
    confidence_score: Optional[float] = None  # Keep this field but allow None values
    reasoning: Optional[str] = None
    createdAt: Optional[datetime] = None
    user_id: Optional[str] = None
    generated_at: Optional[str] = None

# Real outfit generation logic with AI and user wardrobe
async def generate_outfit_logic(req: OutfitRequest, user_id: str) -> Dict[str, Any]:
    """Real outfit generation logic using user's wardrobe and AI recommendations."""
    logger.info(f"🎨 Generating outfit for user {user_id}: {req.style}, {req.mood}, {req.occasion}")
    
    try:
        # 1. Get user's wardrobe items from Firestore
        wardrobe_items = await get_user_wardrobe(user_id)
        logger.info(f"📦 Found {len(wardrobe_items)} items in user's wardrobe")
        
        # 2. Get user's style profile
        user_profile = await get_user_profile(user_id)
        logger.info(f"👤 Retrieved user profile for {user_id}")
        
        # 3. Generate outfit using AI logic
        outfit = await generate_ai_outfit(wardrobe_items, user_profile, req)
        logger.info(f"✨ Generated outfit: {outfit['name']}")
        
        return outfit
        
    except Exception as e:
        logger.warning(f"⚠️ Outfit generation failed, using fallback: {e}")
        # Fallback to basic generation if AI fails
        return await generate_fallback_outfit(req, user_id)

# Helper functions for outfit generation
async def get_user_wardrobe(user_id: str) -> List[Dict[str, Any]]:
    """Get user's wardrobe items from Firestore."""
    try:
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, returning empty wardrobe")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
            
        logger.info(f"📦 Fetching wardrobe for user {user_id}")
        
        # Query user's wardrobe items
        wardrobe_ref = db.collection('users').document(user_id).collection('wardrobe')
        docs = wardrobe_ref.get()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            items.append(item_data)
        
        logger.info(f"✅ Retrieved {len(items)} wardrobe items")
        return items
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch wardrobe for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch wardrobe: {e}")

async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user's style profile from Firestore."""
    try:
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, using default profile")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
            
        logger.info(f"👤 Fetching profile for user {user_id}")
        
        # Query user's profile
        profile_ref = db.collection('users').document(user_id)
        profile_doc = profile_ref.get()
        
        if profile_doc.exists:
            profile_data = profile_doc.to_dict()
            logger.info(f"✅ Retrieved profile for user {user_id}")
            return profile_data
        else:
            logger.info(f"⚠️ No profile found for user {user_id}, using defaults")
            raise HTTPException(status_code=404, detail=f"User profile not found for ID: {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch profile for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user profile: {e}")

async def generate_ai_outfit(wardrobe_items: List[Dict], user_profile: Dict, req: OutfitRequest) -> Dict[str, Any]:
    """Generate outfit using AI logic and user's wardrobe."""
    try:
        logger.info(f"🤖 Generating AI outfit with {len(wardrobe_items)} items")
        
        # For now, implement basic outfit selection logic
        # TODO: Integrate with OpenAI GPT for more sophisticated generation
        
        # Filter items by occasion and style
        suitable_items = []
        for item in wardrobe_items:
            item_style = item.get('style', '').lower()
            item_occasion = item.get('occasion', '').lower()
            
            # Basic matching logic
            if (req.style.lower() in item_style or 
                req.occasion.lower() in item_occasion or
                'versatile' in item_style):
                suitable_items.append(item)
        
        # If no suitable items, use any available items
        if not suitable_items:
            suitable_items = wardrobe_items[:4]  # Take first 4 items
        
        # Create outfit
        outfit_name = f"{req.style.title()} {req.mood.title()} Look"
        
        return {
            "name": outfit_name,
            "style": req.style,
            "mood": req.mood,
            "items": suitable_items[:4],  # Take up to 4 items
            "occasion": req.occasion,
            "confidence_score": 0.85 if suitable_items else 0.6,
            "reasoning": f"Selected {len(suitable_items[:4])} items from your wardrobe that match {req.style} style for {req.occasion}",
            "createdAt": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"❌ AI outfit generation failed: {e}")
        # Fall back to basic generation
        return await generate_fallback_outfit(req, "unknown")

async def generate_fallback_outfit(req: OutfitRequest, user_id: str) -> Dict[str, Any]:
    """Generate basic fallback outfit when AI generation fails."""
    logger.info(f"🔄 Generating fallback outfit for {user_id}")
    
    outfit_name = f"{req.style.title()} {req.mood.title()} Look"
    
    return {
        "name": outfit_name,
        "style": req.style,
        "mood": req.mood,
        "items": [
            {"id": "fallback-1", "name": f"{req.style} Top", "type": "shirt", "imageUrl": None},
            {"id": "fallback-2", "name": f"{req.mood} Pants", "type": "pants", "imageUrl": None}
        ],
        "occasion": req.occasion,
        "confidence_score": 0.5,
        "reasoning": f"Basic {req.style} outfit for {req.occasion} (fallback generation)",
        "createdAt": datetime.now()
    }

# Real Firestore operations
async def save_outfit(user_id: str, outfit_id: str, outfit_record: Dict[str, Any]) -> bool:
    """Save outfit to Firestore."""
    try:
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, skipping save")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
            
        logger.info(f"💾 Saving outfit {outfit_id} for user {user_id}")
        
        # Save to user's outfits collection
        outfits_ref = db.collection('users').document(user_id).collection('outfits')
        outfits_ref.document(outfit_id).set(outfit_record)
        
        # Also save to global outfits collection for analytics
        global_ref = db.collection('outfits').document(outfit_id)
        global_ref.set(outfit_record)
        
        logger.info(f"✅ Successfully saved outfit {outfit_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save outfit {outfit_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save outfit: {e}")

async def get_user_outfits(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Get user outfits from Firestore with pagination."""
    logger.info(f"🔍 DEBUG: Fetching outfits for user {user_id} (limit={limit}, offset={offset})")
    logger.info(f"🔍 DEBUG: FIREBASE_AVAILABLE: {FIREBASE_AVAILABLE}")
    logger.info(f"🔍 DEBUG: firebase_initialized: {firebase_initialized}")
    
    try:
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, returning empty outfits")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
            
        logger.info(f"📚 DEBUG: About to query Firestore collection('outfits') with user_id == '{user_id}'")
        
        # FIXED: Query main outfits collection with user_id filter (not subcollection)
        # This matches where outfits are actually stored: outfits collection with user_id field
        outfits_ref = db.collection("outfits").where("user_id", "==", user_id)
        
        # Apply pagination
        if offset > 0:
            outfits_ref = outfits_ref.offset(offset)
        outfits_ref = outfits_ref.limit(limit)
        
        # Execute query
        logger.info(f"🔍 DEBUG: Executing Firestore query with .stream()...")
        docs = outfits_ref.stream()
        logger.info(f"🔍 DEBUG: Firestore query executed successfully, processing results...")
        
        outfits = []
        for doc in docs:
            outfit_data = doc.to_dict()
            outfit_data['id'] = doc.id
            outfits.append(outfit_data)
            logger.info(f"🔍 DEBUG: Found outfit: {outfit_data.get('name', 'unnamed')} (ID: {doc.id})")
        
        logger.info(f"✅ DEBUG: Successfully retrieved {len(outfits)} outfits from Firestore for user {user_id}")
        return outfits
        
    except Exception as e:
        logger.error(f"❌ ERROR: Failed to fetch outfits from Firestore: {e}", exc_info=True)
        logger.error(f"❌ ERROR: Exception type: {type(e)}")
        logger.error(f"❌ ERROR: Exception details: {str(e)}")
        import traceback
        logger.error(f"❌ ERROR: Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user outfits: {e}")

# Health and debug endpoints (MUST be before parameterized routes)
@router.get("/health", response_model=dict)
async def outfits_health_check():
    """Health check for outfits router."""
    logger.info("🔍 DEBUG: Outfits health check called")
    return {
        "status": "healthy", 
        "router": "outfits", 
        "message": "Outfits router is working!",
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
                "name": outfit_data.get('name', 'unknown'),
                "user_id": outfit_data.get('user_id', 'unknown')
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

@router.get("/debug-user", response_model=dict)
async def debug_user_outfits(
    current_user: UserProfile = Depends(get_current_user_optional)
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
                                "name": outfit_data.get('name', 'unnamed'),
                                "user_id": outfit_data.get('user_id', outfit_data.get('userId', 'no_user_id')),
                                "created_at": outfit_data.get('createdAt', outfit_data.get('created_at', 'no_date')),
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
@router.post("/generate", response_model=OutfitResponse)
async def generate_outfit(
    req: OutfitRequest,
):
    """
    Generate an outfit using decision logic, save it to Firestore,
    and return the standardized response.
    """
    try:
        # TEMPORARILY: Use mock user ID for testing
        current_user_id = "mock-user-123"
        logger.info("Using mock user ID for testing")
        
        logger.info(f"🎨 Generating outfit for user: {current_user_id}")
        
        # 1. Run generation logic (GPT + rules + metadata validation)
        outfit = await generate_outfit_logic(req, current_user_id)

        # 2. Wrap with metadata
        outfit_id = str(uuid4())
        outfit_record = {
            "id": outfit_id,
            "user_id": current_user_id,
            "generated_at": datetime.utcnow().isoformat(),
            **outfit
        }

        # 3. Save to Firestore
        await save_outfit(current_user_id, outfit_id, outfit_record)

        # 4. Return standardized outfit response
        logger.info(f"✅ Successfully generated and saved outfit {outfit_id}")
        return OutfitResponse(**outfit_record)

    except Exception as e:
        logger.error(f"❌ Outfit generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate outfit")

# ⚠️ PARAMETERIZED ROUTE - MUST BE FIRST TO AVOID ROUTE CONFLICTS!
# This route MUST come BEFORE the root route to avoid catching it
@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(outfit_id: str):
    """Get a specific outfit by ID. MUST BE FIRST ROUTE TO AVOID CONFLICTS."""
    logger.info(f"🔍 DEBUG: Get outfit {outfit_id} endpoint called")
    
    try:
        # Use the actual user ID from your database where the 1000+ outfits are stored
        current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # TEMPORARY: Your actual user ID
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
    current_user: UserProfile = Depends(get_current_user_optional)
):
    """
    Fetch a user's outfit history from Firestore.
    """
    try:
        # TEMPORARY FIX: Use the actual user ID from your database
        # TODO: Fix authentication to get real user ID
        if current_user:
            current_user_id = current_user.id
            logger.info(f"📚 Fetching outfits for authenticated user: {current_user_id}")
        else:
            # Use the actual user ID from your database where the 1000+ outfits are stored
            current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # TEMPORARY: Your actual user ID
            logger.info(f"📚 No authenticated user, using hardcoded user ID: {current_user_id}")
        
        logger.info(f"📚 Fetching outfits for user: {current_user_id}")
        
        outfits = await get_user_outfits(current_user_id, limit, offset)
        logger.info(f"✅ Successfully retrieved {len(outfits)} outfits for user {current_user_id}")
        return [OutfitResponse(**o) for o in outfits]
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch outfits for {current_user_id}: {e}", exc_info=True)
        # Fallback to mock data on error
        raise HTTPException(status_code=500, detail=f"Failed to fetch user outfits: {e}")

@router.get("", include_in_schema=False, response_model=List[OutfitResponse])
async def list_outfits_no_slash(
    limit: int = 50,
    offset: int = 0,
    current_user: UserProfile = Depends(get_current_user_optional)
):
    """
    Fetch a user's outfit history from Firestore (no trailing slash).
    """
    try:
        # TEMPORARY FIX: Use the actual user ID from your database
        # TODO: Fix authentication to get real user ID
        if current_user:
            current_user_id = current_user.id
            logger.info(f"📚 Fetching outfits for authenticated user: {current_user_id}")
        else:
            # Use the actual user ID from your database where the 1000+ outfits are stored
            current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # TEMPORARY: Your actual user ID
            logger.info(f"📚 No authenticated user, using hardcoded user ID: {current_user_id}")
        
        logger.info(f"📚 Fetching outfits for user: {current_user_id}")
        
        outfits = await get_user_outfits(current_user_id, limit, offset)
        logger.info(f"✅ Successfully retrieved {len(outfits)} outfits for user {current_user_id}")
        return [OutfitResponse(**o) for o in outfits]
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch outfits for {current_user_id}: {e}", exc_info=True)
        # Fallback to mock data on error
        raise HTTPException(status_code=500, detail=f"Failed to fetch user outfits: {e}")

# 📊 Get Outfit Statistics
@router.get("/stats/summary")
async def get_outfit_stats(
    current_user: UserProfile = Depends(get_current_user_optional)
):
    """
    Get outfit statistics for user.
    """
    try:
        # TEMPORARY FIX: Use the actual user ID from your database
        # TODO: Fix authentication to get real user ID
        if current_user:
            current_user_id = current_user.id
            logger.info(f"📊 Getting outfit stats for authenticated user {current_user_id}")
        else:
            # Use the actual user ID from your database where the 1000+ outfits are stored
            current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # TEMPORARY: Your actual user ID
            logger.info(f"📊 No authenticated user, using hardcoded user ID: {current_user_id}")
        
        logger.info(f"📊 Getting outfit stats for user {current_user_id}")
        
        # Get real outfits for stats
        outfits = await get_user_outfits(current_user_id, 1000, 0)  # Get all outfits for stats
        
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
            occasion = outfit.get('occasion', 'Unknown')
            stats['occasions'][occasion] = stats['occasions'].get(occasion, 0) + 1
            
            style = outfit.get('style', 'Unknown')
            stats['styles'][style] = stats['styles'].get(style, 0) + 1
        
        # Add recent activity
        if outfits:
            stats['recentActivity'] = [
                {
                    'id': o['id'],
                    'name': o['name'],
                    'lastUpdated': o.get('createdAt', datetime.now())
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