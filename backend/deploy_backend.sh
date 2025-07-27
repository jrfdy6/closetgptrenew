#!/bin/bash

echo "🚀 Deploying ClosetGPT Backend to Railway..."

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

# Login to Railway (if not already logged in)
echo "🔐 Logging into Railway..."
railway login

# Create new project or link to existing
echo "📦 Creating/linking Railway project..."
railway init

# Set environment variables
echo "🔧 Setting environment variables..."
railway variables set ENVIRONMENT=production
railway variables set PORT=8080

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Backend deployment initiated!"
echo "📋 Check the Railway dashboard for deployment status"
echo "🔗 Once deployed, update the frontend with the new backend URL" 