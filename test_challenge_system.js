/**
 * Comprehensive Challenge System Test
 * Tests challenge catalog, starting challenges, progress tracking, and completion
 */

const BASE_URL = process.env.BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
const BEARER_TOKEN = process.env.BEARER_TOKEN;

if (!BEARER_TOKEN) {
  console.error('❌ BEARER_TOKEN environment variable is required');
  process.exit(1);
}

const headers = {
  'Authorization': `Bearer ${BEARER_TOKEN}`,
  'Content-Type': 'application/json'
};

// Color output helpers
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  red: '\x1b[31m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function fetchAPI(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...options.headers
      }
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${JSON.stringify(data)}`);
    }
    
    return { success: true, data, status: response.status };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function testChallengeSystem() {
  log('\n🎯 CHALLENGE SYSTEM TEST', 'bright');
  log('='.repeat(60), 'cyan');
  
  // Step 1: Get challenge catalog
  log('\n📋 Step 1: Getting Challenge Catalog', 'yellow');
  const catalogResult = await fetchAPI('/api/challenges/catalog');
  if (!catalogResult.success) {
    log(`❌ Failed to get catalog: ${catalogResult.error}`, 'red');
    return;
  }
  
  const catalog = catalogResult.data.data.challenges || [];
  log(`✅ Found ${catalog.length} challenges in catalog`, 'green');
  
  // Show some sample challenges
  log('\n📝 Sample Challenges:', 'cyan');
  catalog.slice(0, 5).forEach(ch => {
    log(`   • ${ch.title} (${ch.challenge_id}) - ${ch.cadence}`, 'reset');
  });
  
  // Step 2: Get available challenges
  log('\n📋 Step 2: Getting Available Challenges', 'yellow');
  const availableResult = await fetchAPI('/api/challenges/available');
  if (!availableResult.success) {
    log(`❌ Failed to get available challenges: ${availableResult.error}`, 'red');
    return;
  }
  
  const available = availableResult.data.data.challenges || [];
  log(`✅ Found ${available.length} available challenges`, 'green');
  
  if (available.length > 0) {
    log('\n📝 Available Challenges:', 'cyan');
    available.slice(0, 10).forEach(ch => {
      log(`   • ${ch.title} (${ch.challenge_id})`, 'reset');
    });
  }
  
  // Step 3: Get active challenges
  log('\n📋 Step 3: Getting Active Challenges', 'yellow');
  const activeResult = await fetchAPI('/api/challenges/active');
  if (!activeResult.success) {
    log(`❌ Failed to get active challenges: ${activeResult.error}`, 'red');
    return;
  }
  
  const active = activeResult.data.data.challenges || [];
  log(`✅ Found ${active.length} active challenges`, 'green');
  
  if (active.length > 0) {
      log('\n📝 Active Challenges:', 'cyan');
      active.forEach(ch => {
        let progress, target, percent;
        
        // Handle annual challenge special structure
        if (ch.challenge_id === 'annual_wardrobe_master') {
          const progressData = ch.progress || {};
          progress = progressData.total_outfits || 0;
          target = 260; // 52 weeks * 5 outfits
          percent = Math.round((progress / target) * 100);
          const weeks = progressData.weeks_completed || 0;
          log(`   • ${ch.title}: ${progress}/260 outfits, ${weeks}/52 weeks (${percent}%)`, 'reset');
        } else {
          progress = typeof ch.progress === 'number' ? ch.progress : 0;
          target = typeof ch.target === 'number' ? ch.target : 1;
          percent = target > 0 ? Math.round((progress / target) * 100) : 0;
          log(`   • ${ch.title}: ${progress}/${target} (${percent}%)`, 'reset');
        }
      });
  }
  
  // Step 4: Start a few challenges
  log('\n📋 Step 4: Starting New Challenges', 'yellow');
  
  // Try to start some "always" cadence challenges
  const alwaysChallenges = catalog.filter(ch => ch.cadence === 'always');
  const challengesToStart = alwaysChallenges.slice(0, 3);
  
  if (challengesToStart.length === 0) {
    log('⚠️  No "always" cadence challenges found to start', 'yellow');
  } else {
    for (const challenge of challengesToStart) {
      log(`\n   Starting: ${challenge.title}...`, 'cyan');
      const startResult = await fetchAPI(`/api/challenges/${challenge.challenge_id}/start`, {
        method: 'POST'
      });
      
      if (startResult.success) {
        log(`   ✅ Started: ${challenge.title}`, 'green');
      } else {
        log(`   ⚠️  Could not start: ${challenge.title} - ${startResult.error}`, 'yellow');
      }
    }
  }
  
  // Step 5: Get user's outfits to log
  log('\n📋 Step 5: Getting User Outfits for Logging', 'yellow');
  const outfitsResult = await fetchAPI('/api/outfits/');
  
  if (!outfitsResult.success) {
    log(`❌ Failed to get outfits: ${outfitsResult.error}`, 'red');
    log('⚠️  Skipping outfit logging test', 'yellow');
  } else {
    const outfits = outfitsResult.data.outfits || [];
    log(`✅ Found ${outfits.length} outfits`, 'green');
    
    if (outfits.length > 0) {
      // Log an outfit to trigger challenge progress
      log('\n📋 Step 6: Logging Outfit to Trigger Challenge Progress', 'yellow');
      const outfitToLog = outfits[0];
      const itemIds = outfitToLog.items?.map(item => item.id) || [];
      
      if (itemIds.length > 0) {
        const logResult = await fetchAPI('/api/outfit-history/mark-worn', {
          method: 'POST',
          body: JSON.stringify({
            outfitId: outfitToLog.id,
            dateWorn: new Date().toISOString(),
            items: itemIds
          })
        });
        
        if (logResult.success) {
          log('✅ Outfit logged successfully', 'green');
          const rewards = logResult.data;
          if (rewards.xp_earned) {
            log(`   📈 XP Earned: ${rewards.xp_earned}`, 'cyan');
          }
          if (rewards.tokens_earned) {
            log(`   🪙 Tokens Earned: ${rewards.tokens_earned}`, 'cyan');
          }
          if (rewards.challenges_completed && rewards.challenges_completed.length > 0) {
            log(`   🎉 Completed Challenges: ${rewards.challenges_completed.length}`, 'green');
            rewards.challenges_completed.forEach(chId => {
              log(`      • ${chId}`, 'cyan');
            });
          }
        } else {
          log(`⚠️  Could not log outfit: ${logResult.error}`, 'yellow');
        }
      } else {
        log('⚠️  Outfit has no items to log', 'yellow');
      }
    } else {
      log('⚠️  No outfits available to log', 'yellow');
    }
  }
  
  // Step 7: Check updated active challenges
  log('\n📋 Step 7: Checking Updated Active Challenges', 'yellow');
  const updatedActiveResult = await fetchAPI('/api/challenges/active');
  if (updatedActiveResult.success) {
    const updatedActive = updatedActiveResult.data.data.challenges || [];
    log(`✅ Found ${updatedActive.length} active challenges`, 'green');
    
    if (updatedActive.length > 0) {
      log('\n📊 Challenge Progress:', 'cyan');
      updatedActive.forEach(ch => {
        let progress, target, percent;
        
        // Handle annual challenge special structure
        if (ch.challenge_id === 'annual_wardrobe_master') {
          const progressData = ch.progress || {};
          progress = progressData.total_outfits || 0;
          target = 260;
          percent = Math.round((progress / target) * 100);
          const weeks = progressData.weeks_completed || 0;
          const status = ch.status || 'unknown';
          log(`   • ${ch.title}: ${progress}/260 outfits, ${weeks}/52 weeks (${percent}%) [${status}]`, 'reset');
        } else {
          progress = typeof ch.progress === 'number' ? ch.progress : 0;
          target = typeof ch.target === 'number' ? ch.target : 1;
          percent = target > 0 ? Math.round((progress / target) * 100) : 0;
          const status = ch.status || 'unknown';
          log(`   • ${ch.title}: ${progress}/${target} (${percent}%) [${status}]`, 'reset');
        }
      });
    }
  }
  
  // Step 8: Get challenge history
  log('\n📋 Step 8: Getting Challenge History', 'yellow');
  const historyResult = await fetchAPI('/api/challenges/history');
  if (historyResult.success) {
    const history = historyResult.data.data.challenges || [];
    log(`✅ Found ${history.length} completed challenges`, 'green');
    
    if (history.length > 0) {
      log('\n🏆 Completed Challenges:', 'cyan');
      history.slice(0, 5).forEach(ch => {
        const completedAt = ch.completed_at || 'unknown';
        log(`   • ${ch.title || ch.challenge_id} - Completed: ${completedAt}`, 'reset');
      });
    }
  }
  
  // Step 9: Get gamification stats
  log('\n📋 Step 9: Getting Gamification Stats', 'yellow');
  const statsResult = await fetchAPI('/api/gamification/stats');
  if (statsResult.success) {
    const stats = statsResult.data;
    log('✅ Gamification Stats:', 'green');
    log(`   📊 Level: ${stats.level?.current || 'N/A'}`, 'cyan');
    log(`   ⭐ XP: ${stats.xp || 0}`, 'cyan');
    log(`   🪙 Tokens: ${stats.tokens_balance || 0}`, 'cyan');
    log(`   🔥 Streak: ${stats.streak?.current_streak || 0} days`, 'cyan');
    log(`   🏆 Badges: ${stats.badges?.length || 0}`, 'cyan');
  }
  
  // Summary
  log('\n' + '='.repeat(60), 'cyan');
  log('✅ CHALLENGE SYSTEM TEST COMPLETE', 'bright');
  log('='.repeat(60), 'cyan');
}

// Run the test
testChallengeSystem().catch(error => {
  log(`\n❌ Test failed with error: ${error.message}`, 'red');
  console.error(error);
  process.exit(1);
});

