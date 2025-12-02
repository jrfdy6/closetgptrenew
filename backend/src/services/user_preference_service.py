"""
User Preference Service - Spotify-Style Learning System
========================================================

Comprehensive preference tracking and learning from all user interactions.
Persists to Firestore for true long-term personalization.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from collections import Counter

logger = logging.getLogger(__name__)

class UserPreferenceService:
    """
    Centralized service for managing user preferences with Spotify-style learning.
    
    Tracks preferences across all interaction types:
    - Outfit ratings (like/dislike/stars)
    - Outfit wearing (actual usage)
    - Item favoriting (saves)
    - Custom outfit creation (manual combinations)
    """
    
    def __init__(self):
        from ..config.firebase import db
        self.db = db
        self.collection_name = 'user_preferences'
        self._cache = {}  # In-memory cache for performance
    
    async def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences from Firestore (with caching).
        Creates default preferences if none exist.
        """
        # Check cache first
        if user_id in self._cache:
            cached = self._cache[user_id]
            # Cache valid for 5 minutes
            if (datetime.now(timezone.utc) - cached['cached_at']).seconds < 300:
                return cached['data']
        
        try:
            pref_ref = self.db.collection(self.collection_name).document(user_id)
            pref_doc = pref_ref.get()
            
            if pref_doc.exists:
                prefs = pref_doc.to_dict()
                # Update cache
                self._cache[user_id] = {
                    'data': prefs,
                    'cached_at': datetime.now(timezone.utc)
                }
                return prefs
            else:
                # Create default preferences
                default_prefs = self._create_default_preferences(user_id)
                pref_ref.set(default_prefs)
                logger.info(f"✨ Created default preferences for user {user_id}")
                return default_prefs
                
        except Exception as e:
            logger.error(f"❌ Failed to get preferences for {user_id}: {e}")
            return self._create_default_preferences(user_id)
    
    def _create_default_preferences(self, user_id: str) -> Dict[str, Any]:
        """Create default preference structure."""
        return {
            'user_id': user_id,
            
            # Color preferences
            'preferred_colors': [],
            'avoided_colors': [],
            'color_combinations_liked': [],
            'color_combinations_avoided': [],
            
            # Style preferences
            'preferred_styles': [],
            'avoided_styles': [],
            'style_evolution': {
                'initial_style': None,
                'current_trending': None,
                'evolution_timeline': [],
                'style_confidence': 0.0
            },
            
            # Item-level learning
            'preferred_items': [],
            'frequently_worn_items': [],
            'avoided_items': [],
            'avoided_combinations': [],
            
            # Pattern preferences
            'preferred_patterns': ['solid'],  # Default safe choice
            'avoided_patterns': [],
            
            # Formality preferences
            'formality_preference': 3,  # 1=very casual, 5=very formal
            'occasion_preferences': {},
            
            # Learning metrics
            'total_feedback_count': 0,
            'positive_feedback_count': 0,
            'negative_feedback_count': 0,
            'wear_count_total': 0,
            'personalization_level': 0,
            'confidence_level': 'learning',
            
            # Timestamps
            'created_at': datetime.now(timezone.utc).isoformat(),
            'first_feedback_at': None,
            'last_feedback_at': None,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    async def update_from_rating(
        self,
        user_id: str,
        outfit: Dict[str, Any],
        rating: Optional[int] = None,
        is_liked: bool = False,
        is_disliked: bool = False,
        feedback_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update preferences based on outfit rating.
        Returns learning confirmation data.
        """
        prefs = await self.get_preferences(user_id)
        updates = {}
        learning_messages = []
        
        # Extract outfit characteristics
        outfit_style = outfit.get('style', '')
        outfit_colors = self._extract_colors(outfit)
        outfit_items = [item.get('id') for item in outfit.get('items', [])]
        outfit_occasion = outfit.get('occasion', '')
        
        # Determine if positive or negative feedback
        is_positive = (rating and rating >= 4) or is_liked
        is_negative = (rating and rating <= 2) or is_disliked
        
        if is_positive:
            # BOOST preferences
            updates['preferred_styles'] = self._add_to_preference_list(
                prefs.get('preferred_styles', []), 
                [outfit_style],
                max_items=10
            )
            updates['preferred_colors'] = self._add_to_preference_list(
                prefs.get('preferred_colors', []),
                outfit_colors,
                max_items=15
            )
            updates['preferred_items'] = self._add_to_preference_list(
                prefs.get('preferred_items', []),
                outfit_items,
                max_items=20
            )
            
            # Track color combinations that work
            if len(outfit_colors) >= 2:
                color_combo = tuple(sorted(outfit_colors[:3]))
                updates['color_combinations_liked'] = self._add_to_preference_list(
                    prefs.get('color_combinations_liked', []),
                    [color_combo],
                    max_items=10
                )
            
            # Update occasion preferences
            if outfit_occasion:
                occasion_prefs = prefs.get('occasion_preferences', {})
                if outfit_occasion not in occasion_prefs:
                    occasion_prefs[outfit_occasion] = []
                occasion_prefs[outfit_occasion] = self._add_to_preference_list(
                    occasion_prefs[outfit_occasion],
                    [outfit_style],
                    max_items=5
                )
                updates['occasion_preferences'] = occasion_prefs
            
            # Learning messages
            learning_messages.append(f"Great! We'll show you more {outfit_style.lower()} outfits")
            if outfit_colors:
                top_colors = ', '.join(outfit_colors[:2])
                learning_messages.append(f"You prefer {top_colors} - noted!")
            
            updates['positive_feedback_count'] = prefs.get('positive_feedback_count', 0) + 1
            
        elif is_negative:
            # PENALIZE preferences (but be careful not to over-penalize)
            # Only avoid if consistently disliked
            negative_count = prefs.get('negative_feedback_count', 0)
            
            if negative_count >= 2:  # Only start avoiding after 2+ dislikes
                updates['avoided_styles'] = self._add_to_preference_list(
                    prefs.get('avoided_styles', []),
                    [outfit_style],
                    max_items=5
                )
                learning_messages.append(f"We'll try different styles than {outfit_style.lower()}")
            else:
                learning_messages.append("We'll adjust future suggestions based on this feedback")
            
            # Track avoided color combinations
            if len(outfit_colors) >= 2:
                color_combo = tuple(sorted(outfit_colors[:3]))
                updates['color_combinations_avoided'] = self._add_to_preference_list(
                    prefs.get('color_combinations_avoided', []),
                    [color_combo],
                    max_items=5
                )
            
            updates['negative_feedback_count'] = prefs.get('negative_feedback_count', 0) + 1
        
        # Update learning metrics
        updates['total_feedback_count'] = prefs.get('total_feedback_count', 0) + 1
        updates['personalization_level'] = min(100, updates['total_feedback_count'] * 2)
        updates['confidence_level'] = self._calculate_confidence_level(updates['total_feedback_count'])
        
        # Update timestamps
        now = datetime.now(timezone.utc).isoformat()
        updates['last_feedback_at'] = now
        updates['last_updated'] = now
        if not prefs.get('first_feedback_at'):
            updates['first_feedback_at'] = now
        
        # Save to Firestore
        await self._save_preferences(user_id, updates)
        
        # Invalidate cache
        if user_id in self._cache:
            del self._cache[user_id]
        
        return {
            'learning_messages': learning_messages,
            'total_feedback_count': updates['total_feedback_count'],
            'personalization_level': updates['personalization_level'],
            'confidence_level': updates['confidence_level'],
            'preferred_colors': updates.get('preferred_colors', prefs.get('preferred_colors', [])),
            'preferred_styles': updates.get('preferred_styles', prefs.get('preferred_styles', []))
        }
    
    async def update_from_wear(
        self,
        user_id: str,
        outfit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update preferences based on wearing an outfit.
        Wearing is a STRONG signal (stronger than just rating).
        """
        prefs = await self.get_preferences(user_id)
        updates = {}
        learning_messages = []
        
        # Extract characteristics
        outfit_items = [item.get('id') for item in outfit.get('items', [])]
        outfit_colors = self._extract_colors(outfit)
        outfit_style = outfit.get('style', '')
        outfit_occasion = outfit.get('occasion', '')
        
        # STRONG signal - they actually wore it!
        updates['frequently_worn_items'] = self._add_to_preference_list(
            prefs.get('frequently_worn_items', []),
            outfit_items,
            max_items=30,
            weight=2.0  # Wearing is worth 2x a like
        )
        
        updates['preferred_colors'] = self._add_to_preference_list(
            prefs.get('preferred_colors', []),
            outfit_colors,
            max_items=15,
            weight=1.5
        )
        
        updates['preferred_styles'] = self._add_to_preference_list(
            prefs.get('preferred_styles', []),
            [outfit_style],
            max_items=10,
            weight=1.5
        )
        
        # Track occasion-style patterns
        if outfit_occasion:
            occasion_prefs = prefs.get('occasion_preferences', {})
            if outfit_occasion not in occasion_prefs:
                occasion_prefs[outfit_occasion] = []
            occasion_prefs[outfit_occasion] = self._add_to_preference_list(
                occasion_prefs[outfit_occasion],
                [outfit_style],
                max_items=5,
                weight=1.5
            )
            updates['occasion_preferences'] = occasion_prefs
        
        # Update metrics
        updates['wear_count_total'] = prefs.get('wear_count_total', 0) + 1
        updates['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        # Learning messages
        learning_messages.append(f"Noted! You wear {outfit_style.lower()} outfits often")
        if outfit_colors:
            learning_messages.append(f"Tracking your {', '.join(outfit_colors[:2])} color preference")
        
        # Save to Firestore
        await self._save_preferences(user_id, updates)
        
        # Invalidate cache
        if user_id in self._cache:
            del self._cache[user_id]
        
        return {
            'learning_messages': learning_messages,
            'wear_count_total': updates['wear_count_total'],
            'frequently_worn_items': len(updates['frequently_worn_items'])
        }
    
    async def update_from_item_favorite(
        self,
        user_id: str,
        item: Dict[str, Any],
        is_favoriting: bool
    ) -> Dict[str, Any]:
        """Update preferences when user favorites/unfavorites an item."""
        prefs = await self.get_preferences(user_id)
        updates = {}
        learning_messages = []
        
        item_id = item.get('id')
        item_color = item.get('color', '')
        item_style = item.get('style', [])
        if isinstance(item_style, str):
            item_style = [item_style]
        
        if is_favoriting:
            # Add to preferred items
            updates['preferred_items'] = self._add_to_preference_list(
                prefs.get('preferred_items', []),
                [item_id],
                max_items=20
            )
            
            if item_color:
                updates['preferred_colors'] = self._add_to_preference_list(
                    prefs.get('preferred_colors', []),
                    [item_color],
                    max_items=15
                )
            
            learning_messages.append(f"We'll prioritize {item_color} items in future outfits")
        else:
            # Remove from preferred if unfavoriting
            preferred = prefs.get('preferred_items', [])
            if item_id in preferred:
                preferred.remove(item_id)
                updates['preferred_items'] = preferred
        
        updates['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        await self._save_preferences(user_id, updates)
        
        if user_id in self._cache:
            del self._cache[user_id]
        
        return {
            'learning_messages': learning_messages
        }
    
    def _extract_colors(self, outfit: Dict[str, Any]) -> List[str]:
        """Extract colors from outfit items."""
        colors = []
        for item in outfit.get('items', []):
            color = item.get('color', '')
            if color and color not in colors:
                colors.append(color)
        return colors
    
    def _add_to_preference_list(
        self, 
        current_list: List[Any], 
        new_items: List[Any],
        max_items: int = 10,
        weight: float = 1.0
    ) -> List[Any]:
        """
        Add items to preference list with frequency tracking.
        More frequent items stay at top (Spotify-style).
        """
        # Count existing items
        all_items = current_list + (new_items * int(weight))
        
        # Count frequencies
        item_counts = Counter(all_items)
        
        # Sort by frequency (most common first)
        sorted_items = [item for item, count in item_counts.most_common(max_items)]
        
        return sorted_items
    
    def _calculate_confidence_level(self, feedback_count: int) -> str:
        """Calculate confidence level based on feedback count."""
        if feedback_count >= 25:
            return 'high'
        elif feedback_count >= 10:
            return 'medium'
        else:
            return 'learning'
    
    async def _save_preferences(self, user_id: str, updates: Dict[str, Any]):
        """Save preference updates to Firestore."""
        try:
            pref_ref = self.db.collection(self.collection_name).document(user_id)
            pref_ref.set(updates, merge=True)  # Merge to preserve other fields
            logger.info(f"✅ Updated preferences for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Failed to save preferences for {user_id}: {e}")
            raise
    
    def generate_learning_summary(self, prefs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a Spotify-style summary of what we've learned.
        Used for "Personalized for You" explanations.
        """
        total_feedback = prefs.get('total_feedback_count', 0)
        
        if total_feedback < 5:
            return {
                'summary': "We're learning your style! Rate more outfits to improve suggestions.",
                'confidence': 'low',
                'insights': []
            }
        
        insights = []
        
        # Top preferred colors
        preferred_colors = prefs.get('preferred_colors', [])
        if preferred_colors:
            top_colors = ', '.join(preferred_colors[:3])
            insights.append(f"You prefer {top_colors} colors ({len(preferred_colors)} total)")
        
        # Top styles
        preferred_styles = prefs.get('preferred_styles', [])
        if preferred_styles:
            top_styles = ', '.join(preferred_styles[:2])
            insights.append(f"Your go-to styles: {top_styles}")
        
        # Wear patterns
        wear_count = prefs.get('wear_count_total', 0)
        if wear_count > 0:
            insights.append(f"You've worn {wear_count} outfits we suggested")
        
        # Style evolution
        evolution = prefs.get('style_evolution', {})
        if evolution.get('initial_style') and evolution.get('current_trending'):
            if evolution['initial_style'] != evolution['current_trending']:
                insights.append(f"Your style is evolving: {evolution['initial_style']} → {evolution['current_trending']}")
        
        return {
            'summary': f"Based on {total_feedback} ratings, here's what we know about your style:",
            'confidence': prefs.get('confidence_level', 'learning'),
            'insights': insights,
            'personalization_level': prefs.get('personalization_level', 0)
        }


# Global instance
user_preference_service = UserPreferenceService()

