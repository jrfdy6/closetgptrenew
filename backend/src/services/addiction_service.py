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
        UserRole.TRENDSETTER: {
            "outfits_per_week": 5,
            "grace_period_days": 7
        }
    }
    
    # Role configuration
    ROLE_CONFIG = {
        UserRole.LURKER: {
            "next_role": UserRole.SCOUT,
            "promotion_req": {"total_outfits_logged": 10},
            "perks": {
                "token_multiplier": 1.0,
                "xp_multiplier": 1.0,
                "gacha_luck_boost": 0.0
            },
            "description": "Basic app access"
        },
        UserRole.SCOUT: {
            "next_role": UserRole.TRENDSETTER,
            "promotion_req": {"total_outfits_logged": 30, "streak_days": 7},
            "perks": {
                "token_multiplier": 1.2,  # 20% bonus
                "xp_multiplier": 1.1,
                "gacha_luck_boost": 0.05  # +5% to rare/legendary rates
            },
            "description": "Style Scout - Early access, token bonuses"
        },
        UserRole.TRENDSETTER: {
            "next_role": None,  # Top tier
            "maintenance_req": {"outfits_per_week": 5},
            "decay_role": UserRole.SCOUT,
            "perks": {
                "token_multiplier": 1.5,  # 50% bonus
                "xp_multiplier": 1.2,
                "gacha_luck_boost": 0.10,  # +10% to rare/legendary rates
                "exclusive_gacha_pool": True,
                "priority_ai": True
            },
            "description": "Trendsetter - Premium perks, exclusive features"
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
    
    async def process_outfit_log(
        self, 
        user_id: str, 
        log_timestamp: int
    ) -> Dict[str, Any]:
        """
        Processes outfit log: calculates tokens, XP, updates streak, and performs DB updates.
        Returns the metrics awarded.
        """
        try:
            # 1. Check if first log today
            is_first_log = await self.is_first_outfit_today(user_id, log_timestamp)
            
            # 2. Get user role and token multiplier from local config
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"error": "User not found", "tokens_awarded": 0, "xp_awarded": 0}
            
            user_data = user_doc.to_dict()
            role_data = user_data.get('role', {})
            current_role_str = role_data.get('current_role', 'lurker')
            
            try:
                current_role = UserRole(current_role_str)
                role_config = self.ROLE_CONFIG.get(current_role, self.ROLE_CONFIG[UserRole.LURKER])
                token_multiplier = role_config['perks']['token_multiplier']
            except:
                token_multiplier = 1.0  # Default if role is invalid/not set
            
            # 3. Calculate base rewards
            base_tokens = 50 if is_first_log else 5
            base_xp = 10
            
            # 4. Update streak and get multiplier
            streak_data = await self.check_and_update_streak(
                user_id=user_id,
                log_timestamp=log_timestamp,
                is_first_log_today=is_first_log
            )
            xp_multiplier = streak_data.get('multiplier', 1.0)
            
            # 5. Check for pending XP bonus from gacha pull
            pending_xp_bonus = user_data.get('pending_xp_bonus', 0)
            if pending_xp_bonus > 0:
                # Apply bonus and clear it
                awarded_xp = int((base_xp + pending_xp_bonus) * xp_multiplier)
                user_ref.update({
                    'pending_xp_bonus': 0,
                    'pending_xp_bonus_source': None,
                    'pending_xp_bonus_earned_at': None
                })
                logger.info(f"✅ Applied pending XP bonus of {pending_xp_bonus} to outfit log")
            else:
                # Calculate final XP (XP is multiplied by streak)
                awarded_xp = int(base_xp * xp_multiplier)
            
            # 6. Award tokens (pass base amount - award_style_tokens applies role multiplier)
            tokens_result = await self.award_style_tokens(
                user_id=user_id,
                action_type="outfit_logged",
                amount=base_tokens  # Method will apply role multiplier internally
            )
            
            # 7. Award XP (use gamification service)
            from .gamification_service import gamification_service
            xp_result = await gamification_service.award_xp(
                user_id=user_id,
                amount=awarded_xp,  # Already multiplied by streak
                reason="outfit_logged",
                metadata={
                    "log_timestamp": log_timestamp,
                    "is_first_log_today": is_first_log,
                    "streak_multiplier": xp_multiplier
                }
            )
            
            # 8. Return metrics
            return {
                "tokens_awarded": tokens_result.get('tokens_awarded', 0),
                "base_tokens": base_tokens,
                "xp_awarded": awarded_xp,
                "base_xp": base_xp,
                "is_first_log_today": is_first_log,
                "current_streak": streak_data.get('current_streak', 0),
                "streak_multiplier": xp_multiplier,
                "role_multiplier": token_multiplier,
                "level_up": xp_result.get('level_up', False),
                "new_level": xp_result.get('level', 1)
            }
            
        except Exception as e:
            logger.error(f"Error processing outfit log for user {user_id}: {e}", exc_info=True)
            return {"error": "Gamification processing failed", "tokens_awarded": 0, "xp_awarded": 0}
    
    async def award_style_tokens(
        self,
        user_id: str,
        action_type: str,
        amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Award style tokens to user. Applies role multiplier.
        """
        try:
            # Get base amount from rates if not provided
            if amount is None:
                amount = self.TOKEN_EARN_RATES.get(action_type, 0)
            
            # Get user role to apply multiplier
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"error": "User not found"}
            
            user_data = user_doc.to_dict()
            role_data = user_data.get('role', {})
            current_role_str = role_data.get('current_role', 'lurker')
            
            try:
                current_role = UserRole(current_role_str)
                role_config = self.ROLE_CONFIG.get(current_role, self.ROLE_CONFIG[UserRole.LURKER])
                token_multiplier = role_config['perks']['token_multiplier']
            except:
                token_multiplier = 1.0
            
            # Apply multiplier
            final_amount = int(amount * token_multiplier)
            
            # Get current token balance
            tokens_data = user_data.get('style_tokens', {})
            current_balance = tokens_data.get('balance', 0)
            total_earned = tokens_data.get('total_earned', 0)
            
            # Update tokens
            updated_tokens_data = {
                'balance': current_balance + final_amount,
                'total_earned': total_earned + final_amount,
                'total_spent': tokens_data.get('total_spent', 0),
                'last_earned_at': datetime.now().isoformat()
            }
            
            user_ref.update({'style_tokens': updated_tokens_data})
            
            logger.info(f"🪙 Awarded {final_amount} tokens ({amount} base × {token_multiplier}x role multiplier) to user {user_id}")
            
            return {
                "tokens_awarded": final_amount,
                "base_amount": amount,
                "multiplier": token_multiplier,
                "new_balance": updated_tokens_data['balance']
            }
            
        except Exception as e:
            logger.error(f"Error awarding tokens to user {user_id}: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def perform_style_gacha_pull(self, user_id: str) -> Dict[str, Any]:
        """
        Perform a gacha pull. User spends tokens for variable reward.
        """
        try:
            # Check token balance
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"error": "User not found"}
            
            user_data = user_doc.to_dict()
            tokens_data = user_data.get('style_tokens', {})
            current_balance = tokens_data.get('balance', 0)
            
            if current_balance < self.GACHA_PULL_COST:
                return {
                    "error": "Insufficient tokens",
                    "balance": current_balance,
                    "required": self.GACHA_PULL_COST
                }
            
            # Get user role for luck boost
            role_data = user_data.get('role', {})
            current_role_str = role_data.get('current_role', 'lurker')
            
            try:
                current_role = UserRole(current_role_str)
                role_config = self.ROLE_CONFIG.get(current_role, self.ROLE_CONFIG[UserRole.LURKER])
                luck_boost = role_config['perks'].get('gacha_luck_boost', 0.0)
            except:
                luck_boost = 0.0
            
            # Roll for rarity (with role boost)
            roll = random.random()
            
            # Adjust drop rates with luck boost
            legendary_rate = self.DROP_RATES[GachaRarity.LEGENDARY] + luck_boost
            rare_rate = self.DROP_RATES[GachaRarity.RARE] + (luck_boost * 0.5)
            
            if roll < legendary_rate:
                rarity = GachaRarity.LEGENDARY
                reward_type = "style_recipe"
                reward_data = {
                    "type": "Avant-Garde Style Recipe",
                    "description": "Exclusive AI-generated outfit template for your wardrobe",
                    "rarity": "legendary"
                }
                visual_effect = "GOLD_CONFETTI"
            elif roll < (legendary_rate + rare_rate):
                rarity = GachaRarity.RARE
                reward_type = "style_insight"
                reward_data = {
                    "type": "Advanced Styling Insight",
                    "description": "Unlock new color combination or pattern mixing technique",
                    "rarity": "rare"
                }
                visual_effect = "PURPLE_SPARKLE"
            else:
                rarity = GachaRarity.COMMON
                reward_type = "xp_boost"
                reward_data = {
                    "type": "XP Bonus",
                    "description": "+50 XP bonus for your next outfit log",
                    "rarity": "common",
                    "xp_amount": 50
                }
                visual_effect = "BLUE_TICK"
            
            # Deduct tokens
            new_balance = current_balance - self.GACHA_PULL_COST
            total_spent = tokens_data.get('total_spent', 0) + self.GACHA_PULL_COST
            
            updated_tokens_data = {
                'balance': new_balance,
                'total_earned': tokens_data.get('total_earned', 0),
                'total_spent': total_spent,
                'last_earned_at': tokens_data.get('last_earned_at')
            }
            
            user_ref.update({'style_tokens': updated_tokens_data})
            
            # Store pull history
            pull_data = {
                'user_id': user_id,
                'rarity': rarity.value,
                'reward_type': reward_type,
                'reward_data': reward_data,
                'visual_effect': visual_effect,
                'cost': self.GACHA_PULL_COST,
                'pulled_at': datetime.now()
            }
            
            self.db.collection('users').document(user_id).collection('gacha_pulls').add(pull_data)
            
            # Store actual rewards based on rarity
            if rarity == GachaRarity.COMMON:
                # Store pending XP bonus in user profile
                user_ref.update({
                    'pending_xp_bonus': reward_data.get('xp_amount', 50),
                    'pending_xp_bonus_source': 'gacha_pull',
                    'pending_xp_bonus_earned_at': datetime.now().isoformat()
                })
                logger.info(f"✅ Stored pending XP bonus of {reward_data.get('xp_amount', 50)} for user {user_id}")
                
            elif rarity == GachaRarity.RARE:
                # Create style insight record
                insight_data = {
                    'user_id': user_id,
                    'type': 'gacha_reward',
                    'insight': reward_data.get('description', 'Advanced styling insight'),
                    'category': 'color_combination',  # or 'pattern_mixing' based on reward
                    'earned_at': datetime.now(),
                    'rarity': 'rare',
                    'applied': False
                }
                self.db.collection('users').document(user_id).collection('style_insights').add(insight_data)
                logger.info(f"✅ Created style insight record for user {user_id}")
                
            elif rarity == GachaRarity.LEGENDARY:
                # Unlock badge via gamification service
                try:
                    from .gamification_service import gamification_service
                    badge_result = await gamification_service.unlock_badge(
                        user_id=user_id,
                        badge_id="gacha_legendary"
                    )
                    if badge_result.get('success'):
                        logger.info(f"✅ Unlocked legendary badge for user {user_id}")
                    else:
                        logger.warning(f"⚠️ Failed to unlock badge: {badge_result.get('error')}")
                except Exception as badge_error:
                    logger.error(f"Error unlocking badge: {badge_error}", exc_info=True)
            
            logger.info(f"🎰 User {user_id} pulled {rarity.value} reward: {reward_type}")
            
            return {
                "rarity": rarity.value,
                "reward_type": reward_type,
                "reward_data": reward_data,
                "visual_effect": visual_effect,
                "remaining_tokens": new_balance,
                "dopamine_trigger": True
            }
            
        except Exception as e:
            logger.error(f"Error performing gacha pull for user {user_id}: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def check_and_update_role(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user qualifies for role promotion or demotion.
        """
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"error": "User not found"}
            
            user_data = user_doc.to_dict()
            role_data = user_data.get('role', {})
            current_role_str = role_data.get('current_role', 'lurker')
            
            try:
                current_role = UserRole(current_role_str)
            except:
                current_role = UserRole.LURKER
            
            # Check for promotion
            promotion_result = await self.check_for_promotion(user_id)
            
            # Check for demotion (only for Trendsetter)
            demotion_result = None
            if current_role == UserRole.TRENDSETTER:
                demotion_result = await self.check_trendsetter_decay(user_id)
            
            return {
                "current_role": current_role.value,
                "promotion": promotion_result,
                "demotion": demotion_result
            }
            
        except Exception as e:
            logger.error(f"Error checking role for user {user_id}: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def check_for_promotion(self, user_id: str) -> Dict[str, Any]:
        """Check if user meets criteria for next role"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"promoted": False}
            
            user_data = user_doc.to_dict()
            role_data = user_data.get('role', {})
            current_role_str = role_data.get('current_role', 'lurker')
            
            try:
                current_role = UserRole(current_role_str)
            except:
                current_role = UserRole.LURKER
            
            config = self.ROLE_CONFIG.get(current_role)
            if not config or not config.get('next_role'):
                return {"promoted": False, "reason": "Top tier"}
            
            next_role = config['next_role']
            reqs = config['promotion_req']
            
            # Get user stats
            # Count total outfits logged
            outfit_count = await self.get_user_outfit_count(user_id)
            
            # Get streak
            streak_data = user_data.get('streak', {})
            current_streak = streak_data.get('current_streak', 0)
            
            # Check requirements
            meets_outfits = outfit_count >= reqs.get('total_outfits_logged', 0)
            meets_streak = current_streak >= reqs.get('streak_days', 0)
            
            if meets_outfits and meets_streak:
                # PROMOTE!
                new_role_data = {
                    'current_role': next_role.value,
                    'role_earned_at': datetime.now().isoformat(),
                    'role_decay_checks_remaining': 0,
                    'privileges': config['perks']
                }
                
                user_ref.update({'role': new_role_data})
                logger.info(f"🚀 Promoted user {user_id} to {next_role.value}")
                
                return {
                    "promoted": True,
                    "new_role": next_role.value,
                    "message": f"You've been promoted to {next_role.value.title()}! Enjoy your new perks."
                }
            
            return {
                "promoted": False,
                "progress": {
                    "outfits": f"{outfit_count}/{reqs.get('total_outfits_logged', 0)}",
                    "streak": f"{current_streak}/{reqs.get('streak_days', 0)}"
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking promotion for user {user_id}: {e}", exc_info=True)
            return {"promoted": False, "error": str(e)}
    
    async def check_trendsetter_decay(self, user_id: str) -> Dict[str, Any]:
        """Check if Trendsetter needs to be demoted due to inactivity"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return None
            
            user_data = user_doc.to_dict()
            role_data = user_data.get('role', {})
            
            maintenance_req = self.ROLE_MAINTENANCE[UserRole.TRENDSETTER]
            outfits_per_week = maintenance_req['outfits_per_week']
            grace_period_days = maintenance_req['grace_period_days']
            
            # Check outfits logged in last 7 days
            seven_days_ago = datetime.now() - timedelta(days=7)
            seven_days_ago_ts = int(seven_days_ago.timestamp() * 1000)
            
            from google.cloud.firestore_v1 import FieldFilter
            outfit_history_ref = self.db.collection('outfit_history')
            query = outfit_history_ref.where(filter=FieldFilter('user_id', '==', user_id)).where(filter=FieldFilter('date_worn', '>=', seven_days_ago_ts))
            recent_outfits = list(query.stream())
            outfits_count = len(recent_outfits)
            
            if outfits_count < outfits_per_week:
                # Check if in grace period
                role_earned_at_str = role_data.get('role_earned_at')
                if role_earned_at_str:
                    try:
                        role_earned_at = datetime.fromisoformat(role_earned_at_str.replace('Z', '+00:00'))
                        days_since_promotion = (datetime.now() - role_earned_at.replace(tzinfo=None)).days
                        
                        if days_since_promotion < grace_period_days:
                            return {
                                "demoted": False,
                                "warning": True,
                                "message": f"Only {outfits_count}/{outfits_per_week} outfits this week. Maintain your Trendsetter status!",
                                "days_remaining": grace_period_days - days_since_promotion
                            }
                    except:
                        pass
                
                # DEMOTE to Scout and start recovery tracking
                decay_role = UserRole.SCOUT
                scout_config = self.ROLE_CONFIG[decay_role]
                
                # Initialize recovery tracking
                recovery_data = {
                    'in_recovery': True,
                    'recovery_started_at': datetime.now().isoformat(),
                    'recovery_weeks_completed': 0,
                    'recovery_weeks_required': 2,
                    'recovery_outfits_this_week': 0,
                    'recovery_week_start': datetime.now().isoformat()
                }
                
                new_role_data = {
                    'current_role': decay_role.value,
                    'role_earned_at': datetime.now().isoformat(),
                    'role_decay_checks_remaining': 0,
                    'privileges': scout_config['perks'],
                    'recovery': recovery_data
                }
                
                user_ref.update({'role': new_role_data})
                logger.warning(f"⚠️ Demoted user {user_id} from Trendsetter to Scout (inactivity). Recovery mode started.")
                
                return {
                    "demoted": True,
                    "new_role": decay_role.value,
                    "message": "You've been demoted to Scout. Complete 2 weeks of 5 outfits each to regain Trendsetter status!",
                    "recovery_mode": True
                }
            
            # Check if user is in recovery mode (easier path back to Trendsetter)
            recovery_data = role_data.get('recovery', {})
            if recovery_data.get('in_recovery'):
                recovery_result = await self.check_role_recovery(user_id, recovery_data, outfits_count)
                if recovery_result.get('recovered'):
                    return {
                        "demoted": False,
                        "recovered": True,
                        "new_role": UserRole.TRENDSETTER.value,
                        "message": "Congratulations! You've regained Trendsetter status!"
                    }
                return {
                    "demoted": False,
                    "warning": False,
                    "in_recovery": True,
                    "recovery_progress": recovery_result,
                    "outfits_this_week": outfits_count,
                    "required": outfits_per_week
                }
            
            return {
                "demoted": False,
                "warning": False,
                "outfits_this_week": outfits_count,
                "required": outfits_per_week
            }
            
        except Exception as e:
            logger.error(f"Error checking Trendsetter decay for user {user_id}: {e}", exc_info=True)
            return None
    
    async def check_role_recovery(self, user_id: str, recovery_data: Dict[str, Any], outfits_this_week: int) -> Dict[str, Any]:
        """
        Check if user in recovery mode has completed requirements to regain Trendsetter status.
        Recovery requires: 2 weeks of 5 outfits each (10 total, easier than normal maintenance).
        """
        try:
            recovery_started_at_str = recovery_data.get('recovery_started_at')
            if not recovery_started_at_str:
                return {"recovered": False, "error": "Invalid recovery data"}
            
            recovery_started_at = datetime.fromisoformat(recovery_started_at_str.replace('Z', '+00:00'))
            current_date = datetime.now()
            
            # Determine current week (Monday-based)
            days_since_monday = current_date.weekday()
            week_start = current_date - timedelta(days=days_since_monday)
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            recovery_week_start_str = recovery_data.get('recovery_week_start')
            if recovery_week_start_str:
                if isinstance(recovery_week_start_str, str):
                    recovery_week_start = datetime.fromisoformat(recovery_week_start_str.replace('Z', '+00:00'))
                else:
                    recovery_week_start = datetime.fromtimestamp(recovery_week_start_str / 1000)
            else:
                recovery_week_start = week_start
            
            # Check if new week started
            if week_start > recovery_week_start:
                # Previous week ended - check if goal was met
                prev_week_outfits = recovery_data.get('recovery_outfits_this_week', 0)
                if prev_week_outfits >= 5:
                    # Week goal met - increment weeks completed
                    weeks_completed = recovery_data.get('recovery_weeks_completed', 0) + 1
                    recovery_data['recovery_weeks_completed'] = weeks_completed
                    recovery_data['recovery_week_start'] = week_start.isoformat()
                    recovery_data['recovery_outfits_this_week'] = 1  # Current outfit counts for new week
                    
                    # Check if recovery complete (2 weeks done)
                    if weeks_completed >= 2:
                        # Promote back to Trendsetter
                        trendsetter_config = self.ROLE_CONFIG[UserRole.TRENDSETTER]
                        new_role_data = {
                            'current_role': UserRole.TRENDSETTER.value,
                            'role_earned_at': datetime.now().isoformat(),
                            'role_decay_checks_remaining': 0,
                            'privileges': trendsetter_config['perks'],
                            'recovery': {}  # Clear recovery data
                        }
                        
                        user_ref = self.db.collection('users').document(user_id)
                        user_ref.update({'role': new_role_data})
                        
                        logger.info(f"✅ User {user_id} recovered Trendsetter status after 2 weeks of recovery")
                        
                        return {
                            "recovered": True,
                            "weeks_completed": weeks_completed
                        }
                else:
                    # Previous week goal not met - reset recovery
                    recovery_data['recovery_weeks_completed'] = 0
                    recovery_data['recovery_week_start'] = week_start.isoformat()
                    recovery_data['recovery_outfits_this_week'] = 1
            else:
                # Same week - increment outfit count
                recovery_data['recovery_outfits_this_week'] = recovery_data.get('recovery_outfits_this_week', 0) + 1
            
            # Update recovery data in Firestore
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({'role.recovery': recovery_data})
            
            return {
                "recovered": False,
                "weeks_completed": recovery_data.get('recovery_weeks_completed', 0),
                "weeks_required": 2,
                "outfits_this_week": recovery_data.get('recovery_outfits_this_week', 0),
                "outfits_required_per_week": 5
            }
            
        except Exception as e:
            logger.error(f"Error checking role recovery for user {user_id}: {e}", exc_info=True)
            return {"recovered": False, "error": str(e)}
    
    async def get_user_outfit_count(self, user_id: str) -> int:
        """Get total number of outfits logged by user"""
        try:
            from google.cloud.firestore_v1 import FieldFilter
            outfit_history_ref = self.db.collection('outfit_history')
            query = outfit_history_ref.where(filter=FieldFilter('user_id', '==', user_id))
            outfits = list(query.stream())
            return len(outfits)
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

