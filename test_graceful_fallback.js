const axios = require('axios');

async function testGracefulFallback() {
    console.log('🧪 Testing Graceful Fallback System...\n');
    
    const testCases = [
        {
            name: "Loungewear + Classic + Romantic",
            occasion: "Loungewear",
            style: "Classic", 
            mood: "Romantic",
            expectedFallback: "Should fallback to athleisure/casual items"
        },
        {
            name: "Business + Formal + Confident",
            occasion: "Business",
            style: "Formal",
            mood: "Confident", 
            expectedFallback: "Should work with business items"
        },
        {
            name: "Athleisure + Modern + Energetic",
            occasion: "Athleisure",
            style: "Modern",
            mood: "Energetic",
            expectedFallback: "Should work with athleisure items"
        }
    ];
    
    for (const testCase of testCases) {
        console.log(`\n📋 Testing: ${testCase.name}`);
        console.log(`Expected: ${testCase.expectedFallback}`);
        
        try {
            const response = await axios.post('https://closetgpt-backend-production.up.railway.app/api/outfit/generate', {
                occasion: testCase.occasion,
                style: testCase.style,
                mood: testCase.mood,
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
                timeout: 10000
            });
            
            const outfit = response.data.outfit;
            const items = outfit.items || [];
            
            console.log(`✅ Generated ${items.length} items:`);
            
            // Analyze the outfit
            const categories = {};
            const itemTypes = [];
            const colors = [];
            
            items.forEach(item => {
                const type = item.type || 'unknown';
                const color = item.color || 'unknown';
                
                categories[type] = (categories[type] || 0) + 1;
                itemTypes.push(`${item.name} (${type})`);
                colors.push(color);
            });
            
            console.log(`📊 Categories:`, categories);
            console.log(`🎨 Colors:`, colors.slice(0, 3).join(', '));
            console.log(`📝 Items:`, itemTypes.slice(0, 3).join(', '));
            
            // Check for issues
            const issues = [];
            
            // Check for multiple shoes
            if (categories.shoes > 1) {
                issues.push(`Multiple shoes (${categories.shoes})`);
            }
            
            // Check for multiple accessories
            if (categories.accessory > 2) {
                issues.push(`Too many accessories (${categories.accessory})`);
            }
            
            // Check for too many tops
            if ((categories.shirt || 0) + (categories.sweater || 0) + (categories['t-shirt'] || 0) > 3) {
                issues.push(`Too many tops`);
            }
            
            // Check for inappropriate combinations
            const hasBlazer = items.some(item => 
                item.name.toLowerCase().includes('blazer') || 
                item.type.toLowerCase().includes('blazer')
            );
            const hasShorts = items.some(item => 
                item.name.toLowerCase().includes('shorts') || 
                item.type.toLowerCase().includes('shorts')
            );
            
            if (hasBlazer && hasShorts) {
                issues.push('Blazer + Shorts (inappropriate)');
            }
            
            // Check for inappropriate occasion matching
            const hasFormalShoes = items.some(item => 
                (item.name.toLowerCase().includes('oxford') || 
                 item.name.toLowerCase().includes('dress shoes') ||
                 item.name.toLowerCase().includes('heels')) &&
                (testCase.occasion.toLowerCase().includes('loungewear') ||
                 testCase.occasion.toLowerCase().includes('athleisure'))
            );
            
            if (hasFormalShoes) {
                issues.push('Formal shoes with casual occasion');
            }
            
            if (issues.length > 0) {
                console.log(`❌ Issues found:`, issues);
            } else {
                console.log(`✅ No major issues detected`);
            }
            
            // Check if graceful fallback worked
            const isAppropriateForOccasion = items.every(item => {
                const itemName = item.name.toLowerCase();
                const itemType = item.type.toLowerCase();
                const occasion = testCase.occasion.toLowerCase();
                
                // Check if items are appropriate for the occasion
                if (occasion === 'loungewear') {
                    return !itemName.includes('oxford') && 
                           !itemName.includes('dress shoes') &&
                           !itemName.includes('pleated skirt') &&
                           !itemName.includes('formal');
                }
                
                return true; // For other occasions, assume appropriate
            });
            
            if (isAppropriateForOccasion) {
                console.log(`✅ Items appear appropriate for ${testCase.occasion}`);
            } else {
                console.log(`⚠️ Some items may not be appropriate for ${testCase.occasion}`);
            }
            
        } catch (error) {
            console.log(`❌ Error:`, error.response?.data?.detail || error.message);
        }
    }
    
    console.log('\n🏁 Graceful Fallback Test Complete!');
}

testGracefulFallback().catch(console.error);
