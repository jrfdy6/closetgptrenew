# 🚀 Railway One-Time Backfill Deployment

## Overview
This guide shows how to deploy and run the database backfill as a one-time job on Railway.

## 📋 Step 1: Deploy the Backfill Job

### In Railway Dashboard:
1. **Go to your project** (`closetgptrenew-backend`)
2. **Click "New Service"** or **"Deploy from GitHub"**
3. **Select your repository** (`closetgptrenew`)
4. **Configure the service:**
   - **Name**: `backfill-job`
   - **Root Directory**: `/` (root)
   - **Build Command**: (leave empty)
   - **Start Command**: `python3 railway_backfill_job.py`

### Environment Variables:
Add these environment variables in Railway:
```
BACKFILL_DRY_RUN=true
```

## 📋 Step 2: Run Dry Run

### Deploy and Monitor:
1. **Deploy the service** - it will automatically start
2. **Go to the "Logs" tab** to watch the output
3. **Wait for completion** (should take 5-10 minutes)

### Expected Output:
```
🎯 Railway Backfill Job Starting...
🔍 Running in DRY RUN mode (no database changes)
✅ Firebase initialized successfully
🚀 Starting wardrobe backfill [DRY RUN]

📦 Processing batch 1...
   Batch 1: 500 processed, 0 updated, 15 skipped, 0 errors

📦 Processing batch 2...
   Batch 2: 500 processed, 0 updated, 8 skipped, 0 errors

📊 Progress: 1000 items processed so far
...

======================================================================
📊 BACKFILL COMPLETE - FINAL STATISTICS
======================================================================
⏱️  Duration: 0:05:23
📦 Total processed: 3421
✅ Total updated: 0 (dry run)
⏭️  Total skipped: 123
❌ Total errors: 0
📈 Success rate: 100.0%
======================================================================
✅ Backfill job completed successfully!
```

## 📋 Step 3: Run Production Backfill

### If Dry Run Looks Good:
1. **Update environment variable:**
   ```
   BACKFILL_DRY_RUN=false
   ```
2. **Redeploy the service** (or restart)
3. **Monitor logs** for the actual backfill

### Expected Output:
```
🎯 Railway Backfill Job Starting...
⚠️  Running in PRODUCTION mode (will modify database)
✅ Firebase initialized successfully
🚀 Starting wardrobe backfill [PRODUCTION]

📦 Processing batch 1...
   Batch 1: 500 processed, 485 updated, 15 skipped, 0 errors

📦 Processing batch 2...
   Batch 2: 500 processed, 492 updated, 8 skipped, 0 errors

📊 Progress: 1000 items processed so far
...

======================================================================
📊 BACKFILL COMPLETE - FINAL STATISTICS
======================================================================
⏱️  Duration: 0:05:23
📦 Total processed: 3421
✅ Total updated: 3298
⏭️  Total skipped: 123
❌ Total errors: 0
📈 Success rate: 96.4%
======================================================================
✅ Backfill job completed successfully!
```

## 📋 Step 4: Clean Up

### After Successful Backfill:
1. **Delete the backfill service** (it's no longer needed)
2. **Or set it to sleep** to save resources

## 🚨 Troubleshooting

### If the job fails:
1. **Check the logs** for error messages
2. **Verify Firebase credentials** are properly set
3. **Check if the service has proper permissions**

### Common Issues:
- **Firebase connection errors**: Check environment variables
- **Permission errors**: Ensure service has Firestore write access
- **Memory issues**: Railway may need more resources for large datasets

## ✅ Success Criteria

The backfill is successful when:
- ✅ **No errors** in the logs
- ✅ **High success rate** (>95%)
- ✅ **All items processed** (matches expected wardrobe size)
- ✅ **Normalized fields added** to items

## 📊 Next Steps

After successful backfill:
1. ✅ **Enable semantic filtering** feature flags
2. ✅ **Test semantic matching** in personalization demo
3. ✅ **Monitor metrics** for 24-48 hours
4. ✅ **Begin canary release** (5% of users)

---

## 🎯 Quick Commands Summary

**Deploy Dry Run:**
- Environment: `BACKFILL_DRY_RUN=true`
- Start Command: `python3 railway_backfill_job.py`

**Deploy Production:**
- Environment: `BACKFILL_DRY_RUN=false`
- Start Command: `python3 railway_backfill_job.py`

**Monitor:**
- Watch the "Logs" tab in Railway dashboard

Ready to deploy! 🚀
