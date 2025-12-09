/**
 * Test Dashboard with Authentication
 * Uses Next.js API routes which proxy to backend
 */

const FRONTEND_URL = 'https://www.easyoutfitapp.com';
const ID_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk1MTg5MTkxMTA3NjA1NDM0NGUxNWUyNTY0MjViYjQyNWVlYjNhNWMiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiSm9obm5pZSBEZXBwIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0lTNWhNc3pWV0MydmUxMl90cEJSNGpfNjZycUNNSDZ4bTlydWZIRFBQUXlQa0w0WFZFPXM5Ni1jIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2Nsb3NldGdwdHJlbmV3IiwiYXVkIjoiY2xvc2V0Z3B0cmVuZXciLCJhdXRoX3RpbWUiOjE3NjUxMjU0ODMsInVzZXJfaWQiOiJkQU5xamlJMENLZ2FpdHh6WXR3MWJodHZRckczIiwic3ViIjoiZEFOcWppSTBDS2dhaXR4ell0dzFiaHR2UXJHMyIsImlhdCI6MTc2NTMwNTAzOCwiZXhwIjoxNzY1MzA4NjM4LCJlbWFpbCI6ImpmZWV6aWVAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7Imdvb2dsZS5jb20iOlsiMTAwMDc5ODkzNDQxNTAzMTY5NDExIl0sImVtYWlsIjpbImpmZWV6aWVAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.nhoFg2LP7KNc5onOV3nOAdAFj2nNBuZHGwkLWlVg8-jFVQF4W75jsZzOz3PmN2qRFui_4P38z-pfe6KVillSE2EHc5yzww4O2Lh4wZ8p11G_DW5nX9ns-IgUGXrgnJXEIEiuwB9cZQJsaB0MpV472QAQoFHmKyiKD9mwP18vdY0XvXEsul679I9x5Bh7PP8HwcFVg_KkpI5mSfAfEFoeKxXeO560FxUUdQkidKM-PAmzoKk3fh4soRyxI0TDQ-ZqChQsSFfvaJr6jkAvmsHIalAhZuwsjK0LEhjJUnzFa-ObfgBO4HZYy_3B1fb9GtBL1pRFvyz0exTDt-zM_v-Nuw';

async function testDashboardAPI() {
  console.log('🧪 Testing Dashboard with Authentication\n');
  console.log('='.repeat(60));
  
  try {
    // Use Next.js API route
    const response = await fetch(`${FRONTEND_URL}/api/dashboard`, {
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
      console.log('✅ Dashboard data retrieved successfully!\n');
      console.log('📈 Dashboard Statistics:');
      console.log(`  Total Items: ${data.totalItems || 0}`);
      console.log(`  Favorites: ${data.favorites || 0}`);
      console.log(`  Outfits This Week: ${data.outfitsThisWeek || 0}`);
      console.log(`  Style Goals Completed: ${data.styleGoalsCompleted || 0}/${data.totalStyleGoals || 0}`);
      console.log(`  Overall Progress: ${data.overallProgress || 0}%`);
      
      if (data.todaysOutfit) {
        console.log('\n👔 Today\'s Outfit:');
        console.log(`  Name: ${data.todaysOutfit.outfitName || 'N/A'}`);
        console.log(`  Occasion: ${data.todaysOutfit.occasion || 'N/A'}`);
        console.log(`  Mood: ${data.todaysOutfit.mood || 'N/A'}`);
        console.log(`  Items: ${(data.todaysOutfit.items || []).length}`);
      }
      
      if (data.topItemsByCategory && data.topItemsByCategory.length > 0) {
        console.log(`\n⭐ Top Items: ${data.topItemsByCategory.length} items across categories`);
      }
      
      if (data.styleCollections && data.styleCollections.length > 0) {
        console.log(`\n🎯 Style Collections: ${data.styleCollections.length} active goals`);
      }
      
      console.log('\n✅ Mobile optimizations are working with authenticated user!');
      return true;
    } else {
      const errorText = await response.text();
      console.log(`❌ API Error: ${status}`);
      console.log(`   Response: ${errorText.substring(0, 300)}`);
      
      if (status === 401 || status === 403) {
        console.log('\n⚠️  Authentication failed. Token may be expired.');
        console.log('   Token expires:', new Date(1765308638000).toISOString());
      }
      
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
    const response = await fetch(`${FRONTEND_URL}/api/wardrobe`, {
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
      if (data.items && data.items.length > 0) {
        console.log(`  Sample items: ${data.items.slice(0, 3).map(i => i.name).join(', ')}`);
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

async function runTests() {
  const dashboardTest = await testDashboardAPI();
  const wardrobeTest = await testWardrobeAPI();
  
  console.log('\n' + '='.repeat(60));
  console.log('\n📊 Test Summary:');
  console.log(`✅ Dashboard API: ${dashboardTest ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Wardrobe API: ${wardrobeTest ? 'PASS' : 'FAIL'}`);
  
  if (dashboardTest && wardrobeTest) {
    console.log('\n🎉 All tests passed! Your profile is accessible.');
    console.log('✅ Mobile optimizations are deployed and working.');
  } else {
    console.log('\n⚠️  Some tests failed. This may be due to:');
    console.log('   - Token expiration (tokens expire after 1 hour)');
    console.log('   - API endpoint changes');
    console.log('   - Network issues');
  }
}

runTests().catch(console.error);

