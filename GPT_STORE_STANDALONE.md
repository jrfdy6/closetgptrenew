# 🚀 Standalone GPT Store Service

This is a **completely separate** FastAPI service that handles ONLY GPT Store integration.
It won't interfere with your main app!

## ✨ What It Does

1. **OAuth 2.0 authentication** for OpenAI Custom GPTs
2. **GPT Actions API** that proxies requests to your main API
3. **Legal pages** (privacy policy, terms)

## 🎯 Two Deployment Options

### **Option 1: Deploy as Separate Railway Service** (Recommended)

#### Step 1: Create New Railway Project

1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `closetgptrenew` repo
5. Name it: "ClosetGPT GPT Store Service"

#### Step 2: Configure Root Directory

In Railway project settings:
- **Root Directory:** `/backend`
- **Start Command:** `python gpt_store_app.py`
- **Port:** `3002` (or let Railway assign)

#### Step 3: Add Environment Variables

```bash
GPT_OAUTH_CLIENT_ID=closetgpt-custom-gpt
GPT_OAUTH_CLIENT_SECRET=<generate-with-python>
JWT_SECRET=<generate-with-python>
API_BASE_URL=https://your-gpt-store-service.railway.app
MAIN_API_URL=https://closetgptrenew-production.railway.app
```

Generate secrets:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 4: Deploy

Push to GitHub - Railway auto-deploys!

---

### **Option 2: Run Locally for Testing**

```bash
cd backend

# Set environment variables
export GPT_OAUTH_CLIENT_ID=closetgpt-custom-gpt
export GPT_OAUTH_CLIENT_SECRET=your-secret
export JWT_SECRET=your-jwt-secret
export API_BASE_URL=http://localhost:3002
export MAIN_API_URL=https://closetgptrenew-production.railway.app

# Run the service
python gpt_store_app.py
```

Visit: http://localhost:3002

---

## 🧪 Test Endpoints

Once deployed, test:

```bash
# OAuth metadata
curl https://your-gpt-store-url.railway.app/oauth/.well-known/oauth-authorization-server

# Privacy policy
curl https://your-gpt-store-url.railway.app/privacy

# Root endpoint
curl https://your-gpt-store-url.railway.app/
```

---

## 🤖 Configure Custom GPT

In ChatGPT GPT Builder:

### Actions Configuration

**Authentication:**
- Type: OAuth
- Client ID: `closetgpt-custom-gpt`
- Client Secret: (your generated secret)
- Authorization URL: `https://your-gpt-store-url.railway.app/oauth/authorize`
- Token URL: `https://your-gpt-store-url.railway.app/oauth/token`
- Scope: `wardrobe:read wardrobe:write outfits:read outfits:write`

### OpenAPI Schema

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "ClosetGPT API",
    "version": "1.0.0"
  },
  "servers": [
    {"url": "https://your-gpt-store-url.railway.app"}
  ],
  "paths": {
    "/gpt/wardrobe": {
      "get": {
        "operationId": "getWardrobe",
        "summary": "Get wardrobe items",
        "parameters": [
          {
            "name": "type",
            "in": "query",
            "schema": {"type": "string"}
          },
          {
            "name": "limit",
            "in": "query",
            "schema": {"type": "integer", "default": 50}
          }
        ]
      }
    },
    "/gpt/stats": {
      "get": {
        "operationId": "getStats",
        "summary": "Get wardrobe statistics"
      }
    }
  },
  "components": {
    "securitySchemes": {
      "OAuth2": {
        "type": "oauth2",
        "flows": {
          "authorizationCode": {
            "authorizationUrl": "https://your-gpt-store-url.railway.app/oauth/authorize",
            "tokenUrl": "https://your-gpt-store-url.railway.app/oauth/token",
            "scopes": {
              "wardrobe:read": "Read wardrobe",
              "wardrobe:write": "Modify wardrobe"
            }
          }
        }
      }
    }
  },
  "security": [{"OAuth2": ["wardrobe:read", "wardrobe:write"]}]
}
```

### Legal URLs

- Privacy Policy: `https://your-gpt-store-url.railway.app/privacy`
- Terms of Service: `https://your-gpt-store-url.railway.app/terms`

---

## ✅ Benefits of Standalone Approach

1. **No conflicts** - Doesn't touch your main app
2. **Easy to debug** - Isolated service
3. **Independent scaling** - Scale GPT Store separately
4. **Easy to update** - Modify without affecting main app
5. **Clean separation** - GPT Store logic is self-contained

---

## 🔧 How It Works

The standalone service:
1. Handles OAuth authorization for ChatGPT
2. Proxies authenticated requests to your main API
3. Transforms responses for GPT consumption
4. Provides legal pages required by OpenAI

**Flow:**
```
ChatGPT → GPT Store Service (OAuth) → Main API → Database
```

---

## 📝 Next Steps

1. Deploy the service to Railway
2. Test all endpoints
3. Configure your Custom GPT in ChatGPT
4. Test the authorization flow
5. Publish to GPT Store!

---

## 🐛 Troubleshooting

**Service won't start:**
- Check Python 3.11 is available
- Verify all environment variables are set
- Check Railway logs

**OAuth fails:**
- Ensure secrets match in both Railway and GPT Builder
- Check API_BASE_URL is correct
- Verify MAIN_API_URL points to your main API

**Main API proxy fails:**
- Check MAIN_API_URL is accessible
- Verify your main API endpoints are working
- Check CORS settings on main API

---

## 🎉 Success!

Once deployed, you have a dedicated GPT Store service that:
- ✅ Doesn't interfere with your main app
- ✅ Is easy to maintain and update
- ✅ Follows OpenAI's requirements
- ✅ Can be scaled independently

Ready to deploy and create your Custom GPT! 🚀

