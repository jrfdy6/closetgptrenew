# Stripe Live Mode Setup - Step-by-Step Guide

## Step 1: Verify Your Account (REQUIRED FIRST)

1. **Click "Settings"** in the left sidebar (or top menu)
2. **Click "Account details"**
3. **Check what's needed**:
   - Business information
   - Business address
   - Tax information
   - Identity verification
   - Bank account for payouts

**⚠️ You MUST complete verification before accepting real payments!**

---

## Step 2: Switch to Live Mode

1. **Look at the top right corner** of your Stripe Dashboard
2. **Find the toggle** that says "Test mode" or "Live mode"
3. **Click it to switch to "Live mode"**
   - The page will refresh
   - You'll see "Live mode" indicator at the top

**⚠️ Important**: You need to be in Live mode for the next steps!

---

## Step 3: Get Live API Keys

1. **Click "Developers"** in the left sidebar
2. **Click "API keys"** (should be selected by default)
3. **Make sure you're in Live mode** (check the toggle in top right)
4. **Find "Secret key"** section
5. **Click "Reveal live key"** or "Reveal" button
6. **Copy the key**: `sk_live_...` ⭐ **Save this!**

**⚠️ Keep this secret! Never share it publicly!**

---

## Step 4: Create Live Products

1. **Click "Product catalog"** in the left sidebar
2. **Click "Products"** tab
3. **Click "Add product"** button

### Create Pro Subscription:
- **Name**: `Pro Subscription`
- **Description**: `Pro tier subscription - 7 flat lays per week`
- **Pricing**:
  - **Price**: `9.99`
  - **Currency**: `USD`
  - **Billing**: Select **"Recurring"** → **"Monthly"**
- **Click "Save product"**
- **Copy the Price ID**: `price_...` (starts with `price_`) ⭐ **Save this!**

### Create Premium Subscription:
1. **Click "Add product"** again
- **Name**: `Premium Subscription`
- **Description**: `Premium tier subscription - 30 flat lays per week`
- **Pricing**:
  - **Price**: `29.99`
  - **Currency**: `USD`
  - **Billing**: Select **"Recurring"** → **"Monthly"**
- **Click "Save product"**
- **Copy the Price ID**: `price_...` (starts with `price_`) ⭐ **Save this!**

**⚠️ These Price IDs are different from your test Price IDs!**

---

## Step 5: Set Up Live Webhook

1. **Click "Developers"** in the left sidebar
2. **Click "Webhooks"**
3. **Make sure you're in Live mode** (check toggle)
4. **Click "Add endpoint"** button
5. **Enter endpoint URL**: 
   ```
   https://closetgptrenew-production.up.railway.app/api/payments/webhook
   ```
6. **Click "Select events"** or "Add events"
7. **Select these events**:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
   - ✅ `invoice.payment_succeeded`
   - ✅ `invoice.payment_failed`
8. **Click "Add events"** or "Save"
9. **Click "Add endpoint"**
10. **Click on the webhook endpoint** you just created
11. **Find "Signing secret"** section
12. **Click "Reveal"** or "Click to reveal"
13. **Copy the secret**: `whsec_...` ⭐ **Save this!**

**⚠️ This is different from your test webhook secret!**

---

## Step 6: Enable Customer Portal (Live Mode)

1. **Click "Settings"** in the left sidebar
2. **Click "Billing"**
3. **Click "Customer portal"**
4. **Make sure you're in Live mode** (check toggle)
5. **Click "Activate live link"** or toggle to enable
6. **Configure settings** (optional):
   - Allow subscription cancellation
   - Allow payment method updates
   - Set cancellation behavior
7. **Click "Save"**

---

## Step 7: Update Railway Variables

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your backend service** (closetgpt-backend)
3. **Click "Variables"** tab
4. **Update these variables** with your LIVE values:

```
STRIPE_SECRET_KEY=sk_live_... (your live secret key from Step 3)
STRIPE_PRICE_TIER2=price_... (live Pro price ID from Step 4)
STRIPE_PRICE_TIER3=price_... (live Premium price ID from Step 4)
STRIPE_WEBHOOK_SECRET=whsec_... (live webhook secret from Step 5)
```

5. **Click "Save"** or the variable will auto-save
6. **Railway will automatically redeploy** with new variables

**⚠️ Critical**: Make sure you're using LIVE values, not test values!

---

## Step 8: Test with Real Card (Small Amount)

**⚠️ IMPORTANT**: Test before going fully live!

1. **Go to your website**: https://easyoutfitapp.com (or your domain)
2. **Log in to your account**
3. **Go to Subscription page**
4. **Click "Upgrade"** on Pro or Premium
5. **Use your real credit card** (will charge real money)
6. **Complete the payment**
7. **Verify**:
   - ✅ Payment processes
   - ✅ You're redirected back to your site
   - ✅ Subscription page shows correct tier
   - ✅ Flat lay quota is correct
8. **Go back to Stripe Dashboard** → **Payments**
9. **Find your test payment**
10. **Click on it** → **Click "Refund"** → **Refund the payment**

**This verifies everything works!**

---

## ✅ Quick Navigation Reference

From Stripe Dashboard Home:
- **Settings** → Account details (verification)
- **Developers** → API keys (get live keys)
- **Product catalog** → Products (create live products)
- **Developers** → Webhooks (set up live webhook)
- **Settings** → Billing → Customer portal (enable portal)

---

## 🎯 What You'll Have After Setup

- ✅ Live API key: `sk_live_...`
- ✅ Live Pro Price ID: `price_...`
- ✅ Live Premium Price ID: `price_...`
- ✅ Live Webhook Secret: `whsec_...`
- ✅ All variables updated in Railway
- ✅ Customer Portal enabled
- ✅ Tested with real card

**You're ready to accept real payments!** 🚀


