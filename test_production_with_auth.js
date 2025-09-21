#!/usr/bin/env node
/**
 * Production Test with Authentication
 * Tests enhanced validation rules with proper authentication
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

async function testWithAuth() {
    console.log("🧪 Testing Enhanced Validation Rules with Authentication");
    console.log("=" * 60);
    
    // Test with authentication header
    const testRequest = {
        occasion: "business",
        wardrobe: [
            { id: "1", name: "Navy Blazer", type: "blazer", color: "navy" },
            { id: "2", name: "Athletic Shorts", type: "athletic shorts", color: "black" },
            { id: "3", name: "White Sneakers", type: "sneakers", color: "white" },
            { id: "4", name: "Dress Shirt", type: "dress shirt", color: "white" },
            { id: "5", name: "Dress Pants", type: "dress pants", color: "black" }
        ],
        weather: { temperature: 70, condition: "clear" },
        userProfile: { id: "test_user" },
        style: "business"
    };
    
    try {
        console.log("🎯 Testing Business Outfit Generation with Auth...");
        console.log("Input: Blazer + Athletic Shorts + Sneakers (should be filtered)");
        
        const response = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test', // Test token
                'Content-Length': Buffer.byteLength(JSON.stringify(testRequest))
            },
            body: JSON.stringify(testRequest)
        });
        
        if (response.status === 200) {
            console.log("✅ Backend responded successfully with authentication");
            
            if (response.data && response.data.items) {
                const items = response.data.items;
                
                console.log(`\n📋 Generated Outfit (${items.length} items):`);
                items.forEach(item => console.log(`   - ${item.name} (${item.type})`));
                
                // Check for enhanced validation
                const hasBlazer = items.some(item => item.type === "blazer");
                const hasAthleticShorts = items.some(item => item.type === "athletic shorts");
                const hasSneakers = items.some(item => item.type === "sneakers");
                const hasDressShirt = items.some(item => item.type === "dress shirt");
                
                console.log("\n🔍 Enhanced Validation Analysis:");
                
                if (hasBlazer && hasAthleticShorts) {
                    console.log("❌ ENHANCED VALIDATION FAILED: Blazer with athletic shorts");
                } else {
                    console.log("✅ ENHANCED VALIDATION WORKING: No blazer with athletic shorts");
                }
                
                if (hasBlazer && hasSneakers) {
                    console.log("❌ ENHANCED VALIDATION FAILED: Blazer with sneakers");
                } else {
                    console.log("✅ ENHANCED VALIDATION WORKING: No blazer with sneakers");
                }
                
                if (hasAthleticShorts && hasSneakers) {
                    console.log("⚠️  Athletic shorts with sneakers (acceptable for some occasions)");
                }
                
                // Check business appropriateness
                if (hasBlazer && hasDressShirt) {
                    console.log("✅ BUSINESS APPROPRIATE: Blazer with dress shirt");
                }
                
                // Overall assessment
                const inappropriateCombinations = [];
                if (hasBlazer && hasAthleticShorts) inappropriateCombinations.push("blazer + athletic shorts");
                if (hasBlazer && hasSneakers) inappropriateCombinations.push("blazer + sneakers");
                
                if (inappropriateCombinations.length === 0) {
                    console.log("\n🎉 SUCCESS: Enhanced validation rules are working in production!");
                    console.log("✅ No inappropriate combinations detected");
                } else {
                    console.log("\n❌ ISSUES: Enhanced validation may need adjustment");
                    console.log("❌ Inappropriate combinations:", inappropriateCombinations.join(", "));
                }
                
            } else {
                console.log("⚠️  No outfit items in response");
                console.log("Response:", JSON.stringify(response.data, null, 2));
            }
            
        } else if (response.status === 403) {
            console.log("❌ Authentication failed - trying different approach");
            
            // Try without auth header but with user in request
            const requestWithUser = {
                ...testRequest,
                userId: "test-user-id"
            };
            
            const response2 = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(JSON.stringify(requestWithUser))
                },
                body: JSON.stringify(requestWithUser)
            });
            
            if (response2.status === 200) {
                console.log("✅ Backend responded with user ID in request");
                console.log("Response:", JSON.stringify(response2.data, null, 2));
            } else {
                console.log(`❌ Still getting error: ${response2.status}`);
                console.log("Response:", JSON.stringify(response2.data, null, 2));
            }
            
        } else {
            console.log(`❌ Backend error: ${response.status}`);
            console.log("Response:", JSON.stringify(response.data, null, 2));
        }
        
    } catch (error) {
        console.log(`❌ Request failed: ${error.message}`);
    }
}

async function main() {
    await testWithAuth();
    
    console.log("\n🎊 PRODUCTION TEST COMPLETE");
    console.log("=" * 60);
    console.log("If you see 'Enhanced validation rules are working' above,");
    console.log("then the deployment was successful!");
    console.log("\n🚀 You can now test on production frontend:");
    console.log("https://closetgpt-frontend.vercel.app");
    console.log("\n📋 Manual Testing Steps:");
    console.log("1. Go to https://closetgpt-frontend.vercel.app");
    console.log("2. Navigate to outfit generation");
    console.log("3. Select 'Business' occasion");
    console.log("4. Generate outfit");
    console.log("5. Look for NO blazer + shorts combinations!");
}

main().catch(console.error);
