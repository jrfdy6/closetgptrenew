# 🚀 Background Processor Service - Flatlay Processing

## Overview
Your **Background Processor** service (also called "background processor") already handles flatlay generation! The worker code at `backend/worker/main.py` processes both:
- Wardrobe image background removal
- **OpenAI flatlay generation for outfits**

## Current Status
The worker is already configured to process flatlays. It polls Firestore every 5 seconds for outfits with `flat_lay_status: 'pending'` and generates flatlays using OpenAI.

## How It Works

1. **User requests flatlay** → Frontend sets `flat_lay_status: 'pending'` in Firestore
2. **Worker polls** every 5 seconds for outfits with `flat_lay_status: 'pending'`
3. **Worker processes** the flatlay using OpenAI → Updates Firestore with `flat_lay_status: 'done'` and `flat_lay_url`
4. **Frontend listener** picks up the change → Displays the flatlay automatically

## Verify Your Background Processor Service

### Check if it's running:
1. Go to Railway Dashboard → Your project
2. Look for a service named "background processor" or similar
3. Check the **Logs** tab

### Expected logs when working:
```
🔥 Worker started. Listening for new images...
📊 Configuration:
   Firebase Project: closetgptrenew
   Collection: wardrobe
   Poll interval: 5s
🎨 Found 1 outfits needing flat lays
🎨 Processing flatlay for outfit outfit_xxx...
✅ Flatlay processing completed
```

### If the service exists but isn't processing flatlays:

1. **Check environment variables** - Make sure these are set:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_PRIVATE_KEY`
   - `FIREBASE_CLIENT_EMAIL`
   - `FIREBASE_CLIENT_ID`
   - `FIREBASE_CLIENT_X509_CERT_URL`
   - `FIREBASE_PRIVATE_KEY_ID`
   - `OPENAI_API_KEY` (required for flatlay generation)

2. **Check the service configuration**:
   - **Root Directory**: Should be `backend/worker` or root with proper path
   - **Start Command**: Should be `python main.py` or `cd backend/worker && python main.py`

3. **Check logs for errors**:
   - Look for "Failed to import" errors
   - Look for Firebase connection errors
   - Look for OpenAI API errors

## If You Need to Update/Reconfigure the Service

### Option 1: Update Existing Service
1. Go to Railway Dashboard → Your "background processor" service
2. Go to **Settings** → **Deploy**
3. Verify:
   - **Root Directory**: `backend/worker` (or root if using Dockerfile)
   - **Start Command**: `python main.py` (or let Dockerfile handle it)
4. **Redeploy** if needed

### Option 2: Use Dockerfile (Recommended)
If your service uses `railway.worker.toml`:
- The Dockerfile at `backend/Dockerfile.worker` is configured
- It will automatically install dependencies and run the worker

## Troubleshooting

### Worker not finding outfits
- Check that outfits have `flat_lay_status: 'pending'` in Firestore
- Verify the worker has access to the `outfits` collection
- Check worker logs for query errors

### Worker crashes
- Check Railway logs for errors
- Verify all environment variables are set (especially `OPENAI_API_KEY`)
- Check memory limits (flatlay processing needs ~500MB-1GB)

### Flatlays not appearing
- Check worker logs for processing errors
- Verify Firebase credentials are correct
- Check that image URLs are accessible
- Verify `OPENAI_API_KEY` is set and valid

### Worker not processing flatlays
- Check logs for "🎨 Found X outfits needing flat lays" - if you see this, it's finding them
- Check for "Failed to reserve OpenAI flat lay slot" - quota might be exhausted
- Check for OpenAI API errors in logs

