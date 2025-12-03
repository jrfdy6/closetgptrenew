# Subscription Page vs Customer Portal - What's the Difference?

## 📄 Subscription Page (Your App)

**Location**: `/subscription` page in your app

**Purpose**: 
- **View and compare** subscription plans
- **Upgrade** to a new plan
- **See your current subscription status**
- **View usage statistics** (flat lays remaining, etc.)

**What You Can Do**:
- ✅ See all available plans (Free, Pro, Premium)
- ✅ Compare features between tiers
- ✅ Upgrade to a higher tier
- ✅ View your current plan details
- ✅ See how many flat lays you have remaining
- ✅ See usage progress bars

**What You CAN'T Do**:
- ❌ Update payment method
- ❌ Cancel subscription
- ❌ View billing history
- ❌ Change billing address
- ❌ Download invoices

---

## 🔐 Customer Portal (Stripe Hosted)

**Location**: Stripe's secure website (redirects from your app)

**Purpose**:
- **Manage billing** and payment methods
- **Cancel** or modify subscriptions
- **View billing history** and invoices
- **Update account information**

**What You Can Do**:
- ✅ Update credit card/payment method
- ✅ Cancel subscription
- ✅ View past invoices
- ✅ Download receipts
- ✅ Update billing address
- ✅ View payment history
- ✅ Reactivate canceled subscription

**What You CAN'T Do**:
- ❌ Upgrade to a new plan (must use your app)
- ❌ See usage statistics
- ❌ Compare plans

---

## 🎯 When to Use Each

### Use Subscription Page When:
- You want to **upgrade** your plan
- You want to **compare** different plans
- You want to **see your usage** (flat lays remaining)
- You want to **see what features** you have access to

### Use Customer Portal When:
- You need to **update your payment method**
- You want to **cancel** your subscription
- You need to **view or download invoices**
- You want to **change your billing address**
- You need to **view payment history**

---

## 🔄 How They Work Together

1. **User visits `/subscription`** → Sees plans, upgrades if needed
2. **User clicks "Manage Subscription"** → Redirected to Customer Portal
3. **User updates payment method in Portal** → Returns to your app
4. **User can upgrade again** → Back to Subscription page

---

## 💡 Summary

| Feature | Subscription Page | Customer Portal |
|---------|------------------|-----------------|
| **View Plans** | ✅ | ❌ |
| **Upgrade Plan** | ✅ | ❌ |
| **See Usage** | ✅ | ❌ |
| **Update Payment** | ❌ | ✅ |
| **Cancel Subscription** | ❌ | ✅ |
| **View Invoices** | ❌ | ✅ |
| **Billing History** | ❌ | ✅ |

**Think of it this way:**
- **Subscription Page** = "Shopping" for plans and viewing your current status
- **Customer Portal** = "Account management" for billing and payments

Both are needed for a complete subscription experience!

