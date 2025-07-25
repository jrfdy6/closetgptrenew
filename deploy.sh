#!/bin/bash

echo "🚀 Starting ClosetGPT Deployment..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
    
    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI not found. Installing..."
        npm install -g vercel
    fi
    
    print_status "Dependencies check complete!"
}

# Deploy backend to Railway
deploy_backend() {
    print_status "Deploying backend to Railway..."
    
    cd backend
    
    # Check if Railway project is initialized
    if [ ! -f ".railway" ]; then
        print_status "Initializing Railway project..."
        railway init
    fi
    
    # Deploy to Railway
    print_status "Deploying to Railway..."
    railway up
    
    # Get the deployment URL
    BACKEND_URL=$(railway status --json | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
    
    if [ -z "$BACKEND_URL" ]; then
        print_error "Failed to get Railway deployment URL"
        exit 1
    fi
    
    print_status "Backend deployed to: $BACKEND_URL"
    cd ..
    
    # Export the backend URL for frontend deployment
    export BACKEND_URL
}

# Deploy frontend to Vercel
deploy_frontend() {
    print_status "Deploying frontend to Vercel..."
    
    cd frontend
    
    # Create .env.local with backend URL
    if [ ! -z "$BACKEND_URL" ]; then
        print_status "Creating .env.local with backend URL..."
        cat > .env.local << EOF
NEXT_PUBLIC_API_URL=$BACKEND_URL
NEXT_PUBLIC_BACKEND_URL=$BACKEND_URL
NODE_ENV=production
EOF
    fi
    
    # Deploy to Vercel
    print_status "Deploying to Vercel..."
    vercel --prod
    
    cd ..
}

# Main deployment process
main() {
    print_status "Starting deployment process..."
    
    # Check dependencies
    check_dependencies
    
    # Deploy backend first
    deploy_backend
    
    # Deploy frontend
    deploy_frontend
    
    print_status "Deployment complete! 🎉"
    print_status "Backend URL: $BACKEND_URL"
    print_warning "Don't forget to set up your environment variables in Railway and Vercel dashboards!"
}

# Run main function
main "$@" 