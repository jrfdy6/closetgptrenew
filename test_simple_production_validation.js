#!/usr/bin/env node
/**
 * SIMPLE PRODUCTION VALIDATION TEST
 * Test the enhanced validation with realistic wardrobe data
 */

const https = require('https');

const BACKEND_URL = 'https://closetgptrenew-backend-production.up.railway.app';

async function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const requestOptions = {
            method: options.method || 'GET',
            headers: options.headers || {}
        };
        
        const req = https.request(url, requestOptions, (res) => {
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

function createRealisticWardrobe() {
    return [
        { 
            id: "1", 
            name: "Blue Denim Jeans", 
            type: "jeans", 
            color: "blue",
            brand: "Levi's",
            style: "casual",
            metadata: {
                visualAttributes: {
                    material: "denim",
                    pattern: "solid",
                    fit: "regular fit"
                }
            }
        },
        { 
            id: "2", 
            name: "Black Blazer", 
            type: "blazer", 
            color: "black",
            brand: "Zara",
            style: "business",
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
            brand: "Uniqlo",
            style: "casual",
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
            brand: "Cole Haan",
            style: "formal",
            metadata: {
                visualAttributes: {
                    material: "leather"
                }
            }
        },
        { 
            id: "5", 
            name: "Athletic Shorts", 
            type: "shorts", 
            color: "black",
            brand: "Nike",
            style: "athletic",
            metadata: {
                visualAttributes: {
                    material: "polyester",
                    pattern: "solid"
                }
            }
        },
        { 
            id: "6", 
            name: "White Sneakers", 
            type: "sneakers", 
            color: "white",
            brand: "Adidas",
            style: "casual",
            metadata: {
                visualAttributes: {
                    material: "canvas"
                }
            }
        },
        { 
            id: "7", 
            name: "Navy Dress Shirt", 
            type: "shirt", 
            color: "navy",
            brand: "J.Crew",
            style: "business",
            metadata: {
                visualAttributes: {
                    material: "cotton",
                    sleeveLength: "long sleeve",
                    pattern: "solid"
                }
            }
        },
        { 
            id: "8", 
            name: "Khaki Chinos", 
            type: "pants", 
            color: "khaki",
            brand: "Banana Republic",
            style: "business",
            metadata: {
                visualAttributes: {
                    material: "cotton blend",
                    fit: "slim fit"
                }
            }
        }
    ];
}

async function testEnhancedValidation() {
    console.log("🧪 TESTING ENHANCED VALIDATION IN PRODUCTION");
    console.log("=" * 60);
    
    const testCases = [
        {
            name: "Test 1: Blazer + Shorts (Should be prevented)",
            request: {
                occasion: "casual",
                wardrobe: createRealisticWardrobe(),
                userProfile: { id: "test_user" },
                style: "casual",
                mood: "confident"
            }
        },
        {
            name: "Test 2: Business Formal (Should work)",
            request: {
                occasion: "business",
                wardrobe: createRealisticWardrobe(),
                userProfile: { id: "test_user" },
                style: "business",
                mood: "professional"
            }
        },
        {
            name: "Test 3: Athletic Casual (Should work)",
            request: {
                occasion: "athletic",
                wardrobe: createRealisticWardrobe(),
                userProfile: { id: "test_user" },
                style: "athletic",
                mood: "energetic"
            }
        }
    ];
    
    let totalTests = 0;
    let passedTests = 0;
    
    for (let i = 0; i < testCases.length; i++) {
        const testCase = testCases[i];
        console.log(`\n🧪 ${testCase.name}`);
        
        try {
            const response = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer test'
                },
                body: JSON.stringify(testCase.request)
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
                        item.type.toLowerCase().includes('t-shirt') ||
                        item.name.toLowerCase().includes('shirt') ||
                        item.name.toLowerCase().includes('blazer') ||
                        item.name.toLowerCase().includes('t-shirt')
                    ).length,
                    "bottoms": outfit.items.filter(item => 
                        item.type.toLowerCase().includes('pants') || 
                        item.type.toLowerCase().includes('shorts') ||
                        item.type.toLowerCase().includes('jeans') ||
                        item.type.toLowerCase().includes('chinos') ||
                        item.name.toLowerCase().includes('pants') ||
                        item.name.toLowerCase().includes('shorts') ||
                        item.name.toLowerCase().includes('jeans') ||
                        item.name.toLowerCase().includes('chinos')
                    ).length,
                    "shoes": outfit.items.filter(item => 
                        item.type.toLowerCase().includes('shoes') || 
                        item.type.toLowerCase().includes('sneakers') ||
                        item.type.toLowerCase().includes('oxford') ||
                        item.name.toLowerCase().includes('shoes') ||
                        item.name.toLowerCase().includes('sneakers') ||
                        item.name.toLowerCase().includes('oxford')
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
                console.log(`   Response: ${JSON.stringify(response.data).substring(0, 200)}...`);
            }
            
        } catch (error) {
            console.log(`   ❌ EXCEPTION: ${error.message}`);
        }
        
        // Small delay between tests
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Final Results
    console.log("\n🏆 ENHANCED VALIDATION TEST RESULTS");
    console.log("=" * 60);
    
    console.log(`📊 Total Tests: ${totalTests}`);
    console.log(`✅ Passed: ${passedTests}`);
    console.log(`❌ Failed: ${totalTests - passedTests}`);
    console.log(`📈 Success Rate: ${totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0}%`);
    
    if (passedTests === totalTests && totalTests > 0) {
        console.log("\n🎉 ALL TESTS PASSED!");
        console.log("✅ Enhanced validation is working correctly in production");
        console.log("✅ Inappropriate combinations are being prevented");
        console.log("✅ Category rules are being enforced");
        console.log("✅ Essential categories are preserved");
    } else {
        console.log("\n⚠️ SOME TESTS FAILED");
        console.log("❌ Enhanced validation may need further refinement");
    }
    
    console.log("\n🏁 Enhanced validation test completed!");
}

testEnhancedValidation().catch(console.error);
