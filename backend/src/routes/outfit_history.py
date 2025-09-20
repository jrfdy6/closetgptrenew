from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import time

def parse_last_worn(ts):
    """
    Safely parse lastWorn timestamps into timezone-aware UTC datetimes.
    Handles both:
    - Offset-aware ISO strings (with Z or +hh:mm)
    - Offset-naive ISO strings (assume UTC)
    Returns None if parsing fails.
    """
    if not ts:
        return None
    try:
        if isinstance(ts, str):
            if ts.endswith("Z"):
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        elif hasattr(ts, 'timestamp'):
            # Firestore timestamp - already timezone aware
            return ts
        elif isinstance(ts, datetime):
            # Already a datetime - ensure timezone aware
            if ts.tzinfo is None:
                return ts.replace(tzinfo=timezone.utc)
            return ts
        else:
            return None
    except Exception as e:
        # Use print instead of logger since logger isn't defined yet
        print(f"Failed to parse lastWorn timestamp '{ts}': {e}")
        return None
# Firebase imports moved inside functions to prevent import-time crashes
# from google.cloud import firestore
# from ..config.firebase import db
from ..auth.auth_service import get_current_user  # Keep this for dependency injection
from ..custom_types.profile import UserProfile   # Keep this for type hints
from ..core.logging import get_logger
from ..services.analytics_service import log_analytics_event

router = APIRouter(tags=["outfit-history"])
logger = get_logger(__name__)
# Force Railway redeploy - outfit history routes should work

async def calculate_worn_outfits_this_week(user_id: str) -> int:
    """
    Calculate how many outfits were worn this week.
    Checks both 'outfits' and 'outfit_history' collections.
    Uses timezone-safe datetime parsing to avoid comparison errors.
    """
    try:
        from ..config.firebase import db
        if not db:
            return 0
        
        # Get start and end of current week (Monday to Sunday) - timezone aware
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        logger.info(f"🗓️ Checking outfits worn between {week_start} and {week_end}")
        
        # 1️⃣ Check outfits collection for lastWorn
        outfits_ref = db.collection('outfits').where('user_id', '==', user_id)
        outfits_worn_count = 0
        
        docs = outfits_ref.stream()
        for doc in docs:
            data = doc.to_dict()
            last_worn_raw = data.get('lastWorn')
            
            # Use the safe parser
            last_worn_dt = parse_last_worn(last_worn_raw)
            
            if last_worn_dt and week_start <= last_worn_dt <= week_end:
                outfits_worn_count += 1
                logger.info(f"👕 Outfit {doc.id} worn this week: {last_worn_dt}")
        
        # 2️⃣ Check outfit_history collection for date_worn
        history_ref = db.collection('outfit_history').where('user_id', '==', user_id)
        unique_outfits_from_history = set()
        
        history_docs = history_ref.stream()
        for doc in history_docs:
            data = doc.to_dict()
            date_worn_raw = data.get('date_worn')
            outfit_id = data.get('outfit_id')
            
            # Use the safe parser for date_worn
            date_worn_dt = parse_last_worn(date_worn_raw)
            
            if date_worn_dt and week_start <= date_worn_dt <= week_end and outfit_id:
                unique_outfits_from_history.add(outfit_id)
                logger.info(f"📅 Outfit {outfit_id} worn this week (from history): {date_worn_dt}")
        
        history_worn_count = len(unique_outfits_from_history)
        
        # 3️⃣ Combine results (prioritize history if both exist)
        total_worn = max(outfits_worn_count, history_worn_count)
        
        logger.info(f"📊 Worn outfits this week - Outfits collection: {outfits_worn_count}, History collection: {history_worn_count}, Total: {total_worn}")
        
        return total_worn
        
    except Exception as e:
        logger.error(f"❌ Error calculating worn outfits this week: {e}")
        return 0

# Firebase will be imported inside functions to prevent import-time crashes
db = None

def get_db():
    """Get Firebase database client, importing it when needed"""
    try:
        from ..config.firebase import db
        return db
    except ImportError as e:
        logger.warning(f"⚠️ Firebase import failed: {e}")
        raise HTTPException(status_code=500, detail="Database service unavailable")

def serialize_firestore_doc(doc):
    """Serialize Firestore document, converting Timestamps to ISO strings"""
    data = doc.to_dict()
    
    # Convert Firestore Timestamps to ISO strings
    try:
        from firebase_admin import firestore
    for key, value in data.items():
        if isinstance(value, firestore.Timestamp):
            data[key] = value.isoformat()
        elif isinstance(value, dict) and 'seconds' in value and 'nanoseconds' in value:
            # Handle Firestore Timestamp dict format
            try:
                timestamp = firestore.Timestamp(seconds=value['seconds'], nanoseconds=value['nanoseconds'])
                data[key] = timestamp.isoformat()
            except:
                pass  # Keep original value if conversion fails
    except ImportError:
        # If firestore import fails, just return the data as-is
        pass
    
    return data

@router.get("/")
async def get_outfit_history(
    current_user: UserProfile = Depends(get_current_user),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    outfit_id: Optional[str] = Query(None, description="Filter by specific outfit ID"),
    limit: Optional[int] = Query(100, description="Number of entries to return")
):
    """
    Get user's outfit history entries
    """
    # Import Firebase inside function to prevent import-time crashes
    try:
        from google.cloud import firestore
        from ..config.firebase import db
    except ImportError as e:
        logger.warning(f"⚠️ Firebase import failed: {e}")
        raise HTTPException(status_code=500, detail="Database service unavailable")
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        logger.info(f"Fetching outfit history for user {current_user.id}")
        
        # Query outfit_history collection
        db = get_db()
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
    current_user: UserProfile = Depends(get_current_user)
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
        
        # Get Firebase database client
        db = get_db()
        
        # Convert date string to timestamp
        if isinstance(date_worn, str):
            date_obj = datetime.strptime(date_worn, '%Y-%m-%d')
            date_timestamp = int(date_obj.timestamp() * 1000)
        else:
            date_timestamp = date_worn
        
        # Get outfit details from outfits collection
        db = get_db()
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
            logger.info(f"🔍 DEBUG: Entry data: user_id={entry_data.get('user_id')}, date={entry_data.get('date')}, outfit_id={entry_data.get('outfit_id')}")
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
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Update an outfit history entry
    """
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
            
        logger.info(f"Updating outfit history entry {entry_id} for user {current_user.id}")
        
        # Get the entry
        db = get_db()
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
    current_user: UserProfile = Depends(get_current_user)
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

@router.get("/today")
async def get_todays_outfit(
    current_user: UserProfile = Depends(get_current_user)
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
    current_user: UserProfile = Depends(get_current_user)
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
            outfit_data = suggestion_data.get('outfit_data', {})
            items = outfit_data.get('items', [])
            
            # Check if the cached suggestion contains mock items (old fallback items)
            has_mock_items = any(
                item.get('id', '').startswith('fallback-') or 
                item.get('name', '').endswith(' Top') or 
                item.get('name', '').endswith(' Pants') or 
                item.get('name', '').endswith(' Shoes')
                for item in items
            )
            
            if has_mock_items:
                logger.info(f"Found cached suggestion with mock items, regenerating for {today_str}")
                # Delete the old suggestion with mock items
                doc.reference.delete()
                # Continue to generate a new suggestion below
            else:
                logger.info(f"Found existing suggestion for {today_str}")
                return {
                    "success": True,
                    "suggestion": {
                        "id": doc.id,
                        "outfitData": outfit_data,
                        "generatedAt": suggestion_data.get('generated_at'),
                        "date": suggestion_data.get('date')
                    },
                    "isWorn": suggestion_data.get('is_worn', False),
                    "wornAt": suggestion_data.get('worn_at'),
                    "message": "Today's outfit suggestion"
                }
        
        # Generate new suggestion for today (either no existing suggestion or regenerating due to mock items)
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
            
            logger.info(f"About to generate outfit with request: style={daily_request.style}, occasion={daily_request.occasion}, items_count={len(daily_request.wardrobe) if daily_request.wardrobe else 0}")
            
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

@router.delete("/today-suggestion/clear-cache")
async def clear_todays_suggestion_cache(
    current_user: UserProfile = Depends(get_current_user)
):
    """Clear today's outfit suggestion cache for the current user."""
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
        
        logger.info(f"Clearing today's outfit suggestion cache for user {current_user.id}")
        
        # Get today's date
        from datetime import datetime, timezone
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Check if firebase is available
        if not db:
            return {
                "success": False,
                "message": "Firebase not available"
            }
        
        # Delete all suggestions for today
        suggestions_ref = db.collection('daily_outfit_suggestions')
        query = suggestions_ref.where('user_id', '==', current_user.id).where('date', '==', today_str)
        existing_docs = list(query.stream())
        
        deleted_count = 0
        for doc in existing_docs:
            doc.reference.delete()
            deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} cached suggestions for user {current_user.id}")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Cleared {deleted_count} cached suggestions for today"
        }
        
    except Exception as e:
        logger.error(f"Error clearing suggestion cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear suggestion cache")

@router.post("/today-suggestion/wear")
async def mark_today_suggestion_as_worn(
    data: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_user)
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

@router.get("/stats")
async def get_outfit_history_stats(
    current_user: UserProfile = Depends(get_current_user),
    days: int = Query(7, description="Number of days to look back for stats")
):
    """Get outfit statistics from pre-aggregated user stats document - LIGHTNING FAST!"""
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
        
        logger.info(f"Getting pre-aggregated stats for user {current_user.id}")
        
        # Import and use the stats service
        from ..services.user_stats_service import user_stats_service
        
        # Get stats from single document read (fast!)
        stats_data = await user_stats_service.get_user_stats(current_user.id)
        
        # Extract outfit stats
        outfit_stats = stats_data.get("outfits", {})
        wardrobe_stats = stats_data.get("wardrobe", {})
        
        # Calculate worn outfits this week on-the-fly (until stats are properly tracking this)
        worn_this_week = await calculate_worn_outfits_this_week(current_user.id)
        
        # Format for frontend compatibility
        response_stats = {
            "total_outfits": outfit_stats.get("total", 0),
            "outfits_this_week": worn_this_week,  # Show actual worn count
            "totalThisWeek": worn_this_week,  # Frontend compatibility
            "days_queried": days,
            "recent_outfits": [],  # Could be populated if needed
            "wardrobe_total": wardrobe_stats.get("total_items", 0),
            "wardrobe_favorites": wardrobe_stats.get("favorites", 0),
            "last_updated": stats_data.get("last_updated"),
            "date_range": {
                "start": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(),
                "end": datetime.now(timezone.utc).isoformat()
            }
        }
        
        logger.info(f"Fast stats retrieved: {response_stats['total_outfits']} total outfits, {response_stats['outfits_this_week']} this week")
        
        return {
            "success": True,
            "data": response_stats,
            "message": f"Pre-aggregated stats (updated: {stats_data.get('last_updated', 'unknown')})",
            **response_stats  # Also return stats at root level for compatibility
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pre-aggregated stats: {str(e)}")
        
        # Return a working fallback response
        return {
            "success": False,
            "data": {
                "total_outfits": 1500,  # Use known count
                "outfits_this_week": 0,
                "totalThisWeek": 0,
                "days_queried": days,
                "recent_outfits": [],
                "wardrobe_total": 155,  # Use known count
                "wardrobe_favorites": 0,
                "date_range": {
                    "start": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(),
                    "end": datetime.now(timezone.utc).isoformat()
                }
            },
            "error": f"Stats service failed: {str(e)}",
            "message": "Using fallback stats",
            "total_outfits": 1500,
            "outfits_this_week": 0,
            "totalThisWeek": 0
        }

@router.get("/debug-user-docs")
async def debug_user_outfit_history(
    user_id: str = Query(..., description="User ID to debug"),
    current_user: UserProfile = Depends(get_current_user)
):
    """
    DEBUG endpoint:
    Fetches all outfit-related documents for a given user and logs details.
    Useful to verify data, timestamps, and collection/field structure.
    """
    try:
        from ..config.firebase import db
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Check both collections that might contain worn outfit data
        collections_to_check = ["outfits", "outfit_history"]
        all_results = {}
        
        for collection_name in collections_to_check:
            logger.info(f"🔍 Checking collection: {collection_name}")
            collection_ref = db.collection(collection_name)
            query = collection_ref.where("user_id", "==", user_id)
            docs = query.stream()

            collection_docs = []
            for doc in docs:
                doc_data = doc.to_dict()
                logger.info(f"📄 {collection_name} doc ID: {doc.id}")
                logger.info(f"📄 {collection_name} doc data: {doc_data}")
                
                # Special attention to timestamp fields
                timestamp_fields = ["lastWorn", "date_worn", "createdAt", "updatedAt"]
                for field in timestamp_fields:
                    if field in doc_data:
                        value = doc_data[field]
                        logger.info(f"🕐 Timestamp field '{field}': {value} (type: {type(value)})")
                
                collection_docs.append({"id": doc.id, "data": doc_data})

            all_results[collection_name] = {
                "count": len(collection_docs),
                "documents": collection_docs
            }
            
            if not collection_docs:
                logger.info(f"❌ No documents found in {collection_name} for user_id={user_id}")
            else:
                logger.info(f"✅ Found {len(collection_docs)} documents in {collection_name}")

        # Now let's test our worn calculation logic with the actual data
        logger.info(f"🧮 Testing worn outfit calculation for user {user_id}")
        worn_count = await calculate_worn_outfits_this_week(user_id)
        logger.info(f"🧮 calculate_worn_outfits_this_week returned: {worn_count}")

        return {
            "success": True,
            "user_id": user_id,
            "collections_checked": collections_to_check,
            "results": all_results,
            "worn_this_week_calculation": worn_count,
            "debug_info": {
                "current_week_start": datetime.now(timezone.utc) - timedelta(days=datetime.now(timezone.utc).weekday()),
                "current_time": datetime.now(timezone.utc).isoformat()
            }
        }

    except Exception as e:
        logger.error(f"❌ Error in debug endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to debug outfit docs: {e}")

@router.post("/seed-test-data")
async def seed_test_worn_data(
    user_id: str = Query(..., description="User ID to seed data for"),
    current_user: UserProfile = Depends(get_current_user)
):
    """
    DEVELOPMENT ONLY: Seed test worn outfit data for verification.
    Creates test entries in both outfits and outfit_history collections.
    """
    try:
        from ..config.firebase import db
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get current week boundaries
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info(f"🌱 Seeding test data for user {user_id}, week starting {week_start}")
        
        # Create test outfit entries with lastWorn this week
        test_outfits = []
        for i in range(3):  # Create 3 test worn outfits
            outfit_id = f"test_outfit_{i+1}_{int(now.timestamp())}"
            worn_date = week_start + timedelta(days=i+1, hours=10)  # Different days this week
            
            outfit_data = {
                "id": outfit_id,
                "user_id": user_id,
                "name": f"Test Outfit {i+1}",
                "style": "casual",
                "occasion": "daily",
                "items": [],
                "lastWorn": worn_date,
                "wearCount": 1,
                "createdAt": worn_date - timedelta(days=7),
                "updatedAt": worn_date
            }
            
            # Save to outfits collection
            db.collection('outfits').document(outfit_id).set(outfit_data)
            test_outfits.append(outfit_id)
            logger.info(f"✅ Created test outfit {outfit_id} with lastWorn: {worn_date}")
        
        # Create test outfit_history entries
        test_history = []
        for i, outfit_id in enumerate(test_outfits):
            history_id = f"history_{outfit_id}"
            worn_date = week_start + timedelta(days=i+2, hours=14)  # Different times
            
            history_data = {
                "user_id": user_id,
                "outfit_id": outfit_id,
                "date_worn": worn_date,
                "occasion": "daily",
                "mood": "confident",
                "weather": {},
                "notes": f"Test wear entry {i+1}",
                "tags": [],
                "outfit_name": f"Test Outfit {i+1}",
                "outfit_thumbnail": "",
                "created_at": int(worn_date.timestamp() * 1000)
            }
            
            # Save to outfit_history collection
            db.collection('outfit_history').document(history_id).set(history_data)
            test_history.append(history_id)
            logger.info(f"✅ Created test history entry {history_id} with date_worn: {worn_date}")
        
        # Now test our calculation with the seeded data
        logger.info(f"🧮 Testing calculation with seeded data...")
        worn_count = await calculate_worn_outfits_this_week(user_id)
        
        return {
            "success": True,
            "message": "Test data seeded successfully",
            "user_id": user_id,
            "test_outfits_created": len(test_outfits),
            "test_history_entries": len(test_history),
            "calculated_worn_this_week": worn_count,
            "week_start": week_start.isoformat(),
            "test_outfit_ids": test_outfits,
            "test_history_ids": test_history
        }
        
    except Exception as e:
        logger.error(f"❌ Error seeding test data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to seed test data: {e}")

@router.post("/verify-calculation")
async def verify_worn_calculation(
    user_id: str = Query(..., description="User ID to verify calculation for"),
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Verify the worn outfit calculation by manually counting and comparing.
    """
    try:
        from ..config.firebase import db
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Get current week boundaries
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        logger.info(f"🔍 Verifying calculation for user {user_id}")
        logger.info(f"📅 Week range: {week_start} to {week_end}")
        
        # Manual count from outfits collection
        outfits_ref = db.collection('outfits').where('user_id', '==', user_id)
        outfits_count = 0
        outfits_found = []
        
        for doc in outfits_ref.stream():
            data = doc.to_dict()
            last_worn_raw = data.get('lastWorn')
            last_worn_dt = parse_last_worn(last_worn_raw)
            
            if last_worn_dt and week_start <= last_worn_dt <= week_end:
                outfits_count += 1
                outfits_found.append({
                    "id": doc.id,
                    "name": data.get("name"),
                    "lastWorn": last_worn_dt.isoformat(),
                    "parsed_type": str(type(last_worn_raw))
                })
        
        # Manual count from outfit_history collection
        history_ref = db.collection('outfit_history').where('user_id', '==', user_id)
        history_count = 0
        history_found = []
        unique_outfits = set()
        
        for doc in history_ref.stream():
            data = doc.to_dict()
            date_worn_raw = data.get('date_worn')
            date_worn_dt = parse_last_worn(date_worn_raw)
            outfit_id = data.get('outfit_id')
            
            if date_worn_dt and week_start <= date_worn_dt <= week_end:
                history_count += 1
                if outfit_id:
                    unique_outfits.add(outfit_id)
                history_found.append({
                    "id": doc.id,
                    "outfit_id": outfit_id,
                    "date_worn": date_worn_dt.isoformat(),
                    "parsed_type": str(type(date_worn_raw))
                })
        
        # Test our function
        function_result = await calculate_worn_outfits_this_week(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "week_range": {
                "start": week_start.isoformat(),
                "end": week_end.isoformat()
            },
            "manual_counts": {
                "outfits_collection": outfits_count,
                "history_collection": history_count,
                "unique_from_history": len(unique_outfits)
            },
            "function_result": function_result,
            "matches_expected": function_result == max(outfits_count, len(unique_outfits)),
            "outfits_found": outfits_found,
            "history_found": history_found
        }
        
    except Exception as e:
        logger.error(f"❌ Error verifying calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to verify calculation: {e}")

@router.post("/initialize-stats")
async def initialize_user_stats_endpoint(
    current_user: UserProfile = Depends(get_current_user)
):
    """Initialize pre-aggregated stats document for the current user."""
    try:
        if not current_user:
            raise HTTPException(status_code=400, detail="User not found")
        
        logger.info(f"Initializing stats document for user {current_user.id}")
        
        # Import and use the stats service
        from ..services.user_stats_service import user_stats_service
        
        # Initialize the stats document
        success = await user_stats_service.initialize_user_stats(current_user.id)
        
        if success:
            # Get the initialized stats to return
            stats_data = await user_stats_service.get_user_stats(current_user.id)
            
            return {
                "success": True,
                "message": "User stats initialized successfully",
                "stats": stats_data,
                "user_id": current_user.id
            }
        else:
            return {
                "success": False,
                "message": "Failed to initialize user stats",
                "user_id": current_user.id
            }
            
    except Exception as e:
        logger.error(f"Error initializing user stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize stats: {str(e)}")

# Force redeploy Wed Sep 18 15:15:00 EDT 2025 - FIXED DUPLICATE ROUTE ISSUE!
