"""
AI Fit Score Service
Calculates how well the AI understands a user's style preferences
Based on feedback count, preference consistency, and AI prediction confidence
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from ..config.firebase import db

logger = logging.getLogger(__name__)


class AIFitScoreService:
    """Service for calculating and managing AI Fit Score"""
    
    def __init__(self):
        self.db = db
    
    async def get_feedback_count(self, user_id: str) -> int:
        """Get total feedback count for a user"""
        try:
            import time
            count_start = time.time()
            # OPTIMIZED: Limit to 1000 to prevent timeout on users with massive feedback history
            feedback_ref = self.db.collection('outfit_feedback')\
                .where('user_id', '==', user_id)\
                .limit(1000)  # Cap at 1000 for performance
            feedback_docs = list(feedback_ref.stream())
            count = len(feedback_docs)
            logger.info(f"⏱️ AI_FIT: Feedback count query: {count} items ({time.time() - count_start:.2f}s)")
            return count
        except Exception as e:
            logger.error(f"Error getting feedback count: {e}", exc_info=True)
            return 0
    
    async def analyze_preference_consistency(self, user_id: str) -> float:
        """
        Analyze how consistent user's preferences are
        
        Returns:
            Score from 0 to 1 representing consistency
        """
        try:
            # Get user's feedback history
            feedback_ref = self.db.collection('outfit_feedback')\
                .where('user_id', '==', user_id)\
                .limit(50)  # Look at recent 50 feedback items
            
            feedback_docs = list(feedback_ref.stream())
            
            if len(feedback_docs) < 5:
                # Not enough data for consistency analysis
                return 0.3
            
            # Analyze feedback patterns
            likes = 0
            dislikes = 0
            ratings_sum = 0
            ratings_count = 0
            
            for doc in feedback_docs:
                data = doc.to_dict()
                feedback_type = data.get('feedback_type', '')
                rating = data.get('rating')
                
                if feedback_type == 'like' or feedback_type == 'love':
                    likes += 1
                elif feedback_type == 'dislike' or feedback_type == 'never':
                    dislikes += 1
                
                if rating is not None:
                    ratings_sum += rating
                    ratings_count += 1
            
            # Calculate consistency score
            # Higher score if user has clear preferences (not everything is neutral)
            total_feedback = len(feedback_docs)
            opinion_ratio = (likes + dislikes) / total_feedback if total_feedback > 0 else 0
            
            # If user rates things, check if ratings are consistent
            if ratings_count > 0:
                avg_rating = ratings_sum / ratings_count
                # Consistency is higher if average is not exactly neutral (3)
                rating_consistency = abs(avg_rating - 3) / 2  # Normalized to 0-1
            else:
                rating_consistency = 0.5
            
            # Combine metrics
            consistency_score = (opinion_ratio * 0.6 + rating_consistency * 0.4)
            
            return min(max(consistency_score, 0), 1)
            
        except Exception as e:
            logger.error(f"Error analyzing preference consistency: {e}", exc_info=True)
            return 0.5
    
    async def get_average_prediction_confidence(self, user_id: str) -> float:
        """
        Get average confidence of AI predictions for this user
        
        For now, this is a simplified calculation based on:
        - Number of outfits generated
        - Success rate of generated outfits
        - User engagement with generated outfits
        
        Returns:
            Score from 0 to 1 representing AI confidence
        """
        try:
            import time
            confidence_start = time.time()
            
            # OPTIMIZED: Limit to recent 100 outfits instead of fetching all
            # This prevents timeout on users with thousands of outfits
            outfits_ref = self.db.collection('outfits')\
                .where('user_id', '==', user_id)\
                .limit(100)  # Only analyze recent 100 outfits
            outfits_docs = list(outfits_ref.stream())
            logger.info(f"⏱️ AI_FIT: Fetched {len(outfits_docs)} outfits for confidence ({time.time() - confidence_start:.2f}s)")
            
            if len(outfits_docs) < 3:
                # Not enough data
                return 0.3
            
            # Count successful vs unsuccessful outfits
            successful_count = 0
            total_count = 0
            
            for doc in outfits_docs:
                data = doc.to_dict()
                was_successful = data.get('wasSuccessful', None)
                
                if was_successful is not None:
                    total_count += 1
                    if was_successful:
                        successful_count += 1
            
            if total_count == 0:
                # No success data, use neutral score
                return 0.5
            
            # Success rate is our confidence metric
            success_rate = successful_count / total_count
            
            # Scale to be more forgiving (70% success = 0.85 confidence)
            confidence = 0.3 + (success_rate * 0.7)
            
            return min(max(confidence, 0), 1)
            
        except Exception as e:
            logger.error(f"Error calculating prediction confidence: {e}", exc_info=True)
            return 0.5
    
    async def calculate_ai_fit_score(self, user_id: str) -> float:
        """
        Calculate AI Fit Score using hybrid approach:
        - Component 1: Feedback count (0-40 points, caps at 50 feedback items)
        - Component 2: Preference consistency (0-30 points)
        - Component 3: AI prediction confidence (0-30 points)
        
        Returns:
            Score from 0 to 100
        """
        try:
            # Component 1: Feedback count
            feedback_count = await self.get_feedback_count(user_id)
            feedback_component = min(40, feedback_count * 0.8)
            
            # Component 2: Preference consistency
            consistency = await self.analyze_preference_consistency(user_id)
            consistency_component = consistency * 30
            
            # Component 3: AI prediction confidence
            confidence = await self.get_average_prediction_confidence(user_id)
            confidence_component = confidence * 30
            
            # Calculate total score
            total_score = feedback_component + consistency_component + confidence_component
            
            # Round to 1 decimal place
            total_score = round(total_score, 1)
            
            logger.info(f"AI Fit Score for user {user_id}: {total_score} "
                       f"(feedback: {feedback_component:.1f}, "
                       f"consistency: {consistency_component:.1f}, "
                       f"confidence: {confidence_component:.1f})")
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating AI Fit Score for user {user_id}: {e}", exc_info=True)
            return 0.0
    
    async def update_score_from_feedback(
        self,
        user_id: str,
        feedback_data: Dict[str, Any]
    ) -> float:
        """
        Update AI Fit Score when new feedback is provided
        
        Returns:
            New AI Fit Score
        """
        try:
            # Recalculate score
            new_score = await self.calculate_ai_fit_score(user_id)
            
            # Update user profile
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'ai_fit_score': new_score,
                'updatedAt': int(datetime.now().timestamp() * 1000)
            })
            
            # Log the score update event
            from .gamification_service import gamification_service
            await gamification_service.log_gamification_event(
                user_id=user_id,
                event_type="ai_fit_score_updated",
                metadata={
                    "new_score": new_score,
                    "feedback_type": feedback_data.get('feedback_type'),
                    "rating": feedback_data.get('rating')
                }
            )
            
            logger.info(f"Updated AI Fit Score for user {user_id}: {new_score}")
            return new_score
            
        except Exception as e:
            logger.error(f"Error updating AI Fit Score: {e}", exc_info=True)
            return 0.0
    
    async def get_score_explanation(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed explanation of AI Fit Score components
        
        Returns:
            Dict with score breakdown and explanations
        """
        try:
            import time
            explanation_start = time.time()
            logger.info(f"⏱️ AI_FIT: Starting score explanation for user: {user_id}")
            
            # OPTIMIZED: Calculate components once and reuse them
            # This avoids duplicate queries (calculate_ai_fit_score was calling them again)
            feedback_start = time.time()
            feedback_count = await self.get_feedback_count(user_id)
            logger.info(f"⏱️ AI_FIT: Feedback count: {feedback_count} ({time.time() - feedback_start:.2f}s)")
            
            consistency_start = time.time()
            consistency = await self.analyze_preference_consistency(user_id)
            logger.info(f"⏱️ AI_FIT: Consistency: {consistency:.2f} ({time.time() - consistency_start:.2f}s)")
            
            confidence_start = time.time()
            confidence = await self.get_average_prediction_confidence(user_id)
            logger.info(f"⏱️ AI_FIT: Confidence: {confidence:.2f} ({time.time() - confidence_start:.2f}s)")
            
            # Calculate total score using the values we already fetched (no duplicate queries)
            # Component 1: Feedback count (0-40 points, caps at 50 feedback items)
            feedback_score = min(40, feedback_count * 0.8)
            # Component 2: Preference consistency (0-30 points)
            consistency_score = consistency * 30
            # Component 3: AI prediction confidence (0-30 points)
            confidence_score = confidence * 30
            total_score = feedback_score + consistency_score + confidence_score
            
            logger.info(f"⏱️ AI_FIT: Total score calculated: {total_score:.1f} (total: {time.time() - explanation_start:.2f}s)")
            
            # Create explanatory messages
            explanations = []
            
            if feedback_count < 10:
                explanations.append("Rate more outfits to help the AI learn your style")
            elif feedback_count < 25:
                explanations.append("You're actively training the AI - keep it up!")
            else:
                explanations.append("Excellent feedback history - the AI knows your style well")
            
            if consistency < 0.5:
                explanations.append("Your preferences show variety - the AI is learning your range")
            elif consistency < 0.8:
                explanations.append("You have clear style preferences")
            else:
                explanations.append("You have very consistent style preferences")
            
            if confidence < 0.5:
                explanations.append("The AI is still learning what works for you")
            elif confidence < 0.8:
                explanations.append("The AI is getting good at predicting your preferences")
            else:
                explanations.append("The AI has high confidence in its recommendations")
            
            return {
                "total_score": total_score,
                "components": {
                    "feedback": {
                        "score": min(40, feedback_count * 0.8),
                        "max": 40,
                        "count": feedback_count
                    },
                    "consistency": {
                        "score": consistency * 30,
                        "max": 30,
                        "percentage": round(consistency * 100, 1)
                    },
                    "confidence": {
                        "score": confidence * 30,
                        "max": 30,
                        "percentage": round(confidence * 100, 1)
                    }
                },
                "explanations": explanations,
                "next_milestone": self._get_next_milestone(total_score, feedback_count)
            }
            
        except Exception as e:
            logger.error(f"Error getting score explanation: {e}", exc_info=True)
            return {
                "total_score": 0,
                "components": {},
                "explanations": ["Error calculating score"],
                "next_milestone": None
            }
    
    def _get_next_milestone(self, current_score: float, feedback_count: int) -> Optional[Dict[str, Any]]:
        """Get the next milestone for the user to reach"""
        if feedback_count < 10:
            return {
                "type": "feedback_count",
                "target": 10,
                "current": feedback_count,
                "message": "Rate 10 outfits to unlock better personalization"
            }
        elif feedback_count < 25:
            return {
                "type": "feedback_count",
                "target": 25,
                "current": feedback_count,
                "message": "Rate 25 outfits for advanced AI learning"
            }
        elif current_score < 50:
            return {
                "type": "score",
                "target": 50,
                "current": current_score,
                "message": "Reach score 50 for AI Apprentice status"
            }
        elif current_score < 75:
            return {
                "type": "score",
                "target": 75,
                "current": current_score,
                "message": "Reach score 75 for AI Master status"
            }
        else:
            return None  # Already at top tier


# Create singleton instance
ai_fit_score_service = AIFitScoreService()


# Export
__all__ = ['AIFitScoreService', 'ai_fit_score_service']

