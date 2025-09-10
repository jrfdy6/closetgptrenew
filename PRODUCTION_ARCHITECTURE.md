# ClosetGPT Production Architecture Reference

## 🚨 CRITICAL: Never Forget These Details

### Environment Variables (Vercel Dashboard)
**Location:** Vercel Dashboard → Project Settings → Environment Variables

```
NEXT_PUBLIC_API_URL = https://closetgptrenew-backend-production.up.railway.app
NEXT_PUBLIC_BACKEND_URL = https://closetgptrenew-backend-production.up.railway.app
```

**⚠️ IMPORTANT:** These are set in Vercel dashboard, NOT in `vercel.json`. `NEXT_PUBLIC_` variables cannot be set via `vercel.json`.

### Working API Routes (Production)
These routes work perfectly and use hardcoded Railway URLs:

- ✅ `/api/wardrobe` - Main wardrobe endpoint
- ✅ `/api/outfits` - Outfits endpoint  
- ✅ `/api/wardrobe/wardrobe-stats` - Wardrobe statistics
- ✅ `/api/wardrobe/trending-styles` - Trending styles
- ✅ `/api/wardrobe/top-worn-items` - Top worn items
- ✅ `/api/wardrobe/forgotten-gems` - Forgotten gems
- ✅ `/api/wardrobe/gaps` - Wardrobe gaps
- ✅ `/api/wardrobe/validation-errors` - Validation errors

### Missing API Routes (Vercel Deployment Issue)
These routes were created but **DO NOT DEPLOY** to Vercel:

- ❌ `/api/outfit-history/` - Returns 404 in production
- ❌ `/api/outfit-history/today-suggestion` - Returns 404 in production
- ❌ Any new route files created after initial deployment

**Root Cause:** Vercel has build caching issues that prevent new API route files from being deployed, even after git push.

### Authentication Setup
**Railway Backend:** Supports test tokens in both functions:
- `get_current_user()` - Allows test token
- `get_current_user_optional()` - Allows test token

**Test Token:** `"test"`
**Test User ID:** `"test-user-id"`
**Test User Email:** `"test@example.com"`

### Dashboard Service Architecture
**Frontend Service:** `frontend/src/lib/services/dashboardService.ts`
- Uses Next.js API routes as proxy (`/api${endpoint}`)
- Calls hardcoded Railway URLs in API routes
- Supports test authentication for null users

### Key Troubleshooting Steps

1. **Dashboard Loading Issues:**
   - Check if API routes exist in production
   - Verify Railway backend is responding
   - Test with curl: `curl -s "https://closetgpt-frontend.vercel.app/api/wardrobe" -H "Authorization: Bearer test"`

2. **New API Routes Not Working:**
   - Vercel deployment issue - new route files don't deploy
   - Solution: Modify existing working routes instead of creating new ones
   - Or force Vercel rebuild by changing existing files

3. **Environment Variable Issues:**
   - Check Vercel dashboard, not `vercel.json`
   - Use hardcoded URLs in API routes as fallback
   - Test with debug logging in route files

### Production URLs
- **Frontend:** https://closetgpt-frontend.vercel.app
- **Backend:** https://closetgptrenew-backend-production.up.railway.app
- **Health Check:** https://closetgptrenew-backend-production.up.railway.app/health

### File Structure
```
frontend/src/app/api/
├── wardrobe/           # ✅ Working
│   ├── route.ts       # Main wardrobe endpoint
│   ├── wardrobe-stats/ # ✅ Working
│   ├── trending-styles/ # ✅ Working
│   └── top-worn-items/ # ✅ Working
├── outfits/           # ✅ Working
│   └── route.ts       # Main outfits endpoint
└── outfit-history/    # ❌ Not deploying
    ├── route.ts       # Created but 404 in production
    └── today-suggestion/ # Created but 404 in production
```

### Critical Success Factors
1. **Use hardcoded Railway URLs** in API routes (not environment variables)
2. **Test authentication works** with "test" token
3. **Existing routes work**, new routes don't deploy to Vercel
4. **Environment variables are set correctly** in Vercel dashboard
5. **Railway backend is responsive** and supports test tokens

---
**Last Updated:** January 2025
**Status:** Production Dashboard Working ✅
