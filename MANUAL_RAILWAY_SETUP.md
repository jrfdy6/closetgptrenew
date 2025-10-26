# 📋 Manual Railway Setup - Add MCP Service

Follow these exact steps in the Railway dashboard.

## Step 1: Open Your Railway Project

1. Go to: **https://railway.app/dashboard**
2. Find and click on your project: **`closetgptrenew`**

You should see your existing service (main backend) already running.

---

## Step 2: Add New Service

1. In your project, click the **"+ New"** button (top right)
2. Select **"GitHub Repo"**
3. Choose: **`jrfdy6/closetgptrenew`** (your repo)
4. Railway will create a new service

---

## Step 3: Name the Service

1. Click on the new service card
2. Go to **Settings** (gear icon)
3. Under **Service Name**, change it to: `closetgptrenewopenaisdk`
4. Click **Save**

---

## Step 4: Configure Root Directory

Still in Settings:

1. Find **Root Directory**
2. Set it to: `backend`
3. Click **Save**

---

## Step 5: Configure Start Command

Still in Settings:

1. Find **Start Command** or **Custom Start Command**
2. Set it to: `bash start_mcp.sh`
3. Click **Save**

---

## Step 6: Add Environment Variables

1. Go to **Variables** tab
2. Click **"+ New Variable"**
3. Add these **3 variables**:

**Variable 1:**
```
Name: MAIN_API_URL
Value: https://closetgptrenew-production.up.railway.app
```

**Variable 2:**
```
Name: API_KEY
Value: dqvNQIiCRXmUSsEHFpVvWhotNkwAspNGS4nH3u2r844
```

**Variable 3:**
```
Name: PORT
Value: 3002
```

4. Click **Save** after each

---

## Step 7: Deploy

1. Go to **Deployments** tab
2. Railway should auto-deploy since code is already pushed
3. Watch the build logs
4. Wait for **"Success"** ✅

---

## Step 8: Get Your MCP Service URL

1. Go to **Settings** → **Domains**
2. Railway auto-generates a domain like:
   `closetgptrenewopenaisdk-production.up.railway.app`
3. **Copy this URL** - you'll need it for ChatGPT Apps SDK

---

## ✅ Verification

Your Railway project now has **2 services**:

### Service 1: Main Backend (Unchanged)
- Name: `closetgptrenew-production` (or similar)
- URL: `https://closetgptrenew-production.up.railway.app`
- Status: ✅ Running

### Service 2: MCP Server (New)
- Name: `closetgptrenewopenaisdk`
- URL: `https://closetgptrenewopenaisdk-production.up.railway.app`
- Status: ✅ Running (after deployment)

---

## 🧪 Test It

Once deployed, test:

```bash
curl https://closetgptrenewopenaisdk-production.up.railway.app/
```

Should return JSON with service info.

---

## ⚠️ Important Notes

- **Each service deploys independently**
- **Updating one doesn't affect the other**
- **Both are in the same Railway project (same billing)**
- **Each has its own environment variables**
- **Each has its own logs and metrics**

---

## Next Steps After Deployment

1. ✅ Copy your MCP service URL
2. Register in OpenAI Apps SDK
3. Connect to ChatGPT
4. Test your app!

---

That's it! No CLI needed - all done through Railway dashboard.

