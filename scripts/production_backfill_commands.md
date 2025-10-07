# Production Database Backfill Commands

## 🚨 IMPORTANT: Production Backfill Instructions

### Step 1: Dry Run First (REQUIRED)
```bash
# Navigate to project root
cd /app

# Run dry run to see what will be changed
python3 scripts/backfill_normalize.py --dry-run --environment production
```

### Step 2: Monitor the Dry Run
```bash
# In another terminal, monitor the process
python3 scripts/backfill_monitor.py --watch --interval 30
```

### Step 3: Full Production Backfill (After Dry Run Success)
```bash
# Only run this after confirming dry run results
python3 scripts/backfill_normalize.py --environment production
```

### Step 4: Validate Results
```bash
# Validate the backfill results
python3 scripts/backfill_validation.py --sample-size 100
```

### Step 5: Monitor Progress
```bash
# Monitor the backfill progress
python3 scripts/backfill_monitor.py --watch --interval 60
```

## 🔧 Railway Console Commands

### Access Railway Console
1. Go to Railway dashboard
2. Select your backend service
3. Click "Console" tab
4. Run the commands above

### Alternative: Direct Railway CLI
```bash
# If you have Railway CLI installed
railway run python3 scripts/backfill_normalize.py --dry-run --environment production
```

## 📊 Expected Results

### Dry Run Output
- Should show: "DRY RUN: Would update item [ID] with normalized data"
- No actual database changes
- Statistics on how many items would be updated

### Full Backfill Output
- Real-time progress updates
- Batch processing (500 items at a time)
- Final statistics on items processed

### Validation Output
- Consistency rate should be >95%
- All normalized fields should be lowercase
- No missing normalized fields

## 🚨 Safety Measures

1. **Always run dry-run first**
2. **Monitor during low traffic hours**
3. **Have rollback script ready**: `python3 scripts/backfill_rollback.py --dry-run --environment production`
4. **Check logs**: `tail -f backfill_normalize.log`

## 📈 Success Metrics

- **Total Items Processed**: Should match your wardrobe size
- **Consistency Rate**: >95% after validation
- **Error Rate**: <1%
- **Processing Time**: Varies by database size

## 🔄 Rollback (If Needed)

```bash
# Emergency rollback (removes normalized fields)
python3 scripts/backfill_rollback.py --environment production
```

## 📞 Support

If you encounter any issues:
1. Check the logs: `backfill_normalize.log`
2. Run validation: `python3 scripts/backfill_validation.py`
3. Monitor status: `python3 scripts/backfill_monitor.py`
