# Stripe Setup Guide - Step by Step

## 🎯 Quick Start

This guide will walk you through setting up Stripe for Easy Outfit App in about 10 minutes.

---

## Step 1: Create Stripe Account (2 minutes)

1. Go to https://stripe.com
2. Click **"Start now"** or **"Sign up"**
3. Enter your email and create a password
4. Verify your email address
5. You'll start in **Test Mode** (perfect for testing!)

✅ **You're now in Test Mode - everything is free!**

---

## Step 2: Get Your API Keys (1 minute)

1. In Stripe Dashboard, go to **Developers** → **API keys**
2. You'll see two keys:
   - **Publishable key** (starts with `pk_test_...`) - Not needed for backend
   - **Secret key** (starts with `sk_test_...`) - **Copy this one!**

3. Click **"Reveal test key"** next to Secret key
4. Copy the entire key (it looks like: `sk_test_51AbC123...`)

✅ **Save this key - you'll need it for Railway**

---

## Step 3: Create Products and Prices (3 minutes)

### Create Pro Subscription

1. Go to **Products** → **Add product**
2. Fill in:
   - **Name**: `Pro Subscription`
   - **Description**: `Pro tier subscription - 7 flat lays per week, advanced features`
3. Under **Pricing**, click **"Add pricing"**
4. Set:
   - **Price**: `9.99`
   - **Currency**: `USD`
   - **Billing period**: `Monthly` (recurring)
5. Click **"Save"**
6. **Copy the Price ID** (starts with `price_...`) - looks like `price_1AbC123...`

✅ **Save this Price ID for Tier 2**

### Create Premium Subscription

1. Click **Products** → **Add product** again
2. Fill in:
   - **Name**: `Premium Subscription`
   - **Description**: `Premium tier subscription - 30 flat lays per week, all features`
3. Under **Pricing**, click **"Add pricing"**
4. Set:
   - **Price**: `29.99`
   - **Currency**: `USD`
   - **Billing period**: `Monthly` (recurring)
5. Click **"Save"**
6. **Copy the Price ID** (starts with `price_...`)

✅ **Save this Price ID for Tier 3**

---

## Step 4: Set Up Webhook Endpoint (2 minutes)

1. Go to **Developers** → **Webhooks**
2. Click **"Add endpoint"**
3. **Endpoint URL**: 
   ```
   https://closetgptrenew-production.up.railway.app/api/payments/webhook
   ```
4. **Description**: `Easy Outfit App Subscription Webhooks`
5. Under **"Select events to listen to"**, click **"Select events"**
6. Check these events:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
   - ✅ `invoice.payment_succeeded`
   - ✅ `invoice.payment_failed`
7. Click **"Add endpoint"**
8. After creating, click on the endpoint
9. **Copy the Signing secret** (starts with `whsec_...`)

✅ **Save this webhook secret for Railway**

---

## Step 5: Configure Railway Environment Variables (2 minutes)

1. Go to your Railway project: https://railway.app
2. Select your **backend service** (closetgptrenew-production)
3. Click on the **Variables** tab
4. Click **"+ New Variable"** for each of these:

### Add These Variables:

```bash
STRIPE_SECRET_KEY=sk_test_...  # Your secret key from Step 2
STRIPE_WEBHOOK_SECRET=whsec_...  # Your webhook secret from Step 4
STRIPE_PRICE_TIER2=price_...  # Pro tier price ID from Step 3
STRIPE_PRICE_TIER3=price_...  # Premium tier price ID from Step 3
FRONTEND_URL=https://easyoutfitapp.com  # Your frontend URL (or Vercel URL)
```

5. After adding all variables, Railway will automatically redeploy

✅ **Your backend is now configured!**

---

## Step 6: Test the Integration (2 minutes)

### Test Card Numbers (Test Mode Only)

Use these test cards - they work in Test Mode only:

- **Success**: `4242 4242 4242 4242`
- **Requires authentication**: `4000 0025 0000 3155`
- **Declined**: `4000 0000 0000 0002`

Use any:
- **Expiry**: Future date (e.g., `12/25`)
- **CVC**: Any 3 digits (e.g., `123`)
- **ZIP**: Any 5 digits (e.g., `12345`)

### Test Flow

1. **Start your frontend** (if running locally):
   ```bash
   cd frontend
   npm run dev
   ```

2. **Visit the subscription page**:
   - Local: http://localhost:3000/subscription
   - Production: https://easyoutfitapp.com/subscription

3. **Click "Upgrade to Pro"** or **"Upgrade to Premium"**

4. **Use test card**: `4242 4242 4242 4242`
   - Expiry: `12/25`
   - CVC: `123`
   - ZIP: `12345`

5. **Complete checkout** - You'll be redirected to success page

6. **Verify in Stripe Dashboard**:
   - Go to **Payments** - you should see the test payment
   - Go to **Webhooks** → **Events** - you should see webhook events

7. **Check Firestore** (optional):
   - Your user document should have updated subscription info

✅ **If you see the success page, everything is working!**

---

## Step 7: Verify Webhook is Working

1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click on your webhook endpoint
3. Go to **"Events"** tab
4. You should see events like:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `invoice.payment_succeeded`

✅ **If you see events, webhooks are working!**

---

## Troubleshooting

### Webhook Not Receiving Events

1. **Check the webhook URL is correct**:
   - Should be: `https://closetgptrenew-production.up.railway.app/api/payments/webhook`
   - Make sure it's accessible (try opening in browser - should show error, not 404)

2. **Check Railway logs**:
   - Go to Railway → Your service → **Deployments** → Click latest → **View Logs**
   - Look for webhook processing messages

3. **Verify webhook secret**:
   - Make sure `STRIPE_WEBHOOK_SECRET` in Railway matches the one in Stripe

### Payment Not Processing

1. **Check API key**:
   - Make sure `STRIPE_SECRET_KEY` starts with `sk_test_` (for test mode)
   - Verify it's the full key (not truncated)

2. **Check price IDs**:
   - Make sure `STRIPE_PRICE_TIER2` and `STRIPE_PRICE_TIER3` start with `price_`
   - Verify they match the Price IDs in Stripe Dashboard

3. **Check Railway logs**:
   - Look for errors when creating checkout session

### Subscription Not Updating

1. **Check webhook events**:
   - Go to Stripe → Webhooks → Events
   - See if events are being sent

2. **Check webhook processing**:
   - Look at Railway logs for webhook handler messages
   - Should see: "Processing Stripe webhook event: checkout.session.completed"

3. **Check Firestore**:
   - Verify user document has `subscription` and `billing` fields
   - Check that `subscription.role` is updated

---

## Going Live (When Ready)

When you're ready to accept real payments:

1. **Activate Stripe Account**:
   - Complete business verification
   - Add banking information
   - Switch to **Live Mode** (toggle in top right)

2. **Get Live Keys**:
   - Toggle to **Live Mode**
   - Copy new **Secret key** (starts with `sk_live_...`)
   - Update `STRIPE_SECRET_KEY` in Railway

3. **Create Live Products**:
   - Create the same products in Live Mode
   - Copy new **Price IDs**
   - Update `STRIPE_PRICE_TIER2` and `STRIPE_PRICE_TIER3` in Railway

4. **Update Webhook**:
   - Create new webhook endpoint in Live Mode
   - Copy new **Signing secret**
   - Update `STRIPE_WEBHOOK_SECRET` in Railway

5. **Test with Real Payment**:
   - Make a small test purchase
   - Verify everything works

---

## Quick Reference

| What | Where to Find | Example |
|------|--------------|---------|
| **Secret Key** | Developers → API keys | `sk_test_51AbC...` |
| **Webhook Secret** | Developers → Webhooks → [endpoint] | `whsec_...` |
| **Price ID (Pro)** | Products → Pro → Pricing | `price_1AbC...` |
| **Price ID (Premium)** | Products → Premium → Pricing | `price_1XyZ...` |

---

## Support

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Support**: https://support.stripe.com
- **Test Cards**: https://stripe.com/docs/testing

---

## Next Steps

Once everything is set up:

1. ✅ Test with test cards
2. ✅ Verify webhooks are working
3. ✅ Test subscription management (customer portal)
4. ✅ When ready, switch to Live Mode

**You're all set!** 🎉

