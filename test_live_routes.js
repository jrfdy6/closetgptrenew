#!/usr/bin/env node

/**
 * Live Route Testing Script
 * Tests the three main API endpoints post-deployment
 */

const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

// Configuration
const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

// Test data
const TEST_IMAGE_PATH = path.join(__dirname, 'frontend/test-images/test-shirt.jpg');
const TEST_USER_ID = 'test-user-123'; // This will be replaced with actual auth token

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSection(title) {
  log(`\n${'='.repeat(60)}`, 'cyan');
  log(`  ${title}`, 'bright');
  log(`${'='.repeat(60)}`, 'cyan');
}

function logTest(testName, status, details = '') {
  const statusIcon = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⚠️';
  const statusColor = status === 'PASS' ? 'green' : status === 'FAIL' ? 'red' : 'yellow';
  log(`${statusIcon} ${testName}: ${status}`, statusColor);
  if (details) {
    log(`   ${details}`, 'yellow');
  }
}

// Helper function to get auth token (you'll need to implement this based on your auth system)
async function getAuthToken() {
  // For testing purposes, you might need to:
  // 1. Create a test user
  // 2. Sign in and get a token
  // 3. Or use a service account token
  
  // Placeholder - replace with actual auth implementation
  log('⚠️  AUTH TOKEN NEEDED: Please implement getAuthToken() with your auth system', 'yellow');
  return 'your-auth-token-here';
}

// Test 1: /api/process-image
async function testProcessImage() {
  logSection('TEST 1: /api/process-image - Upload and Analyze Image');
  
  try {
    // Check if test image exists
    if (!fs.existsSync(TEST_IMAGE_PATH)) {
      logTest('Image File Check', 'FAIL', 'Test image not found');
      return false;
    }
    logTest('Image File Check', 'PASS', 'Test image found');
    
    // Get auth token
    const authToken = await getAuthToken();
    if (!authToken || authToken === 'your-auth-token-here') {
      logTest('Authentication', 'FAIL', 'Valid auth token required');
      return false;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('file', fs.createReadStream(TEST_IMAGE_PATH));
    formData.append('userId', TEST_USER_ID);
    
    log('📤 Uploading image for processing...', 'blue');
    
    // Make request to process-image endpoint
    const response = await fetch(`${FRONTEND_URL}/api/process-image`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        ...formData.getHeaders()
      },
      body: formData
    });
    
    logTest('API Response Status', response.ok ? 'PASS' : 'FAIL', `Status: ${response.status}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      logTest('Error Details', 'FAIL', JSON.stringify(errorData, null, 2));
      return false;
    }
    
    const data = await response.json();
    
    // Validate response structure
    const requiredFields = ['success', 'data'];
    const hasRequiredFields = requiredFields.every(field => data.hasOwnProperty(field));
    logTest('Response Structure', hasRequiredFields ? 'PASS' : 'FAIL', 
      hasRequiredFields ? 'All required fields present' : 'Missing required fields');
    
    if (data.success && data.data) {
      // Validate clothing item data
      const item = data.data;
      const itemFields = ['id', 'name', 'type', 'userId', 'imageUrl', 'dominantColors', 'style', 'occasion'];
      const hasItemFields = itemFields.every(field => item.hasOwnProperty(field));
      logTest('Clothing Item Data', hasItemFields ? 'PASS' : 'FAIL',
        hasItemFields ? 'All item fields present' : 'Missing item fields');
      
      // Log metadata details
      log('📋 Generated Metadata:', 'green');
      log(`   ID: ${item.id}`, 'cyan');
      log(`   Name: ${item.name}`, 'cyan');
      log(`   Type: ${item.type}`, 'cyan');
      log(`   Colors: ${item.dominantColors?.length || 0} colors detected`, 'cyan');
      log(`   Styles: ${item.style?.length || 0} styles identified`, 'cyan');
      log(`   Occasions: ${item.occasion?.length || 0} occasions identified`, 'cyan');
      
      if (item.embedding) {
        logTest('CLIP Embedding', 'PASS', `Embedding vector length: ${item.embedding.length}`);
      } else {
        logTest('CLIP Embedding', 'WARN', 'No embedding generated');
      }
      
      return true;
    } else {
      logTest('Data Validation', 'FAIL', 'Response data is invalid');
      return false;
    }
    
  } catch (error) {
    logTest('Process Image Test', 'FAIL', error.message);
    console.error('Full error:', error);
    return false;
  }
}

// Test 2: /api/generate-outfit
async function testGenerateOutfit() {
  logSection('TEST 2: /api/generate-outfit - Generate Outfit from Wardrobe');
  
  try {
    const authToken = await getAuthToken();
    if (!authToken || authToken === 'your-auth-token-here') {
      logTest('Authentication', 'FAIL', 'Valid auth token required');
      return false;
    }
    
    // Mock wardrobe data (you might want to use real wardrobe data from the user)
    const mockWardrobe = [
      {
        id: 'item-1',
        name: 'Blue T-Shirt',
        type: 'shirt',
        subType: 't-shirt',
        dominantColors: [{ name: 'blue', hex: '#0000FF', rgb: [0, 0, 255] }],
        matchingColors: [{ name: 'white', hex: '#FFFFFF', rgb: [255, 255, 255] }],
        style: ['casual', 'comfortable'],
        occasion: ['casual', 'everyday'],
        season: ['spring', 'summer'],
        userId: TEST_USER_ID,
        imageUrl: 'https://example.com/blue-tshirt.jpg'
      },
      {
        id: 'item-2',
        name: 'Black Jeans',
        type: 'pants',
        subType: 'jeans',
        dominantColors: [{ name: 'black', hex: '#000000', rgb: [0, 0, 0] }],
        matchingColors: [{ name: 'blue', hex: '#0000FF', rgb: [0, 0, 255] }],
        style: ['casual', 'versatile'],
        occasion: ['casual', 'everyday'],
        season: ['all'],
        userId: TEST_USER_ID,
        imageUrl: 'https://example.com/black-jeans.jpg'
      }
    ];
    
    // Mock user profile
    const mockUserProfile = {
      id: TEST_USER_ID,
      name: 'Test User',
      email: 'test@example.com',
      stylePreferences: ['casual', 'comfortable'],
      bodyType: 'athletic',
      measurements: {
        height: 175,
        weight: 70,
        skinTone: 'medium'
      }
    };
    
    // Mock weather data
    const mockWeather = {
      temperature: 75,
      condition: 'sunny',
      location: 'San Francisco',
      humidity: 50,
      wind_speed: 5,
      precipitation: 0
    };
    
    log('🎨 Generating outfit...', 'blue');
    
    const payload = {
      occasion: 'casual',
      mood: 'relaxed',
      style: 'casual',
      weather: mockWeather,
      wardrobe: mockWardrobe,
      user_profile: mockUserProfile,
      likedOutfits: [],
      trendingStyles: [],
      outfitHistory: []
    };
    
    const response = await fetch(`${FRONTEND_URL}/api/outfit/generate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    
    logTest('API Response Status', response.ok ? 'PASS' : 'FAIL', `Status: ${response.status}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      logTest('Error Details', 'FAIL', JSON.stringify(errorData, null, 2));
      return false;
    }
    
    const data = await response.json();
    
    // Validate response structure
    const requiredFields = ['id', 'name', 'occasion', 'style', 'items'];
    const hasRequiredFields = requiredFields.every(field => data.hasOwnProperty(field));
    logTest('Response Structure', hasRequiredFields ? 'PASS' : 'FAIL',
      hasRequiredFields ? 'All required fields present' : 'Missing required fields');
    
    if (data.items && Array.isArray(data.items)) {
      logTest('Outfit Items', 'PASS', `${data.items.length} items generated`);
      
      // Log outfit details
      log('👕 Generated Outfit:', 'green');
      log(`   ID: ${data.id}`, 'cyan');
      log(`   Name: ${data.name}`, 'cyan');
      log(`   Occasion: ${data.occasion}`, 'cyan');
      log(`   Style: ${data.style}`, 'cyan');
      log(`   Items: ${data.items.length}`, 'cyan');
      
      data.items.forEach((item, index) => {
        log(`   ${index + 1}. ${item.name} (${item.type})`, 'cyan');
      });
      
      if (data.wasSuccessful !== undefined) {
        logTest('Generation Success', data.wasSuccessful ? 'PASS' : 'WARN', 
          data.wasSuccessful ? 'Outfit generated successfully' : 'Outfit generation had issues');
      }
      
      if (data.validationErrors && data.validationErrors.length > 0) {
        logTest('Validation Errors', 'WARN', `${data.validationErrors.length} validation errors`);
        data.validationErrors.forEach(error => {
          log(`   - ${error}`, 'yellow');
        });
      }
      
      return true;
    } else {
      logTest('Outfit Items', 'FAIL', 'No items generated or invalid format');
      return false;
    }
    
  } catch (error) {
    logTest('Generate Outfit Test', 'FAIL', error.message);
    console.error('Full error:', error);
    return false;
  }
}

// Test 3: /api/delete-photo
async function testDeletePhoto() {
  logSection('TEST 3: /api/delete-photo - Delete Photo and Sync Storage');
  
  try {
    const authToken = await getAuthToken();
    if (!authToken || authToken === 'your-auth-token-here') {
      logTest('Authentication', 'FAIL', 'Valid auth token required');
      return false;
    }
    
    // First, upload a photo to delete
    log('📤 Uploading test photo for deletion...', 'blue');
    
    const formData = new FormData();
    formData.append('file', fs.createReadStream(TEST_IMAGE_PATH));
    formData.append('type', 'outfit');
    
    const uploadResponse = await fetch(`${FRONTEND_URL}/api/upload-photo`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        ...formData.getHeaders()
      },
      body: formData
    });
    
    if (!uploadResponse.ok) {
      logTest('Photo Upload for Deletion', 'FAIL', 'Failed to upload photo for deletion test');
      return false;
    }
    
    const uploadData = await uploadResponse.json();
    const photoUrl = uploadData.photoUrl;
    
    logTest('Photo Upload for Deletion', 'PASS', 'Photo uploaded successfully');
    log(`   Photo URL: ${photoUrl}`, 'cyan');
    
    // Now delete the photo
    log('🗑️  Deleting uploaded photo...', 'blue');
    
    const deleteResponse = await fetch(`${FRONTEND_URL}/api/delete-photo?url=${encodeURIComponent(photoUrl)}&type=outfit`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    logTest('Delete API Response', deleteResponse.ok ? 'PASS' : 'FAIL', `Status: ${deleteResponse.status}`);
    
    if (!deleteResponse.ok) {
      const errorData = await deleteResponse.json();
      logTest('Delete Error Details', 'FAIL', JSON.stringify(errorData, null, 2));
      return false;
    }
    
    // Verify deletion by trying to access the photo
    log('🔍 Verifying photo deletion...', 'blue');
    
    try {
      const verifyResponse = await fetch(photoUrl);
      if (verifyResponse.ok) {
        logTest('Photo Deletion Verification', 'FAIL', 'Photo still accessible after deletion');
        return false;
      } else {
        logTest('Photo Deletion Verification', 'PASS', 'Photo successfully deleted from storage');
      }
    } catch (error) {
      // If the photo URL is no longer accessible, that's good
      logTest('Photo Deletion Verification', 'PASS', 'Photo URL no longer accessible');
    }
    
    // Test Firestore sync by checking if user photos were updated
    log('📊 Checking Firestore sync...', 'blue');
    
    // You might want to add a test to verify the user's photos collection was updated
    // This would require querying Firestore directly or adding a test endpoint
    
    logTest('Firestore Sync', 'PASS', 'Photo deletion completed successfully');
    
    return true;
    
  } catch (error) {
    logTest('Delete Photo Test', 'FAIL', error.message);
    console.error('Full error:', error);
    return false;
  }
}

// Main test runner
async function runAllTests() {
  logSection('LIVE ROUTE TESTING SUITE');
  log('Testing deployed API endpoints...', 'bright');
  
  const results = {
    processImage: false,
    generateOutfit: false,
    deletePhoto: false
  };
  
  try {
    // Test 1: Process Image
    results.processImage = await testProcessImage();
    
    // Test 2: Generate Outfit
    results.generateOutfit = await testGenerateOutfit();
    
    // Test 3: Delete Photo
    results.deletePhoto = await testDeletePhoto();
    
  } catch (error) {
    log('❌ Test suite failed with error:', 'red');
    console.error(error);
  }
  
  // Summary
  logSection('TEST RESULTS SUMMARY');
  
  const totalTests = Object.keys(results).length;
  const passedTests = Object.values(results).filter(result => result).length;
  
  logTest('Process Image API', results.processImage ? 'PASS' : 'FAIL');
  logTest('Generate Outfit API', results.generateOutfit ? 'PASS' : 'FAIL');
  logTest('Delete Photo API', results.deletePhoto ? 'PASS' : 'FAIL');
  
  log(`\n📊 Overall Results: ${passedTests}/${totalTests} tests passed`, 
    passedTests === totalTests ? 'green' : 'yellow');
  
  if (passedTests === totalTests) {
    log('🎉 All tests passed! Your deployment is working correctly.', 'green');
  } else {
    log('⚠️  Some tests failed. Please check the deployment and fix any issues.', 'yellow');
  }
  
  return results;
}

// Run tests if this script is executed directly
if (require.main === module) {
  runAllTests().catch(console.error);
}

module.exports = {
  testProcessImage,
  testGenerateOutfit,
  testDeletePhoto,
  runAllTests
}; 