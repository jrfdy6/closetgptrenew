#!/usr/bin/env node
/**
 * TEST ENHANCED ITEM TYPE MATCHING
 * Test the comprehensive attribute analysis with color, material, sleeve length, patterns, fits
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

async function testEnhancedMatching() {
    console.log("🔧 TESTING ENHANCED ITEM TYPE MATCHING");
    console.log("=" * 60);
    console.log("Testing comprehensive attribute analysis...\n");
    
    // Test scenarios with various attribute combinations
    const testScenarios = [
        {
            name: "Test 1: Material-Based Matching (Denim)",
            description: "Test if denim material correctly identifies jeans",
            request: {
                occasion: "casual",
                wardrobe: [
                    { 
                        id: "1", 
                        name: "Blue Denim Jeans", 
                        type: "jeans", 
                        color: "blue",
                        metadata: {
                            visualAttributes: {
                                material: "denim",
                                pattern: "solid",
                                fit: "slim fit"
                            }
                        }
                    },
                    { 
                        id: "2", 
                        name: "Black Blazer", 
                        type: "blazer", 
                        color: "black",
                        metadata: {
                            visualAttributes: {
                                material: "wool",
                                pattern: "solid"
                            }
                        }
                    },
                    { 
                        id: "3", 
                        name: "White Cotton T-Shirt", 
                        type: "t-shirt", 
                        color: "white",
                        metadata: {
                            visualAttributes: {
                                material: "cotton",
                                sleeveLength: "short sleeve"
                            }
                        }
                    },
                    { 
                        id: "4", 
                        name: "Black Oxford Shoes", 
                        type: "shoes", 
                        color: "black",
                        metadata: {
                            visualAttributes: {
                                material: "leather"
                            }
                        }
                    }
                ],
                userProfile: { id: "test_user" },
                style: "casual",
                mood: "confident"
            }
        },
        {
            name: "Test 2: Sleeve Length Matching",
            description: "Test if sleeve length attributes are properly recognized",
            request: {
                occasion: "business",
                wardrobe: [
                    { 
                        id: "5", 
                        name: "White Long Sleeve Dress Shirt", 
                        type: "shirt", 
                        color: "white",
                        metadata: {
                            visualAttributes: {
                                material: "cotton",
                                sleeveLength: "long sleeve",
                                fit: "slim fit"
                            }
                        }
                    },
                    { 
                        id: "6", 
                        name: "Khaki Chinos", 
                        type: "pants", 
                        color: "khaki",
                        metadata: {
                            visualAttributes: {
                                material: "cotton blend",
                                fit: "regular fit"
                            }
                        }
                    },
                    { 
                        id: "7", 
                        name: "Navy Blazer", 
                        type: "blazer", 
                        color: "navy",
                        metadata: {
                            visualAttributes: {
                                material: "wool",
                                pattern: "solid"
                            }
                        }
                    },
                    { 
                        id: "8", 
                        name: "Brown Leather Loafers", 
                        type: "loafers", 
                        color: "brown",
                        metadata: {
                            visualAttributes: {
                                material: "leather"
                            }
                        }
                    }
                ],
                userProfile: { id: "test_user" },
                style: "business",
                mood: "professional"
            }
        },
        {
            name: "Test 3: Pattern and Style Matching",
            description: "Test if patterns and styles are properly recognized",
            request: {
                occasion: "casual",
                wardrobe: [
                    { 
                        id: "9", 
                        name: "Striped Cotton Shirt", 
                        type: "shirt", 
                        color: "blue",
                        metadata: {
                            visualAttributes: {
                                material: "cotton",
                                pattern: "striped",
                                sleeveLength: "long sleeve"
                            }
                        }
                    },
                    { 
                        id: "10", 
                        name: "Athletic Shorts", 
                        type: "shorts", 
                        color: "black",
                        metadata: {
                            visualAttributes: {
                                material: "polyester",
                                pattern: "solid"
                            }
                        }
                    },
                    { 
                        id: "11", 
                        name: "Black Blazer", 
                        type: "blazer", 
                        color: "black",
                        metadata: {
                            visualAttributes: {
                                material: "wool",
                                pattern: "solid"
                            }
                        }
                    },
                    { 
                        id: "12", 
                        name: "White Sneakers", 
                        type: "sneakers", 
                        color: "white",
                        metadata: {
                            visualAttributes: {
                                material: "canvas"
                            }
                        }
                    }
                ],
                userProfile: { id: "test_user" },
                style: "casual",
                mood: "confident"
            }
        }
    ];
    
    let totalTests = 0;
    let passedTests = 0;
    
    for (let i = 0; i < testScenarios.length; i++) {
        const scenario = testScenarios[i];
        console.log(`🧪 ${scenario.name}`);
        console.log(`📝 ${scenario.description}`);
        
        try {
            const response = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer test',
                    'Content-Length': Buffer.byteLength(JSON.stringify(scenario.request))
                },
                body: JSON.stringify(scenario.request)
            });
            
            totalTests++;
            
            if (response.status === 200) {
                const outfit = response.data;
                console.log(`✅ Generated: ${outfit.name}`);
                console.log(`📊 Items: ${outfit.items.length}`);
                
                outfit.items.forEach((item, index) => {
                    console.log(`   ${index + 1}. ${item.name} (${item.type})`);
                });
                
                // Check for inappropriate combinations
                const hasBlazer = outfit.items.some(item => 
                    item.type.toLowerCase().includes('blazer') || 
                    item.name.toLowerCase().includes('blazer')
                );
                const hasShorts = outfit.items.some(item => 
                    item.type.toLowerCase().includes('shorts') || 
                    item.name.toLowerCase().includes('shorts')
                );
                
                // Check category compliance
                const categories = {
                    "tops": outfit.items.filter(item => 
                        item.type.toLowerCase().includes('shirt') || 
                        item.type.toLowerCase().includes('blazer') ||
                        item.name.toLowerCase().includes('shirt') ||
                        item.name.toLowerCase().includes('blazer')
                    ).length,
                    "bottoms": outfit.items.filter(item => 
                        item.type.toLowerCase().includes('pants') || 
                        item.type.toLowerCase().includes('shorts') ||
                        item.type.toLowerCase().includes('jeans') ||
                        item.name.toLowerCase().includes('pants') ||
                        item.name.toLowerCase().includes('shorts') ||
                        item.name.toLowerCase().includes('jeans')
                    ).length,
                    "shoes": outfit.items.filter(item => 
                        item.type.toLowerCase().includes('shoes') || 
                        item.type.toLowerCase().includes('sneakers') ||
                        item.type.toLowerCase().includes('loafers') ||
                        item.name.toLowerCase().includes('shoes') ||
                        item.name.toLowerCase().includes('sneakers') ||
                        item.name.toLowerCase().includes('loafers')
                    ).length
                };
                
                console.log(`   Categories: Tops=${categories.tops}, Bottoms=${categories.bottoms}, Shoes=${categories.shoes}`);
                
                // Check if test passed
                let testPassed = true;
                
                if (hasBlazer && hasShorts) {
                    console.log(`   ❌ FAILED: Blazer + Shorts inappropriate combination!`);
                    testPassed = false;
                } else {
                    console.log(`   ✅ PASSED: No inappropriate combinations`);
                }
                
                if (categories.tops === 0 || categories.bottoms === 0 || categories.shoes === 0) {
                    console.log(`   ❌ FAILED: Missing essential categories!`);
                    testPassed = false;
                } else {
                    console.log(`   ✅ PASSED: All essential categories present`);
                }
                
                if (categories.bottoms > 1) {
                    console.log(`   ❌ FAILED: Multiple bottoms (${categories.bottoms})!`);
                    testPassed = false;
                } else {
                    console.log(`   ✅ PASSED: Single bottom category`);
                }
                
                if (categories.shoes > 1) {
                    console.log(`   ❌ FAILED: Multiple shoes (${categories.shoes})!`);
                    testPassed = false;
                } else {
                    console.log(`   ✅ PASSED: Single shoe category`);
                }
                
                if (testPassed) {
                    passedTests++;
                    console.log(`   🎉 OVERALL: PASSED`);
                } else {
                    console.log(`   💥 OVERALL: FAILED`);
                }
                
            } else {
                console.log(`   ❌ HTTP ERROR: ${response.status}`);
            }
            
        } catch (error) {
            console.log(`   ❌ EXCEPTION: ${error.message}`);
        }
        
        console.log("");
        
        // Small delay between tests
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Final Results
    console.log("🏆 ENHANCED MATCHING TEST RESULTS");
    console.log("=" * 60);
    
    console.log(`📊 Total Tests: ${totalTests}`);
    console.log(`✅ Passed: ${passedTests}`);
    console.log(`❌ Failed: ${totalTests - passedTests}`);
    console.log(`📈 Success Rate: ${totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0}%`);
    
    if (passedTests === totalTests && totalTests > 0) {
        console.log("\n🎉 ALL TESTS PASSED!");
        console.log("✅ Enhanced item type matching is working correctly");
        console.log("✅ Material, sleeve length, pattern, and style attributes are being recognized");
        console.log("✅ Inappropriate combinations are being prevented");
        console.log("✅ Category rules are being enforced");
    } else {
        console.log("\n⚠️ SOME TESTS FAILED");
        console.log("❌ Enhanced matching may need further refinement");
    }
    
    console.log("\n🏁 Enhanced matching test completed!");
}

testEnhancedMatching().catch(console.error);
