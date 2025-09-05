from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import math
from ..config.firebase import db
from ..models.analytics_event import AnalyticsEvent, ItemInteractionType
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.profile import UserProfile
import logging

logger = logging.getLogger(__name__)

ANALYTICS_COLLECTION = "analytics_events"
FAVORITE_SCORES_COLLECTION = "item_favorite_scores"

def log_analytics_event(event: AnalyticsEvent) -> str:
    """Log an analytics event to the data lake."""
    try:
        if not db:
            logger.warning("❌ Firestore database not available, skipping analytics logging")
            return "no-db"
        
        # Convert to dict and clean up any problematic nested objects
        event_dict = event.dict()
        
        # Ensure metadata is a simple dict without nested objects
        if "metadata" in event_dict and event_dict["metadata"]:
            cleaned_metadata = {}
            for key, value in event_dict["metadata"].items():
                # Only store simple types that Firestore can handle
                if isinstance(value, (str, int, float, bool, list, dict)):
                    # For dicts, ensure they're simple (no nested dicts)
                    if isinstance(value, dict):
                        cleaned_metadata[key] = {k: v for k, v in value.items() 
                                               if isinstance(v, (str, int, float, bool))}
                    else:
                        cleaned_metadata[key] = value
            event_dict["metadata"] = cleaned_metadata
        
        logger.debug(f"🔍 DEBUG: Cleaned event dict: {event_dict}")
        
        doc_ref = db.collection(ANALYTICS_COLLECTION).document()
        doc_ref.set(event_dict)
        logger.debug(f"✅ Analytics event logged: {event.event_type}")
        return doc_ref.id
    except Exception as e:
        logger.error(f"❌ Failed to log analytics event: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        # Do not raise - prevents crashing the main endpoint
        return "error"

def log_item_interaction(
    user_id: str,
    item_id: str,
    interaction_type: ItemInteractionType,
    metadata: Optional[Dict[str, Any]] = None,
    outfit_id: Optional[str] = None,
    was_base_item: Optional[bool] = None,
    feedback_rating: Optional[int] = None,
    feedback_type: Optional[str] = None
) -> str:
    """Log an item interaction event and update favorite scores."""
    try:
        # Create analytics event
        event = AnalyticsEvent(
            user_id=user_id,
            event_type="item_interaction",
            item_id=item_id,
            interaction_type=interaction_type,
            outfit_id=outfit_id,
            was_base_item=was_base_item,
            feedback_rating=feedback_rating,
            feedback_type=feedback_type,
            metadata=metadata or {}
        )
        
        # Log to analytics collection
        event_id = log_analytics_event(event)
        
        # Update favorite score in background
        update_item_favorite_score_async(user_id, item_id)
        
        logger.info(f"Logged item interaction: {interaction_type} for item {item_id}")
        return event_id
        
    except Exception as e:
        logger.error(f"Error logging item interaction: {e}")
        raise

def log_outfit_generation(
    user_id: str,
    outfit_id: str,
    items: List[ClothingItem],
    base_item: Optional[ClothingItem] = None
):
    """Log outfit generation events for all items involved."""
    try:
        base_item_id = base_item.id if base_item else None
        
        for item in items:
            was_base = item.id == base_item_id if base_item_id else False
            
            # Log outfit generation event
            log_item_interaction(
                user_id=user_id,
                item_id=item.id,
                interaction_type=ItemInteractionType.OUTFIT_GENERATED,
                metadata={"outfit_id": outfit_id, "occasion": "outfit_generation"},
                outfit_id=outfit_id,
                was_base_item=was
            )
            
            # If this was a base item, log additional base item event
            if was_base:
                log_item_interaction(
                    user_id=user_id,
                    item_id=item.id,
                    interaction_type=ItemInteractionType.BASE_ITEM_USED,
                    metadata={"outfit_id": outfit_id},
                    outfit_id=outfit_id,
                    was_base_item=True
                )
        
        logger.info(f"Logged outfit generation for {len(items)} items")
        
    except Exception as e:
        logger.error(f"Error logging outfit generation: {e}")
        raise

def log_outfit_feedback(
    user_id: str,
    outfit_id: str,
    feedback_rating: int,
    feedback_type: str,
    outfit_items: List[str]  # List of item IDs in the outfit
):
    """Log feedback events for all items in an outfit."""
    try:
        for item_id in outfit_items:
            log_item_interaction(
                user_id=user_id,
                item_id=item_id,
                interaction_type=ItemInteractionType.FEEDBACK_RECEIVED,
                metadata={"outfit_id": outfit_id},
                outfit_id=outfit_id,
                feedback_rating=feedback_rating,
                feedback_type=feedback_type
            )
        
        logger.info(f"Logged feedback for outfit {outfit_id}")
        
    except Exception as e:
        logger.error(f"Error logging outfit feedback: {e}")
        raise

def update_item_favorite_score_async(user_id: str, item_id: str):
    """Calculate and update favorite score for an item (async)."""
    try:
        # Get all analytics events for this item and user
        events_ref = db.collection(ANALYTICS_COLLECTION).where(
            "user_id", "==", user_id
        ).where("item_id", "==", item_id).stream()
        
        analytics_data = [doc.to_dict() for doc in events_ref]
        
        # Calculate component scores
        outfit_usage_score = calculate_outfit_usage_score(analytics_data)
        feedback_score = calculate_feedback_score(analytics_data)
        interaction_score = calculate_interaction_score(analytics_data)
        base_item_score = calculate_base_item_score(analytics_data)
        
        # Get user profile for style preference scoring
        user_profile = get_user_profile(user_id)
        style_preference_score = calculate_style_preference_score(item_id, user_profile)
        
        # Calculate total score (weighted average)
        total_score = (
            outfit_usage_score * 0.3 +
            feedback_score * 0.25 +
            interaction_score * 0.2 +
            style_preference_score * 0.15 +
            base_item_score * 0.1
        )
        
        # Get usage statistics
        stats = calculate_usage_statistics(analytics_data)
        
        # Create or update favorite score document
        score_data = {
            "item_id": item_id,
            "user_id": user_id,
            "total_score": total_score,
            "outfit_usage_score": outfit_usage_score,
            "feedback_score": feedback_score,
            "interaction_score": interaction_score,
            "style_preference_score": style_preference_score,
            "base_item_score": base_item_score,
            "last_updated": datetime.utcnow().isoformat(),
            **stats
        }
        
        # Save to Firestore
        score_ref = db.collection(FAVORITE_SCORES_COLLECTION).document(f"{user_id}_{item_id}")
        score_ref.set(score_data, merge=True)
        
        logger.info(f"Updated favorite score for item {item_id}: {total_score:.3f}")
        
    except Exception as e:
        logger.error(f"Error updating favorite score: {e}")

def calculate_outfit_usage_score(analytics_data: List[Dict]) -> float:
    """Calculate score based on how often item appears in outfits."""
    outfit_count = sum(
        1 for data in analytics_data 
        if data.get("interaction_type") == ItemInteractionType.OUTFIT_GENERATED
    )
    
    if outfit_count == 0:
        return 0.0
    
    # Use logarithmic scaling to prevent domination by very active items
    return min(math.log(1 + outfit_count) / math.log(51), 1.0)

def calculate_feedback_score(analytics_data: List[Dict]) -> float:
    """Calculate score based on user feedback for outfits containing this item."""
    feedback_data = [
        data for data in analytics_data 
        if data.get("interaction_type") == ItemInteractionType.FEEDBACK_RECEIVED
    ]
    
    if not feedback_data:
        return 0.0
    
    total_rating = sum(data.get("feedback_rating", 0) for data in feedback_data)
    avg_rating = total_rating / len(feedback_data)
    
    # Convert 1-5 rating to 0-1 score
    return (avg_rating - 1) / 4

def calculate_interaction_score(analytics_data: List[Dict]) -> float:
    """Calculate score based on user interactions (views, edits, selects)."""
    view_count = sum(
        1 for data in analytics_data 
        if data.get("interaction_type") == ItemInteractionType.VIEW
    )
    edit_count = sum(
        1 for data in analytics_data 
        if data.get("interaction_type") == ItemInteractionType.EDIT
    )
    select_count = sum(
        1 for data in analytics_data 
        if data.get("interaction_type") == ItemInteractionType.SELECT
    )
    
    # Weight different interactions
    total_interactions = view_count + (edit_count * 3) + (select_count * 5)
    
    if total_interactions == 0:
        return 0.0
    
    return min(math.log(1 + total_interactions) / math.log(101), 1.0)

def calculate_base_item_score(analytics_data: List[Dict]) -> float:
    """Calculate score based on how often item is used as base item."""
    base_item_count = sum(
        1 for data in analytics_data 
        if data.get("interaction_type") == ItemInteractionType.BASE_ITEM_USED
    )
    
    if base_item_count == 0:
        return 0.0
    
    # Base items are special, so use higher weight
    return min(base_item_count / 10.0, 1.0)

def calculate_style_preference_score(item_id: str, user_profile: Optional[UserProfile]) -> float:
    """Calculate score based on match with user's style preferences."""
    if not user_profile:
        return 0.5  # Neutral score if no profile
    
    try:
        # Get item details
        item_ref = db.collection("wardrobe").document(item_id)
        item_doc = item_ref.get()
        
        if not item_doc.exists:
            return 0.5
        
        item_data = item_doc.to_dict()
        item_styles = item_data.get("style", [])
        item_type = item_data.get("type", "")
        
        if not item_styles:
            return 0.5
        
        # Calculate style match percentage
        user_styles = user_profile.style_preferences or []
        if not user_styles:
            return 0.5
        
        # Count matching styles
        matching_styles = sum(1 for style in item_styles if style in user_styles)
        style_match = matching_styles / len(item_styles)
        
        # Consider type preferences
        type_match = 0.5  # Default neutral
        if user_profile.preferred_types and item_type in user_profile.preferred_types:
            type_match = 1.0
        
        # Combine style and type matching
        return (style_match * 0.7) + (type_match * 0.3)
        
    except Exception as e:
        logger.error(f"Error calculating style preference score: {e}")
        return 0.5

def calculate_usage_statistics(analytics_data: List[Dict]) -> Dict[str, Any]:
    """Calculate usage statistics from analytics data."""
    stats = {
        "times_in_outfits": 0,
        "times_base_item": 0,
        "total_views": 0,
        "total_edits": 0,
        "total_selects": 0,
        "average_feedback_rating": 0.0
    }
    
    feedback_ratings = []
    
    for data in analytics_data:
        interaction_type = data.get("interaction_type")
        
        if interaction_type == ItemInteractionType.OUTFIT_GENERATED:
            stats["times_in_outfits"] += 1
        elif interaction_type == ItemInteractionType.BASE_ITEM_USED:
            stats["times_base_item"] += 1
        elif interaction_type == ItemInteractionType.VIEW:
            stats["total_views"] += 1
        elif interaction_type == ItemInteractionType.EDIT:
            stats["total_edits"] += 1
        elif interaction_type == ItemInteractionType.SELECT:
            stats["total_selects"] += 1
        elif interaction_type == ItemInteractionType.FEEDBACK_RECEIVED:
            rating = data.get("feedback_rating")
            if rating:
                feedback_ratings.append(rating)
    
    if feedback_ratings:
        stats["average_feedback_rating"] = sum(feedback_ratings) / len(feedback_ratings)
    
    return stats

def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """Get user profile for style preference calculations."""
    try:
        profile_ref = db.collection("users").document(user_id)
        profile_doc = profile_ref.get()
        
        if profile_doc.exists:
            return UserProfile(**profile_doc.to_dict())
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return None

def get_user_favorites(
    user_id: str,
    item_type: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get user's favorite items, optionally filtered by type."""
    try:
        # Query favorite scores - use simpler query to avoid index requirement
        query = db.collection(FAVORITE_SCORES_COLLECTION).where("user_id", "==", user_id)
        score_docs = query.stream()  # Remove ordering from query
        
        # Sort in Python instead of database
        score_data_list = []
        for doc in score_docs:
            score_data = doc.to_dict()
            score_data_list.append(score_data)
        
        # Sort by total_score in descending order
        score_data_list.sort(key=lambda x: x.get("total_score", 0), reverse=True)
        
        # Apply limit
        score_data_list = score_data_list[:limit]
        
        favorites = []
        for score_data in score_data_list:
            item_id = score_data["item_id"]
            logger.debug(f"Checking item_id: {item_id}")
            
            item_ref = db.collection("wardrobe").document(item_id)
            item_doc = item_ref.get()
            
            if not item_doc.exists:
                logger.debug(f"Wardrobe item {item_id} not found, skipping")
                continue
            
            item_data = item_doc.to_dict()
            logger.debug(f"Item {item_id} type: {item_data.get('type', 'No type')}, requested type: {item_type}")
            
            # Filter by type if specified
            if item_type and item_data.get("type") != item_type:
                logger.debug(f"Item {item_id} type mismatch: {item_data.get('type')} != {item_type}, skipping")
                continue
            
            # Add item data to favorites
            favorite_item = {
                "id": item_id,
                "name": item_data.get("name", "Unknown"),
                "type": item_data.get("type", "unknown"),
                "imageUrl": item_data.get("imageUrl", ""),
                "color": item_data.get("color", ""),
                "style": item_data.get("style", []),
                "favorite_score": score_data.get("total_score", 0),
                "usage_count": score_data.get("usage_count", 0),
                "feedback_score": score_data.get("feedback_score", 0),
                "interaction_score": score_data.get("interaction_score", 0),
                "style_match_score": score_data.get("style_match_score", 0),
                "base_item_score": score_data.get("base_item_score", 0)
            }
            favorites.append(favorite_item)
            logger.debug(f"Added favorite item: {item_id} ({item_data.get('type')})")
        
        logger.info(f"Found {len(favorites)} favorite items for user {user_id}, type {item_type}")
        return favorites
        
    except Exception as e:
        logger.error(f"Error getting user favorites: {e}")
        return []

def get_favorite_by_type(user_id: str, item_type: str) -> Optional[Dict[str, Any]]:
    """Get the user's favorite item of a specific type."""
    favorites = get_user_favorites(user_id, item_type, limit=1)
    return favorites[0] if favorites else None 