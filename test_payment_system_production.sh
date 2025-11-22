#!/bin/bash
# Production Payment System Test Script
# Tests payment and subscription endpoints in production

PROD_URL="https://closetgptrenew-production.up.railway.app"
API_URL="${PROD_URL}/api"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Testing Payment System in Production"
echo "========================================"
echo "Production URL: ${PROD_URL}"
echo ""

# You'll need to set this to a valid Firebase auth token
# Get it from browser console: firebase.auth().currentUser.getIdToken()
TOKEN="${1:-test}"

if [ "$TOKEN" == "test" ]; then
    echo -e "${YELLOW}⚠️  Using test token. For real tests, pass your Firebase token as first argument${NC}"
    echo "   Usage: ./test_payment_system_production.sh YOUR_FIREBASE_TOKEN"
    echo ""
fi

echo "1️⃣  Testing Health Check..."
echo "------------------------"
curl -s "${PROD_URL}/health" | jq '.' || echo "Health check failed"
echo ""
echo ""

echo "2️⃣  Testing Current Subscription Endpoint..."
echo "--------------------------------------------"
response=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    "${API_URL}/payments/subscription/current")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: ${http_code}"
echo "Response:"
echo "$body" | jq '.' || echo "$body"
echo ""

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✅ Subscription endpoint working!${NC}"
    role=$(echo "$body" | jq -r '.role // empty')
    if [ ! -z "$role" ]; then
        echo "   Current role: ${role}"
    fi
else
    echo -e "${RED}❌ Subscription endpoint failed${NC}"
fi
echo ""

echo "3️⃣  Testing Style Persona Analysis (Should Require Pro/Premium)..."
echo "-------------------------------------------------------------------"
# Create a test image file (1x1 pixel PNG)
echo "Creating test image..."
echo -e "\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde" > /tmp/test_image.png

response=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -F "file=@/tmp/test_image.png" \
    "${API_URL}/style-analysis/analyze")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: ${http_code}"
echo "Response:"
echo "$body" | jq '.' || echo "$body"
echo ""

if [ "$http_code" == "403" ]; then
    echo -e "${GREEN}✅ Paywall working! Style analysis correctly requires Pro/Premium${NC}"
elif [ "$http_code" == "200" ]; then
    echo -e "${YELLOW}⚠️  Style analysis accessible - user might already have Pro/Premium${NC}"
else
    echo -e "${RED}❌ Unexpected response${NC}"
fi
echo ""

echo "4️⃣  Testing Feature Access Service (Backend Check)..."
echo "-----------------------------------------------------"
# This tests if the subscription feature access service is working
response=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    "${API_URL}/payments/subscription/current")

http_code=$(echo "$response" | tail -n1)
if [ "$http_code" == "200" ]; then
    role=$(echo "$response" | sed '$d' | jq -r '.role // "tier1"')
    echo "   User role: ${role}"
    
    if [ "$role" == "tier2" ] || [ "$role" == "tier3" ]; then
        echo -e "${GREEN}✅ User has Pro/Premium - should have access to premium features${NC}"
    else
        echo -e "${YELLOW}⚠️  User has Free tier - premium features should be blocked${NC}"
    fi
fi
echo ""

echo "5️⃣  Testing Payment Routes Registration..."
echo "------------------------------------------"
response=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    "${API_URL}/payments/subscription/current")

http_code=$(echo "$response" | tail -n1)
if [ "$http_code" != "404" ]; then
    echo -e "${GREEN}✅ Payment routes are registered and accessible${NC}"
else
    echo -e "${RED}❌ Payment routes not found - check if deployed${NC}"
fi
echo ""

echo "6️⃣  Testing Stripe Configuration..."
echo "-----------------------------------"
# Test if Stripe checkout session creation works (will fail if not configured, but should give proper error)
response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"role": "tier2"}' \
    "${API_URL}/payments/checkout/create-session")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: ${http_code}"
echo "Response:"
echo "$body" | jq '.' || echo "$body"
echo ""

if [ "$http_code" == "503" ]; then
    echo -e "${YELLOW}⚠️  Stripe not configured yet - this is expected${NC}"
    echo "   Need to set STRIPE_SECRET_KEY environment variable"
elif [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✅ Stripe is configured and working!${NC}"
else
    echo -e "${YELLOW}⚠️  Unexpected response - check configuration${NC}"
fi
echo ""

echo "========================================"
echo "✅ Test Summary Complete"
echo ""
echo "Next Steps:"
echo "1. Set up Stripe (see STRIPE_SETUP.md)"
echo "2. Configure environment variables in Railway"
echo "3. Test with real Stripe checkout"
echo ""

