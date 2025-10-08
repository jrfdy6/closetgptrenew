#!/usr/bin/env python3
"""
Existing Data Personalization Service
====================================

This service connects the simple personalization system to your existing
Firebase data instead of creating duplicate functionality.

Uses existing data:
- Wardrobe item favorites (item.favorite)
- Wardrobe item wear counts (item.wearCount)
- Outfit favorites (outfit.favorite)
- Outfit wear counts (outfit.wearCount)
- User style profiles (UserStyleProfile)
- Item analytics (ItemAnalyticsService)
"""

import logging
import time
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Import Firebase
from ..config.firebase import db

# Import existing types
from ..custom_types.user_style import UserStyleProfile, FeedbackType
from ..custom_types.wardrobe import ClothingItem
from ..models.item_analytics import ItemAnalytics, ItemFavoriteScore

logger = logging.getLogger(__name__)

@dataclass
class UserPreferenceFromExisting:
    """User preference data derived from existing Firebase data"""
    user_id: str
    preferred_colors: List[str]
    preferred_styles: List[str]
    preferred_occasions: List[str]
    disliked_colors: List[str]
    disliked_styles: List[str]
    favorite_items: List[str]
    most_worn_items: List[str]
    total_interactions: int
    last_updated: float
    data_source: str  # "firebase_existing"

class ExistingDataPersonalizationEngine:
    """Personalization engine that uses existing Firebase data"""
    
    def __init__(self):
        self.db = db
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        logger.info("✅ Existing Data Personalization Engine initialized")
    
    async def get_user_preference_from_existing_data(self, user_id: str) -> UserPreferenceFromExisting:
        """Get user preferences from existing Firebase data"""
        try:
            logger.info(f"🔍 Loading existing data for user {user_id}")
            
            # Initialize preference data
            preference = UserPreferenceFromExisting(
                user_id=user_id,
                preferred_colors=[],
                preferred_styles=[],
                preferred_occasions=[],
                disliked_colors=[],
                disliked_styles=[],
                favorite_items=[],
                most_worn_items=[],
                total_interactions=0,
                last_updated=time.time(),
                data_source="firebase_existing"
            )
            
            # 1. Get wardrobe items and their favorites/wear data
            wardrobe_data = await self._get_wardrobe_preferences(user_id)
            preference.preferred_colors.extend(wardrobe_data['preferred_colors'])
            preference.preferred_styles.extend(wardrobe_data['preferred_styles'])
            preference.preferred_occasions.extend(wardrobe_data['preferred_occasions'])
            preference.favorite_items.extend(wardrobe_data['favorite_items'])
            preference.most_worn_items.extend(wardrobe_data['most_worn_items'])
            preference.total_interactions += wardrobe_data['interactions']
            
            # 2. Get outfit preferences
            outfit_data = await self._get_outfit_preferences(user_id)
            preference.preferred_colors.extend(outfit_data['preferred_colors'])
            preference.preferred_styles.extend(outfit_data['preferred_styles'])
            preference.preferred_occasions.extend(outfit_data['preferred_occasions'])
            preference.total_interactions += outfit_data['interactions']
            
            # 3. Get user style profile if it exists
            style_profile_data = await self._get_user_style_profile(user_id)
            if style_profile_data:
                preference.preferred_colors.extend(style_profile_data['preferred_colors'])
                preference.preferred_styles.extend(style_profile_data['preferred_styles'])
                preference.preferred_occasions.extend(style_profile_data['preferred_occasions'])
                preference.total_interactions += style_profile_data['interactions']
            
            # 4. Get item analytics
            analytics_data = await self._get_item_analytics(user_id)
            preference.total_interactions += analytics_data['interactions']
            
            # Remove duplicates and sort by frequency
            preference.preferred_colors = self._deduplicate_and_rank(preference.preferred_colors)
            preference.preferred_styles = self._deduplicate_and_rank(preference.preferred_styles)
            preference.preferred_occasions = self._deduplicate_and_rank(preference.preferred_occasions)
            
            logger.info(f"✅ Loaded existing preferences for user {user_id}: {preference.total_interactions} interactions")
            return preference
            
        except Exception as e:
            logger.error(f"❌ Failed to load existing data for user {user_id}: {e}")
            # Return empty preference as fallback
            return UserPreferenceFromExisting(
                user_id=user_id,
                preferred_colors=[],
                preferred_styles=[],
                preferred_occasions=[],
                disliked_colors=[],
                disliked_styles=[],
                favorite_items=[],
                most_worn_items=[],
                total_interactions=0,
                last_updated=time.time(),
                data_source="firebase_existing_error"
            )
    
    async def _get_wardrobe_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get preferences from wardrobe items (favorites, wear counts)"""
        try:
            # Get wardrobe items
            wardrobe_ref = self.db.collection('wardrobe')
            docs = wardrobe_ref.where('userId', '==', user_id).stream()
            
            preferred_colors = []
            preferred_styles = []
            preferred_occasions = []
            favorite_items = []
            most_worn_items = []
            interactions = 0
            
            for doc in docs:
                item_data = doc.to_dict()
                item_id = doc.id
                
                # Count interactions
                interactions += 1
                
                # If item is favorited, add its attributes to preferences
                if item_data.get('favorite', False):
                    favorite_items.append(item_id)
                    
                    # Add color to preferences
                    if item_data.get('color'):
                        preferred_colors.append(item_data['color'])
                    
                    # Add styles to preferences
                    if item_data.get('style'):
                        if isinstance(item_data['style'], list):
                            preferred_styles.extend(item_data['style'])
                        else:
                            preferred_styles.append(item_data['style'])
                    
                    # Add occasions to preferences
                    if item_data.get('occasion'):
                        if isinstance(item_data['occasion'], list):
                            preferred_occasions.extend(item_data['occasion'])
                        else:
                            preferred_occasions.append(item_data['occasion'])
                
                # If item is frequently worn, add its attributes to preferences
                wear_count = (item_data.get('wearCount', 0) if item_data else 0)
                if wear_count >= 3:  # Consider frequently worn if worn 3+ times
                    most_worn_items.append(item_id)
                    
                    # Add color to preferences (weighted by wear count)
                    if item_data.get('color'):
                        for _ in range(min(wear_count, 5)):  # Cap at 5 repetitions
                            preferred_colors.append(item_data['color'])
                    
                    # Add styles to preferences (weighted by wear count)
                    if item_data.get('style'):
                        if isinstance(item_data['style'], list):
                            for style in item_data['style']:
                                for _ in range(min(wear_count, 3)):  # Cap at 3 repetitions
                                    preferred_styles.append(style)
                        else:
                            for _ in range(min(wear_count, 3)):
                                preferred_styles.append(item_data['style'])
            
            return {
                'preferred_colors': preferred_colors,
                'preferred_styles': preferred_styles,
                'preferred_occasions': preferred_occasions,
                'favorite_items': favorite_items,
                'most_worn_items': most_worn_items,
                'interactions': interactions
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get wardrobe preferences: {e}")
            return {
                'preferred_colors': [],
                'preferred_styles': [],
                'preferred_occasions': [],
                'favorite_items': [],
                'most_worn_items': [],
                'interactions': 0
            }
    
    async def _get_outfit_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get preferences from outfit favorites and wear counts"""
        try:
            # Get outfits
            outfits_ref = self.db.collection('outfits')
            docs = outfits_ref.where('userId', '==', user_id).stream()
            
            preferred_colors = []
            preferred_styles = []
            preferred_occasions = []
            interactions = 0
            
            for doc in docs:
                outfit_data = doc.to_dict()
                interactions += 1
                
                # If outfit is favorited or frequently worn, add its attributes to preferences
                is_favorite = (outfit_data.get('favorite', False) if outfit_data else False)
                wear_count = (outfit_data.get('wearCount', 0) if outfit_data else 0)
                
                if is_favorite or wear_count >= 2:  # Consider if favorited or worn 2+ times
                    # Add style to preferences
                    if outfit_data.get('style'):
                        weight = 3 if is_favorite else min(wear_count, 3)
                        for _ in range(weight):
                            preferred_styles.append(outfit_data['style'])
                    
                    # Add occasion to preferences
                    if outfit_data.get('occasion'):
                        weight = 2 if is_favorite else min(wear_count, 2)
                        for _ in range(weight):
                            preferred_occasions.append(outfit_data['occasion'])
                    
                    # Extract colors from outfit items
                    if outfit_data.get('items'):
                        for item in outfit_data['items']:
                            if item.get('color'):
                                weight = 2 if is_favorite else 1
                                for _ in range(weight):
                                    preferred_colors.append(item['color'])
            
            return {
                'preferred_colors': preferred_colors,
                'preferred_styles': preferred_styles,
                'preferred_occasions': preferred_occasions,
                'interactions': interactions
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get outfit preferences: {e}")
            return {
                'preferred_colors': [],
                'preferred_styles': [],
                'preferred_occasions': [],
                'interactions': 0
            }
    
    async def _get_user_style_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user style profile if it exists"""
        try:
            # Get user style profile
            style_ref = self.db.collection('user_style_profiles')
            docs = style_ref.where('user_id', '==', user_id).stream()
            
            for doc in docs:
                profile_data = doc.to_dict()
                
                preferred_colors = []
                preferred_styles = []
                preferred_occasions = []
                interactions = 0
                
                # Extract color preferences
                if profile_data.get('color_preferences'):
                    for color, pref in profile_data['color_preferences'].items():
                        if pref.get('positive_feedback', 0) > 0:
                            for _ in range(pref['positive_feedback']):
                                preferred_colors.append(color)
                            interactions += pref['positive_feedback']
                
                # Extract style preferences
                if profile_data.get('style_preferences'):
                    for style, pref in profile_data['style_preferences'].items():
                        if pref.get('positive_feedback', 0) > 0:
                            for _ in range(pref['positive_feedback']):
                                preferred_styles.append(style)
                            interactions += pref['positive_feedback']
                
                # Extract occasion preferences
                if profile_data.get('occasion_preferences'):
                    for occasion, prefs in profile_data['occasion_preferences'].items():
                        for style, confidence in prefs.items():
                            if confidence > 0.5:  # High confidence
                                preferred_occasions.append(occasion)
                                interactions += 1
                
                return {
                    'preferred_colors': preferred_colors,
                    'preferred_styles': preferred_styles,
                    'preferred_occasions': preferred_occasions,
                    'interactions': interactions
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user style profile: {e}")
            return None
    
    async def _get_item_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get item analytics data"""
        try:
            # Get item analytics
            analytics_ref = self.db.collection('item_analytics')
            docs = analytics_ref.where('user_id', '==', user_id).stream()
            
            interactions = 0
            for doc in docs:
                analytics_data = doc.to_dict()
                interactions += 1
            
            return {'interactions': interactions}
            
        except Exception as e:
            logger.error(f"❌ Failed to get item analytics: {e}")
            return {'interactions': 0}
    
    def _deduplicate_and_rank(self, items: List[str]) -> List[str]:
        """Remove duplicates and rank by frequency"""
        if not items:
            return []
        
        # Count frequency
        frequency = {}
        for item in items:
            frequency[item] = (frequency.get(item, 0) if frequency else 0) + 1
        
        # Sort by frequency (highest first)
        sorted_items = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 10 most frequent items
        return [item for item, count in sorted_items[:10]]
    
    def rank_outfits_by_existing_preferences(self, user_id: str, outfits: List[Dict[str, Any]], preference: UserPreferenceFromExisting) -> List[Dict[str, Any]]:
        """Rank outfits based on existing user preferences"""
        if preference.total_interactions < 3:
            # Not enough data for personalization
            return outfits
        
        ranked_outfits = []
        for outfit in outfits:
            score = 0.0
            
            # Color preference scoring
            outfit_colors = (outfit.get('colors', []) if outfit else [])
            for color in outfit_colors:
                if color in preference.preferred_colors:
                    # Higher score for colors that appear more frequently in preferences
                    color_index = preference.preferred_colors.index(color)
                    score += (10 - color_index) * 0.5  # Top colors get higher scores
            
            # Style preference scoring
            outfit_styles = (outfit.get('styles', []) if outfit else [])
            for style in outfit_styles:
                if style in preference.preferred_styles:
                    style_index = preference.preferred_styles.index(style)
                    score += (10 - style_index) * 0.3
            
            # Occasion preference scoring
            outfit_occasion = outfit.get('occasion', '')
            if outfit_occasion in preference.preferred_occasions:
                occasion_index = preference.preferred_occasions.index(outfit_occasion)
                score += (10 - occasion_index) * 0.2
            
            # Favorite items bonus
            outfit_items = (outfit.get('items', []) if outfit else [])
            for item in outfit_items:
                # Handle both dict and Pydantic ClothingItem objects
                item_id = item.get('id') if isinstance(item, dict) else getattr(item, 'id', None)
                if item_id and item_id in preference.favorite_items:
                    score += 1.0  # Bonus for favorite items
            
            # Most worn items bonus
            for item in outfit_items:
                # Handle both dict and Pydantic ClothingItem objects
                item_id = item.get('id') if isinstance(item, dict) else getattr(item, 'id', None)
                if item_id and item_id in preference.most_worn_items:
                    score += 0.5  # Bonus for frequently worn items
            
            # Add personalization info
            outfit['personalization_score'] = score
            outfit['personalization_applied'] = True
            outfit['user_interactions'] = preference.total_interactions
            outfit['data_source'] = preference.data_source
            
            ranked_outfits.append(outfit)
        
        # Sort by personalization score (highest first)
        ranked_outfits.sort(key=lambda x: (x.get('personalization_score', 0) if x else 0), reverse=True)
        
        logger.info(f"✅ Ranked {len(outfits)} outfits for user {user_id} using existing data")
        return ranked_outfits
    
    async def get_personalization_status_from_existing_data(self, user_id: str) -> Dict[str, Any]:
        """Get personalization status from existing data"""
        try:
            preference = await self.get_user_preference_from_existing_data(user_id)
            
            return {
                "user_id": user_id,
                "personalization_enabled": True,
                "has_existing_data": preference.total_interactions > 0,
                "total_interactions": preference.total_interactions,
                "min_interactions_required": 3,
                "ready_for_personalization": preference.total_interactions >= 3,
                "preferred_colors": preference.preferred_colors[:5],  # Top 5
                "preferred_styles": preference.preferred_styles[:5],  # Top 5
                "preferred_occasions": preference.preferred_occasions[:5],  # Top 5
                "favorite_items_count": len(preference.favorite_items),
                "most_worn_items_count": len(preference.most_worn_items),
                "data_source": preference.data_source,
                "system_parameters": {
                    "min_interactions": 3,
                    "max_outfits": 5,
                    "learning_rate": self.learning_rate,
                    "exploration_rate": self.exploration_rate,
                    "uses_existing_data": True
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get personalization status: {e}")
            return {
                "user_id": user_id,
                "personalization_enabled": False,
                "has_existing_data": False,
                "total_interactions": 0,
                "min_interactions_required": 3,
                "ready_for_personalization": False,
                "error": str(e),
                "data_source": "error"
            }
