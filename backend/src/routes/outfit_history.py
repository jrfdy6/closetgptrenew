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
        if isinstance(ts, (int, float)) and not isinstance(ts, bool):
            return datetime.fromtimestamp(ts / 1000 if abs(ts) >= 1e12 else ts, tz=timezone.utc)
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
#         print(f"Failed to parse lastWorn timestamp '{ts}': {e}")
        return None
# Firebase imports moved inside functions to prevent import-time crashes
# from google.cloud import firestore
# from ..config.firebase import db
from ..auth.auth_service import get_current_user  # Keep this for dependency injection
from ..custom_types.profile import UserProfile   # Keep this for type hints
from ..core.logging import get_logger

# Try to import analytics service, but don't fail if it's not available
try:
    from ..services.analytics_service import log_analytics_event
except ImportError:
    def log_analytics_event(*args, **kwargs):
        """Fallback no-op function if analytics service is not available"""
        pass

router = APIRouter(tags=["outfit-history"])
logger = get_logger(__name__)
# Force Railway redeploy - outfit history mark-worn endpoint fixed - v5 - Oct 21 2025 - OUTFIT WEARCOUNT UPDATE ADDED

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
        
        # Get start and end of current week (Sunday to Saturday) - timezone aware
        from zoneinfo import ZoneInfo
        profile_doc = db.collection("users").document(user_id).get()
        profile = profile_doc.to_dict() if profile_doc.exists else {}
        from ..services.wear_rewards import reward_timezone
        now = datetime.now(ZoneInfo(reward_timezone(profile, "UTC")))
        # weekday() returns 0=Monday, 6=Sunday
        # For Sunday start: if today is Sunday (6), days_since_sunday = 0
        # if today is Monday (0), days_since_sunday = 1, etc.
        days_since_sunday = now.weekday()
        week_start = now - timedelta(days=days_since_sunday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        logger.info(f"🗓️ Checking outfits worn between {week_start} and {week_end}")
        
        # Count individual wear events from outfit_history collection
        from google.cloud.firestore_v1 import FieldFilter
        history_ref = db.collection('outfit_history').where(filter=FieldFilter('user_id', '==', user_id))
        total_worn = 0
        
        history_docs = history_ref.stream()
        for doc in history_docs:
            data = doc.to_dict()
            if data.get("undone"):
                continue
            date_worn_raw = (data.get('date_worn') if data else None)
            outfit_id = (data.get('outfit_id') if data else None)
            
            # Use the safe parser for date_worn
            date_worn_dt = parse_last_worn(date_worn_raw)
            
            if date_worn_dt and week_start <= date_worn_dt <= week_end and outfit_id:
                total_worn += 1
                logger.info(f"📅 Wear event {doc.id} for outfit {outfit_id} this week: {date_worn_dt}")
        
        logger.info(f"📊 Total wear events this week: {total_worn}")
        
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
        logger.info(f"🔍 DEBUG: About to query outfit_history collection for user {current_user.id}")
        from google.cloud.firestore_v1 import FieldFilter
        query = db.collection('outfit_history').where(filter=FieldFilter('user_id', '==', current_user.id))
        
        # Add outfit_id filter if provided
        if outfit_id:
            query = query.where(filter=FieldFilter('outfit_id', '==', outfit_id))
        
        # Add date filters if provided
        if start_date:
            start_timestamp = datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000
            query = query.where(filter=FieldFilter('date_worn', '>=', start_timestamp))
        
        if end_date:
            end_timestamp = datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000
            query = query.where(filter=FieldFilter('date_worn', '<=', end_timestamp))
        
        # Limit results before ordering (Firestore requirement)
        if limit:
            query = query.limit(limit)
        
        # Order by date worn (newest first) - only if we have documents
        try:
            from google.cloud.firestore_v1 import Query
            query = query.order_by('date_worn', direction=Query.DESCENDING)
        except Exception as e:
            logger.warning(f"Could not order by date_worn: {e}")
        
        # Execute query
        logger.info(f"🔍 DEBUG: About to execute Firestore query")
        docs = query.stream()
        logger.info(f"🔍 DEBUG: Query executed, processing documents")
        
        outfit_history = []
        doc_count = 0
        for doc in docs:
            doc_count += 1
            data = doc.to_dict()
            if data.get("undone"):
                continue
            outfit_history.append({
                "id": doc.id,
                "outfitId": (data.get('outfit_id') if data else None),
                "outfitName": (data.get('outfit_name', 'Unknown Outfit') if data else 'Unknown Outfit'),
                "outfitImage": (data.get('outfit_image', '') if data else ''),
                "dateWorn": (data.get('date_worn') if data else None),
                "weather": data.get('weather', {
                    "temperature": 0,
                    "condition": "Unknown",
                    "humidity": 0
                }),
                "occasion": (data.get('occasion', 'Casual') if data else 'Casual'),
                "mood": (data.get('mood', 'Comfortable') if data else 'Comfortable'),
                "notes": (data.get('notes', '') if data else ''),
                "tags": (data.get('tags', []) if data else []),
                "createdAt": (data.get('created_at') if data else None),
                "updatedAt": (data.get('updated_at') if data else None)
            })
        
        logger.info(f"Retrieved {len(outfit_history)} outfit history entries for user {current_user.id}")
        logger.info(f"🔍 DEBUG: Processed {doc_count} documents from Firestore")
        
        return {
            "success": True,
            "outfitHistory": outfit_history,
            "count": len(outfit_history),
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching outfit history: {str(e)}")
        logger.error(f"❌ User ID: {current_user.id if current_user else 'None'}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        
        raise HTTPException(503, "Outfit history is temporarily unavailable. Please retry.") from None

@router.post("/mark-worn")
async def mark_outfit_as_worn(data: Dict[str, Any], current_user: UserProfile = Depends(get_current_user)):
    """Calendar and deployed clients share the canonical wear transaction."""
    from ..services.outfit_wear import mark_outfit_worn, OutfitWearError, _digest
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    try:
        outfit_id = data.get("outfitId")
        zone = data.get("timezone") or "UTC"
        value = data.get("dateWorn")
        try:
            local_zone = ZoneInfo(zone)
            if isinstance(value, (float, int)) and not isinstance(value, bool):
                value = datetime.fromtimestamp(value / 1000, local_zone).date().isoformat()
        except (ValueError, TypeError, OverflowError, OSError, ZoneInfoNotFoundError):
            raise HTTPException(422, "Invalid wear date or timezone") from None
        if not outfit_id or not value:
            raise HTTPException(422, "outfitId and dateWorn are required")
        key = data.get("idempotency_key") or "calendar-" + _digest(current_user.id, outfit_id, value)
        result = mark_outfit_worn(get_db(), outfit_id, current_user.id, key, zone, wear_date=value, metadata=data, source="calendar")
        reward = result.get("rewards", {})
        return {**result, "message": "Outfit recorded", "xp_earned": reward.get("xp_awarded", 0), "tokens_earned": reward.get("tokens_awarded", 0), "level_up": reward.get("level_up", False), "new_level": reward.get("new_level"), "current_streak": reward.get("current_streak", 0), "challenges_completed": []}
    except OutfitWearError as exc:
        raise HTTPException(exc.status_code, exc.detail) from None
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "The wear request could not be acknowledged. Retry the same request.") from None

@router.patch("/{entry_id}")
async def update_outfit_history_entry(entry_id: str, updates: Dict[str, Any], current_user: UserProfile = Depends(get_current_user)):
    from ..services.outfit_wear import update_wear_metadata, OutfitWearError
    try:
        return update_wear_metadata(get_db(), current_user.id, entry_id, updates)
    except OutfitWearError as exc:
        raise HTTPException(exc.status_code, exc.detail) from None


@router.delete("/{entry_id}")
async def delete_outfit_history_entry(entry_id: str, current_user: UserProfile = Depends(get_current_user)):
    from ..services.outfit_wear import undo_wear, OutfitWearError
    try:
        return undo_wear(get_db(), current_user.id, entry_id)
    except OutfitWearError as exc:
        raise HTTPException(exc.status_code, exc.detail) from None

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
        from google.cloud.firestore_v1 import FieldFilter
        query = db.collection('outfit_history').where(filter=FieldFilter('user_id', '==', current_user.id))
        query = query.where(filter=FieldFilter('date_worn', '>=', start_timestamp))
        query = query.where(filter=FieldFilter('date_worn', '<=', end_timestamp))
        
        # Execute query with enhanced error handling
        todays_outfits = []
        try:
            docs = query.stream()
            
            for doc in docs:
                try:
                    data = doc.to_dict()
                    if data.get("undone"):
                        continue
                    todays_outfits.append({
                        "id": doc.id,
                        "outfitId": (data.get('outfit_id') if data else None),
                        "outfitName": (data.get('outfit_name', 'Today\'s Outfit') if data else 'Today\'s Outfit'),
                        "outfitImage": (data.get('outfit_image', '') if data else ''),
                        "dateWorn": (data.get('date_worn') if data else None),
                        "weather": data.get('weather', {
                            "temperature": 0,
                            "condition": "Unknown",
                            "humidity": 0
                        }),
                        "occasion": (data.get('occasion', 'Casual') if data else 'Casual'),
                        "mood": (data.get('mood', 'Comfortable') if data else 'Comfortable'),
                        "notes": (data.get('notes', '') if data else ''),
                        "tags": (data.get('tags', []) if data else []),
                        "createdAt": (data.get('created_at') if data else None),
                        "updatedAt": (data.get('updated_at') if data else None)
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
async def get_todays_outfit_suggestion(current_user: UserProfile = Depends(get_current_user)):
    """Use the same admitted generator and saved outfit as other entry points."""
    from google.cloud.firestore_v1 import FieldFilter
    from firebase_admin import firestore
    from ..services.outfit_creation_admission import require_outfit_creation_ready, resolve_owned_items
    from ..services.app_data_privacy import require_app_data_writable, AppDataDeletionError
    from ..services.wear_rewards import reward_timezone
    from ..services.reward_ledger import read, key_for
    from ..utils.outfit_admission import has_complete_combination
    from zoneinfo import ZoneInfo
    database = get_db()
    admission = require_outfit_creation_ready(database, current_user.id)
    user = database.collection("users").document(current_user.id).get().to_dict() or {}
    day = datetime.now(ZoneInfo(reward_timezone(user, "UTC"))).date().isoformat()
    suggestion_id = key_for(current_user.id, "daily", day)
    reference = database.collection("daily_outfit_suggestions").document(suggestion_id)
    existing = reference.get()
    if existing.exists:
        record = existing.to_dict()
    else:
        from ..routes.outfits.routes import generate_outfit, OutfitRequest
        wardrobe = [{**snapshot.to_dict(), "id": snapshot.id} for snapshot in database.collection("wardrobe").where(filter=FieldFilter("userId", "==", current_user.id)).stream()]
        generated = await generate_outfit(OutfitRequest(occasion="Casual", style="Minimalist", mood="Subtle", wardrobe=wardrobe, description="Daily outfit suggestion"), current_user.id)
        outfit = generated.model_dump() if hasattr(generated, "model_dump") else generated.dict() if hasattr(generated, "dict") else generated
        now = int(datetime.now(timezone.utc).timestamp() * 1000)
        @firestore.transactional
        def save(transaction):
            require_app_data_writable(database, current_user.id, admission["app_data_epoch"], transaction)
            require_outfit_creation_ready(database, current_user.id, transaction=transaction)
            previous = read(reference, transaction)
            if previous:
                return previous
            items = resolve_owned_items(database, transaction, current_user.id, outfit.get("items"))
            if not has_complete_combination(items):
                raise HTTPException(422, "Daily suggestion is missing required pieces")
            record = {"user_id": current_user.id, "date": day, "outfit_id": outfit["id"], "outfit_data": {**outfit, "items": items}, "generated_at": now, "created_at": now, "updated_at": now, "is_worn": False, "app_data_epoch": admission["app_data_epoch"]}
            transaction.set(reference, record)
            return record
        try:
            record = save(database.transaction())
        except AppDataDeletionError as exc:
            raise HTTPException(exc.status_code, exc.detail) from None
    return {"success": True, "suggestion": {"id": suggestion_id, "outfitData": record["outfit_data"], "generatedAt": record["generated_at"], "date": day}, "isWorn": record.get("is_worn", False), "wornAt": record.get("worn_at"), "message": "Today's outfit suggestion"}

@router.delete("/today-suggestion/clear-cache")
async def clear_todays_suggestion_cache(current_user: UserProfile = Depends(get_current_user)):
    from google.cloud.firestore_v1 import FieldFilter
    from ..services.app_data_privacy import require_app_data_writable, AppDataDeletionError
    from ..services.wear_rewards import reward_timezone
    from zoneinfo import ZoneInfo
    database = get_db()
    try:
        require_app_data_writable(database, current_user.id)
    except AppDataDeletionError as exc:
        raise HTTPException(exc.status_code, exc.detail) from None
    user = database.collection("users").document(current_user.id).get().to_dict() or {}
    day = datetime.now(ZoneInfo(reward_timezone(user, "UTC"))).date().isoformat()
    records = database.collection("daily_outfit_suggestions").where(filter=FieldFilter("user_id", "==", current_user.id)).where(filter=FieldFilter("date", "==", day)).stream()
    deleted = 0
    for record in records:
        # Saved look/history remain intact. Only the suggestion pointer is cleared.
        record.reference.delete()
        deleted += 1
    return {"success": True, "deleted_count": deleted}

@router.post("/today-suggestion/wear")
async def mark_today_suggestion_as_worn(data: Dict[str, Any], current_user: UserProfile = Depends(get_current_user)):
    from ..services.outfit_wear import mark_outfit_worn, OutfitWearError, _digest
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    try:
        suggestion_id = data.get("suggestionId")
        if not isinstance(suggestion_id, str) or "/" in suggestion_id:
            raise HTTPException(422, "suggestionId is required")
        database = get_db()
        snapshot = database.collection("daily_outfit_suggestions").document(suggestion_id).get()
        suggestion = snapshot.to_dict() if snapshot.exists else None
        if not suggestion or suggestion.get("user_id") != current_user.id:
            raise HTTPException(404, "Suggestion not found")
        outfit_id = suggestion.get("outfit_id") or "suggestion-" + _digest(current_user.id, suggestion_id)
        zone = data.get("timezone") or "UTC"
        try:
            day = datetime.now(ZoneInfo(zone)).date().isoformat()
        except (ValueError, TypeError, ZoneInfoNotFoundError):
            raise HTTPException(422, "Invalid timezone") from None
        key = data.get("idempotency_key") or "suggestion-" + _digest(current_user.id, suggestion_id, day)
        result = mark_outfit_worn(database, outfit_id, current_user.id, key, zone, source="daily_suggestion", suggestion_id=suggestion_id)
        return {**result, "alreadyWorn": result["already_recorded"], "message": "Suggestion recorded"}
    except OutfitWearError as exc:
        raise HTTPException(exc.status_code, exc.detail) from None
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "The wear request could not be acknowledged. Retry the same request.") from None

@router.get("/stats")
async def get_outfit_history_stats(current_user: UserProfile = Depends(get_current_user), days: int = Query(30, ge=1, le=365)):
    from google.cloud.firestore_v1 import FieldFilter
    database = get_db()
    try:
        outfits = [snapshot.to_dict() for snapshot in database.collection("outfits").where(filter=FieldFilter("user_id", "==", current_user.id)).stream()]
        outfits = [item for item in outfits if not any(item.get(key) for key in ("deleted", "isDeleted", "deletedAt", "deleted_at"))]
        garments = [snapshot.to_dict() for snapshot in database.collection("wardrobe").where(filter=FieldFilter("userId", "==", current_user.id)).stream()]
        garments = [item for item in garments if not item.get("deleted_at")]
        weekly = await calculate_worn_outfits_this_week(current_user.id)
        values = {"total_outfits": len(outfits), "outfits_this_week": weekly, "totalThisWeek": weekly, "days_queried": days, "recent_outfits": [], "wardrobe_total": len(garments), "wardrobe_favorites": sum(bool(item.get("isFavorite")) for item in garments)}
        return {"success": True, "data": values, **values}
    except Exception:
        raise HTTPException(503, "Outfit statistics are temporarily unavailable") from None

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
            query = collection_ref.where(filter=FieldFilter("user_id", "==", user_id))
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
        outfits_ref = db.collection('outfits').where(filter=FieldFilter('user_id', '==', user_id))
        outfits_count = 0
        outfits_found = []
        
        for doc in outfits_ref.stream():
            data = doc.to_dict()
            if data.get("undone"):
                continue
            last_worn_raw = (data.get('lastWorn') if data else None)
            last_worn_dt = parse_last_worn(last_worn_raw)
            
            if last_worn_dt and week_start <= last_worn_dt <= week_end:
                outfits_count += 1
                outfits_found.append({
                    "id": doc.id,
                    "name": (data.get("name") if data else None),
                    "lastWorn": last_worn_dt.isoformat(),
                    "parsed_type": str(type(last_worn_raw))
                })
        
        # Manual count from outfit_history collection
        from google.cloud.firestore_v1 import FieldFilter
        history_ref = db.collection('outfit_history').where(filter=FieldFilter('user_id', '==', user_id))
        history_count = 0
        history_found = []
        unique_outfits = set()
        
        for doc in history_ref.stream():
            data = doc.to_dict()
            if data.get("undone"):
                continue
            date_worn_raw = (data.get('date_worn') if data else None)
            date_worn_dt = parse_last_worn(date_worn_raw)
            outfit_id = (data.get('outfit_id') if data else None)
            
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

# Cleaned up - removed broken complex analytics endpoints
