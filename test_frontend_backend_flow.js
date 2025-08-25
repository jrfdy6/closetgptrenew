#!/usr/bin/env node

/**
 * Simple test script to verify frontend → backend flow
 * Run with: node test_frontend_backend_flow.js
 */

const https = require('https');

// Configuration
const BACKEND_URL = 'https://closetgptrenew-backend-production.up.railway.app';
const FRONTEND_URL = 'http://localhost:3000';

// Test data
const testOutfitRequest = {
  style: "casual",
  mood: "relaxed", 
  occasion: "weekend"
};

// Helper function to make HTTP requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({ status: res.statusCode, data: jsonData });
        } catch (e) {
          resolve({ status: res.statusCode, data: data });
        }
      });
    });
    
    req.on('error', reject);
    if (options.body) req.write(options.body);
    req.end();
  });
}

// Test 1: Direct Backend GET /api/outfits
async function testBackendGet() {
  console.log('🧪 Test 1: Direct Backend GET /api/outfits');
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/outfits`);
    console.log(`   Status: ${response.status}`);
    if (response.status === 200) {
      console.log('   ✅ SUCCESS: Backend GET working');
      console.log(`   Data: ${JSON.stringify(response.data).substring(0, 100)}...`);
    } else {
      console.log(`   ❌ FAILED: Status ${response.status}`);
      console.log(`   Response: ${JSON.stringify(response.data)}`);
    }
  } catch (error) {
    console.log(`   ❌ ERROR: ${error.message}`);
  }
  console.log('');
}

// Test 2: Direct Backend POST /api/outfits/generate
async function testBackendPost() {
  console.log('🧪 Test 2: Direct Backend POST /api/outfits/generate');
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testOutfitRequest)
    });
    console.log(`   Status: ${response.status}`);
    if (response.status === 200) {
      console.log('   ✅ SUCCESS: Backend POST working');
      console.log(`   Generated Outfit ID: ${response.data.id}`);
    } else {
      console.log(`   ❌ FAILED: Status ${response.status}`);
      console.log(`   Response: ${JSON.stringify(response.data)}`);
    }
  } catch (error) {
    console.log(`   ❌ ERROR: ${error.message}`);
  }
  console.log('');
}

// Test 3: Frontend → Backend Flow (if frontend is running)
async function testFrontendFlow() {
  console.log('🧪 Test 3: Frontend → Backend Flow (localhost:3000)');
  console.log('   Note: This test requires your frontend to be running on port 3000');
  
  try {
    // Test GET through frontend
    const getResponse = await makeRequest(`${FRONTEND_URL}/api/outfits`);
    console.log(`   Frontend GET Status: ${getResponse.status}`);
    
    // Test POST through frontend  
    const postResponse = await makeRequest(`${FRONTEND_URL}/api/outfits`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testOutfitRequest)
    });
    console.log(`   Frontend POST Status: ${postResponse.status}`);
    
    if (getResponse.status === 200 && postResponse.status === 200) {
      console.log('   ✅ SUCCESS: Complete frontend → backend flow working!');
    } else {
      console.log('   ⚠️  PARTIAL: Some endpoints may have issues');
    }
  } catch (error) {
    console.log(`   ❌ ERROR: ${error.message}`);
    console.log('   (Frontend may not be running on port 3000)');
  }
  console.log('');
}

// Main test runner
async function runTests() {
  console.log('🚀 Frontend → Backend Flow Test');
  console.log('================================');
  console.log(`Backend URL: ${BACKEND_URL}`);
  console.log(`Frontend URL: ${FRONTEND_URL}`);
  console.log('');
  
  await testBackendGet();
  await testBackendPost();
  await testFrontendFlow();
  
  console.log('🏁 Test Complete!');
}

// Run tests
runTests().catch(console.error);
