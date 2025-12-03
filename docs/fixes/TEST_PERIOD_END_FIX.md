# Test the Period End Fix

## 🎯 What We Fixed

The webhook handler now:
1. Tries to get `current_period_end` from webhook payload
2. Falls back to subscription items if not found
3. **Fetches from Stripe API if still 0** (NEW!)

## 🧪 How to Test

### Option 1: Resend Webhook (Easiest - Recommended)

1. **Go to Stripe Dashboard** → **Developers** → **Webhooks**
2. **Click your webhook endpoint**
3. **Find** the `customer.subscription.updated` event from 5:18:15 PM
4. **Click "Resend"** button
5. **Watch Railway logs** - should see:
   ```
   Processing Stripe webhook event: customer.subscription.updated
   Fetched period_end from Stripe API: 1766423888
   Processing subscription update: subscription_id=sub_1SWKRoQ00ZnKRYew2lEbGJwl, price_id=price_1SWIWxQ00ZnKRYewuivsPque, role=tier3, period_end=1766423888, status=active
   Updated subscription sub_1SWKRoQ00ZnKRYew2lEbGJwl for user dANqjiI0CKgaitxzYtw1bhtvQrG3 - cancel_at_period_end: False, period_end: 1766423888
   ```
6. **Check Firestore** - `subscription.currentPeriodEnd` should now be `1766423888` (not 0)

### Option 2: Send Test Webhook

1. **Go to Stripe Dashboard** → **Developers** → **Webhooks**
2. **Click your webhook endpoint**
3. **Click "Send test webhook"** button
4. **Select event**: `customer.subscription.updated`
5. **Enter subscription ID**: `sub_1SWKRoQ00ZnKRYew2lEbGJwl`
6. **Click "Send test webhook"**
7. **Watch Railway logs** for the same messages as above
8. **Check Firestore** - should update `currentPeriodEnd`

### Option 3: Use Fix Script

```bash
cd backend/scripts
python3 fix_subscription_data.py --user-id dANqjiI0CKgaitxzYtw1bhtvQrG3 --execute
```

This will:
- Fetch subscription from Stripe API
- Get `current_period_end` directly
- Update Firestore with correct values

### Option 4: Test via API Endpoint

1. **Call the subscription endpoint**:
   ```bash
   curl -X GET "https://closetgptrenew-production.up.railway.app/api/payments/subscription/current" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **The endpoint checks period end** and will fetch from Stripe if needed
3. **Check Firestore** - should update if period_end was 0

## ✅ Expected Results

### After Testing:

**Firestore should have:**
- ✅ `subscription.currentPeriodEnd`: `1766423888` (or correct timestamp, not 0)
- ✅ `subscription.role`: `tier3` (Premium)
- ✅ `subscription.priceId`: `price_1SWIWxQ00ZnKRYewuivsPque`
- ✅ `subscription.status`: `active`

**Railway logs should show:**
- ✅ `Fetched period_end from Stripe API: 1766423888` (if webhook had 0)
- ✅ `Processing subscription update: ... period_end=1766423888`
- ✅ `Updated subscription ... period_end: 1766423888`

**Your app should show:**
- ✅ Subscription page shows correct tier (Premium)
- ✅ Shows period end date (not "N/A" or missing)
- ✅ Flat lay quota shows 30 (for Premium)

## 🔍 Verify the Fix Worked

### Step 1: Check Railway Logs

Look for these log messages:
```
Fetched period_end from Stripe API: 1766423888
Processing subscription update: ... period_end=1766423888
Updated subscription ... period_end: 1766423888
```

### Step 2: Check Firestore

1. **Go to Firestore Console**
2. **Open user document**: `users/dANqjiI0CKgaitxzYtw1bhtvQrG3`
3. **Check**:
   - `subscription.currentPeriodEnd`: Should be `1766423888` (not 0)
   - `subscription.role`: Should be `tier3`
   - `subscription.priceId`: Should match Stripe

### Step 3: Check Your App

1. **Go to subscription page** (`/subscription`)
2. **Should show**:
   - "Current Plan: Premium"
   - "30 flat lays remaining"
   - Period end date (e.g., "Active until Dec 22, 2025")

## 🐛 If It Still Shows 0

### Check Railway Logs for Errors:
- Look for "Failed to fetch subscription from Stripe"
- Check if `STRIPE_SECRET_KEY` is set correctly
- Verify subscription ID exists in Stripe

### Manual Fix:
If API fetch fails, manually update Firestore:
- `subscription.currentPeriodEnd`: `1766423888`

## 📝 Quick Test Checklist

- [ ] Resend webhook from Stripe Dashboard
- [ ] Check Railway logs for "Fetched period_end from Stripe API"
- [ ] Check Firestore - `currentPeriodEnd` should be set (not 0)
- [ ] Check subscription page - should show period end date
- [ ] Verify role and priceId are correct

---

**Recommended**: Start with **Option 1 (Resend Webhook)** - it's the easiest and will test the fix immediately!

