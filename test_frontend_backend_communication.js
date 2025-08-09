#!/usr/bin/env node

/**
 * Test script for frontend-backend-Firestore communication
 * This script simulates the frontend making requests to the backend
 */

const fs = require('fs');
const path = require('path');

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3001';
const TEST_IMAGE_PATH = path.join(__dirname, 'test-images', 'test-shirt.jpg');

// Create a simple test image if it doesn't exist
function createTestImage() {
  const testImageDir = path.dirname(TEST_IMAGE_PATH);
  if (!fs.existsSync(testImageDir)) {
    fs.mkdirSync(testImageDir, { recursive: true });
  }
  
  // Create a simple 1x1 pixel JPEG (minimal valid JPEG)
  const minimalJpeg = Buffer.from([
    0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
    0x01, 0x01, 0x00, 0x48, 0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
    0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
    0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
    0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
    0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
    0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
    0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x11, 0x08, 0x00, 0x01,
    0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01,
    0xFF, 0xC4, 0x00, 0x14, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0xFF, 0xC4,
    0x00, 0x14, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xDA, 0x00, 0x0C,
    0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3F, 0x00, 0x8A, 0x00,
    0x07, 0xFF, 0xD9
  ]);
  
  fs.writeFileSync(TEST_IMAGE_PATH, minimalJpeg);
  console.log('✅ Created test image');
}

async function testBackendHealth() {
  console.log('🔍 Testing backend health...');
  
  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Backend is responding:', data);
      return true;
    } else {
      console.log('❌ Backend health check failed:', response.status);
      return false;
    }
  } catch (error) {
    console.log('❌ Backend health check failed:', error.message);
    return false;
  }
}

async function testImageUpload() {
  console.log('🔍 Testing image upload...');
  
  try {
    // Create test image if it doesn't exist
    if (!fs.existsSync(TEST_IMAGE_PATH)) {
      createTestImage();
    }
    
    const formData = new FormData();
    const imageBuffer = fs.readFileSync(TEST_IMAGE_PATH);
    const blob = new Blob([imageBuffer], { type: 'image/jpeg' });
    formData.append('file', blob, 'test-shirt.jpg');
    formData.append('category', 'shirt');
    formData.append('name', 'Test Shirt');
    
    const response = await fetch(`${BACKEND_URL}/api/image/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Image upload successful:', data);
      return data;
    } else {
      const errorData = await response.text();
      console.log('❌ Image upload failed:', response.status, errorData);
      return null;
    }
  } catch (error) {
    console.log('❌ Image upload failed:', error.message);
    return null;
  }
}

async function testWardrobeItemCreation() {
  console.log('🔍 Testing wardrobe item creation...');
  
  try {
    const wardrobeItem = {
      name: "Test Item",
      category: "shirt",
      color: "blue",
      brand: "Test Brand",
      image_url: "https://example.com/test-image.jpg",
      description: "Test item created for communication testing",
      season: "all",
      occasion: ["casual", "test"],
      material: "cotton"
    };
    
    const response = await fetch(`${BACKEND_URL}/api/wardrobe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(wardrobeItem),
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Wardrobe item creation successful:', data);
      return data;
    } else {
      const errorData = await response.text();
      console.log('❌ Wardrobe item creation failed:', response.status, errorData);
      return null;
    }
  } catch (error) {
    console.log('❌ Wardrobe item creation failed:', error.message);
    return null;
  }
}

async function testWardrobeRetrieval() {
  console.log('🔍 Testing wardrobe retrieval...');
  
  try {
    const response = await fetch(`${BACKEND_URL}/api/wardrobe`);
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Wardrobe retrieval successful:', {
        itemCount: data.length || 0,
        items: data
      });
      return data;
    } else {
      const errorData = await response.text();
      console.log('❌ Wardrobe retrieval failed:', response.status, errorData);
      return null;
    }
  } catch (error) {
    console.log('❌ Wardrobe retrieval failed:', error.message);
    return null;
  }
}

async function runAllTests() {
  console.log('🚀 Starting Frontend-Backend-Firestore Communication Tests');
  console.log('=' .repeat(60));
  
  const results = [];
  
  // Test 1: Backend Health
  const healthResult = await testBackendHealth();
  results.push({ test: 'Backend Health', success: healthResult });
  
  if (!healthResult) {
    console.log('❌ Backend is not responding. Stopping tests.');
    return false;
  }
  
  // Test 2: Image Upload
  const uploadResult = await testImageUpload();
  results.push({ test: 'Image Upload', success: !!uploadResult });
  
  // Test 3: Wardrobe Item Creation
  const creationResult = await testWardrobeItemCreation();
  results.push({ test: 'Wardrobe Item Creation', success: !!creationResult });
  
  // Test 4: Wardrobe Retrieval
  const retrievalResult = await testWardrobeRetrieval();
  results.push({ test: 'Wardrobe Retrieval', success: !!retrievalResult });
  
  // Summary
  console.log('\n' + '=' .repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('=' .repeat(60));
  
  const passed = results.filter(r => r.success).length;
  const total = results.length;
  
  results.forEach(result => {
    const status = result.success ? '✅ PASS' : '❌ FAIL';
    console.log(`${status} ${result.test}`);
  });
  
  console.log(`\nOverall: ${passed}/${total} tests passed`);
  
  if (passed === total) {
    console.log('🎉 All tests passed! Frontend can communicate with Firestore through backend.');
  } else {
    console.log('⚠️ Some tests failed. Please check the configuration.');
  }
  
  return passed === total;
}

// Run tests if this script is executed directly
if (require.main === module) {
  runAllTests().then(success => {
    process.exit(success ? 0 : 1);
  }).catch(error => {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
  });
}

module.exports = {
  runAllTests,
  testBackendHealth,
  testImageUpload,
  testWardrobeItemCreation,
  testWardrobeRetrieval
};
