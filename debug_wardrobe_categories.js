#!/usr/bin/env node
/**
 * Debug Wardrobe Categories
 * Check what types of items are in the wardrobe
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

async function debugWardrobeCategories() {
    console.log("🔍 Debugging Wardrobe Categories");
    console.log("=" * 50);
    
    try {
        // Get wardrobe data
        const response = await makeRequest(`${BACKEND_URL}/api/wardrobe`, {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer test'
            }
        });
        
        if (response.status === 200 && response.data && response.data.items) {
            const items = response.data.items;
            console.log(`📊 Total wardrobe items: ${items.length}`);
            
            // Categorize items by type
            const categories = {
                "tops": [],
                "bottoms": [],
                "shoes": [],
                "accessories": [],
                "other": []
            };
            
            items.forEach(item => {
                const type = (item.type || '').toLowerCase();
                const name = (item.name || '').toLowerCase();
                
                if (type.includes('shirt') || type.includes('blouse') || type.includes('sweater') || 
                    type.includes('jacket') || type.includes('coat') || name.includes('shirt') ||
                    name.includes('sweater') || name.includes('jacket')) {
                    categories.tops.push(item);
                } else if (type.includes('pants') || type.includes('jeans') || type.includes('shorts') || 
                           type.includes('skirt') || name.includes('pants') || name.includes('jeans') ||
                           name.includes('shorts') || name.includes('skirt')) {
                    categories.bottoms.push(item);
                } else if (type.includes('shoes') || type.includes('sneakers') || type.includes('boots') ||
                           name.includes('shoes') || name.includes('sneakers') || name.includes('boots')) {
                    categories.shoes.push(item);
                } else if (type.includes('belt') || type.includes('accessory') || name.includes('belt')) {
                    categories.accessories.push(item);
                } else {
                    categories.other.push(item);
                }
            });
            
            console.log("\n📋 Wardrobe Categories:");
            console.log(`👕 Tops: ${categories.tops.length} items`);
            console.log(`👖 Bottoms: ${categories.bottoms.length} items`);
            console.log(`👟 Shoes: ${categories.shoes.length} items`);
            console.log(`🎒 Accessories: ${categories.accessories.length} items`);
            console.log(`❓ Other: ${categories.other.length} items`);
            
            // Show sample items from each category
            console.log("\n🔍 Sample Items:");
            
            if (categories.bottoms.length > 0) {
                console.log("\n👖 Sample Bottoms:");
                categories.bottoms.slice(0, 5).forEach(item => {
                    console.log(`   - ${item.name} (${item.type})`);
                });
            } else {
                console.log("\n❌ NO BOTTOMS FOUND!");
            }
            
            if (categories.tops.length > 0) {
                console.log("\n👕 Sample Tops:");
                categories.tops.slice(0, 5).forEach(item => {
                    console.log(`   - ${item.name} (${item.type})`);
                });
            }
            
            if (categories.shoes.length > 0) {
                console.log("\n👟 Sample Shoes:");
                categories.shoes.slice(0, 5).forEach(item => {
                    console.log(`   - ${item.name} (${item.type})`);
                });
            }
            
            // Show some "other" items to see what's not being categorized
            if (categories.other.length > 0) {
                console.log("\n❓ Sample Other Items (not categorized):");
                categories.other.slice(0, 10).forEach(item => {
                    console.log(`   - ${item.name} (${item.type})`);
                });
            }
            
            // Analysis
            console.log("\n🎯 ANALYSIS:");
            if (categories.bottoms.length === 0) {
                console.log("❌ CRITICAL ISSUE: No bottoms found in wardrobe!");
                console.log("   This explains why outfits have no pants/shorts.");
                console.log("   Check if pants are stored with different type names.");
            } else if (categories.bottoms.length < 5) {
                console.log("⚠️  WARNING: Very few bottoms in wardrobe");
                console.log("   This might limit outfit generation options.");
            } else {
                console.log("✅ Good variety of bottoms available");
            }
            
        } else {
            console.log(`❌ Failed to get wardrobe data: ${response.status}`);
            console.log("Response:", JSON.stringify(response.data, null, 2));
        }
        
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }
}

debugWardrobeCategories().catch(console.error);
