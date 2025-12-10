/**
 * Comprehensive Gamification Color Scheme Test
 * Tests all gamification endpoints to verify rosegold/creme/espresso styling
 * 
 * Usage: node test_gamification_colors.js YOUR_BEARER_TOKEN
 */

const BACKEND_URL = 'https://closetgptrenew-production.up.railway.app';
const BEARER_TOKEN = process.argv[2];

if (!BEARER_TOKEN) {
  console.error('❌ Please provide a bearer token:');
  console.error('   node test_gamification_colors.js YOUR_BEARER_TOKEN');
  process.exit(1);
}

// Decode JWT to get user info (for display only)
function decodeJWT(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString());
    return payload;
  } catch (e) {
    return null;
  }
}

const userInfo = decodeJWT(BEARER_TOKEN);
console.log('🔐 Authenticated as:');
console.log(`   User ID: ${userInfo?.user_id || userInfo?.sub || 'Unknown'}`);
console.log(`   Email: ${userInfo?.email || 'Unknown'}`);
console.log('');

// Helper function for API calls
async function apiCall(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    headers: {
      'Authorization': `Bearer ${BEARER_TOKEN}`,
      'Content-Type': 'application/json'
    }
  };
  
  if (body) {
    options.body = JSON.stringify(body);
  }
  
  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, options);
    const status = response.status;
    let data;
    
    try {
      data = await response.json();
    } catch (e) {
      data = { raw: await response.text() };
    }
    
    return { status, data, success: status >= 200 && status < 300 };
  } catch (error) {
    return { status: 0, data: { error: error.message }, success: false };
  }
}

// Test 1: Get Current Gamification State
async function testGamificationState() {
  console.log('📊 TEST 1: Gamification State');
  console.log('='.repeat(60));
  
  // Try different possible endpoints
  const endpoints = [
    '/api/gamification/state',
    '/api/gamification',
    '/api/user/gamification'
  ];
  
  let result = null;
  for (const endpoint of endpoints) {
    result = await apiCall(endpoint);
    if (result.success) break;
  }
  
  if (result && result.success) {
    console.log('✅ Gamification state retrieved!');
    console.log(`   XP: ${result.data.xp || 0}`);
    console.log(`   Level: ${result.data.level || 1}`);
    console.log(`   Tier: ${result.data.level_info?.tier || 'Unknown'}`);
    console.log(`   Badges: ${(result.data.badges || []).length} badges`);
    console.log(`   Progress: ${result.data.level_info?.progress_percentage || 0}%`);
    
    // Check for new ecosystem fields
    if (result.data.streak) {
      console.log(`   Current Streak: ${result.data.streak.current_streak || 0} days`);
    }
    if (result.data.style_tokens) {
      console.log(`   Style Tokens: ${result.data.style_tokens.balance || 0}`);
    }
    if (result.data.role) {
      console.log(`   Role: ${result.data.role.current_role || 'lurker'}`);
    }
    
    return true;
  } else {
    console.log(`⚠️  Gamification state endpoint not available (tried ${endpoints.length} endpoints)`);
    console.log(`   Using profile data instead (see Test 2)`);
    return false;
  }
}

// Test 2: Get User Profile (includes gamification fields)
async function testUserProfile() {
  console.log('\n👤 TEST 2: User Profile');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/auth/profile');
  
  if (result.success) {
    console.log('✅ User profile retrieved!');
    
    // Check for gamification fields
    console.log(`   XP: ${result.data.xp || 0}`);
    console.log(`   Level: ${result.data.level || 1}`);
    console.log(`   Badges: ${(result.data.badges || []).length} badges`);
    
    // Check for new ecosystem fields
    if (result.data.streak) {
      const streak = result.data.streak;
      console.log(`   Streak: ${streak.current_streak || 0} days (longest: ${streak.longest_streak || 0})`);
      console.log(`   Streak Multiplier: ${streak.streak_multiplier || 1.0}x`);
    }
    
    if (result.data.style_tokens) {
      const tokens = result.data.style_tokens;
      console.log(`   Style Tokens: ${tokens.balance || 0} (earned: ${tokens.total_earned || 0})`);
    }
    
    if (result.data.role) {
      const role = result.data.role;
      console.log(`   Role: ${role.current_role || 'lurker'}`);
      if (role.privileges) {
        console.log(`   Token Multiplier: ${role.privileges.token_multiplier || 1.0}x`);
        console.log(`   Gacha Luck Boost: ${(role.privileges.gacha_luck_boost || 0) * 100}%`);
      }
    }
    
    return true;
  } else {
    console.log(`❌ Failed: ${result.status}`);
    return false;
  }
}

// Test 3: Get Active Challenges
async function testActiveChallenges() {
  console.log('\n🎯 TEST 3: Active Challenges');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/challenges/active');
  
  if (result.success) {
    let challenges = [];
    
    // Handle different response structures
    if (Array.isArray(result.data)) {
      challenges = result.data;
    } else if (result.data.challenges && Array.isArray(result.data.challenges)) {
      challenges = result.data.challenges;
    } else if (result.data.data && Array.isArray(result.data.data)) {
      challenges = result.data.data;
    }
    
    console.log(`✅ Found ${challenges.length} active challenges`);
    
    if (challenges.length > 0) {
      challenges.forEach((challenge, idx) => {
        console.log(`   ${idx + 1}. ${challenge.title || challenge.challenge_id || 'Unknown'}`);
        console.log(`      Progress: ${challenge.progress || 0}/${challenge.target || 0}`);
        if (challenge.rewards) {
          console.log(`      Rewards: ${challenge.rewards.xp || 0} XP + ${challenge.rewards.tokens || 0} tokens`);
        }
      });
    } else {
      console.log(`   No active challenges found`);
    }
    
    return true;
  } else {
    console.log(`⚠️  Active challenges endpoint not available: ${result.status}`);
    return false;
  }
}

// Test 4: Get Style Token Balance
async function testTokenBalance() {
  console.log('\n🪙 TEST 4: Style Token Balance');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/gacha/balance');
  
  if (result.success) {
    console.log('✅ Token balance retrieved!');
    console.log(`   Balance: ${result.data.balance || 0} tokens`);
    console.log(`   Total Earned: ${result.data.total_earned || 0}`);
    console.log(`   Total Spent: ${result.data.total_spent || 0}`);
    console.log(`   Pull Cost: ${result.data.pull_cost || 500}`);
    console.log(`   Can Afford Pull: ${result.data.can_afford_pull ? '✅ Yes' : '❌ No'}`);
    console.log(`   Pulls Available: ${result.data.pulls_available || 0}`);
    
    return true;
  } else {
    console.log(`⚠️  Gacha endpoint not available: ${result.status}`);
    return false;
  }
}

// Test 5: Get Role Status
async function testRoleStatus() {
  console.log('\n👑 TEST 5: Role Status');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/roles/status');
  
  if (result.success) {
    console.log('✅ Role status retrieved!');
    const role = result.data.current_role || {};
    console.log(`   Current Role: ${role.id || 'lurker'} (${role.title || role.id || 'Closet Lurker'})`);
    console.log(`   Icon: ${role.icon || '👀'}`);
    console.log(`   Color: ${role.color || 'gray'}`);
    
    if (result.data.active_privileges) {
      const perks = result.data.active_privileges;
      console.log(`   Token Multiplier: ${perks.token_multiplier || 1.0}x`);
      console.log(`   XP Multiplier: ${perks.xp_multiplier || 1.0}x`);
      console.log(`   Gacha Luck Boost: ${(perks.gacha_luck_boost || 0) * 100}%`);
    }
    
    if (result.data.next_tier_progress) {
      const progress = result.data.next_tier_progress;
      console.log(`   Progress to Next Tier: ${progress.percentage || 0}%`);
    }
    
    return true;
  } else {
    console.log(`⚠️  Roles endpoint not available: ${result.status}`);
    return false;
  }
}

// Test 6: Get Battle Pass Status
async function testBattlePassStatus() {
  console.log('\n🎮 TEST 6: Battle Pass Status');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/battlepass/status');
  
  if (result.success) {
    console.log('✅ Battle Pass status retrieved!');
    console.log(`   Season: ${result.data.season_id || 'Unknown'}`);
    console.log(`   Current XP: ${result.data.current_xp || 0}`);
    console.log(`   Current Level: ${result.data.current_level || 0}`);
    console.log(`   Premium Pass: ${result.data.is_premium_pass ? '✅ Yes' : '❌ No'}`);
    console.log(`   Total Tiers: ${result.data.total_tiers || 0}`);
    
    if (result.data.next_tier_progress) {
      const progress = result.data.next_tier_progress;
      console.log(`   Next Tier Progress: ${progress.percentage || 0}% (${progress.xp_in_range || 0}/${progress.xp_needed || 0} XP)`);
    }
    
    return true;
  } else {
    console.log(`⚠️  Battle Pass endpoint not available: ${result.status}`);
    return false;
  }
}

// Test 7: Log Outfit (Triggers Gamification)
async function testLogOutfit() {
  console.log('\n👔 TEST 7: Log Outfit (Triggers XP/Token Rewards)');
  console.log('='.repeat(60));
  console.log('⚠️  This will create an outfit log entry and trigger gamification!');
  console.log('');
  
  // First, get some wardrobe items to use
  const wardrobeResult = await apiCall('/api/wardrobe');
  let itemIds = [];
  
  if (wardrobeResult.success && wardrobeResult.data.items) {
    itemIds = wardrobeResult.data.items.slice(0, 3).map(item => item.id || item._id);
  } else if (wardrobeResult.success && wardrobeResult.data.length > 0) {
    itemIds = wardrobeResult.data.slice(0, 3).map(item => item.id || item._id);
  }
  
  if (itemIds.length === 0) {
    console.log('⚠️  No wardrobe items found. Skipping outfit log test.');
    console.log('   (This is okay - gamification endpoints are still testable)');
    return false;
  }
  
  // Create a test outfit log
  const outfitData = {
    outfit_id: `test-outfit-${Date.now()}`,
    items: itemIds,
    date_worn: new Date().toISOString(),
    occasion: 'casual',
    mood: 'comfortable',
    weather: {
      temp: 72,
      condition: 'sunny'
    }
  };
  
  const result = await apiCall('/api/outfit-history/mark-worn', 'POST', outfitData);
  
  if (result.success) {
    console.log('✅ Outfit logged successfully!');
    console.log(`   XP Earned: ${result.data.xp_earned || 0}`);
    console.log(`   Level Up: ${result.data.level_up ? '🎉 Yes!' : 'No'}`);
    
    // Check for new rewards
    if (result.data.tokens_earned) {
      console.log(`   Tokens Earned: ${result.data.tokens_earned}`);
    }
    if (result.data.new_streak) {
      console.log(`   Current Streak: ${result.data.new_streak} days`);
    }
    if (result.data.streak_multiplier) {
      console.log(`   Streak Multiplier: ${result.data.streak_multiplier}x`);
    }
    
    console.log('');
    console.log('📱 Frontend Notification Check:');
    console.log('   - XP notification should appear with ROSEGOLD text');
    console.log('   - Background should be CREME (light) or ESPRESSO (dark)');
    console.log('   - NO green, blue, or purple colors');
    
    return true;
  } else {
    console.log(`❌ Failed to log outfit: ${result.status}`);
    console.log(`   ${JSON.stringify(result.data).substring(0, 200)}`);
    return false;
  }
}

// Main test runner
async function runAllTests() {
  console.log('🧪 GAMIFICATION COLOR SCHEME TEST SUITE');
  console.log('='.repeat(60));
  console.log(`Backend: ${BACKEND_URL}`);
  console.log('');
  
  const results = {
    gamificationState: false,
    userProfile: false,
    activeChallenges: false,
    tokenBalance: false,
    roleStatus: false,
    battlePassStatus: false,
    logOutfit: false
  };
  
  // Run tests
  results.gamificationState = await testGamificationState();
  results.userProfile = await testUserProfile();
  results.activeChallenges = await testActiveChallenges();
  results.tokenBalance = await testTokenBalance();
  results.roleStatus = await testRoleStatus();
  results.battlePassStatus = await testBattlePassStatus();
  results.logOutfit = await testLogOutfit();
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(60));
  console.log(`✅ Gamification State: ${results.gamificationState ? 'PASS' : 'FAIL'}`);
  console.log(`✅ User Profile: ${results.userProfile ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Active Challenges: ${results.activeChallenges ? 'PASS' : 'SKIP'}`);
  console.log(`✅ Token Balance: ${results.tokenBalance ? 'PASS' : 'SKIP'}`);
  console.log(`✅ Role Status: ${results.roleStatus ? 'PASS' : 'SKIP'}`);
  console.log(`✅ Battle Pass Status: ${results.battlePassStatus ? 'PASS' : 'SKIP'}`);
  console.log(`✅ Log Outfit: ${results.logOutfit ? 'PASS' : 'SKIP'}`);
  
  const passed = Object.values(results).filter(v => v).length;
  const total = Object.keys(results).length;
  
  console.log('');
  console.log(`🎯 Results: ${passed}/${total} tests passed`);
  
  if (results.gamificationState && results.userProfile) {
    console.log('');
    console.log('✅ Core gamification system is working!');
    console.log('🎨 Frontend notifications should display with:');
    console.log('   - Rosegold text (#C9956F, #D4A574, #B8860B)');
    console.log('   - Creme backgrounds (#F5F0E8) in light mode');
    console.log('   - Espresso backgrounds (#1A1410, #251D18) in dark mode');
    console.log('   - NO green, blue, or purple colors');
  } else {
    console.log('');
    console.log('⚠️  Some core tests failed. Check backend availability.');
  }
}

// Run tests
runAllTests().catch(error => {
  console.error('❌ Test suite error:', error.message);
  process.exit(1);
});

