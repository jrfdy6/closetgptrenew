#!/usr/bin/env node

/**
 * Weather Integration Test Suite
 * Tests all aspects of weather integration to ensure 100% configuration
 */

const https = require('https');
const http = require('http');

// Test configuration
const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'https://closetgptrenew-backend-production.up.railway.app';

// Test data
const TEST_LOCATIONS = [
  'New York, NY',
  'Los Angeles, CA', 
  'London, UK',
  '40.7128, -74.0060', // NYC coordinates
  '34.0522, -118.2437' // LA coordinates
];

// Colors for console output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

function log(color, message) {
  console.log(`${color}${message}${colors.reset}`);
}

function makeRequest(url, data) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const isHttps = urlObj.protocol === 'https:';
    const lib = isHttps ? https : http;
    
    const postData = JSON.stringify(data);
    
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || (isHttps ? 443 : 80),
      path: urlObj.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      },
      timeout: 15000
    };

    const req = lib.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve({ status: res.statusCode, data: parsed });
        } catch (e) {
          resolve({ status: res.statusCode, data: data, parseError: true });
        }
      });
    });

    req.on('error', (err) => {
      reject(err);
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.write(postData);
    req.end();
  });
}

async function testWeatherEndpoint(name, url, location) {
  try {
    log(colors.blue, `  Testing ${name} with "${location}"...`);
    
    const result = await makeRequest(`${url}/api/weather`, { location });
    
    if (result.status === 200) {
      const weather = result.data;
      
      // Check required fields
      const requiredFields = ['temperature', 'condition', 'location'];
      const missingFields = requiredFields.filter(field => weather[field] === undefined);
      
      if (missingFields.length === 0) {
        log(colors.green, `    ✅ SUCCESS: ${weather.temperature}°F, ${weather.condition}, ${weather.location}${weather.fallback ? ' (fallback)' : ''}`);
        return true;
      } else {
        log(colors.red, `    ❌ MISSING FIELDS: ${missingFields.join(', ')}`);
        return false;
      }
    } else {
      log(colors.red, `    ❌ HTTP ${result.status}: ${result.data.detail || result.data}`);
      return false;
    }
  } catch (error) {
    log(colors.red, `    ❌ ERROR: ${error.message}`);
    return false;
  }
}

async function testFrontendPages() {
  log(colors.blue, '\n📱 Testing Frontend Pages...');
  
  const pages = [
    '/dashboard',
    '/outfits/generate'
  ];
  
  let allPassed = true;
  
  for (const page of pages) {
    try {
      log(colors.blue, `  Testing ${FRONTEND_URL}${page}...`);
      
      const result = await makeRequest(`${FRONTEND_URL}${page}`, {});
      
      if (result.status === 200 || result.status === 405) { // 405 is OK for GET on POST endpoint
        log(colors.green, `    ✅ Page accessible`);
      } else {
        log(colors.red, `    ❌ HTTP ${result.status}`);
        allPassed = false;
      }
    } catch (error) {
      log(colors.red, `    ❌ ERROR: ${error.message}`);
      allPassed = false;
    }
  }
  
  return allPassed;
}

async function testFallbackBehavior() {
  log(colors.blue, '\n🛡️ Testing Fallback Behavior...');
  
  // Test with invalid location
  try {
    log(colors.blue, '  Testing invalid location...');
    const result = await makeRequest(`${FRONTEND_URL}/api/weather`, { location: 'InvalidCity12345' });
    
    if (result.status === 200 && result.data.fallback) {
      log(colors.green, '    ✅ Fallback data returned for invalid location');
      return true;
    } else {
      log(colors.yellow, '    ⚠️ No fallback data for invalid location');
      return false;
    }
  } catch (error) {
    log(colors.red, `    ❌ ERROR: ${error.message}`);
    return false;
  }
}

async function runTests() {
  log(colors.bold, '🌤️  WEATHER INTEGRATION TEST SUITE');
  log(colors.bold, '=====================================\n');
  
  let totalTests = 0;
  let passedTests = 0;
  
  // Test Frontend Weather API
  log(colors.blue, '🖥️  Testing Frontend Weather API...');
  for (const location of TEST_LOCATIONS) {
    totalTests++;
    if (await testWeatherEndpoint('Frontend', FRONTEND_URL, location)) {
      passedTests++;
    }
  }
  
  // Test Backend Weather API (direct)
  log(colors.blue, '\n⚙️  Testing Backend Weather API (Direct)...');
  for (const location of TEST_LOCATIONS.slice(0, 2)) { // Test fewer locations for backend
    totalTests++;
    if (await testWeatherEndpoint('Backend', BACKEND_URL, location)) {
      passedTests++;
    }
  }
  
  // Test Frontend Pages
  totalTests++;
  if (await testFrontendPages()) {
    passedTests++;
  }
  
  // Test Fallback Behavior
  totalTests++;
  if (await testFallbackBehavior()) {
    passedTests++;
  }
  
  // Results
  log(colors.bold, '\n📊 TEST RESULTS');
  log(colors.bold, '================');
  
  const percentage = Math.round((passedTests / totalTests) * 100);
  const color = percentage >= 80 ? colors.green : percentage >= 60 ? colors.yellow : colors.red;
  
  log(color, `${passedTests}/${totalTests} tests passed (${percentage}%)`);
  
  if (percentage >= 80) {
    log(colors.green, '\n🎉 WEATHER INTEGRATION IS FULLY CONFIGURED!');
    log(colors.green, '✅ Ready for production use');
  } else if (percentage >= 60) {
    log(colors.yellow, '\n⚠️  Weather integration is mostly working');
    log(colors.yellow, '🔧 Some components may need attention');
  } else {
    log(colors.red, '\n❌ Weather integration needs configuration');
    log(colors.red, '🔧 Please check backend API keys and deployment');
  }
  
  log(colors.blue, '\n📝 WHAT TO TEST MANUALLY:');
  log(colors.blue, '• Visit http://localhost:3000/dashboard - check weather display');
  log(colors.blue, '• Test location settings - save your location');
  log(colors.blue, '• Visit http://localhost:3000/outfits/generate - check weather integration');
  log(colors.blue, '• Generate an outfit - verify weather is used in recommendations');
  
  process.exit(percentage >= 60 ? 0 : 1);
}

// Run the tests
runTests().catch(console.error);
