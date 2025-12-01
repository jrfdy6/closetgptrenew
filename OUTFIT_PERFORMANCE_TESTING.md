# Outfit Generation Performance Optimization - Testing Guide

## Overview
This guide covers testing the new performance optimizations including caching, performance monitoring, and admin cache management.

## 1. Testing Outfit Generation Caching

### Test Cache Hit (Same Request)
1. **Generate an outfit** with specific parameters:
   - Occasion: "casual"
   - Style: "modern"
   - Mood: "confident"
   - Note the generation time in the response metadata

2. **Generate the same outfit again** (same occasion, style, mood, weather, baseItemId)
   - Should return much faster (cache hit)
   - Check browser DevTools Network tab - response should be <100ms
   - Response metadata should include `cache_hit: true`

3. **Verify in backend logs:**
   - Look for: `✅ Cache hit for outfit generation`
   - Should NOT see generation attempt logs

### Test Cache Invalidation (Wardrobe Change)
1. **Generate an outfit** and note it's cached
2. **Add or remove a wardrobe item** (this changes wardrobe hash)
3. **Generate the same outfit again**
   - Should be a cache miss (wardrobe hash changed)
   - Should regenerate from scratch

### Test Cache Validation (Item Deletion)
1. **Generate an outfit** and cache it
2. **Delete one of the items** used in the cached outfit
3. **Generate the same outfit again**
   - Should detect invalid cache (item missing)
   - Should regenerate from scratch
   - Backend logs: `⚠️ Cache hit but validation failed - regenerating`

### Test Cache Bypass
1. **Add `bypass_cache: true`** to the outfit generation request
2. **Generate outfit** - should always be a cache miss
3. **Generate again with same params** - should still be a cache miss

**Frontend Test:**
```typescript
// In browser console on outfit generation page
const request = {
  ...formData,
  bypass_cache: true
};
```

## 2. Testing Performance Monitoring

### Test Slow Request Detection
1. **Generate an outfit** that takes >10 seconds
   - Check response metadata for `is_slow: true`
   - Check `generation_duration` in metadata
   - Frontend should show: "This is taking longer than usual..."

2. **Check backend logs:**
   - Look for: `⚠️ SLOW REQUEST: Generation took X.XXs (threshold: 10s)`

### Test Performance Metrics Recording
1. **Generate multiple outfits** with different parameters
2. **Check metrics service** (if you have access to logs):
   - Should see generation times recorded
   - Should see performance target violations if any

## 3. Testing Performance Targets Endpoint

### Test Performance Targets Status
1. **Call the endpoint:**
   ```bash
   curl -X GET "https://closetgptrenew-production.up.railway.app/api/analytics/performance-targets" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Expected response:**
   ```json
   {
     "success": true,
     "performance_targets": {
       "outfit_generation": {
         "target": 5.0,
         "p95_target": 10.0,
         "current_avg": 3.2,
         "current_p95": 8.5,
         "meets_target": true,
         "meets_p95": true,
         "violations_count": 2,
         "recent_violations": [...]
       },
       "targets": {
         "outfit_generation": {"target": 5.0, "p95": 10.0},
         "wardrobe_page_load": {"target": 2.0, "p95": 4.0},
         "upload_processing": {"target": 10.0, "p95": 20.0},
         "dashboard_load": {"target": 1.0, "p95": 2.0}
       }
     }
   }
   ```

## 4. Testing Admin Cache Management

### Prerequisites
- You need admin access (Firebase custom claim `admin: true` or email in `ADMIN_EMAILS` env var)

### Test Cache Statistics
```bash
curl -X GET "https://closetgptrenew-production.up.railway.app/api/outfits/admin/cache-stats" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Expected response:**
```json
{
  "success": true,
  "outfit_cache": {
    "size": 45,
    "max_size": 2000,
    "hits": 120,
    "misses": 80,
    "hit_rate": 60.0,
    "evictions": 2,
    "sets": 80
  },
  "all_caches": {
    "outfit": {...},
    "user": {...},
    "wardrobe": {...}
  }
}
```

### Test Cache Clear
```bash
curl -X POST "https://closetgptrenew-production.up.railway.app/api/outfits/admin/cache-clear" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Expected response:**
```json
{
  "success": true,
  "message": "Outfit cache cleared",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Test Clear All Caches
```bash
curl -X POST "https://closetgptrenew-production.up.railway.app/api/outfits/admin/cache-clear-all" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 5. Frontend Testing

### Test Slow Request Message
1. **Generate an outfit** that takes >10 seconds
2. **Check UI** - should see amber notification card:
   - "This is taking longer than usual..."
   - "We're still working on it. Your outfit will be ready shortly."

### Test Cache Hit (User Experience)
1. **Generate outfit** - note the time
2. **Generate same outfit again** - should be instant
3. **User should see outfit appear immediately** (no loading animation)

## 6. Browser DevTools Testing

### Network Tab
1. **Open DevTools → Network tab**
2. **Generate outfit** - note:
   - First request: Full generation time (e.g., 3-5 seconds)
   - Cached request: <100ms response time
   - Response headers should show cache metadata

### Console Logs
1. **Open DevTools → Console**
2. **Generate outfit** - look for:
   - `✅ Cache hit for outfit generation` (if cached)
   - `❌ Cache miss for outfit generation` (if not cached)
   - Performance warnings if slow

## 7. Backend Logs Testing

### Check Railway Logs
1. **Go to Railway dashboard** → Your backend service → Logs
2. **Generate outfits** and watch for:
   - `✅ Cache hit for outfit generation: outfit:...`
   - `❌ Cache miss for outfit generation`
   - `⚠️ Cache hit but validation failed - regenerating`
   - `⚠️ SLOW REQUEST: Generation took X.XXs`
   - `💾 Cached outfit generation: outfit:...`
   - `⚠️ PERFORMANCE TARGET VIOLATION`

## 8. Quick Test Checklist

- [ ] Generate outfit → Check cache miss in logs
- [ ] Generate same outfit → Check cache hit (fast response)
- [ ] Add wardrobe item → Generate same outfit → Should be cache miss
- [ ] Delete item from cached outfit → Generate → Should validate and regenerate
- [ ] Generate slow outfit (>10s) → Check `is_slow: true` in response
- [ ] Check frontend shows slow request message
- [ ] Call performance targets endpoint → Verify metrics
- [ ] (Admin) Call cache stats endpoint → Verify statistics
- [ ] (Admin) Clear cache → Generate outfit → Should be cache miss

## 9. Expected Performance Improvements

### Before Optimization:
- Average generation: 5-8 seconds
- P95 generation: 10-15 seconds
- No caching

### After Optimization:
- **Cached requests:** <100ms (instant)
- **Cache hit rate:** 40%+ (after warm-up period)
- **Average generation:** 3-5 seconds (for cache misses)
- **P95 generation:** <10 seconds (target)

## 10. Troubleshooting

### Cache Not Working?
1. Check backend logs for cache errors
2. Verify `cache_manager` is initialized
3. Check cache TTL is set correctly (86400 seconds)

### Performance Targets Not Tracking?
1. Verify `log_generation_strategy` is called with `generation_time`
2. Check `GenerationMetricsService` is recording times
3. Verify endpoint is accessible

### Admin Endpoints Return 403?
1. Check Firebase custom claims (`admin: true`)
2. Verify `ADMIN_EMAILS` environment variable
3. Check token is valid and includes admin claim

## Notes

- Cache is in-memory only (resets on server restart)
- Cache validation ensures items still exist before returning cached outfit
- Wardrobe hash auto-invalidates cache when wardrobe changes
- Performance targets are tracked in-memory (resets on restart)
- Admin endpoints require proper authentication

