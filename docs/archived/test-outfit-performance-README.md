# Outfit Performance Testing Script

## Quick Start

### Option 1: Using Firebase Token from Browser

1. **Get your Firebase ID token:**
   - Open your production site: https://www.easyoutfitapp.com
   - Open browser DevTools (F12)
   - Go to Application/Storage → Local Storage
   - Find your Firebase auth token, OR
   - In Console, run:
     ```javascript
     // If you're logged in
     firebase.auth().currentUser?.getIdToken().then(token => console.log(token))
     ```

2. **Run the test:**
   ```bash
   node test-outfit-performance.js YOUR_FIREBASE_TOKEN
   ```

### Option 2: Using Environment Variable

```bash
export FIREBASE_TOKEN="your-firebase-token-here"
node test-outfit-performance.js
```

## What It Tests

1. ✅ **Cache Miss** - First generation (should be slow)
2. ✅ **Cache Hit** - Second generation (should be fast, <1s)
3. ✅ **Performance Monitoring** - Checks for duration and is_slow metadata
4. ✅ **Slow Request Detection** - Verifies slow request flagging
5. ✅ **Cache Bypass** - Tests bypass_cache parameter
6. ✅ **Performance Targets** - Tests analytics endpoint
7. ✅ **Admin Cache Stats** - Tests admin endpoint (requires admin access)

## Expected Output

```
🚀 Starting Outfit Generation Performance Tests

API Base URL: https://closetgptrenew-production.up.railway.app

📦 Testing Cache Miss (First Generation)...
✅ Cache Miss: Generated in 3.45s, cache_hit: false

📦 Testing Cache Hit (Second Generation)...
✅ Cache Hit: Returned in 0.123s (cache hit, should be <1s)

⏱️  Testing Performance Monitoring...
✅ Performance Monitoring: Duration: 3.45s, is_slow: false

🐌 Testing Slow Request Detection...
✅ Slow Request Detection: Correctly identified fast request: 3.45s <= 10s

🚫 Testing Cache Bypass...
✅ Cache Bypass: Cache bypassed correctly (cache_hit: false)

🎯 Testing Performance Targets Endpoint...
✅ Performance Targets: Target: 5s, Current: 3.2s

👑 Testing Admin Cache Stats (Admin Only)...
⚠️  Admin Cache Stats: Access denied (not an admin user)

============================================================
📊 Test Summary
============================================================
✅ Passed: 6
❌ Failed: 0
⚠️  Warnings: 1
============================================================
```

## Troubleshooting

### "Firebase token required"
- Make sure you're passing the token as an argument or setting the environment variable
- Token should be a valid Firebase ID token (not a refresh token)

### "Access denied" for admin endpoints
- Admin endpoints require Firebase custom claims (`admin: true`)
- Or your email must be in the `ADMIN_EMAILS` environment variable
- This is expected if you're not an admin user

### Cache hit not working
- Make sure you're using the exact same parameters (occasion, style, mood, weather, wardrobe)
- Wardrobe hash changes when items are added/removed, causing cache invalidation
- This is expected behavior

### Tests timing out
- Check your network connection
- Verify the API URL is correct
- Check Railway logs for backend issues

## Customization

You can modify the script to:
- Test different outfit parameters
- Test with different wardrobe items
- Test cache invalidation scenarios
- Add more detailed logging

## Notes

- The script uses Node.js built-in `https`/`http` modules (no dependencies)
- All tests run sequentially
- Results are color-coded for easy reading
- Exit code is 0 if all tests pass, 1 if any fail

