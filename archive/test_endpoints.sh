#!/bin/bash

# Test script for prospecting endpoints
# This verifies the endpoints are properly defined and accessible

BASE_URL="http://localhost:3001"
USER_ID="test-user-123"

echo "🧪 Testing Prospecting Workflow Endpoints"
echo "=========================================="
echo ""

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
HEALTH=$(curl -s "$BASE_URL/health" 2>&1)
if [ $? -eq 0 ]; then
    echo "   ✅ Backend is running"
    echo "   Response: $HEALTH"
else
    echo "   ❌ Backend is not running"
    echo "   Start backend with: cd backend && python3 -m uvicorn app:app --reload --port 3001"
    exit 1
fi
echo ""

# Test 2: Upload prospects
echo "2️⃣ Testing prospect upload..."
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/prospects/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "prospects": [
      {
        "name": "Test Prospect",
        "job_title": "VP of Sales",
        "company": "TestCorp Inc",
        "email": "test@testcorp.com",
        "notes": "Test prospect for validation"
      }
    ],
    "user_id": "'$USER_ID'",
    "batch_name": "Test Batch 1"
  }' 2>&1)

if echo "$UPLOAD_RESPONSE" | grep -q "success"; then
    echo "   ✅ Upload endpoint works"
    echo "   Response: $UPLOAD_RESPONSE"
    
    # Extract prospect ID (basic extraction)
    PROSPECT_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"prospect_ids":\["[^"]*' | cut -d'"' -f4 | head -1)
    if [ -n "$PROSPECT_ID" ]; then
        echo "   📝 Extracted Prospect ID: $PROSPECT_ID"
        export PROSPECT_ID
    fi
else
    echo "   ❌ Upload failed"
    echo "   Response: $UPLOAD_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Generate analysis prompt (manual mode)
echo "3️⃣ Testing manual analysis prompt generation..."
if [ -z "$PROSPECT_ID" ]; then
    PROSPECT_ID="test-prospect-id"
    echo "   ⚠️  Using placeholder prospect ID (upload may have failed)"
fi

PROMPT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/prospects/manual/prompts/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_ids": ["'$PROSPECT_ID'"],
    "user_id": "'$USER_ID'",
    "audience_profile": {
      "brand_name": "Test Company",
      "brand_voice": "Professional and friendly",
      "target_pain_points": ["Manual processes"],
      "value_propositions": ["Saves time"],
      "industry_focus": "SaaS"
    }
  }' 2>&1)

if echo "$PROMPT_RESPONSE" | grep -q "full_prompt"; then
    echo "   ✅ Prompt generation works"
    echo "   📝 Prompt available in response"
    
    # Extract full_prompt for display
    FULL_PROMPT=$(echo "$PROMPT_RESPONSE" | grep -o '"full_prompt":"[^"]*' | cut -d'"' -f4 | head -c 200)
    if [ -n "$FULL_PROMPT" ]; then
        echo "   Preview: ${FULL_PROMPT}..."
    fi
else
    echo "   ❌ Prompt generation failed"
    echo "   Response: $PROMPT_RESPONSE"
fi
echo ""

# Test 4: Phase status
echo "4️⃣ Testing phase status..."
PHASE_STATUS=$(curl -s "$BASE_URL/api/phases/phase-status/$USER_ID" 2>&1)
if echo "$PHASE_STATUS" | grep -q "success\|current_phase"; then
    echo "   ✅ Phase status endpoint works"
    echo "   Response: $PHASE_STATUS"
else
    echo "   ⚠️  Phase status endpoint may need data"
    echo "   Response: $PHASE_STATUS"
fi
echo ""

# Test 5: List prospects
echo "5️⃣ Testing prospect list..."
LIST_RESPONSE=$(curl -s "$BASE_URL/api/prospects/list?user_id=$USER_ID" 2>&1)
if echo "$LIST_RESPONSE" | grep -q "success\|prospects"; then
    echo "   ✅ List endpoint works"
    COUNT=$(echo "$LIST_RESPONSE" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    echo "   📊 Found $COUNT prospects"
else
    echo "   ⚠️  List endpoint may be empty"
    echo "   Response: $LIST_RESPONSE"
fi
echo ""

echo "=========================================="
echo "✅ Basic endpoint tests complete!"
echo ""
echo "📝 Next Steps:"
echo "   1. Copy the full_prompt from step 3"
echo "   2. Paste into ChatGPT"
echo "   3. Get JSON response"
echo "   4. Upload via: POST /api/prospects/manual/upload-analysis"
echo ""



