# Quick Production Test Guide

Test the payment system in production without needing Stripe configured yet.

## Option 1: Browser Console Test (Easiest)

1. **Open your app in production**: https://easyoutfitapp.com (or your production URL)

2. **Open browser console** (F12 or Cmd+Option+I)

3. **Get your Firebase token**:
   ```javascript
   // Paste this in console:
   const token = await firebase.auth().currentUser.getIdToken();
   console.log('Token:', token);
   // Copy the token
   ```

4. **Run the test script**:
   ```bash
   node test_payment_system.js YOUR_TOKEN_HERE
   ```

## Option 2: Manual API Testing

### Test 1: Check Current Subscription

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://closetgptrenew-production.up.railway.app/api/payments/subscription/current
```

**Expected Response:**
```json
{
  "role": "tier1",
  "status": "active",
  "flatlays_remaining": 1
}
```

### Test 2: Test Style Persona Paywall

```bash
# Create a test image file first
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > /tmp/test.png

# Test the endpoint
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@/tmp/test.png" \
     https://closetgptrenew-production.up.railway.app/api/style-analysis/analyze
```

**Expected Response (if Free tier):**
```json
{
  "detail": "This feature requires Pro or Premium subscription. You currently have Free."
}
```

**Status Code:** `403 Forbidden`

### Test 3: Test Health Check (No Auth Needed)

```bash
curl https://closetgptrenew-production.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "ok"
}
```

## Option 3: Shell Script Test

```bash
# Make script executable
chmod +x test_payment_system_production.sh

# Run with your Firebase token
./test_payment_system_production.sh YOUR_TOKEN_HERE

# Or test with test token (will show limitations)
./test_payment_system_production.sh test
```

## What to Test

### ✅ Should Work Without Stripe:
- [x] `/api/payments/subscription/current` - Get current subscription
- [x] `/api/style-analysis/*` - Should return 403 for Free tier users
- [x] Health check endpoint
- [x] Feature access checks

### ⚠️ Will Return 503 (Expected) Without Stripe:
- [ ] `/api/payments/checkout/create-session` - Needs `STRIPE_SECRET_KEY`
- [ ] `/api/payments/webhook` - Needs `STRIPE_WEBHOOK_SECRET`

## Expected Results

### Free Tier User (`tier1`):
- ✅ Can access `/api/payments/subscription/current`
- ❌ Gets 403 on `/api/style-analysis/analyze`
- ❌ Gets 403 on `/api/style-analysis/top-styles`
- ⚠️ Gets 503 on `/api/payments/checkout/create-session` (Stripe not configured)

### Pro/Premium User (`tier2` or `tier3`):
- ✅ Can access `/api/payments/subscription/current`
- ✅ Can access `/api/style-analysis/*` endpoints
- ⚠️ Gets 503 on `/api/payments/checkout/create-session` (Stripe not configured)

## Getting Your Firebase Token

### Method 1: Browser Console
```javascript
// On your production app page:
firebase.auth().currentUser.getIdToken().then(token => {
  console.log('Token:', token);
  // Copy this token
});
```

### Method 2: Network Tab
1. Open DevTools → Network tab
2. Make any authenticated request
3. Find the request with `Authorization: Bearer ...`
4. Copy the token from there

## Troubleshooting

### 401 Unauthorized
- Token expired - get a new one
- Token format wrong - should start with `eyJ...`

### 404 Not Found
- Routes not deployed yet - check Railway deployment
- URL might be wrong - verify production URL

### 403 Forbidden on Style Analysis
- ✅ **This is correct!** - Paywall is working
- User has Free tier and needs Pro/Premium

### 503 Service Unavailable on Checkout
- ✅ **This is expected** - Stripe not configured yet
- Need to set `STRIPE_SECRET_KEY` in Railway

## Next Steps After Testing

1. ✅ Verify paywall is working (style analysis blocked for Free tier)
2. ✅ Verify subscription endpoint returns user's current tier
3. 🔧 Set up Stripe (see `STRIPE_SETUP.md`)
4. 🔧 Configure environment variables in Railway
5. 🧪 Test Stripe checkout flow

