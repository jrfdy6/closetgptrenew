# How to Get Stripe Variables for Railway

## 🎯 Step-by-Step: Getting Each Variable

---

## Step 1: Get Your Stripe Secret Key

1. **Go to Stripe Dashboard**: https://dashboard.stripe.com
2. **Click "Developers"** in the left sidebar
3. **Click "API keys"** (under Developers)
4. You'll see two keys:
   - **Publishable key** (starts with `pk_test_...`) - Don't need this
   - **Secret key** (starts with `sk_test_...`) - **This is what you need!**
5. **Click "Reveal test key"** button next to Secret key
6. **Copy the entire key** - it looks like: `sk_test_51AbC123xyz...`

✅ **This is your `STRIPE_SECRET_KEY`**

---

## Step 2: Create Products and Get Price IDs

### Create Pro Subscription Product

1. **Go to "Products"** in the left sidebar
2. **Click "+ Add product"** button
3. Fill in:
   - **Name**: `Pro Subscription`
   - **Description**: `Pro tier subscription - 7 flat lays per week`
4. Under **"Pricing"** section:
   - Click **"Add pricing"**
   - **Price**: `9.99`
   - **Currency**: `USD` (United States Dollar)
   - **Billing period**: Select **"Monthly"** (recurring)
5. Click **"Save product"** button
6. After saving, you'll see the product page
7. **Look for "Price ID"** - it starts with `price_...`
8. **Copy the Price ID** - it looks like: `price_1AbC123xyz...`

✅ **This is your `STRIPE_PRICE_TIER2`**

### Create Premium Subscription Product

1. **Click "Products"** again
2. **Click "+ Add product"** button
3. Fill in:
   - **Name**: `Premium Subscription`
   - **Description**: `Premium tier subscription - 30 flat lays per week`
4. Under **"Pricing"** section:
   - Click **"Add pricing"**
   - **Price**: `29.99`
   - **Currency**: `USD`
   - **Billing period**: Select **"Monthly"** (recurring)
5. Click **"Save product"** button
6. **Copy the Price ID** - it starts with `price_...`

✅ **This is your `STRIPE_PRICE_TIER3`**

---

## Step 3: Set Up Webhook and Get Webhook Secret

1. **Go to "Developers"** in the left sidebar
2. **Click "Webhooks"** (under Developers)
3. **Click "+ Add endpoint"** button
4. Fill in:
   - **Endpoint URL**: 
     ```
     https://closetgptrenew-production.up.railway.app/api/payments/webhook
     ```
   - **Description**: `Easy Outfit App Subscription Webhooks`
5. Under **"Events to send"**, click **"Select events"**
6. Check these 6 events:
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
   - ✅ `invoice.payment_succeeded`
   - ✅ `invoice.payment_failed`
7. Click **"Add endpoint"** button
8. After creating, you'll see the webhook details page
9. **Look for "Signing secret"** - it starts with `whsec_...`
10. **Click "Reveal"** or **"Click to reveal"** button
11. **Copy the Signing secret** - it looks like: `whsec_AbC123xyz...`

✅ **This is your `STRIPE_WEBHOOK_SECRET`**

---

## Step 4: Get Your Frontend URL

You need to know your frontend URL. Check one of these:

### Option A: Check Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Find your project
3. Click on it
4. Look for the **"Visit"** button or **"Domains"** section
5. Your URL will be something like:
   - `https://easyoutfitapp.vercel.app`
   - `https://easyoutfit-frontend.vercel.app`
   - Or your custom domain

### Option B: Use Default
If you're not sure, use:
```
https://easyoutfitapp.com
```

✅ **This is your `FRONTEND_URL`**

---

## Step 5: Add Variables to Railway

Now that you have all the values, add them to Railway:

1. **Go to Railway**: https://railway.app
2. **Select your project** (closetgptrenew)
3. **Click on your backend service** (should be the one running FastAPI)
4. **Click on the "Variables" tab** (at the top)
5. **Click "+ New Variable"** button

### Add Each Variable One by One:

#### Variable 1: STRIPE_SECRET_KEY
- **Name**: `STRIPE_SECRET_KEY`
- **Value**: Paste your secret key from Step 1 (starts with `sk_test_...`)
- Click **"Add"**

#### Variable 2: STRIPE_WEBHOOK_SECRET
- **Name**: `STRIPE_WEBHOOK_SECRET`
- **Value**: Paste your webhook secret from Step 3 (starts with `whsec_...`)
- Click **"Add"**

#### Variable 3: STRIPE_PRICE_TIER2
- **Name**: `STRIPE_PRICE_TIER2`
- **Value**: Paste your Pro price ID from Step 2 (starts with `price_...`)
- Click **"Add"**

#### Variable 4: STRIPE_PRICE_TIER3
- **Name**: `STRIPE_PRICE_TIER3`
- **Value**: Paste your Premium price ID from Step 2 (starts with `price_...`)
- Click **"Add"**

#### Variable 5: FRONTEND_URL
- **Name**: `FRONTEND_URL`
- **Value**: Your frontend URL from Step 4 (e.g., `https://easyoutfitapp.com`)
- Click **"Add"**

---

## ✅ Verification Checklist

After adding all variables, you should have 5 variables in Railway:

- [ ] `STRIPE_SECRET_KEY` = `sk_test_...`
- [ ] `STRIPE_WEBHOOK_SECRET` = `whsec_...`
- [ ] `STRIPE_PRICE_TIER2` = `price_...`
- [ ] `STRIPE_PRICE_TIER3` = `price_...`
- [ ] `FRONTEND_URL` = `https://...`

---

## 🚀 After Adding Variables

Railway will automatically redeploy your service. You can:

1. **Check deployment status** in Railway dashboard
2. **View logs** to see if everything loaded correctly
3. **Test the integration** by visiting `/subscription` page

---

## 📋 Quick Reference: Where to Find Each Variable

| Variable | Where to Find | What It Looks Like |
|----------|--------------|-------------------|
| `STRIPE_SECRET_KEY` | Developers → API keys → Secret key | `sk_test_51...` |
| `STRIPE_WEBHOOK_SECRET` | Developers → Webhooks → [endpoint] → Signing secret | `whsec_...` |
| `STRIPE_PRICE_TIER2` | Products → Pro Subscription → Price ID | `price_1...` |
| `STRIPE_PRICE_TIER3` | Products → Premium Subscription → Price ID | `price_1...` |
| `FRONTEND_URL` | Vercel dashboard or your domain | `https://...` |

---

## 🎯 Example Values (Test Mode)

Here's what your variables should look like (yours will be different):

```bash
STRIPE_SECRET_KEY=sk_test_51AbC123xyz789...
STRIPE_WEBHOOK_SECRET=whsec_AbC123xyz789...
STRIPE_PRICE_TIER2=price_1AbC123xyz789...
STRIPE_PRICE_TIER3=price_1XyZ789abc123...
FRONTEND_URL=https://easyoutfitapp.com
```

**Note**: These are example formats. Your actual values will be different!

---

## ❓ Troubleshooting

### Can't find Secret Key?
- Make sure you're in **Test Mode** (toggle in top right of Stripe dashboard)
- Click **"Reveal test key"** button

### Can't find Price ID?
- Go to Products → Click on your product
- Look for "Price ID" under the pricing section
- It's usually right below the price amount

### Can't find Webhook Secret?
- Make sure you created the webhook endpoint first
- Click on the webhook endpoint to see details
- Click "Reveal" button next to Signing secret

### Railway not redeploying?
- After adding variables, Railway should auto-redeploy
- Check the "Deployments" tab to see status
- You can manually trigger a redeploy if needed

---

## ✅ You're Done!

Once all 5 variables are added to Railway, your Stripe integration is ready to use!

Test it by visiting `/subscription` page and trying to upgrade with test card `4242 4242 4242 4242`.

