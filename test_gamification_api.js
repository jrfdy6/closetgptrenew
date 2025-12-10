/**
 * Test script for gamification API endpoints
 * Tests the new timezone-aware token/streak system
 */

const BACKEND_URL = 'https://closetgptrenew-production.up.railway.app';
const BEARER_TOKEN = process.env.BEARER_TOKEN || 'YOUR_TOKEN_HERE';

async function testGamificationAPI() {
    console.log('='.repeat(60));
    console.log('Gamification API Test');
    console.log('='.repeat(60));
    console.log();

    if (BEARER_TOKEN === 'YOUR_TOKEN_HERE') {
        console.log('❌ Please provide a bearer token:');
        console.log('   export BEARER_TOKEN="your-token-here"');
        console.log('   node test_gamification_api.js');
        console.log();
        return;
    }

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${BEARER_TOKEN}`
    };

    // Test 1: Check gamification stats (should show tokens, streak, etc.)
    console.log('📊 Test 1: Get Gamification Stats');
    console.log('-'.repeat(60));
    try {
        const statsResponse = await fetch(`${BACKEND_URL}/api/gamification/stats`, {
            method: 'GET',
            headers: headers
        });
        
        const statsData = await statsResponse.json();
        console.log('Status:', statsResponse.status);
        console.log('Response:', JSON.stringify(statsData, null, 2));
        
        if (statsData.tokens_balance !== undefined) {
            console.log('✅ Tokens field found:', statsData.tokens_balance);
        }
        if (statsData.streak !== undefined) {
            console.log('✅ Streak field found:', statsData.streak);
        }
        console.log();
    } catch (error) {
        console.log('❌ Error:', error.message);
        console.log();
    }

    // Test 2: Get user's outfits first
    console.log('👕 Test 2a: Get User Outfits');
    console.log('-'.repeat(60));
    let outfitId = null;
    let itemIds = [];
    try {
        const outfitsResponse = await fetch(`${BACKEND_URL}/api/outfits/`, {
            method: 'GET',
            headers: headers
        });
        
        const outfitsData = await outfitsResponse.json();
        console.log('Status:', outfitsResponse.status);
        
        if (Array.isArray(outfitsData) && outfitsData.length > 0) {
            outfitId = outfitsData[0].id;
            itemIds = outfitsData[0].items?.map(item => typeof item === 'string' ? item : item.id) || [];
            console.log(`✅ Found ${outfitsData.length} outfits`);
            console.log(`📦 Using outfit ID: ${outfitId}`);
            console.log(`📦 Items: ${itemIds.length} items`);
        } else {
            console.log('⚠️  No outfits found - cannot test outfit logging');
        }
        console.log();
    } catch (error) {
        console.log('❌ Error:', error.message);
        console.log();
    }

    // Test 2b: Log an outfit (this triggers the new gamification system)
    if (outfitId) {
        console.log('👕 Test 2b: Log Outfit (Triggers Gamification)');
        console.log('-'.repeat(60));
        try {
            const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
            const outfitData = {
                outfitId: outfitId,
                dateWorn: today,
                occasion: 'casual',
                mood: 'happy',
                weather: {},
                notes: 'Test outfit log for gamification system',
                tags: []
            };

        const logResponse = await fetch(`${BACKEND_URL}/api/outfit-history/mark-worn`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(outfitData)
        });

        const logData = await logResponse.json();
        console.log('Status:', logResponse.status);
        console.log('Response:', JSON.stringify(logData, null, 2));
        
        // Check for new gamification fields
        if (logData.tokens_earned !== undefined) {
            console.log('✅ tokens_earned:', logData.tokens_earned);
        }
        if (logData.xp_earned !== undefined) {
            console.log('✅ xp_earned:', logData.xp_earned);
        }
        if (logData.current_streak !== undefined) {
            console.log('✅ current_streak:', logData.current_streak);
        }
        if (logData.level_up !== undefined) {
            console.log('✅ level_up:', logData.level_up);
        }
        console.log();
        } catch (error) {
            console.log('❌ Error:', error.message);
            console.log();
        }
    } else {
        console.log('⏭️  Skipping outfit log test - no outfits available');
        console.log();
    }

    // Test 3: Check gacha balance
    console.log('🎰 Test 3: Check Gacha Balance');
    console.log('-'.repeat(60));
    try {
        const gachaResponse = await fetch(`${BACKEND_URL}/api/gacha/balance`, {
            method: 'GET',
            headers: headers
        });

        const gachaData = await gachaResponse.json();
        console.log('Status:', gachaResponse.status);
        console.log('Response:', JSON.stringify(gachaData, null, 2));
        console.log();
    } catch (error) {
        console.log('❌ Error:', error.message);
        console.log();
    }

    console.log('='.repeat(60));
    console.log('Test Complete');
    console.log('='.repeat(60));
}

// Run the test
testGamificationAPI().catch(console.error);

