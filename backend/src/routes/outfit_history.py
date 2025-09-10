from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile
from ..config.firebase import db
from ..core.logging import get_logger
from ..services.analytics_service import log_analytics_event

router = APIRouter(tags=["outfit-history"])
logger = get_logger(__name__)

db = db

@router.get("/")
async def get_outfit_history(
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user)
):
    """
    Mark an outfit as worn on a specific date
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        logger.info(f"👕 Marking outfit as worn for user {current_user.id}")
        logger.info(f"🔍 DEBUG: Received data: {data}")
        
        outfit_id = data.get('outfitId')
        date_worn = data.get('dateWorn')
        occasion = data.get('occasion', 'Casual')
        mood = data.get('mood', 'Comfortable')
        weather = data.get('weather', {})
        notes = data.get('notes', '')
        tags = data.get('tags', [])
        
        logger.info(f"🔍 DEBUG: Parsed outfit_id: {outfit_id}, date_worn: {date_worn}")
        
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
        try:
            logger.info(f"🔍 DEBUG: About to save outfit history entry to Firestore")
            logger.info(f"🔍 DEBUG: Entry data: {entry_data}")
            logger.info(f"🔍 DEBUG: User ID: {current_user.id}")
            logger.info(f"🔍 DEBUG: Outfit ID: {outfit_id}")
            logger.info(f"🔍 DEBUG: Date worn timestamp: {date_timestamp}")
            
            doc_ref, doc_id = db.collection('outfit_history').add(entry_data)
            logger.info(f"✅ Created outfit history entry with ID: {doc_id}")
            logger.info(f"🔍 DEBUG: Document reference: {doc_ref}")
            logger.info(f"🔍 DEBUG: Document ID: {doc_id}")
            
            # Verify the entry was actually saved
            saved_doc = doc_ref.get()
            if saved_doc.exists:
                saved_data = saved_doc.to_dict()
                logger.info(f"✅ VERIFIED: Entry saved successfully with data: {saved_data}")
            else:
                logger.error(f"❌ VERIFICATION FAILED: Document {doc_id} does not exist after save")
                
        except Exception as firestore_error:
            logger.error(f"❌ Failed to save to Firestore: {firestore_error}")
            logger.error(f"❌ Firestore error details: {str(firestore_error)}")
            raise HTTPException(status_code=500, detail="Failed to save outfit history entry")
        
        # Log analytics event (simplified to avoid serialization issues)
        try:
            # Create a simple dict instead of AnalyticsEvent object
            analytics_data = {
                "user_id": current_user.id,
                "event_type": "outfit_worn",
                "metadata": {
                    "outfit_id": outfit_id,
                    "date_worn": date_worn,
                    "occasion": occasion,
                    "mood": mood,
                    "weather": weather,
                    "source": "outfit_history_api"
                }
            }
            log_analytics_event(analytics_data)
            logger.info(f"✅ Analytics event logged for outfit {outfit_id}")
        except Exception as analytics_error:
            logger.warning(f"⚠️ Failed to log analytics event: {analytics_error}")
            # Don't fail the whole request if analytics fails
        
        logger.info(f"Successfully marked outfit {outfit_id} as worn for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Outfit marked as worn successfully",
            "entryId": str(doc_id)  # Ensure doc_id is serializable
        }
        
    except Exception as e:
        logger.error(f"Error marking outfit as worn: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to mark outfit as worn")

@router.patch("/{entry_id}")
async def update_outfit_history_entry(
    entry_id: str,
    updates: Dict[str, Any],
    current_user = Depends(get_current_user)
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
    current_user = Depends(get_current_user)
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
    current_user = Depends(get_current_user)
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
    current_user = Depends(get_current_user)
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

@router.get("/today-suggestion")
async def get_todays_outfit_suggestion(
    current_user = Depends(get_current_user)
):
    """
    Get or generate today's outfit suggestion for the current user.
    This generates a new outfit suggestion once per day and caches it.
    """
    print("⚡ HIT: today-suggestion from outfit_history.py")
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        logger.info(f"Getting today's outfit suggestion for user {current_user.id}")
        
        # Get today's date as a string for caching
        from datetime import datetime, timezone
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Check if firebase is available
        if not db:
            logger.warning("Firebase not available, returning fallback suggestion")
            return {
                "success": True,
                "suggestion": None,
                "isWorn": False,
                "message": "Service temporarily unavailable"
            }
        
        # Look for existing suggestion for today
        suggestions_ref = db.collection('daily_outfit_suggestions')
        query = suggestions_ref.where('user_id', '==', current_user.id).where('date', '==', today_str)
        existing_docs = list(query.stream())
        
        if existing_docs:
            # Return existing suggestion
            doc = existing_docs[0]
            suggestion_data = doc.to_dict()
            logger.info(f"Found existing suggestion for {today_str}")
            
            return {
                "success": True,
                "suggestion": {
                    "id": doc.id,
                    "outfitData": suggestion_data.get('outfit_data', {}),
                    "generatedAt": suggestion_data.get('generated_at'),
                    "date": suggestion_data.get('date')
                },
                "isWorn": suggestion_data.get('is_worn', False),
                "wornAt": suggestion_data.get('worn_at'),
                "message": "Today's outfit suggestion"
            }
        
        else:
            # Generate new suggestion for today
            logger.info(f"Generating new outfit suggestion for {today_str}")
            
            try:
                # Import outfit generation logic
                from ..routes.outfits import generate_outfit_logic, OutfitRequest
                
                # Create a default request for casual daily wear
                daily_request = OutfitRequest(
                    occasion="casual",
                    style="comfortable", 
                    mood="confident",
                    description="Daily outfit suggestion"
                )
                
                logger.info(f"About to generate outfit with request: {daily_request}")
                
                # Generate outfit using existing logic with timeout
                import asyncio
                try:
                    generated_outfit = await asyncio.wait_for(
                        generate_outfit_logic(daily_request, current_user.id),
                        timeout=30.0  # 30 second timeout
                    )
                    logger.info(f"Successfully generated outfit: {generated_outfit.get('name', 'Unknown')}")
                except asyncio.TimeoutError:
                    logger.error("Outfit generation timed out after 30 seconds")
                    raise Exception("Outfit generation timed out")
                except Exception as gen_error:
                    logger.error(f"Outfit generation failed: {gen_error}")
                    raise gen_error
                
                # Save suggestion to cache
                current_timestamp = int(datetime.utcnow().timestamp() * 1000)
                suggestion_doc = {
                    'user_id': current_user.id,
                    'date': today_str,
                    'outfit_data': generated_outfit,
                    'generated_at': current_timestamp,
                    'is_worn': False,
                    'worn_at': None,
                    'created_at': current_timestamp,
                    'updated_at': current_timestamp
                }
                
                # Save to Firestore
                doc_ref = db.collection('daily_outfit_suggestions').add(suggestion_doc)
                suggestion_id = doc_ref[1].id
                
                logger.info(f"Generated and saved new outfit suggestion {suggestion_id}")
                
                return {
                    "success": True,
                    "suggestion": {
                        "id": suggestion_id,
                        "outfitData": generated_outfit,
                        "generatedAt": current_timestamp,
                        "date": today_str
                    },
                    "isWorn": False,
                    "wornAt": None,
                    "message": "Generated new outfit suggestion for today"
                }
                
            except Exception as generation_error:
                logger.error(f"Failed to generate outfit suggestion: {generation_error}")
                
                # Create a simple fallback outfit with actual wardrobe items
                logger.info("Creating fallback outfit with user's wardrobe items")
                
                # Get user's wardrobe items for fallback
                from ..routes.outfits import get_user_wardrobe
                try:
                    wardrobe_items = await get_user_wardrobe(current_user.id)
                    logger.info(f"Retrieved {len(wardrobe_items)} wardrobe items for fallback")
                    
                    # Simple fallback logic: pick basic items
                    selected_items = []
                    categories_needed = ['tops', 'bottoms']  # Basic outfit needs
                    
                    for category in categories_needed:
                        # Find items in this category
                        category_items = [item for item in wardrobe_items if item.get('type', '').lower() in [category[:-1], category]]  # 'top'/'tops', 'bottom'/'bottoms'
                        if category_items:
                            # Pick the first suitable item
                            selected_items.append(category_items[0])
                            logger.info(f"Selected {category_items[0].get('name', 'Unknown')} for {category}")
                    
                    # Add a jacket/outerwear if available
                    outerwear = [item for item in wardrobe_items if item.get('type', '').lower() in ['jacket', 'outerwear', 'blazer', 'cardigan']]
                    if outerwear:
                        selected_items.append(outerwear[0])
                        logger.info(f"Added outerwear: {outerwear[0].get('name', 'Unknown')}")
                    
                    fallback_outfit = {
                        "name": "Today's Casual Look",
                        "occasion": "casual",
                        "style": "comfortable",
                        "mood": "confident",
                        "description": "A simple, comfortable outfit for your day",
                        "items": selected_items,  # Actual wardrobe items
                        "imageUrl": "",
                        "weather": {}
                    }
                    
                    logger.info(f"Created fallback outfit with {len(selected_items)} items")
                    
                except Exception as wardrobe_error:
                    logger.error(f"Failed to get wardrobe items for fallback: {wardrobe_error}")
                    # Ultimate fallback with empty items
                    fallback_outfit = {
                        "name": "Today's Casual Look",
                        "occasion": "casual",
                        "style": "comfortable",
                        "mood": "confident",
                        "description": "A simple, comfortable outfit for your day",
                        "items": [],
                        "imageUrl": "",
                        "weather": {}
                    }
                
                # Save fallback suggestion to cache
                try:
                    current_timestamp = int(datetime.utcnow().timestamp() * 1000)
                    fallback_doc = {
                        'user_id': current_user.id,
                        'date': today_str,
                        'outfit_data': fallback_outfit,
                        'generated_at': current_timestamp,
                        'is_worn': False,
                        'worn_at': None,
                        'created_at': current_timestamp,
                        'updated_at': current_timestamp,
                        'is_fallback': True  # Mark as fallback
                    }
                    
                    doc_ref = db.collection('daily_outfit_suggestions').add(fallback_doc)
                    suggestion_id = doc_ref[1].id
                    
                    logger.info(f"Created fallback outfit suggestion {suggestion_id}")
                    
                    return {
                        "success": True,
                        "suggestion": {
                            "id": suggestion_id,
                            "outfitData": fallback_outfit,
                            "generatedAt": current_timestamp,
                            "date": today_str
                        },
                        "isWorn": False,
                        "wornAt": None,
                        "message": "Daily outfit suggestion (simplified)"
                    }
                    
                except Exception as fallback_error:
                    logger.error(f"Failed to save fallback suggestion: {fallback_error}")
                    return {
                        "success": True,
                        "suggestion": None,
                        "isWorn": False,
                        "message": "Could not generate outfit suggestion today"
                    }
        
    except Exception as e:
        logger.error(f"Error getting today's outfit suggestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get today's outfit suggestion")

@router.post("/today-suggestion/wear")
async def mark_today_suggestion_as_worn(
    data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """
    Mark today's outfit suggestion as worn.
    This creates an outfit history entry and updates the suggestion status.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        suggestion_id = data.get('suggestionId')
        if not suggestion_id:
            raise HTTPException(status_code=400, detail="suggestionId is required")
            
        logger.info(f"Marking today's suggestion {suggestion_id} as worn for user {current_user.id}")
        
        # Check if firebase is available
        if not db:
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        # Get the suggestion document
        suggestion_ref = db.collection('daily_outfit_suggestions').document(suggestion_id)
        suggestion_doc = suggestion_ref.get()
        
        if not suggestion_doc.exists:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        suggestion_data = suggestion_doc.to_dict()
        
        # Verify ownership
        if suggestion_data.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if already worn
        if suggestion_data.get('is_worn'):
            return {
                "success": True,
                "message": "Suggestion already marked as worn",
                "alreadyWorn": True
            }
        
        # Mark suggestion as worn
        current_timestamp = int(datetime.utcnow().timestamp() * 1000)
        suggestion_ref.update({
            'is_worn': True,
            'worn_at': current_timestamp,
            'updated_at': current_timestamp
        })
        
        # Create outfit history entry
        outfit_data = suggestion_data.get('outfit_data', {})
        history_entry = {
            'user_id': current_user.id,
            'outfit_id': f"suggestion_{suggestion_id}",  # Special ID for suggested outfits
            'outfit_name': outfit_data.get('name', 'Daily Suggestion'),
            'outfit_image': outfit_data.get('imageUrl', ''),
            'date_worn': current_timestamp,
            'occasion': 'Daily Suggestion',
            'mood': 'Confident',
            'weather': {},
            'notes': 'Generated daily outfit suggestion',
            'tags': ['daily-suggestion'],
            'created_at': current_timestamp,
            'updated_at': current_timestamp,
            'suggestion_id': suggestion_id  # Link back to the suggestion
        }
        
        # Save to outfit history
        db.collection('outfit_history').add(history_entry)
        
        # Log analytics event
        try:
            from ..models.analytics_event import AnalyticsEvent
            analytics_event = AnalyticsEvent(
                user_id=current_user.id,
                event_type="daily_suggestion_worn",
                metadata={
                    "suggestion_id": suggestion_id,
                    "outfit_name": outfit_data.get('name', 'Daily Suggestion'),
                    "date": suggestion_data.get('date'),
                    "source": "daily_outfit_suggestion"
                }
            )
            from ..services.analytics_service import log_analytics_event
            log_analytics_event(analytics_event)
        except Exception as analytics_error:
            logger.warning(f"Failed to log analytics: {analytics_error}")
        
        logger.info(f"Successfully marked suggestion {suggestion_id} as worn")
        
        return {
            "success": True,
            "message": "Daily outfit suggestion marked as worn",
            "wornAt": current_timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking suggestion as worn: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to mark suggestion as worn")

# Force redeploy Sun Aug 17 07:23:59 EDT 2025
