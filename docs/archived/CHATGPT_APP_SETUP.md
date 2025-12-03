# 🚀 ChatGPT App Setup Guide

## ✅ Your Gateway is Ready!

**Gateway URL:** https://closetgptrenewopenaisdk-production.up.railway.app

**Status:**
- ✅ HTTP server running
- ✅ OAuth endpoints implemented
- ✅ Proxying to main backend
- ✅ Ready for ChatGPT integration

---

## 📋 Step 1: Register Your App in OpenAI

### Go to OpenAI Platform

1. Visit: https://platform.openai.com/apps
2. Click **"Create App"** or **"New App"**
3. Fill in the details below

---

## 🔧 Step 2: App Configuration

### Basic Information

**App Name:** Easy Outfit

**Description:**
```
AI-powered wardrobe manager and personal stylist. Get outfit suggestions for any occasion, manage your closet, and make better fashion choices with AI assistance.
```

**Category:** Lifestyle / Fashion

---

## 🔐 Step 3: OAuth Configuration

### OAuth Settings

**Client URL:**
```
https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize
```

**Authorization URL:**
```
https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize
```

**Token URL:**
```
https://closetgptrenewopenaisdk-production.up.railway.app/oauth/token
```

**Scope:**
```
wardrobe:read outfits:generate
```

**Redirect URI (from OpenAI):**
```
https://chat.openai.com/aip/oauth/callback
```

---

## 🔌 Step 4: API Configuration

### OpenAPI Schema URL

```
https://closetgptrenewopenaisdk-production.up.railway.app/openapi.json
```

FastAPI automatically generates this OpenAPI spec.

---

## 📝 Step 5: App Metadata

**Logo URL:** (Optional - add your logo)

**Contact Email:**
```
support@closetgpt.app
```

**Privacy Policy URL:**
```
https://easyoutfitapp.com/privacy
```

**Terms of Service URL:**
```
https://easyoutfitapp.com/terms
```

---

## 🧪 Step 6: Test Your App

### In ChatGPT Interface

1. Find your app in the Apps menu
2. Click **"Connect"**
3. OAuth flow starts
4. Try commands:
   - "Show me my wardrobe"
   - "Suggest an outfit for work"
   - "What should I wear to a wedding?"

---

## 🔍 Available Endpoints

Your gateway currently supports:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/oauth/authorize` | GET | Start OAuth flow |
| `/oauth/token` | POST | Exchange code for token |
| `/test-proxy` | GET | Test backend connection |
| `/wardrobe` | GET | Get user's wardrobe items |
| `/suggest-outfits` | POST | Generate outfit suggestions |

---

## 📊 Current OAuth Flow (MVP)

1. User clicks "Connect Easy Outfit" in ChatGPT
2. Redirects to `/oauth/authorize`
3. Auto-generates authorization code
4. Redirects back to ChatGPT
5. ChatGPT calls `/oauth/token`
6. Returns access token
7. ChatGPT uses token for API calls

**Note:** This is a simplified flow for testing. Production should integrate with Firebase Auth.

---

## 🚀 Next Steps

1. **Register app** in OpenAI Platform
2. **Test OAuth flow** in ChatGPT
3. **Add Firebase integration** for real user authentication
4. **Add more endpoints** (add items, mark worn, etc.)
5. **Submit for review** to OpenAI GPT Store

---

## 🔧 Environment Variables

Your gateway uses:

```
MAIN_API_URL=https://closetgptrenew-production.up.railway.app
API_KEY=dqvNQIiCRXmUSsEHFpVvWhotNkwAspNGS4nH3u2r844
PORT=3002
```

Optional (will auto-generate if not set):
```
OAUTH_CLIENT_ID=closetgpt-chatgpt-app
OAUTH_CLIENT_SECRET=(auto-generated)
```

---

## ✅ You're Ready!

Your HTTP gateway is deployed and OAuth-enabled. Time to register with OpenAI! 🎉

