# 🚀 OpenAI Apps SDK Deployment Checklist

## ✅ Pre-Deployment Verification

### Gateway Code Changes (All Complete)
- [x] Manifest includes `verification_tokens` block
- [x] Manifest includes `authorization_type: "code"`
- [x] Redirect URI validation added to `/oauth/authorize`
- [x] Login redirect uses `returnUrl` parameter
- [x] URL encoding properly implemented
- [x] Import statements corrected

### Environment Variables (Railway Gateway Service)
- [ ] `OPENAI_VERIFICATION_TOKEN=PLACEHOLDER_TOKEN` (set before first registration)
- [x] `FIREBASE_PROJECT_ID` (already set)
- [x] `FIREBASE_PRIVATE_KEY` (already set)
- [x] `FIREBASE_CLIENT_EMAIL` (already set)
- [x] `FIREBASE_CLIENT_ID` (already set)
- [x] `FIREBASE_CLIENT_X509_CERT_URL` (already set)
- [x] `GATEWAY_URL=https://closetgptrenewopenaisdk-production.up.railway.app`
- [x] `FRONTEND_URL=https://easyoutfitapp.com`
- [x] `MAIN_BACKEND_URL=https://closetgptrenew-production.up.railway.app`
- [ ] `OAUTH_CLIENT_ID` (will be provided by OpenAI)
- [ ] `OAUTH_CLIENT_SECRET` (will be provided by OpenAI)

## 📋 Deployment Steps

### Step 1: Add Environment Variable
1. Go to Railway Dashboard → Gateway Service → Variables
2. Add: `OPENAI_VERIFICATION_TOKEN=PLACEHOLDER_TOKEN`
3. Save and redeploy

### Step 2: Verify Deployment
Test these URLs in your browser:

**Manifest:**
```
https://closetgptrenewopenaisdk-production.up.railway.app/.well-known/ai-plugin.json
```

**Check for:**
- ✅ `verification_tokens.openai` = "PLACEHOLDER_TOKEN"
- ✅ `authorization_type: "code"` present
- ✅ All OAuth URLs are correct

**OpenAPI Spec:**
```
https://closetgptrenewopenaisdk-production.up.railway.app/openapi.json
```

**Check for:**
- ✅ Valid JSON structure
- ✅ OAuth2 security scheme configured
- ✅ All paths have security requirements

### Step 3: Register with OpenAI
1. Go to: https://platform.openai.com/apps
2. Click "Create App" or "New App"
3. Fill in app details:
   - **Name:** Easy Outfit
   - **Description:** AI-powered wardrobe manager and outfit generator
   - **Category:** Lifestyle

4. **OAuth Configuration:**
   - **Authorization URL:** `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize`
   - **Token URL:** `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/token`
   - **Redirect URI:** `https://chat.openai.com/aip/oauth/callback` (this is what OpenAI uses)
   - **Scopes:** `wardrobe:read outfits:generate`

5. **API Configuration:**
   - **OpenAPI URL:** `https://closetgptrenewopenaisdk-production.up.railway.app/openapi.json`
   - **Manifest URL:** `https://closetgptrenewopenaisdk-production.up.railway.app/.well-known/ai-plugin.json`

6. **Metadata:**
   - **Privacy Policy:** `https://easyoutfitapp.com/privacy`
   - **Terms of Service:** `https://easyoutfitapp.com/terms`
   - **Contact Email:** `support@easyoutfitapp.com`

### Step 4: Handle Verification Token
After first registration attempt:
1. OpenAI will provide a verification token
2. Update Railway environment variable:
   ```
   OPENAI_VERIFICATION_TOKEN=<token-from-openai>
   ```
3. Redeploy gateway service
4. Retry registration (should pass validation)

### Step 5: Get OAuth Credentials
After successful registration:
1. OpenAI will provide:
   - `OAUTH_CLIENT_ID`
   - `OAUTH_CLIENT_SECRET`
2. Add to Railway environment variables
3. Redeploy if needed

## 🧪 Testing Checklist

### Pre-Registration Tests
- [ ] Manifest URL returns valid JSON
- [ ] OpenAPI URL returns valid JSON
- [ ] Health check works: `/health`
- [ ] OAuth authorize endpoint accessible

### Post-Registration Tests
- [ ] OAuth flow completes successfully
- [ ] User can authorize ChatGPT access
- [ ] API calls work with OAuth token
- [ ] Frontend login redirect works correctly

## 🔍 Troubleshooting

### Manifest Issues
- **Problem:** `verification_tokens` missing
  - **Fix:** Check `OPENAI_VERIFICATION_TOKEN` env var is set

- **Problem:** Invalid JSON
  - **Fix:** Check gateway logs for Python errors

### OAuth Issues
- **Problem:** Redirect URI mismatch
  - **Fix:** Ensure `OAUTH_REDIRECT_URI` matches exactly: `https://chat.openai.com/aip/oauth/callback`

- **Problem:** Invalid client_id
  - **Fix:** Update `OAUTH_CLIENT_ID` in Railway with value from OpenAI

### Frontend Integration
- **Problem:** Login doesn't redirect back
  - **Fix:** Verify frontend `/login` page handles `returnUrl` parameter
  - **Fix:** Check that Firebase token is appended to returnUrl

## 📝 Important URLs Reference

| Purpose | URL |
|---------|-----|
| Gateway Base | `https://closetgptrenewopenaisdk-production.up.railway.app` |
| Manifest | `https://closetgptrenewopenaisdk-production.up.railway.app/.well-known/ai-plugin.json` |
| OpenAPI | `https://closetgptrenewopenaisdk-production.up.railway.app/openapi.json` |
| OAuth Authorize | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize` |
| OAuth Token | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/token` |
| Health Check | `https://closetgptrenewopenaisdk-production.up.railway.app/health` |
| Frontend | `https://easyoutfitapp.com` |
| OpenAI Callback | `https://chat.openai.com/aip/oauth/callback` |

## ✅ Final Checklist Before Registration

- [ ] All environment variables set in Railway
- [ ] Gateway deployed with latest code
- [ ] Manifest URL accessible and valid
- [ ] OpenAPI spec URL accessible and valid
- [ ] Redirect URI validation working
- [ ] Frontend login page updated (if not done yet)
- [ ] Ready to register with OpenAI!

---

**Status:** ✅ Gateway code is fully compliant and ready for deployment!


