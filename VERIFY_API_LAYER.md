# 🔍 API Layer Verification Guide

## Step 1: Test the Test Route (Simple Verification)

### Option A: Browser URL Test
Open your browser and navigate to:
```
https://closetgpt-frontend.vercel.app/api/test-route
```

**✅ SUCCESS Response:**
```json
{
  "success": true,
  "message": "API routes are working!",
  "timestamp": "2025-10-11T...",
  "deployment": "vercel-2025-10-11-v3"
}
```

**❌ FAILURE Indicators:**
- 404 Not Found = Route not deployed yet, wait 2 more minutes
- 405 Method Not Allowed = OPTIONS handler missing (shouldn't happen with current config)
- 500 Internal Server Error = Runtime config issue
- Blank page or CORS error = Check browser console

---

## Step 2: Browser Console Test (Detailed Verification)

Open your browser console (F12) and run this script:

```javascript
// Test 1: GET request to test route
fetch('https://closetgpt-frontend.vercel.app/api/test-route')
  .then(r => r.json())
  .then(data => {
    console.log('✅ Test Route GET:', data);
    if (data.success && data.deployment === 'vercel-2025-10-11-v3') {
      console.log('🎉 API routes are working! Deployment v3 confirmed.');
    }
  })
  .catch(e => console.error('❌ Test Route GET Failed:', e));

// Test 2: POST request to test route
fetch('https://closetgpt-frontend.vercel.app/api/test-route', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ test: 'data' })
})
  .then(r => r.json())
  .then(data => {
    console.log('✅ Test Route POST:', data);
    if (data.success && data.message === 'POST method is working!') {
      console.log('🎉 POST method confirmed working!');
    }
  })
  .catch(e => console.error('❌ Test Route POST Failed:', e));

// Test 3: Check if OPTIONS preflight is handled (for CORS)
fetch('https://closetgpt-frontend.vercel.app/api/outfits/generate', {
  method: 'OPTIONS'
})
  .then(r => {
    console.log('✅ OPTIONS Response Status:', r.status);
    console.log('✅ CORS Headers:', {
      'Access-Control-Allow-Methods': r.headers.get('Access-Control-Allow-Methods'),
      'Access-Control-Allow-Headers': r.headers.get('Access-Control-Allow-Headers')
    });
    if (r.status === 200) {
      console.log('🎉 CORS preflight handling confirmed!');
    }
  })
  .catch(e => console.error('❌ OPTIONS Request Failed:', e));
```

---

## Step 3: Verify Configuration

### Check Runtime Config
File: `frontend/src/app/api/outfits/generate/route.ts`

**Required exports (lines 5-7):**
```typescript
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
export const revalidate = 0;
```

✅ **STATUS:** All present

### Check CORS Handler
**Required OPTIONS handler (lines 10-19):**
```typescript
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
```

✅ **STATUS:** Present

### Check Deployment Version
**Required version marker (line 3):**
```typescript
// DEPLOYMENT VERSION: 2025-10-11-v3
```

✅ **STATUS:** Present (forces cache bust)

---

## Step 4: Check Vercel Deployment Status

### Method 1: Check Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Find your `closetgpt-frontend` project
3. Check latest deployment:
   - ✅ **Ready** = Deployment successful
   - ⏳ **Building** = Still deploying (wait)
   - ❌ **Error** = Check build logs

### Method 2: Check via Git Commit
Latest commit should be:
```
5e7c742a3 FIX: Resolve 405 error on /api/outfits/generate route
```

✅ **STATUS:** Confirmed pushed

---

## Step 5: Test the Main Generate Route

After confirming the test route works, test outfit generation:

```javascript
// Get your Firebase auth token first
// (You'll need to be logged in to your app)

const testOutfitGeneration = async (authToken) => {
  const response = await fetch('https://closetgpt-frontend.vercel.app/api/outfits/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      occasion: 'Business',
      style: 'Classic',
      mood: 'Bold',
      weather: { temperature: 65 },
      wardrobe: [], // Add your wardrobe items here
      user_profile: {},
      generation_mode: 'robust'
    })
  });
  
  const data = await response.json();
  console.log('Generate Route Response:', {
    status: response.status,
    success: data.success,
    itemCount: data.items?.length
  });
  
  if (response.status === 200) {
    console.log('🎉 Generate route working!');
  } else if (response.status === 405) {
    console.warn('⚠️ 405 still happening, but fallback should handle it');
  }
};
```

---

## 🐛 Troubleshooting

### If Test Route Returns 404
**Cause:** Route not deployed yet  
**Fix:** Wait 2-3 more minutes, then refresh

### If Test Route Returns 405
**Cause:** OPTIONS handler not recognized  
**Fix:** Check Vercel build logs for errors

### If Generate Route Returns 405
**Cause:** POST method not recognized  
**Fix:** Fallback will handle it, but check:
1. Runtime config is deployed
2. OPTIONS handler is present
3. Clear browser cache

### If CORS Errors in Console
**Cause:** OPTIONS preflight failing  
**Fix:** Verify OPTIONS handler returns status 200

---

## ✅ Success Criteria

All of these should be ✅:
- [ ] Test route returns `{"success": true}`
- [ ] POST to test route works
- [ ] OPTIONS to generate route returns 200
- [ ] Generate route returns 200 OR fallback triggers
- [ ] Deployment version shows `vercel-2025-10-11-v3`

---

## 📊 Next Steps After Verification

Once API layer is confirmed working:
1. Generate 3 outfits for "Business + Classic + Bold"
2. Each should use different items (diversity)
3. Oxford shoes and beige turtleneck should pass filtering (semantic)
4. Check Firestore to confirm outfits are being saved

