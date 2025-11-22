# Recommended Stripe Webhook Events

## ✅ Currently Handled Events (6 events)

Your code currently handles these events:

1. ✅ `checkout.session.completed` - When user completes payment
2. ✅ `customer.subscription.created` - When subscription is created
3. ✅ `customer.subscription.updated` - When subscription changes (including cancel_at_period_end)
4. ✅ `customer.subscription.deleted` - When subscription is deleted (period ended)
5. ✅ `invoice.payment_succeeded` - When payment succeeds (refills quotas)
6. ✅ `invoice.payment_failed` - When payment fails

## ✅ Subscription End Handling - Already Covered!

Your current events **already handle subscription period end**:

- **`customer.subscription.updated`**: Fires when `cancel_at_period_end` is set to `true`
  - Your handler stores `cancelAtPeriodEnd` flag
  - User keeps premium access until period ends

- **`customer.subscription.deleted`**: Fires when period ends and subscription is deleted
  - Your handler downgrades user to free tier
  - Resets quotas to free tier limits

- **`get_current_subscription` endpoint**: Checks period end on every call
  - Auto-downgrades if period expired
  - Works even if webhook is delayed

**No additional events needed for subscription end!** ✅

## 🎯 Optional Additional Events (Nice to Have)

### 1. `invoice.upcoming` ⭐ **RECOMMENDED**
- **When**: 7 days before subscription renewal
- **Use Case**: Send reminder emails, notify users of upcoming charge
- **Why**: Better user experience, reduces failed payments
- **Implementation**: Would need handler to send email/notification

### 2. `invoice.payment_action_required`
- **When**: Payment requires user action (3D Secure, etc.)
- **Use Case**: Notify user to complete payment
- **Why**: Reduce failed payments due to user action needed
- **Implementation**: Would need handler to notify user

### 3. `customer.subscription.trial_will_end` (If you add trials)
- **When**: 3 days before trial ends
- **Use Case**: Notify users trial is ending
- **Why**: Convert trial users to paid
- **Implementation**: Would need handler for trial notifications

### 4. `invoice.finalized`
- **When**: Draft invoice becomes final
- **Use Case**: Track invoice creation
- **Why**: Better invoice tracking
- **Implementation**: Optional logging/analytics

### 5. `customer.subscription.paused` / `customer.subscription.resumed`
- **When**: Subscription is paused/resumed
- **Use Case**: Handle paused subscriptions
- **Why**: If you implement pause functionality
- **Implementation**: Would need handler to manage paused state

## 📋 Current Event Selection

Based on your screenshot, you currently have **7 events selected**. The essential ones are:

### Must Have (Already Selected):
- ✅ `checkout.session.completed`
- ✅ `customer.subscription.created`
- ✅ `customer.subscription.updated`
- ✅ `customer.subscription.deleted`
- ✅ `invoice.payment_succeeded`
- ✅ `invoice.payment_failed`

### Should Add:
- ⭐ `invoice.upcoming` - **Highly recommended**

### Optional (Add Later):
- `invoice.payment_action_required`
- `invoice.finalized`
- `customer.subscription.trial_will_end` (if you add trials)

## 🔧 How to Add Events

1. **Go to Stripe Dashboard** → **Developers** → **Webhooks**
2. **Click your webhook endpoint**
3. **Click "Edit destination"** or find the event list
4. **Search for the event** (e.g., "invoice.upcoming")
5. **Check the box** to enable it
6. **Save**

## 💻 Code Updates Needed

If you add `invoice.upcoming`, you'll need to handle it in your webhook handler:

```python
elif event_type == 'invoice.upcoming':
    invoice = event['data']['object']
    await handle_invoice_upcoming(invoice)
```

But for now, your current events cover all the essential subscription lifecycle events!

## ✅ Summary

**Current setup is good!** You have all essential events. The only one I'd recommend adding is:

- ⭐ **`invoice.upcoming`** - To notify users before renewal

Everything else (subscription end, cancellation, period end) is already covered by your current events.

