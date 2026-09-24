from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any, Optional
from types import SimpleNamespace
from firebase_admin import firestore
import uuid
import time
from datetime import datetime
import logging
import traceback

from .wardrobe_update_contract import build_wardrobe_update
from ..auth.verified_identity import verified_identity, reject_identity_overrides

# Import production monitoring
try:
    from ..services.production_monitoring_service import (
        monitoring_service,
        OperationType,
        UserJourneyStep
    )
    MONITORING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Production monitoring import failed: {e}")
    MONITORING_AVAILABLE = False
    monitoring_service = None

# Set up basic logging
logger = logging.getLogger(__name__)
# Router loaded - force redeploy

# Import safe_get helper
try:
    from ..services.robust_outfit_generation_service import safe_get
except ImportError:
    def safe_get(obj, key, default=None):
        """Fallback safe_get if import fails"""
        if isinstance(obj, dict):
            return (obj.get(key, default) if obj else default)
        return getattr(obj, key, default)

# Optional imports with graceful fallbacks
try:
    from ..custom_types.wardrobe import ClothingItem, ClothingType, Color
    CUSTOM_TYPES_AVAILABLE = True
    pass  # Custom types imported
except ImportError as e:
    logger.warning(f"⚠️ Custom wardrobe types import failed: {e}")
    CUSTOM_TYPES_AVAILABLE = False
    # Create basic fallback types
    from typing import TypedDict
    class ClothingItem(TypedDict):
        id: str
        name: str
        type: str
        color: str
        userId: str
    ClothingType = str
    Color = str

try:
    from ..custom_types.profile import UserProfile
    PROFILE_TYPES_AVAILABLE = True
    pass  # Profile types imported
except ImportError as e:
    logger.warning(f"⚠️ Profile types import failed: {e}")
    PROFILE_TYPES_AVAILABLE = False
    from typing import TypedDict
    class UserProfile(TypedDict):
        id: str
        name: str
        email: str

# Metadata service will be instantiated inside functions to prevent import-time crashes
try:
    from ..services.metadata_enhancement_service import MetadataEnhancementService
    METADATA_SERVICE_AVAILABLE = True
    pass  # Metadata service imported
except ImportError as e:
    logger.warning(f"⚠️ Metadata enhancement service import failed: {e}")
    METADATA_SERVICE_AVAILABLE = False
    MetadataEnhancementService = None

def get_metadata_service():
    """Get metadata service instance, creating it when needed"""
    if METADATA_SERVICE_AVAILABLE and MetadataEnhancementService:
        try:
            return MetadataEnhancementService()
        except Exception as e:
            logger.warning(f"Failed to create metadata service: {e}")
            return None
    return None

try:
    from ..core.logging import get_logger
    logger = get_logger("wardrobe")
    CORE_LOGGING_AVAILABLE = True
    pass  # Core logging imported
except ImportError as e:
    logger.warning(f"⚠️ Core logging import failed: {e}")
    CORE_LOGGING_AVAILABLE = False
    logger = logging.getLogger(__name__)

try:
    from ..models.analytics_event import AnalyticsEvent
    from ..services.analytics_service import log_analytics_event
    ANALYTICS_AVAILABLE = True
    pass  # Analytics imported
except ImportError as e:
    logger.warning(f"⚠️ Analytics services import failed: {e}")
    ANALYTICS_AVAILABLE = False
    def log_analytics_event(*args, **kwargs):
        pass  # No-op fallback

async def verified_wardrobe_user(request: Request, claims: dict = Depends(verified_identity)):
    # All wardrobe operations use the verified token; body aliases are only
    # compatibility hints and cannot choose a different owner.
    if request.method in {'POST', 'PUT', 'PATCH'}:
        try:
            body = await request.json()
        except ValueError:
            body = None  # The route's body validation reports malformed JSON.
        if isinstance(body, dict):
            reject_identity_overrides(claims, body)
    return SimpleNamespace(id=claims['uid'])


def _owned_wardrobe_item(data, user_id):
    owners = [data[key] for key in ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId')
              if data.get(key) is not None]
    return bool(owners) and all(isinstance(owner, str) and owner == user_id for owner in owners)

try:
    from ..services.ai_runtime import merge_completed_upload_analysis_into_item_data
except ImportError:
    def merge_completed_upload_analysis_into_item_data(*, requested_by: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        return item_data

# Remove prefix since app.py will mount it at /api/wardrobe
router = APIRouter(tags=["wardrobe"])

# Initialize Firestore conditionally
try:
    db = firestore.client()
    FIREBASE_AVAILABLE = True
    pass  # Firebase initialized
except Exception as e:
    logger.warning(f"⚠️ Firebase client initialization failed: {e}")
    db = None
    FIREBASE_AVAILABLE = False

# Removed conflicting /wardrobe-stats endpoint - using the one in wardrobe_analysis.py instead

@router.get("/debug-test")
async def debug_test():
    return {"status": "ok", "message": "Router loading test endpoint"}

@router.get("/top-worn-items")
async def get_top_worn_items(
    current_user: Optional[UserProfile] = Depends(verified_wardrobe_user),
    limit: int = 10
) -> Dict[str, Any]:
    """Get the top worn wardrobe items for the current user."""
    try:
        if not FIREBASE_AVAILABLE or not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Query all wardrobe items for the user, ordered by wear count
        from src.services.wardrobe_reads import owned_wardrobe_documents
        from starlette.concurrency import run_in_threadpool
        docs = await run_in_threadpool(owned_wardrobe_documents, db, current_user.id)
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            items.append(item_data)
        
        # Sort by wear count (descending) and take top items
        items.sort(key=lambda x: safe_get(x, 'wearCount', 0), reverse=True)
        top_items = items[:limit]
        
        # Calculate statistics
        total_items = len(items)
        total_wear_count = sum(safe_get(item, 'wearCount', 0) for item in items)
        avg_wear_count = total_wear_count / total_items if total_items > 0 else 0
        
        # Get items with no wear (unworn items)
        unworn_items = [item for item in items if safe_get(item, 'wearCount', 0) == 0]
        
        # Legacy item actions use seconds; canonical outfit wears use
        # milliseconds. Apply the shared parser before comparing recency.
        from datetime import datetime, timedelta, timezone
        from src.services.wear_statistics import parse_wear_timestamp
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        recent_items = [item for item in items
                        if (worn_at := parse_wear_timestamp(item.get('lastWorn'))) is not None
                        and week_ago <= worn_at <= now]

        stats = {
            "total_items": total_items,
            "total_wear_count": total_wear_count,
            "avg_wear_count": round(avg_wear_count, 2),
            "unworn_items_count": len(unworn_items),
            "recently_worn_count": len(recent_items),
            "top_worn_items": [
                {
                    "id": item['id'],
                    "name": safe_get(item, 'name', 'Unknown'),
                    "type": safe_get(item, 'type', 'Unknown'),
                    "color": safe_get(item, 'color', 'Unknown'),
                    "wear_count": safe_get(item, 'wearCount', 0),
                    "last_worn": safe_get(item, 'lastWorn'),
                    "is_favorite": safe_get(item, 'isFavorite', False),
                    "image_url": safe_get(item, 'imageUrl') or safe_get(item, 'image_url') or safe_get(item, 'image')
                }
                for item in top_items
            ]
        }
        
        logger.info(f"Retrieved top worn items for user {current_user.id}: {len(top_items)} items")
        
        return {
            "success": True,
            "data": stats,
            "message": f"Top worn items retrieved successfully ({len(top_items)} items found)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting top worn items: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving top worn items: {str(e)}")

@router.get("/most-worn-by-category")
async def get_most_worn_by_category(
    current_user: UserProfile = Depends(verified_wardrobe_user)
) -> Dict[str, Any]:
    """Get the most worn items organized by category (tops, bottoms, shoes, etc.)."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Query all wardrobe items for the user
        from src.services.wardrobe_reads import owned_wardrobe_documents
        from starlette.concurrency import run_in_threadpool
        docs = await run_in_threadpool(owned_wardrobe_documents, db, current_user.id)
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            items.append(item_data)
        
        # Group items by category
        categories = {}
        for item in items:
            item_type = (item.get('type', 'Unknown') if item else 'Unknown').lower()
            
            # Map item types to categories
            if any(word in item_type for word in ['shirt', 'blouse', 'sweater', 'jacket', 'coat', 'hoodie', 'tank', 'tee']):
                category = 'tops'
            elif any(word in item_type for word in ['pants', 'jeans', 'shorts', 'skirt', 'leggings', 'trousers']):
                category = 'bottoms'
            elif any(word in item_type for word in ['shoes', 'boots', 'sneakers', 'heels', 'flats', 'sandals']):
                category = 'shoes'
            elif any(word in item_type for word in ['dress', 'jumpsuit', 'romper']):
                category = 'dresses'
            elif any(word in item_type for word in ['accessory', 'jewelry', 'bag', 'scarf', 'hat', 'belt']):
                category = 'accessories'
            else:
                category = 'other'
            
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Get top worn item for each category
        most_worn_by_category = {}
        for category, category_items in categories.items():
            if category_items:
                # Sort by wear count and get the most worn
                category_items.sort(key=lambda x: (x.get('wearCount', 0) if x else 0), reverse=True)
                most_worn = category_items[0]
                
                most_worn_by_category[category] = {
                    "item": {
                        "id": most_worn['id'],
                        "name": (most_worn.get('name', 'Unknown') if most_worn else 'Unknown'),
                        "type": (most_worn.get('type', 'Unknown') if most_worn else 'Unknown'),
                        "color": (most_worn.get('color', 'Unknown') if most_worn else 'Unknown'),
                        "wear_count": (most_worn.get('wearCount', 0) if most_worn else 0),
                        "last_worn": (most_worn.get('lastWorn') if most_worn else None),
                        "image_url": (((most_worn.get('imageUrl') if most_worn else None) if most_worn else None) if most_worn else None) or most_worn.get('image_url') or most_worn.get('image')
                    },
                    "total_items": len(category_items),
                    "total_wear_count": sum((item.get('wearCount', 0) if item else 0) for item in category_items),
                    "avg_wear_count": sum((item.get('wearCount', 0) if item else 0) for item in category_items) / len(category_items) if category_items else 0
                }
        
        # Calculate overall statistics
        total_items = len(items)
        total_wear_count = sum((item.get('wearCount', 0) if item else 0) for item in items)
        
        stats = {
            "total_items": total_items,
            "total_wear_count": total_wear_count,
            "avg_wear_count": round(total_wear_count / total_items, 2) if total_items > 0 else 0,
            "categories": most_worn_by_category
        }
        
        logger.info(f"Retrieved most worn by category for user {current_user.id}")
        
        return {
            "success": True,
            "data": stats,
            "message": "Most worn items by category retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting most worn by category: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving most worn by category: {str(e)}")

@router.get("/trending-styles")
async def get_trending_styles(
    current_user: UserProfile = Depends(verified_wardrobe_user)
) -> Dict[str, Any]:
    """Get trending styles based on user's wardrobe and preferences."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Query user's wardrobe items
        from src.services.wardrobe_reads import owned_wardrobe_documents
        from starlette.concurrency import run_in_threadpool
        docs = await run_in_threadpool(owned_wardrobe_documents, db, current_user.id)
        
        items = [{**doc.to_dict(), 'id': doc.id} for doc in docs]
        
        # Analyze style patterns
        style_counts = {}
        color_counts = {}
        type_counts = {}
        
        for item in items:
            # Count styles
            styles = (item.get('style', []) if item else [])
            if isinstance(styles, list):
                for style in styles:
                    style_counts[style] = (style_counts.get(style, 0) if style_counts else 0) + 1
            elif isinstance(styles, str):
                style_counts[styles] = (style_counts.get(styles, 0) if style_counts else 0) + 1
            
            # Count colors
            color = (item.get('color', 'unknown') if item else 'unknown')
            color_counts[color] = (color_counts.get(color, 0) if color_counts else 0) + 1
            
            # Count types
            item_type = (item.get('type', 'unknown') if item else 'unknown')
            type_counts[item_type] = (type_counts.get(item_type, 0) if type_counts else 0) + 1
        
        # Get top styles, colors, and types
        top_styles = sorted(style_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate trending score based on wear count and recency
        trending_items = []
        for item in items:
            if item.get('wearCount', 0) > 0:
                score = item.get('wearCount', 0)
                if item.get('lastWorn'):
                    from src.services.wear_statistics import parse_wear_timestamp
                    worn_at = parse_wear_timestamp(item['lastWorn'])
                    if worn_at is not None:
                        days_since_worn = (time.time() - worn_at.timestamp()) / (24 * 60 * 60)
                        if 0 <= days_since_worn < 7:
                            score += 2
                        elif 0 <= days_since_worn < 30:
                            score += 1
                trending_items.append({
                    'id': (item.get('id') if item else None),
                    'name': (item.get('name') if item else None),
                    'type': (item.get('type') if item else None),
                    'color': (item.get('color', 'unknown') if item else 'unknown'),
                    'style': (item.get('style', []) if item else []),
                    'trending_score': score,
                    'wear_count': (item.get('wearCount', 0) if item else 0)
                })
        
        # Sort by trending score
        trending_items.sort(key=lambda x: x['trending_score'], reverse=True)
        top_trending = trending_items[:10]
        
        result = {
            "top_styles": [{"style": style, "count": count} for style, count in top_styles],
            "top_colors": [{"color": color, "count": count} for color, count in top_colors],
            "top_types": [{"type": type_name, "count": count} for type_name, count in top_types],
            "trending_items": top_trending,
            "total_items_analyzed": len(items),
            "user_id": current_user.id
        }
        
        logger.info(f"Retrieved trending styles for user {current_user.id}: {len(items)} items analyzed")
        
        return {
            "success": True,
            "data": result,
            "message": "Trending styles retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trending styles: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving trending styles: {str(e)}")

@router.post("/add")
async def add_wardrobe_item(
    item_data: Dict[str, Any],
    current_user: UserProfile = Depends(verified_wardrobe_user)
) -> Dict[str, Any]:
    """Compatibility alias for the canonical transactional upload writer."""
    from src.services.wardrobe_persistence import create_owned_wardrobe_item, WardrobeOwnershipConflict, WardrobeInputError
    from src.services.app_data_privacy import AppDataDeletionError
    from starlette.concurrency import run_in_threadpool
    try:
        item = await run_in_threadpool(create_owned_wardrobe_item, db, current_user.id, item_data)
        try:
            from src.services.challenge_actions import refresh_action_rewards
            await refresh_action_rewards(current_user.id, expected_epoch=item.get('app_data_epoch', 0), include_upload_milestones=True)
        except Exception:
            logger.exception('Item saved; wardrobe rewards will be reconciled by maintenance')
        return {"success": True, "item_id": item['id'], "item": item, "message": "Item saved"}
    except AppDataDeletionError as error:
        raise HTTPException(error.status_code, error.detail) from None
    except WardrobeOwnershipConflict:
        raise HTTPException(409, 'This item ID is already in use') from None
    except WardrobeInputError as error:
        raise HTTPException(422, str(error)) from None

@router.get("/test", include_in_schema=False)
async def test_wardrobe_endpoint() -> Dict[str, Any]:
    """Simple test endpoint to verify the wardrobe endpoint is working."""
    return {
        "success": True,
        "message": "Wardrobe endpoint is working",
        "timestamp": "2024-01-01T00:00:00Z",
        "backend": "closetgptrenew-production"
    }

@router.get("/count", include_in_schema=False)
async def count_wardrobe_items(current_user: UserProfile = Depends(verified_wardrobe_user)) -> Dict[str, Any]:
    """Count only the signed-in account's active saved garments."""
    from src.services.wardrobe_reads import owned_wardrobe_documents
    from src.config.firebase import db, firebase_initialized
    from starlette.concurrency import run_in_threadpool
    if db is None or not firebase_initialized:
        raise HTTPException(503, 'Wardrobe temporarily unavailable')
    try:
        documents = await run_in_threadpool(owned_wardrobe_documents, db, current_user.id)
        count = len(documents)
        return {'success': True, 'total_items': count, 'message': f'Found {count} items in your wardrobe'}
    except Exception:
        raise HTTPException(503, 'Wardrobe count could not be confirmed') from None

@router.get("/debug", include_in_schema=False)
async def debug_wardrobe_data() -> Dict[str, Any]:
    """Debug endpoint to check what's actually in the wardrobe collection."""
    try:
        from src.config.firebase import firebase_initialized, db
        
        if not firebase_initialized or db is None:
            return {"error": "Firebase not initialized"}
        
        # Get ALL documents in wardrobe collection (no limit)
        all_docs = db.collection('wardrobe').stream()
        
        items = []
        user_ids_found = set()
        total_count = 0
        
        for doc in all_docs:
            total_count += 1
            data = doc.to_dict()
            data['id'] = doc.id
            
            # Check all possible user ID field names
            user_id = ((((data.get('userId') if data else None) if data else None) if data else None) if data else None) or data.get('uid') or data.get('ownerId') or data.get('user_id')
            if user_id:
                user_ids_found.add(user_id)
            
            # Only include first 10 items for response size
            if len(items) < 10:
                items.append({
                    'id': doc.id,
                    'userId': (data.get('userId', 'NOT_FOUND') if data else 'NOT_FOUND'),
                    'uid': (data.get('uid', 'NOT_FOUND') if data else 'NOT_FOUND'),
                    'ownerId': (data.get('ownerId', 'NOT_FOUND') if data else 'NOT_FOUND'),
                    'user_id': (data.get('user_id', 'NOT_FOUND') if data else 'NOT_FOUND'),
                    'name': (data.get('name', 'NO_NAME') if data else 'NO_NAME'),
                    'keys': list(data.keys())
                })
        
        return {
            "success": True,
            "total_items_in_database": total_count,
            "user_ids_in_collection": list(user_ids_found),
            "sample_items": items,
            "message": f"Found {total_count} total items in database"
        }
        
    except Exception as e:
        return {"error": str(e)}



@router.get("/")
async def get_wardrobe_items_with_slash(
    current_user: UserProfile = Depends(verified_wardrobe_user)
) -> Dict[str, Any]:
    """Get all wardrobe items for the current user."""
    import time
    start_time = time.time()
    logger.info(f"🚀 WARDROBE ENDPOINT: Request received for user: {current_user.id}")
    
    try:
        # Check Firebase initialization status
        logger.info(f"⏱️ WARDROBE: Checking Firebase initialization... ({time.time() - start_time:.2f}s)")
        from src.config.firebase import firebase_initialized, db
        logger.info(f"⏱️ WARDROBE: Firebase import complete ({time.time() - start_time:.2f}s)")
        
        if not firebase_initialized or db is None:
            logger.error(f"❌ WARDROBE: Firebase not initialized")
            raise HTTPException(
                status_code=500, 
                detail="Database connection not available. Firebase may not be properly configured."
            )
        
        logger.info(f"⏱️ WARDROBE: Starting Firestore query for user: {current_user.id} ({time.time() - start_time:.2f}s)")
        
        from src.services.wardrobe_reads import owned_wardrobe_documents
        from starlette.concurrency import run_in_threadpool
        items_list = await run_in_threadpool(owned_wardrobe_documents, db, current_user.id)

        # OPTIMIZED: Process items in single pass with efficient defaults
        from src.services.garment_lifecycle import ERRORS as garment_processing_errors

        current_time = int(time.time())
        transformed_items = []
        errors = []
        
        for doc in items_list:
            try:
                item_data = doc.to_dict() or {}
                if not _owned_wardrobe_item(item_data, current_user.id):
                    continue
                doc_id = doc.id
                
                # Efficient timestamp conversion helper
                def convert_timestamp(ts_value, default):
                    if not ts_value:
                        return default
                    if isinstance(ts_value, (int, float)):
                        return int(ts_value)
                    if hasattr(ts_value, 'timestamp'):
                        return int(ts_value.timestamp())
                    if isinstance(ts_value, str):
                        try:
                            return int(datetime.fromisoformat(ts_value.replace('Z', '+00:00')).timestamp())
                        except:
                            return default
                    return default
                
                # Build transformed item in one pass with efficient defaults
                # Convert lastWorn timestamp if present
                last_worn = item_data.get('lastWorn')
                if last_worn:
                    last_worn = convert_timestamp(last_worn, None)
                
                transformed_item = {
                    "id": doc_id,
                    "name": item_data.get('name', 'Unknown Item'),
                    "type": item_data.get('type', 'unknown'),
                    "color": item_data.get('color', 'unknown'),
                    # A display placeholder is not a saved original and must not
                    # satisfy capsule readiness after the wardrobe is reloaded.
                    "imageUrl": next((value.strip() for value in (
                        item_data.get('imageUrl'), item_data.get('image_url'), item_data.get('originalImageUrl'),
                    ) if isinstance(value, str) and value.strip()), ''),
                    "wearCount": item_data.get('wearCount', 0),
                    "favorite": item_data.get('favorite', False),
                    "style": item_data.get('style', []),
                    "season": item_data.get('season', ['all']),
                    "occasion": item_data.get('occasion', []),
                    "lastWorn": last_worn,  # Already converted above
                    "userId": current_user.id,
                    "createdAt": convert_timestamp(item_data.get('createdAt'), current_time),
                    "updatedAt": convert_timestamp(item_data.get('updatedAt'), current_time),
                    # Include metadata and analysis for frontend to display all attributes
                    "metadata": item_data.get('metadata'),
                    "analysis": item_data.get('analysis'),
                    "brand": item_data.get('brand'),
                    # Keep previously editable values available after a reload.
                    "size": item_data.get('size'),
                    "purchasePrice": item_data.get('purchasePrice'),
                    **{field: item_data[field] for field in (
                        'description', 'material', 'sleeveLength', 'fit', 'neckline',
                        'length', 'transparency', 'collarType', 'embellishments',
                        'printSpecificity', 'rise', 'legOpening', 'heelHeight',
                        'statementLevel',
                    ) if field in item_data},
                    "dominantColors": item_data.get('dominantColors', []),
                    "matchingColors": item_data.get('matchingColors', []),
                    "backgroundRemovedUrl": item_data.get('backgroundRemovedUrl'),
                    "thumbnailUrl": item_data.get('thumbnailUrl'),
                    "processing_status": item_data.get('processing_status'),
                    # Preserve capsule identity and the worker's public projection
                    # across reloads. Private jobs/leases and arbitrary processing
                    # fields are deliberately not copied into this read response.
                    **{field: item_data[field] for field in (
                        'contentHash', 'imageHash', 'image_hash',
                        'image_url', 'originalImageUrl', 'originalUrl', 'originalStoragePath',
                        'deleted', 'isDeleted', 'deletedAt',
                        'processing_attempt_id', 'processing_attempt_count',
                        'processing_retry_count', 'processing_retryable',
                        'processing_retry_action',
                    ) if field in item_data},
                }

                # Older documents may contain raw exception text. Expose only
                # Goal 2's finite, user-facing messages, including on legacy rows.
                error_code = item_data.get('processing_error_code')
                if isinstance(error_code, str) and error_code in garment_processing_errors:
                    safe_code = error_code
                elif error_code or item_data.get('processing_error') or item_data.get('processing_last_error'):
                    safe_code = 'processing_failed'
                else:
                    safe_code = None
                transformed_item.update({
                    'processing_error_code': safe_code,
                    'processing_error': garment_processing_errors.get(safe_code),
                    'processing_last_error': garment_processing_errors.get(safe_code),
                })
                for field in ('processing_next_attempt_at', 'processing_expires_at', 'processing_updated_at'):
                    if field in item_data:
                        transformed_item[field] = convert_timestamp(item_data[field], None)
                
                transformed_items.append(transformed_item)
                
            except Exception as e:
                logger.error(f"Error processing wardrobe item {doc.id}: {e}")
                errors.append(f"Failed to process item {doc.id}: {str(e)}")
        
        # OPTIMIZED: Sort by createdAt (newest first) - only if needed
        sort_start = time.time()
        if transformed_items:
            transformed_items.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        logger.info(f"⏱️ WARDROBE: Sorting complete ({time.time() - sort_start:.2f}s, total: {time.time() - start_time:.2f}s)")
        
        logger.info(f"Retrieved {len(transformed_items)} wardrobe items for user {current_user.id}")
        if errors:
            logger.warning(f"Encountered {len(errors)} errors while processing items")
        
        # OPTIMIZED: Analytics logging - quick Firestore write, wrapped in try-except
        analytics_start = time.time()
        if ANALYTICS_AVAILABLE:
            try:
                analytics_event = AnalyticsEvent(
                    user_id=current_user.id,
                    event_type="wardrobe_items_listed",
                    metadata={
                        "item_count": len(transformed_items),
                        "has_items": len(transformed_items) > 0,
                        "error_count": len(errors)
                    }
                )
                log_analytics_event(analytics_event)  # Quick write, won't block significantly
                logger.info(f"⏱️ WARDROBE: Analytics logged ({time.time() - analytics_start:.2f}s, total: {time.time() - start_time:.2f}s)")
            except Exception as analytics_error:
                logger.warning(f"⏱️ WARDROBE: Analytics failed ({time.time() - analytics_start:.2f}s): {analytics_error}")
        
        # Prepare response
        response_prep_start = time.time()
        
        # Items already exclude metadata/analysis (done during transformation)
        # Ensure all datetime fields are JSON serializable
        import json
        try:
            # Test serialization to catch any remaining datetime issues
            if transformed_items:
                test_json = json.dumps(transformed_items[0])
        except (TypeError, ValueError) as serialization_error:
            logger.error(f"❌ WARDROBE: JSON serialization error in item: {serialization_error}")
            # Try to find and fix the problematic field
            for i, item in enumerate(transformed_items):
                try:
                    json.dumps(item)
                except (TypeError, ValueError) as item_error:
                    logger.error(f"❌ WARDROBE: Item {i} has serialization issue: {item_error}")
                    # Convert any remaining datetime fields
                    for key, value in item.items():
                        if value and hasattr(value, 'timestamp'):
                            try:
                                item[key] = int(value.timestamp())
                            except:
                                item[key] = None
        
        response_data = {
            "success": True,
            "items": transformed_items,
            "count": len(transformed_items),
            "user_id": current_user.id
        }
        
        # Log response size
        try:
            response_json = json.dumps(response_data)
            response_size_mb = len(response_json.encode('utf-8')) / (1024 * 1024)
            logger.info(f"⏱️ WARDROBE: Response prepared ({time.time() - response_prep_start:.2f}s, total: {time.time() - start_time:.2f}s)")
            logger.info(f"📦 WARDROBE: Response size: {response_size_mb:.2f} MB ({len(response_json)} bytes)")
        except (TypeError, ValueError) as size_error:
            logger.error(f"❌ WARDROBE: Failed to calculate response size: {size_error}")
        
        logger.info(f"✅ WARDROBE: Returning {len(transformed_items)} items (total time: {time.time() - start_time:.2f}s)")
        
        # Successfully returning items
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Unexpected error in get_wardrobe_items
        # Error details removed to reduce Railway rate limiting
        import traceback
        logger.error(f"Error retrieving wardrobe items: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving wardrobe items: {str(e)}")

@router.get("/{item_id}")
async def get_wardrobe_item(
    item_id: str,
    current_user: UserProfile = Depends(verified_wardrobe_user)
) -> Dict[str, Any]:
    """
    Get a specific wardrobe item by ID.
    """
    try:
        doc_ref = db.collection('wardrobe').document(item_id)
        doc = doc_ref.get() if doc_ref else None
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Wardrobe item not found")
        
        item_data = doc.to_dict()
        item_data['id'] = doc.id
        
        # Check if user owns this item
        if not _owned_wardrobe_item(item_data, current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        if any(item_data.get(key) for key in ('deleted', 'isDeleted', 'deletedAt', 'deleted_at')):
            raise HTTPException(404, 'Wardrobe item not found')
        
        # Log analytics event
        if ANALYTICS_AVAILABLE:
            analytics_event = AnalyticsEvent(
                user_id=current_user.id,
                event_type="wardrobe_item_viewed",
                metadata={
                    "item_id": item_id,
                    "item_type": (item_data.get("type") if item_data else None)
                }
            )
            log_analytics_event(analytics_event)
        
        return item_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting wardrobe item: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get wardrobe item"
        )

@router.put("/{item_id}")
async def update_wardrobe_item(
    item_id: str,
    item_data: Dict[str, Any],
    current_user: UserProfile = Depends(verified_wardrobe_user)
) -> Dict[str, Any]:
    """Update a wardrobe item."""
    try:
        # Check if item exists and belongs to user
        doc_ref = db.collection('wardrobe').document(item_id)
        doc = doc_ref.get() if doc_ref else None
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Wardrobe item not found")
        
        item = doc.to_dict()
        if not _owned_wardrobe_item(item, current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to update this item")
        
        try:
            update_data = build_wardrobe_update(item_data)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))

        if not update_data:
            return {"success": True, "message": "No changes to save"}

        # Nested field paths preserve metadata siblings and concurrent worker output.
        # Never accept identity, owner, or server-owned timestamps from the client.
        update_data["updatedAt"] = int(time.time())
        from src.services.wardrobe_mutations import mutate_wardrobe
        mutate_wardrobe(db, current_user.id, item_id, 'edit', update_data)
        
        # Log analytics event
        if ANALYTICS_AVAILABLE:
            # Special handling for favorite toggles - use specific interaction type for ML system
            if 'favorite' in item_data:
                try:
                    from ..services.item_analytics_service import ItemAnalyticsService
                    from ..models.item_analytics import ItemInteractionType
                    
                    analytics_service = ItemAnalyticsService()
                    import asyncio
                    asyncio.create_task(
                        analytics_service.track_item_interaction(
                            user_id=current_user.id,
                            item_id=item_id,
                            interaction_type=ItemInteractionType.FAVORITE_TOGGLE,
                            metadata={'new_status': item_data['favorite']}
                        )
                    )
                    logger.info(f"✅ Logged FAVORITE_TOGGLE interaction for item {item_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to log favorite toggle interaction: {e}")
            
            # Analytics failure must not report a successful write as a failed save.
            try:
                analytics_event = AnalyticsEvent(
                    user_id=current_user.id,
                    event_type="wardrobe_item_updated",
                    metadata={
                        "item_id": item_id,
                        "updated_fields": list(item_data.keys()),
                        "item_type": (item.get("type") if item else None)
                    }
                )
                log_analytics_event(analytics_event)
            except Exception as analytics_error:
                logger.warning(f"Failed to log wardrobe update: {analytics_error}")
        
        logger.info(f"Wardrobe item updated: {item_id}")
        
        return {
            "success": True,
            "message": "Wardrobe item updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating wardrobe item: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating wardrobe item: {str(e)}")

@router.delete("/{item_id}")
async def delete_wardrobe_item(
    item_id: str,
    current_user: UserProfile = Depends(verified_wardrobe_user)
) -> Dict[str, Any]:
    """Delete once, preserving the receipt required for safe retries and cleanup."""
    from src.services.wardrobe_mutations import mutate_wardrobe
    mutate_wardrobe(db, current_user.id, item_id, 'delete')
    return {"success": True, "message": "Wardrobe item deleted successfully"}

@router.post("/enhance-metadata")
async def enhance_wardrobe_metadata(
    current_user: UserProfile = Depends(verified_wardrobe_user)
) -> Dict[str, Any]:
    """Enhance metadata for all user's wardrobe items."""
    try:
        from src.services.app_data_privacy import require_app_data_writable, AppDataDeletionError
        from src.services.wardrobe_mutations import mutate_wardrobe
        try:
            epoch = require_app_data_writable(db, current_user.id)
        except AppDataDeletionError as error:
            raise HTTPException(error.status_code, error.detail) from None
        # Get user's wardrobe items
        docs = db.collection('wardrobe').where('userId', '==', current_user.id).stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            items.append(item_data)
        
        if not items:
            return {
                "success": True,
                "message": "No wardrobe items to enhance",
                "enhanced_count": 0
            }
        
        # Enhance metadata for each item
        enhanced_count = 0
        metadata_service = get_metadata_service()
        if not metadata_service:
            logger.warning("Metadata service not available, skipping enhancement")
            return {"enhanced": 0, "message": "Metadata service not available"}
        
        for item in items:
            try:
                enhanced_metadata = await metadata_service.enhance_item_metadata(item)
                
                # Update item in Firestore
                doc_ref = db.collection('wardrobe').document(item['id'])
                mutate_wardrobe(db, current_user.id, item['id'], 'edit',
                    {'metadata': enhanced_metadata}, expected_epoch=epoch)
                
                enhanced_count += 1
                
            except Exception as e:
                logger.error(f"Failed to enhance metadata for item {item['id']}: {e}")
                continue
        
        # Log analytics event
        if ANALYTICS_AVAILABLE:
            analytics_event = AnalyticsEvent(
                user_id=current_user.id,
                event_type="wardrobe_metadata_enhanced",
                metadata={
                    "total_items": len(items),
                    "enhanced_count": enhanced_count,
                    "success_rate": enhanced_count / len(items) if items else 0
                }
            )
            log_analytics_event(analytics_event)
        
        logger.info(f"Enhanced metadata for {enhanced_count}/{len(items)} items")
        
        return {
            "success": True,
            "message": f"Enhanced metadata for {enhanced_count} items",
            "enhanced_count": enhanced_count,
            "total_items": len(items)
        }
        
    except Exception as e:
        logger.error(f"Error enhancing wardrobe metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Error enhancing metadata: {str(e)}")

@router.post("/{item_id}/increment-wear")
async def increment_wardrobe_item_wear_count(
    item_id: str,
    request: Request,
    current_user: UserProfile = Depends(verified_wardrobe_user)
) -> Dict[str, Any]:
    """Log a standalone garment wear with a stable retry receipt."""
    from src.services.wardrobe_mutations import mutate_wardrobe
    result = mutate_wardrobe(db, current_user.id, item_id, 'wear',
                            idempotency_key=request.headers.get('Idempotency-Key'))
    return {"success": True, "message": "Wear count saved", "data": result}
