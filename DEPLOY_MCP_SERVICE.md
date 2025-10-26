# 🚀 Deploy MCP Service - Separate from Main App

This creates a **completely separate** Railway service just for the MCP server.

## ⚠️ Important: This is SEPARATE from your main app

Your main app (`closetgptrenew-production.railway.app`) stays untouched.

---

## Option 1: Railway CLI (Recommended - I can do this)

### Install Railway CLI

```bash
npm install -g @railway/cli
```

### Login to Railway

```bash
railway login
```

### Deploy MCP Service

```bash
cd /Users/johnniefields/Desktop/Cursor/closetgptrenew/backend

# Create new project
railway init

# Name it: closetgpt-mcp-server

# Set environment variables
railway variables set MAIN_API_URL=https://closetgptrenew-production.railway.app
railway variables set API_KEY=dqvNQIiCRXmUSsEHFpVvWhotNkwAspNGS4nH3u2r844
railway variables set PORT=3002

# Deploy
railway up
```

---

## Option 2: Railway Dashboard (Manual)

If CLI doesn't work, do this in Railway dashboard:

### Step 1: Create New Project
1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Click **"Empty Project"**
4. Name: `ClosetGPT MCP Server`

### Step 2: Add Service from GitHub
1. Click **"+ New"** → **"GitHub Repo"**
2. Select: `closetgptrenew`
3. **Important:** This creates a NEW service, not touching your existing one

### Step 3: Configure THIS Service Only

In the **new MCP service** settings:

**Root Directory:**
```
backend
```

**Start Command:**
```
bash start_mcp.sh
```

**Environment Variables:**
```
MAIN_API_URL=https://closetgptrenew-production.railway.app
API_KEY=dqvNQIiCRXmUSsEHFpVvWhotNkwAspNGS4nH3u2r844
PORT=3002
```

### Step 4: Deploy
Railway auto-deploys from GitHub.

---

## ✅ Result

You'll have **TWO separate Railway projects:**

### Project 1: Main App (Existing)
- URL: `https://closetgptrenew-production.railway.app`
- Runs: Your main FastAPI backend
- **Unchanged** - nothing we did touches this

### Project 2: MCP Server (New)
- URL: `https://closetgpt-mcp-xxxxx.railway.app` (Railway assigns)
- Runs: ONLY the MCP server (`mcp_server.py`)
- **Separate** - independent deployment, scaling, logs

---

## 🔍 How to Verify They're Separate

In Railway dashboard, you'll see:
```
Projects:
  ├─ closetgptrenew-backend (your main app)
  └─ closetgpt-mcp-server (new MCP service)
```

Each has its own:
- Deployment logs
- Environment variables
- Scaling settings
- URL

---

## 💡 Why This is Better

1. **Safe**: Main app is never touched
2. **Independent**: Each service scales separately
3. **Clean**: MCP issues don't affect main app
4. **Easy**: Can delete MCP service without affecting anything

---

## API Key Note

The API key `dqvNQIiCRXmUSsEHFpVvWhotNkwAspNGS4nH3u2r844` is for the MCP server to authenticate with your main API.

You'll need to add authentication logic to your main API to accept this key, OR we can use OAuth later.

For now, the MCP server will call your main API endpoints. Some will work, some won't until auth is set up. That's fine for testing.

