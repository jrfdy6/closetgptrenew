"""
Addiction Service - Handles Ecosystem Engineering mechanics:
Streaks, Style Tokens (Gacha), and Role Decay
"""

import logging
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, time, timezone as tz
from zoneinfo import ZoneInfo
from google.cloud.firestore_v1 import FieldFilter
from ..config.firebase import db
from ..custom_types.gamification import (
    UserRole,
    GachaRarity,
)

logger = logging.getLogger(__name__)


class AddictionService:
    """Manages the 'Dark Pattern' mechanics: Streaks, Variable Rewards, and Role Decay"""
    
    def __init__(self):
        self.db = db
    
    # Gacha Drop Rates (Variable Ratio Reinforcement)
    DROP_RATES = {
        GachaRarity.COMMON: 0.70,      # 70% chance
        GachaRarity.RARE: 0.25,         # 25% chance
        GachaRarity.LEGENDARY: 0.05     # 5% chance
    }
    
    # Token earning rates
    TOKEN_EARN_RATES = {
        "outfit_logged": 50,
        "challenge_completed": 75,  # Will be overridden by challenge definition
        "streak_bonus": 25,
        "feedback_given": 10
    }
    
    # Gacha pull cost
    GACHA_PULL_COST = 500
    
    # Role maintenance requirements
    ROLE_MAINTENANCE = {
        UserRole.MASTER: {
            "outfits_per_week": 5,
            "grace_period_days": 7
        }
    }
    
    # Role configuration - 5 levels with progressive perks
    ROLE_CONFIG = {
        UserRole.STARTER: {
            "next_role": UserRole.EXPLORER,
            "promotion_req": {"total_outfits_logged": 10},
            "perks": {
                "token_multiplier": 1.0,
                "gacha_luck_boost": 0.0
            },
            "description": "Starter - Basic app access"
        },
        UserRole.EXPLORER: {
            "next_role": UserRole.STYLIST,
            "promotion_req": {"total_outfits_logged": 25, "streak_days": 5},
            "perks": {
                "token_multiplier": 1.15,  # 15% bonus
                "gacha_luck_boost": 0.03  # +3% to rare/legendary rates
            },
            "description": "Explorer - Early access, token bonuses"
        },
        UserRole.STYLIST: {
            "next_role": UserRole.CURATOR,
            "promotion_req": {"total_outfits_logged": 50, "streak_days": 10},
            "perks": {
                "token_multiplier": 1.3,  # 30% bonus
                "gacha_luck_boost": 0.06  # +6% to rare/legendary rates
            },
            "description": "Stylist - Enhanced perks and bonuses"
        },
        UserRole.CURATOR: {
            "next_role": UserRole.MASTER,
            "promotion_req": {"total_outfits_logged": 100, "streak_days": 14},
            "perks": {
                "token_multiplier": 1.5,  # 50% bonus
                "gacha_luck_boost": 0.08  # +8% to rare/legendary rates
            },
            "description": "Curator - Premium features and priority access"
        },
        UserRole.MASTER: {
            "next_role": None,  # Top tier
            "maintenance_req": {"outfits_per_week": 5},
            "decay_role": UserRole.CURATOR,
            "perks": {
                "token_multiplier": 1.75,  # 75% bonus
                "gacha_luck_boost": 0.12  # +12% to rare/legendary rates
            },
            "description": "Master - Top tier with exclusive features"
        }
    }
    
    def get_user_timezone(self, user_id: str) -> Optional[ZoneInfo]:
        """Get user's IANA timezone from profile, fallback to None (UTC)"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return None
            
            user_data = user_doc.to_dict()
            location_data = user_data.get('location_data', {})
            timezone_str = location_data.get('timezone')
            
            if timezone_str:
                try:
                    return ZoneInfo(timezone_str)
                except Exception as e:
                    logger.warning(f"Invalid timezone {timezone_str} for user {user_id}: {e}")
                    return None
            return None
            
        except Exception as e:
            logger.error(f"Error getting user timezone: {e}")
            return None
    
    async def is_first_outfit_today(self, user_id: str, log_timestamp: int) -> bool:
        """
        Check if this is the first outfit log in user's local day.
        Uses strict midnight rule with user's stored IANA timezone.
        
        Args:
            user_id (str): The ID of the user.
            log_timestamp (int): The timestamp (ms) of the *current* log being processed.
            
        Returns:
            bool: True if no previous logs exist for the user's local calendar day.
        """
        try:
            # Set default to UTC if no timezone is found
            user_tz = self.get_user_timezone(user_id) or tz.utc
            
            # 1. Convert the current UTC timestamp into the user's local datetime
            utc_dt = datetime.fromtimestamp(log_timestamp / 1000, tz=tz.utc)
            local_dt = utc_dt.astimezone(user_tz)
            
            # 2. Find the precise moment of local midnight for that day
            # datetime.combine sets the time to 00:00:00 in the correct timezone
            local_midnight = datetime.combine(local_dt.date(), time.min, tzinfo=user_tz)
            
            # 3. Convert local midnight back to a UTC timestamp (in milliseconds)
            # This gives us the exact UTC time that represents the start of the user's day
            utc_midnight_timestamp_ms = int(local_midnight.timestamp() * 1000)

            # 4. Query Firestore efficiently
            # We look for ANY log by this user, created AFTER their local midnight (in UTC).
            outfit_history_ref = self.db.collection('outfit_history')
            query = outfit_history_ref.where(filter=FieldFilter('user_id', '==', user_id)) \
                                     .where(filter=FieldFilter('created_at', '>=', utc_midnight_timestamp_ms)) \
                                     .order_by('created_at') \
                                     .limit(1)
            
            # If the query returns a log, it's NOT the first log today.
            logs = list(query.stream())
            return len(logs) == 0
            
        except Exception as e:
            logger.error(f"FATAL ERROR in timezone logic for user {user_id}: {e}", exc_info=True)
            # Fallback: assume it's first if logic fails to prevent token loss
            return True
    
    async def check_and_update_streak(self, user_id: str, log_timestamp: int, is_first_log_today: bool) -> Dict[str, Any]:
        """
        Updates the user's streak status based on the strict midnight rule (local time).
        Returns updated streak status and multiplier.
        """
        try:
            user_tz = self.get_user_timezone(user_id) or tz.utc
            current_log_dt = datetime.fromtimestamp(log_timestamp / 1000, tz=tz.utc).astimezone(user_tz)
            current_date_str = current_log_dt.strftime('%Y-%m-%d')
            
            # Firestore is synchronous - no await needed
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                logger.error(f"User {user_id} not found for streak update")
                return {"current_streak": 0, "multiplier": 1.0, "was_broken": False}
            
            user_data = user_doc.to_dict()
            streak_data = user_data.get('streak', {})
            
            last_log_date_str = streak_data.get('last_log_date')
            current_streak_count = streak_data.get('current_streak', 0)
            longest_streak = streak_data.get('longest_streak', 0)
            is_broken = False
            
            if last_log_date_str:
                try:
                    last_log_date = datetime.strptime(last_log_date_str, '%Y-%m-%d').date()
                    current_date = current_log_dt.date()
                    time_difference_days = (current_date - last_log_date).days
                    
                    if time_difference_days == 1:
                        # Perfect continuation
                        current_streak_count += 1
                        if current_streak_count > longest_streak:
                            longest_streak = current_streak_count
                    elif time_difference_days > 1:
                        # Streak broken - reset to 1
                        current_streak_count = 1
                        is_broken = True
                    elif time_difference_days == 0:
                        # Same day - streak count is preserved
                        pass
                    else:
                        # Time traveler or parsing error, start new
                        current_streak_count = 1
                except Exception as e:
                    logger.warning(f"Error parsing last_log_date {last_log_date_str}: {e}")
                    current_streak_count = 1
            else:
                # First ever log - start streak at 1
                current_streak_count = 1
            
            # Calculate streak multiplier (1.0 + 0.1 per day, max 3.0x)
            streak_multiplier = min(1.0 + (current_streak_count * 0.1), 3.0)
            
            # Update Firestore (synchronous - no await)
            updated_streak_data = {
                'current_streak': current_streak_count,
                'longest_streak': longest_streak,
                'last_log_date': current_date_str,
                'streak_multiplier': streak_multiplier,
                'updated_at': log_timestamp
            }
            
            user_ref.update({'streak': updated_streak_data})
            
            logger.info(f"✅ Updated streak for user {user_id}: {current_streak_count} days (multiplier: {streak_multiplier}x)")
            
            return {
                "current_streak": current_streak_count,
                "longest_streak": longest_streak,
                "multiplier": streak_multiplier,
                "was_broken": is_broken,
                "last_log_date": current_date_str
            }
            
        except Exception as e:
            logger.error(f"Error updating streak for user {user_id}: {e}", exc_info=True)
            return {"current_streak": 0, "multiplier": 1.0, "was_broken": True}
    
    async def process_outfit_log(self, user_id: str, log_timestamp: int, event_id: Optional[str] = None) -> Dict[str, Any]:
        """Read a committed canonical reward; never create a second wear award."""
        if not event_id:
            raise ValueError("A canonical wear event is required")
        snapshot = self.db.collection("reward_ledger").document(event_id).get()
        receipt = snapshot.to_dict() if snapshot.exists else None
        if not receipt or receipt.get("user_id") != user_id:
            raise ValueError("Wear reward receipt unavailable")
        return {**receipt.get("rewards", {}), "xp_awarded": 0, "tokens_awarded": 0, "already_recorded": True}

    async def award_style_tokens(
        self,
        user_id: str,
        action_type: str,
        amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Award style tokens to user. Applies role multiplier.
        """
        from .reward_ledger import award
        from uuid import uuid4
        value = self.TOKEN_EARN_RATES.get(action_type, 0) if amount is None else amount
        return award(self.db, user_id, "legacy-tokens-" + str(uuid4()), tokens=value, apply_role_multiplier=True, metadata={"action_type": action_type})

    async def perform_style_gacha_pull(self, user_id: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """One token debit, stored result and reward per explicit action key."""
        from uuid import uuid4
        from firebase_admin import firestore
        from .reward_ledger import read, key_for, WriteEpochFence
        from .app_data_privacy import require_app_data_writable
        from .outfit_wear import KEY
        key = idempotency_key or str(uuid4())
        if not isinstance(key, str) or not KEY.fullmatch(key):
            raise ValueError("Invalid pull request identifier")
        user_ref = self.db.collection("users").document(user_id)
        pull_ref = user_ref.collection("gacha_pulls").document(key_for(user_id, key))
        # Stable random draw across Firestore contention retries.
        roll = random.random()
        timestamp = datetime.now(tz.utc)
        epoch_fence = WriteEpochFence(self.db, user_id)
        @firestore.transactional
        def pull(transaction):
            epoch_fence.check(transaction)
            user = read(user_ref, transaction)
            previous = read(pull_ref, transaction)
            if previous:
                return {**previous["result"], "remaining_tokens": int((user.get("style_tokens") or {}).get("balance", 0)), "already_recorded": True}
            balance = user.get("style_tokens") or {}
            current = int(balance.get("balance", 0))
            if current < self.GACHA_PULL_COST:
                return {"error": "Insufficient tokens", "balance": current, "required": self.GACHA_PULL_COST}
            try:
                role = UserRole((user.get("role") or {}).get("current_role", "starter"))
            except ValueError:
                role = UserRole.STARTER
            luck = self.ROLE_CONFIG[role]["perks"].get("gacha_luck_boost", 0)
            if roll < self.DROP_RATES[GachaRarity.LEGENDARY] + luck:
                rarity, kind, effect = "LEGENDARY", "badge", "GOLD_CONFETTI"
                reward = {"type": "Legendary Style Badge", "description": "Legendary achievement badge saved to your collection", "rarity": "legendary"}
            elif roll < self.DROP_RATES[GachaRarity.LEGENDARY] + luck + self.DROP_RATES[GachaRarity.RARE] + luck * .5:
                rarity, kind, effect = "RARE", "style_insight", "PURPLE_SPARKLE"
                reward = {"type": "Advanced Styling Insight", "description": "Try one patterned piece with solid colors, repeating one accent color across the outfit.", "rarity": "rare"}
            else:
                rarity, kind, effect = "COMMON", "xp_boost", "BLUE_TICK"
                reward = {"type": "XP Bonus", "description": "+50 XP bonus for your next outfit log", "rarity": "common", "xp_amount": 50}
            patch = {"style_tokens": {**balance, "balance": current - self.GACHA_PULL_COST, "total_spent": int(balance.get("total_spent", 0)) + self.GACHA_PULL_COST}}
            if rarity == "COMMON":
                patch.update({"pending_xp_bonus": max(0, int(user.get("pending_xp_bonus", 0))) + 50, "pending_xp_bonus_source": "gacha_pull", "pending_xp_bonus_earned_at": timestamp.isoformat()})
            elif rarity == "LEGENDARY":
                patch["badges"] = list(dict.fromkeys([*(user.get("badges") or []), "gacha_legendary"]))
            else:
                transaction.set(user_ref.collection("style_insights").document(pull_ref.id), {"user_id": user_id, "type": "gacha_reward", "insight": reward["description"], "category": "color_combination", "earned_at": timestamp, "rarity": "rare", "applied": False})
            result = {"rarity": rarity, "reward_type": kind, "reward_data": reward, "visual_effect": effect, "remaining_tokens": current - self.GACHA_PULL_COST, "dopamine_trigger": True, "already_recorded": False}
            transaction.update(user_ref, patch)
            transaction.set(pull_ref, {"user_id": user_id, "rarity": rarity, "reward_type": kind, "reward_data": reward, "visual_effect": effect, "cost": self.GACHA_PULL_COST, "pulled_at": timestamp, "result": result})
            return result
        result = pull(self.db.transaction())
        return {**result, 'app_data_epoch': epoch_fence.expected_epoch}

    async def check_and_update_role(self, user_id: str, expected_epoch=None) -> Dict[str, Any]:
        from firebase_admin import firestore
        from .reward_ledger import read, WriteEpochFence
        from .challenge_actions import _rows
        from .wear_projection import _ms
        from .wear_rewards import reward_timezone
        ref = self.db.collection('users').document(user_id)
        fence = WriteEpochFence(self.db, user_id, expected_epoch)
        @firestore.transactional
        def reconcile(transaction):
            fence.check(transaction)
            user = read(ref, transaction)
            role = dict(user.get('role') or {})
            raw = role.get('current_role', 'starter')
            current = {'lurker':'starter','scout':'explorer','trendsetter':'master'}.get(raw, raw)
            try: current_role = UserRole(current)
            except ValueError: current_role = UserRole.STARTER; current = 'starter'
            history = [r for r in _rows(self.db.collection('outfit_history').where(filter=FieldFilter('user_id', '==', user_id)), transaction) if not r.get('undone')]
            now = datetime.now(tz.utc); now_ms = int(now.timestamp()*1000)
            recent = sum(now_ms-7*86400000 <= _ms(r.get('date_worn')) <= now_ms for r in history)
            result = {'promoted': False, 'demoted': False, 'outfits_this_week': recent, 'required': 5}
            recovery = dict(role.get('recovery') or {})
            if recovery.get('in_recovery'):
                zone = ZoneInfo(reward_timezone(user, 'UTC'))
                today = now.astimezone(zone).date(); this_week = today-timedelta(days=today.weekday())
                began = _ms(recovery.get('recovery_started_at'))
                weeks = {}
                for event in history:
                    worn = _ms(event.get('date_worn'))
                    if began <= worn <= now_ms:
                        day = datetime.fromtimestamp(worn/1000, zone).date(); week = day-timedelta(days=day.weekday())
                        weeks[week] = weeks.get(week, 0)+1
                previous = this_week-timedelta(days=7)
                completed = int(weeks.get(previous,0)>=5)
                if completed and weeks.get(previous-timedelta(days=7),0)>=5: completed=2
                recovery.update(recovery_weeks_completed=completed,recovery_outfits_this_week=weeks.get(this_week,0),recovery_week_start=this_week.isoformat())
                role['recovery'] = recovery
                result.update(in_recovery=True,weeks_completed=completed,outfits_this_week=weeks.get(this_week,0))
                if completed>=2:
                    current='master'; role['role_earned_at']=now.isoformat();role['recovery']={};result.update(recovered=True,new_role='master',in_recovery=False)
            elif current == 'master':
                earned = _ms(role.get('role_earned_at'))
                if recent<5 and earned and now_ms-earned >= 7*86400000:
                    current='curator'; role['role_earned_at']=now.isoformat()
                    role['recovery']={'in_recovery':True,'recovery_started_at':now.isoformat(),'recovery_weeks_completed':0,'recovery_weeks_required':2,'recovery_outfits_this_week':0,'recovery_week_start':now.date().isoformat()}
                    result.update(demoted=True,new_role='curator',recovery_mode=True)
                elif recent<5: result.update(warning=True)
            else:
                config=self.ROLE_CONFIG[current_role];reqs=config.get('promotion_req',{})
                streak_data = user.get('streak') or {}
                streak = 0
                try:
                    last_day = datetime.fromisoformat(streak_data.get('last_log_date', '')).date()
                    today = now.astimezone(ZoneInfo(reward_timezone(user, 'UTC'))).date()
                    if 0 <= (today - last_day).days <= 1:
                        streak = int(streak_data.get('current_streak', 0))
                except (TypeError, ValueError):
                    pass
                result['progress']={'outfits':f"{len(history)}/{reqs.get('total_outfits_logged',0)}",'streak':f"{streak}/{reqs.get('streak_days',0)}"}
                if config.get('next_role') and len(history)>=reqs.get('total_outfits_logged',0) and streak>=reqs.get('streak_days',0):
                    current=config['next_role'].value;role['role_earned_at']=now.isoformat();result.update(promoted=True,new_role=current)
            role.update(current_role=current,privileges=self.ROLE_CONFIG[UserRole(current)]['perks'])
            if role != (user.get('role') or {}): transaction.update(ref,{'role':role})
            return result
        return reconcile(self.db.transaction())

    async def check_for_promotion(self, user_id: str, expected_epoch=None):
        return await self.check_and_update_role(user_id, expected_epoch)

    async def check_master_decay(self, user_id: str, expected_epoch=None):
        return await self.check_and_update_role(user_id, expected_epoch)

    async def check_role_recovery(self, user_id: str, recovery_data=None, outfits_this_week=0, expected_epoch=None):
        # Compatibility parameters are never trusted as activity evidence.
        return await self.check_and_update_role(user_id, expected_epoch)

    async def get_user_outfit_count(self, user_id: str) -> int:
        """Get total number of outfits logged by user"""
        try:
            from google.cloud.firestore_v1 import FieldFilter
            outfit_history_ref = self.db.collection('outfit_history')
            query = outfit_history_ref.where(filter=FieldFilter('user_id', '==', user_id))
            outfits = list(query.stream())
            return sum(not item.to_dict().get("undone") for item in outfits)
        except Exception as e:
            logger.error(f"Error getting outfit count for user {user_id}: {e}")
            return 0
    
    async def get_user_addiction_state(self, user_id: str) -> Dict[str, Any]:
        """Get complete addiction state for user"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"error": "User not found"}
            
            user_data = user_doc.to_dict()
            
            return {
                "streak": user_data.get('streak', {}),
                "style_tokens": user_data.get('style_tokens', {}),
                "role": user_data.get('role', {})
            }
            
        except Exception as e:
            logger.error(f"Error getting addiction state for user {user_id}: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def get_user_audit_state(self, user_id: str, season_id: str = "current") -> Dict[str, Any]:
        """
        Get the Wardrobe Audit state for a user.
        ROI-focused audit that helps users understand wardrobe utilization.
        Access is gated by subscription plan (FREE/PRO/PREMIUM).
        """
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"error": "User not found"}
            
            user_data = user_doc.to_dict()
            
            # 1. Access Control - Check subscription plan
            plan = user_data.get('subscription_plan', 'FREE')
            
            # 2. Get wardrobe size
            from google.cloud.firestore_v1 import FieldFilter
            wardrobe_query = self.db.collection('wardrobe').where(filter=FieldFilter('user_id', '==', user_id))
            wardrobe_docs = list(wardrobe_query.stream())
            total_items = len(wardrobe_docs)
            
            # 3. Get worn items this season
            outfit_history_query = self.db.collection('outfit_history').where(filter=FieldFilter('user_id', '==', user_id))
            worn_item_ids = set()
            
            for doc in outfit_history_query.stream():
                entry = doc.to_dict()
                items = entry.get('items', [])
                for item in items:
                    if isinstance(item, dict):
                        worn_item_ids.add(item.get('id'))
                    elif isinstance(item, str):
                        worn_item_ids.add(item)
            
            # 4. Calculate WUR (Wardrobe Utilization Rate)
            wur = (len(worn_item_ids) / total_items * 100) if total_items > 0 else 0
            
            # 5. Calculate unused items (potential donation candidates)
            unused_items = total_items - len(worn_item_ids)
            
            # 6. Estimate potential savings (using spending ranges)
            estimated_cost_per_item = 0
            if plan in ['PRO', 'PREMIUM']:
                spending_ranges = user_data.get('spending_ranges', {})
                annual_total = spending_ranges.get('annual_total', '$2,500-$5,000')
                # Parse spending range and estimate
                if annual_total:
                    # Simple estimation: extract number and divide by typical items
                    try:
                        # Extract digits from range (e.g., "$2,500-$5,000" → ~$3,750 avg)
                        import re
                        numbers = re.findall(r'\d+', annual_total.replace(',', ''))
                        if numbers:
                            avg_spend = (int(numbers[0]) + int(numbers[-1]) if len(numbers) > 1 else int(numbers[0])) / 2
                            estimated_cost_per_item = avg_spend / max(total_items, 1)
                    except:
                        estimated_cost_per_item = 50  # Default estimate
            
            estimated_waste = unused_items * estimated_cost_per_item if plan in ['PRO', 'PREMIUM'] else 0
            
            # 7. Build response based on plan
            base_response = {
                "plan": plan,
                "season_id": season_id,
                "metrics": {
                    "total_items": total_items,
                    "items_worn": len(worn_item_ids),
                    "items_unworn": unused_items,
                }
            }
            
            if plan == 'FREE':
                # Show ghost report - numbers only, no dollar values
                base_response["wur"] = None  # Locked
                base_response["estimated_waste"] = None  # Locked
                base_response["lock_message"] = "🔒 Unlock PRO to see your Wardrobe Utilization Rate"
                base_response["donation_manifest"] = None
            
            elif plan == 'PRO':
                # Show WUR and utilization
                base_response["wur"] = round(wur, 1)
                base_response["estimated_waste"] = None  # Still locked
                base_response["lock_message"] = None
                base_response["donation_manifest"] = None
            
            elif plan == 'PREMIUM':
                # Full access - show everything including donation list
                base_response["wur"] = round(wur, 1)
                base_response["estimated_waste"] = round(estimated_waste, 2)
                base_response["lock_message"] = None
                base_response["donation_manifest"] = await self.generate_donation_manifest(user_id, list(worn_item_ids))
            
            return base_response
            
        except Exception as e:
            logger.error(f"Error getting audit state for user {user_id}: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def generate_donation_manifest(self, user_id: str, worn_item_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Generate a list of items recommended for donation.
        Only called if user has PREMIUM subscription.
        """
        try:
            from google.cloud.firestore_v1 import FieldFilter
            
            # Get all wardrobe items
            wardrobe_query = self.db.collection('wardrobe').where(filter=FieldFilter('user_id', '==', user_id))
            wardrobe_docs = list(wardrobe_query.stream())
            
            donation_candidates = []
            
            for doc in wardrobe_docs.stream():
                item_data = doc.to_dict()
                item_id = doc.id
                
                # Add to donation list if never worn
                if item_id not in worn_item_ids:
                    donation_candidates.append({
                        "item_id": item_id,
                        "name": item_data.get('name', 'Unknown'),
                        "type": item_data.get('type', 'Unknown'),
                        "color": item_data.get('color', 'Unknown'),
                        "reason": "Never worn this season",
                        "wear_count": item_data.get('wearCount', 0)
                    })
            
            # Sort by wear count (never worn first, then least worn)
            donation_candidates.sort(key=lambda x: x['wear_count'])
            
            return donation_candidates[:20]  # Return top 20 candidates
            
        except Exception as e:
            logger.error(f"Error generating donation manifest for user {user_id}: {e}", exc_info=True)
            return []


# Singleton instance
addiction_service = AddictionService()

