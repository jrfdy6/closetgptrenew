# 🔐 OAuth Firebase Auth Integration Guide

## Overview

The OAuth gateway now requires users to be **logged into your website** (via Firebase Auth) before they can authorize ChatGPT to access their wardrobe data. This ensures secure, user-authenticated access to your API.

## ✅ What's Been Implemented

1. **Firebase Admin SDK Integration** - Gateway can verify Firebase ID tokens
2. **User Authentication Check** - OAuth consent page requires valid Firebase token
3. **Real User IDs** - Stores actual Firebase user_id instead of "demo_user"
4. **Secure Token Flow** - Firebase tokens are stored and used for API calls

## 🔄 How It Works

### OAuth Flow with Firebase Auth

```
1. User in ChatGPT clicks "Connect Easy Outfit"
   ↓
2. ChatGPT redirects to: /oauth/authorize?client_id=...&redirect_uri=...&state=...
   ↓
3. Gateway checks for Firebase token:
   ├─ If NO token → Show login page → Redirect to frontend login
   └─ If token exists → Verify token
       ├─ If invalid → Show login page
       └─ If valid → Show consent page with user info
   ↓
4. User clicks "Authorize" on consent page
   ↓
5. Gateway generates authorization code (linked to real user_id)
   ↓
6. Redirect back to ChatGPT with code
   ↓
7. ChatGPT exchanges code for access token
   ↓
8. Gateway returns access token (stores Firebase token for later use)
   ↓
9. ChatGPT can now call API with access token
   ↓
10. Gateway uses Firebase token to authenticate with main backend
```

## 📋 Frontend Integration

### Option 1: Pass Firebase Token via Query Parameter (Current Implementation)

When a user clicks "Connect Easy Outfit" in ChatGPT and is redirected to the OAuth authorize page, your frontend can intercept this and:

1. **Check if user is logged in** (has Firebase ID token)
2. **If logged in**: Redirect to gateway with Firebase token:
   ```
   https://gateway-url/oauth/authorize?client_id=...&redirect_uri=...&state=...&firebase_token=USER_FIREBASE_TOKEN
   ```
3. **If not logged in**: Redirect to your login page, then back to gateway after login

### Option 2: Use Session/Cookie (Recommended for Production)

1. User logs into your website (Firebase Auth)
2. Frontend stores Firebase ID token in a **secure, httpOnly cookie**
3. When ChatGPT redirects to `/oauth/authorize`, the cookie is sent automatically
4. Gateway verifies the token from the cookie

**To enable cookie-based auth:**
- Update your frontend to set a cookie with the Firebase token
- Make sure the cookie domain allows the gateway to read it
- Gateway already checks cookies (see `get_firebase_token_from_request()`)

### Example Frontend Code (React/Next.js)

```javascript
// When user clicks "Connect Easy Outfit" in ChatGPT
// The OAuth flow redirects to your gateway

// In your login page or OAuth callback handler:
useEffect(() => {
  // Get Firebase ID token
  const user = auth.currentUser;
  if (user) {
    user.getIdToken().then((token) => {
      // Option 1: Pass as query parameter
      const oauthUrl = new URL(window.location.href);
      oauthUrl.searchParams.set('firebase_token', token);
      window.location.href = oauthUrl.toString();
      
      // Option 2: Set cookie (better for production)
      document.cookie = `firebase_token=${token}; path=/; secure; samesite=strict`;
      window.location.href = oauthUrl.toString();
    });
  } else {
    // User not logged in, redirect to login
    router.push('/login?redirect=' + encodeURIComponent(window.location.href));
  }
}, []);
```

## 🔧 Environment Variables

Make sure your **gateway service** has these Firebase environment variables:

```bash
# Firebase Admin SDK credentials (same as main backend)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-service-account@...
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_X509_CERT_URL=https://...

# Frontend URL for login redirect
FRONTEND_URL=https://easyoutfitapp.com

# Gateway URL
GATEWAY_URL=https://closetgptrenewopenaisdk-production.up.railway.app

# Main backend URL
MAIN_BACKEND_URL=https://closetgptrenew-production.up.railway.app

# OAuth credentials (from OpenAI)
OAUTH_CLIENT_ID=<from-openai>
OAUTH_CLIENT_SECRET=<from-openai>
```

## 🔍 How Token Verification Works

1. **Gateway receives Firebase token** (from query param, cookie, or header)
2. **Verifies token** using Firebase Admin SDK
3. **Extracts user_id** from decoded token
4. **Stores user_id** in authorization code
5. **Uses user_id** when generating access tokens
6. **Stores Firebase token** in access token data for later API calls

## 🔒 Security Considerations

### Current Implementation (MVP)
- ✅ Firebase tokens are verified before authorization
- ✅ Real user IDs are stored (not "demo_user")
- ✅ Tokens are stored in memory (will be lost on restart)

### Production Improvements Needed
- [ ] **Persistent token storage** - Use Redis or Database instead of in-memory
- [ ] **Token refresh** - Handle expired Firebase tokens gracefully
- [ ] **Rate limiting** - Prevent abuse of OAuth endpoints
- [ ] **CSRF protection** - Validate state parameter properly
- [ ] **Cookie-based auth** - More secure than query parameters
- [ ] **Token encryption** - Encrypt stored tokens at rest

## 📝 Testing the Integration

### 1. Test Firebase Auth is Working

```bash
# Check gateway health
curl https://closetgptrenewopenaisdk-production.up.railway.app/health

# Should return: {"status": "ok"}
```

### 2. Test OAuth Authorization (Without Login)

```bash
# This should show login page
curl "https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize?client_id=test&redirect_uri=https://chat.openai.com/aip/oauth/callback&state=test123"
```

### 3. Test OAuth Authorization (With Firebase Token)

```bash
# Get Firebase token from your frontend (after user logs in)
FIREBASE_TOKEN="your-firebase-token-here"

# Try authorization with token
curl "https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize?client_id=test&redirect_uri=https://chat.openai.com/aip/oauth/callback&state=test123&firebase_token=${FIREBASE_TOKEN}"
```

### 4. Test in ChatGPT

1. **Register your app** in OpenAI Platform (see `OPENAI_APPS_SDK_SETUP.md`)
2. **Set up Firebase credentials** in gateway service
3. **Ensure users are logged into your website**
4. **In ChatGPT, click "Connect Easy Outfit"**
5. **Should redirect to your website/login if not logged in**
6. **After login, should show consent page**
7. **After authorization, ChatGPT can access user's wardrobe**

## 🐛 Troubleshooting

### Issue: "Authentication required. Please log in first."

**Cause**: No Firebase token provided or token is invalid/expired

**Solution**:
- Ensure user is logged into your website
- Check Firebase token is being passed (query param, cookie, or header)
- Verify Firebase credentials are set in gateway environment variables

### Issue: "Firebase not initialized, cannot verify token"

**Cause**: Firebase Admin SDK failed to initialize

**Solution**:
- Check all Firebase environment variables are set
- Verify Firebase credentials are correct
- Check gateway logs for initialization errors

### Issue: Gateway shows login page even when user is logged in

**Cause**: Firebase token not being passed to gateway

**Solution**:
- Update frontend to pass Firebase token when redirecting to OAuth authorize
- Check cookie is being set with correct domain
- Verify query parameter is being passed correctly

### Issue: "Invalid or expired authentication. Please log in again."

**Cause**: Firebase token has expired

**Solution**:
- User needs to log in again to get a fresh token
- Consider implementing token refresh in frontend

## ✅ Checklist

- [ ] Firebase Admin SDK initialized in gateway
- [ ] Firebase environment variables set in Railway
- [ ] Frontend integrated to pass Firebase tokens
- [ ] Login page redirects back to OAuth flow
- [ ] Consent page shows user info when authenticated
- [ ] Authorization codes store real user_ids
- [ ] Access tokens include Firebase tokens
- [ ] API calls use Firebase tokens for authentication

## 🎉 Success!

Your OAuth gateway now requires users to be logged into your website before authorizing ChatGPT access. This ensures:

- ✅ **Security** - Only authenticated users can authorize access
- ✅ **User Identity** - Real user IDs are used for all API calls
- ✅ **Data Isolation** - Each user's data is properly isolated
- ✅ **Compliance** - Follows best practices for OAuth 2.0 authentication

---

**Next Steps:**
1. Test the integration with a real user
2. Update frontend to handle OAuth redirects
3. Deploy and test in production
4. Submit your app to OpenAI for review


