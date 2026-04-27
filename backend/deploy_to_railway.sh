#!/bin/bash

# Deploy Easy Outfit Backend to Railway
# This script helps deploy the backend to Railway with proper setup

set -e  # Exit on any error

RAILWAY_PROJECT_ID="97ed14e7-f7a6-4f86-b919-94f133ed478e"
RAILWAY_ENVIRONMENT="production"
RAILWAY_SERVICE="closetgptrenew"

echo "🚀 Deploying Easy Outfit Backend to Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed. Please install it first:"
    echo "   npm install -g @railway/cli"
    echo "   or"
    echo "   curl -fsSL https://railway.app/install.sh | sh"
    exit 1
fi

# Check if we're in the backend directory
if [ ! -f "railway.toml" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

# Check if service account key exists
if [ ! -f "serviceAccountKey.json" ]; then
    echo "❌ serviceAccountKey.json not found. Please ensure you have the new Firebase service account key."
    exit 1
fi

echo "📋 Current setup:"
echo "   - Railway config: ✅"
echo "   - Dockerfile: ✅"
echo "   - Requirements: ✅"
echo "   - Service account key: ✅"
echo ""

# Extract Firebase environment variables
echo "🔧 Extracting Firebase environment variables..."
python3 extract_firebase_env.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to extract Firebase environment variables"
    exit 1
fi

echo ""
echo "📝 Next steps:"
echo "1. Copy the Firebase environment variables above to your Railway project"
echo "2. Run: railway login (if not already logged in)"
echo "3. Run: railway up --project $RAILWAY_PROJECT_ID --environment $RAILWAY_ENVIRONMENT --service $RAILWAY_SERVICE"
echo ""

# Check if user wants to proceed with deployment
read -p "Do you want to proceed with Railway deployment? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting Railway deployment..."
    
    # Check if logged in to Railway
    if ! railway whoami &> /dev/null; then
        echo "🔐 Please log in to Railway first:"
        railway login
    fi
    
    # Deploy to Railway
    echo "📤 Deploying to Railway..."
    railway up \
      --project "$RAILWAY_PROJECT_ID" \
      --environment "$RAILWAY_ENVIRONMENT" \
      --service "$RAILWAY_SERVICE"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Deployment successful!"
        echo ""
        echo "🔗 Your Railway deployment URL will be shown above"
        echo "📊 You can monitor the deployment at: https://railway.app/dashboard"
        echo ""
        echo "🧪 Test your deployment:"
        echo "   curl https://your-railway-url.railway.app/health"
    else
        echo "❌ Deployment failed. Check the logs above for errors."
        exit 1
    fi
else
    echo "⏸️  Deployment cancelled. You can run 'railway up --project $RAILWAY_PROJECT_ID --environment $RAILWAY_ENVIRONMENT --service $RAILWAY_SERVICE' manually when ready."
fi
