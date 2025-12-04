#!/bin/bash

# Production Gamification Testing Script
# This script tests all gamification endpoints with your authentication token

# USAGE:
# 1. Get a fresh Firebase token from the browser (token expires after 1 hour)
# 2. Replace YOUR_TOKEN_HERE below with your actual token
# 3. Run: chmod +x test_gamification_production.sh
# 4. Run: ./test_gamification_production.sh

# Configuration
BASE_URL="https://closetgptrenew-production.up.railway.app/api"
TOKEN="YOUR_TOKEN_HERE"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo " Gamification System Production Tests"
echo "=========================================="
echo ""

# Test 1: Initialize/Get Profile
echo -e "${BLUE}Test 1: Get Gamification Profile${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "success"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 2: Get Stats
echo -e "${BLUE}Test 2: Get Gamification Stats${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/stats" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "xp\|level"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 3: Get Badges
echo -e "${BLUE}Test 3: Get User Badges${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/badges" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "success\|badges"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 4: Award XP
echo -e "${BLUE}Test 4: Award XP (Manual Test)${NC}"
response=$(curl -s -X POST "$BASE_URL/gamification/award-xp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 10, "reason": "test", "metadata": {}}')
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "success\|xp"; then
    echo -e "${GREEN}✅ PASS - You earned 10 XP!${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 5: Get AI Fit Score
echo -e "${BLUE}Test 5: Get AI Fit Score${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/ai-fit-score" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "score\|ai_fit_score"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 6: Get CPW Summary
echo -e "${BLUE}Test 6: Get CPW Summary${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/cpw-summary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "cpw\|average"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 7: Get Available Challenges
echo -e "${BLUE}Test 7: Get Available Challenges${NC}"
response=$(curl -s -X GET "$BASE_URL/challenges/available" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "success\|challenges"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 8: Get Active Challenges
echo -e "${BLUE}Test 8: Get Active Challenges${NC}"
response=$(curl -s -X GET "$BASE_URL/challenges/active" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "success\|challenges"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 9: Get Challenge Catalog
echo -e "${BLUE}Test 9: Get Challenge Catalog${NC}"
response=$(curl -s -X GET "$BASE_URL/challenges/catalog" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "success\|challenges"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 10: Try Shuffle
echo -e "${BLUE}Test 10: Generate Shuffle Outfit${NC}"
response=$(curl -s -X POST "$BASE_URL/shuffle/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}')
# Just check for non-error response (outfit generation requires wardrobe items)
if echo "$response" | grep -q "success\|outfit\|Not authenticated"; then
    echo -e "${GREEN}✅ Endpoint responding${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 11: Get GWS (Global Wardrobe Score)
echo -e "${BLUE}Test 11: Get Global Wardrobe Score${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/gws" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "gws\|score"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

# Test 12: Get Utilization
echo -e "${BLUE}Test 12: Get Wardrobe Utilization${NC}"
response=$(curl -s -X GET "$BASE_URL/gamification/utilization" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
echo "$response" | python3 -m json.tool
if echo "$response" | grep -q "utilization\|percentage"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi
echo ""

echo "=========================================="
echo " Tests Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "- If all tests show ✅, gamification is fully working"
echo "- If some show ❌, check Railway logs for errors"
echo "- Check your profile again to see if XP was added"
echo ""

