# Fix Customer Portal 500 Error

## Problem
Getting a 500 error when trying to access the Customer Portal, seeing a Stripe billing portal login URL instead.

## Root Causes

1. **Customer Portal not activated in Live mode**
2. **FRONTEND_URL not set correctly in Railway**
3. **Stripe customer ID missing for the user**

---

## Solution Step-by-Step

### Step 1: Verify FRONTEND_URL in Railway

1. **Go to Railway Dashboard**: https://railway.app
2. **Select your backend service** (closetgpt-backend)
3. **Click "Variables" tab**
4. **Check if `FRONTEND_URL` exists**:
   - If it doesn't exist, **add it**
   - If it exists, **verify the value is correct**

**Correct value should be**:
```
FRONTEND_URL=https://easyoutfitapp.com
```

**Or your actual production domain** (check Vercel dashboard for your domain).

5. **Save the variable**
6. **Wait for Railway to redeploy** (1-2 minutes)

---

### Step 2: Verify Customer Portal is Activated in Live Mode

1. **Go to Stripe Dashboard** (make sure you're in **Live mode**)
2. **Click "Settings"** → **"Billing"** → **"Customer portal"**
3. **Verify**:
   - ✅ **"Activate live link"** is toggled ON
   - ✅ Portal is configured
   - ✅ Return URL is set (optional, but recommended)

**If not activated**:
1. **Click "Activate live link"** or toggle it ON
2. **Configure settings**:
   - Allow subscription cancellation
   - Allow payment method updates
3. **Click "Save"**

---

### Step 3: Check if User Has Stripe Customer ID

The error might occur if the user doesn't have a Stripe customer ID yet. This happens if:
- User hasn't subscribed yet
- Customer wasn't created during checkout

**To check**:
1. **Go to Stripe Dashboard** → **"Customers"**
2. **Search for the user's email**
3. **If customer doesn't exist**, they need to:
   - Go through checkout first (this creates the customer)
   - Then they can access the Customer Portal

**The Customer Portal requires a Stripe customer ID to work.**

---

### Step 4: Test the Fix

1. **Wait for Railway to redeploy** (after updating FRONTEND_URL)
2. **Go to your website**: https://easyoutfitapp.com
3. **Log in**
4. **Go to Subscription page**
5. **Click "Manage Subscription"** or "Open Customer Portal"
6. **Should redirect to Stripe Customer Portal** (not show 500 error)

---

## Common Issues

### Issue 1: "No Stripe customer found"
**Error**: `No Stripe customer found. Please subscribe first.`

**Solution**: User must subscribe first. The Customer Portal only works for users who have an active subscription or have gone through checkout.

### Issue 2: Wrong FRONTEND_URL
**Error**: Portal redirects to wrong URL or shows 500 error.

**Solution**: 
1. Check Railway variables
2. Make sure `FRONTEND_URL` matches your actual production domain
3. Redeploy backend

### Issue 3: Customer Portal not activated
**Error**: 500 error or "Portal not available"

**Solution**: 
1. Go to Stripe Dashboard → Settings → Billing → Customer portal
2. Make sure you're in **Live mode**
3. Activate the live link

---

## Quick Checklist

- [ ] `FRONTEND_URL` is set in Railway
- [ ] `FRONTEND_URL` value is correct (your production domain)
- [ ] Customer Portal is activated in Stripe **Live mode**
- [ ] User has a Stripe customer ID (has subscribed or gone through checkout)
- [ ] Railway has redeployed after variable changes

---

## Verify Your Frontend URL

**To find your actual frontend URL**:

1. **Check Vercel Dashboard**:
   - Go to https://vercel.com/dashboard
   - Select your project
   - Look at "Domains" or "Production" URL
   - Example: `https://easyoutfitapp.vercel.app` or `https://easyoutfitapp.com`

2. **Use that URL** as your `FRONTEND_URL` in Railway

---

## Still Getting 500 Error?

**Check Railway logs**:
1. Go to Railway Dashboard → Your backend service
2. Click "Logs" tab
3. Look for error messages when trying to create portal session
4. Common errors:
   - `Invalid return_url` → FRONTEND_URL is wrong
   - `Customer not found` → User needs to subscribe first
   - `Portal not configured` → Activate Customer Portal in Stripe

**Share the error message** and I can help debug further!


