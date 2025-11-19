# 🚀 Deploying the Background Worker Service

## Problem
Flatlays are not being generated because the worker service that processes them is not running.

## Solution
Deploy the worker as a separate Railway service.

## Quick Deploy Steps

### 1. In Railway Dashboard
1. Go to your project: `closetgptrenew`
2. Click **"New Service"** → **"Deploy from GitHub repo"**
3. Select your repository: `closetgptrenew`
4. Configure:
   - **Name**: `flatlay-worker` (or any name you prefer)
   - **Root Directory**: `backend/worker`
   - **Start Command**: `python main.py`

### 2. Environment Variables
Add the same Firebase credentials as your main app:
- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_CLIENT_ID`
- `FIREBASE_CLIENT_X509_CERT_URL`
- `FIREBASE_PRIVATE_KEY_ID`
- `OPENAI_API_KEY` (for OpenAI flatlay generation)

### 3. Deploy
Click **"Deploy"** and wait for the service to start.

### 4. Verify
Check the logs - you should see:
```
🔥 Worker started. Listening for new images...
📊 Configuration:
   Firebase Project: closetgptrenew
   Collection: wardrobe
   Poll interval: 5s
```

## How It Works

1. User requests flatlay → Frontend sets `flat_lay_status: 'pending'` in Firestore
2. Worker polls every 5 seconds for outfits with `flat_lay_status: 'pending'`
3. Worker processes the flatlay → Updates Firestore with `flat_lay_status: 'done'` and `flat_lay_url`
4. Frontend listener picks up the change → Displays the flatlay

## Troubleshooting

### Worker not finding outfits
- Check that outfits have `flat_lay_status: 'pending'` in Firestore
- Verify the worker has access to the `outfits` collection

### Worker crashes
- Check Railway logs for errors
- Verify all environment variables are set
- Check memory limits (flatlay processing needs ~500MB)

### Flatlays not appearing
- Check worker logs for processing errors
- Verify Firebase credentials are correct
- Check that image URLs are accessible

