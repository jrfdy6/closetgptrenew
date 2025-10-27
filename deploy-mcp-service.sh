#!/bin/bash

echo "🚀 Deploying ClosetGPT MCP Server as SEPARATE Railway Service"
echo "=============================================================="
echo ""
echo "⚠️  This creates a NEW Railway project, separate from your main app"
echo ""

# Navigate to backend directory
cd backend || exit 1

echo "📁 Current directory: $(pwd)"
echo ""

# Check if Railway CLI is logged in
echo "🔐 Checking Railway CLI authentication..."
if ! railway whoami &>/dev/null; then
    echo "❌ Not logged into Railway CLI"
    echo ""
    echo "Please run: railway login"
    echo "Then run this script again."
    exit 1
fi

echo "✅ Authenticated as: $(railway whoami)"
echo ""

# Create new project
echo "🆕 Creating NEW Railway project: closetgpt-mcp-server"
echo ""
echo "⚠️  Railway will ask you to:"
echo "   1. Choose 'Create new project'"
echo "   2. Name it: closetgpt-mcp-server"
echo ""
read -p "Press Enter to continue..."

railway init

echo ""
echo "✅ Project created!"
echo ""

# Set environment variables
echo "⚙️  Setting environment variables..."
railway variables set MAIN_API_URL="https://closetgptrenew-production.railway.app"
railway variables set API_KEY="dqvNQIiCRXmUSsEHFpVvWhotNkwAspNGS4nH3u2r844"
railway variables set PORT="3002"

echo "✅ Variables set!"
echo ""

# Deploy
echo "🚀 Deploying MCP server..."
railway up --detach

echo ""
echo "✅ Deployment started!"
echo ""
echo "📊 Check status: railway status"
echo "📜 View logs: railway logs"
echo "🌐 Get URL: railway domain"
echo ""
echo "=============================================================="
echo "🎉 MCP Service Deployment Complete!"
echo ""
echo "Your services:"
echo "  • Main App: https://closetgptrenew-production.railway.app"
echo "  • MCP Server: (run 'railway domain' to get URL)"
echo ""
echo "Next steps:"
echo "  1. Run: railway domain (to get your MCP server URL)"
echo "  2. Register that URL in OpenAI Apps SDK"
echo "  3. Connect to ChatGPT"
echo ""

