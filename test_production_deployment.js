#!/usr/bin/env node
/**
 * Quick Production Deployment Test
 * Tests if enhanced validation rules are working in production
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

async function testEnhancedValidation() {
    console.log("🧪 Testing Enhanced Validation Rules in Production");
    console.log("=" * 60);
    console.log(`Backend URL: ${BACKEND_URL}`);
    
    // Simple test outfit request
    const testRequest = {
        occasion: "business",
        wardrobe: [
            { id: "1", name: "Navy Blazer", type: "blazer", color: "navy" },
            { id: "2", name: "Athletic Shorts", type: "athletic shorts", color: "black" },
            { id: "3", name: "White Sneakers", type: "sneakers", color: "white" },
            { id: "4", name: "Dress Shirt", type: "dress shirt", color: "white" }
        ],
        weather: { temperature: 70, condition: "clear" },
        userProfile: { id: "test_user" },
        style: "business"
    };
    
    try {
        console.log("\n🎯 Testing Business Outfit Generation...");
        console.log("Input: Blazer + Athletic Shorts + Sneakers (should be filtered)");
        
        const response = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(JSON.stringify(testRequest))
            },
            body: JSON.stringify(testRequest)
        });
        
        if (response.status === 200) {
            console.log("✅ Backend responded successfully");
            
            if (response.data && response.data.items) {
                const items = response.data.items;
                const itemNames = items.map(item => item.name);
                
                console.log(`\n📋 Generated Outfit (${items.length} items):`);
                items.forEach(item => console.log(`   - ${item.name} (${item.type})`));
                
                // Check for inappropriate combinations
                const hasBlazer = items.some(item => item.type === "blazer");
                const hasAthleticShorts = items.some(item => item.type === "athletic shorts");
                const hasSneakers = items.some(item => item.type === "sneakers");
                
                if (hasBlazer && hasAthleticShorts) {
                    console.log("❌ ISSUE: Blazer with athletic shorts - enhanced validation failed");
                } else if (hasBlazer && hasSneakers) {
                    console.log("❌ ISSUE: Blazer with sneakers - enhanced validation failed");
                } else if (hasAthleticShorts && hasSneakers) {
                    console.log("❌ ISSUE: Athletic shorts with sneakers - enhanced validation failed");
                } else {
                    console.log("✅ SUCCESS: Enhanced validation rules working - inappropriate combinations filtered out!");
                }
                
                // Check if outfit is business-appropriate
                const hasFormalItems = items.some(item => 
                    ["blazer", "dress shirt", "oxford", "heels"].includes(item.type)
                );
                
                if (hasFormalItems) {
                    console.log("✅ SUCCESS: Business outfit contains appropriate formal items");
                } else {
                    console.log("⚠️  WARNING: Business outfit may be too casual");
                }
                
            } else {
                console.log("⚠️  No outfit items in response");
                console.log("Response:", JSON.stringify(response.data, null, 2));
            }
            
        } else {
            console.log(`❌ Backend error: ${response.status}`);
            console.log("Response:", JSON.stringify(response.data, null, 2));
        }
        
    } catch (error) {
        console.log(`❌ Request failed: ${error.message}`);
    }
}

async function testHealth() {
    console.log("\n🏥 Testing Backend Health...");
    
    try {
        const response = await makeRequest(`${BACKEND_URL}/health`);
        
        if (response.status === 200) {
            console.log("✅ Backend is healthy and responding");
            console.log(`   Status: ${response.data.status}`);
            console.log(`   Environment: ${response.data.environment}`);
        } else {
            console.log(`❌ Health check failed: ${response.status}`);
        }
    } catch (error) {
        console.log(`❌ Health check error: ${error.message}`);
    }
}

async function main() {
    await testHealth();
    await testEnhancedValidation();
    
    console.log("\n🎊 DEPLOYMENT TEST COMPLETE");
    console.log("=" * 60);
    console.log("If you see 'Enhanced validation rules working' above,");
    console.log("then the deployment was successful!");
    console.log("\n🚀 You can now test on production frontend:");
    console.log("https://closetgpt-frontend.vercel.app");
}

main().catch(console.error);
