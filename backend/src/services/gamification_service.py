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
    badge_details,
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
        from .reward_ledger import award
        from uuid import uuid4
        operation_id = (metadata or {}).get("reward_operation_id") or "legacy-xp-" + str(uuid4())
        result = award(self.db, user_id, operation_id, xp=amount, metadata={"reason": reason, **(metadata or {})}, expected_epoch=(metadata or {}).get("app_data_epoch"))
        return {**result, "reason": reason}

    async def unlock_badge(
        self,
        user_id: str,
        badge_id: str,
        *,
        expected_epoch=None,
        _eligibility_check=None
    ) -> Dict[str, Any]:
        """
        Unlock a badge for a user
        
        Returns:
            Dict with success status and badge info
        """
        from .reward_ledger import award
        result = award(self.db, user_id, "badge-" + badge_id, badge=badge_id,
                       expected_epoch=expected_epoch, eligibility_check=_eligibility_check)
        definition = badge_details(badge_id)
        return {**result, "success": bool(result.get("badge_unlocked")), "already_unlocked": bool(result.get("success") and not result.get("badge_unlocked")), "badge_info": definition}

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
            
            # Get active challenges - simplified to avoid complex collection_group queries
            # For now, return empty list (challenges are stored in user document current_challenges)
            active_challenges = user_data.get('current_challenges', {})
            active_challenges_list = [
                {"challenge_id": k, **v} for k, v in active_challenges.items()
            ] if isinstance(active_challenges, dict) else []
            
            # Count completed challenges (simplified for now)
            completed_count = 0
            
            return GamificationState(
                user_id=user_id,
                xp=xp,
                level=level,
                level_info=level_info,
                ai_fit_score=ai_fit_score,
                badges=badges,
                active_challenges=[],  # Simplified - returning empty for now
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
            from .app_data_privacy import write_optional_record
            reference = self.db.collection('analytics_events').document()
            if not write_optional_record(self.db, user_id, reference, event_data, kind="telemetry", expected_epoch=(metadata or {}).get("app_data_epoch")):
                return False
            
            logger.debug(f"Logged gamification event: {event_type} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging gamification event: {e}", exc_info=True)
            return False
    
    async def check_badge_unlock_conditions(self, user_id: str, *, expected_epoch=None) -> List[str]:
        """Check owned live facts and award atomically within one captured epoch."""
        from google.cloud.firestore_v1.base_query import FieldFilter
        from .app_data_privacy import require_app_data_writable
        from .wardrobe_reads import owned_wardrobe_documents, wardrobe_owned_by, DELETED_FIELDS
        try:
            epoch = require_app_data_writable(self.db, user_id, expected_epoch)
            newly_unlocked = []
            conditions = ((BadgeType.STARTER_CLOSET.value, 'wardrobe', 10),
                          (BadgeType.CLOSET_CATALOGER.value, 'wardrobe', 50),
                          (BadgeType.STYLE_CONTRIBUTOR.value, 'feedback', 25),
                          (BadgeType.AI_TRAINER.value, 'feedback', 100))
            for badge_id, source, threshold in conditions:
                def eligible(transaction, user, source=source, threshold=threshold):
                    if source == 'wardrobe':
                        return len(owned_wardrobe_documents(self.db, user_id, transaction)) >= threshold
                    count = 0
                    query = self.db.collection('outfit_feedback').where(filter=FieldFilter('user_id', '==', user_id))
                    for snapshot in query.stream(transaction=transaction):
                        row = snapshot.to_dict() or {}
                        if wardrobe_owned_by(row, user_id) and not any(row.get(key) for key in DELETED_FIELDS):
                            count += 1
                            if count >= threshold:
                                return True
                    return False
                result = await self.unlock_badge(user_id, badge_id, expected_epoch=epoch,
                                                 _eligibility_check=eligible)
                if result.get('success'):
                    newly_unlocked.append(badge_id)
            return newly_unlocked
        except Exception:
            logger.exception("Error checking badge conditions")
            if expected_epoch is not None:
                raise
            return []


# Create singleton instance
gamification_service = GamificationService()


# Export
__all__ = ['GamificationService', 'gamification_service']

