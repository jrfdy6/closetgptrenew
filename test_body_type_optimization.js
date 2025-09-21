#!/usr/bin/env node
/**
 * TEST BODY TYPE OPTIMIZATION
 * Test the new body type optimization service
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

async function testBodyTypeOptimization() {
    console.log("🎯 TESTING BODY TYPE OPTIMIZATION");
    console.log("=" * 60);
    
    // Test wardrobe with items that should be optimized for different body types
    const testWardrobe = [
        // Bottoms
        { id: "1", name: "High-Waisted Straight Pants", type: "pants", color: "black", style: "business" },
        { id: "2", name: "Wide-Leg Palazzo Pants", type: "pants", color: "navy", style: "casual" },
        { id: "3", name: "Fitted Pencil Skirt", type: "skirt", color: "black", style: "business" },
        { id: "4", name: "A-Line Midi Skirt", type: "skirt", color: "gray", style: "casual" },
        
        // Tops
        { id: "5", name: "V-Neck Structured Blazer", type: "blazer", color: "navy", style: "business" },
        { id: "6", name: "Crew Neck T-Shirt", type: "t-shirt", color: "white", style: "casual" },
        { id: "7", name: "Wrap Top with Belt", type: "shirt", color: "burgundy", style: "casual" },
        { id: "8", name: "Peplum Button-Up Shirt", type: "shirt", color: "light blue", style: "business_casual" },
        
        // Dresses
        { id: "9", name: "Wrap Dress with Belt", type: "dress", color: "black", style: "business" },
        { id: "10", name: "A-Line Shift Dress", type: "dress", color: "navy", style: "casual" },
        { id: "11", name: "Fitted Sheath Dress", type: "dress", color: "gray", style: "business" },
        
        // Shoes
        { id: "12", name: "Black Oxford Shoes", type: "shoes", color: "black", style: "formal" },
        { id: "13", name: "Nude Heels", type: "heels", color: "nude", style: "business" },
        { id: "14", name: "White Sneakers", type: "sneakers", color: "white", style: "casual" }
    ];
    
    const bodyTypeTests = [
        {
            name: "Apple Body Type",
            bodyType: "apple",
            userProfile: {
                id: "test_user_apple",
                body_type: "apple",
                preferences: { body_type: "apple" }
            },
            expectedOptimizations: {
                shouldPrefer: ["structured_blazers", "straight_pants", "v_neck", "a_line_dresses"],
                shouldAvoid: ["tight_midsection", "high_waisted", "belted_waist"],
                silhouette: "structured_and_tailored"
            }
        },
        {
            name: "Pear Body Type", 
            bodyType: "pear",
            userProfile: {
                id: "test_user_pear",
                body_type: "pear",
                preferences: { body_type: "pear" }
            },
            expectedOptimizations: {
                shouldPrefer: ["structured_tops", "a_line_skirts", "wide_leg_pants", "belts"],
                shouldAvoid: ["tight_bottoms", "light_colors_bottom"],
                silhouette: "balanced_top_bottom"
            }
        },
        {
            name: "Hourglass Body Type",
            bodyType: "hourglass", 
            userProfile: {
                id: "test_user_hourglass",
                body_type: "hourglass",
                preferences: { body_type: "hourglass" }
            },
            expectedOptimizations: {
                shouldPrefer: ["fitted_tops", "belted_waists", "wrap_dresses", "pencil_skirts"],
                shouldAvoid: ["boxy_fits", "oversized", "no_waist_definition"],
                silhouette: "fitted_and_curved"
            }
        },
        {
            name: "Rectangle Body Type",
            bodyType: "rectangle",
            userProfile: {
                id: "test_user_rectangle", 
                body_type: "rectangle",
                preferences: { body_type: "rectangle" }
            },
            expectedOptimizations: {
                shouldPrefer: ["belted_waists", "peplum_tops", "a_line_skirts", "layered_tops"],
                shouldAvoid: ["boxy_silhouettes", "straight_lines", "no_definition"],
                silhouette: "create_curves"
            }
        }
    ];
    
    for (const test of bodyTypeTests) {
        console.log(`\n🧪 Testing: ${test.name}`);
        console.log(`   Expected: ${test.expectedOptimizations.silhouette}`);
        console.log(`   Should prefer: ${test.expectedOptimizations.shouldPrefer.join(', ')}`);
        
        const requestData = {
            occasion: "Business Casual",
            style: "Business Casual",
            mood: "Confident",
            wardrobe: testWardrobe,
            user_profile: test.userProfile,
            weather: {
                temperature: 70,
                condition: "Clear",
                humidity: 60,
                windSpeed: 5,
                precipitation: 0
            }
        };
        
        try {
            const response = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer test',
                    'Content-Length': Buffer.byteLength(JSON.stringify(requestData))
                },
                body: JSON.stringify(requestData)
            });
            
            console.log(`📊 Response Status: ${response.status}`);
            
            if (response.status === 200) {
                const outfit = response.data;
                const items = outfit.items || [];
                
                console.log(`✅ Generated outfit: "${outfit.name}"`);
                console.log(`   Items (${items.length}):`);
                items.forEach((item, index) => {
                    console.log(`     ${index + 1}. ${item.name} (${item.type}) - ${item.color}`);
                });
                
                // Analyze body type optimization
                console.log(`\n🎯 BODY TYPE OPTIMIZATION ANALYSIS:`);
                
                // Check if preferred items were selected
                const itemNames = items.map(item => item.name.toLowerCase());
                const itemTypes = items.map(item => item.type.toLowerCase());
                
                let preferredCount = 0;
                let avoidedCount = 0;
                
                for (const preferred in test.expectedOptimizations.shouldPrefer) {
                    const preference = test.expectedOptimizations.shouldPrefer[preferred];
                    if (itemNames.some(name => name.includes(preference.replace('_', ' '))) ||
                        itemTypes.some(type => type.includes(preference.replace('_', ' ')))) {
                        preferredCount++;
                    }
                }
                
                for (const avoided in test.expectedOptimizations.shouldAvoid) {
                    const avoid = test.expectedOptimizations.shouldAvoid[avoided];
                    if (itemNames.some(name => name.includes(avoid.replace('_', ' '))) ||
                        itemTypes.some(type => type.includes(avoid.replace('_', ' ')))) {
                        avoidedCount++;
                    }
                }
                
                console.log(`   Preferred items selected: ${preferredCount}/${test.expectedOptimizations.shouldPrefer.length}`);
                console.log(`   Avoided items selected: ${avoidedCount}/${test.expectedOptimizations.shouldAvoid.length}`);
                
                // Check silhouette appropriateness
                const hasStructuredItems = itemTypes.some(type => 
                    ['blazer', 'structured', 'fitted'].some(structured => type.includes(structured))
                );
                const hasBeltedItems = itemNames.some(name => 
                    ['belt', 'belted', 'wrap'].some(belted => name.includes(belted))
                );
                const hasAlineItems = itemNames.some(name => 
                    ['a_line', 'a-line', 'a line'].some(aline => name.includes(aline))
                );
                
                console.log(`   Silhouette elements:`);
                console.log(`     - Structured items: ${hasStructuredItems ? '✅' : '❌'}`);
                console.log(`     - Belted items: ${hasBeltedItems ? '✅' : '❌'}`);
                console.log(`     - A-line items: ${hasAlineItems ? '✅' : '❌'}`);
                
                // Overall assessment
                const isOptimized = preferredCount > 0 && avoidedCount === 0;
                console.log(`\n🎯 OVERALL ASSESSMENT:`);
                if (isOptimized) {
                    console.log(`✅ BODY TYPE OPTIMIZED: Outfit shows good body type optimization`);
                } else {
                    console.log(`⚠️ PARTIAL OPTIMIZATION: Some body type considerations applied`);
                }
                
            } else {
                console.log(`❌ Request failed: HTTP ${response.status}`);
                console.log(`   Response: ${JSON.stringify(response.data)}`);
            }
            
        } catch (error) {
            console.log(`❌ Error: ${error.message}`);
        }
        
        console.log("\n" + "-" * 50);
    }
}

testBodyTypeOptimization().catch(console.error);
