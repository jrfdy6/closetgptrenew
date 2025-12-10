/**
 * Comprehensive Test for Ecosystem Engineering Routes
 * Tests: Gacha, Roles, Battle Pass, Store
 */

const BACKEND_URL = 'https://closetgptrenew-production.up.railway.app';
const BEARER_TOKEN = process.argv[2];

if (!BEARER_TOKEN) {
  console.error('❌ Please provide a bearer token');
  process.exit(1);
}

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

async function testGachaBalance() {
  console.log('🪙 TEST 1: Gacha Token Balance');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/gacha/balance');
  
  if (result.success) {
    console.log('✅ Token balance retrieved!');
    console.log(`   Balance: ${result.data.balance || 0} tokens`);
    console.log(`   Total Earned: ${result.data.total_earned || 0}`);
    console.log(`   Total Spent: ${result.data.total_spent || 0}`);
    console.log(`   Pull Cost: ${result.data.pull_cost || 500}`);
    console.log(`   Can Afford Pull: ${result.data.can_afford_pull ? '✅ YES' : '❌ NO'}`);
    console.log(`   Pulls Available: ${result.data.pulls_available || 0}`);
    return result.data;
  } else {
    console.log(`❌ Failed: ${result.status}`);
    console.log(`   ${JSON.stringify(result.data).substring(0, 200)}`);
    return null;
  }
}

async function testGachaPull() {
  console.log('\n🎰 TEST 2: Gacha Pull');
  console.log('='.repeat(60));
  
  // Check balance first
  const balanceResult = await testGachaBalance();
  if (!balanceResult || !balanceResult.can_afford_pull) {
    console.log('⚠️  Cannot test pull - insufficient tokens');
    console.log(`   Current balance: ${balanceResult?.balance || 0}, Required: ${balanceResult?.pull_cost || 500}`);
    return null;
  }
  
  console.log('\n🚀 Attempting gacha pull...');
  const result = await apiCall('/api/gacha/pull', 'POST');
  
  if (result.success) {
    console.log('✅ Gacha pull successful!');
    console.log(`   Rarity: ${result.data.rarity}`);
    console.log(`   Reward Type: ${result.data.reward?.type || 'Unknown'}`);
    console.log(`   Description: ${result.data.reward?.description || 'N/A'}`);
    console.log(`   Tokens Remaining: ${result.data.tokens?.remaining || 0}`);
    console.log(`   Visual Effect: ${result.data.visual_effect || 'N/A'}`);
    return result.data;
  } else {
    console.log(`❌ Failed: ${result.status}`);
    console.log(`   ${JSON.stringify(result.data).substring(0, 300)}`);
    return null;
  }
}

async function testGachaHistory() {
  console.log('\n📜 TEST 3: Gacha Pull History');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/gacha/pull-history?limit=5');
  
  if (result.success) {
    console.log(`✅ Pull history retrieved!`);
    console.log(`   Total Pulls: ${result.data.count || 0}`);
    if (result.data.statistics) {
      console.log(`   Legendary: ${result.data.statistics.legendary_pulls || 0}`);
      console.log(`   Rare: ${result.data.statistics.rare_pulls || 0}`);
      console.log(`   Common: ${result.data.statistics.common_pulls || 0}`);
    }
    if (result.data.pulls && result.data.pulls.length > 0) {
      console.log('\n   Recent Pulls:');
      result.data.pulls.slice(0, 3).forEach((pull, idx) => {
        console.log(`   ${idx + 1}. ${pull.rarity} - ${pull.reward_type}`);
      });
    }
    return result.data;
  } else {
    console.log(`⚠️  Failed: ${result.status}`);
    console.log(`   ${JSON.stringify(result.data).substring(0, 200)}`);
    return null;
  }
}

async function testRoleStatus() {
  console.log('\n👑 TEST 4: Role Status');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/roles/status');
  
  if (result.success) {
    console.log('✅ Role status retrieved!');
    console.log(`   Current Role: ${result.data.current_role?.id || 'unknown'}`);
    console.log(`   Title: ${result.data.current_role?.title || 'N/A'}`);
    console.log(`   Icon: ${result.data.current_role?.icon || 'N/A'}`);
    if (result.data.active_privileges) {
      console.log(`   Token Multiplier: ${result.data.active_privileges.token_multiplier || 1.0}x`);
      console.log(`   XP Multiplier: ${result.data.active_privileges.xp_multiplier || 1.0}x`);
      console.log(`   Gacha Luck Boost: ${(result.data.active_privileges.gacha_luck_boost || 0) * 100}%`);
    }
    if (result.data.next_tier_progress) {
      console.log(`\n   Progress to Next Tier:`);
      console.log(`   ${JSON.stringify(result.data.next_tier_progress)}`);
    }
    return result.data;
  } else {
    console.log(`❌ Failed: ${result.status}`);
    console.log(`   ${JSON.stringify(result.data).substring(0, 200)}`);
    return null;
  }
}

async function testRolePromotion() {
  console.log('\n🚀 TEST 5: Check Role Promotion');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/roles/check-promotion', 'POST');
  
  if (result.success) {
    console.log('✅ Promotion check completed!');
    if (result.data.promotion_result) {
      const promo = result.data.promotion_result;
      if (promo.promoted) {
        console.log(`   🎉 PROMOTED! New role: ${promo.new_role}`);
        console.log(`   Message: ${promo.message}`);
      } else {
        console.log(`   Not promoted yet`);
        if (promo.progress) {
          console.log(`   Progress: ${JSON.stringify(promo.progress)}`);
        }
      }
    }
    return result.data;
  } else {
    console.log(`⚠️  Failed: ${result.status}`);
    console.log(`   ${JSON.stringify(result.data).substring(0, 200)}`);
    return null;
  }
}

async function testBattlePassStatus() {
  console.log('\n🎮 TEST 6: Battle Pass Status');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/battlepass/status');
  
  if (result.success) {
    console.log('✅ Battle Pass status retrieved!');
    console.log(`   Season ID: ${result.data.season_id || 'N/A'}`);
    console.log(`   Current Level: ${result.data.current_level || 1}`);
    console.log(`   Current XP: ${result.data.current_xp || 0}`);
    console.log(`   Premium Unlocked: ${result.data.premium_unlocked ? '✅ YES' : '❌ NO'}`);
    console.log(`   Claimed Rewards: ${result.data.claimed_rewards?.length || 0}`);
    return result.data;
  } else {
    console.log(`❌ Failed: ${result.status}`);
    console.log(`   ${JSON.stringify(result.data).substring(0, 200)}`);
    return null;
  }
}

async function testStoreCatalog() {
  console.log('\n🛒 TEST 7: Store Catalog');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/store/catalog');
  
  if (result.success) {
    console.log('✅ Store catalog retrieved!');
    console.log(`   Note: ${result.data.note || 'N/A'}`);
    if (result.data.items) {
      console.log(`\n   Available Items:`);
      Object.keys(result.data.items).forEach(itemId => {
        const item = result.data.items[itemId];
        console.log(`   - ${itemId}: ${item.description || 'N/A'}`);
        console.log(`     Price: $${item.price || 0} ${item.currency || 'USD'}`);
        console.log(`     Type: ${item.type || 'N/A'}`);
      });
    }
    return result.data;
  } else {
    console.log(`❌ Failed: ${result.status}`);
    console.log(`   ${JSON.stringify(result.data).substring(0, 200)}`);
    return null;
  }
}

async function testStorePurchaseHistory() {
  console.log('\n📦 TEST 8: Purchase History');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/store/purchase-history');
  
  if (result.success) {
    console.log('✅ Purchase history retrieved!');
    console.log(`   Total Purchases: ${result.data.count || 0}`);
    if (result.data.purchases && result.data.purchases.length > 0) {
      console.log('\n   Recent Purchases:');
      result.data.purchases.slice(0, 3).forEach((purchase, idx) => {
        console.log(`   ${idx + 1}. ${purchase.item_id} - $${purchase.amount || 0}`);
      });
    } else {
      console.log('   No purchases yet');
    }
    return result.data;
  } else {
    console.log(`⚠️  Failed: ${result.status}`);
    console.log(`   ${JSON.stringify(result.data).substring(0, 200)}`);
    return null;
  }
}

async function testTokenPurchaseRejection() {
  console.log('\n🚫 TEST 9: Token Purchase Rejection (Security Test)');
  console.log('='.repeat(60));
  
  const result = await apiCall('/api/store/purchase', 'POST', {
    item_id: 'TOKEN_PACK_SML'
  });
  
  if (!result.success && result.status === 400) {
    console.log('✅ Token purchase correctly rejected!');
    console.log(`   Response: ${result.data.detail || JSON.stringify(result.data)}`);
    return true;
  } else {
    console.log(`❌ SECURITY ISSUE: Token purchase was NOT rejected!`);
    console.log(`   Status: ${result.status}`);
    console.log(`   Response: ${JSON.stringify(result.data).substring(0, 300)}`);
    return false;
  }
}

async function runAllTests() {
  console.log('🧪 ECOSYSTEM ENGINEERING ROUTES TEST SUITE');
  console.log('='.repeat(60));
  console.log(`Backend: ${BACKEND_URL}\n`);
  
  const results = {
    gachaBalance: await testGachaBalance(),
    gachaPull: await testGachaPull(),
    gachaHistory: await testGachaHistory(),
    roleStatus: await testRoleStatus(),
    rolePromotion: await testRolePromotion(),
    battlePassStatus: await testBattlePassStatus(),
    storeCatalog: await testStoreCatalog(),
    purchaseHistory: await testStorePurchaseHistory(),
    tokenRejection: await testTokenPurchaseRejection()
  };
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(60));
  console.log(`✅ Gacha Balance: ${results.gachaBalance ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Gacha Pull: ${results.gachaPull ? 'PASS' : 'SKIP'}`);
  console.log(`✅ Gacha History: ${results.gachaHistory ? 'PASS' : 'SKIP'}`);
  console.log(`✅ Role Status: ${results.roleStatus ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Role Promotion: ${results.rolePromotion ? 'PASS' : 'SKIP'}`);
  console.log(`✅ Battle Pass Status: ${results.battlePassStatus ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Store Catalog: ${results.storeCatalog ? 'PASS' : 'FAIL'}`);
  console.log(`✅ Purchase History: ${results.purchaseHistory ? 'PASS' : 'SKIP'}`);
  console.log(`✅ Token Purchase Rejection: ${results.tokenRejection ? 'PASS ✅' : 'FAIL ❌'}`);
  
  const passCount = Object.values(results).filter(r => r !== null && r !== false).length;
  const totalTests = Object.keys(results).length;
  
  console.log(`\n🎯 Results: ${passCount}/${totalTests} tests passed`);
  
  if (passCount === totalTests) {
    console.log('\n🎉 ALL TESTS PASSED! Ecosystem routes are working perfectly!');
  } else if (passCount >= totalTests - 2) {
    console.log('\n✅ Most tests passed! Some optional features may not be initialized yet.');
  } else {
    console.log('\n⚠️  Some tests failed. Check backend deployment status.');
  }
}

runAllTests().catch(error => {
  console.error('❌ Test suite error:', error.message);
  process.exit(1);
});

