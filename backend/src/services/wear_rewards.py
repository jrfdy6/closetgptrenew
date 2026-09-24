"""Pure reward calculations used inside the canonical wear transaction.

No I/O or import-time Firebase initialization. Existing balances are baselines;
only a newly committed event can award these deltas.
"""
from datetime import date, timedelta
import math
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from ..custom_types.gamification import get_xp_for_level

TOKEN_MULTIPLIERS = {"starter": 1.0, "explorer": 1.15, "stylist": 1.3, "curator": 1.5, "master": 1.75}


def level_for(xp):
    level = 1
    while get_xp_for_level(level + 1) <= xp:
        level += 1
    return level


def reward_timezone(user, fallback):
    value = (user.get("location_data") or {}).get("timezone")
    if value:
        try:
            ZoneInfo(value)
            return value
        except (ZoneInfoNotFoundError, ValueError, TypeError):
            pass
    return fallback


def calculate_wear_reward(user, day, daily, timestamp):
    first = not daily.get("rewarded")
    old_streak = user.get("streak") or {}
    previous = old_streak.get("last_log_date")
    count = max(0, int(old_streak.get("current_streak", 0)))
    if first:
        count = count + 1 if previous == (date.fromisoformat(day) - timedelta(days=1)).isoformat() else (count if previous == day else 1)
    multiplier = min(1.0 + count * 0.1, 3.0)
    bonus = max(0, int(user.get("pending_xp_bonus", 0)))
    xp = int((10 + bonus) * multiplier)
    role = (user.get("role") or {}).get("current_role", "starter")
    tokens = int((50 if first else 5) * TOKEN_MULTIPLIERS.get(role, 1.0))
    old_xp = max(0, int(user.get("xp", 0)))
    token_state = user.get("style_tokens") or {}
    new_level = level_for(old_xp + xp)
    streak = {**old_streak, "current_streak": count, "longest_streak": max(count, int(old_streak.get("longest_streak", 0))), "last_log_date": day, "streak_multiplier": multiplier, "updated_at": timestamp}
    patch = {"xp": old_xp + xp, "level": new_level, "streak": streak,
             "pending_xp_bonus": 0, "pending_xp_bonus_source": None, "pending_xp_bonus_earned_at": None,
             "style_tokens": {**token_state, "balance": int(token_state.get("balance", 0)) + tokens, "total_earned": int(token_state.get("total_earned", 0)) + tokens, "total_spent": int(token_state.get("total_spent", 0)), "updated_at": timestamp}, "updatedAt": timestamp}
    result = {"xp_awarded": xp, "tokens_awarded": tokens, "base_xp": 10, "base_tokens": 50 if first else 5, "pending_bonus_consumed": bonus, "is_first_log_today": first, "current_streak": count, "streak_multiplier": multiplier, "level_up": new_level > level_for(old_xp), "new_level": new_level, "new_xp": old_xp + xp}
    return patch, result


def tve_delta(garment, user=None, wardrobe=None):
    from .tve_policy import TARGET_WEAR_RATES, RANGE_MIDPOINTS, CATEGORY_TO_SPENDING_KEY
    value = garment.get("value_per_wear")
    if value is None:
        category = CATEGORY_TO_SPENDING_KEY.get(str(garment.get("type", "")).lower().replace(" ", "_"), "tops")
        count = sum(CATEGORY_TO_SPENDING_KEY.get(str(item.get("type", "")).lower().replace(" ", "_"), "tops") == category for item in (wardrobe or []))
        spending = ((user or {}).get("spending_ranges") or {}).get(category, "unknown")
        value = round(RANGE_MIDPOINTS.get(spending, 100) / (count * TARGET_WEAR_RATES.get(category, 52)), 2) if count else 1.0
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
        raise ValueError("Invalid garment value_per_wear")
    return round(float(value), 6)
