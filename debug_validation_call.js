#!/usr/bin/env node
/**
 * DEBUG VALIDATION CALL
 * Check if the enhanced validation is actually being called and working
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

async function debugValidationCall() {
    console.log("🔍 DEBUGGING VALIDATION CALL");
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
        console.log("🧪 Testing outfit generation with validation debug...");
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
                console.log(`  ❌ VALIDATION FAILED: Blazer + Shorts inappropriate combination!`);
                console.log(`  🔍 This means the enhanced validation is NOT working properly`);
                
                // Test the specific items that should be caught
                const blazerItem = outfit.items.find(item => 
                    item.type.toLowerCase().includes('blazer') || 
                    item.name.toLowerCase().includes('blazer')
                );
                const shortsItem = outfit.items.find(item => 
                    item.type.toLowerCase().includes('shorts') || 
                    item.name.toLowerCase().includes('shorts')
                );
                
                console.log(`\n🧪 Testing rule matching:`);
                if (blazerItem) {
                    console.log(`  Blazer: "${blazerItem.name}" (type: "${blazerItem.type}")`);
                    console.log(`  - "blazer" in type: ${blazerItem.type.toLowerCase().includes('blazer')}`);
                    console.log(`  - "blazer" in name: ${blazerItem.name.toLowerCase().includes('blazer')}`);
                    console.log(`  - Should match keep_items: ["blazer", "suit jacket", "sport coat"]`);
                }
                
                if (shortsItem) {
                    console.log(`  Shorts: "${shortsItem.name}" (type: "${shortsItem.type}")`);
                    console.log(`  - "shorts" in type: ${shortsItem.type.toLowerCase().includes('shorts')}`);
                    console.log(`  - "shorts" in name: ${shortsItem.name.toLowerCase().includes('shorts')}`);
                    console.log(`  - Should match remove_items: ["shorts", "athletic shorts", "basketball shorts", "cargo shorts", "denim shorts"]`);
                }
                
                console.log(`\n🔧 DIAGNOSIS:`);
                console.log(`  The enhanced validation rules should have:`);
                console.log(`  1. Detected blazer item (keep_items)`);
                console.log(`  2. Detected shorts item (remove_items)`);
                console.log(`  3. Removed the shorts item because blazer was present`);
                console.log(`  Since this didn't happen, there's a bug in the validation logic.`);
                
            } else {
                console.log(`  ✅ No inappropriate combination - validation working!`);
            }
            
        } else {
            console.log(`❌ Request failed: ${response.status}`);
            console.log("Response:", JSON.stringify(response.data, null, 2));
        }
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }
}

debugValidationCall().catch(console.error);
