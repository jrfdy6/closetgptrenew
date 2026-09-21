"""
Database operations for outfit management.
Handles all Firestore operations for outfits, wardrobe, and user profiles.
"""

import logging
import re
import time
import urllib.parse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from fastapi import HTTPException

logger = logging.getLogger(__name__)


def outfit_belongs_to_user(outfit: Dict[str, Any], user_id: str) -> bool:
    """Accept either historical owner field, but never conflicting owners."""
    owners = [outfit[key] for key in ('user_id', 'userId') if outfit.get(key) is not None]
    return bool(user_id) and bool(owners) and all(owner == user_id for owner in owners)


_MAX_OUTFIT_PAGE_END = 250
_OUTFIT_COHORT_LIMIT = 301
_OUTFIT_FALLBACK_LIMIT = 251
_ISO_CREATED_AT = re.compile(
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}|\+00:00Z)?$'
)


def _get_owned_outfit_documents(db, user_id: str, required_count: int):
    """Merge bounded chronological cohorts, never a partial unordered sample.

    Firestore inequality filters compare matching types (numbers share a type).
    These four ranges reuse owner + createdAt DESC indexes. Extended ISO strings,
    Firestore dates, numeric seconds and numeric milliseconds therefore cannot
    crowd one another out before normalization. Missing createdAt remains
    excluded, just as it is by Firestore order_by.

    At most 4*301 returned documents per owner plus 251 if a query fails
    (including a partial stream) and needs fallback: <=2910 outfit reads total.
    No cursor, offset scan, backfill, or index migration is required.
    """
    from firebase_admin import firestore

    documents = {}
    cohorts = (
        ('iso', (('>=', ''),)),
        ('timestamp', (('>=', datetime.min.replace(tzinfo=timezone.utc)),)),
        ('seconds', (('<=', 1e12),)),
        ('milliseconds', (('>', 1e12),)),
    )
    for owner_field in ('user_id', 'userId'):
        query = db.collection('outfits').where(owner_field, '==', user_id)
        owner_documents = {}
        try:
            for kind, bounds in cohorts:
                cohort = query
                for operator, value in bounds:
                    cohort = cohort.where('createdAt', operator, value)
                # Consume here: missing-index errors also occur on iteration.
                results = list(cohort.order_by(
                    'createdAt', direction=firestore.Query.DESCENDING
                ).limit(_OUTFIT_COHORT_LIMIT).stream())
                owned = [document for document in results
                         if outfit_belongs_to_user(document.to_dict() or {}, user_id)]
                if len(results) == _OUTFIT_COHORT_LIMIT:
                    # Overscan is bounded. If conflicting owners, timestamp
                    # ties, or ISO spelling differences prevent establishing
                    # the newest requested prefix, fail instead of truncating.
                    newest = sorted(
                        (compute_created_at_ms(doc.to_dict()['createdAt']) for doc in owned),
                        reverse=True,
                    )
                    boundary = results[-1].to_dict()['createdAt']
                    unread_ceiling = compute_created_at_ms(boundary)
                    if kind == 'iso':
                        # Extended ISO sorts by wall-clock whole second, not
                        # UTC instant. An unseen row can have a negative offset
                        # even when this entire prefix uses UTC. Python ISO
                        # offsets are strictly under 24h; add that envelope and
                        # the remaining fraction of the boundary second.
                        for document in results:
                            value = document.to_dict()['createdAt']
                            if not _ISO_CREATED_AT.fullmatch(value):
                                raise HTTPException(status_code=503, detail='Outfit timestamp ordering unavailable')
                            datetime.fromisoformat(value.replace('+00:00Z', 'Z').replace('Z', '+00:00'))
                        unread_ceiling = compute_created_at_ms(boundary[:19]) + 86_400_999
                    if len(newest) < required_count or newest[required_count - 1] <= unread_ceiling:
                        raise HTTPException(status_code=503, detail='Outfit listing exceeds safe read limit')
                owner_documents.update((document.id, document) for document in owned)
        except HTTPException:
            raise
        except Exception as error:
            logger.warning('Outfit ordering unavailable for %s; checking complete bounded owner set: %s', owner_field, error)
            results = list(query.limit(_OUTFIT_FALLBACK_LIMIT).stream())
            if len(results) == _OUTFIT_FALLBACK_LIMIT:
                raise HTTPException(status_code=503, detail='Outfit ordering unavailable; owner set exceeds safe read limit')
            owner_documents = {
                document.id: document for document in results
                if (document.to_dict() or {}).get('createdAt') is not None
                and outfit_belongs_to_user(document.to_dict() or {}, user_id)
            }
        documents.update(owner_documents)
    return documents.values()

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
                parsed = datetime.fromisoformat(created_at.replace('+00:00Z', 'Z').replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return int(parsed.timestamp() * 1000)
            except Exception:
                return int(time.time() * 1000)
        
        if FIRESTORE_TIMESTAMP_AVAILABLE and isinstance(created_at, DatetimeWithNanoseconds):
            return int(created_at.timestamp() * 1000)
        
        if isinstance(created_at, datetime):
            aware_created_at = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
            return int(aware_created_at.timestamp() * 1000)
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to compute created_at_ms from {created_at}: {e}")
    
    return int(time.time() * 1000)


def normalize_created_at(created_at) -> str:
    """Safely normalize Firestore created_at into ISO8601 string."""
    try:
        # Case 1: Firestore Timestamp object (DatetimeWithNanoseconds)
        if FIRESTORE_TIMESTAMP_AVAILABLE and isinstance(created_at, DatetimeWithNanoseconds):
            return created_at.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # Case 2: Python datetime object
        if isinstance(created_at, datetime):
            aware_created_at = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
            return aware_created_at.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
        
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
    if limit < 1 or offset < 0:
        raise HTTPException(status_code=422, detail='Outfit limit must be positive and offset nonnegative')
    limit = min(limit, 200)
    if offset + limit > _MAX_OUTFIT_PAGE_END:
        raise HTTPException(status_code=422, detail='Outfit pagination supports the newest 250 outfits')
    logger.info(f"🔍 DEBUG: Fetching outfits for user {user_id} (limit={limit}, offset={offset})")
    
    try:
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ...config.firebase import db, firebase_initialized
            FIREBASE_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"⚠️ Firebase import failed: {e}")
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        if not FIREBASE_AVAILABLE or not firebase_initialized or db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
            
        # Keep reads bounded, including the legacy manual-save owner spelling.
        docs = _get_owned_outfit_documents(db, user_id, limit + offset)
        
        # First pass: collect outfit data
        outfits = []
        for doc in docs:
            try:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                outfit_data['user_id'] = user_id
                # Preserve an explicit false value when an older favorite alias
                # still exists on the document.
                if outfit_data.get('isFavorite') is None:
                    outfit_data['isFavorite'] = bool(outfit_data.get('favorite', False))
                
                # Compute consistent milliseconds timestamp
                raw_created_at = (
                    outfit_data.get('createdAt')
                    or outfit_data.get('created_at_timestamp')
                    or outfit_data.get('created_at_ms')
                )
                created_at_ms = compute_created_at_ms(raw_created_at)
                outfit_data['created_at_ms'] = created_at_ms
                
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
        outfits.sort(key=lambda x: (x.get('created_at_ms', 0), x['id']), reverse=True)
        
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
        
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to fetch outfits from Firestore")
        raise HTTPException(status_code=500, detail="Failed to fetch outfits")


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
