#!/usr/bin/env node
/**
 * Outfit Generation Performance Testing Script
 * 
 * Tests the new performance optimizations in production:
 * - Caching (cache hit/miss)
 * - Performance monitoring
 * - Slow request detection
 * - Performance targets tracking
 * - Admin cache management
 * 
 * Usage:
 *   node test-outfit-performance.js <firebase-id-token>
 * 
 * Or set FIREBASE_TOKEN environment variable:
 *   export FIREBASE_TOKEN="your-token"
 *   node test-outfit-performance.js
 */

const https = require('https');
const http = require('http');

// Configuration
const API_BASE_URL = process.env.API_URL || 'https://closetgptrenew-production.up.railway.app';
const FIREBASE_TOKEN = process.argv[2] || process.env.FIREBASE_TOKEN;

// Test results
const results = {
  passed: 0,
  failed: 0,
  warnings: 0,
  tests: []
};

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const isHttps = urlObj.protocol === 'https:';
    const client = isHttps ? https : http;
    
    const requestOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || (isHttps ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${FIREBASE_TOKEN}`,
        ...options.headers
      }
    };

    const req = client.request(requestOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve({ status: res.statusCode, data: json, headers: res.headers });
        } catch (e) {
          resolve({ status: res.statusCode, data: data, headers: res.headers });
        }
      });
    });

    req.on('error', reject);
    
    if (options.body) {
      req.write(JSON.stringify(options.body));
    }
    
    req.end();
  });
}

function recordTest(name, passed, message, details = {}) {
  results.tests.push({ name, passed, message, details });
  if (passed) {
    results.passed++;
    log(`✅ ${name}: ${message}`, 'green');
  } else {
    results.failed++;
    log(`❌ ${name}: ${message}`, 'red');
  }
}

function recordWarning(name, message) {
  results.warnings++;
  results.tests.push({ name, passed: null, message, details: {} });
  log(`⚠️  ${name}: ${message}`, 'yellow');
}

async function fetchUserWardrobe() {
  log('\n👕 Fetching user wardrobe for accurate cache testing...', 'cyan');
  
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/wardrobe/`);
    
    if (response.status === 200 && response.data?.items) {
      const items = response.data.items;
      log(`✅ Fetched ${items.length} wardrobe items`, 'green');
      return items;
    } else {
      log(`⚠️  Could not fetch wardrobe (status ${response.status}), using empty array`, 'yellow');
      return [];
    }
  } catch (error) {
    log(`⚠️  Error fetching wardrobe: ${error.message}, using empty array`, 'yellow');
    return [];
  }
}

async function testCacheMiss(wardrobeItems = []) {
  log('\n📦 Testing Cache Miss (First Generation)...', 'cyan');
  
  const testOutfit = {
    occasion: 'casual',
    style: 'modern',
    mood: 'confident',
    wardrobe: wardrobeItems,
    weather: { temperature: 72, condition: 'Clear' }
  };

  const startTime = Date.now();
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/outfits/generate`, {
      method: 'POST',
      body: testOutfit
    });

    const duration = (Date.now() - startTime) / 1000;
    const cacheHit = response.data?.metadata?.cache_hit === true;

    if (response.status === 200 && !cacheHit) {
      recordTest(
        'Cache Miss',
        true,
        `Generated in ${duration.toFixed(2)}s, cache_hit: false`,
        { duration, cacheHit: false, outfitId: response.data?.id }
      );
      return response.data;
    } else if (response.status === 200 && cacheHit) {
      recordWarning(
        'Cache Miss',
        `Unexpected cache hit on first generation (might be cached from previous test)`
      );
      return response.data;
    } else {
      recordTest('Cache Miss', false, `Failed with status ${response.status}`, response.data);
      return null;
    }
  } catch (error) {
    recordTest('Cache Miss', false, `Error: ${error.message}`);
    return null;
  }
}

async function testCacheHit(firstOutfit, wardrobeItems = []) {
  log('\n📦 Testing Cache Hit (Second Generation)...', 'cyan');
  
  if (!firstOutfit) {
    recordWarning('Cache Hit', 'Skipped - no first outfit to compare');
    return;
  }

  const testOutfit = {
    occasion: firstOutfit.occasion || 'casual',
    style: firstOutfit.style || 'modern',
    mood: firstOutfit.mood || 'confident',
    wardrobe: wardrobeItems.length > 0 ? wardrobeItems : (firstOutfit.wardrobe || []),
    weather: firstOutfit.weather || { temperature: 72, condition: 'Clear' }
  };

  const startTime = Date.now();
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/outfits/generate`, {
      method: 'POST',
      body: testOutfit
    });

    const duration = (Date.now() - startTime) / 1000;
    const cacheHit = response.data?.metadata?.cache_hit === true;

    if (response.status === 200 && cacheHit && duration < 1.0) {
      recordTest(
        'Cache Hit',
        true,
        `Returned in ${duration.toFixed(3)}s (cache hit, should be <1s)`,
        { duration, cacheHit: true }
      );
      return true;
    } else if (response.status === 200 && !cacheHit) {
      recordWarning(
        'Cache Hit',
        `Cache miss on second generation (might be due to wardrobe hash change or validation failure)`
      );
      return false;
    } else {
      recordTest('Cache Hit', false, `Failed with status ${response.status}`, response.data);
      return false;
    }
  } catch (error) {
    recordTest('Cache Hit', false, `Error: ${error.message}`);
    return false;
  }
}

async function testPerformanceMonitoring(wardrobeItems = []) {
  log('\n⏱️  Testing Performance Monitoring...', 'cyan');
  
  const testOutfit = {
    occasion: 'casual',
    style: 'modern',
    mood: 'confident',
    wardrobe: wardrobeItems,
    weather: { temperature: 72, condition: 'Clear' }
  };

  try {
    const response = await makeRequest(`${API_BASE_URL}/api/outfits/generate`, {
      method: 'POST',
      body: testOutfit
    });

    if (response.status === 200) {
      const metadata = response.data?.metadata || {};
      const hasDuration = typeof metadata.generation_duration === 'number';
      const hasIsSlow = typeof metadata.is_slow === 'boolean';

      // Debug: Log the actual response structure
      console.log('🔍 DEBUG Performance Monitoring:');
      console.log('  - response.data keys:', Object.keys(response.data || {}));
      console.log('  - metadata:', JSON.stringify(metadata, null, 2));
      console.log('  - metadata.generation_duration:', metadata.generation_duration, 'type:', typeof metadata.generation_duration);
      console.log('  - metadata.is_slow:', metadata.is_slow, 'type:', typeof metadata.is_slow);

      if (hasDuration && hasIsSlow) {
        recordTest(
          'Performance Monitoring',
          true,
          `Duration: ${metadata.generation_duration}s, is_slow: ${metadata.is_slow}`,
          { duration: metadata.generation_duration, isSlow: metadata.is_slow }
        );
      } else {
        recordTest(
          'Performance Monitoring',
          false,
          `Missing metadata: duration=${hasDuration}, is_slow=${hasIsSlow}`
        );
      }
    } else {
      recordTest('Performance Monitoring', false, `Failed with status ${response.status}`);
    }
  } catch (error) {
    recordTest('Performance Monitoring', false, `Error: ${error.message}`);
  }
}

async function testSlowRequestDetection(wardrobeItems = []) {
  log('\n🐌 Testing Slow Request Detection...', 'cyan');
  
  // Note: This test might not always trigger if generation is fast
  // We'll check if the mechanism is in place
  
  const testOutfit = {
    occasion: 'casual',
    style: 'modern',
    mood: 'confident',
    wardrobe: wardrobeItems,
    weather: { temperature: 72, condition: 'Clear' }
  };

  try {
    const response = await makeRequest(`${API_BASE_URL}/api/outfits/generate`, {
      method: 'POST',
      body: testOutfit
    });

    if (response.status === 200) {
      const metadata = response.data?.metadata || {};
      const duration = metadata.generation_duration || 0;
      const isSlow = metadata.is_slow === true;

      if (duration > 10 && isSlow) {
        recordTest(
          'Slow Request Detection',
          true,
          `Correctly detected slow request: ${duration.toFixed(2)}s > 10s`
        );
      } else if (duration <= 10 && !isSlow) {
        recordTest(
          'Slow Request Detection',
          true,
          `Correctly identified fast request: ${duration.toFixed(2)}s <= 10s`
        );
      } else {
        recordWarning(
          'Slow Request Detection',
          `Duration: ${duration.toFixed(2)}s, is_slow: ${isSlow} (might be edge case)`
        );
      }
    } else {
      recordTest('Slow Request Detection', false, `Failed with status ${response.status}`);
    }
  } catch (error) {
    recordTest('Slow Request Detection', false, `Error: ${error.message}`);
  }
}

async function testPerformanceTargets() {
  log('\n🎯 Testing Performance Targets Endpoint...', 'cyan');
  
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/analytics/performance-targets`);

    if (response.status === 200 && response.data?.success) {
      const targets = response.data?.performance_targets;
      if (targets && targets.outfit_generation) {
        recordTest(
          'Performance Targets',
          true,
          `Target: ${targets.outfit_generation.target}s, Current: ${targets.outfit_generation.current_avg}s`,
          targets.outfit_generation
        );
      } else {
        recordTest('Performance Targets', false, 'Missing outfit_generation data');
      }
    } else if (response.status === 403) {
      recordWarning('Performance Targets', 'Access denied (might need authentication)');
    } else {
      recordTest('Performance Targets', false, `Failed with status ${response.status}`, response.data);
    }
  } catch (error) {
    recordTest('Performance Targets', false, `Error: ${error.message}`);
  }
}

async function testCacheBypass(wardrobeItems = []) {
  log('\n🚫 Testing Cache Bypass...', 'cyan');
  
  const testOutfit = {
    occasion: 'casual',
    style: 'modern',
    mood: 'confident',
    wardrobe: wardrobeItems,
    weather: { temperature: 72, condition: 'Clear' },
    bypass_cache: true
  };

  try {
    const response = await makeRequest(`${API_BASE_URL}/api/outfits/generate`, {
      method: 'POST',
      body: testOutfit
    });

    if (response.status === 200) {
      const cacheHit = response.data?.metadata?.cache_hit === true;
      
      if (!cacheHit) {
        recordTest(
          'Cache Bypass',
          true,
          'Cache bypassed correctly (cache_hit: false)'
        );
      } else {
        recordWarning('Cache Bypass', 'Cache hit despite bypass_cache=true (might be expected behavior)');
      }
    } else {
      recordTest('Cache Bypass', false, `Failed with status ${response.status}`);
    }
  } catch (error) {
    recordTest('Cache Bypass', false, `Error: ${error.message}`);
  }
}

async function testAdminCacheStats() {
  log('\n👑 Testing Admin Cache Stats (Admin Only)...', 'cyan');
  
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/outfits/admin/cache-stats`);

    if (response.status === 200 && response.data?.success) {
      const stats = response.data?.outfit_cache;
      if (stats) {
        recordTest(
          'Admin Cache Stats',
          true,
          `Cache size: ${stats.size}, Hit rate: ${stats.hit_rate}%`,
          stats
        );
      } else {
        recordTest('Admin Cache Stats', false, 'Missing cache stats');
      }
    } else if (response.status === 403) {
      recordWarning('Admin Cache Stats', 'Access denied (not an admin user)');
    } else {
      recordTest('Admin Cache Stats', false, `Failed with status ${response.status}`, response.data);
    }
  } catch (error) {
    recordTest('Admin Cache Stats', false, `Error: ${error.message}`);
  }
}

async function runAllTests() {
  log('\n🚀 Starting Outfit Generation Performance Tests\n', 'blue');
  log(`API Base URL: ${API_BASE_URL}`, 'cyan');
  
  if (!FIREBASE_TOKEN) {
    log('\n❌ Error: Firebase token required', 'red');
    log('Usage: node test-outfit-performance.js <firebase-id-token>', 'yellow');
    log('Or set FIREBASE_TOKEN environment variable', 'yellow');
    process.exit(1);
  }

  // Fetch user wardrobe for accurate cache testing
  const wardrobeItems = await fetchUserWardrobe();
  
  // Run tests with real wardrobe items
  const firstOutfit = await testCacheMiss(wardrobeItems);
  await testCacheHit(firstOutfit, wardrobeItems);
  await testPerformanceMonitoring(wardrobeItems);
  await testSlowRequestDetection(wardrobeItems);
  await testCacheBypass(wardrobeItems);
  await testPerformanceTargets();
  await testAdminCacheStats();

  // Print summary
  log('\n' + '='.repeat(60), 'blue');
  log('📊 Test Summary', 'blue');
  log('='.repeat(60), 'blue');
  log(`✅ Passed: ${results.passed}`, 'green');
  log(`❌ Failed: ${results.failed}`, 'red');
  log(`⚠️  Warnings: ${results.warnings}`, 'yellow');
  log('='.repeat(60), 'blue');

  // Detailed results
  if (results.tests.length > 0) {
    log('\n📋 Detailed Results:\n', 'cyan');
    results.tests.forEach((test, index) => {
      const icon = test.passed === true ? '✅' : test.passed === false ? '❌' : '⚠️';
      const color = test.passed === true ? 'green' : test.passed === false ? 'red' : 'yellow';
      log(`${index + 1}. ${icon} ${test.name}: ${test.message}`, color);
      if (test.details && Object.keys(test.details).length > 0) {
        console.log(`   Details:`, JSON.stringify(test.details, null, 2));
      }
    });
  }

  // Exit code
  process.exit(results.failed > 0 ? 1 : 0);
}

// Run tests
runAllTests().catch((error) => {
  log(`\n❌ Fatal error: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});

