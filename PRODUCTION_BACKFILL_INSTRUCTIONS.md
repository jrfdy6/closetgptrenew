# Production Database Backfill - Step-by-Step Instructions

## 🎯 Overview
This guide walks you through executing the production database backfill to normalize existing wardrobe items for semantic filtering.

## ⚠️ Prerequisites
- Access to Railway production console
- Backend deployment is healthy
- Low traffic period (recommended)

## 📋 Step 1: Dry Run (Read-Only Test)

### Access Railway Console
1. Go to [Railway Dashboard](https://railway.app/)
2. Select your `closetgptrenew-backend-production` project
3. Click on the backend service
4. Open the **"Console"** tab (or Shell)

### Run Dry Run Command
```bash
python3 run_backfill_production.py --dry-run --environment production
```

### Expected Output
```
Environment: production
🚀 Starting wardrobe backfill [DRY RUN]
   Batch size: 500

📦 Processing batch 1...
🔍 DRY RUN: Would update [item_id]
   Normalized: {
     "style": ["casual", "classic"],
     "occasion": ["everyday"],
     "mood": ["relaxed"],
     "season": ["all"],
     "normalized_at": "2025-10-07T...",
     "normalized_version": "1.0"
   }
...
📊 Progress: 500 items processed so far
...
======================================================================
📊 BACKFILL COMPLETE - FINAL STATISTICS
======================================================================
⏱️  Duration: 0:00:XX
📦 Total processed: XXXX
✅ Total updated: 0 (dry run)
⏭️  Total skipped: XX
❌ Total errors: 0
📈 Success rate: 100.0%
======================================================================
```

### ✅ Validation Checklist
- [ ] No errors in output
- [ ] Total processed matches expected wardrobe size
- [ ] Normalized data looks correct (lowercase, proper format)
- [ ] All batches processed successfully

---

## 📋 Step 2: Full Production Backfill

⚠️ **IMPORTANT**: Only proceed if dry run completed successfully!

### Run Full Backfill
```bash
python3 run_backfill_production.py --environment production
```

### Safety Confirmation
You will be prompted:
```
⚠️  You are about to modify PRODUCTION data. Type 'YES' to continue:
```

**Type `YES` and press Enter to proceed.**

### Expected Output
```
Environment: production
🚀 Starting wardrobe backfill [PRODUCTION]
   Batch size: 500

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
💾 Stats saved to backfill_stats_20251007_XXXXXX.json
```

### 📊 Monitoring During Backfill
While the backfill is running:

1. **Monitor Railway Logs** - Watch for any errors
2. **Check Backend Health** - Ensure API is still responding
3. **Track Progress** - Note batch completion rate

---

## 📋 Step 3: Post-Backfill Validation

### Run Validation Script (Optional)
```bash
python3 scripts/backfill_validation.py --sample-size 100
```

### Manual Spot Check
1. Check a few wardrobe items in Firestore:
   ```
   Collection: wardrobe
   Random item -> Check for 'normalized' field
   ```

2. Verify normalized structure:
   ```json
   {
     "id": "item123",
     "name": "Classic Blazer",
     "style": ["Business", "Classic"],  // Original
     "normalized": {                     // New field
       "style": ["business", "classic"],
       "occasion": ["work", "formal"],
       "mood": ["professional"],
       "season": ["all"],
       "normalized_at": "2025-10-07T10:30:00Z",
       "normalized_version": "1.0"
     }
   }
   ```

### ✅ Validation Checklist
- [ ] `normalized` field exists on items
- [ ] All values are lowercase
- [ ] Arrays are properly formatted
- [ ] `normalized_at` timestamp present
- [ ] Original fields unchanged

---

## 📋 Step 4: Enable Semantic Filtering

### Update Feature Flags
In Railway environment variables:
```
FEATURE_SEMANTIC_MATCH=true
FEATURE_DEBUG_OUTPUT=true
```

### Test Semantic Filtering
1. Go to `/personalization-demo`
2. Toggle "Semantic Matching" ON
3. Generate outfits with different style preferences
4. Verify semantic matches work (e.g., "Classic" matches "Business Casual")

---

## 🚨 Rollback Procedure (If Needed)

### If Something Goes Wrong
```bash
python3 scripts/backfill_rollback.py --dry-run --environment production
```

Then if dry run looks good:
```bash
python3 scripts/backfill_rollback.py --environment production
```

This will remove the `normalized` field from all items.

### Disable Feature Flags
```
FEATURE_SEMANTIC_MATCH=false
```

---

## 📊 Success Metrics

After backfill completion, monitor:

1. **Filter Pass Rate**: Items passing semantic filtering
2. **Outfit Generation Success**: Outfits successfully generated
3. **User Feedback**: Any user-reported issues
4. **Performance**: API response times

### Expected Improvements
- ✅ More flexible style matching
- ✅ Better outfit variety
- ✅ Fewer "no outfits found" scenarios
- ✅ Improved personalization

---

## 📞 Support

If you encounter issues:
1. Check Railway logs for errors
2. Review `backfill_production.log` file
3. Run validation script to identify problem items
4. Use rollback procedure if necessary

---

## 📝 Notes

- **Batch Size**: 500 items per batch (configurable)
- **Processing Time**: ~1-2 seconds per batch
- **Total Duration**: Depends on wardrobe size (~5-10 minutes for 3000 items)
- **Safety**: Original fields are never modified
- **Idempotent**: Can be run multiple times safely (skips already normalized items)

---

## ✅ Next Steps After Successful Backfill

1. ✅ Monitor metrics for 24-48 hours
2. ✅ Begin canary release (5% of users)
3. ✅ Gradual rollout to 100% of users
4. ✅ Collect user feedback
5. ✅ Optimize semantic compatibility rules based on data

Good luck! 🚀

