"""Normalize ended subscriptions without granting credits on a read."""

from datetime import datetime, timezone

from firebase_admin import firestore

from .subscription_utils import DEFAULT_SUBSCRIPTION_TIER, TIER_LIMITS


def read_subscription_user(db, user_id, *, now=None, reset_unbacked_premium=False):
    """Return a fresh user snapshot after any one-time, transactional downgrade.

    Reservation and settlement also transact on this user document. A conflicting
    debit therefore retries this read instead of being overwritten by a stale
    balance. Only those quota operations may refill or advance the quota period.
    """
    now = int(datetime.now(timezone.utc).timestamp()) if now is None else now
    user_ref = db.collection('users').document(user_id)

    @firestore.transactional
    def read_and_repair(transaction):
        snapshot = user_ref.get(transaction=transaction)
        if not snapshot.exists:
            return None
        user = snapshot.to_dict() or {}
        subscription = user.get('subscription') or {}
        role = subscription.get('role') or subscription.get('tier', DEFAULT_SUBSCRIPTION_TIER)
        status = subscription.get('status', 'active')
        try:
            period_end = int(subscription.get('currentPeriodEnd') or 0)
        except (TypeError, ValueError, OverflowError):
            period_end = 0
        unbacked = (reset_unbacked_premium and role != DEFAULT_SUBSCRIPTION_TIER
                    and not (user.get('billing') or {}).get('stripeCustomerId'))
        expired = (period_end > 0 and now >= period_end
                   and (subscription.get('cancelAtPeriodEnd') or status == 'canceled'))
        if not (unbacked or expired):
            return user

        # Never increase a balance or move the period backing a live reservation.
        quotas = user.get('quotas') or {}
        try:
            remaining = max(0, int(quotas.get('flatlaysRemaining', 0)))
        except (TypeError, ValueError, OverflowError):
            remaining = 0
        remaining = min(remaining, TIER_LIMITS.get(DEFAULT_SUBSCRIPTION_TIER, 1))
        updates = {
            'subscription.role': DEFAULT_SUBSCRIPTION_TIER,
            'subscription.status': 'active' if unbacked else 'canceled',
            'subscription.priceId': 'free',
            'subscription.currentPeriodEnd': 0,
            'subscription.cancelAtPeriodEnd': False,
            'subscription.tier': firestore.DELETE_FIELD,
            'subscription.openai_flatlays_used': firestore.DELETE_FIELD,
            'subscription.flatlay_week_start': firestore.DELETE_FIELD,
            'quotas.flatlaysRemaining': remaining,
        }
        if unbacked:
            updates['subscription.stripeSubscriptionId'] = firestore.DELETE_FIELD
        transaction.update(user_ref, updates)

        # Mirror only this transaction's committed patch, not the stale read that
        # preceded a separate write. Never expose Firestore delete sentinels.
        result = {**user, 'subscription': dict(subscription), 'quotas': dict(quotas)}
        for path, value in updates.items():
            section, field = path.split('.', 1)
            if value is firestore.DELETE_FIELD:
                result[section].pop(field, None)
            else:
                result[section][field] = value
        return result

    return read_and_repair(db.transaction())
