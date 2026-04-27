#!/bin/bash

RAILWAY_PROJECT_ID="97ed14e7-f7a6-4f86-b919-94f133ed478e"
RAILWAY_ENVIRONMENT="production"
RAILWAY_SERVICE="closetgptrenew"

echo "🚀 Deploying Easy Outfit Backend to Railway..."

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

echo "🎯 Target project: $RAILWAY_PROJECT_ID"
echo "🎯 Target environment: $RAILWAY_ENVIRONMENT"
echo "🎯 Target service: $RAILWAY_SERVICE"
echo "ℹ️  This script assumes service variables are already configured in Railway."

# Deploy
echo "🚀 Deploying to Railway..."
railway up \
  --project "$RAILWAY_PROJECT_ID" \
  --environment "$RAILWAY_ENVIRONMENT" \
  --service "$RAILWAY_SERVICE"

echo "✅ Backend deployment initiated!"
echo "📋 Check the Railway dashboard for deployment status"
echo "🔗 Once deployed, update the frontend with the new backend URL" 
