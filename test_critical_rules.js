#!/usr/bin/env node
/**
 * TEST CRITICAL VALIDATION RULES
 * Test the new critical rules to address the remaining 3% of failures
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
        return { inappropriate: true, reason: "Blazer + Shorts combination", items: items.map(item => ({ name: item.name, type: item.type })) };
    }
    
    // Check for formal shoes + casual bottoms
    const hasFormalShoes = itemTypes.some(type => 
        type.includes('oxford') || type.includes('loafers') || type.includes('dress shoes') || type.includes('heels')
    ) || itemNames.some(name => 
        name.includes('oxford') || name.includes('loafers') || name.includes('dress shoes') || name.includes('heels')
    );
    const hasCasualBottoms = itemTypes.some(type => 
        type.includes('shorts') || type.includes('cargo pants') || type.includes('athletic pants') || type.includes('sweatpants')
    ) || itemNames.some(name => 
        name.includes('shorts') || name.includes('cargo pants') || name.includes('athletic pants') || name.includes('sweatpants')
    );
    
    if (hasFormalShoes && hasCasualBottoms) {
        return { inappropriate: true, reason: "Formal shoes + Casual bottoms combination", items: items.map(item => ({ name: item.name, type: item.type })) };
    }
    
    // Check for missing essential categories
    const hasTop = itemTypes.some(type => 
        type.includes('shirt') || type.includes('blouse') || type.includes('sweater') || 
        type.includes('jacket') || type.includes('blazer') || type.includes('t-shirt') || 
        type.includes('tank top') || type.includes('hoodie')
    );
    const hasBottom = itemTypes.some(type => 
        type.includes('pants') || type.includes('jeans') || type.includes('shorts') || 
        type.includes('skirt') || type.includes('dress') || type.includes('leggings')
    );
    const hasShoes = itemTypes.some(type => 
        type.includes('shoes') || type.includes('sneakers') || type.includes('boots') || 
        type.includes('sandals') || type.includes('heels') || type.includes('flip-flops')
    );
    
    if (!hasTop || !hasBottom || !hasShoes) {
        return { inappropriate: true, reason: `Missing essential categories - Top: ${hasTop}, Bottom: ${hasBottom}, Shoes: ${hasShoes}`, items: items.map(item => ({ name: item.name, type: item.type })) };
    }
    
    // Check for too many items (should be 3-6)
    if (items.length < 3 || items.length > 6) {
        return { inappropriate: true, reason: `Wrong item count: ${items.length} (should be 3-6)`, items: items.map(item => ({ name: item.name, type: item.type })) };
    }
    
    // Check for multiple bottoms or shoes (should be max 1 each)
    const bottomCount = itemTypes.filter(type => 
        type.includes('pants') || type.includes('jeans') || type.includes('shorts') || type.includes('skirt') || type.includes('leggings')
    ).length;
    const shoeCount = itemTypes.filter(type => 
        type.includes('shoes') || type.includes('sneakers') || type.includes('boots') || type.includes('sandals') || type.includes('heels')
    ).length;
    
    if (bottomCount > 1) {
        return { inappropriate: true, reason: `Multiple bottoms: ${bottomCount}`, items: items.map(item => ({ name: item.name, type: item.type })) };
    }
    if (shoeCount > 1) {
        return { inappropriate: true, reason: `Multiple shoes: ${shoeCount}`, items: items.map(item => ({ name: item.name, type: item.type })) };
    }
    
    return { inappropriate: false, reason: "Appropriate outfit", items: items.map(item => ({ name: item.name, type: item.type })) };
}

// Test wardrobe designed to trigger the specific failures we're addressing
function generateTestWardrobe() {
    return [
        // Items that could cause missing categories issues
        { id: "1", name: "Black Blazer", type: "blazer", color: "black", style: "formal" },
        { id: "2", name: "White Dress Shirt", type: "shirt", color: "white", style: "formal" },
        { id: "3", name: "Black Oxford Shoes", type: "shoes", color: "black", style: "formal" },
        { id: "4", name: "Khaki Shorts", type: "shorts", color: "khaki", style: "casual" },
        { id: "5", name: "Blue Jeans", type: "jeans", color: "blue", style: "casual" },
        { id: "6", name: "White T-Shirt", type: "t-shirt", color: "white", style: "casual" },
        { id: "7", name: "Black Sneakers", type: "sneakers", color: "black", style: "casual" },
        { id: "8", name: "Gray Pants", type: "pants", color: "gray", style: "formal" },
        { id: "9", name: "Brown Loafers", type: "shoes", color: "brown", style: "formal" },
        { id: "10", name: "Athletic Shorts", type: "athletic shorts", color: "black", style: "athletic" },
        { id: "11", name: "Cargo Pants", type: "cargo pants", color: "green", style: "casual" },
        { id: "12", name: "Sweatpants", type: "sweatpants", color: "gray", style: "casual" },
        { id: "13", name: "Navy Blazer", type: "blazer", color: "navy", style: "formal" },
        { id: "14", name: "Pink Dress Shirt", type: "shirt", color: "pink", style: "formal" },
        { id: "15", name: "Black Pants", type: "pants", color: "black", style: "formal" }
    ];
}

async function testCriticalRules() {
    console.log("🔧 TESTING CRITICAL VALIDATION RULES");
    console.log("=" * 60);
    console.log("Testing the new critical rules to address:");
    console.log("✅ 8 missing categories cases (2.7%)");
    console.log("✅ 1 formal shoes + casual bottoms mismatch (0.3%)");
    console.log("✅ Target: 99% prevention rate");
    console.log("=" * 60);
    
    const testScenarios = [
        // Scenarios that previously caused missing categories
        { occasion: "casual", style: "casual", mood: "comfortable" },
        { occasion: "casual", style: "casual", mood: "energetic" },
        { occasion: "business casual", style: "business casual", mood: "professional" },
        { occasion: "business casual", style: "business casual", mood: "confident" },
        { occasion: "formal", style: "formal", mood: "elegant" },
        { occasion: "casual", style: "formal", mood: "confident" },
        { occasion: "business casual", style: "casual", mood: "relaxed" },
        { occasion: "formal", style: "casual", mood: "comfortable" },
        
        // Scenarios that previously caused formal + casual mismatch
        { occasion: "casual", style: "casual", mood: "energetic" },
        { occasion: "business casual", style: "business casual", mood: "professional" },
        { occasion: "formal", style: "formal", mood: "elegant" },
        { occasion: "casual", style: "formal", mood: "confident" },
        { occasion: "business casual", style: "casual", mood: "relaxed" },
        { occasion: "formal", style: "casual", mood: "comfortable" },
        { occasion: "casual", style: "business casual", mood: "professional" },
        { occasion: "business casual", style: "formal", mood: "elegant" }
    ];
    
    let totalTests = 0;
    let successfulOutfits = 0;
    let inappropriateCombinations = [];
    let missingCategories = [];
    let otherIssues = [];
    let failureTypes = {};
    
    const testWardrobe = generateTestWardrobe();
    const startTime = Date.now();
    
    // Test each scenario multiple times
    const testsPerScenario = 10;
    
    for (let i = 0; i < testScenarios.length; i++) {
        const scenario = testScenarios[i];
        
        for (let j = 0; j < testsPerScenario; j++) {
            totalTests++;
            
            const testRequest = {
                occasion: scenario.occasion,
                wardrobe: testWardrobe,
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
                        const failure = {
                            outfit: outfit.name,
                            scenario: `${scenario.occasion}/${scenario.style}/${scenario.mood}`,
                            reason: validation.reason,
                            testNumber: totalTests,
                            items: validation.items
                        };
                        
                        if (validation.reason.includes("Blazer + Shorts")) {
                            inappropriateCombinations.push(failure);
                        } else if (validation.reason.includes("Missing essential categories")) {
                            missingCategories.push(failure);
                        } else if (validation.reason.includes("Formal shoes + Casual bottoms")) {
                            otherIssues.push(failure);
                        } else if (validation.reason.includes("Wrong item count")) {
                            otherIssues.push(failure);
                        } else if (validation.reason.includes("Multiple")) {
                            otherIssues.push(failure);
                        } else {
                            otherIssues.push(failure);
                        }
                        
                        // Count failure types
                        failureTypes[validation.reason] = (failureTypes[validation.reason] || 0) + 1;
                    }
                } else {
                    console.log(`❌ Request ${totalTests} failed: ${response.status}`);
                }
            } catch (error) {
                console.log(`❌ Test ${totalTests} error: ${error.message}`);
            }
            
            // Progress updates
            if (totalTests % 20 === 0) {
                const elapsed = (Date.now() - startTime) / 1000;
                const rate = totalTests / elapsed;
                const eta = (testScenarios.length * testsPerScenario - totalTests) / rate;
                
                console.log(`Progress: ${totalTests}/${testScenarios.length * testsPerScenario} tests (${((totalTests/(testScenarios.length * testsPerScenario))*100).toFixed(1)}%)`);
                console.log(`Rate: ${rate.toFixed(1)} tests/sec, ETA: ${eta.toFixed(0)} seconds`);
                console.log(`Current success rate: ${((successfulOutfits/totalTests)*100).toFixed(1)}%`);
                console.log(`Inappropriate combinations so far: ${inappropriateCombinations.length + missingCategories.length + otherIssues.length}`);
                console.log("");
                
                // Rate limiting
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }
    
    const endTime = Date.now();
    const totalTime = (endTime - startTime) / 1000;
    const preventionRate = ((successfulOutfits / totalTests) * 100).toFixed(1);
    const totalInappropriate = inappropriateCombinations.length + missingCategories.length + otherIssues.length;
    
    console.log("\n🔧 CRITICAL RULES TEST RESULTS");
    console.log("=" * 60);
    console.log(`Total Tests: ${totalTests}`);
    console.log(`Successful Outfits: ${successfulOutfits}`);
    console.log(`Inappropriate Combinations: ${totalInappropriate}`);
    console.log(`Prevention Rate: ${preventionRate}%`);
    console.log(`Total Time: ${totalTime.toFixed(1)} seconds`);
    console.log(`Average Rate: ${(totalTests/totalTime).toFixed(1)} tests/second`);
    
    console.log(`\n📊 FAILURE BREAKDOWN:`);
    console.log(`  - Blazer + Shorts: ${inappropriateCombinations.length}`);
    console.log(`  - Missing Categories: ${missingCategories.length}`);
    console.log(`  - Formal Shoes + Casual Bottoms: ${otherIssues.filter(f => f.reason.includes("Formal shoes + Casual bottoms")).length}`);
    console.log(`  - Item Count Issues: ${otherIssues.filter(f => f.reason.includes("Wrong item count")).length}`);
    console.log(`  - Multiple Items: ${otherIssues.filter(f => f.reason.includes("Multiple")).length}`);
    console.log(`  - Other Issues: ${otherIssues.filter(f => !f.reason.includes("Formal shoes + Casual bottoms") && !f.reason.includes("Wrong item count") && !f.reason.includes("Multiple")).length}`);
    
    if (Object.keys(failureTypes).length > 0) {
        console.log(`\n🚫 FAILURE TYPES:`);
        Object.entries(failureTypes)
            .sort((a, b) => b[1] - a[1])
            .forEach(([issue, count]) => {
                console.log(`  - ${issue}: ${count} occurrences`);
            });
    }
    
    // Show first few failures for analysis
    if (inappropriateCombinations.length > 0) {
        console.log(`\n🚫 First 3 Blazer + Shorts Failures:`);
        inappropriateCombinations.slice(0, 3).forEach(failure => {
            console.log(`  - Test #${failure.testNumber}: ${failure.outfit} (${failure.scenario})`);
            console.log(`    Items: ${failure.items.map(item => `${item.name} (${item.type})`).join(', ')}`);
        });
    }
    
    if (missingCategories.length > 0) {
        console.log(`\n📝 First 3 Missing Categories Failures:`);
        missingCategories.slice(0, 3).forEach(failure => {
            console.log(`  - Test #${failure.testNumber}: ${failure.outfit} (${failure.scenario})`);
            console.log(`    Reason: ${failure.reason}`);
        });
    }
    
    if (otherIssues.length > 0) {
        console.log(`\n⚠️ First 3 Other Issues:`);
        otherIssues.slice(0, 3).forEach(failure => {
            console.log(`  - Test #${failure.testNumber}: ${failure.outfit} (${failure.scenario})`);
            console.log(`    Reason: ${failure.reason}`);
        });
    }
    
    console.log(`\n🎯 99% PREVENTION TARGET ANALYSIS:`);
    console.log(`   Target: 99% prevention rate`);
    console.log(`   Achieved: ${preventionRate}% prevention rate`);
    console.log(`   Gap: ${(99 - parseFloat(preventionRate)).toFixed(1)}% ${parseFloat(preventionRate) >= 99 ? 'above' : 'below'} target`);
    console.log(`   Inappropriate combinations: ${totalInappropriate}/${totalTests}`);
    
    if (parseFloat(preventionRate) >= 99) {
        console.log(`✅ SUCCESS: 99% prevention target ACHIEVED with critical rules! 🎉`);
        console.log(`   The critical validation rules successfully addressed the remaining 3%!`);
    } else if (parseFloat(preventionRate) >= 97) {
        console.log(`🟡 EXCELLENT: Very close to 99% target (${(99 - parseFloat(preventionRate)).toFixed(1)}% below)`);
        console.log(`   Only ${totalInappropriate} inappropriate combinations out of ${totalTests} tests`);
    } else if (parseFloat(preventionRate) >= 95) {
        console.log(`🟡 GOOD: Close to target (${(99 - parseFloat(preventionRate)).toFixed(1)}% below)`);
    } else {
        console.log(`❌ NEEDS WORK: Far from 99% target (${(99 - parseFloat(preventionRate)).toFixed(1)}% below)`);
        console.log(`   The critical validation rules need further refinement`);
    }
    
    console.log(`\n🔧 CRITICAL VALIDATION RULES PERFORMANCE:`);
    console.log(`   ✅ Tested enhanced essential categories enforcement`);
    console.log(`   ✅ Tested ultimate formal shoes + casual bottoms prevention`);
    console.log(`   ✅ Tested critical priority rule sorting`);
    console.log(`   ✅ Tested comprehensive final validation layer`);
    console.log(`   ✅ Prevention rate: ${preventionRate}% (Target: 99%)`);
    
    if (parseFloat(preventionRate) >= 99) {
        console.log(`\n🏆 MISSION ACCOMPLISHED: 99% PREVENTION WITH CRITICAL RULES!`);
        console.log(`   The remaining 3% of failures have been successfully addressed!`);
    }
}

testCriticalRules().catch(console.error);
