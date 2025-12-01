# 🚀 OpenAI Apps SDK Setup Guide - Easy Outfit

## Overview

This guide will help you set up your Easy Outfit app to work directly with OpenAI and ChatGPT using the **OpenAI Apps SDK** (not Custom GPTs). This integration uses **OAuth 2.0** authentication so users can connect their accounts securely.

## ✅ Prerequisites

1. **Gateway Service Deployed**: Your OAuth gateway should be deployed at:
   ```
   https://closetgptrenewopenaisdk-production.up.railway.app
   ```

2. **Main Backend Running**: Your main backend at:
   ```
   https://closetgptrenew-production.up.railway.app
   ```

3. **OpenAI Developer Account**: Access to https://platform.openai.com

## 🔐 Why OAuth is Required

The OpenAI Apps SDK requires **OAuth 2.0** authentication because:

- **Security**: Users authenticate with your app, not OpenAI
- **User Identity**: Each user's data is isolated and secure
- **Compliance**: Follows OAuth 2.0 standard for third-party integrations
- **Privacy**: Users control what data ChatGPT can access

## 📋 Step-by-Step Registration

### Step 1: Access OpenAI Platform

1. Go to: **https://platform.openai.com/apps**
2. If that URL doesn't work, try: **https://chatgpt.com/gpts/editor**
3. Sign in with your OpenAI account

### Step 2: Create New App

1. Click **"Create App"** or **"New App"**
2. Choose **"HTTP API"** or **"Apps SDK"** option (not Custom GPT)

### Step 3: Basic Information

Fill in the app details:

| Field | Value |
|-------|-------|
| **App Name** | `Easy Outfit` |
| **Short Description** | `AI-powered wardrobe manager and outfit generator` |
| **Detailed Description** | `Easy Outfit helps you manage your digital wardrobe and get personalized outfit suggestions. Get AI-powered recommendations for any occasion, style, or weather condition. Organize your closet and make better fashion choices with intelligent outfit generation.` |
| **Category** | `Lifestyle` or `Fashion` |
| **App Icon** | (Optional) Upload a logo or use: `https://easyoutfitapp.com/logo.png` |

### Step 4: Configure Authentication (OAuth 2.0)

This is the **critical step** - you need OAuth to authenticate users.

**Authentication Type:** Select **OAuth 2.0**

Then fill in these values:

| Field | Value |
|-------|-------|
| **Authorization URL** | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize` |
| **Token Exchange URL** | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/token` |
| **Client ID** | *(Will be provided by OpenAI after registration)* |
| **Client Secret** | *(Will be provided by OpenAI after registration)* |
| **Scopes** | `wardrobe:read outfits:generate` |
| **Authorization Method** | `POST with form data` or `application/x-www-form-urlencoded` |
| **Redirect URI** | `https://chat.openai.com/aip/oauth/callback` |

**Important Notes:**
- OpenAI will provide you with a **Client ID** and **Client Secret** after you save the OAuth configuration
- You'll need to add these to your gateway environment variables:
  ```
  OAUTH_CLIENT_ID=<from-openai>
  OAUTH_CLIENT_SECRET=<from-openai>
  ```

### Step 5: API Configuration

Configure how ChatGPT will access your API:

| Field | Value |
|-------|-------|
| **API Type** | `OpenAPI 3.0` |
| **OpenAPI Specification URL** | `https://closetgptrenewopenaisdk-production.up.railway.app/openapi.json` |
| **Base URL** | `https://closetgptrenewopenaisdk-production.up.railway.app` |

**Alternative:** If OpenAI asks for a manifest file:
- **Manifest URL**: `https://closetgptrenewopenaisdk-production.up.railway.app/.well-known/ai-plugin.json`

### Step 6: Privacy & Legal

Add your legal pages:

| Field | Value |
|-------|-------|
| **Privacy Policy URL** | `https://easyoutfitapp.com/privacy` |
| **Terms of Service URL** | `https://easyoutfitapp.com/terms` |
| **Contact Email** | `support@easyoutfitapp.com` |

### Step 7: Save and Get Credentials

1. **Save** your app configuration
2. OpenAI will generate:
   - **Client ID** - Copy this
   - **Client Secret** - Copy this (show it once!)
3. **Add these to your Railway gateway service:**

Go to Railway → Your Gateway Service → Variables:
```
OAUTH_CLIENT_ID=<paste-client-id-here>
OAUTH_CLIENT_SECRET=<paste-client-secret-here>
GATEWAY_URL=https://closetgptrenewopenaisdk-production.up.railway.app
MAIN_BACKEND_URL=https://closetgptrenew-production.up.railway.app
API_KEY=<your-api-key>
```

## 🧪 Step 8: Test Your Integration

### In ChatGPT Interface

1. **Open ChatGPT** (chat.openai.com)
2. **Find your app** in the Apps menu or GPT builder
3. **Click "Connect"** or "Authenticate"
4. **OAuth flow starts:**
   - User is redirected to your authorization page
   - User clicks "Authorize"
   - Returns to ChatGPT with authorization code
   - ChatGPT exchanges code for access token
   - Connection is established!

5. **Try commands:**
   ```
   "Show me my wardrobe"
   "What should I wear to work today?"
   "Suggest an outfit for a wedding"
   "Help me plan outfits for this week"
   ```

## 🔍 How OAuth Flow Works

```
User in ChatGPT
  ↓ clicks "Connect Easy Outfit"
ChatGPT → GET /oauth/authorize (with client_id, redirect_uri, state)
  ↓ Your gateway shows consent page
User clicks "Authorize"
  ↓ Gateway generates authorization code
Gateway → Redirects: callback?code=XXX&state=YYY
  ↓
ChatGPT → POST /oauth/token (grant_type=authorization_code&code=XXX)
  ↓ Gateway validates code and generates access_token
Gateway → Returns: {access_token, refresh_token, expires_in}
  ↓
ChatGPT stores token
  ↓
User: "Show me my wardrobe"
  ↓
ChatGPT → GET /wardrobe (Authorization: Bearer <token>)
  ↓ Gateway verifies token
  ↓ Gateway proxies to main backend with user_id
Gateway → Returns wardrobe data
```

## 📊 Current API Endpoints

Your gateway exposes these endpoints to ChatGPT:

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/.well-known/ai-plugin.json` | GET | App manifest | No |
| `/openapi.json` | GET | OpenAPI spec | No |
| `/oauth/authorize` | GET | Start OAuth flow | No |
| `/oauth/consent` | GET | User consent page | No |
| `/oauth/token` | POST | Get access token | No |
| `/health` | GET | Health check | No |
| `/wardrobe` | GET | Get user's wardrobe | Yes (OAuth) |
| `/suggest-outfits` | POST | Generate outfits | Yes (OAuth) |

## 🔧 Environment Variables

Make sure your gateway service has these environment variables set in Railway:

```bash
# Required
GATEWAY_URL=https://closetgptrenewopenaisdk-production.up.railway.app
MAIN_BACKEND_URL=https://closetgptrenew-production.up.railway.app
API_KEY=<your-api-key>

# OAuth (from OpenAI after registration)
OAUTH_CLIENT_ID=<from-openai>
OAUTH_CLIENT_SECRET=<from-openai>

# Optional (will auto-generate if not set)
OAUTH_REDIRECT_URI=https://chat.openai.com/aip/oauth/callback
PORT=8080
```

## 🎯 Next Steps

1. **Register your app** in OpenAI Platform (follow steps above)
2. **Add OAuth credentials** to Railway environment variables
3. **Redeploy gateway** if needed
4. **Test OAuth flow** in ChatGPT
5. **Verify endpoints** work correctly
6. **Submit for review** if you want to publish your app

## ✅ Firebase Auth Integration

**Firebase Auth is now integrated!** Users must be logged into your website before authorizing ChatGPT access.

- ✅ **User Authentication Required** - OAuth consent page checks for Firebase login
- ✅ **Real User IDs** - Uses actual Firebase user_id (not "demo_user")
- ✅ **Secure Token Flow** - Firebase tokens are verified and stored

See `OAUTH_FIREBASE_INTEGRATION.md` for details on frontend integration.

## ⚠️ Current Limitations (MVP)

1. **In-memory tokens** - Tokens lost on restart (use Redis/DB in production)
2. **No PKCE support** - OAuth 2.0 basic flow (PKCE is recommended for production)
3. **Token refresh** - Need to handle expired Firebase tokens gracefully

### Production Improvements Needed:

- [x] **Real Firebase Auth integration** - ✅ COMPLETE - Users must log in before authorization
- [ ] **Persistent token storage** - Use Redis or Database instead of in-memory
- [ ] **PKCE support** - Add Proof Key for Code Exchange for enhanced security
- [ ] **More endpoints** - Add items, mark worn, stats, etc.
- [ ] **Token expiration handling** - Proper refresh token flow for Firebase tokens
- [ ] **Rate limiting** - Prevent abuse
- [ ] **Cookie-based auth** - More secure than query parameters
- [ ] **OAuth discovery endpoint** - Add `/.well-known/oauth-authorization-server` metadata

## 🔗 Important URLs Reference

Copy these URLs for the OpenAI registration form:

| Field | URL |
|-------|-----|
| **Manifest URL** | `https://closetgptrenewopenaisdk-production.up.railway.app/.well-known/ai-plugin.json` |
| **OpenAPI URL** | `https://closetgptrenewopenaisdk-production.up.railway.app/openapi.json` |
| **Authorization URL** | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize` |
| **Token URL** | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/token` |
| **Callback URL** | `https://chat.openai.com/aip/oauth/callback` |

## ✅ Checklist

- [ ] Gateway service deployed and accessible
- [ ] Health check works: `https://closetgptrenewopenaisdk-production.up.railway.app/health`
- [ ] Manifest accessible: `https://closetgptrenewopenaisdk-production.up.railway.app/.well-known/ai-plugin.json`
- [ ] OpenAPI spec accessible: `https://closetgptrenewopenaisdk-production.up.railway.app/openapi.json`
- [ ] App registered in OpenAI Platform
- [ ] OAuth credentials added to Railway
- [ ] OAuth flow tested in ChatGPT
- [ ] Endpoints working with authentication

## 🎉 You're Ready!

Your app is now set up to work with OpenAI Apps SDK using OAuth 2.0 authentication!

**Next:** Test the integration and start using your app with ChatGPT! 🚀

## 📞 Need Help?

If you run into issues:
1. Check gateway logs in Railway
2. Verify all environment variables are set
3. Test endpoints manually with curl/Postman
4. Check OpenAI Platform for error messages

---

**Remember:** OAuth is required for the OpenAI Apps SDK because it ensures secure, user-authenticated access to your application's data.

