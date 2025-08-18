from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from firebase_admin import firestore
import uuid
import time
from datetime import datetime

# Use relative imports for router loading compatibility
from ..custom_types.wardrobe import ClothingItem, ClothingType, Color
from ..custom_types.profile import UserProfile
from ..services.metadata_enhancement_service import MetadataEnhancementService
from ..core.logging import get_logger
from ..models.analytics_event import AnalyticsEvent
from ..services.analytics_service import log_analytics_event
from ..auth.auth_service import get_current_user_optional

router = APIRouter(prefix="/api/wardrobe", tags=["wardrobe"])

# Initialize Firestore conditionally
try:
    db = firestore.client()
    metadata_service = MetadataEnhancementService()
    logger = get_logger("wardrobe")
except Exception as e:
    print(f"Warning: Could not initialize Firebase services: {e}")
    db = None
    metadata_service = None
    logger = None

@router.get("/wardrobe-stats")
async def get_wardrobe_stats(
    current_user: UserProfile = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Get comprehensive wardrobe statistics for the current user."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Query all wardrobe items for the user
        query = db.collection('wardrobe').where('userId', '==', current_user.id)
        docs = query.stream()
        
        items = []
        categories = {}
        colors = {}
        
        for doc in docs:
            item = doc.to_dict()
            items.append(item)
            
            # Count by category
            item_type = item.get('type', 'unknown')
            categories[item_type] = categories.get(item_type, 0) + 1
            
            # Count by color
            item_color = item.get('color', 'unknown')
            colors[item_color] = colors.get(item_color, 0) + 1
        
        # Calculate additional stats (handle empty wardrobe gracefully)
        total_items = len(items)
        favorites = sum(1 for item in items if item.get('favorite', False))
        total_wear_count = sum(item.get('wearCount', 0) for item in items)
        avg_wear_count = total_wear_count / total_items if total_items > 0 else 0
        
        # Get recent items (last 30 days)
        thirty_days_ago = int(time.time()) - (30 * 24 * 60 * 60)
        recent_items = [item for item in items if item.get('createdAt', 0) > thirty_days_ago]
        
        stats = {
            "total_items": total_items,
            "categories": categories,
            "colors": colors,
            "favorites": favorites,
            "total_wear_count": total_wear_count,
            "avg_wear_count": round(avg_wear_count, 2),
            "recent_items_count": len(recent_items),
            "user_id": current_user.id,
            "last_updated": int(time.time())
        }
        
        logger.info(f"Retrieved wardrobe stats for user {current_user.id}: {total_items} items")
        
        return {
            "success": True,
            "data": stats,
            "message": f"Wardrobe statistics retrieved successfully ({total_items} items found)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting wardrobe stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving wardrobe statistics: {str(e)}")

@router.get("/trending-styles")
async def get_trending_styles(
    current_user: UserProfile = Depends(get_current_user_optional)
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
                    days_since_worn = (int(time.time()) - item.get('lastWorn', 0)) / (24 * 60 * 60)
                    if days_since_worn < 7:
                        score += 2
                    elif days_since_worn < 30:
                        score += 1
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
    current_user: UserProfile = Depends(get_current_user_optional)
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
            "dominantColors": [{"name": item_data["color"], "hex": "#000000", "rgb": [0, 0, 0]}],
            "matchingColors": [],
            "tags": item_data.get("tags", []),
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "metadata": {
                "analysisTimestamp": int(time.time()),
                "originalType": item_data["type"],
                "styleTags": item_data.get("style", []),
                "occasionTags": item_data.get("occasion", []),
                "colorAnalysis": {
                    "dominant": [item_data["color"]],
                    "matching": []
                },
                "visualAttributes": {
                    "pattern": "solid",
                    "formalLevel": "casual",
                    "fit": "regular",
                    "material": "cotton",
                    "fabricWeight": "medium"
                },
                "itemMetadata": {
                    "tags": item_data.get("tags", []),
                    "careInstructions": "Check care label"
                }
            }
        }
        
        # Save to Firestore
        doc_ref = db.collection('wardrobe').document(item_id)
        doc_ref.set(wardrobe_item)
        
        # Log analytics event
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

@router.get("/")
async def get_wardrobe_items(
    current_user: UserProfile = Depends(get_current_user_optional)
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
        
        # Query Firestore for user's wardrobe items
        try:
            docs = db.collection('wardrobe').where('userId', '==', current_user.id).stream()
            print("🔍 DEBUG: Firestore query executed successfully")
        except Exception as db_error:
            print(f"🔍 DEBUG: Firestore query failed: {db_error}")
            logger.error(f"Firestore query failed: {db_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Database query failed: {str(db_error)}"
            )
        
        items = []
        errors = []
        
        for doc in docs:
            try:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                
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
    current_user: UserProfile = Depends(get_current_user_optional)
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
    current_user: UserProfile = Depends(get_current_user_optional)
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
    current_user: UserProfile = Depends(get_current_user_optional)
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
    current_user: UserProfile = Depends(get_current_user_optional)
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
    current_user: UserProfile = Depends(get_current_user_optional)
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
 