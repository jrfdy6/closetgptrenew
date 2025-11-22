# Going Live with Stripe - Complete Checklist

## ⚠️ Current Status: TEST MODE

You're currently in **Stripe Test Mode (Sandbox)**. All payments are fake and no real money is processed.

## 🚀 Steps to Go Live

### Step 1: Complete Stripe Account Verification ⭐ **REQUIRED**

Before you can accept real payments, Stripe requires:

1. **Go to Stripe Dashboard** → **Settings** → **Account details**
2. **Complete verification**:
   - ✅ Business information
   - ✅ Business address
   - ✅ Tax information (if required)
   - ✅ Identity verification
   - ✅ Bank account for payouts

**Status**: Check your Stripe Dashboard to see what's still needed.

---

### Step 2: Get Live API Keys

1. **Go to Stripe Dashboard** → **Developers** → **API keys**
2. **Toggle to "Live mode"** (switch in top right corner)
3. **Copy your live keys**:
   - **Publishable key**: `pk_live_...` (not needed for backend)
   - **Secret key**: `sk_live_...` ⭐ **Copy this!**

**⚠️ Important**: These are different from your test keys!

---

### Step 3: Create Live Products and Prices

1. **Make sure you're in Live mode** (toggle in Stripe Dashboard)
2. **Go to Products** → **Add product**

#### Create Pro Subscription (Live):
- **Name**: `Pro Subscription`
- **Description**: `Pro tier subscription - 7 flat lays per week`
- **Price**: `9.99`
- **Currency**: `USD`
- **Billing**: `Monthly` (recurring)
- **Copy the Live Price ID**: `price_...` (starts with `price_`)

#### Create Premium Subscription (Live):
- **Name**: `Premium Subscription`
- **Description**: `Premium tier subscription - 30 flat lays per week`
- **Price**: `29.99`
- **Currency**: `USD`
- **Billing**: `Monthly` (recurring)
- **Copy the Live Price ID**: `price_...` (starts with `price_`)

**⚠️ Important**: These will be different Price IDs from your test products!

---

### Step 4: Set Up Live Webhook

1. **Go to Stripe Dashboard** → **Developers** → **Webhooks** (in Live mode)
2. **Click "Add endpoint"**
3. **Enter endpoint URL**: `https://closetgptrenew-production.up.railway.app/api/payments/webhook`
4. **Select events to listen to**:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
   - ✅ `invoice.payment_succeeded`
   - ✅ `invoice.payment_failed`
   - (Optional) `invoice.upcoming`
5. **Click "Add endpoint"**
6. **Copy the Signing secret**: `whsec_...` ⭐ **Copy this!**

**⚠️ Important**: This is different from your test webhook secret!

---

### Step 5: Update Railway Environment Variables

1. **Go to Railway Dashboard** → Your backend service → **Variables**
2. **Update these variables** with LIVE values:

```
STRIPE_SECRET_KEY=sk_live_... (replace test key)
STRIPE_PRICE_TIER2=price_... (live Pro price ID)
STRIPE_PRICE_TIER3=price_... (live Premium price ID)
STRIPE_WEBHOOK_SECRET=whsec_... (live webhook secret)
```

**⚠️ Critical**: 
- Remove or update the test keys
- Use LIVE Price IDs (different from test)
- Use LIVE webhook secret (different from test)

---

### Step 6: Enable Customer Portal (Live Mode)

1. **Go to Stripe Dashboard** → **Settings** → **Billing** → **Customer portal** (in Live mode)
2. **Click "Activate live link"**
3. **Configure portal settings**:
   - Allow subscription cancellation
   - Allow payment method updates
   - Set cancellation behavior
4. **Save changes**

---

### Step 7: Test with Real Card (Small Amount)

**⚠️ IMPORTANT**: Test with a real card before going fully live!

1. **Use your own card** to test the flow
2. **Upgrade to Pro or Premium** (will charge real money)
3. **Verify**:
   - Payment processes correctly
   - Webhook is received
   - Firestore updates correctly
   - Subscription page shows correct tier
4. **Refund the test payment** in Stripe Dashboard:
   - Go to **Payments** → Find the payment → **Refund**

---

### Step 8: Update Frontend URL (If Needed)

Make sure `FRONTEND_URL` in Railway points to your production frontend:
- Current: `https://easyoutfitapp.com` (or your actual domain)
- Verify this is correct for live mode

---

## ✅ Pre-Launch Checklist

Before accepting real payments, verify:

- [ ] Stripe account fully verified
- [ ] Live API keys obtained
- [ ] Live products created (Pro and Premium)
- [ ] Live Price IDs copied
- [ ] Live webhook endpoint configured
- [ ] Live webhook secret copied
- [ ] Railway environment variables updated with LIVE values
- [ ] Customer Portal enabled for live mode
- [ ] Tested with real card (and refunded)
- [ ] Webhook events are being received
- [ ] Firestore updates correctly
- [ ] Subscription page shows correct data
- [ ] Flat lay quota works correctly

---

## 🚨 Important Warnings

### ⚠️ Don't Mix Test and Live Keys

- **Never use test keys** (`sk_test_...`) in production
- **Never use live keys** (`sk_live_...`) in test mode
- **Keep them separate** - use different Railway environments if possible

### ⚠️ Test Mode vs Live Mode

- **Test Mode**: Everything is fake, no real money
- **Live Mode**: Real payments, real money, real customers
- **You can switch between them** using the toggle in Stripe Dashboard

### ⚠️ Webhook Secrets

- **Test webhook secret**: `whsec_...` (for test mode)
- **Live webhook secret**: `whsec_...` (different, for live mode)
- **Must match** the mode you're using

---

## 📊 Monitoring After Going Live

### Daily Checks:

1. **Stripe Dashboard**:
   - Check for failed payments
   - Monitor subscription cancellations
   - Review webhook delivery success rate

2. **Railway Logs**:
   - Check for webhook errors
   - Monitor subscription update errors
   - Watch for quota calculation issues

3. **Firestore**:
   - Verify user subscriptions are updating correctly
   - Check quota refills are working
   - Monitor subscription status changes

---

## 🔄 Switching Back to Test Mode

If you need to test something:

1. **Toggle back to Test mode** in Stripe Dashboard
2. **Update Railway variables** back to test keys
3. **Use test cards** for testing
4. **Switch back to Live** when ready

---

## 🎯 Quick Reference

### Test Mode (Current):
- API Key: `sk_test_...`
- Price IDs: `price_1SWIWxQ00ZnKRYewuivsPque` (test)
- Webhook Secret: `whsec_...` (test)
- Cards: `4242 4242 4242 4242` (test card)

### Live Mode (After Setup):
- API Key: `sk_live_...`
- Price IDs: `price_...` (new live IDs)
- Webhook Secret: `whsec_...` (new live secret)
- Cards: Real credit cards

---

## ✅ Ready to Go Live?

Once you've completed all steps:
1. ✅ Account verified
2. ✅ Live keys obtained
3. ✅ Live products created
4. ✅ Live webhook configured
5. ✅ Railway variables updated
6. ✅ Tested with real card

**You're ready to accept real payments!** 🚀

---

**⚠️ Remember**: Always test with a small amount first and refund it to verify everything works!

