"""
Challenge Service - Manages gamification challenges
Wraps existing Forgotten Gems logic and adds new challenge types
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
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
    
    async def start_challenge(
        self,
        user_id: str,
        challenge_id: str
    ) -> Dict[str, Any]:
        """
        Start a challenge for a user
        
        Returns:
            Dict with success status and challenge data
        """
        try:
            # Check if challenge exists in catalog
            if challenge_id not in CHALLENGE_CATALOG:
                logger.error(f"Challenge {challenge_id} not found in catalog")
                return {"success": False, "error": "Challenge not found"}
            
            challenge_def = CHALLENGE_CATALOG[challenge_id]
            
            # Check if user already has this challenge active
            existing_ref = self.db.collection('user_challenges')\
                .document(user_id)\
                .collection('active')\
                .document(challenge_id)
            
            existing_doc = existing_ref.get()
            if existing_doc.exists:
                logger.info(f"User {user_id} already has challenge {challenge_id} active")
                return {"success": False, "error": "Challenge already active"}
            
            # Generate challenge-specific data
            if challenge_id == "forgotten_gems_weekly":
                challenge_data = await self.generate_forgotten_gems_challenge(user_id)
                if not challenge_data:
                    return {"success": False, "error": "Could not generate challenge"}
            else:
                # Generic challenge start
                now = datetime.now()
                expires_at = now + timedelta(days=7) if challenge_def.cadence == "weekly" else None
                
                challenge_data = {
                    "challenge_id": challenge_id,
                    "user_id": user_id,
                    "started_at": now,
                    "expires_at": expires_at,
                    "progress": 0,
                    "target": challenge_def.rules.get("items_required", 1),
                    "status": ChallengeStatus.IN_PROGRESS.value,
                    "items": [],
                    "metadata": {}
                }
            
            # Save to Firestore
            existing_ref.set(challenge_data)
            
            # Log event
            from .gamification_service import gamification_service
            await gamification_service.log_gamification_event(
                user_id=user_id,
                event_type="challenge_started",
                metadata={
                    "challenge_id": challenge_id,
                    "challenge_type": challenge_def.type.value
                }
            )
            
            logger.info(f"✅ Started challenge {challenge_id} for user {user_id}")
            return {
                "success": True,
                "challenge": challenge_data
            }
            
        except Exception as e:
            logger.error(f"Error starting challenge: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def check_challenge_progress(
        self,
        user_id: str,
        outfit_data: Dict[str, Any]
    ) -> List[str]:
        """
        Check if any active challenges progressed based on outfit logged
        
        Args:
            user_id: User ID
            outfit_data: Dict with items and date worn
            
        Returns:
            List of challenge IDs that were completed
        """
        try:
            completed_challenges = []
            
            # Get user's active challenges
            active_challenges_ref = self.db.collection('user_challenges')\
                .document(user_id)\
                .collection('active')
            
            active_docs = list(active_challenges_ref.stream())
            
            for doc in active_docs:
                challenge_data = doc.to_dict()
                challenge_id = challenge_data.get('challenge_id')
                
                # Handle annual challenge separately
                if challenge_id == 'annual_wardrobe_master':
                    annual_result = await self.check_annual_challenge_progress(user_id, outfit_data)
                    if annual_result.get('challenge_completed'):
                        completed_challenges.append(challenge_id)
                    continue
                
                # Handle other challenge types (existing logic)
                challenge_items = challenge_data.get('items', [])
                outfit_items = outfit_data.get('items', [])
                
                # Check if any challenge items are in the outfit
                progress_made = False
                for item_id in outfit_items:
                    if item_id in challenge_items:
                        progress_made = True
                        break
                
                if progress_made:
                    # Update progress
                    current_progress = challenge_data.get('progress', 0)
                    new_progress = current_progress + 1
                    target = challenge_data.get('target', 1)
                    
                    update_data = {'progress': new_progress}
                    
                    # Check if challenge is now complete
                    if new_progress >= target:
                        update_data['status'] = ChallengeStatus.COMPLETED.value
                        update_data['completed_at'] = datetime.now()
                        
                        # Complete the challenge
                        await self.complete_challenge(user_id, challenge_id)
                        completed_challenges.append(challenge_id)
                    
                    # Update document
                    doc.reference.update(update_data)
                    
                    logger.info(f"Challenge {challenge_id} progress: {new_progress}/{target} for user {user_id}")
            
            return completed_challenges
            
        except Exception as e:
            logger.error(f"Error checking challenge progress: {e}", exc_info=True)
            return []
    
    async def complete_challenge(
        self,
        user_id: str,
        challenge_id: str
    ) -> Dict[str, Any]:
        """
        Mark a challenge as complete and award rewards
        
        Returns:
            Dict with rewards awarded
        """
        try:
            # Get challenge definition
            challenge_def = CHALLENGE_CATALOG.get(challenge_id)
            if not challenge_def:
                logger.error(f"Challenge {challenge_id} not in catalog")
                return {"success": False, "error": "Challenge not found"}
            
            # Move from active to completed
            active_ref = self.db.collection('user_challenges')\
                .document(user_id)\
                .collection('active')\
                .document(challenge_id)
            
            active_doc = active_ref.get()
            if not active_doc.exists:
                logger.warning(f"Challenge {challenge_id} not active for user {user_id}")
                return {"success": False, "error": "Challenge not active"}
            
            challenge_data = active_doc.to_dict()
            challenge_data['status'] = ChallengeStatus.COMPLETED.value
            challenge_data['completed_at'] = datetime.now()
            
            # Save to completed collection
            completed_ref = self.db.collection('user_challenges')\
                .document(user_id)\
                .collection('completed')\
                .document()
            
            completed_ref.set(challenge_data)
            
            # Delete from active
            active_ref.delete()
            
            # Award XP
            from .gamification_service import gamification_service
            from .addiction_service import AddictionService
            
            xp_reward = challenge_def.rewards.get('xp', 0)
            if xp_reward > 0:
                await gamification_service.award_xp(
                    user_id=user_id,
                    amount=xp_reward,
                    reason=f"Completed challenge: {challenge_def.title}",
                    metadata={"challenge_id": challenge_id}
                )
            
            # Award tokens (matching XP amount, with role multiplier applied)
            token_reward = challenge_def.rewards.get('tokens', xp_reward)  # Default to XP amount if not specified
            if token_reward > 0:
                addiction_service = AddictionService()
                token_result = await addiction_service.award_style_tokens(
                    user_id=user_id,
                    action_type="challenge_completed",
                    amount=token_reward  # Role multiplier will be applied internally
                )
                logger.info(f"✅ Awarded {token_result.get('tokens_awarded', 0)} tokens for challenge completion")
            
            # Award badge if specified
            badge_id = challenge_def.rewards.get('badge')
            badge_unlocked = None
            if badge_id:
                result = await gamification_service.unlock_badge(user_id, badge_id)
                if result.get('success'):
                    badge_unlocked = result.get('badge_info')
            
            # Log completion event
            await gamification_service.log_gamification_event(
                user_id=user_id,
                event_type="challenge_completed",
                xp_amount=xp_reward,
                metadata={
                    "challenge_id": challenge_id,
                    "challenge_type": challenge_def.type.value,
                    "badge_unlocked": badge_id if badge_unlocked else None
                }
            )
            
            logger.info(f"🎉 User {user_id} completed challenge {challenge_id}! Awarded {xp_reward} XP")
            
            return {
                "success": True,
                "xp_awarded": xp_reward,
                "badge_unlocked": badge_unlocked,
                "challenge_title": challenge_def.title
            }
            
        except Exception as e:
            logger.error(f"Error completing challenge: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
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
        """
        Auto-start annual challenge on first outfit log (or sign-up).
        Gets user signup date, calculates current cycle, creates challenge.
        """
        try:
            # Get user profile to find signup date
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"success": False, "error": "User not found"}
            
            user_data = user_doc.to_dict()
            signup_timestamp = user_data.get('createdAt', 0)
            
            # Convert timestamp to datetime
            if isinstance(signup_timestamp, int):
                signup_date = datetime.fromtimestamp(signup_timestamp / 1000)
            else:
                signup_date = datetime.now()  # Fallback
            
            current_date = datetime.now()
            cycle_number = self.calculate_annual_challenge_cycle(signup_date, current_date)
            
            # Check if challenge already exists for this cycle
            active_ref = self.db.collection('user_challenges').document(user_id).collection('active')
            existing_docs = list(active_ref.where('challenge_id', '==', 'annual_wardrobe_master').stream())
            
            # Check if any existing challenge is for current cycle
            for doc in existing_docs:
                challenge_data = doc.to_dict()
                if challenge_data.get('cycle_number') == cycle_number:
                    logger.info(f"Annual challenge already exists for user {user_id}, cycle {cycle_number}")
                    return {"success": True, "already_exists": True, "challenge_id": doc.id}
            
            # Get challenge definition
            challenge_def = CHALLENGE_CATALOG.get('annual_wardrobe_master')
            if not challenge_def:
                return {"success": False, "error": "Annual challenge not found in catalog"}
            
            # Calculate cycle start and end dates
            cycle_start = self.get_cycle_start_date(signup_date, cycle_number)
            cycle_end = cycle_start + timedelta(weeks=52)
            
            # Create challenge with cycle-specific badge name
            badge_id = f"annual_master_cycle_{cycle_number}"
            
            challenge_data = {
                'challenge_id': 'annual_wardrobe_master',
                'user_id': user_id,
                'started_at': cycle_start,
                'expires_at': cycle_end,
                'cycle_number': cycle_number,
                'progress': {
                    'total_outfits': 0,
                    'weeks_completed': 0,
                    'current_week_outfits': 0,
                    'current_week_start': None
                },
                'status': ChallengeStatus.IN_PROGRESS.value,
                'metadata': {
                    'badge_id': badge_id,
                    'outfits_per_week': challenge_def.rules.get('outfits_per_week', 5),
                    'weeks_required': challenge_def.rules.get('weeks_required', 52)
                }
            }
            
            # Save to Firestore
            doc_ref = active_ref.add(challenge_data)
            challenge_id = doc_ref[1].id
            
            logger.info(f"✅ Auto-started annual challenge for user {user_id}, cycle {cycle_number}")
            
            return {
                "success": True,
                "challenge_id": challenge_id,
                "cycle_number": cycle_number,
                "start_date": cycle_start.isoformat(),
                "end_date": cycle_end.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error auto-starting annual challenge: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def check_annual_challenge_progress(self, user_id: str, outfit_data: Dict) -> Dict[str, Any]:
        """
        Tracks progress for annual challenge: 5 outfits per week.
        Checks if weekly goal met, if cycle complete, awards milestones.
        """
        try:
            # Get active annual challenge
            active_ref = self.db.collection('user_challenges').document(user_id).collection('active')
            annual_docs = list(active_ref.where('challenge_id', '==', 'annual_wardrobe_master').stream())
            
            if not annual_docs:
                return {"progress_updated": False}
            
            challenge_doc = annual_docs[0]
            challenge_data = challenge_doc.to_dict()
            progress = challenge_data.get('progress', {})
            metadata = challenge_data.get('metadata', {})
            
            outfits_per_week = metadata.get('outfits_per_week', 5)
            weeks_required = metadata.get('weeks_required', 52)
            
            # Get outfit date
            outfit_date_ts = outfit_data.get('date')
            if isinstance(outfit_date_ts, int):
                outfit_date = datetime.fromtimestamp(outfit_date_ts / 1000)
            else:
                outfit_date = datetime.now()
            
            # Determine current week start (Monday)
            days_since_monday = outfit_date.weekday()
            week_start = outfit_date - timedelta(days=days_since_monday)
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Update progress
            current_week_start = progress.get('current_week_start')
            if current_week_start:
                # Convert to datetime if it's a timestamp
                if isinstance(current_week_start, int):
                    current_week_start = datetime.fromtimestamp(current_week_start / 1000)
                elif isinstance(current_week_start, str):
                    current_week_start = datetime.fromisoformat(current_week_start)
            
            # Check if this is a new week
            if not current_week_start or week_start > current_week_start:
                # New week - check if previous week goal was met
                if current_week_start:
                    prev_week_outfits = progress.get('current_week_outfits', 0)
                    if prev_week_outfits >= outfits_per_week:
                        # Week goal met - increment weeks_completed
                        progress['weeks_completed'] = progress.get('weeks_completed', 0) + 1
                        logger.info(f"✅ Week goal met for user {user_id}: {prev_week_outfits} outfits")
                
                # Start new week
                progress['current_week_start'] = week_start.isoformat()
                progress['current_week_outfits'] = 1
            else:
                # Same week - increment outfit count
                progress['current_week_outfits'] = progress.get('current_week_outfits', 0) + 1
            
            # Increment total outfits
            progress['total_outfits'] = progress.get('total_outfits', 0) + 1
            
            # Check if cycle complete (52 weeks with 5 outfits each)
            weeks_completed = progress.get('weeks_completed', 0)
            if progress.get('current_week_outfits', 0) >= outfits_per_week:
                # Current week also counts if goal is met
                effective_weeks = weeks_completed + 1
            else:
                effective_weeks = weeks_completed
            
            challenge_completed = False
            if effective_weeks >= weeks_required:
                challenge_completed = True
                # Complete the challenge
                await self.complete_challenge(user_id, challenge_doc.id, 'annual_wardrobe_master')
            
            # Update Firestore
            challenge_doc.reference.update({'progress': progress})
            
            return {
                "progress_updated": True,
                "total_outfits": progress['total_outfits'],
                "weeks_completed": weeks_completed,
                "current_week_outfits": progress.get('current_week_outfits', 0),
                "challenge_completed": challenge_completed
            }
            
        except Exception as e:
            logger.error(f"Error checking annual challenge progress: {e}", exc_info=True)
            return {"progress_updated": False, "error": str(e)}
    
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
            for challenge_id, challenge_def in CHALLENGE_CATALOG.items():
                logger.info(f"Checking challenge {challenge_id}: featured={challenge_def.featured}, cadence={challenge_def.cadence}")
                
                # Skip if already active
                if challenge_id in active_ids:
                    logger.info(f"  -> Skipping {challenge_id}: already active")
                    continue
                
                # Only show featured or always-available challenges
                if challenge_def.featured or challenge_def.cadence == "always":
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
                        "featured": challenge_def.featured
                    })
                else:
                    logger.info(f"  -> Skipping {challenge_id}: not featured and not always available")
            
            logger.info(f"Returning {len(available)} available challenges")
            return available
            
        except Exception as e:
            logger.error(f"Error getting available challenges: {e}", exc_info=True)
            return []
    
    async def check_30_wears_milestones(
        self,
        user_id: str,
        item_id: str,
        new_wear_count: int
    ) -> Optional[Dict[str, Any]]:
        """
        Check if item reached a 30-wears milestone
        
        Args:
            user_id: User ID
            item_id: Item ID
            new_wear_count: New wear count after increment
            
        Returns:
            Dict with badge info if milestone reached, None otherwise
        """
        try:
            badge_unlocked = None
            
            # Check milestones
            if new_wear_count == 30:
                badge_id = BadgeType.SUSTAINABLE_STYLE_BRONZE.value
            elif new_wear_count == 60:
                badge_id = BadgeType.SUSTAINABLE_STYLE_SILVER.value
            elif new_wear_count == 100:
                badge_id = BadgeType.SUSTAINABLE_STYLE_GOLD.value
            else:
                return None
            
            # Award badge
            from .gamification_service import gamification_service
            result = await gamification_service.unlock_badge(user_id, badge_id)
            
            if result.get('success'):
                # Award bonus XP
                xp_amounts = {30: 100, 60: 150, 100: 250}
                xp = xp_amounts.get(new_wear_count, 100)
                
                await gamification_service.award_xp(
                    user_id=user_id,
                    amount=xp,
                    reason=f"Reached {new_wear_count} wears milestone",
                    metadata={"item_id": item_id, "wear_count": new_wear_count}
                )
                
                badge_unlocked = result.get('badge_info')
                
                logger.info(f"🏆 User {user_id} reached {new_wear_count} wears on item {item_id}!")
            
            return {
                "milestone_reached": new_wear_count,
                "badge_unlocked": badge_unlocked,
                "xp_awarded": xp_amounts.get(new_wear_count, 100)
            }
            
        except Exception as e:
            logger.error(f"Error checking 30-wears milestone: {e}", exc_info=True)
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
                        metadata={"milestone": milestone["count"], "wardrobe_count": wardrobe_count}
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
            
            now = datetime.now()
            expired_count = 0
            
            for doc in active_ref.stream():
                challenge_data = doc.to_dict()
                expires_at = challenge_data.get('expires_at')
                
                if expires_at and isinstance(expires_at, datetime):
                    if expires_at < now:
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

