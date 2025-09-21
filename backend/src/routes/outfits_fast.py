"""
Fast Outfit Loading Routes

Provides lightning-fast outfit loading using pre-aggregated stats and metadata.
Designed to replace slow pagination with instant loading.
Updated for Railway deployment.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import logging
# from ..core.logging import get_logger  # Module doesn't exist
from ..custom_types.profile import UserProfile
from ..auth.auth_service import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/metadata")
async def get_outfits_metadata(
    current_user: UserProfile = Depends(get_current_user),
    limit: Optional[int] = Query(100, description="Number of outfits to return metadata for"),
    offset: Optional[int] = Query(0, description="Number of outfits to skip"),
    occasion: Optional[str] = Query(None, description="Filter by occasion"),
    style: Optional[str] = Query(None, description="Filter by style"),
    is_favorite: Optional[bool] = Query(None, description="Filter by favorite status"),
    sort_by: Optional[str] = Query("date-newest", description="Sort order: date-newest, date-oldest, wear-most, wear-least")
):
    """
    Get outfit metadata for fast grid loading.
    Returns lightweight outfit data optimized for UI rendering.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")

        from ..config.firebase import db
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")

        logger.info(f"Fetching outfit metadata for user {current_user.id} with limit={limit}, offset={offset}")

        # Build query
        query = db.collection('outfits').where('user_id', '==', current_user.id)
        
        # Apply filters
        if occasion:
            query = query.where('occasion', '==', occasion)
        if style:
            query = query.where('style', '==', style)
        if is_favorite is not None:
            query = query.where('isFavorite', '==', is_favorite)

        # Apply sorting
        if sort_by == "date-newest":
            query = query.order_by('createdAt', direction=db.Query.DESCENDING)
        elif sort_by == "date-oldest":
            query = query.order_by('createdAt', direction=db.Query.ASCENDING)
        elif sort_by == "wear-most":
            query = query.order_by('wearCount', direction=db.Query.DESCENDING)
        elif sort_by == "wear-least":
            query = query.order_by('wearCount', direction=db.Query.ASCENDING)
        else:
            query = query.order_by('createdAt', direction=db.Query.DESCENDING)

        # Apply pagination
        query = query.offset(offset).limit(limit)

        # Execute query
        docs = await query.stream()
        outfits_metadata = []
        
        async for doc in docs:
            data = doc.to_dict()
            
            # Create lightweight metadata object
            metadata = {
                'id': doc.id,
                'name': data.get('name', ''),
                'occasion': data.get('occasion', ''),
                'style': data.get('style', ''),
                'mood': data.get('mood', ''),
                'isFavorite': data.get('isFavorite', False),
                'isWorn': data.get('isWorn', False),
                'wearCount': data.get('wearCount', 0),
                'rating': data.get('rating'),
                'createdAt': data.get('createdAt'),
                'updatedAt': data.get('updatedAt'),
                'thumbnailUrl': data.get('thumbnailUrl', ''),
                # Include item count for UI
                'itemCount': len(data.get('items', [])),
                # Include first few item thumbnails for preview
                'itemPreviews': [
                    {
                        'id': item.get('id', ''),
                        'name': item.get('name', ''),
                        'imageUrl': item.get('imageUrl', ''),
                        'type': item.get('type', '')
                    }
                    for item in (data.get('items', [])[:4])  # First 4 items for preview
                ]
            }
            outfits_metadata.append(metadata)

        # Get total count for pagination (use stats document for speed)
        total_count = 0
        try:
            from ..services.user_stats_service import user_stats_service
            stats = await user_stats_service.get_user_stats(current_user.id)
            total_count = stats.get('outfits', {}).get('total', 0)
        except Exception as e:
            logger.warning(f"Could not get total count from stats: {e}")
            # Fallback to expensive count query
            count_query = db.collection('outfits').where('user_id', '==', current_user.id)
            if occasion:
                count_query = count_query.where('occasion', '==', occasion)
            if style:
                count_query = count_query.where('style', '==', style)
            if is_favorite is not None:
                count_query = count_query.where('isFavorite', '==', is_favorite)
            
            count_result = await count_query.count().get()
            total_count = count_result[0][0].value

        return {
            "success": True,
            "outfits": outfits_metadata,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total_count,
                "has_more": offset + len(outfits_metadata) < total_count
            },
            "filters": {
                "occasion": occasion,
                "style": style,
                "is_favorite": is_favorite,
                "sort_by": sort_by
            }
        }

    except Exception as e:
        logger.error(f"Error fetching outfit metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch outfit metadata: {e}")


@router.get("/summary")
async def get_outfits_summary(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get outfit collection summary for instant dashboard-style loading.
    Returns aggregated stats and recent outfits.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")

        from ..services.user_stats_service import user_stats_service
        
        # Get pre-aggregated stats
        stats = await user_stats_service.get_user_stats(current_user.id)
        
        if not stats:
            # Initialize stats if they don't exist
            await user_stats_service.initialize_user_stats(current_user.id)
            stats = await user_stats_service.get_user_stats(current_user.id)

        # Get recent outfits for quick preview
        from ..config.firebase import db
        if db:
            recent_query = db.collection('outfits').where('user_id', '==', current_user.id).order_by('createdAt', direction=db.Query.DESCENDING).limit(6)
            recent_docs = await recent_query.stream()
            
            recent_outfits = []
            async for doc in recent_docs:
                data = doc.to_dict()
                recent_outfits.append({
                    'id': doc.id,
                    'name': data.get('name', ''),
                    'thumbnailUrl': data.get('thumbnailUrl', ''),
                    'occasion': data.get('occasion', ''),
                    'createdAt': data.get('createdAt')
                })
        else:
            recent_outfits = []

        # Calculate quick stats
        outfit_stats = stats.get('outfits', {})
        
        return {
            "success": True,
            "summary": {
                "total_outfits": outfit_stats.get('total', 0),
                "outfits_this_week": outfit_stats.get('this_week', 0),
                "recent_outfits": recent_outfits,
                "last_updated": stats.get('last_updated')
            },
            "quick_stats": {
                "total": outfit_stats.get('total', 0),
                "favorites": 0,  # TODO: Add to stats service
                "worn_this_week": outfit_stats.get('this_week', 0),
                "never_worn": 0  # TODO: Add to stats service
            }
        }

    except Exception as e:
        logger.error(f"Error fetching outfit summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch outfit summary: {e}")


@router.get("/filter-options")
async def get_filter_options(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get available filter options for outfits.
    Pre-aggregated for fast filtering UI.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")

        from ..config.firebase import db
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")

        # Get unique values for filtering
        # This could be cached/pre-aggregated in the future
        query = db.collection('outfits').where('user_id', '==', current_user.id)
        docs = await query.stream()
        
        occasions = set()
        styles = set()
        moods = set()
        
        async for doc in docs:
            data = doc.to_dict()
            if data.get('occasion'):
                occasions.add(data.get('occasion'))
            if data.get('style'):
                styles.add(data.get('style'))
            if data.get('mood'):
                moods.add(data.get('mood'))

        return {
            "success": True,
            "filter_options": {
                "occasions": sorted(list(occasions)),
                "styles": sorted(list(styles)),
                "moods": sorted(list(moods)),
                "sort_options": [
                    {"value": "date-newest", "label": "Newest First"},
                    {"value": "date-oldest", "label": "Oldest First"},
                    {"value": "wear-most", "label": "Most Worn"},
                    {"value": "wear-least", "label": "Least Worn"}
                ]
            }
        }

    except Exception as e:
        logger.error(f"Error fetching filter options: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch filter options: {e}")
