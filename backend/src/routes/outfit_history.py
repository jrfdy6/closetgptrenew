from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

from ..auth.auth_service import get_current_user_optional
from ..custom_types.profile import UserProfile
from ..config.firebase import db
from ..core.logging import get_logger
from ..services.analytics_service import log_analytics_event

router = APIRouter(tags=["outfit-history"])
logger = get_logger(__name__)

db = db

@router.get("/")
async def get_outfit_history(
    current_user = Depends(get_current_user_optional),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    outfit_id: Optional[str] = Query(None, description="Filter by specific outfit ID"),
    limit: Optional[int] = Query(100, description="Number of entries to return")
):
    """
    Get user's outfit history entries
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        logger.info(f"Fetching outfit history for user {current_user.id}")
        
        # Query outfit_history collection
        query = db.collection('outfit_history').where('user_id', '==', current_user.id)
        
        # Add outfit_id filter if provided
        if outfit_id:
            query = query.where('outfit_id', '==', outfit_id)
        
        # Add date filters if provided
        if start_date:
            start_timestamp = datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000
            query = query.where('date_worn', '>=', start_timestamp)
        
        if end_date:
            end_timestamp = datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000
            query = query.where('date_worn', '<=', end_timestamp)
        
        # Limit results before ordering (Firestore requirement)
        if limit:
            query = query.limit(limit)
        
        # Order by date worn (newest first) - only if we have documents
        try:
            query = query.order_by('date_worn', direction=db.Query.DESCENDING)
        except Exception as e:
            logger.warning(f"Could not order by date_worn: {e}")
        
        # Execute query
        docs = query.stream()
        
        outfit_history = []
        for doc in docs:
            data = doc.to_dict()
            outfit_history.append({
                "id": doc.id,
                "outfitId": data.get('outfit_id'),
                "outfitName": data.get('outfit_name', 'Unknown Outfit'),
                "outfitImage": data.get('outfit_image', ''),
                "dateWorn": data.get('date_worn'),
                "weather": data.get('weather', {
                    "temperature": 0,
                    "condition": "Unknown",
                    "humidity": 0
                }),
                "occasion": data.get('occasion', 'Casual'),
                "mood": data.get('mood', 'Comfortable'),
                "notes": data.get('notes', ''),
                "tags": data.get('tags', []),
                "createdAt": data.get('created_at'),
                "updatedAt": data.get('updated_at')
            })
        
        logger.info(f"Retrieved {len(outfit_history)} outfit history entries for user {current_user.id}")
        
        return {
            "success": True,
            "outfitHistory": outfit_history
        }
        
    except Exception as e:
        logger.error(f"Error fetching outfit history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch outfit history")

@router.post("/mark-worn")
async def mark_outfit_as_worn(
    data: Dict[str, Any],
    current_user = Depends(get_current_user_optional)
):
    """
    Mark an outfit as worn on a specific date
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        logger.info(f"Marking outfit as worn for user {current_user.id}")
        
        outfit_id = data.get('outfitId')
        date_worn = data.get('dateWorn')
        occasion = data.get('occasion', 'Casual')
        mood = data.get('mood', 'Comfortable')
        weather = data.get('weather', {})
        notes = data.get('notes', '')
        tags = data.get('tags', [])
        
        if not outfit_id or not date_worn:
            raise HTTPException(status_code=400, detail="outfitId and dateWorn are required")
        
        # Convert date string to timestamp
        if isinstance(date_worn, str):
            date_obj = datetime.strptime(date_worn, '%Y-%m-%d')
            date_timestamp = int(date_obj.timestamp() * 1000)
        else:
            date_timestamp = date_worn
        
        # Get outfit details from outfits collection
        outfit_doc = db.collection('outfits').document(outfit_id).get()
        outfit_data = outfit_doc.to_dict() if outfit_doc.exists else {}
        
        # Extract item IDs from the outfit
        item_ids = []
        if outfit_data.get('items'):
            for item in outfit_data['items']:
                if isinstance(item, dict) and 'id' in item:
                    item_ids.append(item['id'])
                elif isinstance(item, str):
                    item_ids.append(item)
        
        # Increment wear count for all items in the outfit
        current_timestamp = int(datetime.utcnow().timestamp() * 1000)
        if item_ids:
            batch = db.batch()
            wardrobe_ref = db.collection('wardrobe')
            
            for item_id in item_ids:
                item_ref = wardrobe_ref.document(item_id)
                item_doc = item_ref.get()
                
                if item_doc.exists:
                    item_data = item_doc.to_dict()
                    current_wear_count = item_data.get('wearCount', 0)
                    
                    # Update wear count and last worn timestamp
                    batch.update(item_ref, {
                        'wearCount': current_wear_count + 1,
                        'lastWorn': current_timestamp,
                        'updatedAt': current_timestamp
                    })
            
            # Commit the batch update
            batch.commit()
            logger.info(f"Updated wear counts for {len(item_ids)} items in outfit {outfit_id}")
        
        # Create outfit history entry
        entry_data = {
            'user_id': current_user.id,
            'outfit_id': outfit_id,
            'outfit_name': outfit_data.get('name', 'Unknown Outfit'),
            'outfit_image': '',  # We'll leave this empty for now since items are stored as strings
            'date_worn': date_timestamp,
            'occasion': occasion,
            'mood': mood,
            'weather': weather,
            'notes': notes,
            'tags': tags,
            'created_at': current_timestamp,
            'updated_at': current_timestamp
        }
        
        # Save to Firestore
        doc_ref = db.collection('outfit_history').add(entry_data)
        
        # Log analytics event
        from ..models.analytics_event import AnalyticsEvent
        analytics_event = AnalyticsEvent(
            user_id=current_user.id,
            event_type="outfit_worn",
            metadata={
                "outfit_id": outfit_id,
                "date_worn": date_worn,
                "occasion": occasion,
                "mood": mood,
                "weather": weather,
                "source": "outfit_history_api"
            }
        )
        log_analytics_event(analytics_event)
        
        logger.info(f"Successfully marked outfit {outfit_id} as worn for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Outfit marked as worn successfully",
            "entryId": doc_ref[1].id
        }
        
    except Exception as e:
        logger.error(f"Error marking outfit as worn: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to mark outfit as worn")

@router.patch("/{entry_id}")
async def update_outfit_history_entry(
    entry_id: str,
    updates: Dict[str, Any],
    current_user = Depends(get_current_user_optional)
):
    """
    Update an outfit history entry
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        logger.info(f"Updating outfit history entry {entry_id} for user {current_user.id}")
        
        # Get the entry
        doc_ref = db.collection('outfit_history').document(entry_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        entry_data = doc.to_dict()
        
        # Verify ownership
        if entry_data.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this entry")
        
        # Prepare update data
        update_data = {
            'updated_at': int(datetime.utcnow().timestamp() * 1000)
        }
        
        # Map frontend field names to database field names
        field_mapping = {
            'occasion': 'occasion',
            'mood': 'mood',
            'weather': 'weather',
            'notes': 'notes',
            'tags': 'tags'
        }
        
        for frontend_field, db_field in field_mapping.items():
            if frontend_field in updates:
                update_data[db_field] = updates[frontend_field]
        
        # Update the document
        doc_ref.update(update_data)
        
        # Log analytics event
        from ..models.analytics_event import AnalyticsEvent
        analytics_event = AnalyticsEvent(
            user_id=current_user.id,
            event_type="outfit_history_updated",
            metadata={
                "entry_id": entry_id,
                "outfit_id": entry_data.get('outfit_id'),
                "updates": updates,
                "source": "outfit_history_api"
            }
        )
        log_analytics_event(analytics_event)
        
        logger.info(f"Successfully updated outfit history entry {entry_id}")
        
        return {
            "success": True,
            "message": "Outfit history entry updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating outfit history entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update outfit history entry")

@router.delete("/{entry_id}")
async def delete_outfit_history_entry(
    entry_id: str,
    current_user = Depends(get_current_user_optional)
):
    """
    Delete an outfit history entry
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        logger.info(f"Deleting outfit history entry {entry_id} for user {current_user.id}")
        
        # Get the entry
        doc_ref = db.collection('outfit_history').document(entry_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        entry_data = doc.to_dict()
        
        # Verify ownership
        if entry_data.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this entry")
        
        # Delete the document
        doc_ref.delete()
        
        # Log analytics event
        from ..models.analytics_event import AnalyticsEvent
        analytics_event = AnalyticsEvent(
            user_id=current_user.id,
            event_type="outfit_history_deleted",
            metadata={
                "entry_id": entry_id,
                "outfit_id": entry_data.get('outfit_id'),
                "outfit_name": entry_data.get('outfit_name'),
                "date_worn": entry_data.get('date_worn'),
                "occasion": entry_data.get('occasion'),
                "mood": entry_data.get('mood'),
                "source": "outfit_history_api"
            }
        )
        log_analytics_event(analytics_event)
        
        logger.info(f"Successfully deleted outfit history entry {entry_id}")
        
        return {
            "success": True,
            "message": "Outfit history entry deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting outfit history entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete outfit history entry")

@router.get("/stats")
async def get_outfit_history_stats(
    current_user = Depends(get_current_user_optional)
):
    """
    Get outfit history statistics
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        logger.info(f"Getting outfit history stats for user {current_user.id}")
        
        # Query outfit history
        query = db.collection('outfit_history').where('user_id', '==', current_user.id)
        docs = query.stream()
        
        entries = [doc.to_dict() for doc in docs]
        
        if not entries:
            return {
                "success": True,
                "stats": {
                    "totalEntries": 0,
                    "uniqueOutfits": 0,
                    "mostWornOutfit": None,
                    "favoriteOccasion": None,
                    "favoriteMood": None,
                    "weatherPatterns": {}
                }
            }
        
        # Calculate statistics
        total_entries = len(entries)
        unique_outfits = len(set(entry.get('outfit_id') for entry in entries))
        
        # Most worn outfit
        outfit_counts = {}
        for entry in entries:
            outfit_id = entry.get('outfit_id')
            outfit_counts[outfit_id] = outfit_counts.get(outfit_id, 0) + 1
        
        most_worn_outfit = max(outfit_counts.items(), key=lambda x: x[1]) if outfit_counts else None
        
        # Favorite occasion and mood
        occasion_counts = {}
        mood_counts = {}
        for entry in entries:
            occasion = entry.get('occasion', 'Casual')
            mood = entry.get('mood', 'Comfortable')
            occasion_counts[occasion] = occasion_counts.get(occasion, 0) + 1
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        favorite_occasion = max(occasion_counts.items(), key=lambda x: x[1])[0] if occasion_counts else None
        favorite_mood = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else None
        
        # Weather patterns
        weather_patterns = {}
        for entry in entries:
            weather = entry.get('weather', {})
            condition = weather.get('condition', 'Unknown')
            weather_patterns[condition] = weather_patterns.get(condition, 0) + 1
        
        stats = {
            "totalEntries": total_entries,
            "uniqueOutfits": unique_outfits,
            "mostWornOutfit": {
                "outfitId": most_worn_outfit[0],
                "count": most_worn_outfit[1]
            } if most_worn_outfit else None,
            "favoriteOccasion": favorite_occasion,
            "favoriteMood": favorite_mood,
            "weatherPatterns": weather_patterns
        }
        
        logger.info(f"Retrieved outfit history stats for user {current_user.id}")
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting outfit history stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get outfit history stats")
@router.get("/today")
async def get_todays_outfit(
    current_user = Depends(get_current_user_optional)
):
    """
    Get today's outfit for the current user
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        logger.info(f"Getting today's outfit for user {current_user.id}")
        
        # Get today's date range (start of day to end of day)
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        # Convert to timestamps for Firestore query
        start_timestamp = int(start_of_day.timestamp() * 1000)
        end_timestamp = int(end_of_day.timestamp() * 1000)
        
        logger.info(f"Querying outfit history for today: {start_timestamp} to {end_timestamp}")
        
        # Check if firebase is available
        if not db:
            logger.warning("Firebase not available, returning empty today's outfit")
            return {
                "success": True,
                "todaysOutfit": None,
                "hasOutfitToday": False,
                "message": "Database not available"
            }
        
        # Query outfit history for today
        query = db.collection('outfit_history').where('user_id', '==', current_user.id)
        query = query.where('date_worn', '>=', start_timestamp)
        query = query.where('date_worn', '<=', end_timestamp)
        
        # Execute query with enhanced error handling
        todays_outfits = []
        try:
            docs = query.stream()
            
            for doc in docs:
                try:
                    data = doc.to_dict()
                    todays_outfits.append({
                        "id": doc.id,
                        "outfitId": data.get('outfit_id'),
                        "outfitName": data.get('outfit_name', 'Today\'s Outfit'),
                        "outfitImage": data.get('outfit_image', ''),
                        "dateWorn": data.get('date_worn'),
                        "weather": data.get('weather', {
                            "temperature": 0,
                            "condition": "Unknown",
                            "humidity": 0
                        }),
                        "occasion": data.get('occasion', 'Casual'),
                        "mood": data.get('mood', 'Comfortable'),
                        "notes": data.get('notes', ''),
                        "tags": data.get('tags', []),
                        "createdAt": data.get('created_at'),
                        "updatedAt": data.get('updated_at')
                    })
                except Exception as doc_error:
                    logger.warning(f"Error processing outfit history document {doc.id}: {doc_error}")
                    continue
                    
        except Exception as query_error:
            logger.error(f"Error executing outfit history query: {query_error}")
            # Return empty result gracefully
            return {
                "success": True,
                "todaysOutfit": None,
                "hasOutfitToday": False,
                "message": "Could not retrieve today's outfit data"
            }
        
        logger.info(f"Retrieved {len(todays_outfits)} today's outfits for user {current_user.id}")
        
        return {
            "success": True,
            "todaysOutfit": todays_outfits[0] if todays_outfits else None,
            "hasOutfitToday": len(todays_outfits) > 0
        }
        
    except Exception as e:
        logger.error(f"Error getting today's outfit: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get today's outfit")

# Force redeploy Sun Aug 17 07:23:59 EDT 2025
