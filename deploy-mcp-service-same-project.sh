#!/bin/bash

echo "🚀 Adding MCP Server as NEW SERVICE to existing Railway project"
echo "================================================================"
echo ""
echo "This will:"
echo "  • Add a new service to your closetgptrenew project"
echo "  • Call it: closetgptrenewopenaisdk"
echo "  • Keep your main app service unchanged"
echo ""

cd backend || exit 1

echo "📁 Current directory: $(pwd)"
echo ""

# Check Railway CLI authentication
echo "🔐 Checking Railway authentication..."
if ! railway whoami &>/dev/null; then
    echo "❌ Not logged into Railway"
    echo "Please run: railway login"
    exit 1
fi

echo "✅ Authenticated as: $(railway whoami)"
echo ""

# Link to existing project
echo "🔗 Linking to your existing Railway project..."
echo ""
echo "When prompted, select your existing 'closetgptrenew' project"
echo ""
read -p "Press Enter to continue..."

railway link

echo ""
echo "✅ Linked to project!"
echo ""

# Create new service in the same project
echo "🆕 Creating new service: closetgptrenewopenaisdk"
echo ""
echo "This adds a NEW service alongside your main app"
echo ""

# Set service name
export RAILWAY_SERVICE=closetgptrenewopenaisdk

# Set environment variables for this service
echo "⚙️  Setting environment variables for MCP service..."
railway variables set MAIN_API_URL="https://closetgptrenew-production.up.railway.app" --service closetgptrenewopenaisdk
railway variables set API_KEY="dqvNQIiCRXmUSsEHFpVvWhotNkwAspNGS4nH3u2r844" --service closetgptrenewopenaisdk
railway variables set PORT="3002" --service closetgptrenewopenaisdk

echo "✅ Variables set!"
echo ""

# Deploy to the new service
echo "🚀 Deploying MCP server to new service..."
railway up --service closetgptrenewopenaisdk

echo ""
echo "✅ Deployment complete!"
echo ""
echo "================================================================"
echo "🎉 Success! Your Railway project now has TWO services:"
echo ""
echo "  1. Main App (unchanged)"
echo "     URL: https://closetgptrenew-production.up.railway.app"
echo ""
echo "  2. MCP Server (new)"
echo "     Service name: closetgptrenewopenaisdk"
echo "     URL: (Railway will assign)"
echo ""
echo "To get the MCP service URL:"
echo "  railway domain --service closetgptrenewopenaisdk"
echo ""
echo "To view logs:"
echo "  railway logs --service closetgptrenewopenaisdk"
echo ""

