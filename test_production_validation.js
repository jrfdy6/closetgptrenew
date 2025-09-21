#!/usr/bin/env node
/**
 * TEST PRODUCTION VALIDATION
 * Test if the enhanced validation system is working in production
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

async function testProductionValidation() {
    console.log("🔍 TESTING PRODUCTION VALIDATION SYSTEM");
    console.log("=" * 60);
    
    // Test with a wardrobe that should trigger validation issues
    const testWardrobe = [
        { id: "1", name: "Black Blazer", type: "blazer", color: "black", style: "formal" },
        { id: "2", name: "Khaki Shorts", type: "shorts", color: "khaki", style: "casual" },
        { id: "3", name: "Brown Pants", type: "pants", color: "brown", style: "casual" },
        { id: "4", name: "Black Oxford Shoes", type: "shoes", color: "black", style: "formal" },
        { id: "5", name: "White T-Shirt", type: "t-shirt", color: "white", style: "casual" },
        { id: "6", name: "White Sneakers", type: "sneakers", color: "white", style: "casual" },
        { id: "7", name: "Blue Jeans", type: "jeans", color: "blue", style: "casual" },
        { id: "8", name: "Black Belt", type: "belt", color: "black", style: "casual" }
    ];
    
    const testRequest = {
        occasion: "Fall",
        wardrobe: testWardrobe,
        userProfile: { id: "test_user" },
        style: "Coastal Chic",
        mood: "Serene",
        weather: {
            temperature: 70,
            condition: "Clouds",
            humidity: 80,
            windSpeed: 4.12,
            precipitation: 0
        }
    };
    
    console.log("🧪 Testing with problematic wardrobe that should trigger validation...");
    console.log("   - Has blazer + shorts (should be prevented)");
    console.log("   - Has formal shoes + casual bottoms (should be prevented)");
    console.log("   - Has multiple bottoms (should be limited to 1)");
    
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
        
        console.log(`\n📊 RESPONSE STATUS: ${response.status}`);
        
        if (response.status === 200) {
            const outfit = response.data;
            const items = outfit.items || [];
            
            console.log(`✅ Success: Generated outfit "${outfit.name}"`);
            console.log(`   Items (${items.length}):`);
            items.forEach((item, index) => {
                console.log(`     ${index + 1}. ${item.name} (${item.type}) - ${item.color}`);
            });
            
            // Check for validation issues
            const itemTypes = items.map(item => item.type.toLowerCase());
            const itemNames = items.map(item => item.name.toLowerCase());
            
            console.log(`\n🔍 VALIDATION CHECKS:`);
            
            // Check for blazer + shorts
            const hasBlazer = itemTypes.some(type => type.includes('blazer')) || itemNames.some(name => name.includes('blazer'));
            const hasShorts = itemTypes.some(type => type.includes('shorts')) || itemNames.some(name => name.includes('shorts'));
            
            if (hasBlazer && hasShorts) {
                console.log(`❌ VALIDATION FAILED: Blazer + Shorts combination detected!`);
            } else {
                console.log(`✅ VALIDATION PASSED: No blazer + shorts combination`);
            }
            
            // Check for multiple bottoms
            const bottomTypes = ['pants', 'jeans', 'shorts', 'skirt', 'dress'];
            const bottomCount = itemTypes.filter(type => bottomTypes.some(bottom => type.includes(bottom))).length;
            
            if (bottomCount > 1) {
                console.log(`❌ VALIDATION FAILED: Multiple bottoms detected (${bottomCount})!`);
            } else {
                console.log(`✅ VALIDATION PASSED: Only ${bottomCount} bottom(s)`);
            }
            
            // Check for multiple shoes
            const shoeTypes = ['shoes', 'sneakers', 'boots', 'sandals', 'heels'];
            const shoeCount = itemTypes.filter(type => shoeTypes.some(shoe => type.includes(shoe))).length;
            
            if (shoeCount > 1) {
                console.log(`❌ VALIDATION FAILED: Multiple shoes detected (${shoeCount})!`);
            } else {
                console.log(`✅ VALIDATION PASSED: Only ${shoeCount} shoe(s)`);
            }
            
            // Check for formal shoes + casual bottoms
            const hasFormalShoes = itemTypes.some(type => type.includes('oxford') || type.includes('loafers') || type.includes('heels'));
            const hasCasualBottoms = itemTypes.some(type => type.includes('shorts') || type.includes('cargo pants') || type.includes('sweatpants'));
            
            if (hasFormalShoes && hasCasualBottoms) {
                console.log(`❌ VALIDATION FAILED: Formal shoes + Casual bottoms combination detected!`);
            } else {
                console.log(`✅ VALIDATION PASSED: No formal shoes + casual bottoms combination`);
            }
            
            // Check essential categories
            const hasTop = itemTypes.some(type => type.includes('shirt') || type.includes('blazer') || type.includes('t-shirt'));
            const hasBottom = itemTypes.some(type => bottomTypes.some(bottom => type.includes(bottom)));
            const hasShoes = itemTypes.some(type => shoeTypes.some(shoe => type.includes(shoe)));
            
            console.log(`\n📋 ESSENTIAL CATEGORIES:`);
            console.log(`   Top: ${hasTop ? '✅' : '❌'}`);
            console.log(`   Bottom: ${hasBottom ? '✅' : '❌'}`);
            console.log(`   Shoes: ${hasShoes ? '✅' : '❌'}`);
            
            // Check item count
            if (items.length >= 3 && items.length <= 6) {
                console.log(`✅ VALIDATION PASSED: Item count is appropriate (${items.length}/3-6)`);
            } else {
                console.log(`❌ VALIDATION FAILED: Item count is inappropriate (${items.length}/3-6)`);
            }
            
            // Overall assessment
            const hasValidationIssues = (hasBlazer && hasShorts) || bottomCount > 1 || shoeCount > 1 || (hasFormalShoes && hasCasualBottoms) || !hasTop || !hasBottom || !hasShoes || items.length < 3 || items.length > 6;
            
            console.log(`\n🎯 OVERALL ASSESSMENT:`);
            if (hasValidationIssues) {
                console.log(`❌ VALIDATION SYSTEM NOT WORKING: Multiple issues detected`);
                console.log(`   The enhanced validation system is not being applied properly`);
            } else {
                console.log(`✅ VALIDATION SYSTEM WORKING: All checks passed`);
                console.log(`   The enhanced validation system is working correctly`);
            }
            
        } else {
            console.log(`❌ Request failed: HTTP ${response.status}`);
            console.log(`   Response: ${JSON.stringify(response.data)}`);
        }
        
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }
}

testProductionValidation().catch(console.error);