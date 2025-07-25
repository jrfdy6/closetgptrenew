from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import math
from ..config.firebase import db
from ..models.item_analytics import (
    ItemAnalytics, 
    ItemFavoriteScore, 
    ItemUsageSummary, 
    ItemInteractionType
)
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.profile import UserProfile
import logging

logger = logging.getLogger(__name__)

class ItemAnalyticsService:
    def __init__(self):
        self.db = db
        self.analytics_collection = "item_analytics"
        self.scores_collection = "item_favorite_scores"
        
    async def track_item_interaction(
        self,
        user_id: str,
        item_id: str,
        interaction_type: ItemInteractionType,
        metadata: Optional[Dict[str, Any]] = None,
        outfit_id: Optional[str] = None,
        was_base_item: Optional[bool] = None,
        feedback_rating: Optional[int] = None,
        feedback_type: Optional[str] = None
    ) -> str:
        """Track a user interaction with an item."""
        try:
            analytics_data = ItemAnalytics(
                item_id=item_id,
                user_id=user_id,
                interaction_type=interaction_type,
                metadata=metadata or {},
                outfit_id=outfit_id,
                was_base_item=was_base_item,
                feedback_rating=feedback_rating,
                feedback_type=feedback_type
            )
            
            doc_ref = self.db.collection(self.analytics_collection).document()
            doc_ref.set(analytics_data.dict())
            
            # Update the item's favorite score
            await self._update_item_favorite_score(user_id, item_id)
            
            logger.info(f"Tracked {interaction_type} interaction for item {item_id}")
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"Error tracking item interaction: {e}")
            raise
    
    async def track_outfit_generation(
        self,
        user_id: str,
        outfit_id: str,
        items: List[ClothingItem],
        base_item: Optional[ClothingItem] = None
    ):
        """Track when items are used in outfit generation."""
        try:
            base_item_id = base_item.id if base_item else None
            
            for item in items:
                was_base = item.id == base_item_id if base_item_id else False
                
                await self.track_item_interaction(
                    user_id=user_id,
                    item_id=item.id,
                    interaction_type=ItemInteractionType.OUTFIT_GENERATED,
                    metadata={"outfit_id": outfit_id, "occasion": "outfit_generation"},
                    outfit_id=outfit_id,
                    was_base_item=was
                )
                
                if was_base:
                    await self.track_item_interaction(
                        user_id=user_id,
                        item_id=item.id,
                        interaction_type=ItemInteractionType.BASE_ITEM_USED,
                        metadata={"outfit_id": outfit_id},
                        outfit_id=outfit_id,
                        was_base_item=True
                    )
            
            logger.info(f"Tracked outfit generation for {len(items)} items")
            
        except Exception as e:
            logger.error(f"Error tracking outfit generation: {e}")
            raise
    
    async def track_outfit_feedback(
        self,
        user_id: str,
        outfit_id: str,
        feedback_rating: int,
        feedback_type: str,
        outfit_items: List[str]  # List of item IDs in the outfit
    ):
        """Track feedback for outfits and update item scores."""
        try:
            for item_id in outfit_items:
                await self.track_item_interaction(
                    user_id=user_id,
                    item_id=item_id,
                    interaction_type=ItemInteractionType.FEEDBACK_RECEIVED,
                    metadata={"outfit_id": outfit_id},
                    outfit_id=outfit_id,
                    feedback_rating=feedback_rating,
                    feedback_type=feedback_type
                )
            
            logger.info(f"Tracked feedback for outfit {outfit_id}")
            
        except Exception as e:
            logger.error(f"Error tracking outfit feedback: {e}")
            raise
    
    async def _update_item_favorite_score(self, user_id: str, item_id: str):
        """Calculate and update the favorite score for an item."""
        try:
            # Get all analytics for this item and user
            analytics_refs = self.db.collection(self.analytics_collection).where(
                "user_id", "==", user_id
            ).where("item_id", "==", item_id).stream()
            
            analytics_data = [doc.to_dict() for doc in analytics_refs]
            
            # Calculate component scores
            outfit_usage_score = self._calculate_outfit_usage_score(analytics_data)
            feedback_score = self._calculate_feedback_score(analytics_data)
            interaction_score = self._calculate_interaction_score(analytics_data)
            base_item_score = self._calculate_base_item_score(analytics_data)
            
            # Get user profile for style preference scoring
            user_profile = await self._get_user_profile(user_id)
            style_preference_score = await self._calculate_style_preference_score(
                item_id, user_profile
            )
            
            # Calculate total score (weighted average)
            total_score = (
                outfit_usage_score * 0.3 +
                feedback_score * 0.25 +
                interaction_score * 0.2 +
                style_preference_score * 0.15 +
                base_item_score * 0.1
            )
            
            # Get usage statistics
            stats = self._calculate_usage_statistics(analytics_data)
            
            # Create or update favorite score
            score_data = ItemFavoriteScore(
                item_id=item_id,
                user_id=user_id,
                total_score=total_score,
                outfit_usage_score=outfit_usage_score,
                feedback_score=feedback_score,
                interaction_score=interaction_score,
                style_preference_score=style_preference_score,
                base_item_score=base_item_score,
                **stats
            )
            
            # Save to Firestore
            score_ref = self.db.collection(self.scores_collection).document(f"{user_id}_{item_id}")
            score_ref.set(score_data.dict(), merge=True)
            
            logger.info(f"Updated favorite score for item {item_id}: {total_score:.3f}")
            
        except Exception as e:
            logger.error(f"Error updating favorite score: {e}")
            raise
    
    def _calculate_outfit_usage_score(self, analytics_data: List[Dict]) -> float:
        """Calculate score based on how often item appears in outfits."""
        outfit_count = sum(
            1 for data in analytics_data 
            if data.get("interaction_type") == ItemInteractionType.OUTFIT_GENERATED
        )
        
        # Use logarithmic scaling to prevent domination by very active items
        if outfit_count == 0:
            return 0.0
        
        # Normalize: log(1 + count) / log(1 + max_expected_count)
        # Assuming max expected is around 50 outfits per item
        return min(math.log(1 + outfit_count) / math.log(51), 1.0)
    
    def _calculate_feedback_score(self, analytics_data: List[Dict]) -> float:
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
    
    def _calculate_interaction_score(self, analytics_data: List[Dict]) -> float:
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
        
        # Use logarithmic scaling
        if total_interactions == 0:
            return 0.0
        
        return min(math.log(1 + total_interactions) / math.log(101), 1.0)
    
    def _calculate_base_item_score(self, analytics_data: List[Dict]) -> float:
        """Calculate score based on how often item is used as base item."""
        base_item_count = sum(
            1 for data in analytics_data 
            if data.get("interaction_type") == ItemInteractionType.BASE_ITEM_USED
        )
        
        if base_item_count == 0:
            return 0.0
        
        # Base items are special, so use higher weight
        return min(base_item_count / 10.0, 1.0)
    
    async def _calculate_style_preference_score(self, item_id: str, user_profile: Optional[UserProfile]) -> float:
        """Calculate score based on match with user's style preferences."""
        if not user_profile:
            return 0.5  # Neutral score if no profile
        
        try:
            # Get item details
            item_ref = self.db.collection("wardrobe").document(item_id)
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
    
    def _calculate_usage_statistics(self, analytics_data: List[Dict]) -> Dict[str, Any]:
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
    
    async def _get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile for style preference calculations."""
        try:
            profile_ref = self.db.collection("users").document(user_id)
            profile_doc = profile_ref.get()
            
            if profile_doc.exists:
                return UserProfile(**profile_doc.to_dict())
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def get_user_favorites(
        self,
        user_id: str,
        item_type: Optional[str] = None,
        limit: int = 10
    ) -> List[ItemUsageSummary]:
        """Get user's favorite items, optionally filtered by type."""
        try:
            # Query favorite scores
            query = self.db.collection(self.scores_collection).where("user_id", "==", user_id)
            score_docs = query.order_by("total_score", direction="DESCENDING").limit(limit).stream()
            
            favorites = []
            for doc in score_docs:
                score_data = doc.to_dict()
                
                # Get item details
                item_ref = self.db.collection("wardrobe").document(score_data["item_id"])
                item_doc = item_ref.get()
                
                if not item_doc.exists:
                    continue
                
                item_data = item_doc.to_dict()
                
                # Filter by type if specified
                if item_type and item_data.get("type") != item_type:
                    continue
                
                # Create usage summary
                summary = ItemUsageSummary(
                    item_id=score_data["item_id"],
                    user_id=user_id,
                    item_name=item_data.get("name", "Unknown"),
                    item_type=item_data.get("type", "unknown"),
                    image_url=item_data.get("imageUrl", ""),
                    outfit_appearances=score_data.get("times_in_outfits", 0),
                    base_item_uses=score_data.get("times_base_item", 0),
                    total_views=score_data.get("total_views", 0),
                    total_edits=score_data.get("total_edits", 0),
                    total_selects=score_data.get("total_selects", 0),
                    favorite_score=score_data.get("total_score", 0.0),
                    average_rating=score_data.get("average_feedback_rating", 0.0)
                )
                
                favorites.append(summary)
            
            # Add rank
            for i, favorite in enumerate(favorites):
                favorite.rank = i + 1
            
            return favorites
            
        except Exception as e:
            logger.error(f"Error getting user favorites: {e}")
            return []
    
    async def get_favorite_by_type(self, user_id: str, item_type: str) -> Optional[ItemUsageSummary]:
        """Get the user's favorite item of a specific type."""
        favorites = await self.get_user_favorites(user_id, item_type, limit=1)
        return favorites[0] if favorites else None 