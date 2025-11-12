# 🚀 OpenAI Apps SDK Registration Guide

## ✅ Your Gateway is Ready!

**All systems operational:**
- ✅ HTTP Gateway deployed
- ✅ OAuth endpoints live
- ✅ Manifest accessible
- ✅ OpenAPI spec auto-generated

---

## 📋 Step-by-Step Registration

### Step 1: Access OpenAI Apps Platform

**Go to:** https://platform.openai.com/apps

(Or if that doesn't exist yet, try: https://chatgpt.com/gpts/editor)

---

### Step 2: Create New App

Click **"Create App"** or **"New App"**

---

### Step 3: Basic Information

**App Name:**
```
Easy Outfit
```

**Short Description:**
```
AI-powered wardrobe manager and outfit generator
```

**Detailed Description:**
```
Easy Outfit helps you manage your digital wardrobe and get personalized outfit suggestions. Get AI-powered recommendations for any occasion, style, or weather condition. Organize your closet and make better fashion choices with intelligent outfit generation.
```

**Category:**
```
Lifestyle
```

---

### Step 4: Configure Authentication (OAuth 2.0)

**Authentication Type:** OAuth 2.0

**Authorization URL:**
```
https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize
```

**Token Exchange URL:**
```
https://closetgptrenewopenaisdk-production.up.railway.app/oauth/token
```

**Client ID:** (Will be provided by OpenAI after registration)

**Client Secret:** (Will be provided by OpenAI after registration)

**Scopes:**
```
wardrobe:read outfits:generate
```

**Authorization Method:**
```
POST with form data
```

---

### Step 5: API Configuration

**API Type:** OpenAPI 3.0

**OpenAPI Specification URL:**
```
https://closetgptrenewopenaisdk-production.up.railway.app/openapi.json
```

**Or** if they ask for the manifest:
```
https://closetgptrenewopenaisdk-production.up.railway.app/.well-known/ai-plugin.json
```

**Base URL:**
```
https://closetgptrenewopenaisdk-production.up.railway.app
```

---

### Step 6: Privacy & Legal

**Privacy Policy URL:**
```
https://easyoutfitapp.com/privacy
```

**Terms of Service URL:**
```
https://easyoutfitapp.com/terms
```

**Contact Email:**
```
support@closetgpt.app
```

---

### Step 7: App Icon/Logo (Optional)

Upload a logo or provide URL:
```
https://easyoutfitapp.com/logo.png
```

Recommended size: 512x512px PNG

---

## 🧪 Step 8: Test Your App

### In ChatGPT Interface

1. **Find your app** in the Apps menu or GPT builder
2. **Click "Connect"** or "Authenticate"
3. **OAuth flow starts:**
   - Redirects to authorization URL
   - Returns auth code
   - Exchanges for access token
4. **Try commands:**
   ```
   "Show me my wardrobe"
   "What should I wear to work today?"
   "Suggest an outfit for a wedding"
   "Help me plan outfits for this week"
   ```

---

## 🔍 Available API Endpoints

Your app exposes these endpoints to ChatGPT:

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/health` | GET | Health check | No |
| `/.well-known/ai-plugin.json` | GET | App manifest | No |
| `/oauth/authorize` | GET | Start OAuth | No |
| `/oauth/token` | POST | Get access token | No |
| `/test-proxy` | GET | Test backend connection | No |
| `/wardrobe` | GET | Get user's wardrobe | Yes (OAuth) |
| `/suggest-outfits` | POST | Generate outfits | Yes (OAuth) |

---

## 📊 OAuth Flow

```
User in ChatGPT
  ↓ clicks "Connect Easy Outfit"
ChatGPT → GET /oauth/authorize
  ↓ Gateway generates auth code
  ↓ Redirects: callback?code=XXX&state=YYY
ChatGPT → POST /oauth/token (grant_type=authorization_code&code=XXX)
  ↓ Gateway returns access_token
ChatGPT stores token
  ↓
User: "Show me my wardrobe"
  ↓
ChatGPT → GET /wardrobe (Authorization: Bearer <token>)
  ↓ Gateway verifies token
  ↓ Proxies to main backend
Gateway returns wardrobe data
```

---

## 🔧 Important URLs to Copy

**For OpenAI Registration Form:**

| Field | Value |
|-------|-------|
| Manifest URL | `https://closetgptrenewopenaisdk-production.up.railway.app/.well-known/ai-plugin.json` |
| OpenAPI URL | `https://closetgptrenewopenaisdk-production.up.railway.app/openapi.json` |
| Authorization URL | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize` |
| Token URL | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/token` |
| Callback URL | `https://chat.openai.com/aip/oauth/callback` |

---

## ⚠️ Current Limitations (MVP)

1. **OAuth is simplified** - Auto-approves without user consent screen
2. **No Firebase integration yet** - Uses test user
3. **In-memory token storage** - Tokens lost on restart
4. **Limited endpoints** - Only wardrobe + suggest-outfits

### Production Improvements Needed:

- [ ] Real Firebase Auth integration
- [ ] Persistent token storage (Redis/Database)
- [ ] User consent screen
- [ ] More endpoints (add item, mark worn, stats)
- [ ] Privacy policy page
- [ ] Terms of service page

---

## 🎉 You're Ready to Register!

Your app is fully functional for testing with ChatGPT Apps SDK.

**Next:** Go to the OpenAI Apps platform and follow the steps above!

Let me know if you need help with any specific step. 🚀

