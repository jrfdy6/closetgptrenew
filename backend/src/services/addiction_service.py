"""
Addiction Service - Handles Ecosystem Engineering mechanics:
Streaks, Style Tokens (Gacha), and Role Decay
"""

import logging
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
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
    
    async def check_and_update_streak(self, user_id: str) -> Dict[str, Any]:
        """
        Check and update user's streak. Called when user logs an outfit.
        Returns streak status and multiplier.
        """
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                return {"error": "User not found"}
            
            user_data = user_doc.to_dict()
            streak_data = user_data.get('streak', {})
            
            current_streak = streak_data.get('current_streak', 0)
            longest_streak = streak_data.get('longest_streak', 0)
            last_log_date_str = streak_data.get('last_log_date')
            
            now = datetime.now()
            today_str = now.strftime('%Y-%m-%d')
            
            # Check if streak should be broken
            streak_broken = False
            if last_log_date_str:
                try:
                    last_log_date = datetime.strptime(last_log_date_str, '%Y-%m-%d')
                    days_since_last = (now - last_log_date).days
                    
                    if days_since_last > 1:
                        streak_broken = True
                        current_streak = 0
                except:
                    pass
            
            # Increment streak if logging today
            if not streak_broken and last_log_date_str != today_str:
                current_streak += 1
                if current_streak > longest_streak:
                    longest_streak = current_streak
            
            # Calculate streak multiplier (max 3x)
            streak_multiplier = min(1.0 + (current_streak * 0.1), 3.0)
            
            # Update Firestore
            updated_streak_data = {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'last_log_date': today_str,
                'streak_multiplier': streak_multiplier
            }
            
            user_ref.update({'streak': updated_streak_data})
            
            status = "ACTIVE" if not streak_broken else "BROKEN"
            message = f"Streak Active! {streak_multiplier:.1f}x XP Bonus." if not streak_broken else "Streak broken! Start over."
            
            return {
                "streak": current_streak,
                "longest_streak": longest_streak,
                "status": status,
                "message": message,
                "multiplier": streak_multiplier,
                "streak_broken": streak_broken
            }
            
        except Exception as e:
            logger.error(f"Error checking streak for user {user_id}: {e}", exc_info=True)
            return {"error": str(e), "streak": 0, "multiplier": 1.0}
    
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
                
                # DEMOTE to Scout
                decay_role = UserRole.SCOUT
                scout_config = self.ROLE_CONFIG[decay_role]
                
                new_role_data = {
                    'current_role': decay_role.value,
                    'role_earned_at': datetime.now().isoformat(),
                    'role_decay_checks_remaining': 0,
                    'privileges': scout_config['perks']
                }
                
                user_ref.update({'role': new_role_data})
                logger.warning(f"⚠️ Demoted user {user_id} from Trendsetter to Scout (inactivity)")
                
                return {
                    "demoted": True,
                    "new_role": decay_role.value,
                    "message": "You've been demoted to Scout due to inactivity. Log more outfits to regain Trendsetter status!"
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

