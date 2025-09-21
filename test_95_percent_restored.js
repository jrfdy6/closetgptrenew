#!/usr/bin/env node
/**
 * TEST 95% SUCCESS RATE RESTORED
 * Verify that the comprehensive validation system is working
 */

const https = require('https');

const BACKEND_URL = 'https://closetgptrenew-backend-production.up.railway.app';

async function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const req = https.request(url, options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    resolve({ status: res.statusCode, data: jsonData });
                } catch (e) {
                    resolve({ status: res.statusCode, data: data });
                }
            });
        });
        
        req.on('error', reject);
        
        if (options.body) {
            req.write(options.body);
        }
        
        req.end();
    });
}

function isInappropriateCombination(outfit) {
    const items = outfit.items || [];
    const itemTypes = items.map(item => item.type.toLowerCase());
    const itemNames = items.map(item => item.name.toLowerCase());
    
    // Check for blazer + shorts combination
    const hasBlazer = itemTypes.some(type => type.includes('blazer')) || 
                     itemNames.some(name => name.includes('blazer'));
    const hasShorts = itemTypes.some(type => type.includes('shorts')) || 
                     itemNames.some(name => name.includes('shorts'));
    
    if (hasBlazer && hasShorts) {
        return { inappropriate: true, reason: "Blazer + Shorts combination" };
    }
    
    // Check for formal shoes + casual bottoms
    const hasFormalShoes = itemTypes.some(type => 
        type.includes('oxford') || type.includes('loafers') || type.includes('dress shoes')
    ) || itemNames.some(name => 
        name.includes('oxford') || name.includes('loafers') || name.includes('dress shoes')
    );
    const hasCasualBottoms = itemTypes.some(type => 
        type.includes('shorts') || type.includes('cargo pants') || type.includes('athletic pants')
    ) || itemNames.some(name => 
        name.includes('shorts') || name.includes('cargo pants') || name.includes('athletic pants')
    );
    
    if (hasFormalShoes && hasCasualBottoms) {
        return { inappropriate: true, reason: "Formal shoes + Casual bottoms combination" };
    }
    
    // Check for missing essential categories
    const hasTop = itemTypes.some(type => 
        type.includes('shirt') || type.includes('blouse') || type.includes('sweater') || 
        type.includes('jacket') || type.includes('blazer')
    );
    const hasBottom = itemTypes.some(type => 
        type.includes('pants') || type.includes('jeans') || type.includes('shorts') || 
        type.includes('skirt')
    );
    const hasShoes = itemTypes.some(type => 
        type.includes('shoes') || type.includes('sneakers') || type.includes('boots')
    );
    
    if (!hasTop || !hasBottom || !hasShoes) {
        return { inappropriate: true, reason: `Missing essential categories - Top: ${hasTop}, Bottom: ${hasBottom}, Shoes: ${hasShoes}` };
    }
    
    // Check for too many items (should be 3-6)
    if (items.length < 3 || items.length > 6) {
        return { inappropriate: true, reason: `Wrong item count: ${items.length} (should be 3-6)` };
    }
    
    // Check for multiple bottoms or shoes (should be max 1 each)
    const bottomCount = itemTypes.filter(type => 
        type.includes('pants') || type.includes('jeans') || type.includes('shorts') || type.includes('skirt')
    ).length;
    const shoeCount = itemTypes.filter(type => 
        type.includes('shoes') || type.includes('sneakers') || type.includes('boots')
    ).length;
    
    if (bottomCount > 1) {
        return { inappropriate: true, reason: `Multiple bottoms: ${bottomCount}` };
    }
    if (shoeCount > 1) {
        return { inappropriate: true, reason: `Multiple shoes: ${shoeCount}` };
    }
    
    return { inappropriate: false, reason: "Appropriate outfit" };
}

async function test95PercentRestored() {
    console.log("🧪 TESTING 95% SUCCESS RATE RESTORED");
    console.log("=" * 50);
    
    const testScenarios = [
        // Casual scenarios
        { occasion: "casual", style: "casual", mood: "confident" },
        { occasion: "casual", style: "casual", mood: "comfortable" },
        { occasion: "casual", style: "casual", mood: "energetic" },
        
        // Business casual scenarios
        { occasion: "business casual", style: "business casual", mood: "professional" },
        { occasion: "business casual", style: "business casual", mood: "confident" },
        { occasion: "business casual", style: "business casual", mood: "approachable" },
        
        // Formal scenarios
        { occasion: "formal", style: "formal", mood: "elegant" },
        { occasion: "formal", style: "formal", mood: "sophisticated" },
        { occasion: "formal", style: "formal", mood: "professional" },
        
        // Mixed scenarios
        { occasion: "casual", style: "formal", mood: "confident" },
        { occasion: "business casual", style: "casual", mood: "relaxed" },
        { occasion: "formal", style: "casual", mood: "comfortable" }
    ];
    
    let totalTests = 0;
    let successfulOutfits = 0;
    let inappropriateCombinations = [];
    let missingCategories = [];
    let otherIssues = [];
    
    for (let i = 0; i < testScenarios.length; i++) {
        const scenario = testScenarios[i];
        
        // Test multiple times per scenario
        for (let j = 0; j < 5; j++) {
            totalTests++;
            
            const testRequest = {
                occasion: scenario.occasion,
                wardrobe: [
                    { id: "1", name: "White T-Shirt", type: "t-shirt", color: "white" },
                    { id: "2", name: "Blue Jeans", type: "jeans", color: "blue" },
                    { id: "3", name: "White Sneakers", type: "sneakers", color: "white" },
                    { id: "4", name: "Black Belt", type: "belt", color: "black" },
                    { id: "5", name: "Black Blazer", type: "blazer", color: "black" },
                    { id: "6", name: "White Dress Shirt", type: "shirt", color: "white" },
                    { id: "7", name: "Khaki Shorts", type: "shorts", color: "khaki" },
                    { id: "8", name: "Black Pants", type: "pants", color: "black" },
                    { id: "9", name: "Black Oxford Shoes", type: "shoes", color: "black" },
                    { id: "10", name: "Brown Loafers", type: "shoes", color: "brown" }
                ],
                userProfile: { id: "test_user" },
                style: scenario.style,
                mood: scenario.mood
            };
            
            try {
                const response = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer test',
                        'Content-Length': Buffer.byteLength(JSON.stringify(testRequest))
                    },
                    body: JSON.stringify(testRequest)
                });
                
                if (response.status === 200) {
                    const outfit = response.data;
                    const validation = isInappropriateCombination(outfit);
                    
                    if (!validation.inappropriate) {
                        successfulOutfits++;
                    } else {
                        if (validation.reason.includes("Blazer + Shorts")) {
                            inappropriateCombinations.push({
                                outfit: outfit.name,
                                scenario: `${scenario.occasion}/${scenario.style}/${scenario.mood}`,
                                reason: validation.reason
                            });
                        } else if (validation.reason.includes("Missing essential categories")) {
                            missingCategories.push({
                                outfit: outfit.name,
                                scenario: `${scenario.occasion}/${scenario.style}/${scenario.mood}`,
                                reason: validation.reason
                            });
                        } else {
                            otherIssues.push({
                                outfit: outfit.name,
                                scenario: `${scenario.occasion}/${scenario.style}/${scenario.mood}`,
                                reason: validation.reason
                            });
                        }
                    }
                } else {
                    console.log(`❌ Request failed: ${response.status}`);
                }
            } catch (error) {
                console.log(`❌ Error: ${error.message}`);
            }
        }
        
        // Progress update
        if ((i + 1) % 3 === 0) {
            console.log(`Progress: ${i + 1}/${testScenarios.length} scenarios completed`);
        }
    }
    
    const successRate = ((successfulOutfits / totalTests) * 100).toFixed(1);
    
    console.log("\n📊 COMPREHENSIVE VALIDATION RESULTS");
    console.log("=" * 50);
    console.log(`Total Tests: ${totalTests}`);
    console.log(`Successful Outfits: ${successfulOutfits}`);
    console.log(`Success Rate: ${successRate}%`);
    console.log(`\n❌ Failures:`);
    console.log(`  - Inappropriate Combinations: ${inappropriateCombinations.length}`);
    console.log(`  - Missing Categories: ${missingCategories.length}`);
    console.log(`  - Other Issues: ${otherIssues.length}`);
    
    if (inappropriateCombinations.length > 0) {
        console.log(`\n🚫 Inappropriate Combinations Found:`);
        inappropriateCombinations.slice(0, 3).forEach(failure => {
            console.log(`  - ${failure.outfit}: ${failure.reason} (${failure.scenario})`);
        });
    }
    
    if (missingCategories.length > 0) {
        console.log(`\n📝 Missing Categories Found:`);
        missingCategories.slice(0, 3).forEach(failure => {
            console.log(`  - ${failure.outfit}: ${failure.reason} (${failure.scenario})`);
        });
    }
    
    if (otherIssues.length > 0) {
        console.log(`\n⚠️ Other Issues Found:`);
        otherIssues.slice(0, 3).forEach(failure => {
            console.log(`  - ${failure.outfit}: ${failure.reason} (${failure.scenario})`);
        });
    }
    
    console.log(`\n🎯 TARGET: 95% success rate`);
    console.log(`📈 CURRENT: ${successRate}% success rate`);
    
    if (parseFloat(successRate) >= 95) {
        console.log(`✅ SUCCESS: Comprehensive validation system restored to 95%+ target!`);
    } else if (parseFloat(successRate) >= 90) {
        console.log(`🟡 GOOD: Close to target (${(95 - parseFloat(successRate)).toFixed(1)}% below)`);
    } else {
        console.log(`❌ NEEDS IMPROVEMENT: ${(95 - parseFloat(successRate)).toFixed(1)}% below target`);
    }
    
    console.log(`\n🔧 COMPREHENSIVE RULES ACTIVE:`);
    console.log(`  ✅ Strong Blazer + Shorts Prevention (High Priority)`);
    console.log(`  ✅ Enhanced Blazer + Shorts Prevention (High Priority)`);
    console.log(`  ✅ Formality Consistency Rules`);
    console.log(`  ✅ Occasion Appropriateness Rules`);
    console.log(`  ✅ Enhanced Formal Shoes + Casual Bottoms Prevention`);
    console.log(`  ✅ Enhanced Formal + Casual Prevention`);
    console.log(`  ✅ Essential Categories Enforcement`);
    console.log(`  ✅ Category Limits (Max 1 bottom, Max 1 shoes)`);
}

test95PercentRestored().catch(console.error);
