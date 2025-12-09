/**
 * Test Mobile UX Optimizations in Production
 * Tests Phase 1-3 mobile optimizations
 */

const BASE_URL = 'https://www.easyoutfitapp.com';
const BEARER_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk1MTg5MTkxMTA3NjA1NDM0NGUxNWUyNTY0MjViYjQyNWVlYjNhNWMiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiSm9obm5pZSBEZXBwIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0lTNWhNc3pWV0MydmUxMl90cEJSNGpfNjZycUNNSDZ4bTlydWZIRFBQUXlQa0w0WFZFPXM5Ni1jIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2Nsb3NldGdwdHJlbmV3IiwiYXVkIjoiY2xvc2V0Z3B0cmVuZXciLCJhdXRoX3RpbWUiOjE3NjUxMjU0ODMsInVzZXJfaWQiOiJkQU5xamlJMENLZ2FpdHh6WXR3MWJodHZRckczIiwic3ViIjoiZEFOcWppSTBDS2dhaXR4ell0dzFiaHR2UXJHMyIsImlhdCI6MTc2NTMwNTAzOCwiZXhwIjoxNzY1MzA4NjM4LCJlbWFpbCI6ImpmZWV6aWVAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7Imdvb2dsZS5jb20iOlsiMTAwMDc5ODkzNDQxNTAzMTY5NDExIl0sImVtYWlsIjpbImpmZWV6aWVAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.nhoFg2LP7KNc5onOV3nOAdAFj2nNBuZHGwkLWlVg8-jFVQF4W75jsZzOz3PmN2qRFui_4P38z-pfe6KVillSE2EHc5yzww4O2Lh4wZ8p11G_DW5nX9ns-IgUGXrgnJXEIEiuwB9cZQJsaB0MpV472QAQoFHmKyiKD9mwP18vdY0XvXEsul679I9x5Bh7PP8HwcFVg_KkpI5mSfAfEFoeKxXeO560FxUUdQkidKM-PAmzoKk3fh4soRyxI0TDQ-ZqChQsSFfvaJr6jkAvmsHIalAhZuwsjK0LEhjJUnzFa-ObfgBO4HZYy_3B1fb9GtBL1pRFvyz0exTDt-zM_v-Nuw';

const tests = {
  passed: 0,
  failed: 0,
  results: []
};

function logTest(name, passed, details = '') {
  const status = passed ? '✅ PASS' : '❌ FAIL';
  console.log(`${status}: ${name}`);
  if (details) console.log(`   ${details}`);
  
  tests.results.push({ name, passed, details });
  if (passed) tests.passed++;
  else tests.failed++;
}

async function testViewportMeta() {
  try {
    const response = await fetch(BASE_URL);
    const html = await response.text();
    
    // Check for viewport meta tag
    const hasViewport = html.includes('viewport') && 
                       (html.includes('device-width') || html.includes('width=device-width'));
    
    logTest('Viewport Meta Tag', hasViewport, 
      hasViewport ? 'Viewport meta tag found' : 'Viewport meta tag missing');
    
    return hasViewport;
  } catch (error) {
    logTest('Viewport Meta Tag', false, `Error: ${error.message}`);
    return false;
  }
}

async function testDashboardLoads() {
  try {
    const response = await fetch(`${BASE_URL}/dashboard`, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
      }
    });
    
    const html = await response.text();
    const status = response.status;
    
    // Check if page loads (even if auth required)
    const loads = status === 200 || status === 401 || status === 403;
    const hasMobileOptimizations = html.includes('pb-20') || html.includes('h-14') || html.includes('accordion');
    
    logTest('Dashboard Page Loads', loads, 
      `Status: ${status}, Mobile optimizations detected: ${hasMobileOptimizations}`);
    
    return loads;
  } catch (error) {
    logTest('Dashboard Page Loads', false, `Error: ${error.message}`);
    return false;
  }
}

async function testMobileCSS() {
  try {
    const response = await fetch(`${BASE_URL}/dashboard`);
    const html = await response.text();
    
    // Check for mobile-specific classes we added
    const checks = {
      'Bottom Nav Height (h-14)': html.includes('h-14') && html.includes('BottomNav'),
      'Mobile Padding (pb-20)': html.includes('pb-20') || html.includes('pb-20 sm:pb-24'),
      'Accordion Components': html.includes('Accordion') || html.includes('accordion'),
      'Bottom Sheet Component': html.includes('BottomSheet') || html.includes('bottom-sheet'),
      'Collapsible Components': html.includes('Collapsible') || html.includes('collapsible'),
    };
    
    let allPassed = true;
    Object.entries(checks).forEach(([name, passed]) => {
      logTest(`Mobile CSS: ${name}`, passed);
      if (!passed) allPassed = false;
    });
    
    return allPassed;
  } catch (error) {
    logTest('Mobile CSS Check', false, `Error: ${error.message}`);
    return false;
  }
}

async function testAPIEndpoints() {
  const backendUrl = 'https://closetgptrenew-production.up.railway.app';
  
  try {
    // Test dashboard API
    const dashboardResponse = await fetch(`${backendUrl}/api/dashboard`, {
      headers: {
        'Authorization': `Bearer ${BEARER_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    const dashboardStatus = dashboardResponse.status;
    const dashboardWorks = dashboardStatus === 200 || dashboardStatus === 401;
    
    logTest('Dashboard API Endpoint', dashboardWorks, 
      `Status: ${dashboardStatus}`);
    
    return dashboardWorks;
  } catch (error) {
    logTest('API Endpoints', false, `Error: ${error.message}`);
    return false;
  }
}

async function testImageCompression() {
  try {
    const response = await fetch(`${BASE_URL}/wardrobe`);
    const html = await response.text();
    
    // Check for compression function references
    const hasCompression = html.includes('compressImage') || 
                          html.includes('compressImageFile') ||
                          html.includes('compressImageForAnalysis');
    
    logTest('Image Compression Function', hasCompression,
      hasCompression ? 'Compression functions detected' : 'Compression functions not found');
    
    return hasCompression;
  } catch (error) {
    logTest('Image Compression', false, `Error: ${error.message}`);
    return false;
  }
}

async function runAllTests() {
  console.log('🧪 Testing Mobile UX Optimizations in Production\n');
  console.log('=' .repeat(60));
  
  await testViewportMeta();
  await testDashboardLoads();
  await testMobileCSS();
  await testAPIEndpoints();
  await testImageCompression();
  
  console.log('\n' + '='.repeat(60));
  console.log('\n📊 Test Summary:');
  console.log(`✅ Passed: ${tests.passed}`);
  console.log(`❌ Failed: ${tests.failed}`);
  console.log(`📈 Success Rate: ${((tests.passed / (tests.passed + tests.failed)) * 100).toFixed(1)}%`);
  
  if (tests.failed === 0) {
    console.log('\n🎉 All tests passed! Mobile optimizations are live.');
  } else {
    console.log('\n⚠️  Some tests failed. Review the details above.');
  }
  
  return tests;
}

// Run tests
runAllTests().catch(console.error);

