#!/usr/bin/env node

/**
 * OpenWeather API Key Status Test
 * Tests if the API key is properly configured and working
 */

const https = require('https');

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
    const postData = JSON.stringify(data);
    
    const options = {
      hostname: urlObj.hostname,
      port: 443,
      path: urlObj.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      },
      timeout: 10000
    };

    const req = https.request(options, (res) => {
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

async function testAPIKey() {
  log(colors.bold, '🔑 OPENWEATHER API KEY STATUS TEST');
  log(colors.bold, '===================================\n');
  
  const testCases = [
    { name: 'City Name (US)', location: 'New York, NY', expectReal: true },
    { name: 'City Name (UK)', location: 'London, UK', expectReal: true },
    { name: 'Coordinates (NYC)', location: '40.7128, -74.0060', expectReal: true },
    { name: 'Invalid Location', location: 'InvalidCity12345', expectReal: false },
  ];
  
  let workingTests = 0;
  let totalTests = testCases.length;
  
  for (const test of testCases) {
    try {
      log(colors.blue, `Testing: ${test.name} - "${test.location}"`);
      
      const result = await makeRequest(
        'https://closetgptrenew-backend-production.up.railway.app/api/weather',
        { location: test.location }
      );
      
      if (result.status === 200) {
        const weather = result.data;
        if (weather.temperature && weather.condition) {
          log(colors.green, `  ✅ SUCCESS: ${weather.temperature}°F, ${weather.condition}, ${weather.location}`);
          workingTests++;
        } else {
          log(colors.yellow, `  ⚠️ PARTIAL: Missing weather data fields`);
        }
      } else if (result.status === 404 && !test.expectReal) {
        log(colors.green, `  ✅ EXPECTED: Location not found (as expected)`);
        workingTests++;
      } else if (result.status === 500) {
        const error = result.data.detail || 'Unknown error';
        if (error.includes('API key not configured')) {
          log(colors.red, `  ❌ API KEY MISSING: ${error}`);
        } else if (error.includes('Invalid coordinates')) {
          log(colors.red, `  ❌ PARSING ERROR: ${error}`);
        } else {
          log(colors.red, `  ❌ SERVER ERROR: ${error}`);
        }
      } else {
        log(colors.red, `  ❌ HTTP ${result.status}: ${result.data.detail || result.data}`);
      }
      
    } catch (error) {
      log(colors.red, `  ❌ REQUEST FAILED: ${error.message}`);
    }
    
    console.log(); // Empty line for readability
  }
  
  // Results
  const percentage = Math.round((workingTests / totalTests) * 100);
  const color = percentage === 100 ? colors.green : percentage >= 75 ? colors.yellow : colors.red;
  
  log(colors.bold, '📊 RESULTS');
  log(colors.bold, '==========');
  log(color, `${workingTests}/${totalTests} tests passed (${percentage}%)`);
  
  if (percentage === 100) {
    log(colors.green, '\n🎉 API KEY IS 100% WORKING!');
    log(colors.green, '✅ All location types supported');
    log(colors.green, '✅ Real weather data for all valid locations');
  } else if (percentage >= 50) {
    log(colors.yellow, '\n⚠️ API KEY PARTIALLY WORKING');
    log(colors.yellow, '🔧 Some location types may need fixes');
  } else {
    log(colors.red, '\n❌ API KEY NOT WORKING');
    log(colors.red, '🔧 Check Railway environment variables');
  }
  
  // Diagnostic info
  log(colors.blue, '\n🔍 DIAGNOSTIC INFO:');
  log(colors.blue, '• Backend URL: https://closetgptrenew-backend-production.up.railway.app');
  log(colors.blue, '• Expected env var: OPENWEATHER_API_KEY or WEATHER_API_KEY');
  log(colors.blue, '• Coordinates work: Check if NYC coordinates (40.7128, -74.0060) returned real data');
  log(colors.blue, '• City names work: Check if "London, UK" returned real data');
}

testAPIKey().catch(console.error);
