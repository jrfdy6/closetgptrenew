# Fashion Trends System Setup

This system fetches real-time fashion trends from Google Trends and stores them in Firestore, updating once daily.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Firebase Credentials
```bash
# Set the path to your Firebase service account key file
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/serviceAccountKey.json"
```

### 3. Test the System
```bash
# Run a manual fetch to test
python manual_fetch_trends.py
```

### 4. Start the Daily Scheduler
```bash
# Start the scheduler (runs daily at 9 AM and 3 PM)
python run_fashion_trends_scheduler.py
```

## 📋 What's Included

### Files Created:
- `src/services/fashion_trends_service.py` - Main service for fetching and storing trends
- `src/jobs/fashion_trends_job.py` - Scheduled job runner
- `run_fashion_trends_scheduler.py` - Startup script for the scheduler
- `manual_fetch_trends.py` - Manual testing script
- `FASHION_TRENDS_README.md` - This documentation

### Dependencies Added:
- `pytrends>=4.9.0` - Google Trends API wrapper
- `schedule>=1.2.0` - Python scheduler
- `google-cloud-firestore>=2.11.0` - Firestore client

## 🔧 How It Works

### 1. Trend Fetching
- Fetches 40+ fashion keywords from Google Trends
- Processes data in batches of 5 (Google Trends limit)
- Calculates average popularity scores over 7 days
- Determines trend direction (increasing/decreasing/stable)

### 2. Data Storage
- Stores trends in `fashion_trends` collection
- Maintains daily history in `fashion_trends_daily` collection
- Tracks fetch timestamps to prevent duplicate daily runs

### 3. Integration
- Updates `wardrobe_analysis_service.py` to use real trends
- Falls back to curated data if real trends unavailable
- Provides comprehensive trend metadata

## 📊 Trend Categories

The system tracks trends across these categories:
- **Style Aesthetics**: Y2K, Coastal Chic, Grunge, Old Money, etc.
- **Specific Trends**: Oversized blazers, Cargo pants, Platform shoes, etc.
- **Colors & Patterns**: Sage green, Millennial pink, Checkerboard, etc.
- **Seasonal Trends**: Spring/Summer/Fall/Winter 2024

## ⏰ Scheduling

### Daily Schedule:
- **Primary**: 9:00 AM daily
- **Backup**: 3:00 PM daily (in case morning run fails)

### Rate Limiting:
- 2-second delays between API batches
- Respects Google Trends rate limits
- Prevents duplicate daily fetches

## 🔍 Monitoring

### Logs:
- All activities logged to `fashion_trends_job.log`
- Console output for real-time monitoring
- Error handling with detailed error messages

### Firestore Collections:
- `fashion_trends` - Current trending styles
- `fashion_trends_daily` - Historical daily data
- `fashion_trends_fetch_log` - Fetch timestamps

## 🧪 Testing

### Manual Testing:
```bash
# Test trend fetching
python manual_fetch_trends.py

# Check Firestore data
# Look in fashion_trends collection
```

### Expected Output:
```
🔄 Manually fetching fashion trends...
📊 Fetch Result: success
✅ Successfully fetched 45 trends
⏰ Timestamp: 2024-01-15T10:30:00

🎨 Current Trending Styles:
 1. Y2K Fashion (Popularity: 87)
    Reviving Y2K Fashion with modern twists
    Trend: increasing
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Import Errors**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Firebase Credentials**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"
   ```

3. **Rate Limiting**:
   - System automatically handles rate limits
   - Wait 2 seconds between batches
   - Check logs for rate limit errors

4. **No Trends Available**:
   - System falls back to curated data
   - Check Firestore collections
   - Verify Google Trends API access

### Debug Mode:
```python
# Add to fashion_trends_service.py for detailed logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 🔄 Integration with Frontend

The trends are automatically used by:
- **Dashboard Trending Component** - Shows current trends
- **Wardrobe Analysis** - Identifies trending style gaps
- **Recommendations** - Suggests trending items

## 💰 Cost Analysis

### Free Tier Usage:
- **Google Trends**: Free (with rate limits)
- **Firestore**: Free tier includes 1GB storage, 50K reads/day
- **Estimated Cost**: $0/month for typical usage

### Rate Limits:
- Google Trends: ~100 requests/hour
- Firestore: 50K reads/day (free tier)
- Our usage: ~10 requests/day (well within limits)

## 🚀 Production Deployment

### For Production:
1. Use a proper task scheduler (cron, AWS Lambda, etc.)
2. Set up monitoring and alerting
3. Configure proper logging
4. Set up backup strategies

### Environment Variables:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
FASHION_TRENDS_ENV=production
LOG_LEVEL=INFO
```

## 📈 Future Enhancements

### Potential Improvements:
- Multiple data sources (Instagram, Pinterest, etc.)
- Machine learning trend prediction
- Seasonal trend analysis
- Geographic trend variations
- Brand-specific trend tracking

---

**Note**: This system provides real-time fashion trends while maintaining cost-effectiveness and reliability. 