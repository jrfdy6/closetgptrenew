# 🚀 Production Monitoring System - Complete Guide

**Version:** 1.0  
**Created:** December 2, 2025  
**Status:** Ready for First Real Users

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [What's Being Monitored](#whats-being-monitored)
3. [Dashboard Endpoints](#dashboard-endpoints)
4. [Key Metrics](#key-metrics)
5. [Accessing Monitoring Data](#accessing-monitoring-data)
6. [Alert Thresholds](#alert-thresholds)
7. [Firebase Collections](#firebase-collections)
8. [Integration Points](#integration-points)
9. [First Week Monitoring Plan](#first-week-monitoring-plan)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Production Monitoring System provides comprehensive real-time monitoring for your first real users. It tracks:

- ✅ **Errors** with full context and stack traces
- ✅ **Performance** for all critical operations
- ✅ **Success rates** for key user actions
- ✅ **User journey** funnel tracking
- ✅ **Service-level metrics** (fallback tracking)
- ✅ **Cache performance**
- ✅ **External API calls**
- ✅ **Automatic alerting** for critical failures

---

## What's Being Monitored

### 🎯 Critical Operations

| Operation | What It Tracks | Target Performance |
|-----------|---------------|-------------------|
| **Outfit Generation** | Full generation pipeline | < 5 seconds (p95) |
| **Image Upload** | File upload + processing | < 10 seconds |
| **Image Analysis** | AI analysis (GPT-4 Vision) | < 15 seconds |
| **Wardrobe Fetch** | Loading user's wardrobe | < 2 seconds |
| **Wardrobe Add** | Adding new item | < 3 seconds |
| **Dashboard Load** | Initial page load | < 3 seconds |
| **Authentication** | Login/signup flow | < 2 seconds |

### 📍 User Journey Milestones

1. **Signup** - User creates account
2. **Onboarding Start** - Begins onboarding flow
3. **Onboarding Complete** - Finishes onboarding
4. **First Item Added** - Adds first wardrobe item
5. **First Outfit Generated** - Generates first outfit
6. **First Outfit Saved** - Saves generated outfit
7. **First Favorite** - Marks outfit as favorite
8. **Return Visit** - Comes back after first session
9. **Subscription View** - Views subscription options
10. **Subscription Purchase** - Completes purchase

### 🔧 Service Layers (Outfit Generation)

The system tracks which generation strategy is used:

1. **Robust Generation** (Primary) - Full AI-powered generation
2. **Personalization** (Enhanced) - Personalized recommendations
3. **Rule-Based** (Fallback) - Rule-based generation
4. **Simple Fallback** (Emergency) - Basic outfit creation
5. **Emergency Mock** (Last Resort) - Mock data return

⚠️ **Important:** High fallback usage indicates issues with primary services.

---

## Dashboard Endpoints

### Base URL
```
Production: https://closetgptrenew-production.up.railway.app/api/monitoring
Local: http://localhost:3001/api/monitoring
```

### Available Endpoints

#### 1. Health Check
```bash
GET /api/monitoring/health
```

**Returns:**
```json
{
  "status": "healthy",
  "monitoring_enabled": true,
  "timestamp": "2025-12-02T10:30:00Z"
}
```

#### 2. Summary Dashboard
```bash
GET /api/monitoring/stats/summary?time_window_minutes=60
```

**Returns:** Comprehensive stats including:
- Success rates for all operations
- Performance percentiles (p50, p95, p99)
- Cache hit rates
- Recent errors
- User funnel stats
- Service layer distribution

**Example:**
```json
{
  "time_window_minutes": 60,
  "success_rates": {
    "outfit_generation": 95.5,
    "image_upload": 98.2,
    "wardrobe_add": 99.1
  },
  "performance": {
    "outfit_generation": {
      "p50_ms": 2340,
      "p95_ms": 4580,
      "p99_ms": 7120
    }
  },
  "cache_hit_rate": 42.3,
  "recent_errors_count": 3,
  "user_funnel": {...},
  "service_layers": {...},
  "total_operations": 247
}
```

#### 3. Operation-Specific Stats
```bash
GET /api/monitoring/stats/operations?operation=outfit_generation&time_window_minutes=60
```

**Returns:**
```json
{
  "operation": "outfit_generation",
  "success_rate": 95.5,
  "total_operations": 120,
  "successful": 115,
  "failed": 5,
  "performance": {
    "p50_ms": 2340,
    "p95_ms": 4580,
    "p99_ms": 7120
  }
}
```

#### 4. Recent Errors
```bash
GET /api/monitoring/stats/errors?limit=50&operation=outfit_generation
```

**Returns:**
```json
{
  "total_errors": 5,
  "returned_count": 5,
  "errors": [
    {
      "operation": "outfit_generation",
      "user_id": "user_123",
      "error": "Validation failed: insufficient items",
      "error_type": "ValidationError",
      "stack_trace": "...",
      "context": {
        "occasion": "business",
        "wardrobe_size": 12
      },
      "timestamp": "2025-12-02T10:25:30Z"
    }
  ]
}
```

#### 5. User Funnel Statistics
```bash
GET /api/monitoring/stats/user-funnel
```

**Returns:**
```json
{
  "total_users": 50,
  "funnel": {
    "signup": {
      "completed": 50,
      "conversion_rate": 100.0
    },
    "first_item_added": {
      "completed": 45,
      "conversion_rate": 90.0
    },
    "first_outfit_generated": {
      "completed": 38,
      "conversion_rate": 76.0
    }
  }
}
```

#### 6. Service Layer Distribution
```bash
GET /api/monitoring/stats/service-layers
```

**Returns:**
```json
{
  "distribution": {
    "robust_generation": {
      "count": 115,
      "percentage": 95.8
    },
    "rule_based": {
      "count": 5,
      "percentage": 4.2
    }
  },
  "total_generations": 120
}
```

#### 7. Cache Performance
```bash
GET /api/monitoring/stats/cache
```

**Returns:**
```json
{
  "hit_rate_percent": 42.3,
  "hits": 105,
  "misses": 143,
  "total_requests": 248
}
```

#### 8. External API Calls
```bash
GET /api/monitoring/stats/api-calls
```

**Returns:**
```json
{
  "api_calls": {
    "openai_gpt4": 150,
    "firebase_query": 520,
    "firebase_write": 180
  },
  "total_calls": 850
}
```

#### 9. Alerts
```bash
GET /api/monitoring/alerts?limit=20&acknowledged=false
```

**Returns:**
```json
{
  "alerts": [
    {
      "id": "alert_xyz",
      "title": "Low Success Rate Alert: outfit_generation",
      "message": "Success rate: 85.2% (threshold: 90%)",
      "severity": "critical",
      "data": {...},
      "timestamp": "2025-12-02T10:20:00Z",
      "acknowledged": false
    }
  ]
}
```

#### 10. Acknowledge Alert
```bash
POST /api/monitoring/alerts/{alert_id}/acknowledge
```

---

## Key Metrics

### ⚡ Performance Targets

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| **Outfit Generation Time (p95)** | < 5s | > 10s |
| **Image Analysis Time (p95)** | < 15s | > 20s |
| **Success Rate** | > 95% | < 90% |
| **Cache Hit Rate** | > 40% | < 20% |
| **Fallback Usage** | < 5% | > 15% |

### 📊 Success Rate Calculation

```
Success Rate = (Successful Operations / Total Operations) × 100
```

### 🎯 User Funnel Conversion

```
Conversion Rate = (Users Who Completed Step / Total Users) × 100
```

---

## Accessing Monitoring Data

### Option 1: API Calls (Recommended for First Week)

```bash
# Get overall summary
curl https://closetgptrenew-production.up.railway.app/api/monitoring/stats/summary

# Get recent errors
curl https://closetgptrenew-production.up.railway.app/api/monitoring/stats/errors?limit=10

# Get user funnel
curl https://closetgptrenew-production.up.railway.app/api/monitoring/stats/user-funnel
```

### Option 2: Firebase Console

Monitoring data is automatically saved to Firebase collections:
- `performance_metrics` - All operation performance data
- `errors` - All error events with full context
- `user_journeys` - User milestone tracking
- `service_layer_usage` - Service layer distribution
- `alerts` - System alerts

### Option 3: Railway Logs

All monitoring events are logged to Railway. Search for:
- `🚨` - Critical errors/alerts
- `⚠️` - Warnings (slow requests, fallbacks)
- `✅` - Successful operations
- `📊` - Performance metrics

---

## Alert Thresholds

The system automatically alerts when:

### 🚨 Critical Alerts

1. **Success Rate < 90%** for any operation
2. **Generation Time > 10 seconds** (p95)
3. **Image Analysis Time > 15 seconds** (p95)
4. **Fallback Usage > 15%**

### ⚠️ Warning Alerts

1. **Success Rate < 95%** for any operation
2. **Cache Hit Rate < 20%**
3. **Slow Request** (> threshold for operation)

### 📬 Alert Delivery

Currently alerts are:
- ✅ Logged to Railway console
- ✅ Saved to Firebase `alerts` collection
- ⏳ **TODO:** Email notifications (integrate SendGrid)
- ⏳ **TODO:** Slack notifications (webhook)

---

## Firebase Collections

### Collection: `performance_metrics`

```javascript
{
  operation: "outfit_generation",
  user_id: "user_123",
  status: "success",
  duration_ms: 2340,
  timestamp: "2025-12-02T10:30:00Z",
  context: {
    occasion: "business",
    style: "classic",
    wardrobe_size: 45,
    cache_hit: false
  }
}
```

### Collection: `errors`

```javascript
{
  operation: "outfit_generation",
  user_id: "user_123",
  error: "Validation failed after 3 attempts",
  error_type: "ValidationError",
  stack_trace: "...",
  context: {
    occasion: "business",
    wardrobe_size: 12
  },
  timestamp: "2025-12-02T10:25:30Z"
}
```

### Collection: `user_journeys`

```javascript
{
  "user_123": {
    signup: {
      timestamp: "2025-12-02T09:00:00Z",
      metadata: {},
      completed: true
    },
    first_item_added: {
      timestamp: "2025-12-02T09:15:00Z",
      metadata: { item_type: "shirt" },
      completed: true
    },
    first_outfit_generated: {
      timestamp: "2025-12-02T09:30:00Z",
      metadata: { occasion: "business" },
      completed: true
    }
  }
}
```

### Collection: `alerts`

```javascript
{
  title: "Low Success Rate Alert: outfit_generation",
  message: "Success rate: 85.2% (threshold: 90%)",
  severity: "critical",
  data: {...},
  timestamp: "2025-12-02T10:20:00Z",
  acknowledged: false,
  acknowledged_at: null
}
```

---

## Integration Points

### Monitoring is Integrated Into:

1. ✅ **Outfit Generation** (`/api/outfits/generate`)
   - Tracks duration, success/failure, context
   - Tracks cache hits/misses
   - Tracks service layer usage
   - Tracks first outfit generated milestone

2. ✅ **Wardrobe Management** (`/api/wardrobe/add`)
   - Tracks item addition performance
   - Tracks first item added milestone
   - Tracks image upload success

3. ⏳ **Image Upload** (TODO - Easy to add using same pattern)
4. ⏳ **Image Analysis** (TODO - Easy to add using same pattern)
5. ⏳ **Dashboard Load** (TODO - Add to frontend)

### Adding Monitoring to New Endpoints

```python
from src.services.production_monitoring_service import (
    monitoring_service,
    OperationType,
    UserJourneyStep
)

@router.post("/your-endpoint")
async def your_function(user_id: str):
    start_time = time.time()
    
    try:
        # Your logic here
        result = do_something()
        
        # Track success
        await monitoring_service.track_operation(
            operation=OperationType.YOUR_OPERATION,
            user_id=user_id,
            status="success",
            duration_ms=(time.time() - start_time) * 1000,
            context={"key": "value"}
        )
        
        return result
    
    except Exception as e:
        # Track failure
        await monitoring_service.track_operation(
            operation=OperationType.YOUR_OPERATION,
            user_id=user_id,
            status="failure",
            duration_ms=(time.time() - start_time) * 1000,
            error=str(e),
            error_type=type(e).__name__,
            stack_trace=traceback.format_exc()
        )
        raise
```

---

## First Week Monitoring Plan

### Day 1-3: Focus on "Does it work?"

**Check Every 4 Hours:**
```bash
# Overall health
curl /api/monitoring/stats/summary?time_window_minutes=240

# Recent errors
curl /api/monitoring/stats/errors?limit=20

# Success rates
curl /api/monitoring/stats/operations
```

**Key Questions:**
- What's the outfit generation success rate?
- Are there any recurring errors?
- Are users completing the onboarding flow?

### Day 4-7: Focus on "Is it fast enough?"

**Check Twice Daily:**
```bash
# Performance metrics
curl /api/monitoring/stats/operations?operation=outfit_generation

# Service layer distribution
curl /api/monitoring/stats/service-layers
```

**Key Questions:**
- What's the p95 generation time?
- Are we hitting fallback layers too often?
- What's causing slow requests?

### Week 2+: Focus on "Are users coming back?"

**Check Daily:**
```bash
# User funnel
curl /api/monitoring/stats/user-funnel

# Cache performance
curl /api/monitoring/stats/cache
```

**Key Questions:**
- What's the signup → first outfit conversion rate?
- Are users returning after first session?
- How many users are generating multiple outfits?

---

## Troubleshooting

### Problem: High Error Rate

**Diagnosis:**
```bash
curl /api/monitoring/stats/errors?limit=50
```

**Look for:**
- Recurring error messages
- Common user contexts (small wardrobes, specific occasions)
- Stack trace patterns

**Action:**
- Fix root cause in code
- Add better validation
- Improve error messages

### Problem: Slow Performance

**Diagnosis:**
```bash
curl /api/monitoring/stats/operations?operation=outfit_generation
```

**Look for:**
- p95/p99 times significantly higher than p50
- Specific occasions or contexts causing slowness
- Cache hit rate

**Action:**
- Optimize slow code paths
- Increase cache TTL
- Add more caching layers

### Problem: Low Conversion Rates

**Diagnosis:**
```bash
curl /api/monitoring/stats/user-funnel
```

**Look for:**
- Which step has biggest drop-off
- Common patterns in user journeys

**Action:**
- Improve UX at drop-off point
- Add better onboarding guidance
- Reduce friction

### Problem: High Fallback Usage

**Diagnosis:**
```bash
curl /api/monitoring/stats/service-layers
```

**Look for:**
- Which layer is being used most
- Errors in primary service logs

**Action:**
- Fix issues in robust generation service
- Check AI API rate limits
- Verify Firebase connectivity

---

## Quick Reference Card

### Most Important Endpoints

```bash
# Dashboard overview
GET /api/monitoring/dashboard

# Recent errors
GET /api/monitoring/stats/errors?limit=10

# Success rates
GET /api/monitoring/stats/operations

# User funnel
GET /api/monitoring/stats/user-funnel
```

### Most Important Metrics

- **Outfit Generation Success Rate:** Target > 95%
- **Outfit Generation Time (p95):** Target < 5s
- **First Outfit Conversion:** Target > 70%
- **Fallback Usage:** Target < 5%

### When to Investigate

- ❗ Success rate drops below 90%
- ❗ p95 time exceeds 10 seconds
- ❗ More than 3 errors per hour
- ❗ Fallback usage above 15%
- ❗ Funnel conversion drops below 50%

---

## Next Steps

1. ✅ **Deployed** - Monitoring is live in production
2. ⏳ **Test** - Generate test outfits and verify monitoring data
3. ⏳ **Build Frontend** - Create React dashboard component
4. ⏳ **Set Up Alerts** - Configure email/Slack notifications
5. ⏳ **Monitor First Users** - Watch dashboard during launch

---

**Questions?** Check the monitoring endpoints or review the logs in Railway.

**Need Help?** All monitoring code is in:
- `backend/src/services/production_monitoring_service.py`
- `backend/src/routes/production_monitoring.py`

