# Flatlay Workflow - How It Works

## Current Workflow

1. **User generates outfit** → Outfit saved with `flat_lay_status: 'awaiting_consent'`
2. **User clicks "Create flat lay"** → Frontend updates Firestore:
   - `flat_lay_status: 'pending'`
   - `flatLayStatus: 'pending'`
   - `metadata.flat_lay_status: 'pending'`
   - `metadata.flatLayStatus: 'pending'`
3. **Background Processor polls** every 5 seconds for outfits with `flat_lay_status: 'pending'`
4. **Worker processes flatlay** → Generates using OpenAI
5. **Worker updates Firestore** with:
   - `flat_lay_status: 'done'`
   - `flat_lay_url: <url>`
6. **Frontend listener** detects change → Displays flatlay automatically

## Verify Your Background Processor Service

### Step 1: Check if Service is Running
1. Go to Railway Dashboard → Your project
2. Find your "background processor" service
3. Check the **Logs** tab

### Step 2: Look for These Log Messages

**When service starts:**
```
🔥 Worker started. Listening for new images...
📊 Configuration:
   Firebase Project: closetgptrenew
   Collection: wardrobe
   Poll interval: 5s
```

**When it finds a flatlay to process:**
```
🎨 Found 1 outfits needing flat lays
🎨 Processing flatlay for outfit outfit_xxx...
```

**When processing completes:**
```
✅ Flatlay processing completed for outfit outfit_xxx
🎨 Outfit outfit_xxx: OpenAI flat lay ready (https://...)
```

### Step 3: Check Environment Variables

Your background processor service needs:
- ✅ All Firebase credentials (same as main app)
- ✅ `OPENAI_API_KEY` (REQUIRED for flatlay generation)

### Step 4: Test the Workflow

1. Generate an outfit
2. Click "Create flat lay"
3. Check Firestore - outfit should have `flat_lay_status: 'pending'`
4. Check background processor logs - should see "🎨 Found 1 outfits needing flat lays"
5. Wait 30-60 seconds
6. Check Firestore again - should have `flat_lay_status: 'done'` and `flat_lay_url`

## Troubleshooting

### If flatlays aren't being processed:

1. **Check if service is running**
   - Go to Railway → Your background processor service
   - Check if it's "Active" and not crashed

2. **Check logs for errors**
   - Look for "Failed to import" errors
   - Look for Firebase connection errors
   - Look for OpenAI API errors

3. **Verify environment variables**
   - `OPENAI_API_KEY` must be set
   - All Firebase credentials must match main app

4. **Check Firestore directly**
   - Go to Firebase Console → Firestore
   - Find your outfit document
   - Verify `flat_lay_status` is set to `'pending'` after you click the button

5. **Check worker is polling**
   - Look for "💤 No pending tasks" messages in logs
   - This means worker is running but not finding pending items
   - If you don't see this, worker might not be running

## Common Issues

### Issue: Worker not finding outfits
- **Cause**: Worker query might not match the field names
- **Fix**: Worker checks multiple field variations (`flat_lay_status`, `flatLayStatus`, `metadata.flat_lay_status`)

### Issue: Worker crashes on startup
- **Cause**: Missing dependencies or environment variables
- **Fix**: Check logs for import errors, verify all env vars are set

### Issue: OpenAI quota exhausted
- **Cause**: Weekly limit reached
- **Fix**: Check user's `openai_flatlays_used` vs their tier limit
- **Note**: Quota resets weekly based on `flatlay_week_start`

### Issue: Flatlay generated but not showing
- **Cause**: Frontend listener not picking up changes
- **Fix**: Check browser console for Firestore listener errors
- **Verify**: Outfit document in Firestore has `flat_lay_url` set

