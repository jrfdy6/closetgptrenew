# 🎯 OpenAI ChatGPT App Registration - Step by Step

## ✅ Prerequisites Complete

Your gateway is live and ready:
- **Gateway URL:** https://closetgptrenewopenaisdk-production.up.railway.app
- **Health:** ✅ Passing
- **OAuth:** ✅ Implemented
- **Backend Proxy:** ✅ Working

---

## 📝 Registration Steps

### Step 1: Access OpenAI Platform

**Option A: Custom GPT Store (Simpler)**
1. Go to: https://chat.openai.com
2. Click your profile (bottom left)
3. Click **"My GPTs"**
4. Click **"Create a GPT"**

**Option B: Apps SDK Platform (If Available)**
1. Go to: https://platform.openai.com
2. Look for "Apps" or "GPT Actions" section
3. Click **"Create New App"**

---

### Step 2: Basic Information

**Name:**
```
ClosetGPT
```

**Description:**
```
Your AI-powered personal stylist and wardrobe manager. Get outfit suggestions for any occasion, manage your closet, and make better fashion choices with personalized AI recommendations.
```

**Instructions for the model:**
```
You are ClosetGPT, a personal styling assistant. You help users:
1. View and organize their wardrobe items
2. Get outfit suggestions based on occasion, weather, and style preferences
3. Make better fashion choices with AI-powered recommendations

When users ask about outfits or what to wear:
- Use the suggest-outfits endpoint with their preferences
- Present options in a friendly, fashionable way
- Consider the occasion, weather, and their personal style

When users want to see their wardrobe:
- Use the wardrobe endpoint to show their items
- Help them understand what they have
```

---

### Step 3: Configure Actions/API

**Authentication Type:** OAuth 2.0

**OAuth Configuration:**

| Field | Value |
|-------|-------|
| **Client URL** | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize` |
| **Authorization URL** | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/authorize` |
| **Token URL** | `https://closetgptrenewopenaisdk-production.up.railway.app/oauth/token` |
| **Scope** | `wardrobe:read outfits:generate` |

**API Schema:**

Import from URL:
```
https://closetgptrenewopenaisdk-production.up.railway.app/openapi.json
```

Or manually add actions:

#### Action 1: Get Wardrobe
- **Name:** `getWardrobe`
- **Method:** GET
- **URL:** `https://closetgptrenewopenaisdk-production.up.railway.app/wardrobe`
- **Description:** Get all wardrobe items for the user

#### Action 2: Suggest Outfits
- **Name:** `suggestOutfits`
- **Method:** POST
- **URL:** `https://closetgptrenewopenaisdk-production.up.railway.app/suggest-outfits`
- **Description:** Generate outfit suggestions based on occasion, style, and preferences
- **Parameters:**
  ```json
  {
    "occasion": "string (optional)",
    "style": "string (optional)",
    "weather": "string (optional)"
  }
  ```

---

### Step 4: Privacy & Legal

**Privacy Policy URL:**
```
https://closetgpt.app/privacy
```

**Terms of Service URL:**
```
https://closetgpt.app/terms
```

*(If you don't have these yet, you can use placeholder pages)*

---

### Step 5: Test Your GPT

1. Click **"Save"** or **"Publish"** (might be "Only Me" first for testing)
2. In ChatGPT, find your GPT
3. Click **"Connect"**
4. Test the OAuth flow
5. Try commands:
   - "Show me my wardrobe"
   - "What should I wear to work?"
   - "Suggest an outfit for a casual dinner"

---

## 🧪 Testing Checklist

Before submitting:

- [ ] OAuth flow works (user can connect)
- [ ] Wardrobe endpoint returns data
- [ ] Outfit suggestions work
- [ ] Responses are formatted nicely
- [ ] Error handling works gracefully

---

## 🐛 Common Issues

### Issue: "OAuth Failed"
**Fix:** Check that redirect URI matches exactly what OpenAI provides

### Issue: "API Not Responding"
**Fix:** Verify gateway URL is accessible: `curl https://closetgptrenewopenaisdk-production.up.railway.app/health`

### Issue: "Invalid Token"
**Fix:** OAuth token storage is in-memory - restart clears tokens (upgrade to Redis/DB for production)

---

## 📊 Current Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| HTTP Gateway | ✅ Live | Railway deployed |
| OAuth Flow | ✅ Working | MVP implementation |
| Wardrobe Endpoint | ✅ Ready | Proxies to main backend |
| Outfit Suggestions | ✅ Ready | Proxies to main backend |
| Firebase Auth | ⏳ TODO | Currently uses test tokens |
| User Sessions | ⏳ TODO | In-memory (use Redis for production) |

---

## 🎯 Next Steps After Registration

1. **Test with real users** in ChatGPT
2. **Add Firebase auth integration** for real user tokens
3. **Add more endpoints** (add item, stats, mark worn)
4. **Improve error messages** for better UX
5. **Submit to GPT Store** for public access

---

## 📞 Need Help?

If you encounter issues during registration:
1. Check the OpenAI developer docs
2. Verify all URLs are accessible
3. Test OAuth flow manually
4. Check Railway logs for errors

---

**You're ready to register! Follow these steps and let me know if you hit any blockers.** 🚀

