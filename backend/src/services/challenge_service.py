"""
Challenge Service - Manages gamification challenges
Wraps existing Forgotten Gems logic and adds new challenge types
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from ..config.firebase import db
from ..custom_types.gamification import (
    Challenge,
    UserChallenge,
    ChallengeStatus,
    ChallengeType,
    BadgeType,
    CHALLENGE_CATALOG,
)

logger = logging.getLogger(__name__)


class ChallengeService:
    """Service for managing challenges"""
    
    def __init__(self):
        self.db = db
    
    async def generate_forgotten_gems_challenge(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate a Forgotten Gems challenge for a user
        Calls existing forgotten gems endpoint to find dormant items
        """
        try:
            # Import the existing forgotten gems function
            from ..routes.forgotten_gems import get_forgotten_gems
            
            # Get dormant items (60+ days)
            gems_response = await get_forgotten_gems(
                days_threshold=60,
                min_rediscovery_potential=20.0,
                current_user=type('obj', (object,), {'id': user_id})
            )
            
            if not gems_response or not gems_response.get('success'):
                logger.warning(f"Could not get forgotten gems for user {user_id}")
                return None
            
            forgotten_items = gems_response['data'].get('forgottenItems', [])
            
            if len(forgotten_items) < 2:
                logger.info(f"Not enough dormant items for user {user_id} to create challenge")
                return None
            
            # Pick 2 items for the challenge
            selected_items = forgotten_items[:2]
            item_ids = [item['id'] for item in selected_items]
            
            # Calculate next Monday for expiration
            now = datetime.now()
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            next_monday = now + timedelta(days=days_until_monday)
            next_monday = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
            
            challenge_data = {
                "challenge_id": "forgotten_gems_weekly",
                "user_id": user_id,
                "started_at": now,
                "expires_at": next_monday,
                "progress": 0,
                "target": 2,
                "status": ChallengeStatus.IN_PROGRESS.value,
                "items": item_ids,
                "metadata": {
                    "item_details": [
                        {"id": item['id'], "name": item['name'], "type": item['type']}
                        for item in selected_items
                    ]
                }
            }
            
            return challenge_data
            
        except Exception as e:
            logger.error(f"Error generating Forgotten Gems challenge: {e}", exc_info=True)
            return None
    
    async def start_challenge(self, user_id: str, challenge_id: str) -> Dict[str, Any]:
        from firebase_admin import firestore
        from .reward_ledger import read, WriteEpochFence
        from .app_data_privacy import require_app_data_writable
        from .wear_projection import _target
        definition = CHALLENGE_CATALOG.get(challenge_id)
        if not definition:
            return {"success": False, "error": "Challenge not found"}
        if challenge_id == "annual_wardrobe_master":
            return await self.auto_start_annual_challenge(user_id)
        now = datetime.now(timezone.utc)
        year, week, _ = now.isocalendar()
        instance_id = challenge_id + (f"-{year}-W{week:02d}" if definition.cadence == "weekly" else "")
        reference = self.db.collection("user_challenges").document(user_id).collection("active").document(instance_id)
        if challenge_id == "forgotten_gems_weekly":
            record = await self.generate_forgotten_gems_challenge(user_id)
            if not record:
                return {"success": False, "error": "No eligible forgotten pieces yet"}
        else:
            record = {"challenge_id": challenge_id, "user_id": user_id, "started_at": now, "expires_at": now + timedelta(days=7) if definition.cadence == "weekly" else None, "progress": 0, "target": _target(definition), "status": "in_progress", "items": [], "metadata": {}}
        record["instance_id"] = instance_id
        epoch_fence = WriteEpochFence(self.db, user_id)
        @firestore.transactional
        def create(transaction):
            epoch = epoch_fence.check(transaction)
            previous = read(reference, transaction)
            legacy_ref = self.db.collection("user_challenges").document(user_id).collection("active").document(challenge_id)
            legacy = read(legacy_ref, transaction) if instance_id != challenge_id else previous
            if previous or legacy and legacy.get("status") == "in_progress" and (not legacy.get("expires_at") or legacy["expires_at"].replace(tzinfo=timezone.utc) > now):
                return {"success": True, "already_started": True, "challenge": previous or legacy}
            transaction.set(reference, {**record, "app_data_epoch": epoch})
            return {"success": True, "challenge": record}
        return create(self.db.transaction())

    async def check_challenge_progress(self, user_id: str, outfit_data: Dict[str, Any]) -> List[str]:
        """Compatibility adapter accepts only a committed canonical event."""
        from .wear_projection import project_instance
        event_id = outfit_data.get("event_id")
        if not event_id:
            return []
        snapshot = self.db.collection("outfit_history").document(event_id).get()
        event = snapshot.to_dict() if snapshot.exists else None
        if not event or event.get("user_id") != user_id:
            return []
        active = self.db.collection("user_challenges").document(user_id).collection("active")
        for instance in active.stream():
            project_instance(self.db, event_id, event.get("event_revision", 1), instance.reference)
        return []

    async def complete_challenge(self, user_id: str, challenge_id: str, catalog_id: Optional[str] = None) -> Dict[str, Any]:
        """Complete a verified instance once; never infer unpaid historical rewards."""
        from firebase_admin import firestore
        from .reward_ledger import read, key_for, reward_patch, WriteEpochFence
        from .wear_rewards import TOKEN_MULTIPLIERS
        from .app_data_privacy import require_app_data_writable
        reference = self.db.collection("user_challenges").document(user_id).collection("active").document(challenge_id)
        user_ref = self.db.collection("users").document(user_id)
        epoch_fence = WriteEpochFence(self.db, user_id)
        @firestore.transactional
        def complete(transaction):
            epoch_fence.check(transaction)
            instance = read(reference, transaction)
            user = read(user_ref, transaction)
            if not instance or not user:
                return {"success": False, "error": "Challenge not active"}
            cid = catalog_id or instance.get("challenge_id") or challenge_id
            definition = CHALLENGE_CATALOG.get(cid)
            if not definition:
                return {"success": False, "error": "Unknown challenge"}
            ledger_ref = self.db.collection("reward_ledger").document(key_for(user_id, "challenge", reference.path, str(instance.get("started_at"))))
            receipt = read(ledger_ref, transaction)
            if receipt or instance.get("status") == "completed":
                return {"success": True, "already_completed": True, "xp_awarded": 0}
            progress = instance.get("progress", 0)
            achieved = (progress.get("weeks_completed", 0) >= definition.rules.get("weeks_required", 52)) if isinstance(progress, dict) else progress >= instance.get("target", definition.rules.get("outfits_required", definition.rules.get("items_required", 1)))
            if not achieved:
                return {"success": False, "error": "Challenge target not reached"}
            if instance.get("status") in {"expired", "failed"}:
                return {"success": False, "error": "Challenge expired"}
            rewards = definition.rewards
            token_count = int(rewards.get("tokens", rewards.get("xp", 0)) * TOKEN_MULTIPLIERS.get((user.get("role") or {}).get("current_role", "starter"), 1))
            badge = (instance.get("metadata") or {}).get("badge_id", rewards.get("badge"))
            patch, result = reward_patch(user, xp=rewards.get("xp", 0), tokens=token_count, badge=badge, timestamp=int(datetime.now(timezone.utc).timestamp() * 1000))
            finished = {**instance, "status": "completed", "completed_at": datetime.now(timezone.utc)}
            transaction.update(user_ref, patch)
            transaction.update(reference, finished)
            transaction.set(self.db.collection("user_challenges").document(user_id).collection("completed").document(key_for(reference.path, str(instance.get("started_at")))), finished)
            transaction.set(ledger_ref, {"user_id": user_id, "kind": "challenge", "result": result})
            return {**result, "challenge_title": definition.title}
        return complete(self.db.transaction())

    def calculate_annual_challenge_cycle(self, user_signup_date: datetime, current_date: datetime) -> int:
        """
        Calculates which 52-week cycle user is in.
        Formula: floor((current_date - signup_date).days / 7 / 52) + 1
        """
        days_since_signup = (current_date - user_signup_date).days
        weeks_since_signup = days_since_signup / 7
        cycle_number = int(weeks_since_signup / 52) + 1
        return cycle_number
    
    def get_cycle_start_date(self, user_signup_date: datetime, cycle_number: int) -> datetime:
        """
        Returns start date for specific cycle.
        Cycle 1 starts at signup, cycle 2 starts 52 weeks later, etc.
        """
        weeks_offset = (cycle_number - 1) * 52
        cycle_start = user_signup_date + timedelta(weeks=weeks_offset)
        return cycle_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def is_in_grace_period(self, user_signup_date: datetime, current_date: datetime, cycle_number: int) -> bool:
        """
        Checks if user is in 1-week grace period after cycle end.
        """
        cycle_start = self.get_cycle_start_date(user_signup_date, cycle_number)
        cycle_end = cycle_start + timedelta(weeks=52)
        grace_end = cycle_end + timedelta(weeks=1)
        
        return cycle_end <= current_date <= grace_end
    
    async def auto_start_annual_challenge(self, user_id: str) -> Dict[str, Any]:
        from .wear_projection import ensure_annual_challenge
        instance = ensure_annual_challenge(self.db, user_id, int(datetime.now(timezone.utc).timestamp() * 1000))
        return {"success": bool(instance), "challenge_id": instance}

    async def check_annual_challenge_progress(self, user_id: str, outfit_data: Dict) -> Dict[str, Any]:
        await self.check_challenge_progress(user_id, outfit_data)
        return {"progress_updated": bool(outfit_data.get("event_id"))}

    async def get_active_challenges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's active challenges"""
        try:
            active_ref = self.db.collection('user_challenges')\
                .document(user_id)\
                .collection('active')
            
            challenges = []
            for doc in active_ref.stream():
                challenge_data = doc.to_dict()
                challenge_id = challenge_data.get('challenge_id')
                expires = challenge_data.get('expires_at')
                if challenge_data.get('status') != 'in_progress' or expires and isinstance(expires, datetime) and expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                    continue
                # Add challenge definition info
                challenge_def = CHALLENGE_CATALOG.get(challenge_id)
                if challenge_def:
                    challenge_data['title'] = challenge_def.title
                    challenge_data['description'] = challenge_def.description
                    challenge_data['rewards'] = challenge_def.rewards
                    challenge_data['icon'] = challenge_def.icon
                
                challenges.append(challenge_data)
            
            return challenges
            
        except Exception as e:
            logger.error(f"Error getting active challenges: {e}", exc_info=True)
            return []
    
    async def get_available_challenges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get challenges available to start"""
        try:
            logger.info(f"Getting available challenges for user {user_id}")
            logger.info(f"CHALLENGE_CATALOG has {len(CHALLENGE_CATALOG)} challenges")
            
            # Get user's active challenge IDs
            active_challenges = await self.get_active_challenges(user_id)
            active_ids = [c.get('challenge_id') for c in active_challenges]
            logger.info(f"User has {len(active_ids)} active challenges: {active_ids}")
            
            # Get featured challenges
            available = []
            featured_docs = {doc.id: doc.to_dict().get("featured", False) for doc in self.db.collection("challenges").stream()}
            for challenge_id, challenge_def in CHALLENGE_CATALOG.items():
                featured = featured_docs.get(challenge_id, challenge_def.featured)
                logger.info(f"Checking challenge {challenge_id}: featured={challenge_def.featured}, cadence={challenge_def.cadence}")
                
                # Skip if already active
                if challenge_id in active_ids:
                    logger.info(f"  -> Skipping {challenge_id}: already active")
                    continue
                
                # Only show featured or always-available challenges
                if featured or challenge_def.cadence == "always":
                    logger.info(f"  -> Adding {challenge_id} to available list")
                    # Handle type - could be enum or string
                    challenge_type = challenge_def.type
                    if hasattr(challenge_type, 'value'):
                        challenge_type = challenge_type.value
                    
                    available.append({
                        "challenge_id": challenge_id,
                        "title": challenge_def.title,
                        "description": challenge_def.description,
                        "type": challenge_type,
                        "rewards": challenge_def.rewards,
                        "icon": challenge_def.icon,
                        "featured": featured
                    })
                else:
                    logger.info(f"  -> Skipping {challenge_id}: not featured and not always available")
            
            logger.info(f"Returning {len(available)} available challenges")
            return available
            
        except Exception as e:
            logger.error(f"Error getting available challenges: {e}", exc_info=True)
            return []
    
    async def check_30_wears_milestones(self, user_id: str, item_id: str, new_wear_count: int) -> Optional[Dict[str, Any]]:
        # Canonical wear projection supplies before/after evidence. This old
        # interface cannot prove a crossing and must not backfill a reward.
        return None

    async def check_cold_start_progress(
        self,
        user_id: str,
        wardrobe_count: int
    ) -> Optional[Dict[str, Any]]:
        """
        Check Cold Start Quest progress and award milestones
        
        Args:
            user_id: User ID
            wardrobe_count: Current number of wardrobe items
            
        Returns:
            Dict with milestone info if reached, None otherwise
        """
        try:
            # Milestones: 10, 25, 50 items
            milestones = [
                {"count": 10, "xp": 50, "badge": BadgeType.STARTER_CLOSET.value, "message": "First 10 items!"},
                {"count": 25, "xp": 100, "badge": None, "message": "25 items cataloged!"},
                {"count": 50, "xp": 200, "badge": BadgeType.CLOSET_CATALOGER.value, "message": "50 items - Closet Cataloger!"}
            ]
            
            # Check if user has a cold_start_progress tracking doc
            progress_ref = self.db.collection('user_challenges')\
                .document(user_id)\
                .collection('active')\
                .document('cold_start_quest')
            
            progress_doc = progress_ref.get()
            
            if progress_doc.exists:
                progress_data = progress_doc.to_dict()
                milestones_reached = progress_data.get('milestones_reached', [])
            else:
                # Create progress tracking
                progress_data = {
                    "challenge_id": "cold_start_quest",
                    "user_id": user_id,
                    "started_at": datetime.now(),
                    "progress": wardrobe_count,
                    "target": 50,
                    "status": "in_progress",
                    "milestones_reached": []
                }
                progress_ref.set(progress_data)
                milestones_reached = []
            
            # Check for new milestones
            for milestone in milestones:
                if wardrobe_count >= milestone["count"] and milestone["count"] not in milestones_reached:
                    # Award milestone
                    from .gamification_service import gamification_service
                    
                    await gamification_service.award_xp(
                        user_id=user_id,
                        amount=milestone["xp"],
                        reason=f"Cold Start Quest: {milestone['message']}",
                        metadata={"milestone": milestone["count"], "wardrobe_count": wardrobe_count, "reward_operation_id": "cold-start-" + str(milestone["count"])}
                    )
                    
                    # Award badge if specified
                    if milestone["badge"]:
                        await gamification_service.unlock_badge(user_id, milestone["badge"])
                    
                    # Update progress
                    milestones_reached.append(milestone["count"])
                    progress_ref.update({
                        "milestones_reached": milestones_reached,
                        "progress": wardrobe_count
                    })
                    
                    logger.info(f"🎉 User {user_id} reached Cold Start milestone: {milestone['count']} items!")
                    
                    return {
                        "milestone_reached": milestone["count"],
                        "xp_awarded": milestone["xp"],
                        "badge_awarded": milestone.get("badge"),
                        "message": milestone["message"]
                    }
            
            # Update progress even if no milestone
            progress_ref.update({"progress": wardrobe_count})
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking Cold Start progress: {e}", exc_info=True)
            return None
    
    async def expire_old_challenges(self, user_id: str) -> int:
        """
        Check and expire challenges that have passed their expiration date
        
        Returns:
            Number of challenges expired
        """
        try:
            active_ref = self.db.collection('user_challenges')\
                .document(user_id)\
                .collection('active')
            
            now = datetime.now(timezone.utc)
            expired_count = 0
            
            for doc in active_ref.stream():
                challenge_data = doc.to_dict()
                expires_at = challenge_data.get('expires_at')
                
                if expires_at and isinstance(expires_at, datetime):
                    if expires_at.replace(tzinfo=timezone.utc) < now and challenge_data.get("status") == "in_progress":
                        # Mark as expired
                        challenge_data['status'] = ChallengeStatus.EXPIRED.value
                        
                        # Move to completed (but as expired)
                        completed_ref = self.db.collection('user_challenges')\
                            .document(user_id)\
                            .collection('completed')\
                            .document()
                        
                        completed_ref.set(challenge_data)
                        
                        # Delete from active
                        doc.reference.delete()
                        
                        expired_count += 1
                        logger.info(f"Expired challenge {challenge_data.get('challenge_id')} for user {user_id}")
            
            return expired_count
            
        except Exception as e:
            logger.error(f"Error expiring challenges: {e}", exc_info=True)
            return 0
    
    async def validate_color_palette_challenge(
        self,
        user_id: str,
        challenge_id: str,
        outfit_items: List[str]
    ) -> bool:
        """
        Validate if outfit meets color palette challenge requirements
        
        Args:
            user_id: User ID
            challenge_id: Challenge ID (e.g., "color_harmony")
            outfit_items: List of item IDs in the outfit
            
        Returns:
            True if outfit meets color rules
        """
        try:
            # Get challenge definition
            challenge_def = CHALLENGE_CATALOG.get(challenge_id)
            if not challenge_def or challenge_def.type != ChallengeType.COLOR_PALETTE:
                return False
            
            # Get color rule from challenge
            color_rule = challenge_def.rules.get('color_rule', 'complementary')
            
            # Fetch items to get their colors
            item_colors = []
            for item_id in outfit_items:
                item_ref = self.db.collection('wardrobe').document(item_id)
                item_doc = item_ref.get()
                if item_doc.exists:
                    item_data = item_doc.to_dict()
                    color = item_data.get('color', '').lower()
                    if color:
                        item_colors.append(color)
            
            # Validate based on rule
            if color_rule == 'monochrome':
                # All items should be same color family
                return len(set(item_colors)) <= 2
            
            elif color_rule == 'complementary':
                # Should have contrasting colors (simplified check)
                return len(set(item_colors)) >= 2 and len(set(item_colors)) <= 3
            
            elif color_rule == 'neutrals_only':
                # All colors should be neutrals
                neutrals = ['black', 'white', 'gray', 'grey', 'beige', 'tan', 'brown', 'navy']
                return all(any(neutral in color for neutral in neutrals) for color in item_colors)
            
            return True  # Default to true for unknown rules
            
        except Exception as e:
            logger.error(f"Error validating color challenge: {e}", exc_info=True)
            return False
    
    async def validate_context_challenge(
        self,
        user_id: str,
        challenge_id: str,
        outfit_data: Dict[str, Any]
    ) -> bool:
        """
        Validate if outfit meets context challenge requirements
        
        Args:
            user_id: User ID
            challenge_id: Challenge ID (e.g., "snow_day_chic")
            outfit_data: Outfit data including weather, items, etc.
            
        Returns:
            True if outfit meets context rules
        """
        try:
            challenge_def = CHALLENGE_CATALOG.get(challenge_id)
            if not challenge_def or challenge_def.type != ChallengeType.CONTEXT:
                return False
            
            rules = challenge_def.rules
            
            # Weather challenges
            if 'weather_condition' in rules:
                weather = outfit_data.get('weather', {})
                temp = weather.get('temp')
                condition = rules.get('weather_condition')
                
                if condition == 'cold' and temp and temp < 32:
                    # Should have appropriate layering
                    items = outfit_data.get('items', [])
                    has_outerwear = any('jacket' in str(item).lower() or 'coat' in str(item).lower() for item in items)
                    return has_outerwear and len(items) >= 4  # Multiple layers
                
                return True
            
            # Context-based (simplified validation)
            return True
            
        except Exception as e:
            logger.error(f"Error validating context challenge: {e}", exc_info=True)
            return False


# Create singleton instance
challenge_service = ChallengeService()


# Export
__all__ = ['ChallengeService', 'challenge_service']

