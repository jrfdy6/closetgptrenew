# Background Image Processing Worker

This worker service runs alpha matting on uploaded wardrobe items in the background, providing "stealth mode" image upgrades.

## How It Works

1. **User uploads** wardrobe item → saved immediately with `processing_status: "pending"`
2. **Worker detects** pending item → downloads, processes with alpha matting
3. **Worker uploads** clean PNG → updates Firestore with `backgroundRemovedUrl`
4. **Frontend auto-swaps** to clean image when ready (no user action needed)

## Deployment on Railway

### Option 1: Add as New Service (Recommended)

1. In Railway dashboard, click **"New Service"**
2. Select **"Deploy from GitHub repo"**
3. Choose this repo
4. Set **Root Directory**: `backend/worker`
5. Railway will auto-detect Python and install requirements
6. Add environment variables (same as main backend):
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_PRIVATE_KEY`
   - `FIREBASE_CLIENT_EMAIL`
   - All other Firebase credentials

### Option 2: Manual Start Command

If Railway doesn't auto-start, set:
```
Start Command: python main.py
```

## Environment Variables Needed

The worker needs the **same Firebase credentials** as your main backend:

```
FIREBASE_PROJECT_ID=closetgptrenew
FIREBASE_PRIVATE_KEY=(from Railway)
FIREBASE_CLIENT_EMAIL=(from Railway)
FIREBASE_CLIENT_ID=(from Railway)
FIREBASE_CLIENT_X509_CERT_URL=(from Railway)
FIREBASE_PRIVATE_KEY_ID=(from Railway)
```

## Monitoring

The worker logs to stdout. Check Railway logs for:

```
🔥 Worker started. Listening for new images...
📸 Processing abc-123...
  🎨 Running alpha matting...
  ✅ Background removed with alpha matting
✅ COMPLETE: abc-123 - Image auto-upgraded in UI
```

## Performance

- **Processing time**: 5-10 seconds per item (alpha matting)
- **Batch size**: 3 items at a time
- **Polling interval**: 5 seconds when idle
- **Memory**: ~500MB (loads rembg + PyMatting models)

## Frontend Integration

No changes needed! Frontend already uses:

```typescript
const imageSrc = item.backgroundRemovedUrl ?? item.imageUrl;
```

When worker finishes, Firestore updates trigger automatic UI refresh.

## Scaling

- **Current**: Single worker processes items sequentially
- **Future**: Add Redis queue + multiple workers for parallel processing
- **Load**: Handles ~10-20 uploads/minute comfortably

## Troubleshooting

### Worker not processing items

1. Check Railway logs for startup errors
2. Verify Firebase credentials are set
3. Check Firestore has items with `processing_status: "pending"`

### Items stuck in "pending"

1. Check worker logs for errors
2. Verify image URLs are accessible
3. Check Railway memory limits (alpha matting needs ~500MB)

### Worker crashes/restarts

- Alpha matting is memory-intensive
- Upgrade Railway plan if OOM errors occur
- Or disable alpha matting (use fast mode) in `main.py`

## Local Development

```bash
cd backend/worker
pip install -r requirements.txt

# Set Firebase credentials
export FIREBASE_PROJECT_ID=closetgptrenew
# ... other env vars

python main.py
```

