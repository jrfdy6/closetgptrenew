#!/bin/bash

# Live Route Testing Runner
# This script sets up the environment and runs the live route tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if file exists
file_exists() {
    [ -f "$1" ]
}

# Function to check if directory exists
dir_exists() {
    [ -d "$1" ]
}

# Print banner
echo "============================================================"
echo "  ClosetGPT Live Route Testing Suite"
echo "============================================================"
echo ""

# Check prerequisites
print_status "Checking prerequisites..."

# Check Node.js
if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js v16 or higher."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    print_error "Node.js version 16 or higher is required. Current version: $(node --version)"
    exit 1
fi

print_success "Node.js $(node --version) is installed"

# Check npm
if ! command_exists npm; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

print_success "npm $(npm --version) is installed"

# Check test image
if ! file_exists "frontend/test-images/test-shirt.jpg"; then
    print_error "Test image not found at frontend/test-images/test-shirt.jpg"
    exit 1
fi

print_success "Test image found"

# Check if package.json exists
if ! file_exists "package.json"; then
    print_warning "package.json not found, using test-package.json"
    if file_exists "test-package.json"; then
        cp test-package.json package.json
        print_success "Created package.json from test-package.json"
    else
        print_error "Neither package.json nor test-package.json found"
        exit 1
    fi
fi

# Install dependencies
print_status "Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Check environment variables
print_status "Checking environment configuration..."

# Set default values if not provided
if [ -z "$FRONTEND_URL" ]; then
    export FRONTEND_URL="http://localhost:3000"
    print_warning "FRONTEND_URL not set, using default: $FRONTEND_URL"
else
    print_success "FRONTEND_URL set to: $FRONTEND_URL"
fi

if [ -z "$NEXT_PUBLIC_BACKEND_URL" ]; then
    export NEXT_PUBLIC_BACKEND_URL="https://closetgptrenew-backend-production.up.railway.app"
    print_warning "NEXT_PUBLIC_BACKEND_URL not set, using default: $NEXT_PUBLIC_BACKEND_URL"
else
    print_success "NEXT_PUBLIC_BACKEND_URL set to: $NEXT_PUBLIC_BACKEND_URL"
fi

# Check Firebase credentials
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    print_warning "GOOGLE_APPLICATION_CREDENTIALS not set"
    print_warning "You may need to set up Firebase Admin credentials for authentication"
else
    if file_exists "$GOOGLE_APPLICATION_CREDENTIALS"; then
        print_success "Firebase credentials found at: $GOOGLE_APPLICATION_CREDENTIALS"
    else
        print_error "Firebase credentials file not found at: $GOOGLE_APPLICATION_CREDENTIALS"
    fi
fi

# Check if auth helper is available
if file_exists "auth_helper.js"; then
    print_success "Auth helper script found"
else
    print_warning "Auth helper script not found. You'll need to implement authentication manually."
fi

echo ""
print_status "Environment check completed"
echo ""

# Ask user if they want to proceed
read -p "Do you want to proceed with the tests? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Tests cancelled by user"
    exit 0
fi

echo ""

# Run the tests
print_status "Starting live route tests..."
echo ""

# Run the test script
node test_live_routes.js

# Capture the exit code
TEST_EXIT_CODE=$?

echo ""

# Report results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "All tests completed successfully!"
    echo ""
    echo "🎉 Your ClosetGPT deployment is working correctly!"
    echo ""
    echo "Next steps:"
    echo "  - Monitor your application logs for any issues"
    echo "  - Set up continuous testing in your CI/CD pipeline"
    echo "  - Consider adding performance monitoring"
else
    print_error "Some tests failed. Please check the output above for details."
    echo ""
    echo "Troubleshooting tips:"
    echo "  - Check your Firebase credentials and permissions"
    echo "  - Verify your API endpoints are accessible"
    echo "  - Ensure your test image exists"
    echo "  - Review the troubleshooting section in LIVE_TESTING_README.md"
fi

echo ""
echo "============================================================"
echo "  Testing completed"
echo "============================================================"

exit $TEST_EXIT_CODE 