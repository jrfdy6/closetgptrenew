from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from firebase_admin import firestore
import uuid
import time
from datetime import datetime
import logging
import traceback

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

try:
    from ..auth.auth_service import get_current_user, get_current_user_id, get_current_user_optional
    AUTH_SERVICE_AVAILABLE = True
    pass  # Auth service imported
except ImportError as e:
    logger.warning(f"⚠️ Auth service import failed: {e}")
    AUTH_SERVICE_AVAILABLE = False
    def get_current_user():
        return None
    def get_current_user_id():
        return "fallback-user-id"
    def get_current_user_optional():
        return None

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
    current_user: Optional[UserProfile] = Depends(get_current_user_optional),
    limit: int = 10
) -> Dict[str, Any]:
    """Get the top worn wardrobe items for the current user."""
    try:
        if not FIREBASE_AVAILABLE or not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Query all wardrobe items for the user, ordered by wear count
        query = db.collection('wardrobe').where('userId', '==', current_user.id)
        docs = query.stream()
        
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
        
        # Get items worn this week (last 7 days)
        from datetime import datetime, timedelta, timezone
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_items = []
        for item in items:
            last_worn = safe_get(item, 'lastWorn')
            if last_worn:
                try:
                    if isinstance(last_worn, datetime):
                        item_date = last_worn
                    elif isinstance(last_worn, str):
                        item_date = datetime.fromisoformat(last_worn.replace('Z', '+00:00'))
                    elif isinstance(last_worn, (int, float)):
                        item_date = datetime.fromtimestamp(last_worn, tz=timezone.utc)
                    else:
                        continue
                    
                    # Ensure both dates are timezone-aware
                    if item_date.tzinfo is None:
                        item_date = item_date.replace(tzinfo=timezone.utc)
                    if week_ago.tzinfo is None:
                        week_ago = week_ago.replace(tzinfo=timezone.utc)
                    
                    if item_date > week_ago:
                        recent_items.append(item)
                except (ValueError, TypeError):
                    continue
        
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
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the most worn items organized by category (tops, bottoms, shoes, etc.)."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Query all wardrobe items for the user
        query = db.collection('wardrobe').where('userId', '==', current_user.id)
        docs = query.stream()
        
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
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get trending styles based on user's wardrobe and preferences."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Query user's wardrobe items
        query = db.collection('wardrobe').where('userId', '==', current_user.id)
        docs = query.stream()
        
        items = [doc.to_dict() for doc in docs]
        
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
                    # Add bonus for recent wear
                    try:
                        last_worn = (item.get('lastWorn', 0) if item else 0)
                        if isinstance(last_worn, (int, float)):
                            # Already a timestamp
                            days_since_worn = (int(time.time()) - last_worn) / (24 * 60 * 60)
                        else:
                            # Convert datetime to timestamp
                            from datetime import datetime, timezone
                            if hasattr(last_worn, 'timestamp'):
                                days_since_worn = (int(time.time()) - int(last_worn.timestamp())) / (24 * 60 * 60)
                            else:
                                # Skip if we can't convert
                                continue
                        
                        if days_since_worn < 7:
                            score += 2
                        elif days_since_worn < 30:
                            score += 1
                    except (ValueError, TypeError, AttributeError):
                        # Skip if we can't process the date
                        pass
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
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Add a new wardrobe item for the current user.
    
    Expected fields:
    - name: str
    - type: str (clothing type)
    - color: str
    - style: str or List[str]
    - occasion: str or List[str]
    - season: str or List[str]
    - imageUrl: str (optional)
    """
    start_time = time.time()
    try:
        # Validate required fields
        required_fields = ['name', 'type', 'color']
        for field in required_fields:
            if field not in item_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create item ID
        item_id = str(uuid.uuid4())
        
        # Extract AI analysis results if available
        analysis = (item_data.get("analysis", {}) if item_data else {})
        metadata_analysis = (analysis.get("metadata", {}) if analysis else {})
        visual_attrs = (metadata_analysis.get("visualAttributes", {}) if metadata_analysis else {})
        
        # Use AI analysis results or fallback to defaults (ALL 13 fields)
        visual_attributes = {
            "wearLayer": (visual_attrs.get("wearLayer", "Mid") if visual_attrs else "Mid"),
            "sleeveLength": (visual_attrs.get("sleeveLength", "Unknown") if visual_attrs else "Unknown"),
            "material": (visual_attrs.get("material", "cotton") if visual_attrs else "cotton"),
            "pattern": (visual_attrs.get("pattern", "solid") if visual_attrs else "solid"),
            "textureStyle": (visual_attrs.get("textureStyle", "smooth") if visual_attrs else "smooth"),
            "fabricWeight": (visual_attrs.get("fabricWeight", "Medium") if visual_attrs else "Medium"),
            "fit": (visual_attrs.get("fit", "regular") if visual_attrs else "regular"),
            "silhouette": (visual_attrs.get("silhouette", "regular") if visual_attrs else "regular"),
            "length": (visual_attrs.get("length", "regular") if visual_attrs else "regular"),
            "formalLevel": (visual_attrs.get("formalLevel", "Casual") if visual_attrs else "Casual"),
            "genderTarget": (visual_attrs.get("genderTarget", "Unisex") if visual_attrs else "Unisex"),
            "backgroundRemoved": (visual_attrs.get("backgroundRemoved", False) if visual_attrs else False),
            "hangerPresent": (visual_attrs.get("hangerPresent", False) if visual_attrs else False)
        }
        
        # Extract dominant colors from AI analysis if available
        dominant_colors = (analysis.get("dominantColors", []) if analysis else [])
        if not dominant_colors:
            # Fallback to basic color analysis
            dominant_colors = [{"name": item_data["color"], "hex": "#000000", "rgb": [0, 0, 0]}]
        
        # Extract matching colors from AI analysis if available
        matching_colors = (analysis.get("matchingColors", []) if analysis else [])
        
        # Prepare item data with ROOT-level AI fields
        wardrobe_item = {
            "id": item_id,
            "userId": current_user.id,
            "name": item_data["name"],
            "type": item_data["type"],
            "color": item_data["color"],
            "style": (item_data.get("style", []) if item_data else []),
            "occasion": (item_data.get("occasion", []) if item_data else []),
            "season": (item_data.get("season", ["all"]) if item_data else ["all"]),
            "imageUrl": (item_data.get("imageUrl", "") if item_data else ""),
            "dominantColors": dominant_colors,
            "matchingColors": matching_colors,
            "tags": (item_data.get("tags", []) if item_data else []),
            "mood": (analysis.get("mood", []) if analysis else []),
            # ROOT-level fields from AI analysis
            "bodyTypeCompatibility": (analysis.get("bodyTypeCompatibility", []) if analysis else []),
            "weatherCompatibility": (analysis.get("weatherCompatibility", []) if analysis else []),
            "gender": (analysis.get("gender", "unisex") if analysis else "unisex"),
            "backgroundRemoved": (analysis.get("backgroundRemoved", False) if analysis else False),
            "backgroundRemovedUrl": None,  # Will be filled by worker in background
            "processing_status": "pending",  # Triggers background processing worker
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "metadata": {
                "analysisTimestamp": int(time.time()),
                "originalType": item_data["type"],
                "styleTags": (item_data.get("style", []) if item_data else []),
                "occasionTags": (item_data.get("occasion", []) if item_data else []),
                "colorAnalysis": {
                    "dominant": [(color.get("name", item_data["color"]) if color else item_data["color"]) for color in dominant_colors],
                    "matching": [(color.get("name", "") if color else "") for color in matching_colors]
                },
                "visualAttributes": visual_attributes,
                "naturalDescription": (metadata_analysis.get("naturalDescription", "") if metadata_analysis else ""),
                "itemMetadata": {
                    "tags": (item_data.get("tags", []) if item_data else []),
                    "careInstructions": "Check care label",
                    "brand": (analysis.get("brand") if analysis else None),
                    "priceEstimate": None
                },
                # Store the full AI analysis for reference
                "aiAnalysis": analysis if analysis else None
            }
        }
        
        # Normalize the item metadata before saving
        from ..utils.semantic_normalization import normalize_item_metadata
        normalized_item = normalize_item_metadata(wardrobe_item)
        
        # Save to Firestore
        doc_ref = db.collection('wardrobe').document(item_id)
        doc_ref.set(normalized_item)
        
        # Track usage (async, don't fail if it errors)
        try:
            from ..services.usage_tracking_service import UsageTrackingService
            usage_service = UsageTrackingService()
            await usage_service.track_item_upload(current_user.id)
            logger.info(f"📊 Tracked item upload usage for user {current_user.id}")
        except Exception as usage_error:
            logger.warning(f"Usage tracking failed: {usage_error}")
        
        # Log analytics event
        if ANALYTICS_AVAILABLE:
            analytics_event = AnalyticsEvent(
                user_id=current_user.id,
                event_type="wardrobe_item_added",
                metadata={
                    "item_id": item_id,
                    "item_type": item_data["type"],
                    "has_image": bool((item_data.get("imageUrl") if item_data else None)),
                    "style_count": len((item_data.get("style", []) if item_data else [])),
                    "occasion_count": len((item_data.get("occasion", []) if item_data else []))
                }
            )
            log_analytics_event(analytics_event)
        
        logger.info(f"Wardrobe item added: {item_id} for user {current_user.id}")
        
        # 🚀 PRODUCTION MONITORING: Track successful wardrobe add
        if MONITORING_AVAILABLE and monitoring_service:
            try:
                duration_ms = (time.time() - start_time) * 1000
                await monitoring_service.track_operation(
                    operation=OperationType.WARDROBE_ADD,
                    user_id=current_user.id,
                    status="success",
                    duration_ms=duration_ms,
                    context={
                        "item_type": item_data["type"],
                        "has_image": bool(item_data.get("imageUrl")),
                        "has_ai_analysis": bool(item_data.get("analysis"))
                    }
                )
                
                # Track first item added milestone
                await monitoring_service.track_user_journey(
                    user_id=current_user.id,
                    step=UserJourneyStep.FIRST_ITEM_ADDED,
                    metadata={"item_type": item_data["type"]}
                )
            except Exception as monitoring_error:
                logger.warning(f"Production monitoring failed: {monitoring_error}")
        
        return {
            "success": True,
            "message": "Wardrobe item added successfully",
            "item": normalized_item
        }
        
    except HTTPException:
        # Track HTTP exceptions
        if MONITORING_AVAILABLE and monitoring_service:
            try:
                duration_ms = (time.time() - start_time) * 1000
                await monitoring_service.track_operation(
                    operation=OperationType.WARDROBE_ADD,
                    user_id=current_user.id if current_user else 'unknown',
                    status="failure",
                    duration_ms=duration_ms,
                    error="HTTP Exception",
                    error_type="HTTPException"
                )
            except:
                pass
        raise
    except Exception as e:
        logger.error(f"Error adding wardrobe item: {e}")
        
        # 🚀 PRODUCTION MONITORING: Track failure
        if MONITORING_AVAILABLE and monitoring_service:
            try:
                duration_ms = (time.time() - start_time) * 1000
                await monitoring_service.track_operation(
                    operation=OperationType.WARDROBE_ADD,
                    user_id=current_user.id if current_user else 'unknown',
                    status="failure",
                    duration_ms=duration_ms,
                    error=str(e),
                    error_type=type(e).__name__,
                    stack_trace=traceback.format_exc(),
                    context={"item_type": item_data.get("type") if item_data else "unknown"}
                )
            except Exception as monitoring_error:
                logger.warning(f"Production monitoring failed during error handling: {monitoring_error}")
        
        raise HTTPException(status_code=500, detail=f"Error adding wardrobe item: {str(e)}")

@router.get("/test", include_in_schema=False)
async def test_wardrobe_endpoint() -> Dict[str, Any]:
    """Simple test endpoint to verify the wardrobe endpoint is working."""
    return {
        "success": True,
        "message": "Wardrobe endpoint is working",
        "timestamp": "2024-01-01T00:00:00Z",
        "backend": "closetgptrenew-backend-production"
    }

@router.get("/count", include_in_schema=False)
async def count_wardrobe_items() -> Dict[str, Any]:
    """Count all items in wardrobe collection."""
    try:
        from src.config.firebase import firebase_initialized, db
        
        if not firebase_initialized or db is None:
            return {"error": "Firebase not initialized"}
        
        # Count all items
        all_docs = db.collection('wardrobe').stream()
        total_count = len(list(all_docs))
        
        return {
            "success": True,
            "total_items": total_count,
            "message": f"Found {total_count} items in wardrobe collection"
        }
        
    except Exception as e:
        return {"error": str(e)}

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
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get all wardrobe items for the current user."""
    try:
        # Check Firebase initialization status
        from src.config.firebase import firebase_initialized, db
        # Debug logging removed to reduce Railway rate limiting
        # Railway redeploy trigger - Firebase credentials updated
        
        if not firebase_initialized or db is None:
            # Firebase not available
            raise HTTPException(
                status_code=500, 
                detail="Database connection not available. Firebase may not be properly configured."
            )
        
        logger.info(f"Getting wardrobe items for user: {current_user.id}")
        # User authenticated, querying wardrobe
        
        # Query Firestore for user's wardrobe items - SIMPLE APPROACH
        try:
            # Get all documents and filter by user ID
            all_docs = db.collection('wardrobe').stream()
            
            items = []
            for doc in all_docs:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Check all possible user ID field names
                user_id = ((data.get('userId') if data else None) or 
                          (data.get('uid') if data else None) or 
                          (data.get('ownerId') if data else None) or 
                          (data.get('user_id') if data else None))
                
                # If this item belongs to the current user, include it
                if user_id == current_user.id:
                    items.append(data)
            
            # Convert to the format expected by the rest of the function
            docs_list = items
            
        except Exception as db_error:
            # Firestore query failed
            logger.error(f"Firestore query failed: {db_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Database query failed: {str(db_error)}"
            )
        
        items = []
        errors = []
        
        # Process documents (debug logging removed to reduce Railway rate limiting)
        for i, item_data in enumerate(docs_list):
            try:
                
                # Ensure required fields exist
                if 'name' not in item_data:
                    item_data['name'] = 'Unknown Item'
                if 'type' not in item_data:
                    item_data['type'] = 'unknown'
                if 'color' not in item_data:
                    item_data['color'] = 'unknown'
                if 'style' not in item_data:
                    item_data['style'] = []
                if 'occasion' not in item_data:
                    item_data['occasion'] = []
                if 'season' not in item_data:
                    item_data['season'] = ['all']
                if 'tags' not in item_data:
                    item_data['tags'] = []
                if 'dominantColors' not in item_data:
                    item_data['dominantColors'] = []
                if 'matchingColors' not in item_data:
                    item_data['matchingColors'] = []
                if 'imageUrl' not in item_data:
                    item_data['imageUrl'] = 'https://placeholder.com/image.jpg'
                if 'userId' not in item_data:
                    item_data['userId'] = current_user.id
                if 'metadata' not in item_data:
                    item_data['metadata'] = {
                        'analysisTimestamp': int(time.time() * 1000),
                        'originalType': (item_data.get('type', 'other') if item_data else 'other'),
                        'colorAnalysis': {'dominant': [], 'matching': []}
                    }
                if 'favorite' not in item_data:
                    item_data['favorite'] = False
                if 'wearCount' not in item_data:
                    item_data['wearCount'] = 0
                if 'lastWorn' not in item_data:
                    item_data['lastWorn'] = None
                
                # Handle timestamp conversion
                try:
                    if 'createdAt' in item_data:
                        if isinstance(item_data['createdAt'], str):
                            item_data['createdAt'] = int(datetime.fromisoformat(item_data['createdAt'].replace('Z', '+00:00')).timestamp())
                        elif hasattr(item_data['createdAt'], 'timestamp'):
                            item_data['createdAt'] = int(item_data['createdAt'].timestamp())
                    else:
                        item_data['createdAt'] = int(time.time())
                except Exception as e:
                    logger.warning(f"Error converting createdAt for item {doc.id}: {e}")
                    item_data['createdAt'] = int(time.time())
                
                try:
                    if 'updatedAt' in item_data:
                        if isinstance(item_data['updatedAt'], str):
                            item_data['updatedAt'] = int(datetime.fromisoformat(item_data['updatedAt'].replace('Z', '+00:00')).timestamp())
                        elif hasattr(item_data['updatedAt'], 'timestamp'):
                            item_data['updatedAt'] = int(item_data['updatedAt'].timestamp())
                    else:
                        item_data['updatedAt'] = int(time.time())
                except Exception as e:
                    logger.warning(f"Error converting updatedAt for item {doc.id}: {e}")
                    item_data['updatedAt'] = int(time.time())
                
                items.append(item_data)
                logger.debug(f"Successfully processed item {doc.id}")
                
            except Exception as e:
                logger.error(f"Error processing wardrobe item {doc.id}: {e}")
                errors.append(f"Failed to process item {doc.id}: {str(e)}")
        
        # Sort items by creation date (newest first)
        items.sort(key=lambda x: (x.get('createdAt', 0) if x else 0), reverse=True)
        
        logger.info(f"Retrieved {len(items)} wardrobe items for user {current_user.id}")
        if errors:
            logger.warning(f"Encountered {len(errors)} errors while processing items")
        
        # Log analytics event
        if ANALYTICS_AVAILABLE:
            try:
                analytics_event = AnalyticsEvent(
                    user_id=current_user.id,
                    event_type="wardrobe_items_listed",
                    metadata={
                        "item_count": len(items),
                        "has_items": len(items) > 0,
                        "error_count": len(errors)
                    }
                )
                log_analytics_event(analytics_event)
            except Exception as analytics_error:
                # Analytics logging failed
                # Don't fail the request if analytics fails
                pass
        
        # Transform backend data to match frontend expectations
        transformed_items = []
        for item in items:
            transformed_item = {
                "id": item['id'],
                "name": (item.get('name', 'Unknown Item') if item else 'Unknown Item'),
                "type": (item.get('type', 'unknown') if item else 'unknown'),  # Keep as type for frontend
                "color": (item.get('color', 'unknown') if item else 'unknown'),
                "imageUrl": (item.get('imageUrl', '/placeholder.png') if item else '/placeholder.png'),  # Keep as imageUrl for frontend
                "wearCount": (item.get('wearCount', 0) if item else 0),  # Keep as wearCount for frontend
                "favorite": (item.get('favorite', False) if item else False),
                "style": (item.get('style', []) if item else []),
                "season": (item.get('season', ['all']) if item else ['all']),
                "occasion": (item.get('occasion', []) if item else []),
                "lastWorn": (item.get('lastWorn') if item else None),  # Keep as lastWorn for frontend
                "userId": current_user.id,
                "createdAt": (item.get('createdAt') if item else None),  # Keep as createdAt for frontend
                "updatedAt": (item.get('updatedAt') if item else None),  # Keep as updatedAt for frontend
                "metadata": (item.get('metadata') if item else None),  # Include metadata for pattern/material/fit scoring
                "analysis": (item.get('analysis') if item else None),  # Include AI analysis metadata for frontend display
                
                # NEW - Worker-processed background removal fields (stealth mode)
                "backgroundRemovedUrl": (item.get('backgroundRemovedUrl') if item else None),
                "thumbnailUrl": (item.get('thumbnailUrl') if item else None),
                "processing_status": (item.get('processing_status') if item else None),
            }
            transformed_items.append(transformed_item)
        
        # Successfully returning items
        return {
            "success": True,
            "items": transformed_items,
            "count": len(transformed_items),
            "user_id": current_user.id
        }
        
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
    current_user: UserProfile = Depends(get_current_user)
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
        if item_data.get('userId') != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
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
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update a wardrobe item."""
    try:
        # Check if item exists and belongs to user
        doc_ref = db.collection('wardrobe').document(item_id)
        doc = doc_ref.get() if doc_ref else None
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Wardrobe item not found")
        
        item = doc.to_dict()
        if item.get('userId') != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this item")
        
        # Update item data
        update_data = {
            **item_data,
            "updatedAt": int(time.time())
        }
        
        # Update in Firestore
        doc_ref.update(update_data)
        
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
            
            # Also log general update event
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
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a wardrobe item."""
    try:
        # Check if item exists and belongs to user
        doc_ref = db.collection('wardrobe').document(item_id)
        doc = doc_ref.get() if doc_ref else None
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Wardrobe item not found")
        
        item = doc.to_dict()
        if item.get('userId') != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this item")
        
        # Log analytics event before deletion
        if ANALYTICS_AVAILABLE:
            analytics_event = AnalyticsEvent(
                user_id=current_user.id,
                event_type="wardrobe_item_deleted",
                metadata={
                    "item_id": item_id,
                    "item_type": (item.get("type") if item else None),
                    "item_name": (item.get("name") if item else None)
                }
            )
            log_analytics_event(analytics_event)
        
        # Delete from Firestore
        doc_ref.delete()
        
        logger.info(f"Wardrobe item deleted: {item_id}")
        
        return {
            "success": True,
            "message": "Wardrobe item deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting wardrobe item: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting wardrobe item: {str(e)}")

@router.post("/enhance-metadata")
async def enhance_wardrobe_metadata(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Enhance metadata for all user's wardrobe items."""
    try:
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
                doc_ref.update({
                    'metadata': enhanced_metadata,
                    'updatedAt': int(time.time())
                })
                
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
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """Increment the wear count for a specific wardrobe item."""
    try:
        # Check if item exists and belongs to user
        doc_ref = db.collection('wardrobe').document(item_id)
        doc = doc_ref.get() if doc_ref else None
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Wardrobe item not found")
        
        item = doc.to_dict()
        if item.get('userId') != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this item")
        
        # Get current wear count and increment it
        current_wear_count = (item.get('wearCount', 0) if item else 0)
        new_wear_count = current_wear_count + 1
        current_timestamp = int(time.time())
        
        # Update wear count and last worn timestamp
        update_data = {
            'wearCount': new_wear_count,
            'lastWorn': current_timestamp,
            'updatedAt': current_timestamp
        }
        
        doc_ref.update(update_data)
        
        # Log analytics event
        if ANALYTICS_AVAILABLE:
            analytics_event = AnalyticsEvent(
                user_id=current_user.id,
                event_type="wardrobe_item_wear_incremented",
                metadata={
                    "item_id": item_id,
                    "item_type": (item.get("type") if item else None),
                    "previous_wear_count": current_wear_count,
                    "new_wear_count": new_wear_count
                }
            )
            log_analytics_event(analytics_event)
        
        logger.info(f"Wear count incremented for item {item_id}: {current_wear_count} -> {new_wear_count}")
        
        return {
            "success": True,
            "message": "Wear count incremented successfully",
            "data": {
                "itemId": item_id,
                "previousWearCount": current_wear_count,
                "newWearCount": new_wear_count,
                "lastWorn": current_timestamp
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error incrementing wear count for item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error incrementing wear count: {str(e)}")
 