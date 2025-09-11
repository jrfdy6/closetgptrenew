#!/bin/bash

# Outfit Editing Testing Setup Script
# Run with: bash scripts/setup-testing.sh

set -e

echo "🧪 Setting up Outfit Editing Testing Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "Please run this script from the frontend directory"
    exit 1
fi

# Install dependencies
print_status "Installing dependencies..."
npm install

# Check if backend is running
print_status "Checking backend connection..."
if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
    print_status "Backend is running on port 3001"
else
    print_warning "Backend not running on port 3001. Please start the backend server."
    echo "To start backend: cd ../backend && python app.py"
fi

# Check environment variables
print_status "Checking environment variables..."
if [ -f ".env.local" ]; then
    print_status "Environment file found"
else
    print_warning "No .env.local file found. Creating template..."
    cat > .env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_BACKEND_URL=http://localhost:3001

# Firebase Configuration (if using)
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abcdef
EOF
    print_warning "Please update .env.local with your actual configuration"
fi

# Run type checking
print_status "Running TypeScript type checking..."
if npm run type-check 2>/dev/null; then
    print_status "TypeScript compilation successful"
else
    print_warning "TypeScript compilation has issues. Please check and fix."
fi

# Run linting
print_status "Running ESLint..."
if npm run lint 2>/dev/null; then
    print_status "Linting passed"
else
    print_warning "Linting has issues. Please check and fix."
fi

# Create test data directory
print_status "Creating test data directory..."
mkdir -p test-data

# Create sample test data
cat > test-data/sample-outfit.json << EOF
{
  "id": "test-outfit-123",
  "name": "Test Outfit",
  "occasion": "casual",
  "style": "modern",
  "mood": "comfortable",
  "items": [
    {
      "id": "item-1",
      "name": "Blue T-Shirt",
      "category": "top",
      "style": "casual",
      "color": "blue",
      "imageUrl": "https://example.com/tshirt.jpg",
      "user_id": "test-user-1"
    }
  ],
  "user_id": "test-user-1",
  "isFavorite": false,
  "wearCount": 0,
  "createdAt": "2024-01-15T10:00:00Z",
  "updatedAt": "2024-01-15T10:00:00Z"
}
EOF

cat > test-data/sample-wardrobe.json << EOF
[
  {
    "id": "item-1",
    "name": "Blue T-Shirt",
    "type": "top",
    "color": "blue",
    "brand": "Nike",
    "imageUrl": "https://example.com/tshirt.jpg",
    "user_id": "test-user-1",
    "season": "summer",
    "isFavorite": false,
    "wearCount": 5,
    "lastWorn": "2024-01-15",
    "createdAt": "2024-01-01",
    "updatedAt": "2024-01-15",
    "size": "M",
    "material": "cotton",
    "condition": "good",
    "price": 25,
    "purchaseDate": "2024-01-01",
    "tags": ["casual"],
    "notes": "Comfortable everyday shirt"
  },
  {
    "id": "item-2",
    "name": "Black Jeans",
    "type": "bottom",
    "color": "black",
    "brand": "Levi's",
    "imageUrl": "https://example.com/jeans.jpg",
    "user_id": "test-user-1",
    "season": "all",
    "isFavorite": true,
    "wearCount": 10,
    "lastWorn": "2024-01-20",
    "createdAt": "2024-01-01",
    "updatedAt": "2024-01-20",
    "size": "32",
    "material": "denim",
    "condition": "good",
    "price": 80,
    "purchaseDate": "2024-01-01",
    "tags": ["casual", "work"],
    "notes": "Perfect fit"
  }
]
EOF

print_status "Sample test data created in test-data/ directory"

# Make test script executable
chmod +x src/scripts/test-outfit-editing.js

print_status "Test script made executable"

# Start development server
print_status "Starting development server..."
echo ""
echo "🚀 Development server will start on http://localhost:3000"
echo ""
echo "📋 Testing Checklist:"
echo "1. Open http://localhost:3000/outfits"
echo "2. Click edit button on any outfit"
echo "3. Test the modal functionality"
echo "4. Run: node src/scripts/test-outfit-editing.js --checklist"
echo ""
echo "Press Ctrl+C to stop the server when done testing"
echo ""

# Start the development server
npm run dev
