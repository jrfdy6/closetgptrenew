#!/usr/bin/env node
/**
 * TEST COHESIVE OUTFIT COMPOSITION
 * Test the new cohesive outfit composition service
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

async function testCohesiveOutfitGeneration() {
    console.log("🎨 TESTING COHESIVE OUTFIT COMPOSITION");
    console.log("=" * 60);
    
    // Test with a diverse wardrobe that should create cohesive outfits
    const testWardrobe = [
        // Bottoms
        { id: "1", name: "Dark Navy Dress Pants", type: "pants", color: "navy", style: "business", occasion: "business" },
        { id: "2", name: "Black Jeans", type: "jeans", color: "black", style: "casual", occasion: "casual" },
        { id: "3", name: "Khaki Chinos", type: "chinos", color: "khaki", style: "casual", occasion: "casual" },
        
        // Tops
        { id: "4", name: "White Dress Shirt", type: "shirt", color: "white", style: "business", occasion: "business" },
        { id: "5", name: "Light Blue Button-Up", type: "shirt", color: "light blue", style: "casual", occasion: "casual" },
        { id: "6", name: "Gray T-Shirt", type: "t-shirt", color: "gray", style: "casual", occasion: "casual" },
        
        // Layers
        { id: "7", name: "Navy Blazer", type: "blazer", color: "navy", style: "business", occasion: "business" },
        { id: "8", name: "Black Sweater", type: "sweater", color: "black", style: "casual", occasion: "casual" },
        
        // Shoes
        { id: "9", name: "Black Oxford Shoes", type: "shoes", color: "black", style: "formal", occasion: "business" },
        { id: "10", name: "White Sneakers", type: "sneakers", color: "white", style: "casual", occasion: "casual" },
        { id: "11", name: "Brown Loafers", type: "loafers", color: "brown", style: "business_casual", occasion: "business_casual" }
    ];
    
    const testScenarios = [
        {
            name: "Business Casual Weekend",
            request: {
                occasion: "Weekend",
                style: "Business Casual", 
                mood: "Serene",
                wardrobe: testWardrobe,
                userProfile: { id: "test_user" },
                weather: {
                    temperature: 70,
                    condition: "Clear",
                    humidity: 60,
                    windSpeed: 5,
                    precipitation: 0
                }
            },
            expectedCohesion: {
                maxItems: 4,
                colorHarmony: "Should have 2-3 harmonious colors",
                styleConsistency: "All items should match business casual formality",
                basePiece: "Should start with appropriate bottom"
            }
        },
        {
            name: "Casual Weekend",
            request: {
                occasion: "Weekend",
                style: "Casual",
                mood: "Relaxed", 
                wardrobe: testWardrobe,
                userProfile: { id: "test_user" },
                weather: {
                    temperature: 75,
                    condition: "Sunny",
                    humidity: 50,
                    windSpeed: 3,
                    precipitation: 0
                }
            },
            expectedCohesion: {
                maxItems: 3,
                colorHarmony: "Should have 2-3 harmonious colors",
                styleConsistency: "All items should match casual formality",
                basePiece: "Should start with casual bottom"
            }
        }
    ];
    
    for (const scenario of testScenarios) {
        console.log(`\n🧪 Testing: ${scenario.name}`);
        console.log(`   Expected: ${scenario.expectedCohesion.maxItems} items max, ${scenario.expectedCohesion.colorHarmony}`);
        
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
            
            console.log(`📊 Response Status: ${response.status}`);
            
            if (response.status === 200) {
                const outfit = response.data;
                const items = outfit.items || [];
                
                console.log(`✅ Generated outfit: "${outfit.name}"`);
                console.log(`   Items (${items.length}):`);
                items.forEach((item, index) => {
                    console.log(`     ${index + 1}. ${item.name} (${item.type}) - ${item.color}`);
                });
                
                // Analyze cohesion
                console.log(`\n🔍 COHESION ANALYSIS:`);
                
                // Check item count
                const itemCount = items.length;
                const maxExpected = scenario.expectedCohesion.maxItems;
                if (itemCount <= maxExpected) {
                    console.log(`✅ Item count: ${itemCount}/${maxExpected} - Good cohesion`);
                } else {
                    console.log(`❌ Item count: ${itemCount}/${maxExpected} - Too many items`);
                }
                
                // Check color harmony
                const colors = items.map(item => item.color.toLowerCase());
                const uniqueColors = [...new Set(colors)];
                console.log(`🎨 Colors used: ${uniqueColors.join(', ')} (${uniqueColors.length} unique)`);
                if (uniqueColors.length <= 3) {
                    console.log(`✅ Color harmony: Good (${uniqueColors.length} colors)`);
                } else {
                    console.log(`⚠️ Color harmony: Could be better (${uniqueColors.length} colors)`);
                }
                
                // Check for base piece (bottom)
                const hasBottom = items.some(item => 
                    ['pants', 'jeans', 'chinos', 'shorts', 'skirt'].some(bottom => 
                        item.type.toLowerCase().includes(bottom)
                    )
                );
                if (hasBottom) {
                    console.log(`✅ Base piece: Has appropriate bottom`);
                } else {
                    console.log(`❌ Base piece: Missing bottom`);
                }
                
                // Check style consistency
                const itemTypes = items.map(item => item.type.toLowerCase());
                const hasFormalItems = itemTypes.some(type => 
                    ['blazer', 'dress_shirt', 'oxford'].some(formal => type.includes(formal))
                );
                const hasCasualItems = itemTypes.some(type => 
                    ['t-shirt', 'sneakers', 'jeans'].some(casual => type.includes(casual))
                );
                
                if (hasFormalItems && hasCasualItems) {
                    console.log(`⚠️ Style consistency: Mixed formal/casual items`);
                } else {
                    console.log(`✅ Style consistency: Consistent formality level`);
                }
                
                // Overall assessment
                const isCohesive = itemCount <= maxExpected && uniqueColors.length <= 3 && hasBottom;
                console.log(`\n🎯 OVERALL ASSESSMENT:`);
                if (isCohesive) {
                    console.log(`✅ COHESIVE: Outfit shows good composition and harmony`);
                } else {
                    console.log(`❌ NOT COHESIVE: Outfit needs better composition`);
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

testCohesiveOutfitGeneration().catch(console.error);
