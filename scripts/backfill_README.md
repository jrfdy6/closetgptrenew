# Wardrobe Backfill System

This directory contains scripts for safely migrating existing wardrobe items to include normalized fields for the semantic filtering system.

## Overview

The backfill system provides a comprehensive, safe approach to migrating existing wardrobe data:

- **Incremental Processing**: Processes items in configurable batches
- **Safety First**: Dry-run mode and environment checks
- **Monitoring**: Real-time progress tracking and health monitoring
- **Validation**: Quality assurance and consistency checking
- **Rollback**: Safe rollback capability if issues arise

## Scripts

### 1. `backfill_normalize.py` - Main Backfill Script

**Purpose**: Migrates existing wardrobe items to include normalized fields.

**Usage**:
```bash
# Dry run on staging
python3 scripts/backfill_normalize.py --dry-run --environment staging

# Run on staging
python3 scripts/backfill_normalize.py --environment staging

# Run on production (with confirmation)
python3 scripts/backfill_normalize.py --environment production
```

**Options**:
- `--batch-size`: Number of items to process per batch (default: 500)
- `--dry-run`: Run without making changes
- `--environment`: Target environment (development/staging/production)

**What it does**:
- Reads wardrobe items in batches
- Normalizes style, occasion, mood, and season fields
- Adds `normalized` field with lowercase, canonical values
- Preserves original fields for auditing
- Tracks progress and statistics

### 2. `backfill_monitor.py` - Monitoring Script

**Purpose**: Monitors the progress and health of the backfill process.

**Usage**:
```bash
# Single report
python3 scripts/backfill_monitor.py

# Continuous monitoring
python3 scripts/backfill_monitor.py --watch --interval 30

# Save report to file
python3 scripts/backfill_monitor.py --save-report
```

**Options**:
- `--watch`: Continuous monitoring mode
- `--interval`: Watch interval in seconds (default: 30)
- `--save-report`: Save report to JSON file

**What it shows**:
- Total items vs normalized items
- Completion percentage
- Recent normalizations
- Error items
- Health status and recommendations

### 3. `backfill_validation.py` - Validation Script

**Purpose**: Validates the quality and correctness of normalized items.

**Usage**:
```bash
# Validate 100 sample items
python3 scripts/backfill_validation.py

# Validate larger sample
python3 scripts/backfill_validation.py --sample-size 500

# Save validation report
python3 scripts/backfill_validation.py --save-report
```

**Options**:
- `--sample-size`: Number of items to validate (default: 100)
- `--save-report`: Save validation report to JSON file

**What it validates**:
- Normalization quality (required fields, data types)
- Semantic compatibility functionality
- Consistency between original and normalized fields
- Data quality metrics

### 4. `backfill_rollback.py` - Rollback Script

**Purpose**: Safely rolls back normalized fields if issues arise.

**Usage**:
```bash
# Dry run rollback
python3 scripts/backfill_rollback.py --dry-run

# Rollback on staging
python3 scripts/backfill_rollback.py --environment staging

# Rollback on production (with confirmation)
python3 scripts/backfill_rollback.py --environment production
```

**Options**:
- `--batch-size`: Number of items to process per batch (default: 500)
- `--dry-run`: Run without making changes
- `--environment`: Target environment

**What it does**:
- Removes `normalized` fields from items
- Preserves original data
- Tracks rollback progress

## Migration Strategy

### Phase 1: Staging Validation
1. **Run dry-run on staging**:
   ```bash
   python3 scripts/backfill_normalize.py --dry-run --environment staging
   ```

2. **Monitor staging data**:
   ```bash
   python3 scripts/backfill_monitor.py --watch
   ```

3. **Validate quality**:
   ```bash
   python3 scripts/backfill_validation.py --sample-size 200
   ```

### Phase 2: Staging Deployment
1. **Run backfill on staging**:
   ```bash
   python3 scripts/backfill_normalize.py --environment staging
   ```

2. **Monitor progress**:
   ```bash
   python3 scripts/backfill_monitor.py --watch --interval 60
   ```

3. **Validate results**:
   ```bash
   python3 scripts/backfill_validation.py --sample-size 500 --save-report
   ```

### Phase 3: Production Deployment
1. **Run during low traffic**:
   ```bash
   python3 scripts/backfill_normalize.py --environment production
   ```

2. **Monitor continuously**:
   ```bash
   python3 scripts/backfill_monitor.py --watch --interval 30
   ```

3. **Validate production**:
   ```bash
   python3 scripts/backfill_validation.py --sample-size 1000 --save-report
   ```

## Data Structure

### Before Backfill
```json
{
  "id": "item_123",
  "name": "Blue Jeans",
  "style": ["Casual", "Streetwear"],
  "occasion": ["Everyday", "Weekend"],
  "mood": ["Relaxed", "Cool"],
  "season": ["Spring", "Summer"]
}
```

### After Backfill
```json
{
  "id": "item_123",
  "name": "Blue Jeans",
  "style": ["Casual", "Streetwear"],
  "occasion": ["Everyday", "Weekend"],
  "mood": ["Relaxed", "Cool"],
  "season": ["Spring", "Summer"],
  "normalized": {
    "style": ["casual", "streetwear"],
    "occasion": ["everyday", "weekend"],
    "mood": ["relaxed", "cool"],
    "season": ["spring", "summer"],
    "normalized_at": "2024-01-15T10:30:00Z",
    "normalized_version": "1.0"
  }
}
```

## Safety Features

### 1. Dry Run Mode
- Test the backfill process without making changes
- Validate logic and data processing
- Estimate processing time and resource usage

### 2. Environment Checks
- Production deployments require explicit confirmation
- Environment-specific configurations
- Safety warnings for production operations

### 3. Batch Processing
- Configurable batch sizes to control resource usage
- Progress tracking and resumable operations
- Error isolation (failures don't affect entire batch)

### 4. Monitoring and Validation
- Real-time progress monitoring
- Quality validation and consistency checks
- Health status reporting and recommendations

### 5. Rollback Capability
- Safe rollback of normalized fields
- Preserves original data
- Emergency recovery procedures

## Error Handling

### Common Issues and Solutions

1. **Firebase Connection Issues**:
   - Verify Firebase configuration
   - Check network connectivity
   - Validate service account permissions

2. **Normalization Errors**:
   - Review item data structure
   - Check for malformed data
   - Validate normalization logic

3. **Batch Processing Failures**:
   - Reduce batch size
   - Check database limits
   - Monitor resource usage

4. **Validation Failures**:
   - Review validation criteria
   - Check data quality
   - Investigate specific failure reasons

## Best Practices

### 1. Always Start with Dry Run
```bash
python3 scripts/backfill_normalize.py --dry-run --environment staging
```

### 2. Monitor Progress Continuously
```bash
python3 scripts/backfill_monitor.py --watch --interval 30
```

### 3. Validate Quality Regularly
```bash
python3 scripts/backfill_validation.py --sample-size 200
```

### 4. Run During Low Traffic
- Schedule production backfill during off-peak hours
- Monitor system performance
- Have rollback plan ready

### 5. Keep Original Data
- Never modify original fields
- Use normalized fields as source of truth
- Maintain audit trail

## Troubleshooting

### Check Logs
- Review backfill logs for errors
- Monitor Firebase console for issues
- Check system resource usage

### Validate Data
- Run validation scripts regularly
- Check sample items manually
- Verify semantic compatibility

### Monitor Performance
- Track processing speed
- Monitor database performance
- Check for resource constraints

### Emergency Procedures
- Stop backfill process if issues arise
- Run rollback if necessary
- Investigate and fix issues before resuming

## Support

For issues or questions:
1. Check the logs and error messages
2. Run validation scripts to identify problems
3. Review the monitoring reports
4. Consult the troubleshooting section
5. Contact the development team if needed

## Files Generated

The backfill process generates several files:

- `backfill_normalize.log` - Main backfill log
- `backfill_stats_YYYYMMDD_HHMMSS.json` - Processing statistics
- `backfill_report_YYYYMMDD_HHMMSS.json` - Monitoring reports
- `validation_report_YYYYMMDD_HHMMSS.json` - Validation results
- `rollback_stats_YYYYMMDD_HHMMSS.json` - Rollback statistics

These files provide detailed information about the backfill process and can be used for analysis and troubleshooting.
