# Next Steps After Stripe Sandbox Setup

## ✅ What You've Completed

1. ✅ Created Stripe account
2. ✅ Set up products and prices (Pro and Premium)
3. ✅ Configured webhook endpoint
4. ✅ Added environment variables to Railway
5. ✅ Integrated payment system in code

## 🧪 Step 1: Test the Payment Flow

### A. Test Subscription Upgrade

1. **Go to your subscription page**:
   - Navigate to `/subscription` on your app
   - You should see the three tiers (Free, Pro, Premium)

2. **Click "Join Pro" or "Join Premium"**:
   - Should redirect to Stripe Checkout
   - Use test card numbers (see below)

3. **Use Stripe Test Cards**:
   ```
   Card Number: 4242 4242 4242 4242
   Expiry: Any future date (e.g., 12/34)
   CVC: Any 3 digits (e.g., 123)
   ZIP: Any 5 digits (e.g., 12345)
   ```

4. **Complete the payment**:
   - Should redirect back to your app
   - Subscription page should show "Current Plan: Pro" or "Premium"
   - Flat lay quota should update (7 for Pro, 30 for Premium)

### B. Test Customer Portal

1. **Go to subscription page** (while on Pro/Premium)
2. **Click "Open Customer Portal"**
3. **Test features**:
   - Update payment method
   - Cancel subscription (should schedule for period end)
   - Reactivate subscription

### C. Test Flat Lay Quota

1. **Generate an outfit**
2. **Request a flat lay**
3. **Verify quota counts down**:
   - Pro: Should show "6 out of 7" after first use
   - Premium: Should show "29 out of 30" after first use

### D. Test Subscription Cancellation

1. **Cancel subscription** via Customer Portal
2. **Verify**:
   - Subscription shows "Active until [date]"
   - Premium features still work until period ends
   - After period ends, user downgrades to free tier

## 🔍 Step 2: Verify Webhook Events

### Check Railway Logs

1. **Go to Railway Dashboard** → Your backend service
2. **Open Logs tab**
3. **Look for webhook events**:
   ```
   Processing Stripe webhook event: checkout.session.completed
   Processing Stripe webhook event: customer.subscription.created
   Processing Stripe webhook event: invoice.payment_succeeded
   ```

### Check Stripe Dashboard

1. **Go to Stripe Dashboard** → Developers → Webhooks
2. **Click on your webhook endpoint**
3. **View "Recent events"**:
   - Should see successful webhook deliveries
   - Green checkmarks indicate success

### Test Webhook Events Manually

1. **In Stripe Dashboard** → Developers → Webhooks
2. **Click "Send test webhook"**
3. **Select event types**:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

## 🐛 Step 3: Troubleshooting Common Issues

### Issue: "Method Not Allowed" on Customer Portal

**Solution**: Enable Customer Portal in Stripe Dashboard
1. Go to Stripe Dashboard → Settings → Billing → Customer portal
2. Click "Activate test link"
3. Configure portal settings
4. Save changes

### Issue: Webhooks Not Receiving Events

**Check**:
1. Webhook URL is correct in Stripe Dashboard
2. `STRIPE_WEBHOOK_SECRET` is set in Railway
3. Backend is accessible from internet (Railway provides public URL)
4. Check Railway logs for webhook errors

### Issue: Quota Not Updating

**Check**:
1. Webhook events are being received (check logs)
2. User document in Firestore has `quotas.flatlaysRemaining`
3. Subscription role is correct (`tier2` or `tier3`)

### Issue: Subscription Not Showing After Payment

**Check**:
1. Webhook was received (check Stripe Dashboard)
2. User document updated in Firestore
3. Frontend is calling `/api/payments/subscription/current`
4. Check browser console for errors

## 📊 Step 4: Monitor Test Transactions

### In Stripe Dashboard

1. **Go to Payments** → Should see test payments
2. **Go to Customers** → Should see test customers
3. **Go to Subscriptions** → Should see active test subscriptions

### In Your App

1. **Check Firestore**:
   - `users` collection → User should have:
     - `subscription.role`: `tier2` or `tier3`
     - `subscription.status`: `active`
     - `billing.stripeCustomerId`: `cus_...`
     - `quotas.flatlaysRemaining`: 7 or 30

## 🚀 Step 5: Prepare for Live Mode

### Before Going Live

1. **Complete Stripe account verification**:
   - Add business information
   - Verify identity
   - Add bank account for payouts

2. **Get Live API Keys**:
   - Go to Stripe Dashboard → Developers → API keys
   - Switch to "Live mode" (toggle in top right)
   - Copy live keys:
     - `pk_live_...` (Publishable key)
     - `sk_live_...` (Secret key)

3. **Create Live Products**:
   - Switch to Live mode in Stripe Dashboard
   - Create products again (Pro and Premium)
   - Copy live Price IDs

4. **Set Up Live Webhook**:
   - Add webhook endpoint URL
   - Select events to listen to
   - Copy webhook signing secret

5. **Update Railway Environment Variables**:
   ```
   STRIPE_SECRET_KEY=sk_live_... (replace test key)
   STRIPE_PRICE_TIER2=price_... (live price ID)
   STRIPE_PRICE_TIER3=price_... (live price ID)
   STRIPE_WEBHOOK_SECRET=whsec_... (live webhook secret)
   ```

6. **Test with Real Card** (small amount):
   - Use your own card
   - Test complete flow
   - Verify webhooks work
   - Refund test payment

## ✅ Step 6: Go Live Checklist

- [ ] Stripe account fully verified
- [ ] Live API keys obtained
- [ ] Live products and prices created
- [ ] Live webhook endpoint configured
- [ ] Railway environment variables updated
- [ ] Tested with real card (and refunded)
- [ ] Customer Portal enabled for live mode
- [ ] Monitoring and logging set up
- [ ] Error handling tested
- [ ] Support process ready for payment issues

## 📝 Step 7: Post-Launch Monitoring

### Daily Checks

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

## 🆘 Support Resources

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Support**: Available in Dashboard
- **Webhook Testing**: Use Stripe CLI for local testing
- **Your App Logs**: Railway Dashboard → Logs

## 🎯 Quick Test Checklist

Run through this quick test to verify everything works:

- [ ] Can upgrade to Pro tier
- [ ] Can upgrade to Premium tier
- [ ] Subscription shows correct tier after payment
- [ ] Flat lay quota shows correct limit (7 or 30)
- [ ] Flat lay quota counts down when used
- [ ] Customer Portal opens successfully
- [ ] Can cancel subscription via portal
- [ ] Premium features work until period ends
- [ ] User downgrades to free after period ends
- [ ] Webhook events are being received
- [ ] Firestore user document updates correctly

---

**Ready to test?** Start with Step 1 and work through each test. If you encounter any issues, refer to Step 3 for troubleshooting.

