# Subscription and credit authority release

Account identity comes from verified Firebase authentication. Profile edits pass an explicit server allowlist; the client cannot create/delete authority documents, write subscription/quotas/billing, move ownership, or write generated flatlay projections. Server Admin SDK paths enforce the same boundary independently of Firestore rules.

## Credit policy

Weekly allowances remain 1/7/30. A seven-day window starts at initialization or the first debit/refund after an expired window. Unused weeks do not accumulate. Upgrades add only the difference above the highest allowance granted in that window; downgrades retain its remaining credits and reset date. Refunds settle once and never add old-period credit to a new period.

`quotas.highestAllowanceGranted` records the grant ceiling, and `highestAllowanceInferred` identifies historical records without complete grant history. Valid legacy balances and anchors remain unchanged. Missing/invalid financial state is review-required, never an instruction to mint a balance. New account bootstrap is transactional and create-once.

Signed Stripe events are reconciled against current Stripe state under an expiring per-account lease. Entitlement and processed event records commit atomically with a fence against expired lease owners. Event retries and invoices cannot independently refill weekly credits. Unknown prices, ambiguous subscriptions, or unverified customer mappings require review. The private Stripe customer mapping or exact Stripe customer UID metadata must corroborate historical associations before portal access or reconciliation.

## Compatibility

Existing profile and outfit routes remain available. Profile saves return the full stored profile and authoritative identity; failures are visible and retriable. Manual/fallback saves resolve owned wardrobe items and are idempotent when given the same outfit ID. Outfit item changes invalidate obsolete imagery while retaining any ongoing request until settlement. Private credit history survives outfit deletion; deletion is refused while a request is pending.

Ten-item capsule onboarding remains intact. Quiz failures preserve answers and do not claim completion. `quota_review_required` is an additive subscription response field; consumers display unavailable credits without an exhausted-balance upgrade prompt.

## Validation and release gates

- Backend unittest suite covers authenticated API boundaries, profile writes, owned garment resolution, credit concurrency, weekly boundaries, payment duplicates/reordering, signatures, leases and legacy data.
- Frontend Jest covers profile forwarding, quiz failure/retry, outfits and quota-review displays. Firestore emulator tests run against a demo project and exercise denied and permitted writes. CI uses Node 22 and Java 21.
- One canonical rules source is `frontend/firestore.rules`. Deploy explicitly with the frontend Firebase config and `--only firestore:rules`; do not deploy indexes or Storage as part of this release.
- Deploy compatible API/worker/frontend revisions before tightening rules. Confirm exact active rules hash afterward. On failure, keep financial writes closed and repair forward or use compatible application rollback.
- Before production promotion, resolve reviewed legacy account initialization, verify Stripe test-mode checkout/plan changes, and enable the existing configured plan prices in the billing portal without silently changing proration policy.
- Observe denied legitimate writes, profile/quiz failures, payment reconciliation failures and flatlay credit outcomes through the following day.

The private operator report and customer corrections are deliberately excluded from this public repository. No historical account balance changes are part of an application deployment itself.
