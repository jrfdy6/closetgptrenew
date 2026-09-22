"""Validated Stripe confirmation links for changes to an existing subscription."""
from .billing_reconciliation import BillingReconciliationError, _id, _known_price_tiers


class BillingPortalConfigurationError(Exception):
    """The deployed portal cannot safely offer the requested plan change."""


def create_subscription_update_confirmation(stripe, customer_id, subscription_id,
                                            requested_price, price_ids, return_url):
    known = _known_price_tiers(price_ids)
    if requested_price not in known:
        raise BillingReconciliationError('Requested price is not configured')
    subscription = stripe.Subscription.retrieve(subscription_id)
    if (_id(subscription.get('id')) != subscription_id
            or _id(subscription.get('customer')) != customer_id):
        raise BillingReconciliationError('Subscription customer does not match account')
    if subscription.get('status') not in ('active', 'trialing'):
        raise BillingReconciliationError('Resolve the current subscription payment before changing plans')
    if subscription.get('schedule') or subscription.get('pending_update'):
        raise BillingReconciliationError('Subscription already has a pending change')
    items = (subscription.get('items') or {}).get('data') or []
    if len(items) != 1 or items[0].get('quantity', 1) != 1:
        raise BillingReconciliationError('Subscription items require review')
    item_id = _id(items[0].get('id'))
    current_price = _id(items[0].get('price'))
    if not item_id or current_price not in known:
        raise BillingReconciliationError('Current subscription item or price requires review')

    configurations = stripe.billing_portal.Configuration.list(active=True, is_default=True, limit=2)
    configs = configurations.get('data') or []
    if len(configs) != 1 or configurations.get('has_more'):
        raise BillingPortalConfigurationError('No unique active default portal configuration')
    config = configs[0]
    updates = (config.get('features') or {}).get('subscription_update') or {}
    if not config.get('active') or not updates.get('enabled') or 'price' not in (updates.get('default_allowed_updates') or []):
        raise BillingPortalConfigurationError('Subscription price updates are disabled')
    allowed_prices = {price for product in updates.get('products', []) for price in product.get('prices', [])}
    if current_price not in allowed_prices or requested_price not in allowed_prices:
        raise BillingPortalConfigurationError('Portal does not offer the current and requested prices')
    # Keep the deployed billing policy: invoice prorations immediately, without
    # silently introducing deferred plan changes through a portal configuration.
    if (updates.get('proration_behavior') != 'always_invoice'
            or (updates.get('schedule_at_period_end') or {}).get('conditions')):
        raise BillingPortalConfigurationError('Portal update billing policy requires review')
    config_id = _id(config.get('id'))
    if not config_id:
        raise BillingPortalConfigurationError('Portal configuration identity missing')
    return stripe.billing_portal.Session.create(
        customer=customer_id,
        configuration=config_id,
        return_url=return_url,
        flow_data={
            'type': 'subscription_update_confirm',
            'subscription_update_confirm': {
                'subscription': subscription_id,
                'items': [{'id': item_id, 'price': requested_price, 'quantity': 1}],
            },
            'after_completion': {'type': 'redirect', 'redirect': {'return_url': return_url}},
        },
    )
