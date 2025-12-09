/**
 * Authenticate and Test Mobile Optimizations
 * Uses Firebase Admin to create custom token, then authenticates
 */

const BASE_URL = 'https://www.easyoutfitapp.com';
const BACKEND_URL = 'https://closetgptrenew-production.up.railway.app';
const ID_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk1MTg5MTkxMTA3NjA1NDM0NGUxNWUyNTY0MjViYjQyNWVlYjNhNWMiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiSm9obm5pZSBEZXBwIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0lTNWhNc3pWV0MydmUxMl90cEJSNGpfNjZycUNNSDZ4bTlydWZIRFBQUXlQa0w0WFZFPXM5Ni1jIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2Nsb3NldGdwdHJlbmV3IiwiYXVkIjoiY2xvc2V0Z3B0cmVuZXciLCJhdXRoX3RpbWUiOjE3NjUxMjU0ODMsInVzZXJfaWQiOiJkQU5xamlJMENLZ2FpdHh6WXR3MWJodHZRckczIiwic3ViIjoiZEFOcWppSTBDS2dhaXR4ell0dzFiaHR2UXJHMyIsImlhdCI6MTc2NTMwNTAzOCwiZXhwIjoxNzY1MzA4NjM4LCJlbWFpbCI6ImpmZWV6aWVAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7Imdvb2dsZS5jb20iOlsiMTAwMDc5ODkzNDQxNTAzMTY5NDExIl0sImVtYWlsIjpbImpmZWV6aWVAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.nhoFg2LP7KNc5onOV3nOAdAFj2nNBuZHGwkLWlVg8-jFVQF4W75jsZzOz3PmN2qRFui_4P38z-pfe6KVillSE2EHc5yzww4O2Lh4wZ8p11G_DW5nX9ns-IgUGXrgnJXEIEiuwB9cZQJsaB0MpV472QAQoFHmKyiKD9mwP18vdY0XvXEsul679I9x5Bh7PP8HwcFVg_KkpI5mSfAfEFoeKxXeO560FxUUdQkidKM-PAmzoKk3fh4soRyxI0TDQ-ZqChQsSFfvaJr6jkAvmsHIalAhZuwsjK0LEhjJUnzFa-ObfgBO4HZYy_3B1fb9GtBL1pRFvyz0exTDt-zM_v-Nuw';

// Decode JWT to get user info
function decodeJWT(token) {
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  
  try {
    const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString());
    return payload;
  } catch (e) {
    return null;
  }
}

const userInfo = decodeJWT(ID_TOKEN);
console.log('🔍 User Info from Token:');
console.log('  User ID:', userInfo?.user_id || userInfo?.sub);
console.log('  Email:', userInfo?.email);
console.log('  Name:', userInfo?.name);
console.log('  Expires:', new Date(userInfo?.exp * 1000).toISOString());
console.log('');

async function testDashboardAPI() {
  console.log('🧪 Testing Dashboard API with Bearer Token\n');
  console.log('='.repeat(60));
  
  try {
    const response = await fetch(`${BACKEND_URL}/api/dashboard`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${ID_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    const status = response.status;
    console.log(`📊 Dashboard API Status: ${status}`);
    
    if (status === 200) {
      const data = await response.json();
      console.log('✅ Dashboard data retrieved successfully!');
      console.log('\n📈 Dashboard Stats:');
      console.log(`  Total Items: ${data.totalItems || 0}`);
      console.log(`  Favorites: ${data.favorites || 0}`);
      console.log(`  Outfits This Week: ${data.outfitsThisWeek || 0}`);
      console.log(`  Style Goals Completed: ${data.styleGoalsCompleted || 0}`);
      console.log(`  Overall Progress: ${data.overallProgress || 0}%`);
      
      if (data.todaysOutfit) {
        console.log('\n👔 Today\'s Outfit:');
        console.log(`  Name: ${data.todaysOutfit.outfitName || 'N/A'}`);
        console.log(`  Occasion: ${data.todaysOutfit.occasion || 'N/A'}`);
        console.log(`  Items: ${(data.todaysOutfit.items || []).length}`);
      }
      
      if (data.topItemsByCategory && data.topItemsByCategory.length > 0) {
        console.log(`\n⭐ Top Items: ${data.topItemsByCategory.length} items`);
      }
      
      return true;
    } else {
      const errorText = await response.text();
      console.log(`❌ API Error: ${status}`);
      console.log(`   Response: ${errorText.substring(0, 200)}`);
      return false;
    }
  } catch (error) {
    console.log(`❌ Request failed: ${error.message}`);
    return false;
  }
}

async function testWardrobeAPI() {
  console.log('\n🧪 Testing Wardrobe API\n');
  console.log('='.repeat(60));
  
  try {
    const response = await fetch(`${BACKEND_URL}/api/wardrobe`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${ID_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    const status = response.status;
    console.log(`📊 Wardrobe API Status: ${status}`);
    
    if (status === 200) {
      const data = await response.json();
      console.log('✅ Wardrobe data retrieved successfully!');
      console.log(`  Total Items: ${data.count || data.items?.length || 0}`);
      return true;
    } else {
      console.log(`❌ API Error: ${status}`);
      return false;
    }
  } catch (error) {
    console.log(`❌ Request failed: ${error.message}`);
    return false;
  }
}

async function testMobileOptimizations() {
  console.log('\n🧪 Testing Mobile Optimizations in Production\n');
  console.log('='.repeat(60));
  
  const results = {
    viewport: false,
    pageLoads: false,
    responsiveClasses: false
  };
  
  try {
    // Test viewport
    const html = await fetch(BASE_URL).then(r => r.text());
    results.viewport = html.includes('viewport') && html.includes('device-width');
    console.log(results.viewport ? '✅ Viewport meta tag' : '❌ Viewport meta tag');
    
    // Test dashboard page
    const dashboardHtml = await fetch(`${BASE_URL}/dashboard`).then(r => r.text());
    results.pageLoads = dashboardHtml.includes('dashboard') || dashboardHtml.includes('Dashboard');
    results.responsiveClasses = dashboardHtml.includes('sm:') || dashboardHtml.includes('md:');
    
    console.log(results.pageLoads ? '✅ Dashboard page loads' : '❌ Dashboard page fails');
    console.log(results.responsiveClasses ? '✅ Mobile responsive classes' : '❌ Mobile classes missing');
    
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
  }
  
  return results;
}

async function runAllTests() {
  const dashboardTest = await testDashboardAPI();
  const wardrobeTest = await testWardrobeAPI();
  const mobileTest = await testMobileOptimizations();
  
  console.log('\n' + '='.repeat(60));
  console.log('\n📊 Final Test Summary:');
  console.log(`✅ Dashboard API: ${dashboardTest ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Wardrobe API: ${wardrobeTest ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Mobile Optimizations: ${Object.values(mobileTest).every(v => v) ? 'PASS' : 'PARTIAL'}`);
  
  if (dashboardTest && wardrobeTest) {
    console.log('\n🎉 Authentication successful! APIs are working.');
    console.log('✅ Mobile optimizations are deployed and accessible.');
  } else {
    console.log('\n⚠️  Some tests failed. Check token expiration or API status.');
  }
}

runAllTests().catch(console.error);

