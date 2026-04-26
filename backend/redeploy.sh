#!/bin/bash

RAILWAY_PROJECT_ID="97ed14e7-f7a6-4f86-b919-94f133ed478e"
RAILWAY_ENVIRONMENT="production"
RAILWAY_SERVICE="closetgptrenew-backend"

echo "🚀 Redeploying Easy Outfit Backend with correct app..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Check if we're in the backend directory
if [ ! -f "Dockerfile" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

echo "🔧 Redeploying to Railway..."
railway up \
  --project "$RAILWAY_PROJECT_ID" \
  --environment "$RAILWAY_ENVIRONMENT" \
  --service "$RAILWAY_SERVICE"

echo "✅ Backend redeployment initiated!"
echo "📋 Check the Railway dashboard for deployment status"
echo "🔗 Once deployed, the image analysis endpoints should be available" 
