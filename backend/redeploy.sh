#!/bin/bash

echo "🚀 Redeploying ClosetGPT Backend with correct app..."

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
railway up

echo "✅ Backend redeployment initiated!"
echo "📋 Check the Railway dashboard for deployment status"
echo "🔗 Once deployed, the image analysis endpoints should be available" 