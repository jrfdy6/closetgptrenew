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
            
            if hasattr(gems_response, 'model_dump'):
                gems_response = gems_response.model_dump()
            if not gems_response or not gems_response.get('success'):
                logger.warning(f"Could not get forgotten gems for user {user_id}")
                return None
            
            forgotten_items = [item for item in gems_response['data'].get('forgottenItems', []) if isinstance(item.get('daysSinceWorn'), (int, float)) and item['daysSinceWorn'] >= 60 and item.get('lastWorn')]
            
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
        from .wear_rewards import reward_timezone
        from .app_data_privacy import require_app_data_writable
        from zoneinfo import ZoneInfo
        initial_epoch = require_app_data_writable(self.db, user_id)
        profile = self.db.collection('users').document(user_id).get().to_dict() or {}
        now = datetime.now(ZoneInfo(reward_timezone(profile, 'UTC')))
        year, week, _ = now.isocalendar()
        from .challenge_periods import challenge_period
        suffix, expires = challenge_period(definition.cadence, now)
        streak_days = definition.rules.get('ratings_days') or definition.rules.get('streak_days') or (definition.rules.get('days_required') if definition.rules.get('consecutive') else None)
        if streak_days:
            expires = now + timedelta(days=int(streak_days))
        if definition.id == 'role_defender':
            expires = now + timedelta(weeks=int(definition.rules['weeks_required']))
        if definition.rules.get('time_limit_hours'):
            deadline = now + timedelta(hours=definition.rules['time_limit_hours'])
            expires = min(expires, deadline) if expires else deadline
        instance_id = challenge_id + suffix
        reference = self.db.collection("user_challenges").document(user_id).collection("active").document(instance_id)
        if challenge_id == "forgotten_gems_weekly":
            record = await self.generate_forgotten_gems_challenge(user_id)
            if not record:
                return {"success": False, "error": "No eligible forgotten pieces yet"}
        else:
            record = {"challenge_id": challenge_id, "user_id": user_id, "started_at": now, "expires_at": expires, "progress": 0, "target": _target(definition), "status": "in_progress", "items": [], "metadata": {}}
        record["expires_at"] = expires
        record["instance_id"] = instance_id
        epoch_fence = WriteEpochFence(self.db, user_id, initial_epoch)
        @firestore.transactional
        def create(transaction):
            epoch = epoch_fence.check(transaction)
            previous = read(reference, transaction)
            from google.cloud.firestore_v1.base_query import FieldFilter
            enrolled = list(self.db.collection('user_challenges').document(user_id).collection('active').where(filter=FieldFilter('challenge_id', '==', challenge_id)).stream(transaction=transaction))
            archived = list(self.db.collection('user_challenges').document(user_id).collection('completed').where(filter=FieldFilter('challenge_id', '==', challenge_id)).stream(transaction=transaction))
            from .challenge_periods import completed_in_period
            if completed_in_period(definition, [r.to_dict() for r in [*enrolled, *archived]], now):
                return {'success': False, 'error': 'Challenge already completed for this period'}
            for snapshot in enrolled:
                current = snapshot.to_dict(); expiry = current.get('expires_at')
                if current.get('status') == 'in_progress' and (not expiry or (expiry.astimezone(timezone.utc) if expiry.tzinfo else expiry.replace(tzinfo=timezone.utc)) > now):
                    return {'success': True, 'already_started': True, 'challenge': current}
            legacy_ref = self.db.collection("user_challenges").document(user_id).collection("active").document(challenge_id)
            legacy = read(legacy_ref, transaction) if instance_id != challenge_id else previous
            if previous or legacy and legacy.get("status") == "in_progress" and (not legacy.get("expires_at") or legacy["expires_at"].replace(tzinfo=timezone.utc) > now):
                return {"success": True, "already_started": True, "challenge": previous or legacy}
            transaction.set(reference, {**record, "app_data_epoch": epoch})
            return {"success": True, "challenge": record}
        result = create(self.db.transaction())
        from .challenge_actions import reconcile_action_challenges
        reconcile_action_challenges(self.db, user_id, epoch_fence.expected_epoch)
        return result

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
            cid = instance.get("challenge_id") or challenge_id
            if catalog_id and catalog_id != cid:
                return {"success": False, "error": "Challenge identity does not match"}
            definition = CHALLENGE_CATALOG.get(cid)
            if not definition:
                return {"success": False, "error": "Unknown challenge"}
            ledger_ref = self.db.collection("reward_ledger").document(key_for(user_id, "challenge", reference.path, str(instance.get("started_at"))))
            receipt = read(ledger_ref, transaction)
            if receipt or instance.get("status") == "completed":
                return {"success": True, "already_completed": True, "xp_awarded": 0}
            progress = instance.get("progress", 0)
            from .wear_projection import _target
            achieved = (progress.get("weeks_completed", 0) >= definition.rules.get("weeks_required", 52)) if cid == 'annual_wardrobe_master' and isinstance(progress, dict) else isinstance(progress, (int, float)) and progress >= _target(definition)
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
        from .challenge_actions import reconcile_action_challenges
        reconcile_action_challenges(self.db, user_id)
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
            from .challenge_periods import challenge_period
            from .wear_rewards import reward_timezone
            from zoneinfo import ZoneInfo
            profile = self.db.collection('users').document(user_id).get().to_dict() or {}
            now = datetime.now(ZoneInfo(reward_timezone(profile, 'UTC')))
            instances = {doc.id: doc.to_dict() for doc in self.db.collection('user_challenges').document(user_id).collection('active').stream()}
            from .challenge_periods import completed_in_period
            archives = [doc.to_dict() for doc in self.db.collection('user_challenges').document(user_id).collection('completed').stream()]
            available = []
            featured_docs = {doc.id: doc.to_dict().get("featured", False) for doc in self.db.collection("challenges").stream()}
            for challenge_id, challenge_def in CHALLENGE_CATALOG.items():
                if challenge_id == 'role_defender' or any(k in challenge_def.rules for k in ('pulls_required', 'rarity_required', 'token_balance_required', 'target_role')):
                    continue  # Dormant controls have no mounted user journey.
                featured = featured_docs.get(challenge_id, challenge_def.featured)
                logger.info(f"Checking challenge {challenge_id}: featured={challenge_def.featured}, cadence={challenge_def.cadence}")
                
                if completed_in_period(challenge_def, [*instances.values(), *archives], now):
                    continue
                suffix, _ = challenge_period(challenge_def.cadence, now)
                if challenge_id + suffix in instances:
                    continue
                # Skip if already active
                if challenge_id in active_ids:
                    logger.info(f"  -> Skipping {challenge_id}: already active")
                    continue
                
                # Only show featured or always-available challenges
                if featured or challenge_def.featured or challenge_def.cadence == "always":
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

    async def check_cold_start_progress(self, user_id: str, wardrobe_count: int, expected_epoch=None):
        """Award wardrobe milestones once from owned persisted items, atomically."""
        from firebase_admin import firestore
        from google.cloud.firestore_v1.base_query import FieldFilter
        from .reward_ledger import read, key_for, reward_patch, WriteEpochFence
        from .challenge_actions import _rows
        milestones = [(10, 50, 'starter_closet'), (25, 100, None), (50, 200, 'closet_cataloger')]
        user_ref = self.db.collection('users').document(user_id)
        progress_ref = self.db.collection('user_challenges').document(user_id).collection('active').document('cold_start_quest')
        fence = WriteEpochFence(self.db, user_id, expected_epoch)
        @firestore.transactional
        def apply(transaction):
            epoch = fence.check(transaction)
            user = read(user_ref, transaction)
            progress = read(progress_ref, transaction) or {'challenge_id': 'cold_start_quest', 'user_id': user_id, 'started_at': datetime.now(timezone.utc), 'status': 'in_progress', 'milestones_reached': []}
            archives = _rows(self.db.collection('user_challenges').document(user_id).collection('completed').where(filter=FieldFilter('challenge_id', '==', 'cold_start_quest')), transaction)
            # Legacy completions may predate active tombstones and reward receipts.
            # Completion is proof of earned entitlement, never permission to backfill.
            if progress.get('status') == 'completed' or any(row.get('status') == 'completed' for row in archives):
                return None
            archived_milestones = {value for row in archives for value in (row.get('milestones_reached') or [])}
            from .wardrobe_reads import owned_wardrobe_documents
            actual = len(owned_wardrobe_documents(self.db, user_id, transaction))
            receipts = [(threshold, xp, badge, self.db.collection('reward_ledger').document(key_for(user_id, 'cold-start-' + str(threshold)))) for threshold, xp, badge in milestones]
            prior = {threshold: read(ref, transaction) for threshold, _, _, ref in receipts}
            reached = set(progress.get('milestones_reached') or []) | archived_milestones
            total = 0; badges = []; new = []
            for threshold, xp, badge, ref in receipts:
                if actual >= threshold and threshold not in reached and not prior[threshold]:
                    from .wear_rewards import TOKEN_MULTIPLIERS
                    tokens = int(200 * TOKEN_MULTIPLIERS.get((user.get('role') or {}).get('current_role', 'starter'), 1)) if threshold == 50 else 0
                    mutation, result = reward_patch(user, xp=xp, tokens=tokens, badge=badge, timestamp=int(datetime.now(timezone.utc).timestamp()*1000))
                    user = {**user, **mutation};total += xp;new.append(threshold)
                    if badge: badges.append(badge)
                    transaction.set(ref, {'user_id': user_id, 'kind': 'cold_start', 'result': result, 'app_data_epoch': epoch})
                if actual >= threshold: reached.add(threshold)
            if new:
                transaction.update(user_ref, {k:user[k] for k in ('xp', 'level', 'style_tokens', 'badges', 'updatedAt')})
            next_progress = {**progress, 'progress': actual, 'target': 50, 'milestones_reached': sorted(reached), 'app_data_epoch': epoch}
            if actual >= 50 or progress.get('status') == 'completed':
                next_progress.update(status='completed', completed_at=progress.get('completed_at') or datetime.now(timezone.utc))
                archive = self.db.collection('user_challenges').document(user_id).collection('completed').document(key_for(progress_ref.path, str(progress.get('started_at'))))
                transaction.set(archive, next_progress)
            transaction.set(progress_ref, next_progress)
            if not new: return None
            return {'milestone_reached': max(new), 'xp_awarded': total, 'badge_awarded': badges[-1] if badges else None, 'message': f'{max(new)} items cataloged!'}
        return apply(self.db.transaction())

    async def expire_old_challenges(self, user_id: str, expected_epoch=None) -> int:
        """Archive expired instances atomically; never overwrite a completion."""
        from firebase_admin import firestore
        from .reward_ledger import read, key_for, WriteEpochFence
        now = datetime.now(timezone.utc)
        active = self.db.collection('user_challenges').document(user_id).collection('active')
        count = 0
        fence = WriteEpochFence(self.db, user_id, expected_epoch)
        for snapshot in active.stream():
            @firestore.transactional
            def expire(transaction):
                fence.check(transaction)
                current = read(snapshot.reference, transaction)
                if not current or current.get('status') != 'in_progress':
                    return False
                expires = current.get('expires_at')
                if not isinstance(expires, datetime) or (expires.astimezone(timezone.utc) if expires.tzinfo else expires.replace(tzinfo=timezone.utc)) > now:
                    return False
                target = self.db.collection('user_challenges').document(user_id).collection('completed').document(key_for(snapshot.reference.path, str(current.get('started_at'))))
                expired = {**current, 'status': 'expired', 'expired_at': now}
                transaction.set(target, expired)
                # Keep deterministic enrollment tombstone, preventing restart farming.
                transaction.update(snapshot.reference, {'status': 'expired', 'expired_at': now})
                return True
            count += int(expire(self.db.transaction()))
        return count

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

