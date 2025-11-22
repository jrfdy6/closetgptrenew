from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any

DEFAULT_SUBSCRIPTION_TIER = "tier1"

TIER_LIMITS: Dict[str, Optional[int]] = {
    "tier1": 1,
    "tier2": 7,
    "tier3": 30,
}

WEEKLY_ALLOWANCE_SECONDS = 7 * 24 * 60 * 60


def parse_iso8601(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def format_iso8601(dt: Optional[datetime] = None) -> str:
    dt = (dt or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def subscription_defaults(
    tier: str = DEFAULT_SUBSCRIPTION_TIER,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Generate default subscription fields using new Stripe payment system schema."""
    now = now or datetime.now(timezone.utc)
    return {
        "role": tier,  # Use 'role' instead of 'tier' for Stripe compatibility
        "status": "active",
        "priceId": "free" if tier == "tier1" else None,
    }


def quotas_defaults(
    tier: str = DEFAULT_SUBSCRIPTION_TIER,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Generate default quotas using new Stripe payment system schema."""
    now = now or datetime.now(timezone.utc)
    now_timestamp = int(now.timestamp())
    limit = TIER_LIMITS.get(tier, 1)
    
    return {
        "flatlaysRemaining": limit,
        "lastRefillAt": now_timestamp,
    }


