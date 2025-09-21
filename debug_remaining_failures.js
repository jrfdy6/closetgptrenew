#!/usr/bin/env node
/**
 * DEBUG REMAINING FAILURES
 * Investigate exactly why 20 inappropriate combinations are still getting through
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

function analyzeInappropriateCombination(outfit) {
    const items = outfit.items || [];
    const itemTypes = items.map(item => item.type.toLowerCase());
    const itemNames = items.map(item => item.name.toLowerCase());
    
    const analysis = {
        inappropriate: false,
        issues: [],
        itemBreakdown: {
            tops: [],
            bottoms: [],
            shoes: [],
            accessories: []
        },
        ruleAnalysis: {
            blazerShorts: { hasBlazer: false, hasShorts: false, shouldPrevent: false },
            formalShoesCasualBottoms: { hasFormalShoes: false, hasCasualBottoms: false, shouldPrevent: false },
            formalCasualMismatch: { hasFormalItems: false, hasCasualItems: false, shouldPrevent: false }
        }
    };
    
    // Categorize items
    items.forEach(item => {
        const itemType = item.type.toLowerCase();
        const itemName = item.name.toLowerCase();
        
        if (itemType.includes('shirt') || itemType.includes('blouse') || itemType.includes('sweater') || 
            itemType.includes('jacket') || itemType.includes('blazer') || itemType.includes('t-shirt')) {
            analysis.itemBreakdown.tops.push({ name: item.name, type: item.type });
        } else if (itemType.includes('pants') || itemType.includes('jeans') || itemType.includes('shorts') || 
                   itemType.includes('skirt')) {
            analysis.itemBreakdown.bottoms.push({ name: item.name, type: item.type });
        } else if (itemType.includes('shoes') || itemType.includes('sneakers') || itemType.includes('boots')) {
            analysis.itemBreakdown.shoes.push({ name: item.name, type: item.type });
        } else {
            analysis.itemBreakdown.accessories.push({ name: item.name, type: item.type });
        }
    });
    
    // Rule 1: Blazer + Shorts Analysis
    analysis.ruleAnalysis.blazerShorts.hasBlazer = itemTypes.some(type => type.includes('blazer')) || 
                                                  itemNames.some(name => name.includes('blazer'));
    analysis.ruleAnalysis.blazerShorts.hasShorts = itemTypes.some(type => type.includes('shorts')) || 
                                                   itemNames.some(name => name.includes('shorts'));
    analysis.ruleAnalysis.blazerShorts.shouldPrevent = analysis.ruleAnalysis.blazerShorts.hasBlazer && analysis.ruleAnalysis.blazerShorts.hasShorts;
    
    if (analysis.ruleAnalysis.blazerShorts.shouldPrevent) {
        analysis.inappropriate = true;
        analysis.issues.push("Blazer + Shorts combination");
    }
    
    // Rule 2: Formal Shoes + Casual Bottoms Analysis
    analysis.ruleAnalysis.formalShoesCasualBottoms.hasFormalShoes = itemTypes.some(type => 
        type.includes('oxford') || type.includes('loafers') || type.includes('dress shoes')
    ) || itemNames.some(name => 
        name.includes('oxford') || name.includes('loafers') || name.includes('dress shoes')
    );
    analysis.ruleAnalysis.formalShoesCasualBottoms.hasCasualBottoms = itemTypes.some(type => 
        type.includes('shorts') || type.includes('cargo pants') || type.includes('athletic pants')
    ) || itemNames.some(name => 
        name.includes('shorts') || name.includes('cargo pants') || name.includes('athletic pants')
    );
    analysis.ruleAnalysis.formalShoesCasualBottoms.shouldPrevent = analysis.ruleAnalysis.formalShoesCasualBottoms.hasFormalShoes && analysis.ruleAnalysis.formalShoesCasualBottoms.hasCasualBottoms;
    
    if (analysis.ruleAnalysis.formalShoesCasualBottoms.shouldPrevent) {
        analysis.inappropriate = true;
        analysis.issues.push("Formal shoes + Casual bottoms combination");
    }
    
    // Rule 3: General Formal + Casual Mismatch Analysis
    analysis.ruleAnalysis.formalCasualMismatch.hasFormalItems = itemTypes.some(type => 
        type.includes('blazer') || type.includes('suit') || type.includes('dress shirt') || 
        type.includes('oxford') || type.includes('heels') || type.includes('dress pants')
    ) || itemNames.some(name => 
        name.includes('blazer') || name.includes('suit') || name.includes('dress shirt') || 
        name.includes('oxford') || name.includes('heels') || name.includes('dress pants')
    );
    analysis.ruleAnalysis.formalCasualMismatch.hasCasualItems = itemTypes.some(type => 
        type.includes('shorts') || type.includes('athletic shorts') || type.includes('cargo pants') || 
        type.includes('flip-flops') || type.includes('slides') || type.includes('tank top') || 
        type.includes('hoodie') || type.includes('sneakers')
    ) || itemNames.some(name => 
        name.includes('shorts') || name.includes('athletic shorts') || name.includes('cargo pants') || 
        name.includes('flip-flops') || name.includes('slides') || name.includes('tank top') || 
        name.includes('hoodie') || name.includes('sneakers')
    );
    analysis.ruleAnalysis.formalCasualMismatch.shouldPrevent = analysis.ruleAnalysis.formalCasualMismatch.hasFormalItems && analysis.ruleAnalysis.formalCasualMismatch.hasCasualItems && !analysis.ruleAnalysis.blazerShorts.shouldPrevent;
    
    if (analysis.ruleAnalysis.formalCasualMismatch.shouldPrevent) {
        analysis.inappropriate = true;
        analysis.issues.push("Formal + Casual mismatch (other than blazer+shorts)");
    }
    
    // Check for missing essential categories
    const hasTop = analysis.itemBreakdown.tops.length > 0;
    const hasBottom = analysis.itemBreakdown.bottoms.length > 0;
    const hasShoes = analysis.itemBreakdown.shoes.length > 0;
    
    if (!hasTop || !hasBottom || !hasShoes) {
        analysis.inappropriate = true;
        analysis.issues.push(`Missing essential categories - Top: ${hasTop}, Bottom: ${hasBottom}, Shoes: ${hasShoes}`);
    }
    
    // Check for too many items (should be 3-6)
    if (items.length < 3 || items.length > 6) {
        analysis.inappropriate = true;
        analysis.issues.push(`Wrong item count: ${items.length} (should be 3-6)`);
    }
    
    // Check for multiple bottoms or shoes (should be max 1 each)
    if (analysis.itemBreakdown.bottoms.length > 1) {
        analysis.inappropriate = true;
        analysis.issues.push(`Multiple bottoms: ${analysis.itemBreakdown.bottoms.length}`);
    }
    if (analysis.itemBreakdown.shoes.length > 1) {
        analysis.inappropriate = true;
        analysis.issues.push(`Multiple shoes: ${analysis.itemBreakdown.shoes.length}`);
    }
    
    return analysis;
}

async function debugRemainingFailures() {
    console.log("🔍 DEBUGGING REMAINING FAILURES FOR 99% PREVENTION");
    console.log("=" * 60);
    
    const testScenarios = [
        { occasion: "casual", style: "casual", mood: "confident" },
        { occasion: "casual", style: "casual", mood: "comfortable" },
        { occasion: "casual", style: "casual", mood: "energetic" },
        { occasion: "business casual", style: "business casual", mood: "professional" },
        { occasion: "business casual", style: "business casual", mood: "confident" },
        { occasion: "business casual", style: "business casual", mood: "approachable" },
        { occasion: "formal", style: "formal", mood: "elegant" },
        { occasion: "formal", style: "formal", mood: "sophisticated" },
        { occasion: "formal", style: "formal", mood: "professional" },
        { occasion: "casual", style: "formal", mood: "confident" },
        { occasion: "business casual", style: "casual", mood: "relaxed" },
        { occasion: "formal", style: "casual", mood: "comfortable" }
    ];
    
    const failures = [];
    const failureTypes = {};
    
    for (let i = 0; i < testScenarios.length; i++) {
        const scenario = testScenarios[i];
        
        // Test multiple times per scenario
        for (let j = 0; j < 5; j++) {
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
                    const analysis = analyzeInappropriateCombination(outfit);
                    
                    if (analysis.inappropriate) {
                        const failure = {
                            outfit: outfit.name,
                            scenario: `${scenario.occasion}/${scenario.style}/${scenario.mood}`,
                            issues: analysis.issues,
                            ruleAnalysis: analysis.ruleAnalysis,
                            itemBreakdown: analysis.itemBreakdown,
                            items: outfit.items.map(item => ({ name: item.name, type: item.type }))
                        };
                        failures.push(failure);
                        
                        // Count failure types
                        analysis.issues.forEach(issue => {
                            failureTypes[issue] = (failureTypes[issue] || 0) + 1;
                        });
                    }
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
    
    console.log(`\n📊 DETAILED FAILURE ANALYSIS`);
    console.log("=" * 60);
    console.log(`Total Failures Found: ${failures.length}`);
    console.log(`\n🚫 FAILURE TYPES:`);
    
    Object.entries(failureTypes)
        .sort((a, b) => b[1] - a[1])
        .forEach(([issue, count]) => {
            console.log(`  - ${issue}: ${count} occurrences`);
        });
    
    console.log(`\n🔍 DETAILED RULE ANALYSIS FOR FIRST 5 FAILURES:`);
    failures.slice(0, 5).forEach((failure, index) => {
        console.log(`\n${index + 1}. ${failure.outfit} (${failure.scenario})`);
        console.log(`   Issues: ${failure.issues.join(', ')}`);
        console.log(`   Items:`);
        failure.items.forEach(item => {
            console.log(`     - ${item.name} (${item.type})`);
        });
        
        console.log(`   Rule Analysis:`);
        console.log(`     Blazer + Shorts: Blazer=${failure.ruleAnalysis.blazerShorts.hasBlazer}, Shorts=${failure.ruleAnalysis.blazerShorts.hasShorts}, ShouldPrevent=${failure.ruleAnalysis.blazerShorts.shouldPrevent}`);
        console.log(`     Formal Shoes + Casual Bottoms: FormalShoes=${failure.ruleAnalysis.formalShoesCasualBottoms.hasFormalShoes}, CasualBottoms=${failure.ruleAnalysis.formalShoesCasualBottoms.hasCasualBottoms}, ShouldPrevent=${failure.ruleAnalysis.formalShoesCasualBottoms.shouldPrevent}`);
        console.log(`     Formal + Casual Mismatch: FormalItems=${failure.ruleAnalysis.formalCasualMismatch.hasFormalItems}, CasualItems=${failure.ruleAnalysis.formalCasualMismatch.hasCasualItems}, ShouldPrevent=${failure.ruleAnalysis.formalCasualMismatch.shouldPrevent}`);
        
        console.log(`   Breakdown:`);
        console.log(`     - Tops: ${failure.itemBreakdown.tops.map(t => t.name).join(', ')}`);
        console.log(`     - Bottoms: ${failure.itemBreakdown.bottoms.map(b => b.name).join(', ')}`);
        console.log(`     - Shoes: ${failure.itemBreakdown.shoes.map(s => s.name).join(', ')}`);
        console.log(`     - Accessories: ${failure.itemBreakdown.accessories.map(a => a.name).join(', ')}`);
    });
    
    console.log(`\n🎯 DIAGNOSIS FOR 99% PREVENTION:`);
    
    const blazerShortsCount = failureTypes["Blazer + Shorts combination"] || 0;
    const formalShoesCasualBottomsCount = failureTypes["Formal shoes + Casual bottoms combination"] || 0;
    const formalCasualMismatchCount = failureTypes["Formal + Casual mismatch (other than blazer+shorts)"] || 0;
    
    if (blazerShortsCount > 0) {
        console.log(`❌ CRITICAL: Blazer + Shorts: ${blazerShortsCount} failures still getting through`);
        console.log(`   🔧 The blazer + shorts prevention rule is NOT working properly`);
        console.log(`   🔧 Need to debug why the enhanced validation is not catching these`);
    }
    
    if (formalShoesCasualBottomsCount > 0) {
        console.log(`❌ CRITICAL: Formal Shoes + Casual Bottoms: ${formalShoesCasualBottomsCount} failures still getting through`);
        console.log(`   🔧 The formal shoes + casual bottoms prevention rule is NOT working properly`);
    }
    
    if (formalCasualMismatchCount > 0) {
        console.log(`❌ CRITICAL: Formal + Casual Mismatch: ${formalCasualMismatchCount} failures still getting through`);
        console.log(`   🔧 Need a stronger general formal + casual mismatch prevention rule`);
    }
    
    const totalInappropriateCombinations = blazerShortsCount + formalShoesCasualBottomsCount + formalCasualMismatchCount;
    console.log(`\n📊 SUMMARY FOR 99% TARGET:`);
    console.log(`   Total inappropriate combinations: ${totalInappropriateCombinations}`);
    console.log(`   Current prevention rate: ${((60 - totalInappropriateCombinations) / 60 * 100).toFixed(1)}%`);
    console.log(`   Need to prevent: ${totalInappropriateCombinations} more combinations to reach 99%`);
    
    if (totalInappropriateCombinations <= 1) {
        console.log(`✅ EXCELLENT: Only ${totalInappropriateCombinations} inappropriate combinations remain - very close to 99%!`);
    } else if (totalInappropriateCombinations <= 5) {
        console.log(`🟡 GOOD: ${totalInappropriateCombinations} inappropriate combinations remain - close to 99% target`);
    } else {
        console.log(`❌ NEEDS WORK: ${totalInappropriateCombinations} inappropriate combinations remain - far from 99% target`);
    }
}

debugRemainingFailures().catch(console.error);
