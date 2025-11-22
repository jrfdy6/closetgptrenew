# Stripe Payment Setup Guide

Complete guide for setting up Stripe payments for Easy Outfit App.

## 1. Create Stripe Account

1. Go to https://stripe.com and create an account
2. Complete account setup and verification
3. You'll start in **Test Mode** (recommended for development)

## 2. Create Products and Prices

### Step 1: Create Pro Product

1. Go to **Products** → **Add Product**
2. Name: `Pro Subscription`
3. Description: `Pro tier subscription - 7 flat lays per week, advanced features`
4. Pricing:
   - **Price**: $9.99
   - **Billing period**: Monthly (recurring)
   - **Currency**: USD
5. Click **Save**
6. **Copy the Price ID** (starts with `price_...`)

### Step 2: Create Premium Product

1. Go to **Products** → **Add Product**
2. Name: `Premium Subscription`
3. Description: `Premium tier subscription - 30 flat lays per week, all features`
4. Pricing:
   - **Price**: $29.99
   - **Billing period**: Monthly (recurring)
   - **Currency**: USD
5. Click **Save**
6. **Copy the Price ID** (starts with `price_...`)

## 3. Get API Keys

1. Go to **Developers** → **API keys**
2. Copy your **Secret key** (starts with `sk_test_...` for test mode)
3. Your **Publishable key** is also available (for frontend use)

## 4. Set Up Webhook Endpoint

### Step 1: Create Webhook Endpoint

1. Go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. **Endpoint URL**: `https://closetgptrenew-production.up.railway.app/api/payments/webhook`
   - Update with your actual backend URL
4. **Description**: `Easy Outfit App Subscription Webhooks`
5. **Events to send**: Select these events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
6. Click **Add endpoint**

### Step 2: Copy Webhook Signing Secret

1. After creating the webhook, click on it
2. Copy the **Signing secret** (starts with `whsec_...`)
3. Keep this secret secure - you'll need it for your backend

## 5. Set Environment Variables

Add these to your Railway backend environment variables:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...  # Your Stripe secret key
STRIPE_WEBHOOK_SECRET=whsec_...  # Webhook signing secret

# Stripe Price IDs (from Step 2)
STRIPE_PRICE_TIER2=price_...  # Pro tier price ID
STRIPE_PRICE_TIER3=price_...  # Premium tier price ID

# Frontend URL (for redirects)
FRONTEND_URL=https://easyoutfitapp.com  # Your frontend URL
```

### How to Add in Railway:

1. Go to your Railway project
2. Select your backend service
3. Go to **Variables** tab
4. Click **+ New Variable**
5. Add each variable above
6. Click **Deploy** to apply changes

## 6. Test the Integration

### Test Card Numbers (Test Mode Only)

Use these test card numbers in Stripe test mode:

- **Success**: `4242 4242 4242 4242`
- **Requires authentication**: `4000 0025 0000 3155`
- **Declined**: `4000 0000 0000 0002`

Use any:
- **Expiry**: Future date (e.g., 12/25)
- **CVC**: Any 3 digits (e.g., 123)
- **ZIP**: Any 5 digits (e.g., 12345)

### Test Flow:

1. Visit your app's subscription page
2. Click "Upgrade to Pro"
3. Use test card `4242 4242 4242 4242`
4. Complete checkout
5. Check webhook logs in Stripe dashboard
6. Verify user subscription updated in Firestore

## 7. Go Live (Production)

When ready for production:

1. **Activate your Stripe account**:
   - Complete business verification
   - Add banking information
   - Switch to **Live Mode**

2. **Get Live API Keys**:
   - Toggle to **Live Mode** in Stripe dashboard
   - Copy new **Secret key** (starts with `sk_live_...`)
   - Update `STRIPE_SECRET_KEY` in Railway

3. **Create Live Products**:
   - Create the same products in Live Mode
   - Copy new **Price IDs**
   - Update environment variables

4. **Update Webhook Endpoint**:
   - Update webhook URL to production URL
   - Copy new webhook signing secret
   - Update `STRIPE_WEBHOOK_SECRET`

5. **Test with Real Payments**:
   - Make a small test purchase
   - Verify webhook receives events
   - Check subscription updates correctly

## 8. Monitoring

### Stripe Dashboard:
- Monitor payments in **Payments** section
- View subscription activity in **Subscriptions**
- Check webhook logs in **Developers** → **Webhooks** → **Events**

### Your App:
- Check Firestore user documents for subscription updates
- Monitor backend logs for webhook processing
- Verify quota refills work correctly

## Troubleshooting

### Webhook Not Receiving Events:
- Verify webhook URL is correct and accessible
- Check webhook signing secret matches
- Verify endpoint is public (not behind auth)
- Check Railway logs for errors

### Payments Not Processing:
- Verify `STRIPE_SECRET_KEY` is correct
- Check you're using correct mode (test vs live)
- Verify price IDs match Stripe dashboard

### Subscription Not Updating:
- Check webhook events are firing
- Verify webhook handler logs in Railway
- Check Firestore rules allow updates
- Verify user document structure matches expected schema

## Support

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Support**: https://support.stripe.com
- **Test Cards**: https://stripe.com/docs/testing

## Quick Reference

| Variable | Where to Get | Example |
|----------|-------------|---------|
| `STRIPE_SECRET_KEY` | Developers → API keys | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Developers → Webhooks → [endpoint] | `whsec_...` |
| `STRIPE_PRICE_TIER2` | Products → [Pro] → Pricing | `price_abc123...` |
| `STRIPE_PRICE_TIER3` | Products → [Premium] → Pricing | `price_xyz789...` |
| `FRONTEND_URL` | Your app URL | `https://easyoutfitapp.com` |

