# Test Webhook Endpoint

## ✅ Your Server is Running

Railway logs show:
- ✅ Server started successfully
- ✅ Payment routes registered:
  - `/api/payments/webhook` (POST)
  - `/api/payments/subscription/current` (GET)
  - `/api/payments/checkout/create-session` (POST)
  - `/api/payments/checkout/create-portal-session` (POST)
  - `/api/payments/flatlay/consume` (POST)
- ✅ Environment variables loaded (STRIPE_SECRET_KEY, STRIPE_PRICE_TIER2, STRIPE_PRICE_TIER3, STRIPE_WEBHOOK_SECRET)

## 🧪 Test Your Webhook Endpoint

### Option 1: Test from Stripe Dashboard (Easiest)

1. **Go to Stripe Dashboard** → **Developers** → **Webhooks**
2. **Click on your webhook endpoint**
3. **Click "Send test webhook"** button
4. **Select event**: `customer.subscription.updated`
5. **Enter subscription ID**: `sub_1SWIwpQ00ZnKRYewaoCUVePE`
6. **Click "Send test webhook"**
7. **Check Railway logs** - should see:
   ```
   Processing Stripe webhook event: customer.subscription.updated
   Updated subscription sub_1SWIwpQ00ZnKRYewaoCUVePE for user...
   ```

### Option 2: Check Recent Webhook Deliveries

1. **Go to Stripe Dashboard** → **Developers** → **Webhooks**
2. **Click on your webhook endpoint**
3. **View "Recent deliveries"** tab
4. **Look for the `customer.subscription.updated` event** from 4:04:42 PM
5. **Check status**:
   - ✅ **200 OK** = Webhook delivered successfully
   - ❌ **4xx/5xx** = Error (check response body)

### Option 3: Check Railway Logs for Webhook Processing

1. **Go to Railway Dashboard** → Your service → **Logs**
2. **Filter logs** for "webhook" or "subscription"
3. **Look for entries** around 4:04:42 PM:
   ```
   Processing Stripe webhook event: customer.subscription.updated
   Updated subscription sub_1SWIwpQ00ZnKRYewaoCUVePE...
   ```

## 🔍 Verify Subscription Data Was Updated

### Check Firestore

Go to Firestore and check your user document (`users/dANqjiI0CKgaitxzYtw1bhtvQrG3`):

**Should have:**
- ✅ `subscription.currentPeriodEnd`: `1766418123` (not 0)
- ✅ `subscription.cancelAtPeriodEnd`: `true`
- ✅ `subscription.priceId`: `price_1SWIV7Q00ZnKRYewvOmTXGU1`
- ✅ `subscription.role`: `tier2` or `tier3` (based on price ID mapping)

**If still showing 0:**
- Webhook may not have processed correctly
- Check Railway logs for errors
- Resend webhook from Stripe Dashboard

## 🐛 Troubleshooting

### Issue: Webhook Not Received

**Check:**
1. Webhook URL is correct: `https://closetgptrenew-production.up.railway.app/api/payments/webhook`
2. Webhook is enabled in Stripe Dashboard
3. Events are selected (should include `customer.subscription.updated`)

### Issue: Webhook Returns Error

**Check Railway logs for:**
- `Invalid signature` → `STRIPE_WEBHOOK_SECRET` mismatch
- `Invalid payload` → Webhook format issue
- `500 error` → Backend processing error

### Issue: Data Not Updating

**Check:**
1. Railway logs show webhook was processed
2. No errors in webhook handler
3. User document exists in Firestore
4. `billing.stripeCustomerId` matches Stripe customer ID

## ✅ Next Steps

1. **Verify webhook was processed** (check Railway logs)
2. **Check Firestore** (currentPeriodEnd should be set)
3. **Test subscription page** (should show correct tier and period end)
4. **Test cancellation flow** (premium features work until period ends)

---

**Quick Test**: Send a test webhook from Stripe Dashboard and watch Railway logs to see if it processes!

