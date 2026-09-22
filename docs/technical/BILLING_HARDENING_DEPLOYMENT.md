# Billing hardening deployment prerequisites

The authenticated checkout route creates a Checkout Session only when the verified
customer has no current subscription. For an existing subscriber it creates a
Stripe `subscription_update_confirm` portal flow for the requested configured
price, using the existing subscription and item IDs and quantity 1. Confirmation,
proration presentation and payment authentication remain in Stripe. The API
response remains `{checkout_url, session_id}`.

## Stripe configuration required before releasing plan changes

Verify the live and test environments separately. Do not infer live configuration
from local `.env` files or alter customer balances during these checks.

1. Verify the backend has its matching `STRIPE_SECRET_KEY`,
   `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_TIER2`, `STRIPE_PRICE_TIER3`,
   `STRIPE_PRICE_TIER2_YEARLY`, and `STRIPE_PRICE_TIER3_YEARLY`. Prices must reference
   the existing monthly/yearly Pro and Premium products in the same Stripe mode.
2. Retrieve the active default Stripe billing-portal configuration. Enable
   `features.subscription_update.enabled` and include `price` in
   `features.subscription_update.default_allowed_updates`.
3. Set `features.subscription_update.products` to the existing products and their
   existing four configured price IDs, grouped by the actual product each price
   belongs to. Do not create replacement products or prices. Quantity stays 1;
   quantity editing is not required.
4. Preserve the established billing policy:
   `features.subscription_update.proration_behavior = always_invoice` and
   `features.subscription_update.schedule_at_period_end.conditions = []`.
   Preserve all other portal features, cancellation policy, branding and URLs.
5. Read the configuration back and verify the enabled flags, all four prices,
   proration behavior and schedule conditions. The application passes that
   configuration ID explicitly when creating a confirmation link.

If price switching is disabled, a selected price is not offered, or the portal
billing policy differs, the endpoint returns a clear HTTP 503 instead of sending
an existing subscriber to an unusable portal or creating a second subscription.
Unpaid, incomplete, scheduled, ambiguous or otherwise unsupported subscriptions
require account review before starting another purchase.

## Existing account identities and trials

Checkout and portal requests resolve the known customer aliases
`billing.stripeCustomerId`, `subscription.stripeCustomerId`, and top-level
`stripeCustomerId`. The corresponding three `stripeSubscriptionId` aliases can
also identify a customer through a fresh Stripe subscription lookup. Conflicting
customer evidence requires review; it never triggers creation of a replacement
customer.

A resolved customer is bound to the canonical billing field only after its
Stripe metadata corroborates the authenticated UID or a private customer mapping
already proves ownership. Subscription history is paginated before deciding
whether a new monthly subscription is eligible for its existing trial policy.
This prevents a legacy field layout from resetting customer identity or trial
history. Normalizing a verified customer mapping does not change quota balances.

## Verification and release

- Run `backend/tests/test_billing_reconciliation.py` with the repository's Python
  3.11 environment. It covers exact confirmation-flow fields, disabled portal
  configuration, historical identity/trial handling, and replay-safe credit logic.
- In Stripe test mode, confirm an existing Pro subscription can review and accept
  Premium and interval changes. Verify the existing subscription is updated,
  its quantity remains 1, and no second subscription is created.
- Confirm prorations are shown before acceptance. Verify the signed webhook
  applies only the weekly allowance increase, preserving spent credits and the
  existing weekly anchor; a repeated webhook must not grant another increase.
- Keep production changes staged until the live configuration passes the checks
  above. Never use a live customer purchase or plan change as a smoke test.

References: [Stripe portal deep links](https://docs.stripe.com/customer-management/portal-deep-links),
[portal session API](https://docs.stripe.com/api/customer_portal/sessions/create),
[portal configurations](https://docs.stripe.com/api/customer_portal/configurations/list).
