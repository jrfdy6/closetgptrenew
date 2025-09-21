#!/usr/bin/env node
/**
 * PRODUCTION 1000-OUTFIT TEST WITH ENHANCED VALIDATION
 * Test the enhanced item type matching system in production with proper rate limiting
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

function generateRandomWardrobe() {
    const itemTypes = [
        'shirt', 'blouse', 't-shirt', 'polo', 'sweater', 'hoodie', 'blazer', 'jacket',
        'pants', 'jeans', 'chinos', 'shorts', 'skirt', 'dress',
        'shoes', 'sneakers', 'boots', 'loafers', 'oxford', 'heels', 'sandals',
        'belt', 'watch', 'bag', 'accessory'
    ];
    
    const colors = [
        'black', 'white', 'blue', 'navy', 'red', 'green', 'brown', 'gray', 'pink', 'yellow', 'purple', 'orange',
        'beige', 'khaki', 'olive', 'burgundy', 'maroon', 'charcoal', 'ivory', 'cream'
    ];
    
    const materials = [
        'cotton', 'denim', 'wool', 'leather', 'silk', 'polyester', 'linen', 'canvas', 'cashmere', 'tweed'
    ];
    
    const patterns = [
        'solid', 'striped', 'polka dot', 'floral', 'plaid', 'paisley', 'checkered', 'geometric'
    ];
    
    const sleeveLengths = [
        'long sleeve', 'short sleeve', 'sleeveless'
    ];
    
    const fits = [
        'slim fit', 'loose fit', 'regular fit', 'relaxed fit', 'tailored'
    ];
    
    const brands = [
        'Nike', 'Adidas', 'Zara', 'H&M', 'Uniqlo', 'J.Crew', 'Gap', 'Banana Republic', 
        'Calvin Klein', 'Tommy Hilfiger', 'Ralph Lauren', 'Polo', 'Levi\'s'
    ];
    
    // Generate 50-100 random wardrobe items
    const wardrobeSize = Math.floor(Math.random() * 51) + 50; // 50-100 items
    const wardrobe = [];
    
    for (let i = 0; i < wardrobeSize; i++) {
        const itemType = itemTypes[Math.floor(Math.random() * itemTypes.length)];
        const color = colors[Math.floor(Math.random() * colors.length)];
        const material = materials[Math.floor(Math.random() * materials.length)];
        const pattern = patterns[Math.floor(Math.random() * patterns.length)];
        const sleeveLength = sleeveLengths[Math.floor(Math.random() * sleeveLengths.length)];
        const fit = fits[Math.floor(Math.random() * fits.length)];
        const brand = brands[Math.floor(Math.random() * brands.length)];
        
        const item = {
            id: `item_${i}`,
            name: `${color} ${material} ${pattern} ${itemType}`,
            type: itemType,
            color: color,
            brand: brand,
            style: ['casual', 'business', 'formal', 'athletic'][Math.floor(Math.random() * 4)],
            metadata: {
                visualAttributes: {
                    material: material,
                    pattern: pattern,
                    sleeveLength: sleeveLength,
                    fit: fit
                }
            },
            tags: [color, material, pattern, itemType, brand],
            wearCount: Math.floor(Math.random() * 20),
            favorite_score: Math.random() * 5
        };
        
        wardrobe.push(item);
    }
    
    return wardrobe;
}

function generateRandomRequest() {
    const occasions = [
        'casual', 'business', 'formal', 'athletic', 'evening', 'party', 'workout', 'date', 'meeting'
    ];
    
    const styles = [
        'casual', 'business', 'formal', 'athletic', 'streetwear', 'preppy', 'minimalist', 'bohemian'
    ];
    
    const moods = [
        'confident', 'comfortable', 'professional', 'creative', 'energetic', 'relaxed', 'sophisticated'
    ];
    
    return {
        occasion: occasions[Math.floor(Math.random() * occasions.length)],
        wardrobe: generateRandomWardrobe(),
        userProfile: { 
            id: "test_user",
            style: styles[Math.floor(Math.random() * styles.length)]
        },
        style: styles[Math.floor(Math.random() * styles.length)],
        mood: moods[Math.floor(Math.random() * moods.length)],
        weather: {
            temperature: Math.floor(Math.random() * 40) + 40, // 40-80°F
            condition: ['sunny', 'cloudy', 'rainy', 'snowy'][Math.floor(Math.random() * 4)],
            humidity: Math.floor(Math.random() * 100),
            windSpeed: Math.floor(Math.random() * 20),
            precipitation: Math.floor(Math.random() * 10)
        }
    };
}

function analyzeOutfit(outfit) {
    const analysis = {
        totalItems: outfit.items.length,
        hasBlazer: false,
        hasShorts: false,
        hasJeans: false,
        hasSneakers: false,
        hasOxford: false,
        hasDressShirt: false,
        hasTShirt: false,
        hasHoodie: false,
        categories: {
            tops: 0,
            bottoms: 0,
            shoes: 0,
            accessories: 0
        },
        inappropriateCombinations: [],
        missingCategories: [],
        categoryViolations: []
    };
    
    outfit.items.forEach(item => {
        const itemType = item.type.toLowerCase();
        const itemName = item.name.toLowerCase();
        
        // Check for specific item types
        if (itemType.includes('blazer') || itemName.includes('blazer')) {
            analysis.hasBlazer = true;
            analysis.categories.tops++;
        } else if (itemType.includes('shirt') || itemName.includes('shirt')) {
            if (itemName.includes('dress') || itemName.includes('button')) {
                analysis.hasDressShirt = true;
            } else if (itemType.includes('t-shirt') || itemName.includes('t-shirt')) {
                analysis.hasTShirt = true;
            }
            analysis.categories.tops++;
        } else if (itemType.includes('sweater') || itemName.includes('sweater') || 
                   itemType.includes('hoodie') || itemName.includes('hoodie')) {
            analysis.hasHoodie = true;
            analysis.categories.tops++;
        } else if (itemType.includes('pants') || itemName.includes('pants') || 
                   itemType.includes('chinos') || itemName.includes('chinos') ||
                   itemType.includes('trousers') || itemName.includes('trousers')) {
            analysis.categories.bottoms++;
        } else if (itemType.includes('jeans') || itemName.includes('jeans')) {
            analysis.hasJeans = true;
            analysis.categories.bottoms++;
        } else if (itemType.includes('shorts') || itemName.includes('shorts')) {
            analysis.hasShorts = true;
            analysis.categories.bottoms++;
        } else if (itemType.includes('shoes') || itemName.includes('shoes') ||
                   itemType.includes('sneakers') || itemName.includes('sneakers') ||
                   itemType.includes('boots') || itemName.includes('boots') ||
                   itemType.includes('loafers') || itemName.includes('loafers') ||
                   itemType.includes('oxford') || itemName.includes('oxford') ||
                   itemType.includes('heels') || itemName.includes('heels')) {
            if (itemType.includes('sneakers') || itemName.includes('sneakers')) {
                analysis.hasSneakers = true;
            } else if (itemType.includes('oxford') || itemName.includes('oxford') ||
                       itemType.includes('loafers') || itemName.includes('loafers')) {
                analysis.hasOxford = true;
            }
            analysis.categories.shoes++;
        } else if (itemType.includes('belt') || itemName.includes('belt') ||
                   itemType.includes('watch') || itemName.includes('watch') ||
                   itemType.includes('bag') || itemName.includes('bag')) {
            analysis.categories.accessories++;
        }
    });
    
    // Check for inappropriate combinations
    if (analysis.hasBlazer && analysis.hasShorts) {
        analysis.inappropriateCombinations.push('blazer_with_shorts');
    }
    
    if (analysis.hasBlazer && analysis.hasSneakers) {
        analysis.inappropriateCombinations.push('blazer_with_sneakers');
    }
    
    if (analysis.hasDressShirt && analysis.hasShorts) {
        analysis.inappropriateCombinations.push('dress_shirt_with_shorts');
    }
    
    if (analysis.hasOxford && analysis.hasShorts) {
        analysis.inappropriateCombinations.push('oxford_shoes_with_shorts');
    }
    
    if (analysis.hasOxford && analysis.hasTShirt) {
        analysis.inappropriateCombinations.push('oxford_shoes_with_t_shirt');
    }
    
    // Check for missing categories
    if (analysis.categories.tops === 0) {
        analysis.missingCategories.push('tops');
    }
    
    if (analysis.categories.bottoms === 0) {
        analysis.missingCategories.push('bottoms');
    }
    
    if (analysis.categories.shoes === 0) {
        analysis.missingCategories.push('shoes');
    }
    
    // Check for category violations
    if (analysis.categories.bottoms > 1) {
        analysis.categoryViolations.push(`multiple_bottoms_${analysis.categories.bottoms}`);
    }
    
    if (analysis.categories.shoes > 1) {
        analysis.categoryViolations.push(`multiple_shoes_${analysis.categories.shoes}`);
    }
    
    if (analysis.categories.tops > 3) {
        analysis.categoryViolations.push(`too_many_tops_${analysis.categories.tops}`);
    }
    
    // Check total item count
    if (analysis.totalItems < 3) {
        analysis.categoryViolations.push(`too_few_items_${analysis.totalItems}`);
    }
    
    if (analysis.totalItems > 6) {
        analysis.categoryViolations.push(`too_many_items_${analysis.totalItems}`);
    }
    
    return analysis;
}

async function test1000Outfits() {
    console.log("🎯 PRODUCTION 1000-OUTFIT TEST WITH ENHANCED VALIDATION");
    console.log("=" * 80);
    console.log("Testing enhanced item type matching in production with proper rate limiting...\n");
    
    const results = {
        total: 0,
        successful: 0,
        failed: 0,
        inappropriateCombinations: 0,
        missingCategories: 0,
        categoryViolations: 0,
        issues: {
            blazer_with_shorts: 0,
            blazer_with_sneakers: 0,
            dress_shirt_with_shorts: 0,
            oxford_shoes_with_shorts: 0,
            oxford_shoes_with_t_shirt: 0,
            multiple_bottoms: 0,
            multiple_shoes: 0,
            too_many_tops: 0,
            too_few_items: 0,
            too_many_items: 0,
            missing_tops: 0,
            missing_bottoms: 0,
            missing_shoes: 0
        },
        itemCountDistribution: {},
        categoryDistribution: {
            tops: [],
            bottoms: [],
            shoes: [],
            accessories: []
        }
    };
    
    const totalTests = 1000;
    
    for (let i = 0; i < totalTests; i++) {
        const testRequest = generateRandomRequest();
        
        try {
            const response = await makeRequest(`${BACKEND_URL}/api/outfits/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer test'
                },
                body: JSON.stringify(testRequest)
            });
            
            results.total++;
            
            if (response.status !== 200) {
                results.failed++;
                console.log(`   ❌ Test ${i + 1}: HTTP ${response.status}`);
                
                // If we get too many 500 errors, slow down
                if (response.status === 500 && i > 50 && results.failed / results.total > 0.5) {
                    console.log(`   ⏸️ Slowing down due to server errors...`);
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
                continue;
            }
            
            const analysis = analyzeOutfit(response.data);
            results.successful++;
            
            // Track item count distribution
            const itemCount = analysis.totalItems;
            results.itemCountDistribution[itemCount] = (results.itemCountDistribution[itemCount] || 0) + 1;
            
            // Track category distributions
            results.categoryDistribution.tops.push(analysis.categories.tops);
            results.categoryDistribution.bottoms.push(analysis.categories.bottoms);
            results.categoryDistribution.shoes.push(analysis.categories.shoes);
            results.categoryDistribution.accessories.push(analysis.categories.accessories);
            
            // Check for issues
            if (analysis.inappropriateCombinations.length > 0) {
                results.inappropriateCombinations++;
                analysis.inappropriateCombinations.forEach(combo => {
                    results.issues[combo] = (results.issues[combo] || 0) + 1;
                });
            }
            
            if (analysis.missingCategories.length > 0) {
                results.missingCategories++;
                analysis.missingCategories.forEach(category => {
                    results.issues[`missing_${category}`] = (results.issues[`missing_${category}`] || 0) + 1;
                });
            }
            
            if (analysis.categoryViolations.length > 0) {
                results.categoryViolations++;
                analysis.categoryViolations.forEach(violation => {
                    results.issues[violation] = (results.issues[violation] || 0) + 1;
                });
            }
            
            // Log progress every 50 tests
            if ((i + 1) % 50 === 0) {
                const successRate = Math.round((results.successful / results.total) * 100);
                const inappropriateRate = Math.round((results.inappropriateCombinations / results.total) * 100);
                const missingRate = Math.round((results.missingCategories / results.total) * 100);
                const violationRate = Math.round((results.categoryViolations / results.total) * 100);
                
                console.log(`   📊 Progress: ${i + 1}/${totalTests} | Success: ${successRate}% | Inappropriate: ${inappropriateRate}% | Missing: ${missingRate}% | Violations: ${violationRate}%`);
            }
            
        } catch (error) {
            results.total++;
            results.failed++;
            console.log(`   ❌ Test ${i + 1}: ERROR - ${error.message}`);
        }
        
        // Rate limiting: 1 request per second to avoid overwhelming production
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Calculate final statistics
    const successRate = Math.round((results.successful / results.total) * 100);
    const inappropriateRate = Math.round((results.inappropriateCombinations / results.total) * 100);
    const missingRate = Math.round((results.missingCategories / results.total) * 100);
    const violationRate = Math.round((results.categoryViolations / results.total) * 100);
    
    // Calculate category averages
    const avgTops = results.categoryDistribution.tops.length > 0 ? 
        Math.round(results.categoryDistribution.tops.reduce((a, b) => a + b, 0) / results.categoryDistribution.tops.length * 10) / 10 : 0;
    const avgBottoms = results.categoryDistribution.bottoms.length > 0 ? 
        Math.round(results.categoryDistribution.bottoms.reduce((a, b) => a + b, 0) / results.categoryDistribution.bottoms.length * 10) / 10 : 0;
    const avgShoes = results.categoryDistribution.shoes.length > 0 ? 
        Math.round(results.categoryDistribution.shoes.reduce((a, b) => a + b, 0) / results.categoryDistribution.shoes.length * 10) / 10 : 0;
    const avgAccessories = results.categoryDistribution.accessories.length > 0 ? 
        Math.round(results.categoryDistribution.accessories.reduce((a, b) => a + b, 0) / results.categoryDistribution.accessories.length * 10) / 10 : 0;
    
    // Final Results
    console.log("\n🏆 PRODUCTION 1000-OUTFIT TEST RESULTS");
    console.log("=" * 80);
    
    console.log(`📊 OVERALL STATISTICS:`);
    console.log(`   Total Tests: ${results.total}`);
    console.log(`   Successful: ${results.successful} (${successRate}%)`);
    console.log(`   Failed: ${results.failed} (${Math.round((results.failed / results.total) * 100)}%)`);
    
    console.log(`\n🎯 VALIDATION PERFORMANCE:`);
    console.log(`   Inappropriate Combinations: ${results.inappropriateCombinations} (${inappropriateRate}%)`);
    console.log(`   Missing Categories: ${results.missingCategories} (${missingRate}%)`);
    console.log(`   Category Violations: ${results.categoryViolations} (${violationRate}%)`);
    
    console.log(`\n📈 CATEGORY DISTRIBUTION:`);
    console.log(`   Average Tops: ${avgTops}`);
    console.log(`   Average Bottoms: ${avgBottoms}`);
    console.log(`   Average Shoes: ${avgShoes}`);
    console.log(`   Average Accessories: ${avgAccessories}`);
    
    console.log(`\n📊 ITEM COUNT DISTRIBUTION:`);
    Object.entries(results.itemCountDistribution)
        .sort(([a], [b]) => parseInt(a) - parseInt(b))
        .forEach(([count, frequency]) => {
            const percentage = Math.round((frequency / results.total) * 100);
            console.log(`   ${count} items: ${frequency} outfits (${percentage}%)`);
        });
    
    console.log(`\n❌ DETAILED ISSUE BREAKDOWN:`);
    Object.entries(results.issues)
        .filter(([issue, count]) => count > 0)
        .sort(([, a], [, b]) => b - a)
        .forEach(([issue, count]) => {
            const percentage = Math.round((count / results.total) * 100);
            console.log(`   ${issue}: ${count} occurrences (${percentage}%)`);
        });
    
    // Overall Assessment
    console.log(`\n🎯 OVERALL ASSESSMENT:`);
    
    if (inappropriateRate <= 1 && missingRate <= 1 && violationRate <= 5) {
        console.log(`🎉 EXCELLENT PERFORMANCE!`);
        console.log(`✅ Enhanced validation is working exceptionally well`);
        console.log(`✅ Inappropriate combinations: ${inappropriateRate}% (target: ≤1%)`);
        console.log(`✅ Missing categories: ${missingRate}% (target: ≤1%)`);
        console.log(`✅ Category violations: ${violationRate}% (target: ≤5%)`);
    } else if (inappropriateRate <= 5 && missingRate <= 5 && violationRate <= 10) {
        console.log(`✅ GOOD PERFORMANCE!`);
        console.log(`✅ Enhanced validation is working well with minor issues`);
        console.log(`⚠️ Inappropriate combinations: ${inappropriateRate}% (target: ≤1%)`);
        console.log(`⚠️ Missing categories: ${missingRate}% (target: ≤1%)`);
        console.log(`⚠️ Category violations: ${violationRate}% (target: ≤5%)`);
    } else {
        console.log(`⚠️ NEEDS IMPROVEMENT!`);
        console.log(`❌ Enhanced validation needs further refinement`);
        console.log(`❌ Inappropriate combinations: ${inappropriateRate}% (target: ≤1%)`);
        console.log(`❌ Missing categories: ${missingRate}% (target: ≤1%)`);
        console.log(`❌ Category violations: ${violationRate}% (target: ≤5%)`);
    }
    
    console.log(`\n🏁 Production 1000-outfit test completed!`);
    console.log(`⏱️ Total time: ~${Math.round(totalTests / 60)} minutes with 1-second rate limiting`);
}

test1000Outfits().catch(console.error);
