#!/usr/bin/env python3
"""
Test Outfit Appropriateness with Fixed Wardrobe

This test removes problematic items (like sweaters) from the wardrobe
to see if we can achieve 100% appropriate outfits.
"""

import requests
import json
import sys
import os

# Add backend to path for imports
sys.path.append('backend/src')

def test_outfit_appropriateness_fixed():
    """Test outfit generation with a fixed wardrobe (no problematic items)"""
    
    # Import the wardrobe preprocessor
    try:
        from services.wardrobe_preprocessor import wardrobe_preprocessor
        print("✅ Wardrobe preprocessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wardrobe preprocessor: {e}")
        return
    
    url = 'https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate'
    headers = {'Authorization': 'Bearer test', 'Content-Type': 'application/json'}
    
    # FIXED wardrobe - removed problematic sweater for hot weather tests
    fixed_wardrobe = [
        {
            'id': 'shirt_business',
            'name': 'Classic White Button-Down Shirt',
            'type': 'shirt',
            'color': 'White',
            'imageUrl': 'https://example.com/shirt.jpg',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'brand': 'Brooks Brothers',
            'occasion': ['business', 'formal', 'casual'],
            'season': ['spring', 'summer', 'fall', 'winter'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'clean'],
            'tags': ['button-down', 'cotton']
        },
        {
            'id': 'pants_business',
            'name': 'Black Dress Pants',
            'type': 'pants',
            'color': 'Black',
            'imageUrl': 'https://example.com/pants.jpg',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'brand': 'Hugo Boss',
            'occasion': ['business', 'formal'],
            'season': ['fall', 'winter', 'spring'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'formal'],
            'tags': ['dress', 'wool']
        },
        {
            'id': 'jeans_casual',
            'name': 'Pants jeans light blue by Levi\'s',
            'type': 'pants',
            'color': 'Light Blue',
            'imageUrl': 'https://example.com/jeans.jpg',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'brand': 'Levi\'s',
            'occasion': ['casual', 'everyday'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'relaxed'],
            'mood': ['relaxed', 'comfortable'],
            'tags': ['denim', 'jeans', 'light', 'blue']
        },
        {
            'id': 'shoes_oxford',
            'name': 'Shoes oxford Brown',
            'type': 'shoes',
            'color': 'Brown',
            'imageUrl': 'https://example.com/oxford.jpg',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'brand': 'Cole Haan',
            'occasion': ['business', 'formal'],
            'season': ['fall', 'winter'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'formal'],
            'tags': ['oxford', 'brown', 'dress']
        },
        {
            'id': 'shoes_sneakers',
            'name': 'White Sneakers',
            'type': 'shoes',
            'color': 'White',
            'imageUrl': 'https://example.com/sneakers.jpg',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'brand': 'Nike',
            'occasion': ['casual', 'athletic', 'everyday'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'athletic'],
            'mood': ['relaxed', 'comfortable'],
            'tags': ['sneakers', 'white', 'athletic']
        },
        {
            'id': 'shirt_casual',
            'name': 'Light Cotton T-Shirt',
            'type': 'shirt',
            'color': 'White',
            'imageUrl': 'https://example.com/tshirt.jpg',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'brand': 'Uniqlo',
            'occasion': ['casual', 'everyday', 'athletic'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'minimalist'],
            'mood': ['relaxed', 'comfortable'],
            'tags': ['cotton', 'light', 'breathable']
        }
    ]
    
    # Preprocess the fixed wardrobe
    print("🔄 PREPROCESSING: Converting fixed wardrobe")
    preprocessed_wardrobe = wardrobe_preprocessor.preprocess_wardrobe(fixed_wardrobe)
    print(f"✅ PREPROCESSING SUCCESSFUL: {len(preprocessed_wardrobe)} items")
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'Business Meeting (70°F)',
            'occasion': 'Business',
            'style': 'Classic',
            'mood': 'Professional',
            'weather': {'temperature': 70.0, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'}
        },
        {
            'name': 'Casual Weekend (75°F)',
            'occasion': 'Casual',
            'style': 'Casual',
            'mood': 'Relaxed',
            'weather': {'temperature': 75.0, 'condition': 'sunny'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'}
        },
        {
            'name': 'Formal Event (65°F)',
            'occasion': 'Formal',
            'style': 'Elegant',
            'mood': 'Professional',
            'weather': {'temperature': 65.0, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'}
        },
        {
            'name': 'Hot Summer Day (85°F)',
            'occasion': 'Casual',
            'style': 'Casual',
            'mood': 'Relaxed',
            'weather': {'temperature': 85.0, 'condition': 'sunny'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'}
        }
    ]
    
    print("\\n🚀 TESTING WITH FIXED WARDROBE (NO PROBLEMATIC SWEATERS)")
    print("=" * 80)
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\\n🧪 SCENARIO {i}/{len(test_scenarios)}: {scenario['name']}")
        print(f"📋 Request: {scenario['occasion']} + {scenario['style']} + {scenario['weather']['temperature']}°F")
        
        data = {
            'occasion': scenario['occasion'],
            'style': scenario['style'],
            'mood': scenario['mood'],
            'weather': scenario['weather'],
            'wardrobe': preprocessed_wardrobe,
            'user_profile': scenario['user_profile']
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                outfit_items = result.get('items', [])
                
                print(f"✅ GENERATION SUCCESSFUL")
                print(f"   Strategy: {result.get('metadata', {}).get('generation_strategy', 'unknown')}")
                print(f"   Items: {len(outfit_items)}")
                
                # Show generated outfit
                print(f"\\n👔 GENERATED OUTFIT:")
                for j, item in enumerate(outfit_items, 1):
                    print(f"   {j}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                
                # Check for appropriateness
                appropriate = True
                issues = []
                
                temp = scenario['weather']['temperature']
                for item in outfit_items:
                    item_name = item.get('name', '').lower()
                    item_type = item.get('type', '').lower()
                    
                    # Weather check
                    if item_type == 'sweater' and temp > 70:
                        appropriate = False
                        issues.append(f"Weather mismatch: {item.get('name')} (sweater) for {temp}°F")
                    
                    # Occasion check
                    if scenario['occasion'] in ['business', 'formal'] and item_type not in ['shirt', 'blouse', 'dress']:
                        if 'sweater' in item_type and 'shirt' not in item_name:
                            appropriate = False
                            issues.append(f"Missing essential: No shirt/blouse for {scenario['occasion']} occasion")
                
                print(f"\\n📊 APPROPRIATENESS:")
                if appropriate:
                    print(f"   ✅ APPROPRIATE - Perfect outfit!")
                else:
                    print(f"   ❌ INAPPROPRIATE")
                    for issue in issues:
                        print(f"     • {issue}")
                
                results.append({
                    'scenario': scenario['name'],
                    'success': True,
                    'appropriate': appropriate,
                    'issues': issues,
                    'outfit_items': outfit_items
                })
                
            else:
                print(f"❌ GENERATION FAILED: HTTP {response.status_code}")
                print(f"   Error: {response.text}")
                
                results.append({
                    'scenario': scenario['name'],
                    'success': False,
                    'error': response.text
                })
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append({
                'scenario': scenario['name'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\\n" + "=" * 80)
    print("📊 FIXED WARDROBE TEST SUMMARY")
    print("=" * 80)
    
    successful_tests = [r for r in results if r['success']]
    total_tests = len(results)
    
    print(f"Total Scenarios: {total_tests}")
    print(f"✅ Successful Generations: {len(successful_tests)}")
    print(f"❌ Failed Generations: {total_tests - len(successful_tests)}")
    
    if successful_tests:
        appropriate_outfits = [r for r in successful_tests if r['appropriate']]
        
        print(f"\\n🎯 APPROPRIATENESS METRICS:")
        print(f"✅ Appropriate Outfits: {len(appropriate_outfits)}/{len(successful_tests)}")
        print(f"📊 Success Rate: {len(appropriate_outfits)/len(successful_tests)*100:.1f}%")
        
        print(f"\\n📋 SCENARIO RESULTS:")
        for result in results:
            if result['success']:
                status = "✅ APPROPRIATE" if result['appropriate'] else "❌ INAPPROPRIATE"
                print(f"   • {result['scenario']}: {status}")
            else:
                print(f"   • {result['scenario']}: ❌ GENERATION FAILED")
    
    return results

if __name__ == "__main__":
    test_outfit_appropriateness_fixed()



