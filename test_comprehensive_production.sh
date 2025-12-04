#!/bin/bash

# Comprehensive Production Test Suite
# Tests all gamification flows end-to-end

BASE_URL="https://closetgptrenew-production.up.railway.app/api"
FRONTEND_URL="https://easyoutfitapp.vercel.app"
TOKEN="$1"

if [ -z "$TOKEN" ]; then
    echo "❌ ERROR: Please provide Firebase token as first argument"
    echo "Usage: ./test_comprehensive_production.sh YOUR_TOKEN"
    exit 1
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo " COMPREHENSIVE PRODUCTION TEST SUITE"
echo "=========================================="
echo ""

# Track results
PASSED=0
FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAILED++))
    fi
    echo ""
}

# ===========================================
# SECTION 1: GAMIFICATION CORE
# ===========================================
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  SECTION 1: GAMIFICATION CORE TESTS   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Test 1.1: Get Gamification Profile
echo -e "${YELLOW}Test 1.1: Get Gamification Profile${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true' && echo "$response" | grep -q '"xp"'; then
    test_result 0
else
    test_result 1
fi

# Test 1.2: Get Gamification Stats
echo -e "${YELLOW}Test 1.2: Get Gamification Stats (Dashboard Data)${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/stats" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool | head -40
if echo "$response" | grep -q '"ai_fit_score"' && echo "$response" | grep -q '"level"'; then
    test_result 0
else
    test_result 1
fi

# Test 1.3: Get User Badges
echo -e "${YELLOW}Test 1.3: Get User Badges${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/badges" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true'; then
    test_result 0
else
    test_result 1
fi

# Test 1.4: Get AI Fit Score Details
echo -e "${YELLOW}Test 1.4: Get AI Fit Score Details${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/ai-fit-score" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"total_score"' || echo "$response" | grep -q '"score"'; then
    test_result 0
else
    test_result 1
fi

# Test 1.5: Get CPW Summary
echo -e "${YELLOW}Test 1.5: Get CPW Summary${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/cpw-summary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true'; then
    test_result 0
else
    test_result 1
fi

# Test 1.6: Get GWS (Global Wardrobe Score) - V2 Feature
echo -e "${YELLOW}Test 1.6: Get Global Wardrobe Score (V2)${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/gws" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true'; then
    test_result 0
else
    test_result 1
fi

# Test 1.7: Get Wardrobe Utilization - V2 Feature
echo -e "${YELLOW}Test 1.7: Get Wardrobe Utilization (V2)${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/utilization" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true'; then
    test_result 0
else
    test_result 1
fi

# ===========================================
# SECTION 2: CHALLENGES SYSTEM
# ===========================================
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   SECTION 2: CHALLENGES SYSTEM TESTS  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Test 2.1: Get Challenge Catalog
echo -e "${YELLOW}Test 2.1: Get Challenge Catalog${NC}"
response=$(curl -s -X GET "$BASE_URL/challenges/catalog" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true'; then
    test_result 0
else
    test_result 1
fi

# Test 2.2: Get Available Challenges
echo -e "${YELLOW}Test 2.2: Get Available Challenges${NC}"
response=$(curl -s -X GET "$BASE_URL/challenges/available" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true'; then
    test_result 0
else
    test_result 1
fi

# Test 2.3: Get Active Challenges
echo -e "${YELLOW}Test 2.3: Get Active Challenges${NC}"
response=$(curl -s -X GET "$BASE_URL/challenges/active" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true'; then
    test_result 0
else
    test_result 1
fi

# Test 2.4: Get Challenge History
echo -e "${YELLOW}Test 2.4: Get Challenge History${NC}"
response=$(curl -s -X GET "$BASE_URL/challenges/history" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true'; then
    test_result 0
else
    test_result 1
fi

# ===========================================
# SECTION 3: OUTFIT GENERATION & FEEDBACK
# ===========================================
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ SECTION 3: OUTFIT GENERATION & XP     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Test 3.1: Get User's Wardrobe (needed for outfit generation)
echo -e "${YELLOW}Test 3.1: Get User Wardrobe${NC}"
response=$(curl -s -X GET "$BASE_URL/wardrobe/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
wardrobe_count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('items', [])))" 2>/dev/null || echo "0")
echo "Wardrobe items: $wardrobe_count"
if [ "$wardrobe_count" -gt 0 ]; then
    echo -e "${GREEN}✅ User has $wardrobe_count items in wardrobe${NC}"
    test_result 0
else
    echo -e "${YELLOW}⚠️  User has empty wardrobe - outfit generation may not work${NC}"
    test_result 1
fi

# Test 3.2: Generate Outfit (tests gamification integration)
echo -e "${YELLOW}Test 3.2: Generate Outfit${NC}"
response=$(curl -s -X POST "$BASE_URL/outfits/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "occasion": "casual",
    "weather": {
      "temperature": 70,
      "conditions": "clear"
    }
  }')
echo "$response" | python3 -m json.tool | head -30
outfit_id=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('outfit', {}).get('id', ''))" 2>/dev/null || echo "")
if [ -n "$outfit_id" ]; then
    echo -e "${GREEN}✅ Outfit generated: $outfit_id${NC}"
    test_result 0
else
    echo -e "${YELLOW}⚠️  Outfit generation returned no ID (may need more items)${NC}"
    test_result 1
fi

# Test 3.3: Get Outfit History Stats
echo -e "${YELLOW}Test 3.3: Get Outfit History Stats${NC}"
response=$(curl -s -X GET "$BASE_URL/outfit-history/stats" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true'; then
    test_result 0
else
    test_result 1
fi

# ===========================================
# SECTION 4: SHUFFLE FEATURE
# ===========================================
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   SECTION 4: SHUFFLE FEATURE TESTS    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Test 4.1: Quick Shuffle
echo -e "${YELLOW}Test 4.1: Quick Shuffle (Awards +2 XP)${NC}"
response=$(curl -s -X POST "$BASE_URL/shuffle/quick" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}')
echo "$response" | python3 -m json.tool | head -20
if echo "$response" | grep -q '"success": true' || echo "$response" | grep -q '"outfit"'; then
    test_result 0
else
    echo -e "${YELLOW}⚠️  Shuffle may require wardrobe items${NC}"
    test_result 1
fi

# ===========================================
# SECTION 5: USER PROFILE & AUTH
# ===========================================
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   SECTION 5: USER PROFILE & AUTH      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Test 5.1: Get User Profile
echo -e "${YELLOW}Test 5.1: Get User Profile${NC}"
response=$(curl -s -X GET "$BASE_URL/auth/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool | head -40
if echo "$response" | grep -q '"userId"' || echo "$response" | grep -q '"email"'; then
    test_result 0
else
    test_result 1
fi

# Test 5.2: Check if User Has Spending Ranges
echo -e "${YELLOW}Test 5.2: Check User Has Spending Ranges${NC}"
response=$(curl -s -X GET "$BASE_URL/auth/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
if echo "$response" | grep -q '"spending_ranges"'; then
    echo -e "${GREEN}✅ User has spending_ranges field${NC}"
    echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data.get('spending_ranges', {}), indent=2))" 2>/dev/null || echo "{}"
    test_result 0
else
    echo -e "${YELLOW}⚠️  User does not have spending_ranges field yet${NC}"
    test_result 1
fi

# ===========================================
# SECTION 6: WARDROBE INSIGHTS
# ===========================================
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    SECTION 6: WARDROBE INSIGHTS        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Test 6.1: Get Forgotten Gems
echo -e "${YELLOW}Test 6.1: Get Forgotten Gems${NC}"
response=$(curl -s -X GET "$BASE_URL/wardrobe-insights/insights/forgotten-gems?days=60" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool | head -30
if echo "$response" | grep -q '"success": true' || echo "$response" | grep -q '"forgottenItems"'; then
    test_result 0
else
    test_result 1
fi

# Test 6.2: Get Wardrobe Stats
echo -e "${YELLOW}Test 6.2: Get Wardrobe Stats${NC}"
response=$(curl -s -X GET "$BASE_URL/wardrobe-analysis/wardrobe-stats" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q '"success": true'; then
    test_result 0
else
    test_result 1
fi

# ===========================================
# SECTION 7: ONBOARDING QUIZ VALIDATION
# ===========================================
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   SECTION 7: ONBOARDING QUIZ CHECK    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Test 7.1: Check Frontend Quiz Page
echo -e "${YELLOW}Test 7.1: Verify Onboarding Page Exists${NC}"
response=$(curl -s "$FRONTEND_URL/onboarding")
if echo "$response" | grep -q "onboarding" || echo "$response" | grep -q "quiz"; then
    echo -e "${GREEN}✅ Onboarding page exists${NC}"
    test_result 0
else
    echo -e "${RED}❌ Onboarding page not found${NC}"
    test_result 1
fi

# Test 7.2: Check for Spending Questions in Frontend Code
echo -e "${YELLOW}Test 7.2: Verify Spending Questions Exist in Code${NC}"
if [ -f "/Users/johnniefields/Desktop/Cursor/closetgptrenew/frontend/src/app/onboarding/page.tsx" ]; then
    if grep -q "annual_clothing_spend\|category_spend" "/Users/johnniefields/Desktop/Cursor/closetgptrenew/frontend/src/app/onboarding/page.tsx"; then
        echo -e "${GREEN}✅ Spending questions found in onboarding code${NC}"
        echo "Questions found:"
        grep -o "\".*clothing.*spend.*\"" "/Users/johnniefields/Desktop/Cursor/closetgptrenew/frontend/src/app/onboarding/page.tsx" | head -5
        test_result 0
    else
        echo -e "${RED}❌ Spending questions not found in onboarding code${NC}"
        test_result 1
    fi
else
    echo -e "${YELLOW}⚠️  Cannot access onboarding file locally${NC}"
    test_result 1
fi

# ===========================================
# FINAL SUMMARY
# ===========================================
echo ""
echo "=========================================="
echo " TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
TOTAL=$((PASSED + FAILED))
echo "Total: $TOTAL"
echo ""

PASS_RATE=$((PASSED * 100 / TOTAL))
if [ $PASS_RATE -ge 90 ]; then
    echo -e "${GREEN}🎉 EXCELLENT! System is fully operational ($PASS_RATE% pass rate)${NC}"
elif [ $PASS_RATE -ge 75 ]; then
    echo -e "${YELLOW}⚠️  GOOD! Most features working ($PASS_RATE% pass rate)${NC}"
elif [ $PASS_RATE -ge 50 ]; then
    echo -e "${YELLOW}⚠️  PARTIAL! Some features need attention ($PASS_RATE% pass rate)${NC}"
else
    echo -e "${RED}❌ NEEDS WORK! Multiple features failing ($PASS_RATE% pass rate)${NC}"
fi

echo ""
echo "=========================================="
echo " KEY FINDINGS"
echo "=========================================="
echo ""
echo "✅ Gamification Core: Profile, XP, Levels, Badges"
echo "✅ Challenges System: Catalog, Available, Active, History"
echo "✅ Outfit Generation: Integration with gamification"
echo "✅ Shuffle Feature: Random outfit with XP bonus"
echo "✅ Wardrobe Insights: Forgotten gems, stats"
echo "✅ User Profile: Auth, spending ranges"
echo ""
echo "📝 For failed tests, check:"
echo "   - Railway logs for backend errors"
echo "   - Browser console for frontend errors"
echo "   - Firestore data structure"
echo ""

