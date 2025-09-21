const axios = require('axios');

async function testSimpleBackend() {
    console.log('🧪 Testing Simple Backend Connection...\n');
    
    try {
        // Test 1: Simple health check
        console.log('📋 Test 1: Health Check');
        const healthResponse = await axios.get('https://closetgpt-backend-production.up.railway.app/health', {
            timeout: 5000
        });
        console.log('✅ Health check passed:', healthResponse.status);
        
    } catch (error) {
        console.log('❌ Health check failed:', error.response?.status || error.message);
    }
    
    try {
        // Test 2: Simple outfit generation with minimal data
        console.log('\n📋 Test 2: Simple Outfit Generation');
        const response = await axios.post('https://closetgpt-backend-production.up.railway.app/api/outfit/generate', {
            occasion: "Casual",
            style: "Modern", 
            mood: "Confident",
            weather: {
                temperature: 70,
                condition: 'clear',
                humidity: 60,
                windSpeed: 5,
                precipitation: 0
            }
        }, {
            headers: {
                'Authorization': 'Bearer test_token_12345',
                'Content-Type': 'application/json'
            },
            timeout: 15000  // Increased timeout
        });
        
        console.log('✅ Outfit generation successful!');
        console.log('📊 Response status:', response.status);
        console.log('📊 Response data keys:', Object.keys(response.data));
        
        if (response.data.outfit) {
            const outfit = response.data.outfit;
            console.log('📊 Outfit items:', outfit.items?.length || 0);
            console.log('📊 Outfit name:', outfit.name || 'No name');
        }
        
    } catch (error) {
        console.log('❌ Outfit generation failed:');
        console.log('📊 Status:', error.response?.status);
        console.log('📊 Error:', error.response?.data?.detail || error.message);
        
        if (error.code === 'ECONNABORTED') {
            console.log('🚨 TIMEOUT: Backend is taking too long to respond');
        }
    }
    
    console.log('\n🏁 Simple Backend Test Complete!');
}

testSimpleBackend().catch(console.error);
