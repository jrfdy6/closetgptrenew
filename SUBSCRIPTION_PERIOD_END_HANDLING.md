# Subscription Period End Handling

## How Stripe Notifies Your App About Subscription Cancellations

When a user cancels their subscription, Stripe follows this flow:

### 1. User Cancels Subscription
- User clicks "Cancel" in Stripe Customer Portal
- Stripe sets `cancel_at_period_end: true` on the subscription
- Subscription status remains `active` until the period ends

### 2. Stripe Sends Webhook Events

#### `customer.subscription.updated` Event
- **When**: Immediately after cancellation, and whenever subscription changes
- **Contains**:
  - `cancel_at_period_end: true` (if scheduled to cancel)
  - `status: 'active'` (still active until period ends)
  - `current_period_end: <timestamp>` (when subscription will end)
- **What We Do**: 
  - Store `cancelAtPeriodEnd` flag in user document
  - Update `currentPeriodEnd` timestamp
  - Keep user on premium tier until period ends

#### `customer.subscription.deleted` Event
- **When**: At the end of the billing period (`current_period_end`)
- **Contains**:
  - `status: 'canceled'`
  - Subscription is deleted from Stripe
- **What We Do**:
  - Downgrade user to free tier (`tier1`)
  - Reset quotas to free tier limits
  - Update subscription status to `canceled`

### 3. Real-Time Period End Checks

Even if webhooks are delayed or missed, the app checks period end in two places:

#### A. When User Fetches Subscription (`/api/payments/subscription/current`)
- Checks if `current_period_end` has passed
- If yes and subscription was canceled, downgrades immediately
- Returns updated subscription status

#### B. When User Accesses Premium Features (`subscription_feature_access.py`)
- Checks period end before granting access
- Prevents premium features if period has expired
- Auto-downgrades if period ended

## Implementation Details

### Webhook Handler: `handle_subscription_updated`
```python
# Detects cancel_at_period_end
# Stores cancelAtPeriodEnd flag
# Updates currentPeriodEnd
# If period already ended, downgrades immediately
```

### Subscription Endpoint: `get_current_subscription`
```python
# Checks if current_period_end < now
# If period ended and canceled, downgrades to tier1
# Returns current subscription status
```

### Feature Access Check: `check_feature_access`
```python
# Checks period end before granting premium access
# Auto-downgrades if period expired
# Prevents premium features after period ends
```

## User Experience

1. **User Cancels**: 
   - Subscription marked to cancel at period end
   - User keeps premium features until `current_period_end`
   - Status shows "Active until [date]"

2. **Period Ends**:
   - Stripe sends `customer.subscription.deleted` webhook
   - App downgrades user to free tier
   - User loses premium features immediately

3. **If Webhook Missed**:
   - Next time user accesses app, period end check runs
   - User is downgraded automatically
   - No premium features after period ends

## Testing

To test period end handling:

1. **Cancel a subscription** in Stripe Dashboard
2. **Check user document** - should have `cancelAtPeriodEnd: true`
3. **Manually set `currentPeriodEnd`** to past timestamp in Firestore
4. **Call `/api/payments/subscription/current`** - should return `tier1`
5. **Try to access premium feature** - should be denied

## Important Notes

- Users keep premium access until `current_period_end`, even after canceling
- Period end is checked on every subscription fetch and feature access
- Webhook is primary method, but real-time checks provide backup
- Downgrade happens automatically - no manual intervention needed

