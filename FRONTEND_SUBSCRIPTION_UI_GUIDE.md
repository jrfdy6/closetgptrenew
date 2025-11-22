# Frontend Subscription UI Guide

## What You'll See on the Frontend

### 1. **Subscription Page** (`/subscription` or `/upgrade`)

**What it shows:**
- 3 subscription tiers displayed as cards:
  - **Free (tier1)** - $0/month
  - **Pro (tier2)** - $9.99/month - "Most Popular" badge
  - **Premium (tier3)** - $29.99/month
- **Current Plan Badge** showing:
  - Your current subscription tier
  - Number of flat lays remaining this week
- **Upgrade Buttons** on Pro/Premium cards
  - Clicking redirects to Stripe checkout
  - Shows "Processing..." while creating checkout session

**Visual Layout:**
```
┌─────────────────────────────────────┐
│   Subscription Plans                │
│   Current Plan: Free • 1 remaining │
├──────────┬──────────┬───────────────┤
│  Free    │  Pro ⭐  │  Premium      │
│  $0      │ $9.99    │  $29.99       │
│          │          │               │
│  [Current]│ [Upgrade]│ [Upgrade]    │
└──────────┴──────────┴───────────────┘
```

**For Pro/Premium users:**
- "Manage Subscription" section at bottom
- "Open Customer Portal" button
- Opens Stripe customer portal in new window

---

### 2. **Style Persona Page** (`/style-persona`)

**Free Tier Users Will See:**
```
┌─────────────────────────────────────┐
│  🔒 Style Persona Analysis          │
│                                     │
│  Requires Pro Subscription          │
│                                     │
│  What you'll get:                   │
│  ✓ Deep style profiling            │
│  ✓ AI-powered style analysis       │
│  ✓ Personal style recommendations  │
│  ✓ Style evolution tracking        │
│                                     │
│  [Upgrade to Pro]                   │
│                                     │
│  You're currently on Free plan      │
└─────────────────────────────────────┘
```

**Pro/Premium Users Will See:**
- Full style persona analysis (existing content)
- AI-powered style insights
- Style evolution tracking

---

### 3. **Profile Page** (`/profile`)

**What to add:**
- Subscription status card showing:
  - Current tier
  - Flat lays remaining
  - Link to subscription page

---

### 4. **Subscription Success Page** (`/subscription-success`)

**What it shows:**
- ✅ Checkmark icon
- "Payment Successful!" message
- "Your subscription has been activated"
- Two buttons:
  - "View Subscription" → Goes to `/subscription`
  - "Start Generating Outfits" → Goes to `/outfits`

**When you see it:**
- After completing Stripe checkout
- Automatically redirected here by Stripe
- Shows session ID in URL: `?session_id=cs_...`

---

### 5. **Navigation Updates** (Optional - to add)

You can add a subscription indicator in navigation:
- Show current tier badge
- Link to subscription page
- Show flat lays remaining

---

## User Experience Flow

### **Free Tier User Journey:**

1. **Visit Style Persona Page**
   ```
   User → /style-persona
   → Sees upgrade prompt
   → Clicks "Upgrade to Pro"
   → Redirects to /subscription
   ```

2. **Subscription Page**
   ```
   User → /subscription
   → Sees 3 tier cards
   → Sees "Current Plan: Free • 1 flat lay remaining"
   → Clicks "Upgrade" on Pro card
   → Redirects to Stripe checkout
   ```

3. **Stripe Checkout**
   ```
   User → Stripe hosted checkout page
   → Enters payment info
   → Completes payment
   → Redirects to /subscription-success
   ```

4. **Success Page**
   ```
   User → /subscription-success?session_id=cs_...
   → Sees success message
   → Clicks "Start Generating Outfits"
   → Now has access to premium features
   ```

5. **Return to Style Persona**
   ```
   User → /style-persona
   → Now sees full analysis (no upgrade prompt)
   → Can use all features
   ```

---

## Visual States

### **Subscription Page States:**

**Loading State:**
```
┌─────────────────┐
│   [Spinner]     │
│   Loading...    │
└─────────────────┘
```

**Loaded State:**
```
┌─────────────────────────────────────┐
│ Subscription Plans                  │
│ Current Plan: Free • 1 remaining   │
│                                     │
│ [Free] [Pro] [Premium]             │
│                                     │
│ [Current] [Upgrade] [Upgrade]      │
└─────────────────────────────────────┘
```

**Error State:**
```
┌─────────────────────────────────────┐
│ ⚠️ Failed to load subscription     │
│ Error message here                  │
└─────────────────────────────────────┘
```

**Upgrading State:**
```
┌─────────────────────────────────────┐
│ [Processing...]                     │
│ Button shows spinner                │
└─────────────────────────────────────┘
```

---

## What Users Should See Now

### ✅ **Immediately Available (No Stripe Needed):**

1. **Subscription Page** (`/subscription`)
   - Shows current subscription tier
   - Shows flat lays remaining
   - Shows upgrade buttons (will fail gracefully if Stripe not configured)

2. **Style Persona Paywall** (`/style-persona`)
   - Free users see upgrade prompt
   - Pro/Premium users see full features

3. **Current Subscription Status**
   - Fetched from backend
   - Shows tier and quota info

### ⚠️ **Requires Stripe Configuration:**

1. **Upgrade Buttons**
   - Clicking shows error if Stripe not configured
   - Will work once Stripe is set up

2. **Customer Portal**
   - Manages subscription, payment methods
   - Requires Stripe setup

---

## Testing Checklist

### Test as Free User:

- [ ] Go to `/subscription` → See Free plan highlighted
- [ ] Go to `/style-persona` → See upgrade prompt
- [ ] Click "Upgrade to Pro" → Redirects to subscription page
- [ ] Click "Upgrade" button → Should show error (Stripe not configured yet)

### Test as Pro User:

- [ ] Go to `/subscription` → See Pro plan highlighted
- [ ] Go to `/style-persona` → See full analysis (no prompt)
- [ ] See "Manage Subscription" section
- [ ] Click "Open Customer Portal" → Should open Stripe portal

### Test Payment Flow (After Stripe Setup):

- [ ] Click "Upgrade" → Redirects to Stripe checkout
- [ ] Complete payment → Redirects to `/subscription-success`
- [ ] See success message
- [ ] Verify subscription updated in Firestore

---

## Quick Test Right Now

1. **Open your app**: https://easyoutfitapp.com

2. **Navigate to `/subscription`** (or `/upgrade`)
   - You should see the subscription page
   - Your current tier displayed
   - Flat lays remaining shown

3. **Navigate to `/style-persona`**
   - If Free tier: See upgrade prompt
   - If Pro/Premium: See full features

4. **Try clicking "Upgrade"**
   - Should show error (Stripe not configured)
   - Error message will say "Payment processing not configured"

This confirms:
- ✅ Frontend is connected to backend
- ✅ Subscription status is being fetched
- ✅ Paywall is working
- ✅ Ready for Stripe configuration

---

## Next Steps

1. **Set up Stripe** (see `STRIPE_SETUP.md`)
2. **Add environment variables** to Railway
3. **Test full payment flow**
4. **Verify webhooks** are working

---

**All UI components are ready and deployed!** 🎉

