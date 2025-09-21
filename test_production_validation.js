#!/usr/bin/env node
/**
 * Production Testing Script for Enhanced Validation Rules
 * Tests the production backend with enhanced validation rules
 */

const https = require('https');
const http = require('http');

// Configuration
const BACKEND_URL = 'https://closetgpt-backend-production.up.railway.app'; // Update with your production URL
const FRONTEND_URL = 'https://closetgpt-frontend.vercel.app'; // Update with your production URL

// Test scenarios
const TEST_SCENARIOS = [
    {
        name: "Business Occasion",
        occasion: "business",
        expectedFormality: "high",
        shouldNotHave: ["sneakers", "hoodie", "t-shirt", "athletic shorts", "cargo pants"]
    },
    {
        name: "Athletic Occasion", 
        occasion: "athletic",
        expectedFormality: "low",
        shouldNotHave: ["blazer", "suit", "dress shirt", "oxford", "heels"]
    },
    {
        name: "Formal Occasion",
        occasion: "formal", 
        expectedFormality: "very high",
        shouldNotHave: ["sneakers", "hoodie", "t-shirt", "jeans", "cargo pants"]
    },
    {
        name: "Casual Occasion",
        occasion: "casual",
        expectedFormality: "low",
        shouldNotHave: ["suit", "dress shirt"] // Should allow some mixing
    },
    {
        name: "Business Casual Occasion",
        occasion: "business casual",
        expectedFormality: "medium",
        shouldNotHave: ["suit", "athletic shorts", "flip-flops"]
    }
];

// Mock wardrobe data for testing
const MOCK_WARDROBE = [
    // Formal items
    { id: "1", name: "Navy Blazer", type: "blazer", color: "navy", style: ["formal"], occasion: ["business", "formal"] },
    { id: "2", name: "Black Suit", type: "suit", color: "black", style: ["formal"], occasion: ["formal", "business"] },
    { id: "3", name: "White Dress Shirt", type: "dress shirt", color: "white", style: ["formal"], occasion: ["business", "formal"] },
    { id: "4", name: "Black Oxford Shoes", type: "oxford", color: "black", style: ["formal"], occasion: ["business", "formal"] },
    { id: "5", name: "Black Heels", type: "heels", color: "black", style: ["formal"], occasion: ["business", "formal"] },
    
    // Business casual items
    { id: "6", name: "Navy Polo Shirt", type: "polo shirt", color: "navy", style: ["business casual"], occasion: ["business casual"] },
    { id: "7", name: "Khaki Chinos", type: "chinos", color: "khaki", style: ["business casual"], occasion: ["business casual"] },
    { id: "8", name: "Brown Loafers", type: "loafers", color: "brown", style: ["business casual"], occasion: ["business casual"] },
    
    // Casual items
    { id: "9", name: "White T-Shirt", type: "t-shirt", color: "white", style: ["casual"], occasion: ["casual", "athletic"] },
    { id: "10", name: "Blue Jeans", type: "jeans", color: "blue", style: ["casual"], occasion: ["casual"] },
    { id: "11", name: "White Sneakers", type: "sneakers", color: "white", style: ["casual"], occasion: ["casual", "athletic"] },
    { id: "12", name: "Gray Hoodie", type: "hoodie", color: "gray", style: ["casual"], occasion: ["casual", "athletic"] },
    
    // Problematic items (should be filtered)
    { id: "13", name: "Black Athletic Shorts", type: "athletic shorts", color: "black", style: ["athletic"], occasion: ["athletic"] },
    { id: "14", name: "Khaki Cargo Pants", type: "cargo pants", color: "khaki", style: ["casual"], occasion: ["casual"] },
    { id: "15", name: "Black Flip Flops", type: "flip-flops", color: "black", style: ["casual"], occasion: ["casual", "beach"] },
    { id: "16", name: "White Tank Top", type: "tank top", color: "white", style: ["casual"], occasion: ["casual", "athletic"] }
];

async function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const protocol = url.startsWith('https') ? https : http;
        
        const req = protocol.request(url, options, (res) => {
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

async function testOutfitGeneration(occasion) {
    console.log(`\n🧪 Testing ${occasion} outfit generation...`);
    
    try {
        const requestBody = JSON.stringify({
            occasion: occasion,
            wardrobe: MOCK_WARDROBE,
            weather: {
                temperature: 70,
                condition: "clear",
                humidity: 50,
                windSpeed: 5,
                precipitation: 0
            },
            userProfile: {
                id: "test_user",
                preferences: {},
                bodyType: "average"
            },
            style: occasion === "casual" ? "casual" : "business",
            mood: "confident"
        });
        
        const response = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(requestBody)
            },
            body: requestBody
        });
        
        if (response.status === 200) {
            console.log(`✅ ${occasion} outfit generated successfully`);
            return response.data;
        } else {
            console.log(`❌ ${occasion} outfit generation failed: ${response.status}`);
            console.log(`   Response: ${JSON.stringify(response.data, null, 2)}`);
            return null;
        }
    } catch (error) {
        console.log(`❌ ${occasion} outfit generation error: ${error.message}`);
        return null;
    }
}

function analyzeOutfit(outfit, scenario) {
    if (!outfit || !outfit.items) {
        return {
            isValid: false,
            issues: ["No outfit generated"],
            items: []
        };
    }
    
    const items = outfit.items;
    const itemNames = items.map(item => item.name.toLowerCase());
    const itemTypes = items.map(item => item.type.toLowerCase());
    
    const issues = [];
    
    // Check for inappropriate items based on occasion
    scenario.shouldNotHave.forEach(forbiddenItem => {
        if (itemTypes.includes(forbiddenItem.toLowerCase())) {
            issues.push(`Contains inappropriate ${forbiddenItem} for ${scenario.name} occasion`);
        }
    });
    
    // Check for specific problematic combinations
    const hasBlazer = itemTypes.includes('blazer');
    const hasSuit = itemTypes.includes('suit');
    const hasFormalShoes = itemTypes.some(type => ['oxford', 'heels', 'loafers'].includes(type));
    const hasCasualBottoms = itemTypes.some(type => ['jeans', 'athletic shorts', 'cargo pants'].includes(type));
    const hasCasualItems = itemTypes.some(type => ['sneakers', 'hoodie', 't-shirt', 'tank top'].includes(type));
    
    // Check blazer + casual items
    if (hasBlazer && hasCasualItems) {
        issues.push("Blazer paired with casual items");
    }
    
    // Check formal shoes + casual bottoms
    if (hasFormalShoes && hasCasualBottoms) {
        issues.push("Formal shoes paired with casual bottoms");
    }
    
    // Check suit + casual items
    if (hasSuit && hasCasualItems) {
        issues.push("Suit paired with casual items");
    }
    
    return {
        isValid: issues.length === 0,
        issues: issues,
        items: items,
        itemCount: items.length
    };
}

async function runProductionTests() {
    console.log("🚀 Production Testing for Enhanced Validation Rules");
    console.log("=" * 60);
    console.log(`Backend URL: ${BACKEND_URL}`);
    console.log(`Frontend URL: ${FRONTEND_URL}`);
    console.log("=" * 60);
    
    const results = {
        total: 0,
        passed: 0,
        failed: 0,
        scenarios: []
    };
    
    for (const scenario of TEST_SCENARIOS) {
        console.log(`\n🎭 Testing ${scenario.name}...`);
        
        const outfit = await testOutfitGeneration(scenario.occasion);
        const analysis = analyzeOutfit(outfit, scenario);
        
        results.total++;
        results.scenarios.push({
            name: scenario.name,
            occasion: scenario.occasion,
            isValid: analysis.isValid,
            issues: analysis.issues,
            itemCount: analysis.itemCount,
            items: analysis.items?.map(item => `${item.name} (${item.type})`) || []
        });
        
        if (analysis.isValid) {
            results.passed++;
            console.log(`✅ ${scenario.name}: PASSED`);
            console.log(`   Items: ${analysis.items?.map(item => item.name).join(', ') || 'None'}`);
        } else {
            results.failed++;
            console.log(`❌ ${scenario.name}: FAILED`);
            analysis.issues.forEach(issue => console.log(`   - ${issue}`));
            console.log(`   Items: ${analysis.items?.map(item => item.name).join(', ') || 'None'}`);
        }
        
        // Wait a bit between requests
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Print summary
    console.log("\n📊 PRODUCTION TEST RESULTS");
    console.log("=" * 60);
    console.log(`Total Tests: ${results.total}`);
    console.log(`Passed: ${results.passed}`);
    console.log(`Failed: ${results.failed}`);
    console.log(`Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);
    
    console.log("\n📋 DETAILED RESULTS:");
    results.scenarios.forEach(scenario => {
        const status = scenario.isValid ? "✅ PASS" : "❌ FAIL";
        console.log(`\n${status} ${scenario.name}:`);
        console.log(`   Occasion: ${scenario.occasion}`);
        console.log(`   Items (${scenario.itemCount}): ${scenario.items.join(', ')}`);
        if (scenario.issues.length > 0) {
            console.log(`   Issues: ${scenario.issues.join(', ')}`);
        }
    });
    
    // Final assessment
    const successRate = (results.passed / results.total) * 100;
    console.log("\n🎊 FINAL ASSESSMENT:");
    if (successRate >= 90) {
        console.log("🎉 EXCELLENT: Enhanced validation rules are working perfectly in production!");
    } else if (successRate >= 80) {
        console.log("✅ GOOD: Enhanced validation rules are working well in production!");
    } else if (successRate >= 70) {
        console.log("⚠️  MODERATE: Enhanced validation rules need some improvement");
    } else {
        console.log("❌ NEEDS WORK: Enhanced validation rules need significant improvement");
    }
    
    return results;
}

// Run the tests
if (require.main === module) {
    runProductionTests().catch(console.error);
}

module.exports = { runProductionTests, testOutfitGeneration, analyzeOutfit };
