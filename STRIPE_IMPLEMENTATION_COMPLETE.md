# Stripe Payment System - Implementation Complete

## Overview

The Stripe payment system has been fully implemented for Easy Outfit App. This document provides a complete guide to the implementation, setup, and usage.

## Architecture

### Backend (FastAPI)
- **Location**: `backend/src/routes/payments.py`
- **Endpoints**:
  - `GET /api/payments/subscription/current` - Get current subscription
  - `POST /api/payments/checkout/create-session` - Create Stripe checkout session
  - `POST /api/payments/checkout/create-portal-session` - Create customer portal session
  - `POST /api/payments/webhook` - Handle Stripe webhooks

### Frontend (Next.js)
- **Subscription Service**: `frontend/src/lib/services/subscriptionService.ts`
- **Pages**:
  - `/subscription` - Subscription plans and upgrade page
  - `/subscription-success` - Success page after payment

## Features Implemented

### 1. Subscription Tiers
- **Tier 1 (Free)**: 1 flat lay per week
- **Tier 2 (Pro)**: $9.99/month - 7 flat lays per week
- **Tier 3 (Premium)**: $29.99/month - 30 flat lays per week

### 2. Payment Flow
1. User selects subscription tier
2. Backend creates Stripe checkout session
3. User redirected to Stripe checkout
4. After payment, webhook updates user subscription
5. User redirected to success page

### 3. Subscription Management
- Customer portal for managing subscriptions
- Update payment methods
- Cancel subscriptions
- View billing history

### 4. Webhook Handlers
- `checkout.session.completed` - Activate subscription after payment
- `customer.subscription.created` - Handle new subscriptions
- `customer.subscription.updated` - Update subscription changes
- `customer.subscription.deleted` - Downgrade on cancellation
- `invoice.payment_succeeded` - Refill quotas after payment
- `invoice.payment_failed` - Mark subscription as past_due

## Environment Variables

### Backend (Railway)
Add these to your Railway backend service environment variables:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...  # Your Stripe secret key (test or live)
STRIPE_WEBHOOK_SECRET=whsec_...  # Webhook signing secret

# Stripe Price IDs (from Stripe Dashboard)
STRIPE_PRICE_TIER2=price_...  # Pro tier price ID
STRIPE_PRICE_TIER3=price_...  # Premium tier price ID

# Frontend URL (for redirects)
FRONTEND_URL=https://easyoutfitapp.com  # Your frontend URL
```

### Frontend (Vercel)
Add this to your Vercel environment variables:

```bash
NEXT_PUBLIC_API_URL=https://closetgptrenew-production.up.railway.app
```

## Setup Instructions

### 1. Create Stripe Account
1. Go to https://stripe.com and create an account
2. Complete account setup and verification
3. Start in **Test Mode** for development

### 2. Create Products and Prices
1. Go to **Products** → **Add Product**
2. Create "Pro Subscription" product:
   - Price: $9.99/month (recurring)
   - Copy the Price ID (starts with `price_...`)
3. Create "Premium Subscription" product:
   - Price: $29.99/month (recurring)
   - Copy the Price ID

### 3. Set Up Webhook Endpoint
1. Go to **Developers** → **Webhooks** → **Add endpoint**
2. **Endpoint URL**: `https://closetgptrenew-production.up.railway.app/api/payments/webhook`
3. **Events to send**:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy the **Signing secret** (starts with `whsec_...`)

### 4. Configure Environment Variables
1. **Railway Backend**:
   - Go to your Railway project
   - Select backend service
   - Go to **Variables** tab
   - Add all backend environment variables listed above
   - Click **Deploy** to apply

2. **Vercel Frontend**:
   - Go to your Vercel project settings
   - Go to **Environment Variables**
   - Add `NEXT_PUBLIC_API_URL`
   - Redeploy if needed

## Testing

### Test Cards (Test Mode Only)
- **Success**: `4242 4242 4242 4242`
- **Requires authentication**: `4000 0025 0000 3155`
- **Declined**: `4000 0000 0000 0002`

Use any:
- **Expiry**: Future date (e.g., 12/25)
- **CVC**: Any 3 digits (e.g., 123)
- **ZIP**: Any 5 digits (e.g., 12345)

### Test Flow
1. Visit `/subscription` page
2. Click "Upgrade to Pro" or "Upgrade to Premium"
3. Use test card `4242 4242 4242 4242`
4. Complete checkout
5. Verify webhook logs in Stripe dashboard
6. Check user subscription updated in Firestore

## API Endpoints

### Get Current Subscription
```http
GET /api/payments/subscription/current
Authorization: Bearer <token>
```

**Response**:
```json
{
  "role": "tier2",
  "status": "active",
  "flatlays_remaining": 7
}
```

### Create Checkout Session
```http
POST /api/payments/checkout/create-session
Authorization: Bearer <token>
Content-Type: application/json

{
  "role": "tier2"
}
```

**Response**:
```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_..."
}
```

### Create Portal Session
```http
POST /api/payments/checkout/create-portal-session
Authorization: Bearer <token>
```

**Response**:
```json
{
  "url": "https://billing.stripe.com/..."
}
```

## Database Schema

### User Document Structure
```json
{
  "subscription": {
    "role": "tier2",
    "status": "active",
    "stripeSubscriptionId": "sub_...",
    "currentPeriodEnd": 1234567890,
    "priceId": "price_..."
  },
  "billing": {
    "stripeCustomerId": "cus_..."
  },
  "quotas": {
    "flatlaysRemaining": 7,
    "lastRefillAt": 1234567890
  }
}
```

## Production Deployment

### Going Live
1. **Activate Stripe Account**:
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

## Monitoring

### Stripe Dashboard
- Monitor payments in **Payments** section
- View subscription activity in **Subscriptions**
- Check webhook logs in **Developers** → **Webhooks** → **Events**

### Your App
- Check Firestore user documents for subscription updates
- Monitor backend logs for webhook processing
- Verify quota refills work correctly

## Troubleshooting

### Webhook Not Receiving Events
- Verify webhook URL is correct and accessible
- Check webhook signing secret matches
- Verify endpoint is public (not behind auth)
- Check Railway logs for errors

### Payments Not Processing
- Verify `STRIPE_SECRET_KEY` is correct
- Check you're using correct mode (test vs live)
- Verify price IDs match Stripe dashboard

### Subscription Not Updating
- Check webhook events are firing
- Verify webhook handler logs in Railway
- Check Firestore rules allow updates
- Verify user document structure matches expected schema

### Customer Portal Not Working
- Verify user has a `stripeCustomerId` in their billing data
- Check that customer exists in Stripe
- Verify `FRONTEND_URL` is set correctly

## Security Considerations

1. **Webhook Verification**: All webhooks are verified using Stripe's signature verification
2. **Authentication**: All payment endpoints require user authentication
3. **Environment Variables**: Never commit API keys to version control
4. **HTTPS**: All webhook endpoints must use HTTPS in production

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

## Implementation Status

✅ Backend payment routes implemented
✅ Frontend subscription service implemented
✅ Subscription pages created
✅ Customer portal endpoint added
✅ Webhook handlers for all events
✅ Invoice payment handlers
✅ Quota management
✅ Error handling and logging

The Stripe payment system is now fully functional and ready for use!

