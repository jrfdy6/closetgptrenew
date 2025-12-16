# 30-Day Free Trial Strategy

## Overview
The Easy Outfit App offers a **30-day free trial exclusively for monthly subscriptions** (not yearly). Here's the complete logic and reasoning.

---

## Why Monthly Only, Not Yearly?

### 1. **Economic Reasoning**
- **Monthly Plans**: Users are less committed initially and need incentive → Free trial reduces risk
- **Yearly Plans**: Already include ~28% discount (save $24-47 depending on tier)
  - Adding 30-day trial = giving away 8% additional value
  - Example: Tier 2 yearly = $60/year. 30-day trial = ~$1.75 value given away

### 2. **User Commitment Signal**
- **Yearly Buyers**: Already demonstrate long-term commitment and intent to stay
- **Monthly Buyers**: May be testing/evaluating the product → Trial provides safe entry point

### 3. **Industry Standard**
- Netflix, Spotify, and most SaaS apps: Trials only for entry-level plans
- Annual subscribers get discount, not discount + trial

### 4. **Conversion Funnel**
```
Free User
    ↓
Free Trial (Monthly) ← Reduces friction for commitment
    ↓
Paid Monthly Subscription
    ↓
(Later) Upgrade to Yearly ← Already using, minimal friction
```

---

## Implementation Details

### Backend Logic (`/backend/src/routes/payments.py`)

**Location**: `create_checkout_session()` function, lines 252-276

```python
# Add 30-day free trial ONLY for monthly subscriptions if user hasn't used one
# Rationale: Yearly subscriptions already have a discount and indicate committed users
if not has_used_trial and interval == "month":
    checkout_params['subscription_data'] = {
        'trial_period_days': 30,
    }
    logger.info(f"Adding 30-day free trial to checkout for user {user_id} (monthly plan)")
```

**Key Checks**:
1. `not has_used_trial` → User hasn't used a trial before
2. `interval == "month"` → **NEW**: Only monthly plans get trials
3. Trial is applied at Stripe checkout level

### Frontend Logic (`/frontend/src/app/subscription/page.tsx`)

**Components Added**:
1. **Billing Cycle Toggle**: Users can switch between Monthly/Yearly
2. **Dynamic Pricing Display**:
   - Monthly: Shows `$7.00/month` (tier 2), `$11.00/month` (tier 3)
   - Yearly: Shows `$60/year` (tier 2), `$85/year` (tier 3)
3. **Free Trial Badge**: Only appears when:
   - User is eligible (`canUpgrade`)
   - User hasn't used trial (`!subscription?.trial_used`)
   - **Monthly billing cycle is selected** (`billingCycle === 'month'`)
4. **Button Labels**:
   - Monthly + No trial used: "Start Free Trial"
   - Monthly + Trial used: "Upgrade Now"
   - Yearly (any): "Subscribe Now"

---

## User Flow

### First-Time User (Monthly Path)
```
1. User lands on /subscription
2. Sees "30-Day Free Trial" badge on Pro/Premium (monthly)
3. Clicks "Start Free Trial"
4. Redirected to Stripe checkout with trial enabled
5. After 30 days: Charged monthly subscription
```

### First-Time User (Yearly Path)
```
1. User lands on /subscription
2. Toggles to "Yearly" billing
3. No trial badge shown (intentional)
4. Clicks "Subscribe Now"
5. Immediately charged yearly subscription (no trial period)
```

### Returning User (Trial Already Used)
```
1. User lands on /subscription
2. No trial badge shown (any billing cycle)
3. Shows "Upgrade Now" button
4. Proceeds to full payment immediately
```

---

## Stripe Configuration

The trial is enabled at Stripe's checkout session level:

```python
checkout_params['subscription_data'] = {
    'trial_period_days': 30,
}
```

Stripe automatically:
- Delays first charge by 30 days
- Sends notification before trial ends
- Updates subscription status to `trialing`
- Handles automatic billing after trial completes

---

## Tracking Trial Status

Users' trial information is stored in Firestore:

```firestore
users/{uid}/subscription:
  ├── trial_used: boolean         # Has user ever used a trial?
  ├── trialEnd: timestamp         # When does current trial end?
  └── status: string              # 'trialing', 'active', 'canceled', etc.
```

---

## Key Business Metrics

### What This Achieves:
- ✅ Reduces friction for monthly subscription signups
- ✅ Prevents discount stacking (yearly already discounted)
- ✅ Preserves revenue from committed yearly buyers
- ✅ Aligns with industry best practices
- ✅ Clear differentiation: Trial = conversion tool, Yearly = loyalty tool

### Conversion Incentives by Path:
| Path | Incentive | Conversion Goal |
|------|-----------|-----------------|
| **Free → Monthly Trial** | 30-day free trial | Lower risk entry |
| **Free → Yearly** | Save ~28% | Upfront commitment |
| **Monthly → Yearly** | None needed | Already proven value |

---

## How to Modify This

### To Change Trial Days:
```python
# /backend/src/routes/payments.py, line 274
'trial_period_days': 30,  # Change to desired number
```

### To Enable Trial for Yearly:
```python
# Change this line:
if not has_used_trial and interval == "month":
# To:
if not has_used_trial:  # Removes interval check
```

### To Disable Trials Entirely:
```python
# Comment out or remove the entire block (lines 272-276)
```

---

## Testing

### Manual Testing Checklist:
- [ ] Create new account, try monthly → See "Start Free Trial" button
- [ ] Create new account, switch to yearly → No trial badge, "Subscribe Now" button
- [ ] Use trial, complete 30 days → Charge automatically
- [ ] Use trial, then login → No second trial option available
- [ ] Try yearly directly → No trial option at all
- [ ] Check Stripe dashboard → Subscription shows `trialing` status during trial

---

## Related Files
- Backend: `backend/src/routes/payments.py`
- Frontend: `frontend/src/app/subscription/page.tsx`
- Services: `frontend/src/lib/services/subscriptionService.ts`
- Types: `frontend/src/types/subscription.ts` (if applicable)

