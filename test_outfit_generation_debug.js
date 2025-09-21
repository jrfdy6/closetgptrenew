#!/usr/bin/env node
/**
 * Test Outfit Generation with Debug
 * Generate an outfit and see what happens
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

async function testOutfitGeneration() {
    console.log("🧪 Testing Outfit Generation with Debug");
    console.log("=" * 50);
    
    // Create a test request
    const testRequest = {
        occasion: "casual",
        wardrobe: [
            // Tops
            { id: "1", name: "White T-Shirt", type: "t-shirt", color: "white" },
            { id: "2", name: "Blue Shirt", type: "shirt", color: "blue" },
            { id: "3", name: "Gray Sweater", type: "sweater", color: "gray" },
            
            // Bottoms - THESE SHOULD BE INCLUDED
            { id: "4", name: "Blue Jeans", type: "jeans", color: "blue" },
            { id: "5", name: "Black Pants", type: "pants", color: "black" },
            { id: "6", name: "Khaki Shorts", type: "shorts", color: "khaki" },
            
            // Shoes
            { id: "7", name: "White Sneakers", type: "sneakers", color: "white" },
            { id: "8", name: "Brown Loafers", type: "loafers", color: "brown" },
            
            // Accessories
            { id: "9", name: "Black Belt", type: "belt", color: "black" }
        ],
        weather: { 
            temperature: 70, 
            condition: "clear",
            humidity: 65,
            wind_speed: 5,
            precipitation: 0
        },
        userProfile: { id: "test_user" },
        style: "casual",
        mood: "confident"
    };
    
    try {
        console.log("🎯 Generating outfit with test wardrobe...");
        console.log(`📊 Test wardrobe: ${testRequest.wardrobe.length} items`);
        console.log("   Tops:", testRequest.wardrobe.filter(item => 
            item.type.includes('shirt') || item.type.includes('sweater')).length);
        console.log("   Bottoms:", testRequest.wardrobe.filter(item => 
            item.type.includes('pants') || item.type.includes('jeans') || item.type.includes('shorts')).length);
        console.log("   Shoes:", testRequest.wardrobe.filter(item => 
            item.type.includes('shoes') || item.type.includes('sneakers') || item.type.includes('loafers')).length);
        
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
            console.log("✅ Outfit generated successfully");
            
            if (response.data && response.data.items) {
                const items = response.data.items;
                console.log(`\n📋 Generated Outfit (${items.length} items):`);
                
                items.forEach((item, index) => {
                    console.log(`   ${index + 1}. ${item.name} (${item.type})`);
                });
                
                // Categorize generated items
                const categories = {
                    "tops": 0,
                    "bottoms": 0,
                    "shoes": 0,
                    "accessories": 0
                };
                
                items.forEach(item => {
                    const type = (item.type || '').toLowerCase();
                    if (type.includes('shirt') || type.includes('sweater') || type.includes('jacket')) {
                        categories.tops++;
                    } else if (type.includes('pants') || type.includes('jeans') || type.includes('shorts')) {
                        categories.bottoms++;
                    } else if (type.includes('shoes') || type.includes('sneakers') || type.includes('loafers')) {
                        categories.shoes++;
                    } else if (type.includes('belt') || type.includes('accessory')) {
                        categories.accessories++;
                    }
                });
                
                console.log("\n📊 Generated Outfit Categories:");
                console.log(`   👕 Tops: ${categories.tops}`);
                console.log(`   👖 Bottoms: ${categories.bottoms}`);
                console.log(`   👟 Shoes: ${categories.shoes}`);
                console.log(`   🎒 Accessories: ${categories.accessories}`);
                
                // Analysis
                console.log("\n🎯 ANALYSIS:");
                if (categories.bottoms === 0) {
                    console.log("❌ ISSUE: Generated outfit has NO BOTTOMS!");
                    console.log("   This confirms the validation is filtering out pants/bottoms.");
                } else if (categories.bottoms < 1) {
                    console.log("⚠️  WARNING: Very few bottoms in generated outfit");
                } else {
                    console.log("✅ Good: Generated outfit includes bottoms");
                }
                
                if (categories.tops === 0) {
                    console.log("❌ ISSUE: Generated outfit has NO TOPS!");
                } else {
                    console.log("✅ Good: Generated outfit includes tops");
                }
                
                if (categories.shoes === 0) {
                    console.log("❌ ISSUE: Generated outfit has NO SHOES!");
                } else {
                    console.log("✅ Good: Generated outfit includes shoes");
                }
                
            } else {
                console.log("❌ No items in generated outfit");
                console.log("Response:", JSON.stringify(response.data, null, 2));
            }
            
        } else {
            console.log(`❌ Outfit generation failed: ${response.status}`);
            console.log("Response:", JSON.stringify(response.data, null, 2));
        }
        
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }
}

testOutfitGeneration().catch(console.error);
