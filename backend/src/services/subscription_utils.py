"""Pure weekly-credit policy; mirrored verbatim into the isolated worker root.

Only call mutation helpers with a user snapshot read inside a Firestore
transaction. Payment notifications change entitlement, never independently
refill credits. Unknown legacy balances require review instead of reconstruction.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any

DEFAULT_SUBSCRIPTION_TIER = "tier1"
TIER_LIMITS: Dict[str, int] = {"tier1": 1, "tier2": 7, "tier3": 30}
WEEKLY_ALLOWANCE_SECONDS = 7 * 24 * 60 * 60


class QuotaNeedsReview(ValueError):
    """Existing quota data cannot safely prove a balance or weekly period."""


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
    except (ValueError, TypeError, AttributeError):
        return None


def format_iso8601(dt: Optional[datetime] = None) -> str:
    dt = (dt or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def subscription_defaults(tier: str = DEFAULT_SUBSCRIPTION_TIER,
                          now: Optional[datetime] = None) -> Dict[str, Any]:
    return {"role": tier, "status": "active", "priceId": "free" if tier == "tier1" else None}


def quotas_defaults(tier: str = DEFAULT_SUBSCRIPTION_TIER,
                    now: Optional[datetime] = None) -> Dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    limit = TIER_LIMITS[tier]
    return {"flatlaysRemaining": limit, "lastRefillAt": int(now.timestamp()),
            "highestAllowanceGranted": limit, "highestAllowanceInferred": False}


def _integer(value, field, *, minimum=0, maximum=None):
    # Reject bools, fractional values, NaN, timestamps in milliseconds, and
    # malformed historical fields. None must never mean a new free allowance.
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise QuotaNeedsReview(f"Invalid {field}")
    try:
        result = int(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise QuotaNeedsReview(f"Invalid {field}") from error
    if result < minimum or (maximum is not None and result > maximum):
        raise QuotaNeedsReview(f"Invalid {field}")
    return result


def subscription_role(user_data, now=None):
    subscription = user_data.get("subscription") or {}
    if not isinstance(subscription, dict):
        raise QuotaNeedsReview("Invalid subscription")
    billing = user_data.get("billing") or {}
    if not isinstance(billing, dict):
        raise QuotaNeedsReview("Invalid billing")
    role = subscription.get("role") or subscription.get("tier") or DEFAULT_SUBSCRIPTION_TIER
    if role not in TIER_LIMITS:
        raise QuotaNeedsReview("Unknown subscription role")
    # An expired, billing-backed cancellation cannot refill at its old paid tier,
    # even when the worker runs before a subscription read repairs its projection.
    if now is not None and billing.get("stripeCustomerId"):
        try:
            end = int(subscription.get("currentPeriodEnd") or 0)
        except (ValueError, TypeError, OverflowError):
            end = 0
        if end > 0 and now >= end and (subscription.get("cancelAtPeriodEnd")
                                       or subscription.get("status") == "canceled"):
            return DEFAULT_SUBSCRIPTION_TIER
    return role


def _validated_quota(user_data, now):
    original = user_data.get("quotas")
    if not isinstance(original, dict):
        raise QuotaNeedsReview("Missing quotas")
    quota = dict(original)
    remaining = _integer(quota.get("flatlaysRemaining"), "flatlaysRemaining", maximum=30)
    start = _integer(quota.get("lastRefillAt"), "lastRefillAt", minimum=1, maximum=now)
    role = subscription_role(user_data)
    if "highestAllowanceGranted" in quota:
        highest = _integer(quota["highestAllowanceGranted"], "highestAllowanceGranted", minimum=1, maximum=30)
        if highest < remaining:
            raise QuotaNeedsReview("Balance exceeds recorded allowance")
    else:
        # Old documents did not record upgrade history. Preserve their exact
        # balance/anchor, infer only from current evidence, and flag that limit in
        # the private account audit. History before this cutoff is not provable.
        highest = max(TIER_LIMITS[role], remaining)
        quota["highestAllowanceInferred"] = True
    quota.update(flatlaysRemaining=remaining, lastRefillAt=start, highestAllowanceGranted=highest)
    return quota


def current_quota(user_data, now):
    """Get an allowance for an actual debit/refund, advancing at most one week.

    Existing valid anchors refill lazily at first use after seven days. Unused
    weeks never accumulate; a missing/invalid anchor never produces a grant.
    """
    quota = _validated_quota(user_data, now)
    if now - quota["lastRefillAt"] >= WEEKLY_ALLOWANCE_SECONDS:
        allowance = TIER_LIMITS[subscription_role(user_data, now)]
        quota.update(flatlaysRemaining=allowance, lastRefillAt=now,
                     highestAllowanceGranted=allowance, highestAllowanceInferred=False)
    return quota


def apply_subscription_entitlement(user_data, tier, now, *, advance_period=False):
    """Return full quota values to commit atomically with a verified entitlement.

    Billing uses the default: expired periods stay unchanged until actual usage.
    Within a live period, upgrade only above the highest previously granted tier;
    downgrade never destroys remaining credits or moves the period anchor.
    """
    if tier not in TIER_LIMITS:
        raise ValueError("Unknown entitlement tier")
    quota = _validated_quota(user_data, now)
    expired = now - quota["lastRefillAt"] >= WEEKLY_ALLOWANCE_SECONDS
    if expired:
        if not advance_period:
            return dict(user_data["quotas"])
        quota.update(flatlaysRemaining=TIER_LIMITS[tier], lastRefillAt=now,
                     highestAllowanceGranted=TIER_LIMITS[tier], highestAllowanceInferred=False)
        return quota
    allowance = TIER_LIMITS[tier]
    additional = max(0, allowance - quota["highestAllowanceGranted"])
    quota["flatlaysRemaining"] += additional
    quota["highestAllowanceGranted"] = max(quota["highestAllowanceGranted"], allowance)
    return quota
