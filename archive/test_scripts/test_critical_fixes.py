#!/usr/bin/env python3
"""
Test Critical Fixes for Outfit Generation

Tests the specific scenarios that were failing in the stress test:
1. 70°F temperature threshold (universal failure point)
2. Mood filtering (0% success rate)
3. User profile filtering (8.3% success rate)
"""

import requests
import json
import sys
import os

# Add backend to path for imports
sys.path.append('backend/src')

def test_critical_fixes():
    """Test the critical fixes for previously failing scenarios"""
    
    # Import the wardrobe preprocessor
    try:
        from services.wardrobe_preprocessor import wardrobe_preprocessor
        print("✅ Wardrobe preprocessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wardrobe preprocessor: {e}")
        return
    
    url = 'https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate'
    headers = {'Authorization': 'Bearer test', 'Content-Type': 'application/json'}
    
    # Simple test wardrobe
    test_wardrobe = [
        {
            'id': 'shirt_white',
            'name': 'White Cotton T-Shirt',
            'type': 'shirt',
            'color': 'White',
            'brand': 'Uniqlo',
            'occasion': ['casual', 'everyday'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'minimalist'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [65, 95],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': True,
            'usage_count': 40,
            'wearCount': 35
        },
        {
            'id': 'pants_jeans',
            'name': 'Dark Blue Jeans',
            'type': 'pants',
            'color': 'Dark Blue',
            'brand': 'Levi\'s',
            'occasion': ['casual', 'everyday'],
            'season': ['spring', 'summer', 'fall', 'winter'],
            'style': ['casual', 'classic'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [50, 85],
            'weather_conditions': ['clear', 'cloudy'],
            'favorite': True,
            'usage_count': 45,
            'wearCount': 40
        },
        {
            'id': 'shoes_sneakers',
            'name': 'White Sneakers',
            'type': 'shoes',
            'color': 'White',
            'brand': 'Nike',
            'occasion': ['casual', 'athletic', 'everyday'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'athletic'],
            'mood': ['relaxed', 'comfortable'],
            'temperature_range': [50, 90],
            'weather_conditions': ['clear', 'sunny'],
            'favorite': True,
            'usage_count': 50,
            'wearCount': 45
        }
    ]
    
    # Preprocess the test wardrobe
    print("🔄 PREPROCESSING: Converting test wardrobe")
    preprocessed_wardrobe = wardrobe_preprocessor.preprocess_wardrobe(test_wardrobe)
    print(f"✅ PREPROCESSING SUCCESSFUL: {len(preprocessed_wardrobe)} items")
    
    # Test scenarios that were previously failing
    critical_test_scenarios = [
        # 1. 70°F Temperature Threshold (was universal failure)
        {
            'name': 'CRITICAL: 70°F Temperature Test',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'comfortable',
            'weather': {'temperature': 70, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'expected_success': True
        },
        
        # 2. Mood Filtering Tests (was 0% success rate)
        {
            'name': 'CRITICAL: Professional Mood Test',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'professional',
            'weather': {'temperature': 70, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'expected_success': True
        },
        {
            'name': 'CRITICAL: Relaxed Mood Test',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'relaxed',
            'weather': {'temperature': 70, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'expected_success': True
        },
        {
            'name': 'CRITICAL: Comfortable Mood Test',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'comfortable',
            'weather': {'temperature': 70, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'expected_success': True
        },
        
        # 3. User Profile Tests (was 8.3% success rate)
        {
            'name': 'CRITICAL: Petite Body Type Test',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'comfortable',
            'weather': {'temperature': 70, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Petite', 'height': 'Short', 'weight': 'Light'},
            'expected_success': True
        },
        {
            'name': 'CRITICAL: Athletic Body Type Test',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'comfortable',
            'weather': {'temperature': 70, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Athletic', 'height': 'Average', 'weight': 'Average'},
            'expected_success': True
        },
        
        # 4. Temperature Range Tests
        {
            'name': 'CRITICAL: 75°F Test (boundary)',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'comfortable',
            'weather': {'temperature': 75, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'expected_success': True
        },
        {
            'name': 'CRITICAL: 80°F Test (hot weather)',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'comfortable',
            'weather': {'temperature': 80, 'condition': 'clear'},
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'expected_success': True
        },
        
        # 5. Edge Cases
        {
            'name': 'CRITICAL: Missing Weather Data',
            'occasion': 'casual',
            'style': 'casual',
            'mood': 'comfortable',
            'weather': None,
            'user_profile': {'bodyType': 'Average', 'height': 'Average', 'weight': 'Average', 'gender': 'Unspecified', 'skinTone': 'Medium'},
            'expected_success': True
        }
    ]
    
    print("\\n🚀 TESTING CRITICAL FIXES")
    print("=" * 80)
    
    results = []
    
    for i, scenario in enumerate(critical_test_scenarios, 1):
        print(f"\\n🧪 SCENARIO {i}/{len(critical_test_scenarios)}: {scenario['name']}")
        print(f"📋 Config: {scenario['occasion']} + {scenario['style']} + {scenario['mood']}")
        if scenario['weather']:
            print(f"📋 Weather: {scenario['weather']['temperature']}°F, {scenario['weather']['condition']}")
        else:
            print(f"📋 Weather: None")
        
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
                strategy = result.get('metadata', {}).get('generation_strategy', 'unknown')
                
                print(f"✅ SUCCESS")
                print(f"   Strategy: {strategy}")
                print(f"   Items: {len(outfit_items)}")
                
                # Show generated outfit
                for j, item in enumerate(outfit_items, 1):
                    print(f"   {j}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                
                results.append({
                    'scenario': scenario['name'],
                    'success': True,
                    'expected_success': scenario['expected_success'],
                    'strategy': strategy,
                    'items_count': len(outfit_items),
                    'error': None
                })
                
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"   Error: {response.text}")
                
                results.append({
                    'scenario': scenario['name'],
                    'success': False,
                    'expected_success': scenario['expected_success'],
                    'strategy': None,
                    'items_count': 0,
                    'error': f"HTTP {response.status_code}: {response.text}"
                })
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append({
                'scenario': scenario['name'],
                'success': False,
                'expected_success': scenario['expected_success'],
                'strategy': None,
                'items_count': 0,
                'error': str(e)
            })
    
    # Analysis
    print("\\n" + "=" * 80)
    print("📊 CRITICAL FIXES TEST RESULTS")
    print("=" * 80)
    
    total_tests = len(results)
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"📊 Total Scenarios: {total_tests}")
    print(f"✅ Successful: {len(successful_tests)}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"📈 Success Rate: {len(successful_tests)/total_tests*100:.1f}%")
    
    # Expected vs Actual
    expected_successful = [r for r in results if r['expected_success']]
    actually_successful = [r for r in expected_successful if r['success']]
    
    print(f"\\n🎯 EXPECTED vs ACTUAL:")
    print(f"Expected to succeed: {len(expected_successful)}")
    print(f"Actually succeeded: {len(actually_successful)}")
    print(f"Expectation accuracy: {len(actually_successful)/len(expected_successful)*100:.1f}%")
    
    # Category breakdown
    print(f"\\n📊 CATEGORY BREAKDOWN:")
    categories = {
        '70°F Temperature': [r for r in results if '70°F' in r['scenario']],
        'Mood Filtering': [r for r in results if 'Mood Test' in r['scenario']],
        'User Profiles': [r for r in results if 'Body Type Test' in r['scenario']],
        'Temperature Range': [r for r in results if '75°F' in r['scenario'] or '80°F' in r['scenario']],
        'Edge Cases': [r for r in results if 'Missing Weather' in r['scenario']]
    }
    
    for category, category_results in categories.items():
        if category_results:
            success_count = len([r for r in category_results if r['success']])
            print(f"   {category}: {success_count}/{len(category_results)} ({success_count/len(category_results)*100:.1f}%)")
    
    # Show failures
    if failed_tests:
        print(f"\\n❌ FAILURES:")
        for result in failed_tests:
            print(f"   • {result['scenario']}: {result['error']}")
    
    return results

if __name__ == "__main__":
    test_critical_fixes()



