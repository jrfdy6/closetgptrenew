#!/usr/bin/env node
/**
 * DEBUG SINGLE OUTFIT
 * Test a single outfit generation to debug the validation
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

async function debugSingleOutfit() {
    console.log("🔍 DEBUGGING SINGLE OUTFIT GENERATION");
    console.log("=" * 50);
    
    const testRequest = {
        occasion: "casual",
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
        style: "casual",
        mood: "confident"
    };
    
    try {
        console.log("🧪 Testing outfit generation...");
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
            console.log(`✅ Outfit generated: ${outfit.name}`);
            console.log(`📊 Items: ${outfit.items.length}`);
            
            console.log("\n👕 Outfit Items:");
            outfit.items.forEach((item, index) => {
                console.log(`  ${index + 1}. ${item.name} (${item.type}) - ${item.color}`);
            });
            
            // Check for blazer + shorts combination
            const hasBlazer = outfit.items.some(item => 
                item.type.toLowerCase().includes('blazer') || 
                item.name.toLowerCase().includes('blazer')
            );
            const hasShorts = outfit.items.some(item => 
                item.type.toLowerCase().includes('shorts') || 
                item.name.toLowerCase().includes('shorts')
            );
            
            console.log(`\n🔍 Analysis:`);
            console.log(`  - Has Blazer: ${hasBlazer ? '✅' : '❌'}`);
            console.log(`  - Has Shorts: ${hasShorts ? '✅' : '❌'}`);
            
            if (hasBlazer && hasShorts) {
                console.log(`  ❌ PROBLEM: Blazer + Shorts inappropriate combination!`);
            } else {
                console.log(`  ✅ No inappropriate combination`);
            }
            
            // Check essential categories
            const hasTop = outfit.items.some(item => 
                item.type.toLowerCase().includes('shirt') || 
                item.type.toLowerCase().includes('blazer')
            );
            const hasBottom = outfit.items.some(item => 
                item.type.toLowerCase().includes('pants') || 
                item.type.toLowerCase().includes('jeans') ||
                item.type.toLowerCase().includes('shorts')
            );
            const hasShoes = outfit.items.some(item => 
                item.type.toLowerCase().includes('shoes') || 
                item.type.toLowerCase().includes('sneakers')
            );
            
            console.log(`  - Has Top: ${hasTop ? '✅' : '❌'}`);
            console.log(`  - Has Bottom: ${hasBottom ? '✅' : '❌'}`);
            console.log(`  - Has Shoes: ${hasShoes ? '✅' : '❌'}`);
            
            // Check item count
            console.log(`  - Item Count: ${outfit.items.length} (should be 3-6)`);
            
            // Check for multiple bottoms/shoes
            const bottomCount = outfit.items.filter(item => 
                item.type.toLowerCase().includes('pants') || 
                item.type.toLowerCase().includes('jeans') ||
                item.type.toLowerCase().includes('shorts')
            ).length;
            const shoeCount = outfit.items.filter(item => 
                item.type.toLowerCase().includes('shoes') || 
                item.type.toLowerCase().includes('sneakers')
            ).length;
            
            console.log(`  - Bottom Count: ${bottomCount} (should be 1)`);
            console.log(`  - Shoe Count: ${shoeCount} (should be 1)`);
            
        } else {
            console.log(`❌ Request failed: ${response.status}`);
            console.log("Response:", JSON.stringify(response.data, null, 2));
        }
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }
}

debugSingleOutfit().catch(console.error);
