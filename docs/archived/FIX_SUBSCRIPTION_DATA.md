# Fix Subscription Data

## Issue Found

Your Firestore subscription data shows:
- ✅ `role: "tier2"` (correct - Pro tier)
- ✅ `status: "active"` (correct)
- ✅ `stripeSubscriptionId: "sub_1SWIwpQ00ZnKRYewaoCUVePE"` (exists)
- ❌ `currentPeriodEnd: 0` (should be a timestamp)
- ❌ `priceId: "price_1SWIV7Q00ZnKRYewvOmTXGU1"` (Premium price but role is tier2 - mismatch)
- ⚠️ Legacy fields still present (`tier`, `openai_flatlays_used`, `flatlay_week_start`)

## Quick Fix

### Option 1: Fix via Script (Recommended)

1. **Set environment variables** (if not already set):
   ```bash
   export STRIPE_SECRET_KEY="sk_test_..."
   export STRIPE_PRICE_TIER2="price_1SWIWxQ00ZnKRYewuivsPque"
   export STRIPE_PRICE_TIER3="price_1SWIV7Q00ZnKRYewvOmTXGU1"
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```

2. **Dry run** (see what would be fixed):
   ```bash
   cd backend/scripts
   python3 fix_subscription_data.py --user-id dANqjiI0CKgaitxzYtw1bhtvQrG3
   ```

3. **Actually fix** (after reviewing dry run):
   ```bash
   python3 fix_subscription_data.py --user-id dANqjiI0CKgaitxzYtw1bhtvQrG3 --execute
   ```

### Option 2: Manual Fix in Firestore

1. **Go to Firestore Console**
2. **Find user document**: `users/dANqjiI0CKgaitxzYtw1bhtvQrG3`
3. **Get subscription from Stripe**:
   - Go to Stripe Dashboard → Subscriptions
   - Find subscription `sub_1SWIwpQ00ZnKRYewaoCUVePE`
   - Note the `current_period_end` timestamp
   - Note the `price.id` to determine correct role

4. **Update Firestore**:
   - Set `subscription.currentPeriodEnd` to the timestamp from Stripe
   - Set `subscription.role` to match the price (tier2 for Pro, tier3 for Premium)
   - Set `subscription.priceId` to match the Stripe price ID
   - Optionally delete legacy fields: `tier`, `openai_flatlays_used`, `flatlay_week_start`

### Option 3: Trigger Webhook Manually

1. **Go to Stripe Dashboard** → Developers → Webhooks
2. **Click on your webhook endpoint**
3. **Click "Send test webhook"**
4. **Select**: `customer.subscription.updated`
5. **Enter subscription ID**: `sub_1SWIwpQ00ZnKRYewaoCUVePE`
6. **Send** - This will trigger the webhook handler to update the data

## What the Script Does

1. ✅ Fetches subscription from Stripe API
2. ✅ Determines correct role from Stripe price ID
3. ✅ Gets `current_period_end` from Stripe
4. ✅ Updates Firestore with correct data
5. ✅ Removes legacy fields (optional)
6. ✅ Fixes role/priceId mismatches

## Expected Result After Fix

Your subscription should have:
- `subscription.role`: `tier2` (or `tier3` if Premium)
- `subscription.priceId`: Correct price ID matching the role
- `subscription.currentPeriodEnd`: Unix timestamp (e.g., `1734567890`)
- `subscription.status`: `active`
- `subscription.cancelAtPeriodEnd`: `false` (or `true` if canceled)
- Legacy fields removed (optional)

## Verify Fix

After running the fix, check:
1. **Firestore**: User document should have correct `currentPeriodEnd`
2. **App**: Subscription page should show correct tier and period end date
3. **Period End Check**: Should work correctly when period expires

