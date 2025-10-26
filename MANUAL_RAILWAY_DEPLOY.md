# 📝 Manual Railway Deployment - Step by Step

Follow these exact steps in the Railway dashboard to add the MCP service.

## 🎯 Goal

Add a **new service** called `closetgptrenewopenaisdk` to your existing Railway project, keeping your main app unchanged.

---

## Step 1: Open Your Railway Project

1. Go to: **https://railway.app/dashboard**
2. Find and click on your **"closetgptrenew"** project
3. You should see your existing service(s)

---

## Step 2: Add New Service

1. Click the **"+ New"** button (top right)
2. Select **"GitHub Repo"**
3. Choose repository: **`jrfdy6/closetgptrenew`** (your repo)
4. Railway will ask you to configure the service

---

## Step 3: Configure the New Service

### Service Name
When Railway asks for a name, enter:
```
closetgptrenewopenaisdk
```

### Settings → General

Click on the service → **Settings** tab:

| Setting | Value |
|---------|-------|
| **Service Name** | `closetgptrenewopenaisdk` |
| **Root Directory** | `backend` |
| **Watch Paths** | `backend/**` |

### Settings → Deploy

| Setting | Value |
|---------|-------|
| **Start Command** | `bash start_mcp.sh` |
| **Build Command** | (leave empty) |
| **Restart Policy** | On Failure |

---

## Step 4: Add Environment Variables

Click on the service → **Variables** tab → **"+ New Variable"**

Add these **3 variables** (click "+ New Variable" for each):

### Variable 1:
```
Name:  MAIN_API_URL
Value: https://closetgptrenew-production.up.railway.app
```

### Variable 2:
```
Name:  API_KEY
Value: dqvNQIiCRXmUSsEHFpVvWhotNkwAspNGS4nH3u2r844
```

### Variable 3:
```
Name:  PORT
Value: 3002
```

Click **"Add"** after each one.

---

## Step 5: Deploy

1. The service should automatically start deploying
2. Watch the **"Deployments"** tab
3. Build should take 2-3 minutes

### Build Process Will:
- ✅ Install Python 3.11
- ✅ Install MCP SDK and dependencies
- ✅ Start the MCP server with `start_mcp.sh`
- ✅ Assign a public URL

---

## Step 6: Get Your MCP Service URL

Once deployment shows **"Success"** ✅:

1. Go to **Settings** → **Networking**
2. You'll see a URL like: `closetgptrenewopenaisdk-production.up.railway.app`
3. **Copy this URL** - you'll need it for ChatGPT

---

## Step 7: Verify It's Working

Test the URL:

```bash
curl https://closetgptrenewopenaisdk-production.up.railway.app/
```

Should return something (even an error is OK - means it's running).

---

## ✅ Final Result

You now have **2 services** in your Railway project:

### Service 1: Main App (Unchanged)
- **Name:** closetgptrenew-production
- **URL:** https://closetgptrenew-production.up.railway.app
- **Status:** Running as before

### Service 2: MCP Server (New)
- **Name:** closetgptrenewopenaisdk
- **URL:** https://closetgptrenewopenaisdk-production.up.railway.app
- **Status:** Running

Both are independent - you can restart, update, or scale each separately.

---

## 🎉 Next Steps After Deployment

Once your MCP service is deployed and you have the URL:

1. **Test the MCP endpoint**
2. **Register in OpenAI Apps SDK** (https://platform.openai.com/apps)
3. **Connect to ChatGPT**
4. **Test with real users**

---

## 🐛 Troubleshooting

### Deployment Fails

Check Railway logs:
- Click service → "Deployments" → Click latest deployment → View logs
- Look for errors in build or start process

### MCP SDK Not Installing

Make sure `start_mcp.sh` has:
```bash
pip install mcp httpx --quiet
```

### Service Won't Start

Check:
- Environment variables are set correctly
- Start command is `bash start_mcp.sh`
- Root directory is `backend`

---

**Follow these steps and let me know when the deployment is complete!** 

I'll help you test and connect to ChatGPT once the service is live.

