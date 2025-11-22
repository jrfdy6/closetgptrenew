# What You Can Control with Stripe Webhooks

## ❌ What You CANNOT Change

**You cannot modify the structure or content of what Stripe sends in webhooks.** Stripe controls:
- The payload structure
- The field names (e.g., `current_period_end` vs `currentPeriodEnd`)
- Which fields are included
- The data format

## ✅ What You CAN Control

### 1. Choose Which Events to Receive

You can configure which webhook events Stripe sends:

1. **Go to Stripe Dashboard** → **Developers** → **Webhooks**
2. **Click your webhook endpoint**
3. **Click "Edit"** or **"Add events"**
4. **Select/deselect events**:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
   - ✅ `invoice.payment_succeeded`
   - ✅ `invoice.payment_failed`
   - And many more...

### 2. Resend Webhooks

If a webhook didn't process correctly:

1. **Go to Stripe Dashboard** → **Developers** → **Webhooks**
2. **Click your webhook endpoint**
3. **Find the event** in "Recent deliveries"
4. **Click "Resend"**
5. Your handler will process it again (with updated code)

### 3. Fetch Data Directly from Stripe API

If webhook data is incomplete, fetch it from Stripe:

```python
# Example: Fetch subscription to get current_period_end
stripe_sub = stripe.Subscription.retrieve(subscription_id)
period_end = stripe_sub.get('current_period_end', 0)
```

**This is already implemented** in your code as a fallback when `current_period_end` is missing!

### 4. Test Webhooks Manually

You can send test webhooks:

1. **Go to Stripe Dashboard** → **Developers** → **Webhooks**
2. **Click "Send test webhook"**
3. **Select event type**
4. **Enter subscription/customer ID**
5. **Send** - This triggers your handler

## 🔍 Why `current_period_end` Might Be Missing

Stripe webhooks sometimes don't include all fields, especially:
- During subscription creation (before period is set)
- During certain update events
- In test mode (sometimes)

## ✅ Your Current Solution

Your code now has a **fallback mechanism**:

1. **First**: Try to get `current_period_end` from webhook payload
2. **Second**: Try to get it from subscription items
3. **Third**: Fetch subscription from Stripe API directly

This ensures `current_period_end` is always set correctly!

## 🛠️ How to Fix Current Data

Since your Firestore still shows `currentPeriodEnd: 0`, you have options:

### Option 1: Resend Webhook (Easiest)

1. **Stripe Dashboard** → **Webhooks** → Your endpoint
2. **Find** `customer.subscription.updated` event
3. **Click "Resend"**
4. New code will fetch from Stripe API if needed

### Option 2: Use Fix Script

```bash
cd backend/scripts
python3 fix_subscription_data.py --user-id dANqjiI0CKgaitxzYtw1bhtvQrG3 --execute
```

This script:
- Fetches subscription from Stripe API
- Gets `current_period_end` directly
- Updates Firestore

### Option 3: Manual Firestore Update

1. **Go to Stripe Dashboard** → **Subscriptions**
2. **Find subscription**: `sub_1SWKRoQ00ZnKRYew2lEbGJwl`
3. **Note** `current_period_end` timestamp
4. **Update Firestore**: Set `subscription.currentPeriodEnd` to that value

## 📝 Summary

- **Can't change**: What Stripe sends in webhooks
- **Can control**: Which events you receive
- **Can do**: Resend webhooks, fetch from API, test manually
- **Your code**: Already handles missing data with API fallback

**Best approach**: Resend the webhook - your updated code will fetch `current_period_end` from Stripe API if it's missing!

