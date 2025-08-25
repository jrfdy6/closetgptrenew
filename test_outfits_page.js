#!/usr/bin/env node

/**
 * Outfits Page Test - Focused testing for outfits functionality
 * Run with: node test_outfits_page.js
 */

const https = require('https');

// Configuration
const BACKEND_URL = 'https://closetgptrenew-backend-production.up.railway.app';
const FRONTEND_URL = 'http://localhost:3000';

// Test data for outfit generation
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

// Test 1: Outfits List (GET /api/outfits)
async function testOutfitsList() {
  console.log('🧪 Test 1: Outfits List (GET /api/outfits)');
  console.log('   This tests the main outfits listing page');
  
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/outfits`);
    console.log(`   Status: ${response.status}`);
    
    if (response.status === 200) {
      console.log('   ✅ SUCCESS: Outfits list working');
      if (Array.isArray(response.data)) {
        console.log(`   📊 Found ${response.data.length} outfits`);
        if (response.data.length > 0) {
          const firstOutfit = response.data[0];
          console.log(`   🎯 First outfit: ${firstOutfit.name} (${firstOutfit.style})`);
        }
      }
    } else if (response.status === 405) {
      console.log('   ❌ FAILED: Method Not Allowed - route not properly configured');
    } else {
      console.log(`   ❌ FAILED: Status ${response.status}`);
      console.log(`   Response: ${JSON.stringify(response.data)}`);
    }
  } catch (error) {
    console.log(`   ❌ ERROR: ${error.message}`);
  }
  console.log('');
}

// Test 2: Generate New Outfit (POST /api/outfits/generate)
async function testGenerateOutfit() {
  console.log('🧪 Test 2: Generate New Outfit (POST /api/outfits/generate)');
  console.log('   This tests creating a new outfit from the outfits page');
  
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
      console.log('   ✅ SUCCESS: Outfit generation working');
      console.log(`   🆔 Generated Outfit ID: ${response.data.id}`);
      console.log(`   🎨 Style: ${response.data.style}`);
      console.log(`   😊 Mood: ${response.data.mood}`);
      console.log(`   📅 Occasion: ${response.data.occasion}`);
    } else {
      console.log(`   ❌ FAILED: Status ${response.status}`);
      console.log(`   Response: ${JSON.stringify(response.data)}`);
    }
  } catch (error) {
    console.log(`   ❌ ERROR: ${error.message}`);
  }
  console.log('');
}

// Test 3: Frontend Outfits Page Flow
async function testFrontendOutfitsPage() {
  console.log('🧪 Test 3: Frontend Outfits Page Flow');
  console.log('   This tests the complete frontend → backend flow for outfits');
  console.log('   Note: Requires frontend running on localhost:3000');
  
  try {
    // Test GET outfits through frontend
    console.log('   📱 Testing GET through frontend...');
    const getResponse = await makeRequest(`${FRONTEND_URL}/api/outfits`);
    console.log(`      Frontend GET Status: ${getResponse.status}`);
    
    // Test POST outfit generation through frontend
    console.log('   📱 Testing POST through frontend...');
    const postResponse = await makeRequest(`${FRONTEND_URL}/api/outfits`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testOutfitRequest)
    });
    console.log(`      Frontend POST Status: ${postResponse.status}`);
    
    // Summary
    if (getResponse.status === 200 && postResponse.status === 200) {
      console.log('   🎉 SUCCESS: Complete outfits page flow working!');
      console.log('   ✅ Users can view outfits list');
      console.log('   ✅ Users can generate new outfits');
    } else {
      console.log('   ⚠️  PARTIAL: Some outfits page features may have issues');
      if (getResponse.status !== 200) {
        console.log(`      ❌ Outfits list not working (${getResponse.status})`);
      }
      if (postResponse.status !== 200) {
        console.log(`      ❌ Outfit generation not working (${postResponse.status})`);
      }
    }
  } catch (error) {
    console.log(`   ❌ ERROR: ${error.message}`);
    console.log('   (Frontend may not be running on port 3000)');
  }
  console.log('');
}

// Test 4: Outfit Details (GET /api/outfits/{id})
async function testOutfitDetails() {
  console.log('🧪 Test 4: Outfit Details (GET /api/outfits/{id})');
  console.log('   This tests viewing individual outfit details');
  
  try {
    // First generate an outfit to get an ID
    const generateResponse = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testOutfitRequest)
    });
    
    if (generateResponse.status === 200) {
      const outfitId = generateResponse.data.id;
      console.log(`   🔍 Testing with outfit ID: ${outfitId}`);
      
      // Now test getting the outfit details
      const detailsResponse = await makeRequest(`${BACKEND_URL}/api/outfits/${outfitId}`);
      console.log(`   Details Status: ${detailsResponse.status}`);
      
      if (detailsResponse.status === 200) {
        console.log('   ✅ SUCCESS: Outfit details working');
        console.log(`   📋 Outfit: ${detailsResponse.data.name}`);
      } else {
        console.log(`   ❌ FAILED: Status ${detailsResponse.status}`);
        console.log(`   Response: ${JSON.stringify(detailsResponse.data)}`);
      }
    } else {
      console.log('   ⚠️  SKIPPED: Could not generate outfit for testing');
    }
  } catch (error) {
    console.log(`   ❌ ERROR: ${error.message}`);
  }
  console.log('');
}

// Main test runner
async function runOutfitsPageTests() {
  console.log('🚀 Outfits Page Test Suite');
  console.log('==========================');
  console.log(`Backend URL: ${BACKEND_URL}`);
  console.log(`Frontend URL: ${FRONTEND_URL}`);
  console.log('');
  
  await testOutfitsList();
  await testGenerateOutfit();
  await testOutfitDetails();
  await testFrontendOutfitsPage();
  
  console.log('🏁 Outfits Page Test Complete!');
  console.log('');
  console.log('📊 Summary:');
  console.log('   • Test 1: Outfits List (Main page)');
  console.log('   • Test 2: Generate Outfit (Create functionality)');
  console.log('   • Test 3: Frontend Flow (User experience)');
  console.log('   • Test 4: Outfit Details (Individual view)');
}

// Run tests
runOutfitsPageTests().catch(console.error);
