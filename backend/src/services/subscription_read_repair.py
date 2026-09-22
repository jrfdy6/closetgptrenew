"""Normalize ended subscriptions without granting credits on a read."""

from datetime import datetime, timezone

from firebase_admin import firestore

from .subscription_utils import DEFAULT_SUBSCRIPTION_TIER, apply_subscription_entitlement, QuotaNeedsReview


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
        status = subscription.get('status', 'active')
        try:
            period_end = int(subscription.get('currentPeriodEnd') or 0)
        except (TypeError, ValueError, OverflowError):
            period_end = 0
        # Keep the old keyword for callers during rollout. A read must not
        # revoke historically uncertain access merely because billing is absent.
        expired = (bool((user.get('billing') or {}).get('stripeCustomerId'))
                   and period_end > 0 and now >= period_end
                   and (subscription.get('cancelAtPeriodEnd') or status == 'canceled'))
        if not expired:
            return user

        # Downgrades preserve every remaining credit and its anchor until the
        # next actual weekly refill. Payment reconciliation controls grants.
        updates = {
            'subscription.role': DEFAULT_SUBSCRIPTION_TIER,
            'subscription.status': 'canceled',
            'subscription.priceId': 'free',
            'subscription.currentPeriodEnd': 0,
            'subscription.cancelAtPeriodEnd': False,
            'subscription.tier': firestore.DELETE_FIELD,
            'subscription.openai_flatlays_used': firestore.DELETE_FIELD,
            'subscription.flatlay_week_start': firestore.DELETE_FIELD,
        }
        try:
            # Remember the paid high-water before removing the old role. This
            # prevents read repair itself from reopening an upgrade grant.
            quotas = apply_subscription_entitlement(user, DEFAULT_SUBSCRIPTION_TIER, now)
        except QuotaNeedsReview:
            quotas = None
        if quotas is not None and quotas != user.get('quotas'):
            updates['quotas'] = quotas
        transaction.update(user_ref, updates)

        # Mirror only this transaction's committed patch, not the stale read that
        # preceded a separate write. Never expose Firestore delete sentinels.
        result = {**user, 'subscription': dict(subscription)}
        for path, value in updates.items():
            if path == 'quotas':
                result['quotas'] = value
                continue
            section, field = path.split('.', 1)
            if value is firestore.DELETE_FIELD:
                result[section].pop(field, None)
            else:
                result[section][field] = value
        return result

    return read_and_repair(db.transaction())
