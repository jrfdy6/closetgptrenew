# Stripe Payment System Testing Checklist

## ✅ Setup Complete

- ✅ Server running on Railway
- ✅ Payment routes registered
- ✅ Environment variables loaded:
  - `STRIPE_SECRET_KEY` ✅
  - `STRIPE_PRICE_TIER2` ✅
  - `STRIPE_PRICE_TIER3` ✅
  - `STRIPE_WEBHOOK_SECRET` ✅
- ✅ Firebase connected

## 🧪 Testing Steps

### Step 1: Test Subscription Upgrade Flow

1. **Go to your app**: Navigate to `/subscription` page
2. **Click "Join Pro"** or "Join Premium"
3. **Should redirect to Stripe Checkout**
4. **Use test card**:
   ```
   Card: 4242 4242 4242 4242
   Expiry: 12/34
   CVC: 123
   ZIP: 12345
   ```
5. **Complete payment**
6. **Should redirect back** to your app
7. **Check subscription page**:
   - Should show "Current Plan: Pro" (or Premium)
   - Should show correct flat lay quota (7 for Pro, 30 for Premium)

**Expected Result**: ✅ Subscription upgraded, quota updated

---

### Step 2: Verify Webhook Processing

1. **Go to Stripe Dashboard** → **Developers** → **Webhooks**
2. **Click your webhook endpoint**
3. **Check "Recent deliveries"** tab
4. **Look for** `checkout.session.completed` event
5. **Status should be**: `200 OK` ✅

**If not 200 OK**:
- Check Railway logs for errors
- Verify `STRIPE_WEBHOOK_SECRET` is correct
- Check webhook URL is correct

**Expected Result**: ✅ Webhook delivered successfully

---

### Step 3: Verify Firestore Data

1. **Go to Firestore Console**
2. **Open user document**: `users/dANqjiI0CKgaitxzYtw1bhtvQrG3`
3. **Check subscription object**:
   - ✅ `subscription.role`: `tier2` or `tier3`
   - ✅ `subscription.status`: `active`
   - ✅ `subscription.currentPeriodEnd`: Should be a timestamp (not 0)
   - ✅ `subscription.priceId`: Should match Stripe price ID
   - ✅ `subscription.stripeSubscriptionId`: Should exist
   - ✅ `billing.stripeCustomerId`: Should exist
4. **Check quotas object**:
   - ✅ `quotas.flatlaysRemaining`: Should be 7 (Pro) or 30 (Premium)
   - ✅ `quotas.lastRefillAt`: Should be a timestamp

**Expected Result**: ✅ All fields populated correctly

---

### Step 4: Test Flat Lay Quota Countdown

1. **Generate an outfit** in your app
2. **Request a flat lay** for the outfit
3. **Check quota display**:
   - Should show "6 out of 7" (if Pro) or "29 out of 30" (if Premium)
4. **Request another flat lay**:
   - Should show "5 out of 7" (if Pro) or "28 out of 30" (if Premium)

**Expected Result**: ✅ Quota counts down correctly

---

### Step 5: Test Customer Portal

1. **Go to subscription page** (while on Pro/Premium)
2. **Click "Open Customer Portal"**
3. **Should open Stripe Customer Portal**
4. **Test features**:
   - Update payment method
   - View subscription details
   - Cancel subscription (schedules for period end)

**Expected Result**: ✅ Portal opens and works correctly

---

### Step 6: Test Subscription Cancellation

1. **Cancel subscription** via Customer Portal
2. **Check Firestore**:
   - `subscription.cancelAtPeriodEnd`: Should be `true`
   - `subscription.status`: Should still be `active` (until period ends)
   - `subscription.currentPeriodEnd`: Should show when subscription ends
3. **Check subscription page**:
   - Should show "Active until [date]"
4. **Test premium features**:
   - Should still work until period ends

**Expected Result**: ✅ Cancellation scheduled, premium features still work

---

### Step 7: Verify Period End Handling

**Note**: You can't wait 30 days, but you can test the logic:

1. **Manually set `currentPeriodEnd`** in Firestore to a past timestamp
2. **Call `/api/payments/subscription/current`** endpoint
3. **Should automatically downgrade** to free tier
4. **Check Firestore**:
   - `subscription.role`: Should be `tier1`
   - `subscription.status`: Should be `canceled`
   - `quotas.flatlaysRemaining`: Should be `1`

**Expected Result**: ✅ Auto-downgrade works when period ends

---

## 🐛 Troubleshooting

### Issue: Webhook Not Processing

**Symptoms**: Webhook shows 200 OK but data not updating

**Check**:
1. Railway logs for webhook processing messages
2. Firestore user document exists
3. `billing.stripeCustomerId` matches Stripe customer ID
4. Webhook handler is not throwing errors

**Fix**: Resend webhook from Stripe Dashboard

---

### Issue: Quota Not Counting Down

**Symptoms**: Always shows max quota

**Check**:
1. `/api/payments/flatlay/consume` endpoint is being called
2. Railway logs show "Consumed flat lay credit"
3. Firestore `quotas.flatlaysRemaining` is updating

**Fix**: Check frontend is calling consume endpoint

---

### Issue: Wrong Tier Assigned

**Symptoms**: User has Premium price ID but shows as Pro

**Check**:
1. Railway `STRIPE_PRICE_TIER2` and `STRIPE_PRICE_TIER3` values
2. Match them to actual Stripe price IDs
3. Resend webhook to update role

**Fix**: Update Railway environment variables or use fix script

---

## ✅ Success Criteria

All of these should work:

- [ ] Can upgrade to Pro/Premium
- [ ] Webhook processes successfully
- [ ] Firestore updates correctly
- [ ] Quota counts down when using flat lays
- [ ] Customer Portal opens
- [ ] Cancellation schedules correctly
- [ ] Premium features work until period ends
- [ ] Auto-downgrade works at period end

---

## 🚀 Ready for Production?

Before going live, ensure:

- [ ] All tests pass in sandbox
- [ ] Stripe account verified
- [ ] Live API keys obtained
- [ ] Live products created
- [ ] Live webhook configured
- [ ] Railway environment variables updated for live mode
- [ ] Tested with real card (small amount, then refunded)

---

**Start Testing**: Begin with Step 1 and work through each test!

