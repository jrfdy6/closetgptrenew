#!/bin/bash

# Quick test script for GPT Store standalone service

echo "🧪 Testing GPT Store Standalone Service Locally"
echo "==============================================="
echo ""

# Check if running
echo "Starting service in background..."
cd backend

export GPT_OAUTH_CLIENT_ID=closetgpt-custom-gpt
export GPT_OAUTH_CLIENT_SECRET=test-secret-for-local-testing
export JWT_SECRET=test-jwt-secret-for-local
export API_BASE_URL=http://localhost:3002
export MAIN_API_URL=https://closetgptrenew-production.railway.app

# Start service in background
python gpt_store_app.py &
PID=$!

echo "Service started (PID: $PID)"
echo "Waiting for startup..."
sleep 3

echo ""
echo "Running tests..."
echo ""

# Test 1: Root endpoint
echo "1️⃣ Testing root endpoint..."
curl -s http://localhost:3002/ | python3 -m json.tool

echo ""
echo "2️⃣ Testing OAuth metadata..."
curl -s http://localhost:3002/oauth/.well-known/oauth-authorization-server | python3 -m json.tool

echo ""
echo "3️⃣ Testing privacy policy (should return HTML)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3002/privacy)
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Privacy Policy: PASSED"
else
    echo "   ❌ Privacy Policy: FAILED ($HTTP_CODE)"
fi

echo ""
echo "4️⃣ Testing terms (should return HTML)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3002/terms)
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Terms: PASSED"
else
    echo "   ❌ Terms: FAILED ($HTTP_CODE)"
fi

echo ""
echo "==============================================="
echo "✨ Tests complete!"
echo ""
echo "To view in browser: http://localhost:3002"
echo "To stop service: kill $PID"
echo ""
echo "Press Enter to stop service and exit..."
read

# Cleanup
kill $PID 2>/dev/null
echo "Service stopped"

