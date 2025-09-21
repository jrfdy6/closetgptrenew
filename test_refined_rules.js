#!/usr/bin/env node
/**
 * TEST REFINED ENHANCED VALIDATION RULES
 * Quick test to verify the refined rules are working
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

async function testRefinedRules() {
    console.log("🔧 TESTING REFINED ENHANCED VALIDATION RULES");
    console.log("=" * 60);
    
    // Test 1: Blazer + Shorts Prevention (should be blocked)
    console.log("\n🧪 TEST 1: Blazer + Shorts Prevention");
    const blazerShortsTest = {
        occasion: "casual",
        wardrobe: [
            { id: "1", name: "Black Blazer", type: "blazer", color: "black" },
            { id: "2", name: "White Shirt", type: "shirt", color: "white" },
            { id: "3", name: "Khaki Shorts", type: "shorts", color: "khaki" },
            { id: "4", name: "Black Pants", type: "pants", color: "black" },
            { id: "5", name: "Black Oxford Shoes", type: "shoes", color: "black" },
            { id: "6", name: "White Sneakers", type: "sneakers", color: "white" }
        ],
        userProfile: { id: "test_user" },
        style: "casual",
        mood: "confident"
    };
    
    try {
        const response1 = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test',
                'Content-Length': Buffer.byteLength(JSON.stringify(blazerShortsTest))
            },
            body: JSON.stringify(blazerShortsTest)
        });
        
        if (response1.status === 200) {
            const outfit1 = response1.data;
            console.log(`✅ Generated: ${outfit1.name}`);
            console.log(`📊 Items: ${outfit1.items.length}`);
            
            const hasBlazer = outfit1.items.some(item => 
                item.type.toLowerCase().includes('blazer') || 
                item.name.toLowerCase().includes('blazer')
            );
            const hasShorts = outfit1.items.some(item => 
                item.type.toLowerCase().includes('shorts') || 
                item.name.toLowerCase().includes('shorts')
            );
            
            console.log(`   Blazer: ${hasBlazer ? '✅' : '❌'}`);
            console.log(`   Shorts: ${hasShorts ? '✅' : '❌'}`);
            
            if (hasBlazer && hasShorts) {
                console.log(`❌ FAILED: Blazer + Shorts inappropriate combination present!`);
            } else {
                console.log(`✅ PASSED: Blazer + Shorts combination prevented!`);
            }
        }
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }
    
    // Test 2: Essential Categories Enforcement
    console.log("\n🧪 TEST 2: Essential Categories Enforcement");
    const essentialTest = {
        occasion: "casual",
        wardrobe: [
            { id: "7", name: "White T-Shirt", type: "t-shirt", color: "white" },
            { id: "8", name: "Blue Jeans", type: "jeans", color: "blue" },
            { id: "9", name: "White Sneakers", type: "sneakers", color: "white" }
        ],
        userProfile: { id: "test_user" },
        style: "casual",
        mood: "confident"
    };
    
    try {
        const response2 = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test',
                'Content-Length': Buffer.byteLength(JSON.stringify(essentialTest))
            },
            body: JSON.stringify(essentialTest)
        });
        
        if (response2.status === 200) {
            const outfit2 = response2.data;
            console.log(`✅ Generated: ${outfit2.name}`);
            console.log(`📊 Items: ${outfit2.items.length}`);
            
            const categories = {
                "tops": outfit2.items.filter(item => 
                    item.type.toLowerCase().includes('shirt') || 
                    item.type.toLowerCase().includes('t-shirt') ||
                    item.name.toLowerCase().includes('shirt')
                ).length,
                "bottoms": outfit2.items.filter(item => 
                    item.type.toLowerCase().includes('pants') || 
                    item.type.toLowerCase().includes('jeans') ||
                    item.name.toLowerCase().includes('pants') ||
                    item.name.toLowerCase().includes('jeans')
                ).length,
                "shoes": outfit2.items.filter(item => 
                    item.type.toLowerCase().includes('shoes') || 
                    item.type.toLowerCase().includes('sneakers') ||
                    item.name.toLowerCase().includes('shoes') ||
                    item.name.toLowerCase().includes('sneakers')
                ).length
            };
            
            console.log(`   Tops: ${categories.tops}`);
            console.log(`   Bottoms: ${categories.bottoms}`);
            console.log(`   Shoes: ${categories.shoes}`);
            
            if (categories.tops > 0 && categories.bottoms > 0 && categories.shoes > 0) {
                console.log(`✅ PASSED: All essential categories present!`);
            } else {
                console.log(`❌ FAILED: Missing essential categories!`);
            }
        }
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }
    
    console.log("\n🏁 Refined rules test completed!");
}

testRefinedRules().catch(console.error);
