# 🚀 Quick Start: Easy Outfit MCP App

Get your ChatGPT native app running in under 30 minutes.

## Step 1: Install Dependencies (2 min)

```bash
cd backend

# Install MCP SDK
pip install mcp

# Or install all MCP requirements
pip install -r requirements-mcp.txt
```

## Step 2: Test Locally (5 min)

```bash
# Quick test
./test-mcp-local.sh
```

This will:
- ✅ Check if MCP SDK is installed
- ✅ Start MCP server
- ✅ Open MCP Inspector (interactive testing UI)

### In MCP Inspector:

1. You'll see all 6 tools listed
2. Click any tool to test it
3. Provide test parameters
4. See the response with UI components

**Test these first:**
- `get_wardrobe_stats` (no params needed)
- `get_wardrobe` with `{"type": "all"}`
- `suggest_outfits` with `{"occasion": "work"}`

## Step 3: Deploy to Railway (10 min)

### Create New Railway Project

1. Go to Railway dashboard
2. "New Project" → "Deploy from GitHub"
3. Select `closetgptrenew` repo
4. Name it: "Easy Outfit MCP Server"

### Configure Service

**Root Directory:** `/backend`

**Start Command:** `python mcp_server.py`

**Environment Variables:**
```bash
MAIN_API_URL=https://closetgptrenew-production.railway.app
API_KEY=<your-api-key>
```

### Deploy

Push to GitHub - Railway auto-deploys!

## Step 4: Connect to ChatGPT (10 min)

### Get Your MCP Server URL

From Railway: `https://closetgpt-mcp.railway.app`

### Register in Apps SDK

1. Go to [OpenAI Apps SDK](https://platform.openai.com/apps)
2. Click "Create New App"
3. Fill in details:
   - **Name:** Easy Outfit
   - **Description:** AI wardrobe management & outfit recommendations
   - **Category:** Lifestyle
   - **MCP Server URL:** Your Railway URL

4. Add **App Metadata:**
   - **Privacy Policy:** `https://easyoutfitapp.com/privacy`
   - **Terms:** `https://easyoutfitapp.com/terms`
   - **Icon:** Upload your logo (512x512 PNG)

### Test in ChatGPT

1. Open ChatGPT
2. Your app will appear in available apps
3. Start a conversation:
   ```
   "Show me my wardrobe"
   "What should I wear to a wedding?"
   "Add a blue shirt to my wardrobe"
   ```

## Step 5: Submit for Review (5 min)

1. Test thoroughly in ChatGPT
2. Ensure all tools work correctly
3. Click "Submit for Review"
4. Wait 1-3 business days for approval

## 🎉 Done!

Your app will be live in ChatGPT once approved!

---

## Troubleshooting

### MCP Server Won't Start

```bash
# Check Python version (need 3.11+)
python --version

# Install MCP SDK
pip install mcp

# Check imports
python -c "import mcp; print('MCP OK')"
```

### Tools Not Working

```bash
# Check main API is accessible
curl https://closetgptrenew-production.railway.app/api/wardrobe/test

# Check environment variables
echo $MAIN_API_URL
echo $API_KEY
```

### Need Help?

See full guide: `MCP_APP_GUIDE.md`

---

## What You Built

✅ **MCP Server** - Native protocol for ChatGPT integration
✅ **6 Core Tools** - Wardrobe management functions
✅ **Beautiful UI** - Cards, carousels following Apps SDK guidelines
✅ **Conversational** - Natural chat-based interactions

**Total Time:** ~30 minutes
**Result:** Native ChatGPT app! 🚀

