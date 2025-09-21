#!/usr/bin/env node
/**
 * BACKEND HEALTH CHECK
 * Simple test to check if the backend is responding
 */

const https = require('https');

const BACKEND_URL = 'https://closetgptrenew-backend-production.up.railway.app';

async function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const requestOptions = {
            method: options.method || 'GET',
            headers: options.headers || {}
        };
        
        const req = https.request(url, requestOptions, (res) => {
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

async function testBackendHealth() {
    console.log("🏥 BACKEND HEALTH CHECK");
    console.log("=" * 50);
    
    try {
        // Test basic endpoint
        console.log("Testing basic endpoint...");
        const response = await makeRequest(`${BACKEND_URL}/`);
        console.log(`Status: ${response.status}`);
        console.log(`Response: ${JSON.stringify(response.data).substring(0, 200)}...`);
        
        // Test a simple outfit generation with minimal data
        console.log("\nTesting simple outfit generation...");
        const simpleRequest = {
            occasion: "casual",
            wardrobe: [
                { 
                    id: "1", 
                    name: "Blue Jeans", 
                    type: "jeans", 
                    color: "blue"
                },
                { 
                    id: "2", 
                    name: "White T-Shirt", 
                    type: "t-shirt", 
                    color: "white"
                },
                { 
                    id: "3", 
                    name: "Black Sneakers", 
                    type: "sneakers", 
                    color: "black"
                }
            ],
            userProfile: { id: "test_user" },
            style: "casual",
            mood: "confident"
        };
        
        const outfitResponse = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test'
            },
            body: JSON.stringify(simpleRequest)
        });
        
        console.log(`Outfit Generation Status: ${outfitResponse.status}`);
        if (outfitResponse.status === 200) {
            console.log(`✅ Backend is working! Generated outfit: ${outfitResponse.data.name}`);
            console.log(`Items: ${outfitResponse.data.items.length}`);
        } else {
            console.log(`❌ Backend error: ${JSON.stringify(outfitResponse.data).substring(0, 300)}`);
        }
        
    } catch (error) {
        console.log(`❌ Connection error: ${error.message}`);
    }
}

testBackendHealth().catch(console.error);
