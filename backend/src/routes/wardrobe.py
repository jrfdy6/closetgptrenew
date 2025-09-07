from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from firebase_admin import firestore
import uuid
import time
from datetime import datetime
import logging

# Set up basic logging
logger = logging.getLogger(__name__)
logger.info("✅ wardrobe router loaded")

# Optional imports with graceful fallbacks
try:
    from ..custom_types.wardrobe import ClothingItem, ClothingType, Color
    CUSTOM_TYPES_AVAILABLE = True
    logger.info("✅ Custom wardrobe types imported successfully")
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
    logger.info("✅ Profile types imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Profile types import failed: {e}")
    PROFILE_TYPES_AVAILABLE = False
    from typing import TypedDict
    class UserProfile(TypedDict):
        id: str
        name: str
        email: str

try:
    from ..services.metadata_enhancement_service import MetadataEnhancementService
    metadata_service = MetadataEnhancementService()
    METADATA_SERVICE_AVAILABLE = True
    logger.info("✅ Metadata enhancement service imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Metadata enhancement service import failed: {e}")
    metadata_service = None
    METADATA_SERVICE_AVAILABLE = False

try:
    from ..core.logging import get_logger
    logger = get_logger("wardrobe")
    CORE_LOGGING_AVAILABLE = True
    logger.info("✅ Core logging imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Core logging import failed: {e}")
    CORE_LOGGING_AVAILABLE = False
    logger = logging.getLogger(__name__)

try:
    from ..models.analytics_event import AnalyticsEvent
    from ..services.analytics_service import log_analytics_event
    ANALYTICS_AVAILABLE = True
    logger.info("✅ Analytics services imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Analytics services import failed: {e}")
    ANALYTICS_AVAILABLE = False
    def log_analytics_event(*args, **kwargs):
        pass  # No-op fallback

try:
    from ..auth.auth_service import get_current_user, get_current_user_id
    AUTH_SERVICE_AVAILABLE = True
    logger.info("✅ Auth service imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Auth service import failed: {e}")
    AUTH_SERVICE_AVAILABLE = False
    def get_current_user():
        return None
    def get_current_user_id():
        return "fallback-user-id"

# Remove prefix since app.py will mount it at /api/wardrobe
router = APIRouter(tags=["wardrobe"])

# Initialize Firestore conditionally
try:
    db = firestore.client()
    FIREBASE_AVAILABLE = True
    logger.info("✅ Firebase client initialized successfully")
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
        items.sort(key=lambda x: x.get('wearCount', 0), reverse=True)
        top_items = items[:limit]
        
        # Calculate statistics
        total_items = len(items)
        total_wear_count = sum(item.get('wearCount', 0) for item in items)
        avg_wear_count = total_wear_count / total_items if total_items > 0 else 0
        
        # Get items with no wear (unworn items)
        unworn_items = [item for item in items if item.get('wearCount', 0) == 0]
        
        # Get items worn this week (last 7 days)
        from datetime import datetime, timedelta, timezone
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_items = []
        for item in items:
            last_worn = item.get('lastWorn')
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
                    "name": item.get('name', 'Unknown'),
                    "type": item.get('type', 'Unknown'),
                    "color": item.get('color', 'Unknown'),
                    "wear_count": item.get('wearCount', 0),
                    "last_worn": item.get('lastWorn'),
                    "is_favorite": item.get('isFavorite', False),
                    "image_url": item.get('imageUrl') or item.get('image_url') or item.get('image')
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
            item_type = item.get('type', 'Unknown').lower()
            
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
                category_items.sort(key=lambda x: x.get('wearCount', 0), reverse=True)
                most_worn = category_items[0]
                
                most_worn_by_category[category] = {
                    "item": {
                        "id": most_worn['id'],
                        "name": most_worn.get('name', 'Unknown'),
                        "type": most_worn.get('type', 'Unknown'),
                        "color": most_worn.get('color', 'Unknown'),
                        "wear_count": most_worn.get('wearCount', 0),
                        "last_worn": most_worn.get('lastWorn'),
                        "image_url": most_worn.get('imageUrl') or most_worn.get('image_url') or most_worn.get('image')
                    },
                    "total_items": len(category_items),
                    "total_wear_count": sum(item.get('wearCount', 0) for item in category_items),
                    "avg_wear_count": sum(item.get('wearCount', 0) for item in category_items) / len(category_items) if category_items else 0
                }
        
        # Calculate overall statistics
        total_items = len(items)
        total_wear_count = sum(item.get('wearCount', 0) for item in items)
        
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
            styles = item.get('style', [])
            if isinstance(styles, list):
                for style in styles:
                    style_counts[style] = style_counts.get(style, 0) + 1
            elif isinstance(styles, str):
                style_counts[styles] = style_counts.get(styles, 0) + 1
            
            # Count colors
            color = item.get('color', 'unknown')
            color_counts[color] = color_counts.get(color, 0) + 1
            
            # Count types
            item_type = item.get('type', 'unknown')
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
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
                        last_worn = item.get('lastWorn', 0)
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
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'type': item.get('type'),
                    'color': item.get('color', 'unknown'),
                    'style': item.get('style', []),
                    'trending_score': score,
                    'wear_count': item.get('wearCount', 0)
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
    try:
        # Validate required fields
        required_fields = ['name', 'type', 'color']
        for field in required_fields:
            if field not in item_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create item ID
        item_id = str(uuid.uuid4())
        
        # Extract AI analysis results if available
        analysis = item_data.get("analysis", {})
        metadata_analysis = analysis.get("metadata", {})
        visual_attrs = metadata_analysis.get("visualAttributes", {})
        
        # Use AI analysis results or fallback to defaults
        visual_attributes = {
            "pattern": visual_attrs.get("pattern", "solid"),
            "formalLevel": visual_attrs.get("formalLevel", "casual"),
            "fit": visual_attrs.get("fit", "regular"),
            "material": visual_attrs.get("material", "cotton"),
            "fabricWeight": visual_attrs.get("fabricWeight", "medium"),
            "sleeveLength": visual_attrs.get("sleeveLength", "unknown"),
            "silhouette": visual_attrs.get("silhouette", "regular"),
            "genderTarget": visual_attrs.get("genderTarget", "unisex")
        }
        
        # Extract dominant colors from AI analysis if available
        dominant_colors = analysis.get("dominantColors", [])
        if not dominant_colors:
            # Fallback to basic color analysis
            dominant_colors = [{"name": item_data["color"], "hex": "#000000", "rgb": [0, 0, 0]}]
        
        # Extract matching colors from AI analysis if available
        matching_colors = analysis.get("matchingColors", [])
        
        # Prepare item data
        wardrobe_item = {
            "id": item_id,
            "userId": current_user.id,
            "name": item_data["name"],
            "type": item_data["type"],
            "color": item_data["color"],
            "style": item_data.get("style", []),
            "occasion": item_data.get("occasion", []),
            "season": item_data.get("season", ["all"]),
            "imageUrl": item_data.get("imageUrl", ""),
            "dominantColors": dominant_colors,
            "matchingColors": matching_colors,
            "tags": item_data.get("tags", []),
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "metadata": {
                "analysisTimestamp": int(time.time()),
                "originalType": item_data["type"],
                "styleTags": item_data.get("style", []),
                "occasionTags": item_data.get("occasion", []),
                "colorAnalysis": {
                    "dominant": [color.get("name", item_data["color"]) for color in dominant_colors],
                    "matching": [color.get("name", "") for color in matching_colors]
                },
                "visualAttributes": visual_attributes,
                "itemMetadata": {
                    "tags": item_data.get("tags", []),
                    "careInstructions": "Check care label"
                },
                # Store the full AI analysis for reference
                "aiAnalysis": analysis if analysis else None
            }
        }
        
        # Save to Firestore
        doc_ref = db.collection('wardrobe').document(item_id)
        doc_ref.set(wardrobe_item)
        
        # Log analytics event
        if ANALYTICS_AVAILABLE:
            analytics_event = AnalyticsEvent(
                user_id=current_user.id,
                event_type="wardrobe_item_added",
                metadata={
                    "item_id": item_id,
                    "item_type": item_data["type"],
                    "has_image": bool(item_data.get("imageUrl")),
                    "style_count": len(item_data.get("style", [])),
                    "occasion_count": len(item_data.get("occasion", []))
                }
            )
            log_analytics_event(analytics_event)
        
        logger.info(f"Wardrobe item added: {item_id} for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Wardrobe item added successfully",
            "item": wardrobe_item
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding wardrobe item: {e}")
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
            user_id = data.get('userId') or data.get('uid') or data.get('ownerId') or data.get('user_id')
            if user_id:
                user_ids_found.add(user_id)
            
            # Only include first 10 items for response size
            if len(items) < 10:
                items.append({
                    'id': doc.id,
                    'userId': data.get('userId', 'NOT_FOUND'),
                    'uid': data.get('uid', 'NOT_FOUND'),
                    'ownerId': data.get('ownerId', 'NOT_FOUND'),
                    'user_id': data.get('user_id', 'NOT_FOUND'),
                    'name': data.get('name', 'NO_NAME'),
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
        print(f"🔍 DEBUG: Firebase initialized: {firebase_initialized}")
        print(f"🔍 DEBUG: Database client: {db}")
        # Railway redeploy trigger - Firebase credentials updated
        
        if not firebase_initialized or db is None:
            print("🔍 DEBUG: Firebase not initialized or database client is None")
            raise HTTPException(
                status_code=500, 
                detail="Database connection not available. Firebase may not be properly configured."
            )
        
        logger.info(f"Getting wardrobe items for user: {current_user.id}")
        print(f"🔍 DEBUG: User authenticated: {current_user.id}")
        print(f"🔍 DEBUG: Querying wardrobe collection for userId: {current_user.id}")
        
        # Query Firestore for user's wardrobe items - SIMPLE APPROACH
        try:
            # Get all documents and filter by user ID
            all_docs = db.collection('wardrobe').stream()
            
            items = []
            for doc in all_docs:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Check all possible user ID field names
                user_id = (data.get('userId') or 
                          data.get('uid') or 
                          data.get('ownerId') or 
                          data.get('user_id'))
                
                # If this item belongs to the current user, include it
                if user_id == current_user.id:
                    items.append(data)
            
            # Convert to the format expected by the rest of the function
            docs_list = items
            
        except Exception as db_error:
            print(f"🔍 DEBUG: Firestore query failed: {db_error}")
            logger.error(f"Firestore query failed: {db_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Database query failed: {str(db_error)}"
            )
        
        items = []
        errors = []
        
        print(f"🔍 DEBUG: Processing {len(docs_list)} documents...")
        for i, item_data in enumerate(docs_list):
            try:
                print(f"🔍 DEBUG: Processing document {i+1}: {item_data.get('id', 'NO_ID')}")
                print(f"🔍 DEBUG: Document data keys: {list(item_data.keys())}")
                print(f"🔍 DEBUG: Document userId field: {item_data.get('userId', 'NOT_FOUND')}")
                print(f"🔍 DEBUG: Document uid field: {item_data.get('uid', 'NOT_FOUND')}")
                print(f"🔍 DEBUG: Document ownerId field: {item_data.get('ownerId', 'NOT_FOUND')}")
                print(f"🔍 DEBUG: Document user_id field: {item_data.get('user_id', 'NOT_FOUND')}")
                
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
                    item_data['imageUrl'] = ''
                if 'metadata' not in item_data:
                    item_data['metadata'] = {}
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
        items.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
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
                print(f"🔍 DEBUG: Analytics logging failed: {analytics_error}")
                # Don't fail the request if analytics fails
        
        # Transform backend data to match frontend expectations
        transformed_items = []
        for item in items:
            transformed_item = {
                "id": item['id'],
                "name": item.get('name', 'Unknown Item'),
                "type": item.get('type', 'unknown'),  # Keep as type for frontend
                "color": item.get('color', 'unknown'),
                "imageUrl": item.get('imageUrl', '/placeholder.png'),  # Keep as imageUrl for frontend
                "wearCount": item.get('wearCount', 0),  # Keep as wearCount for frontend
                "favorite": item.get('favorite', False),
                "style": item.get('style', []),
                "season": item.get('season', ['all']),
                "occasion": item.get('occasion', []),
                "lastWorn": item.get('lastWorn'),  # Keep as lastWorn for frontend
                "userId": current_user.id,
                "createdAt": item.get('createdAt'),  # Keep as createdAt for frontend
                "updatedAt": item.get('updatedAt'),  # Keep as updatedAt for frontend
            }
            transformed_items.append(transformed_item)
        
        print(f"🔍 DEBUG: Successfully returning {len(transformed_items)} items")
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
        print(f"🔍 DEBUG: Unexpected error in get_wardrobe_items: {e}")
        print(f"🔍 DEBUG: Error type: {type(e)}")
        import traceback
        print(f"🔍 DEBUG: Full traceback: {traceback.format_exc()}")
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
        doc = doc_ref.get()
        
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
                    "item_type": item_data.get("type")
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
        doc = doc_ref.get()
        
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
            analytics_event = AnalyticsEvent(
                user_id=current_user.id,
                event_type="wardrobe_item_updated",
                metadata={
                    "item_id": item_id,
                    "updated_fields": list(item_data.keys()),
                    "item_type": item.get("type")
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
        doc = doc_ref.get()
        
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
                    "item_type": item.get("type"),
                    "item_name": item.get("name")
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
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Wardrobe item not found")
        
        item = doc.to_dict()
        if item.get('userId') != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this item")
        
        # Get current wear count and increment it
        current_wear_count = item.get('wearCount', 0)
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
                    "item_type": item.get("type"),
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
 