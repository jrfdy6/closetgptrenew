"""Reconcile signed Stripe notifications without replaying their stale snapshots.

A fenced, expiring account lease spans the external Stripe reads. Only its owner
can commit entitlement and event completion together. Stripe/network calls never
run inside a Firestore transaction, whose callback can be retried.
"""
from datetime import datetime, timezone
from uuid import uuid4

from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from .subscription_utils import apply_subscription_entitlement, QuotaNeedsReview

EVENTS_COLLECTION = 'stripe_webhook_events'
LOCKS_COLLECTION = 'stripe_reconciliation_locks'
CUSTOMERS_COLLECTION = 'stripe_customers'
LEASE_SECONDS = 120
SUPPORTED_EVENTS = {
    'checkout.session.completed',
    'customer.subscription.created', 'customer.subscription.updated',
    'customer.subscription.deleted',
    'invoice.payment_succeeded', 'invoice.payment_failed',
}


class BillingReconciliationError(Exception):
    """Leave the event incomplete so Stripe will retry after a repair."""


def _now():
    return int(datetime.now(timezone.utc).timestamp())


def _id(value):
    value = value.get('id') if isinstance(value, dict) else value
    return value if isinstance(value, str) and value and '/' not in value else None


CUSTOMER_PATHS = ('billing.stripeCustomerId', 'subscription.stripeCustomerId', 'stripeCustomerId')
SUBSCRIPTION_PATHS = ('subscription.stripeSubscriptionId', 'billing.stripeSubscriptionId', 'stripeSubscriptionId')


def _billing_aliases(user, paths):
    values = set()
    for path in paths:
        value = user
        for part in path.split('.'):
            if not isinstance(value, dict):
                raise BillingReconciliationError('Malformed account billing identity')
            value = value.get(part)
            if value is None:
                break
        if value is not None and value != '':
            identifier = _id(value)
            if not identifier:
                raise BillingReconciliationError('Malformed account billing identity')
            values.add(identifier)
    return values


def known_customer_id(user):
    """Read historical aliases without trusting or changing their ownership."""
    customer_ids = _billing_aliases(user, CUSTOMER_PATHS)
    if len(customer_ids) > 1:
        raise BillingReconciliationError('Conflicting historical Stripe customers require review')
    return next(iter(customer_ids), None)


def resolve_checkout_customer_id(stripe, user):
    """Do not create a new customer or trial when older identity evidence exists.

    This only resolves candidate IDs. The Stripe customer still needs metadata or
    a private mapping corroborating the authenticated UID before it is bound.
    """
    customer_id = known_customer_id(user)
    candidates = {customer_id} if customer_id else set()
    for subscription_id in _billing_aliases(user, SUBSCRIPTION_PATHS):
        subscription = stripe.Subscription.retrieve(subscription_id)
        if _id(subscription.get('id')) != subscription_id:
            raise BillingReconciliationError('Historical subscription identity mismatch')
        resolved = _id(subscription.get('customer'))
        if not resolved:
            raise BillingReconciliationError('Historical subscription customer unavailable')
        candidates.add(resolved)
    if len(candidates) > 1:
        raise BillingReconciliationError('Conflicting historical Stripe customers require review')
    return next(iter(candidates), None)


def _subscription_id(obj, event_type):
    if event_type.startswith('customer.subscription.'):
        return _id(obj.get('id'))
    subscription = obj.get('subscription')
    if not subscription:
        subscription = ((obj.get('parent') or {}).get('subscription_details') or {}).get('subscription')
    return _id(subscription)


def _known_price_tiers(price_ids):
    result = {}
    for key, value in price_ids.items():
        if key not in ('tier2', 'tier3', 'tier2_yearly', 'tier3_yearly') or not value:
            continue
        tier = key.split('_')[0]
        if value in result and result[value] != tier:
            raise BillingReconciliationError('Ambiguous configured Stripe price')
        result[value] = tier
    return result


def _subscriptions_for_customer(stripe, customer_id):
    # Read all pages: an older invoice must not hide a current replacement.
    page = stripe.Subscription.list(customer=customer_id, status='all', limit=100)
    subscriptions = []
    while True:
        rows = page.get('data', [])
        subscriptions.extend(rows)
        if not page.get('has_more'):
            return subscriptions
        if not rows or len(subscriptions) >= 1000:
            raise BillingReconciliationError('Subscription history needs review')
        page = stripe.Subscription.list(customer=customer_id, status='all', limit=100,
                                        starting_after=rows[-1]['id'])


def _latest_entitlement(stripe, customer_id, trigger_subscription, price_ids, now):
    """Select current account state, never a tier or user ID from event metadata."""
    trigger = stripe.Subscription.retrieve(trigger_subscription)
    if _id(trigger.get('customer')) != customer_id:
        raise BillingReconciliationError('Subscription customer does not match event')
    subscriptions = _subscriptions_for_customer(stripe, customer_id)
    if not any(_id(sub.get('id')) == trigger_subscription for sub in subscriptions):
        # A list/retrieve inconsistency may indicate propagation lag. Retry rather
        # than making a downgrade decision from an incomplete snapshot.
        raise BillingReconciliationError('Subscription missing from current customer history')
    for sub in subscriptions:
        if _id(sub.get('customer')) != customer_id:
            raise BillingReconciliationError('Subscription list customer mismatch')

    terminal = {'canceled', 'incomplete_expired'}
    current = [sub for sub in subscriptions if sub.get('status') not in terminal]
    if len(current) > 1:
        raise BillingReconciliationError('Multiple current subscriptions require review')
    if current:
        # Retrieve after listing while holding the account lease. A late event for
        # an old canceled subscription therefore reconciles the active successor.
        latest = stripe.Subscription.retrieve(_id(current[0].get('id')))
    else:
        latest = max(subscriptions, key=lambda sub: (int(sub.get('created') or 0), sub.get('id', '')))
        latest = stripe.Subscription.retrieve(_id(latest.get('id')))
    if _id(latest.get('customer')) != customer_id:
        raise BillingReconciliationError('Current subscription customer mismatch')

    items = (latest.get('items') or {}).get('data') or []
    prices = _known_price_tiers(price_ids)
    if len(items) != 1 or items[0].get('quantity', 1) != 1:
        raise BillingReconciliationError('Unexpected subscription items require review')
    price = _id(items[0].get('price'))
    if price not in prices:
        raise BillingReconciliationError('Unknown subscription price requires review')
    stripe_status = latest.get('status')
    if stripe_status not in {'active', 'trialing', 'past_due', 'unpaid', 'paused',
                             'incomplete', 'incomplete_expired', 'canceled'}:
        raise BillingReconciliationError('Unknown subscription status')
    period_end = int(latest.get('current_period_end') or items[0].get('current_period_end') or 0)
    trial_end = int(latest.get('trial_end') or 0)
    cancel_at_end = bool(latest.get('cancel_at_period_end'))
    paid = stripe_status in {'active', 'trialing'}
    if paid and not period_end:
        raise BillingReconciliationError('Current subscription period missing')
    if cancel_at_end and period_end <= now:
        paid = False
    if stripe_status == 'trialing' and (not trial_end or trial_end <= now):
        paid = False
    return {
        'role': prices[price] if paid else 'tier1',
        'status': stripe_status,
        'priceId': price,
        'stripeSubscriptionId': _id(latest.get('id')),
        'currentPeriodEnd': period_end,
        'cancelAtPeriodEnd': cancel_at_end,
        'trialEnd': trial_end or None,
        'trial_used': bool(trial_end),
    }


def user_for_customer(db, customer_id):
    mapping = db.collection(CUSTOMERS_COLLECTION).document(customer_id).get()
    matches = {}
    for path in CUSTOMER_PATHS:
        rows = db.collection('users').where(filter=FieldFilter(path, '==', customer_id)).limit(2).stream()
        for row in rows:
            matches[row.id] = row.to_dict() or {}
    if len(matches) != 1:
        raise BillingReconciliationError('Stripe customer has no unique account mapping')
    user_id, user = next(iter(matches.items()))
    if known_customer_id(user) != customer_id:
        raise BillingReconciliationError('Stripe customer aliases disagree')
    if mapping.exists and (mapping.to_dict() or {}).get('user_id') != user_id:
        raise BillingReconciliationError('Stripe customer mapping disagrees with account')
    return user_id


def _assert_customer_identity(mapping, customer, user_id):
    declared_user = (customer.get('metadata') or {}).get('user_id')
    if mapping is not None:
        if mapping.get('user_id') != user_id or (declared_user and declared_user != user_id):
            raise BillingReconciliationError('Customer identity needs review')
    elif declared_user != user_id:
        # Before rules hardening the user could edit their billing customer ID.
        # That legacy value alone must never grant access to someone else's
        # portal or become a trusted private ownership mapping.
        raise BillingReconciliationError('Legacy customer ownership is unverified')


def verify_customer_identity(db, user_id, customer):
    customer_id = _id(customer.get('id'))
    if not customer_id or customer.get('deleted'):
        raise BillingReconciliationError('Customer record unavailable')
    mapping = db.collection(CUSTOMERS_COLLECTION).document(customer_id).get()
    _assert_customer_identity(mapping.to_dict() if mapping.exists else None, customer, user_id)


def _acquire(db, user_id, customer_id, event_id, token, now):
    user_ref = db.collection('users').document(user_id)
    event_ref = db.collection(EVENTS_COLLECTION).document(event_id)
    lock_ref = db.collection(LOCKS_COLLECTION).document(user_id)

    @firestore.transactional
    def acquire(transaction):
        event = event_ref.get(transaction=transaction)
        user = user_ref.get(transaction=transaction)
        lock = lock_ref.get(transaction=transaction)
        if event.exists and (event.to_dict() or {}).get('status') == 'completed':
            return False
        if not user.exists or known_customer_id(user.to_dict() or {}) != customer_id:
            raise BillingReconciliationError('Account customer changed during reconciliation')
        held = (lock.to_dict() or {}) if lock.exists else {}
        if held.get('token') and held.get('lease_until', 0) > now:
            raise BillingReconciliationError('Account reconciliation already in progress')
        transaction.set(lock_ref, {'token': token, 'lease_until': now + LEASE_SECONDS,
                                   'event_id': event_id, 'customer_id': customer_id})
        return True

    return acquire(db.transaction())


def _release(db, user_id, token):
    ref = db.collection(LOCKS_COLLECTION).document(user_id)

    @firestore.transactional
    def release(transaction):
        snapshot = ref.get(transaction=transaction)
        if snapshot.exists and (snapshot.to_dict() or {}).get('token') == token:
            transaction.update(ref, {'token': None, 'lease_until': 0})

    release(db.transaction())


def reconcile_stripe_event(db, stripe, event, price_ids, *, clock=_now):
    event_type = event.get('type')
    if event_type not in SUPPORTED_EVENTS:
        return {'status': 'ignored'}
    event_id = _id(event.get('id'))
    if not event_id:
        raise BillingReconciliationError('Signed event has no valid ID')
    event_ref = db.collection(EVENTS_COLLECTION).document(event_id)
    previous = event_ref.get()
    if previous.exists and (previous.to_dict() or {}).get('status') == 'completed':
        return {'status': 'success', 'duplicate': True}
    obj = (event.get('data') or {}).get('object') or {}
    if event_type == 'checkout.session.completed' and obj.get('mode') != 'subscription':
        return {'status': 'ignored'}
    subscription_id = _subscription_id(obj, event_type)
    if event_type.startswith('invoice.') and not subscription_id:
        return {'status': 'ignored'}
    customer_id = _id(obj.get('customer'))
    if not customer_id or not subscription_id:
        raise BillingReconciliationError('Subscription event identity is incomplete')
    user_id = user_for_customer(db, customer_id)
    token = str(uuid4())
    if not _acquire(db, user_id, customer_id, event_id, token, clock()):
        return {'status': 'success', 'duplicate': True}

    try:
        customer = stripe.Customer.retrieve(customer_id)
        if customer.get('deleted') or _id(customer.get('id')) != customer_id:
            raise BillingReconciliationError('Customer record unavailable')
        verify_customer_identity(db, user_id, customer)
        entitlement = _latest_entitlement(stripe, customer_id, subscription_id, price_ids, clock())
        user_ref = db.collection('users').document(user_id)
        lock_ref = db.collection(LOCKS_COLLECTION).document(user_id)

        @firestore.transactional
        def commit(transaction):
            user_snapshot = user_ref.get(transaction=transaction)
            lock_snapshot = lock_ref.get(transaction=transaction)
            previous = event_ref.get(transaction=transaction)
            mapping_ref = db.collection(CUSTOMERS_COLLECTION).document(customer_id)
            mapping = mapping_ref.get(transaction=transaction)
            if previous.exists and (previous.to_dict() or {}).get('status') == 'completed':
                return {'status': 'success', 'duplicate': True}
            now = clock()
            lock = (lock_snapshot.to_dict() or {}) if lock_snapshot.exists else {}
            if lock.get('token') != token or lock.get('lease_until', 0) <= now:
                raise BillingReconciliationError('Reconciliation lease expired; retry with fresh Stripe state')
            user = (user_snapshot.to_dict() or {}) if user_snapshot.exists else {}
            if known_customer_id(user) != customer_id:
                raise BillingReconciliationError('Account customer changed during reconciliation')
            _assert_customer_identity(mapping.to_dict() if mapping.exists else None, customer, user_id)
            old_subscription = user.get('subscription') or {}
            subscription = {**old_subscription, **entitlement,
                            'trial_used': bool(entitlement['trial_used'] or old_subscription.get('trial_used')),
                            'last_updated': now}
            # Remove obsolete financial aliases only when authoritative Stripe
            # reconciliation succeeds, without inferring any legacy balance.
            for field in ('tier', 'openai_flatlays_used', 'flatlay_week_start'):
                subscription.pop(field, None)
            updates = {'subscription': subscription, 'billing.stripeCustomerId': customer_id}
            quota_review = False
            try:
                updates['quotas'] = apply_subscription_entitlement(user, entitlement['role'], now,
                                                                  advance_period=False)
            except QuotaNeedsReview:
                quota_review = True
            transaction.update(user_ref, updates)
            transaction.set(mapping_ref, {'user_id': user_id, 'verified_at': now})
            transaction.set(event_ref, {'status': 'completed', 'event_type': event_type,
                                       'user_id': user_id, 'customer_id': customer_id,
                                       'subscription_id': entitlement['stripeSubscriptionId'],
                                       'processed_at': now, 'quota_needs_review': quota_review})
            transaction.update(lock_ref, {'token': None, 'lease_until': 0})
            return {'status': 'success'}

        return commit(db.transaction())
    finally:
        # A crash leaves only a bounded lease. A newer owner's fence cannot be
        # released by this attempt, and no completed event is written on failure.
        _release(db, user_id, token)


def bind_checkout_customer(db, user_id, customer):
    """Bind an externally verified Stripe customer without a last-writer-wins race."""
    customer_id = _id(customer.get('id'))
    if not customer_id or customer.get('deleted'):
        raise BillingReconciliationError('Customer record unavailable')
    user_ref = db.collection('users').document(user_id)
    mapping_ref = db.collection(CUSTOMERS_COLLECTION).document(customer_id)

    @firestore.transactional
    def bind(transaction):
        user_snapshot = user_ref.get(transaction=transaction)
        mapping = mapping_ref.get(transaction=transaction)
        if not user_snapshot.exists:
            raise BillingReconciliationError('Account not found')
        user = user_snapshot.to_dict() or {}
        existing = known_customer_id(user)
        if existing and existing != customer_id:
            raise BillingReconciliationError('Account already has another Stripe customer')
        _assert_customer_identity(mapping.to_dict() if mapping.exists else None, customer, user_id)
        transaction.update(user_ref, {'billing.stripeCustomerId': customer_id})
        transaction.set(mapping_ref, {'user_id': user_id, 'verified_at': _now()})

    bind(db.transaction())
