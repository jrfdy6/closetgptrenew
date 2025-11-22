# Stripe Quick Start - Copy & Paste Checklist

## ✅ Step-by-Step Checklist

### 1. Create Stripe Account
- [ ] Go to https://stripe.com and sign up
- [ ] Verify email
- [ ] You're now in **Test Mode** (free!)

### 2. Get API Keys
- [ ] Go to **Developers** → **API keys**
- [ ] Click **"Reveal test key"** for Secret key
- [ ] Copy: `sk_test_...` ← **Save this!**

### 3. Create Products
- [ ] **Products** → **Add product**
- [ ] Name: `Pro Subscription`
- [ ] Price: `9.99` USD, Monthly recurring
- [ ] Copy Price ID: `price_...` ← **Save this!**
- [ ] Repeat for `Premium Subscription` ($29.99)
- [ ] Copy Price ID: `price_...` ← **Save this!**

### 4. Set Up Webhook
- [ ] **Developers** → **Webhooks** → **Add endpoint**
- [ ] URL: `https://closetgptrenew-production.up.railway.app/api/payments/webhook`
- [ ] Select events:
  - ✅ `checkout.session.completed`
  - ✅ `customer.subscription.created`
  - ✅ `customer.subscription.updated`
  - ✅ `customer.subscription.deleted`
  - ✅ `invoice.payment_succeeded`
  - ✅ `invoice.payment_failed`
- [ ] Copy Signing secret: `whsec_...` ← **Save this!**

### 5. Add to Railway
- [ ] Go to Railway → Your backend service → **Variables**
- [ ] Add these 5 variables:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_TIER2=price_...
STRIPE_PRICE_TIER3=price_...
FRONTEND_URL=https://easyoutfitapp.com
```

*(Replace `...` with your actual values)*

### 6. Test It!
- [ ] Visit: `/subscription` page
- [ ] Click "Upgrade to Pro"
- [ ] Use test card: `4242 4242 4242 4242`
- [ ] Expiry: `12/25`, CVC: `123`, ZIP: `12345`
- [ ] Complete checkout
- [ ] ✅ Should redirect to success page!

---

## 🎯 What You Need (Copy These)

After setup, you'll have:

1. **Secret Key**: `sk_test_51...` (from Step 2)
2. **Webhook Secret**: `whsec_...` (from Step 4)
3. **Pro Price ID**: `price_1...` (from Step 3)
4. **Premium Price ID**: `price_1...` (from Step 3)
5. **Frontend URL**: Your Vercel URL or `https://easyoutfitapp.com`

---

## 🧪 Test Cards

| Card Number | Result |
|------------|--------|
| `4242 4242 4242 4242` | ✅ Success |
| `4000 0025 0000 3155` | ⚠️ Requires authentication |
| `4000 0000 0000 0002` | ❌ Declined |

Use any future expiry date, any CVC, any ZIP.

---

## 📍 Important URLs

- **Backend**: `https://closetgptrenew-production.up.railway.app`
- **Webhook**: `https://closetgptrenew-production.up.railway.app/api/payments/webhook`
- **Frontend**: Your Vercel URL (check Vercel dashboard)

---

## ❓ Need Help?

See `STRIPE_SETUP_GUIDE.md` for detailed instructions with screenshots and troubleshooting.

