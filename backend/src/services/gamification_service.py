"""
Gamification Service - Handles XP, levels, badges, and gamification events
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..config.firebase import db
from ..custom_types.gamification import (
    BadgeType,
    LevelTier,
    LevelInfo,
    GamificationState,
    GamificationEvent,
    XPReward,
    BADGE_DEFINITIONS,
    LEVEL_TIERS,
    get_xp_for_level,
)

logger = logging.getLogger(__name__)


class GamificationService:
    """Service for managing gamification features"""
    
    def __init__(self):
        self.db = db
    
    def calculate_level(self, xp: int) -> int:
        """Calculate level from XP"""
        level = 1
        while get_xp_for_level(level + 1) <= xp:
            level += 1
        return level
    
    def get_level_tier(self, level: int) -> LevelTier:
        """Get the tier name for a level"""
        for tier_config in LEVEL_TIERS:
            if level in tier_config["levels"]:
                return tier_config["tier"]
        return LevelTier.CONNOISSEUR
    
    def get_level_info(self, xp: int) -> LevelInfo:
        """Get detailed level information"""
        current_level = self.calculate_level(xp)
        tier = self.get_level_tier(current_level)
        
        current_level_xp = get_xp_for_level(current_level)
        next_level_xp = get_xp_for_level(current_level + 1)
        xp_in_current_level = xp - current_level_xp
        xp_needed_for_next = next_level_xp - current_level_xp
        
        progress_percentage = (xp_in_current_level / xp_needed_for_next) * 100 if xp_needed_for_next > 0 else 100
        
        return LevelInfo(
            level=current_level,
            tier=tier,
            current_xp=xp,
            xp_for_next_level=next_level_xp,
            progress_percentage=round(progress_percentage, 1)
        )
    
    async def award_xp(
        self,
        user_id: str,
        amount: int,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Award XP to a user and check for level up
        
        Returns:
            Dict containing new_xp, level, level_up (bool), and optional new_badge
        """
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                logger.error(f"User {user_id} not found")
                return {"error": "User not found"}
            
            user_data = user_doc.to_dict()
            current_xp = user_data.get('xp', 0)
            current_level = self.calculate_level(current_xp)
            
            # Add XP
            new_xp = current_xp + amount
            new_level = self.calculate_level(new_xp)
            
            level_up = new_level > current_level
            
            # Update user document
            update_data = {
                'xp': new_xp,
                'level': new_level,
                'updatedAt': int(datetime.now().timestamp() * 1000)
            }
            user_ref.update(update_data)
            
            # Log XP event to analytics
            await self.log_gamification_event(
                user_id=user_id,
                event_type="xp_earned",
                xp_amount=amount,
                metadata={
                    "reason": reason,
                    "new_xp": new_xp,
                    "new_level": new_level,
                    **(metadata or {})
                }
            )
            
            result = {
                "xp_awarded": amount,
                "new_xp": new_xp,
                "level": new_level,
                "level_up": level_up,
                "reason": reason
            }
            
            # If level up, log that event too
            if level_up:
                await self.log_gamification_event(
                    user_id=user_id,
                    event_type="level_up",
                    metadata={
                        "old_level": current_level,
                        "new_level": new_level,
                        "tier": self.get_level_tier(new_level).value
                    }
                )
                result["tier"] = self.get_level_tier(new_level).value
                logger.info(f"🎉 User {user_id} leveled up! {current_level} → {new_level}")
            
            logger.info(f"✅ Awarded {amount} XP to user {user_id} for '{reason}'. New XP: {new_xp}")
            return result
            
        except Exception as e:
            logger.error(f"Error awarding XP to user {user_id}: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def unlock_badge(
        self,
        user_id: str,
        badge_id: str
    ) -> Dict[str, Any]:
        """
        Unlock a badge for a user
        
        Returns:
            Dict with success status and badge info
        """
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                logger.error(f"User {user_id} not found")
                return {"success": False, "error": "User not found"}
            
            user_data = user_doc.to_dict()
            current_badges = user_data.get('badges', [])
            
            # Check if badge already unlocked
            if badge_id in current_badges:
                logger.info(f"Badge {badge_id} already unlocked for user {user_id}")
                return {"success": False, "already_unlocked": True}
            
            # Add badge
            current_badges.append(badge_id)
            user_ref.update({
                'badges': current_badges,
                'updatedAt': int(datetime.now().timestamp() * 1000)
            })
            
            # Log badge unlock event
            badge_info = BADGE_DEFINITIONS.get(BadgeType(badge_id))
            await self.log_gamification_event(
                user_id=user_id,
                event_type="badge_unlocked",
                metadata={
                    "badge_id": badge_id,
                    "badge_name": badge_info.name if badge_info else badge_id,
                    "rarity": badge_info.rarity if badge_info else "common"
                }
            )
            
            logger.info(f"🏆 Badge {badge_id} unlocked for user {user_id}")
            return {
                "success": True,
                "badge_id": badge_id,
                "badge_info": badge_info.dict() if badge_info else None
            }
            
        except Exception as e:
            logger.error(f"Error unlocking badge for user {user_id}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def get_user_gamification_state(self, user_id: str) -> Optional[GamificationState]:
        """Get complete gamification state for a user"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                logger.error(f"User {user_id} not found")
                return None
            
            user_data = user_doc.to_dict()
            xp = user_data.get('xp', 0)
            level = user_data.get('level', 1)
            ai_fit_score = user_data.get('ai_fit_score', 0.0)
            badges = user_data.get('badges', [])
            
            # Get level info
            level_info = self.get_level_info(xp)
            
            # Get active challenges
            challenges_ref = self.db.collection_group('active').where('user_id', '==', user_id)
            active_challenges = []
            for doc in challenges_ref.stream():
                active_challenges.append(doc.to_dict())
            
            # Count completed challenges
            completed_ref = self.db.collection_group('completed').where('user_id', '==', user_id)
            completed_count = len(list(completed_ref.stream()))
            
            return GamificationState(
                user_id=user_id,
                xp=xp,
                level=level,
                level_info=level_info,
                ai_fit_score=ai_fit_score,
                badges=badges,
                active_challenges=active_challenges,
                completed_challenges_count=completed_count
            )
            
        except Exception as e:
            logger.error(f"Error getting gamification state for user {user_id}: {e}", exc_info=True)
            return None
    
    async def log_gamification_event(
        self,
        user_id: str,
        event_type: str,
        xp_amount: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log a gamification event to analytics_events collection
        
        Event types:
        - xp_earned
        - level_up
        - badge_unlocked
        - challenge_started
        - challenge_completed
        - ai_fit_score_updated
        """
        try:
            event_data = {
                "user_id": user_id,
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            if xp_amount is not None:
                event_data["xp_amount"] = xp_amount
            
            # Add to analytics_events collection
            self.db.collection('analytics_events').add(event_data)
            
            logger.debug(f"Logged gamification event: {event_type} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging gamification event: {e}", exc_info=True)
            return False
    
    async def check_badge_unlock_conditions(self, user_id: str) -> List[str]:
        """
        Check if user has unlocked any new badges based on their activity
        
        Returns:
            List of newly unlocked badge IDs
        """
        try:
            newly_unlocked = []
            
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return []
            
            user_data = user_doc.to_dict()
            current_badges = user_data.get('badges', [])
            
            # Get wardrobe count for starter badges
            wardrobe_ref = self.db.collection('wardrobe').where('userId', '==', user_id)
            wardrobe_count = len(list(wardrobe_ref.stream()))
            
            # Check starter closet badge (10 items)
            if wardrobe_count >= 10 and BadgeType.STARTER_CLOSET.value not in current_badges:
                result = await self.unlock_badge(user_id, BadgeType.STARTER_CLOSET.value)
                if result.get('success'):
                    newly_unlocked.append(BadgeType.STARTER_CLOSET.value)
            
            # Check closet cataloger badge (50 items)
            if wardrobe_count >= 50 and BadgeType.CLOSET_CATALOGER.value not in current_badges:
                result = await self.unlock_badge(user_id, BadgeType.CLOSET_CATALOGER.value)
                if result.get('success'):
                    newly_unlocked.append(BadgeType.CLOSET_CATALOGER.value)
            
            # Check feedback badges
            feedback_ref = self.db.collection('outfit_feedback').where('user_id', '==', user_id)
            feedback_count = len(list(feedback_ref.stream()))
            
            if feedback_count >= 25 and BadgeType.STYLE_CONTRIBUTOR.value not in current_badges:
                result = await self.unlock_badge(user_id, BadgeType.STYLE_CONTRIBUTOR.value)
                if result.get('success'):
                    newly_unlocked.append(BadgeType.STYLE_CONTRIBUTOR.value)
            
            if feedback_count >= 100 and BadgeType.AI_TRAINER.value not in current_badges:
                result = await self.unlock_badge(user_id, BadgeType.AI_TRAINER.value)
                if result.get('success'):
                    newly_unlocked.append(BadgeType.AI_TRAINER.value)
            
            return newly_unlocked
            
        except Exception as e:
            logger.error(f"Error checking badge conditions for user {user_id}: {e}", exc_info=True)
            return []


# Create singleton instance
gamification_service = GamificationService()


# Export
__all__ = ['GamificationService', 'gamification_service']

