"""
Feedback Processing Service for Real-Time Learning
Processes outfit feedback and updates user preferences immediately
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from firebase_admin import firestore
from ..config.firebase import db
import logging

logger = logging.getLogger(__name__)


class FeedbackProcessingService:
    """Process feedback and update personalization in real-time"""
    
    def __init__(self):
        self.db = db
        self.preferences_collection = "user_preferences"
        self.feedback_collection = "outfit_feedback"
    
    async def process_feedback(
        self,
        user_id: str,
        outfit_id: str,
        feedback_type: str,  # 'like' | 'dislike' | 'love' | 'never'
        rating: Optional[int] = None,
        outfit_data: Optional[Dict[str, Any]] = None,
        reasons: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Process feedback and immediately update user preferences
        Returns a confirmation message to show the user
        """
        try:
            logger.info(f"Processing {feedback_type} feedback for user {user_id} on outfit {outfit_id}")
            
            if not outfit_data:
                # Fetch outfit data if not provided
                outfit_ref = self.db.collection("outfits").document(outfit_id)
                outfit_doc = outfit_ref.get()
                if outfit_doc.exists:
                    outfit_data = outfit_doc.to_dict()
                else:
                    logger.warning(f"Outfit {outfit_id} not found")
                    return {"message": "Feedback received"}
            
            # Get or create user preferences
            preferences = await self._get_user_preferences(user_id)
            
            # Update preferences based on feedback
            if feedback_type in ['like', 'love']:
                await self._boost_preferences(user_id, outfit_data, preferences, weight=2 if feedback_type == 'love' else 1)
                message = await self._generate_positive_confirmation(outfit_data)
            elif feedback_type in ['dislike', 'never']:
                await self._penalize_preferences(user_id, outfit_data, preferences, reasons, severity=2 if feedback_type == 'never' else 1)
                message = await self._generate_negative_confirmation(outfit_data, reasons)
            else:
                message = "Feedback received"
            
            # Update last feedback timestamp
            await self._update_learning_stats(user_id)
            
            logger.info(f"Successfully processed feedback for user {user_id}")
            return {"message": message}
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}", exc_info=True)
            return {"message": "Feedback received"}
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get or create user preferences document"""
        try:
            pref_ref = self.db.collection(self.preferences_collection).document(user_id)
            pref_doc = pref_ref.get()
            
            if pref_doc.exists:
                return pref_doc.to_dict()
            else:
                # Create new preferences document
                new_preferences = {
                    "user_id": user_id,
                    "created_at": datetime.utcnow(),
                    "last_updated": datetime.utcnow(),
                    "style_preferences": {},
                    "color_preferences": {},
                    "occasion_preferences": {},
                    "avoid_combinations": [],
                    "total_interactions": 0,
                    "personalization_level": "beginner"  # beginner, intermediate, advanced
                }
                pref_ref.set(new_preferences)
                return new_preferences
                
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}
    
    async def _boost_preferences(
        self,
        user_id: str,
        outfit_data: Dict[str, Any],
        preferences: Dict[str, Any],
        weight: int = 1
    ):
        """Boost preferences based on liked outfit"""
        try:
            pref_ref = self.db.collection(self.preferences_collection).document(user_id)
            
            updates = {
                "last_updated": datetime.utcnow(),
                "total_interactions": firestore.Increment(1)
            }
            
            # Boost style preferences
            if outfit_data.get('style'):
                style = outfit_data['style']
                current_score = preferences.get('style_preferences', {}).get(style, 0)
                updates[f'style_preferences.{style}'] = current_score + (10 * weight)
            
            # Boost occasion preferences
            if outfit_data.get('occasion'):
                occasion = outfit_data['occasion']
                current_score = preferences.get('occasion_preferences', {}).get(occasion, 0)
                updates[f'occasion_preferences.{occasion}'] = current_score + (10 * weight)
            
            # Boost color preferences (from items)
            if outfit_data.get('items'):
                for item in outfit_data['items']:
                    if item.get('color'):
                        color = item['color']
                        current_score = preferences.get('color_preferences', {}).get(color, 0)
                        updates[f'color_preferences.{color}'] = current_score + (5 * weight)
            
            # Update personalization level
            total_interactions = preferences.get('total_interactions', 0) + 1
            if total_interactions >= 50:
                updates['personalization_level'] = 'advanced'
            elif total_interactions >= 10:
                updates['personalization_level'] = 'intermediate'
            
            pref_ref.update(updates)
            logger.info(f"Boosted preferences for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error boosting preferences: {e}")
    
    async def _penalize_preferences(
        self,
        user_id: str,
        outfit_data: Dict[str, Any],
        preferences: Dict[str, Any],
        reasons: Optional[List[str]],
        severity: int = 1
    ):
        """Penalize preferences based on disliked outfit"""
        try:
            pref_ref = self.db.collection(self.preferences_collection).document(user_id)
            
            updates = {
                "last_updated": datetime.utcnow(),
                "total_interactions": firestore.Increment(1)
            }
            
            # Learn what to avoid
            if reasons:
                # Store specific avoidances
                avoid_combinations = preferences.get('avoid_combinations', [])
                
                for reason in reasons:
                    avoidance = {
                        "type": reason,
                        "outfit_id": outfit_data.get('id'),
                        "timestamp": datetime.utcnow().isoformat(),
                        "severity": severity
                    }
                    avoid_combinations.append(avoidance)
                
                # Keep only last 50 avoidances
                avoid_combinations = avoid_combinations[-50:]
                updates['avoid_combinations'] = avoid_combinations
            
            # Penalize style if severe dislike
            if severity >= 2 and outfit_data.get('style'):
                style = outfit_data['style']
                current_score = preferences.get('style_preferences', {}).get(style, 0)
                updates[f'style_preferences.{style}'] = max(0, current_score - (20 * severity))
            
            pref_ref.update(updates)
            logger.info(f"Updated avoidances for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error penalizing preferences: {e}")
    
    async def _update_learning_stats(self, user_id: str):
        """Update learning statistics"""
        try:
            stats_ref = self.db.collection("user_learning_stats").document(user_id)
            stats_ref.set({
                "last_feedback": datetime.utcnow(),
                "total_feedback": firestore.Increment(1)
            }, merge=True)
        except Exception as e:
            logger.error(f"Error updating learning stats: {e}")
    
    async def _generate_positive_confirmation(self, outfit_data: Dict[str, Any]) -> str:
        """Generate encouraging confirmation message for positive feedback"""
        style = outfit_data.get('style', 'this style')
        occasion = outfit_data.get('occasion', 'this occasion')
        
        messages = [
            f"✓ Learned: You love {style} outfits! We'll show you more like this.",
            f"✓ Got it! We'll prioritize {style} looks for you.",
            f"✓ Awesome! We'll suggest more outfits perfect for {occasion}.",
            f"✓ Noted! Your preferences for {style} style have been updated.",
        ]
        
        # Simple selection based on what data is available
        if outfit_data.get('style'):
            return messages[0]
        elif outfit_data.get('occasion'):
            return messages[2]
        else:
            return messages[3]
    
    async def _generate_negative_confirmation(
        self,
        outfit_data: Dict[str, Any],
        reasons: Optional[List[str]]
    ) -> str:
        """Generate helpful confirmation message for negative feedback"""
        if reasons:
            reason_text = ", ".join(reasons)
            return f"✓ Understood: We'll avoid {reason_text} in future suggestions."
        
        style = outfit_data.get('style', 'this style')
        return f"✓ Got it: We'll adjust our suggestions based on your feedback."
    
    async def get_personalization_status(self, user_id: str) -> Dict[str, Any]:
        """Get current personalization status for display to user"""
        try:
            pref_ref = self.db.collection(self.preferences_collection).document(user_id)
            pref_doc = pref_ref.get()
            
            if not pref_doc.exists:
                return {
                    "personalization_level": "beginner",
                    "total_interactions": 0,
                    "progress_percentage": 0,
                    "message": "Start rating outfits to personalize your experience!"
                }
            
            preferences = pref_doc.to_dict()
            total_interactions = preferences.get('total_interactions', 0)
            level = preferences.get('personalization_level', 'beginner')
            
            # Calculate progress to next level
            if level == 'beginner':
                progress = min(100, (total_interactions / 10) * 100)
                next_milestone = 10
            elif level == 'intermediate':
                progress = min(100, ((total_interactions - 10) / 40) * 100)
                next_milestone = 50
            else:  # advanced
                progress = 100
                next_milestone = None
            
            return {
                "personalization_level": level,
                "total_interactions": total_interactions,
                "progress_percentage": int(progress),
                "next_milestone": next_milestone,
                "message": self._get_level_message(level, total_interactions, next_milestone),
                "top_styles": list(preferences.get('style_preferences', {}).keys())[:3],
                "top_colors": list(preferences.get('color_preferences', {}).keys())[:3]
            }
            
        except Exception as e:
            logger.error(f"Error getting personalization status: {e}")
            return {
                "personalization_level": "beginner",
                "total_interactions": 0,
                "progress_percentage": 0,
                "message": "Unable to load personalization status"
            }
    
    def _get_level_message(
        self,
        level: str,
        interactions: int,
        next_milestone: Optional[int]
    ) -> str:
        """Get appropriate message based on personalization level"""
        if level == 'beginner':
            return f"Rate {next_milestone - interactions} more outfits to reach Intermediate level!"
        elif level == 'intermediate':
            return f"You're {next_milestone - interactions} ratings away from Advanced personalization!"
        else:
            return "Your AI is fully trained! It learns from every interaction."


# Global instance
feedback_processing_service = FeedbackProcessingService()

