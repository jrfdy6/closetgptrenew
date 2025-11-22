# Enable Stripe Customer Portal

The "Method Not Allowed" error when clicking "Open Customer Portal" is likely because the Customer Portal needs to be enabled in Stripe.

## Quick Fix

1. **Go to Stripe Dashboard**: https://dashboard.stripe.com
2. **Click "Billing"** in the left sidebar
3. **Click "Customer portal"** (or "Billing portal")
4. **Click "Activate test link"** or **"Activate link"** button
5. Configure settings (or use defaults):
   - Allow customers to update payment methods: ✅
   - Allow customers to cancel subscriptions: ✅ (optional)
   - Return URL: Your frontend URL
6. **Save** or **Activate**

## After Enabling

The Customer Portal button should work. When users click it, they'll be able to:
- Update payment methods
- View billing history
- Cancel subscriptions (if enabled)
- Update billing information

## Alternative: Check Webhook Processing

If the portal is already enabled, the error might be because:
1. The webhook hasn't processed yet (wait 10-30 seconds)
2. The `stripeCustomerId` wasn't saved to your user document

**Check Stripe Dashboard → Webhooks → Events** to see if `checkout.session.completed` was processed.

---

**Note**: The subscription itself is working (you're on Pro plan with 7 flat lays), so the main integration is successful! The portal is just an extra feature for subscription management.

