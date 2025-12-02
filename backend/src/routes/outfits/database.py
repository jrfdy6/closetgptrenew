"""
Database operations for outfit management.
Handles all Firestore operations for outfits, wardrobe, and user profiles.
"""

import logging
import time
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Import for Firestore timestamp handling
try:
    from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds
    FIRESTORE_TIMESTAMP_AVAILABLE = True
except ImportError:
    FIRESTORE_TIMESTAMP_AVAILABLE = False


def convert_firebase_url(raw_image_url: str) -> str:
    """Convert Firebase Storage gs:// URLs to https:// URLs"""
    if raw_image_url and raw_image_url.startswith('gs://'):
        # Convert gs://bucket-name/path to https://firebasestorage.googleapis.com/v0/b/bucket-name/o/path
        parts = raw_image_url.replace('gs://', '').split('/', 1)
        if len(parts) == 2:
            bucket_name = parts[0]
            file_path = parts[1]
            # Encode the file path for URL
            encoded_path = urllib.parse.quote(file_path, safe='')
            return f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{encoded_path}?alt=media"
    return raw_image_url


def compute_created_at_ms(created_at) -> int:
    """Convert any supported created_at value to epoch milliseconds."""
    try:
        if created_at is None:
            return int(time.time() * 1000)
        
        if isinstance(created_at, (int, float)):
            # Distinguish between seconds and milliseconds
            return int(created_at if created_at > 1e12 else created_at * 1000)
        
        if isinstance(created_at, str):
            try:
                parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                return int(parsed.timestamp() * 1000)
            except Exception:
                return int(time.time() * 1000)
        
        if FIRESTORE_TIMESTAMP_AVAILABLE and isinstance(created_at, DatetimeWithNanoseconds):
            return int(created_at.timestamp() * 1000)
        
        if isinstance(created_at, datetime):
            return int(created_at.timestamp() * 1000)
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to compute created_at_ms from {created_at}: {e}")
    
    return int(time.time() * 1000)


def normalize_created_at(created_at) -> str:
    """Safely normalize Firestore created_at into ISO8601 string."""
    try:
        # Case 1: Firestore Timestamp object (DatetimeWithNanoseconds)
        if FIRESTORE_TIMESTAMP_AVAILABLE and isinstance(created_at, DatetimeWithNanoseconds):
            return created_at.isoformat() + "Z" if not created_at.isoformat().endswith("Z") else created_at.isoformat()
        
        # Case 2: Python datetime object
        if isinstance(created_at, datetime):
            return created_at.isoformat() + "Z" if not created_at.isoformat().endswith("Z") else created_at.isoformat()
        
        # Case 3: Int/float timestamp (seconds or milliseconds since epoch) - SAFE RANGE CHECK
        if isinstance(created_at, (int, float)):
            # Handle both seconds and milliseconds timestamps
            if created_at > 1e12:  # Likely milliseconds (> year 33658)
                timestamp_seconds = created_at / 1000.0
            else:
                timestamp_seconds = created_at
            
            # Sanity check: Unix timestamps should be roughly between 2000-2100
            # 946684800 = Jan 1, 2000 UTC, 4102444800 = Jan 1, 2100 UTC  
            if 946684800 <= timestamp_seconds <= 4102444800:
                return datetime.utcfromtimestamp(timestamp_seconds).isoformat() + "Z"
            else:
                logger.warning(f"⚠️ Invalid timestamp value: {created_at} (computed seconds: {timestamp_seconds}, out of reasonable range)")
                return datetime.utcnow().isoformat() + "Z"
        
        # Case 4: Already ISO string
        if isinstance(created_at, str):
            # Handle double timezone issue: "2025-08-27T21:10:11.828353+00:00Z"
            if "+00:00Z" in created_at:
                # Remove the +00:00 part, keep only Z
                created_at = created_at.replace("+00:00Z", "Z")
            elif "+00:00" in created_at and not created_at.endswith("Z"):
                # Replace +00:00 with Z
                created_at = created_at.replace("+00:00", "Z")
            elif not created_at.endswith("Z"):
                # Add Z if missing
                created_at = created_at + "Z"
            return created_at
        
        # Case 5: None or other unexpected types
        logger.warning(f"⚠️ Unexpected created_at type: {type(created_at)} value: {created_at}")
        return datetime.utcnow().isoformat() + "Z"
        
    except Exception as e:
        # Fallback for any corrupted values
        logger.warning(f"⚠️ Failed to normalize created_at {created_at}: {e}, using current time")
        return datetime.utcnow().isoformat() + "Z"


async def get_user_wardrobe(user_id: str) -> List[Dict[str, Any]]:
    """Get user's wardrobe items from Firestore."""
    try:
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ...config.firebase import db, firebase_initialized
            FIREBASE_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"⚠️ Firebase import failed: {e}")
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, returning empty wardrobe")
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
            
        logger.info(f"📦 Fetching wardrobe for user {user_id}")
        
        # Query user's wardrobe items - use the same path as the wardrobe page
        wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
        docs = wardrobe_ref.stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            
            # Defensive normalization for older items
            try:
                from ...utils.semantic_normalization import normalize_item_metadata
                normalized_item = normalize_item_metadata(item_data)
                items.append(normalized_item)
            except Exception as e:
                logger.warning(f"Failed to normalize item {doc.id}: {e}")
                items.append(item_data)  # Fallback to original item
        
        logger.info(f"✅ Retrieved {len(items)} wardrobe items")
        return items
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch wardrobe for {user_id}: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to fetch wardrobe: {e}")


async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user's style profile from Firestore."""
    try:
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ...config.firebase import db, firebase_initialized
            FIREBASE_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"⚠️ Firebase import failed: {e}")
            FIREBASE_AVAILABLE = False
            firebase_initialized = False
        
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, using default profile")
            # Return default profile instead of throwing error
            return {
                "id": user_id,
                "gender": "male",  # Default to male for better filtering
                "bodyType": "average",
                "skinTone": "medium",
                "style": ["casual", "versatile"],
                "stylePreferences": ["classic", "modern", "business casual"],  # Default style preferences
                "preferences": {},
                "colorPalette": {
                    "primary": ["navy", "gray", "black", "white"],
                    "secondary": ["blue", "brown", "beige"],
                    "avoid": ["pink", "purple", "yellow"]
                },
                "materialPreferences": {
                    "preferred": ["cotton", "wool", "linen"],
                    "avoid": ["polyester", "acrylic"]
                }
            }
            
        logger.info(f"👤 Fetching profile for user {user_id}")
        
        # Query user's profile
        profile_ref = db.collection('users').document(user_id)
        profile_doc = profile_ref.get() if profile_ref else None
        
        if profile_doc and profile_doc.exists:
            profile_data = profile_doc.to_dict()
            logger.info(f"✅ Retrieved profile for user {user_id}")
            
            # CRITICAL: Ensure gender is set - if missing or null, default to male
            if not (profile_data.get('gender') if profile_data else None):
                profile_data['gender'] = 'male'
                logger.info(f"🔧 Setting missing gender to 'male' for user {user_id}")
                
            return profile_data
        else:
            logger.info(f"⚠️ No profile found for user {user_id}, using defaults")
            # Return default profile instead of throwing error
            return {
                "id": user_id,
                "gender": "male",  # Default to male for better filtering
                "bodyType": "average",
                "skinTone": "medium",
                "style": ["casual", "versatile"],
                "stylePreferences": ["classic", "modern", "business casual"],
                "preferences": {},
                "colorPalette": {
                    "primary": ["navy", "gray", "black", "white"],
                    "secondary": ["blue", "brown", "beige"],
                    "avoid": ["pink", "purple", "yellow"]
                },
                "materialPreferences": {
                    "preferred": ["cotton", "wool", "linen"],
                    "avoid": ["polyester", "acrylic"]
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Failed to fetch profile for {user_id}: {e}")
        # Return default profile instead of throwing error
        return {
            "id": user_id,
            "gender": "male",
            "bodyType": "average",
            "skinTone": "medium",
            "style": ["casual", "versatile"],
            "stylePreferences": ["classic", "modern", "business casual"],
            "preferences": {},
            "colorPalette": {
                "primary": ["navy", "gray", "black", "white"],
                "secondary": ["blue", "brown", "beige"],
                "avoid": ["pink", "purple", "yellow"]
            },
            "materialPreferences": {
                "preferred": ["cotton", "wool", "linen"],
                "avoid": ["polyester", "acrylic"]
            }
        }


async def save_outfit(user_id: str, outfit_id: str, outfit_record: Dict[str, Any]) -> bool:
    """Save outfit to Firestore."""
    try:
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ...config.firebase import db, firebase_initialized
            FIREBASE_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"⚠️ Firebase import failed: {e}")
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, skipping save")
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
            
        logger.info(f"💾 Saving outfit {outfit_id} for user {user_id}")
        
        # Save to main outfits collection with user_id field (consistent with fetching)
        outfits_ref = db.collection('outfits')
        doc_ref = outfits_ref.document(outfit_id)
        
        try:
            # CRITICAL FIX: Wrap Firestore operation in try/catch to catch silent failures
            doc_ref.set(outfit_record)
        except Exception as firestore_error:
            logger.error(f"💾 Firestore set() FAILED with exception: {firestore_error}")
            raise firestore_error
        
        # Verify the write by immediately reading it back
        verification_doc = doc_ref.get() if doc_ref else None
        if not verification_doc or not verification_doc.exists:
            logger.error(f"❌ VERIFICATION FAILED: Document does NOT exist after save!")
            return False
        
        logger.info(f"✅ Successfully saved outfit {outfit_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save outfit {outfit_id}: {e}")
        logger.error(f"❌ Exception type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to save outfit: {e}")


async def resolve_item_ids_to_objects(items: List[Any], user_id: str, wardrobe_cache: Dict[str, Dict] = None) -> List[Dict[str, Any]]:
    """
    Resolve item IDs to actual item objects from the wardrobe collection.
    If an item is already a dictionary, return it as is.
    If an item is a string ID, fetch the item from the wardrobe collection.
    
    Args:
        items: List of item IDs or item objects
        user_id: User ID for the wardrobe
        wardrobe_cache: Optional cache of wardrobe items to avoid repeated queries
    """
    resolved_items = []
    
    # Import Firebase inside function
    try:
        from ...config.firebase import db, firebase_initialized
    except ImportError:
        logger.warning("Firebase not available, returning mock items")
        firebase_initialized = False
    
    # If Firebase is not available, return mock items
    if not firebase_initialized:
        logger.warning("Firebase not available, returning mock items")
        for item in items:
            if isinstance(item, dict):
                # Fix imageUrl even for existing items
                item_copy = item.copy()
                raw_url = item_copy.get('imageUrl', '') or item_copy.get('image_url', '') or item_copy.get('image', '')
                item_copy['imageUrl'] = convert_firebase_url(raw_url)
                resolved_items.append(item_copy)
            else:
                resolved_items.append({
                    'id': str(item),
                    'name': 'Mock Item',
                    'type': 'shirt',
                    'imageUrl': None
                })
        return resolved_items
    
    # Collect unique item IDs that need to be fetched
    item_ids_to_fetch = []
    for item in items:
        if isinstance(item, dict):
            # Item is already a complete object - fix imageUrl
            item_copy = item.copy()
            raw_url = item_copy.get('imageUrl', '') or item_copy.get('image_url', '') or item_copy.get('image', '')
            item_copy['imageUrl'] = convert_firebase_url(raw_url)
            resolved_items.append(item_copy)
        elif isinstance(item, str):
            if wardrobe_cache and item in wardrobe_cache:
                # Use cached item - fix imageUrl
                cached_item = wardrobe_cache[item].copy()
                raw_url = cached_item.get('imageUrl', '') or cached_item.get('image_url', '') or cached_item.get('image', '')
                cached_item['imageUrl'] = convert_firebase_url(raw_url)
                resolved_items.append(cached_item)
            else:
                # Need to fetch this item
                item_ids_to_fetch.append(item)
    
    # Fetch items that aren't in cache
    if item_ids_to_fetch:
        try:
            for item_id in item_ids_to_fetch:
                try:
                    item_ref = db.collection('wardrobe').document(item_id)
                    item_doc = item_ref.get() if item_ref else None
                    if item_doc and item_doc.exists:
                        item_data = item_doc.to_dict()
                        item_data['id'] = item_doc.id
                        # Fix imageUrl
                        raw_url = item_data.get('imageUrl', '') or item_data.get('image_url', '') or item_data.get('image', '')
                        item_data['imageUrl'] = convert_firebase_url(raw_url)
                        resolved_items.append(item_data)
                    else:
                        logger.warning(f"⚠️ Item {item_id} not found in wardrobe")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to fetch item {item_id}: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to fetch items: {e}")
    
    return resolved_items


async def get_user_outfits(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Get user outfits from Firestore with pagination."""
    # Temporary: Increase limit to show more outfits
    limit = min(limit, 200)
    logger.info(f"🔍 DEBUG: Fetching outfits for user {user_id} (limit={limit}, offset={offset})")
    
    try:
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ...config.firebase import db, firebase_initialized
            FIREBASE_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"⚠️ Firebase import failed: {e}")
            return []
        
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, returning empty outfits")
            return []
            
        logger.info(f"📚 DEBUG: About to query Firestore collection('outfits') with user_id == '{user_id}'")
        
        # FIXED: Query main outfits collection with user_id field (snake_case)
        # This matches the Pydantic model and outfit creation code
        outfits_ref = db.collection("outfits").where("user_id", "==", user_id)
        
        # CRITICAL FIX: Use proper Firestore ordering to get newest outfits first
        use_firestore_ordering = True
        try:
            from firebase_admin import firestore
            outfits_ref = outfits_ref.order_by("createdAt", direction=firestore.Query.DESCENDING)
            logger.info("✅ DEBUG: Using Firestore server-side ordering by createdAt DESC")
        except Exception as e:
            logger.warning(f"⚠️ DEBUG: Firestore ordering failed ({e}), will use client-side sorting")
            use_firestore_ordering = False
        
        # Apply pagination based on whether ordering worked
        # Always fetch a small buffer to ensure custom outfits are included even if Firestore ordering differs
        fetch_limit = limit + offset + 50
        fetch_limit = min(max(fetch_limit, limit), 250)
        
        if use_firestore_ordering:
            outfits_ref = outfits_ref.limit(fetch_limit)
        else:
            outfits_ref = outfits_ref.limit(min(fetch_limit, 250))
        
        logger.info(f"🔍 DEBUG: Firestore query: limit={limit}, offset={offset}")
        
        # Execute query with error handling to prevent timeout
        try:
            logger.info(f"🔍 DEBUG: Executing Firestore query with .stream()...")
            docs = outfits_ref.stream()
            logger.info(f"🔍 DEBUG: Firestore query executed successfully, processing results...")
        except Exception as e:
            logger.error(f"🔥 Firestore query failed: {e}", exc_info=True)
            return []  # Return empty list instead of crashing
        
        # First pass: collect outfit data
        outfits = []
        for doc in docs:
            try:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                
                # Compute consistent milliseconds timestamp
                raw_created_at = (
                    outfit_data.get('createdAt')
                    or outfit_data.get('created_at_timestamp')
                    or outfit_data.get('created_at_ms')
                )
                created_at_ms = compute_created_at_ms(raw_created_at)
                outfit_data['created_at_ms'] = created_at_ms
                
                # Backfill missing milliseconds field in Firestore for future ordering
                if not outfit_data.get('created_at_ms'):
                    try:
                        doc.reference.update({"created_at_ms": created_at_ms})
                    except Exception as update_error:
                        logger.debug(f"🔁 DEBUG: Skipped created_at_ms backfill for {doc.id}: {update_error}")
                
                # Normalize timestamp immediately to prevent later errors
                outfit_data['createdAt'] = normalize_created_at(raw_created_at)
                
                outfits.append(outfit_data)
                logger.info(f"🔍 DEBUG: Found outfit: {outfit_data.get('name', 'unnamed')} (ID: {doc.id}, Created: {outfit_data.get('createdAt', 'Unknown')})")
                logger.info(f"🔍 DEBUG: Outfit {doc.id} wearCount: {outfit_data.get('wearCount', 'NOT_FOUND')}, lastWorn: {outfit_data.get('lastWorn', 'NOT_FOUND')}")
                logger.info(f"🔍 DEBUG: Outfit {doc.id} all fields: {list(outfit_data.keys())}")
            except Exception as e:
                logger.error(f"🔥 Failed to process outfit {doc.id}: {e}", exc_info=True)
                # Skip this outfit instead of crashing the whole request
                continue
        
        if outfits:
            logger.info(f"🔍 DEBUG: First outfit in results: {outfits[0].get('name')} - {outfits[0].get('createdAt')}")
            logger.info(f"🔍 DEBUG: Last outfit in results: {outfits[-1].get('name')} - {outfits[-1].get('createdAt')}")
        
        # Optimization: Fetch user's wardrobe once for all outfits (only if reasonable size)
        if len(outfits) <= 100:  # Only cache for reasonable dataset sizes
            logger.info(f"🔍 DEBUG: Fetching wardrobe cache for batch item resolution...")
            try:
                wardrobe_docs = db.collection('wardrobe').where('userId', '==', user_id).stream()
                wardrobe_cache = {}
                for doc in wardrobe_docs:
                    item_data = doc.to_dict()
                    item_data['id'] = doc.id
                    wardrobe_cache[doc.id] = item_data
                logger.info(f"✅ DEBUG: Cached {len(wardrobe_cache)} wardrobe items")
            except Exception as e:
                logger.warning(f"⚠️ Could not cache wardrobe: {e}, will fetch items individually")
                wardrobe_cache = None
        else:
            logger.info(f"⚠️ DEBUG: Skipping wardrobe cache for {len(outfits)} outfits (too many for performance)")
            wardrobe_cache = None
        
        # Always apply client-side sorting to ensure consistency across mixed timestamp types
        outfits.sort(key=lambda x: x.get('created_at_ms', 0), reverse=True)
        
        # Apply pagination in application layer
        start_idx = offset
        end_idx = offset + limit
        outfits = outfits[start_idx:end_idx]
        logger.info(f"✅ DEBUG: Client-side sorted and paginated to {len(outfits)} outfits (offset={offset}, limit={limit})")
        
        # Final pass: resolve items using cache (reduced logging)
        for outfit_data in outfits:
            if 'items' in outfit_data and outfit_data['items']:
                try:
                    outfit_data['items'] = await resolve_item_ids_to_objects(outfit_data['items'], user_id, wardrobe_cache)
                except Exception as e:
                    logger.error(f"🔥 Failed to resolve items for outfit {outfit_data.get('id')}: {e}")
                    outfit_data['items'] = []  # Set empty items instead of crashing
        
        if outfits:
            logger.info(f"🔍 DEBUG: First outfit: {outfits[0].get('name')} - {outfits[0].get('createdAt')}")
            logger.info(f"🔍 DEBUG: Last outfit: {outfits[-1].get('name')} - {outfits[-1].get('createdAt')}")
        
        logger.info(f"✅ DEBUG: Successfully retrieved {len(outfits)} outfits from Firestore for user {user_id}")
        return outfits
        
    except Exception as e:
        logger.error(f"❌ ERROR: Failed to fetch outfits from Firestore: {e}", exc_info=True)
        logger.error(f"❌ ERROR: Exception type: {type(e)}")
        logger.error(f"❌ ERROR: Exception details: {str(e)}")
        import traceback
        logger.error(f"❌ ERROR: Full traceback: {traceback.format_exc()}")
        # Return empty list instead of raising exception to prevent timeout
        return []


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

