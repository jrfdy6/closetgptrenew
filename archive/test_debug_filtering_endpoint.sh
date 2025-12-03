#!/bin/bash

echo "================================================================================"
echo "🧪 TESTING DEBUG FILTERING ENDPOINT"
echo "================================================================================"
echo ""

# Test configuration
BACKEND_URL="https://closetgptrenew-backend-production.up.railway.app"
USER_ID="dANqjiI0CKgaitxzYtw1bhtvQrG3"

# You'll need to get a real Firebase token - for now using a placeholder
# Run this command in your browser console while logged in:
# firebase.auth().currentUser.getIdToken().then(token => console.log(token))

echo "📋 Test Case: Casual/Classic/Comfortable combination"
echo ""

# Create test payload
TEST_PAYLOAD='{
  "occasion": "Casual",
  "style": "Classic",
  "mood": "Comfortable",
  "weather": {
    "temperature": 72,
    "condition": "Clear",
    "humidity": 50
  }
}'

echo "🔍 Calling debug endpoint..."
echo "URL: ${BACKEND_URL}/api/outfits/debug-filter"
echo ""

# Call endpoint (will fail without auth token, but shows structure)
curl -X POST "${BACKEND_URL}/api/outfits/debug-filter?semantic=false" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d "${TEST_PAYLOAD}" \
  --verbose

echo ""
echo "================================================================================"
echo "📋 To get a real auth token:"
echo "   1. Open https://closetgpt-frontend.vercel.app in browser"
echo "   2. Open DevTools Console"
echo "   3. Run: firebase.auth().currentUser.getIdToken().then(token => console.log(token))"
echo "   4. Copy the token"
echo "   5. Replace YOUR_TOKEN_HERE with the actual token"
echo "================================================================================"

