#!/usr/bin/env python3
"""
Test with Your Actual Complex Wardrobe Data Structure
"""

import requests
import json
import time

def test_with_real_wardrobe_structure():
    """Test outfit generation with your actual wardrobe data structure"""
    
    url = 'https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate'
    headers = {'Authorization': 'Bearer test', 'Content-Type': 'application/json'}
    
    # Your actual wardrobe structure based on the debug data
    real_wardrobe = [
        {
            'id': '006crwqcyyl7kmby62lrf',
            'name': 'A loose, short, textured, ribbed sweater by Abercrombie & Fitch',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'type': 'sweater',
            'color': 'Gray',
            'imageUrl': 'https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F006crwqcyyl7kmby62lrf.jpg',
            'brand': 'Abercrombie & Fitch',
            'occasion': ['casual', 'business'],
            'season': ['fall', 'winter'],
            'style': ['classic', 'preppy'],
            'mood': ['relaxed', 'professional'],
            'gender': 'Male',
            'matchingColors': ['Black', 'Navy', 'White'],
            'tags': ['ribbed', 'textured', 'loose', 'short'],
            'createdAt': '2024-01-01T00:00:00Z'
        },
        {
            'id': '009d5hmyg8dgmby6a7tf',
            'name': 'A woven, smooth shoes',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'type': 'shoes',
            'color': 'Brown',
            'imageUrl': 'https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F009d5hmyg8dgmby6a7tf.jpg',
            'brand': 'Unknown',
            'occasion': ['business', 'formal'],
            'season': ['fall', 'winter'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'formal'],
            'gender': 'Male',
            'matchingColors': ['Black', 'Navy', 'Gray'],
            'tags': ['woven', 'smooth', 'dress'],
            'createdAt': '2024-01-01T00:00:00Z'
        },
        {
            'id': '0100b030-8f95-4a50-82f7-7c02c7b745ba',
            'name': 'Pants jeans light blue by Levi\'s',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'type': 'pants',
            'color': 'Light Blue',
            'imageUrl': 'https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F0100b030-8f95-4a50-82f7-7c02c7b745ba.jpg',
            'brand': 'Levi\'s',
            'occasion': ['casual', 'everyday'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'relaxed'],
            'mood': ['relaxed', 'comfortable'],
            'gender': 'Male',
            'matchingColors': ['White', 'Gray', 'Navy'],
            'tags': ['denim', 'jeans', 'light', 'blue'],
            'createdAt': '2024-01-01T00:00:00Z'
        },
        {
            'id': '061126ed-9a3d-4989-be0a-8bea96a99d6d',
            'name': 'Shoes oxford Brown',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'type': 'shoes',
            'color': 'Brown',
            'imageUrl': 'https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F061126ed-9a3d-4989-be0a-8bea96a99d6d.jpg',
            'brand': 'Unknown',
            'occasion': ['business', 'formal'],
            'season': ['fall', 'winter'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'formal'],
            'gender': 'Male',
            'matchingColors': ['Black', 'Navy', 'Gray'],
            'tags': ['oxford', 'brown', 'dress'],
            'createdAt': '2024-01-01T00:00:00Z'
        },
        {
            'id': 'shirt_sample',
            'name': 'Classic White Button-Down Shirt',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'type': 'shirt',
            'color': 'White',
            'imageUrl': 'https://example.com/shirt.jpg',
            'brand': 'Brooks Brothers',
            'occasion': ['business', 'formal', 'casual'],
            'season': ['spring', 'summer', 'fall', 'winter'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'clean'],
            'gender': 'Male',
            'matchingColors': ['Black', 'Navy', 'Gray', 'Brown'],
            'tags': ['button-down', 'cotton', 'classic'],
            'createdAt': '2024-01-01T00:00:00Z'
        }
    ]
    
    test_cases = [
        {
            'name': 'Business + Classic (Your Real Data)',
            'occasion': 'Business',
            'style': 'Classic',
            'mood': 'Professional',
            'weather': {'temperature': 70.0, 'condition': 'clear'},
            'user_profile': {
                'bodyType': 'Average',
                'height': '5\'8\" - 5\'11\"',
                'weight': '150-200 lbs',
                'gender': 'Male',
                'skinTone': 'Medium'
            }
        },
        {
            'name': 'Casual + Relaxed (Your Real Data)',
            'occasion': 'Casual',
            'style': 'Casual',
            'mood': 'Relaxed',
            'weather': {'temperature': 75.0, 'condition': 'sunny'},
            'user_profile': {
                'bodyType': 'Average',
                'height': '5\'8\" - 5\'11\"',
                'weight': '150-200 lbs',
                'gender': 'Male',
                'skinTone': 'Medium'
            }
        },
        {
            'name': 'Missing Weather Data (Your Real Data)',
            'occasion': 'Business',
            'style': 'Classic',
            'mood': 'Professional',
            'weather': None,  # Missing weather data
            'user_profile': {
                'bodyType': 'Average',
                'height': '5\'8\" - 5\'11\"',
                'weight': '150-200 lbs',
                'gender': 'Male',
                'skinTone': 'Medium'
            }
        },
        {
            'name': 'Empty User Profile (Your Real Data)',
            'occasion': 'Casual',
            'style': 'Casual',
            'mood': 'Relaxed',
            'weather': {'temperature': 70.0, 'condition': 'clear'},
            'user_profile': None  # Empty user profile
        }
    ]
    
    print("🚀 TESTING WITH YOUR ACTUAL WARDROBE STRUCTURE")
    print("=" * 70)
    print(f"Wardrobe: {len(real_wardrobe)} items (based on your real data)")
    print(f"Test Cases: {len(test_cases)}")
    print("=" * 70)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}/{len(test_cases)}: {test_case['name']}")
        print(f"📋 Config: {test_case['occasion']} + {test_case['style']}")
        print(f"   Weather: {test_case['weather']}")
        print(f"   Profile: {test_case['user_profile']}")
        
        data = {
            'occasion': test_case['occasion'],
            'style': test_case['style'],
            'mood': test_case['mood'],
            'weather': test_case['weather'],
            'wardrobe': real_wardrobe,
            'user_profile': test_case['user_profile']
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                strategy = result.get('metadata', {}).get('generation_strategy', 'unknown')
                items = result.get('items', [])
                
                print(f"✅ SUCCESS")
                print(f"   Strategy: {strategy}")
                print(f"   Items: {len(items)}")
                for j, item in enumerate(items, 1):
                    print(f"   {j}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                
                results.append({
                    'test': test_case['name'],
                    'status': 'success',
                    'strategy': strategy,
                    'items': len(items)
                })
                
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"   Error: {response.text}")
                
                results.append({
                    'test': test_case['name'],
                    'status': 'failed',
                    'error': response.text
                })
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append({
                'test': test_case['name'],
                'status': 'exception',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 REAL WARDROBE STRUCTURE TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len(results)
    successful_tests = len([r for r in results if r['status'] == 'success'])
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Successful: {successful_tests}")
    print(f"❌ Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if successful_tests > 0:
        strategies = [r['strategy'] for r in results if r.get('strategy')]
        strategy_counts = {}
        for strategy in strategies:
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        print(f"\n🎯 Strategy Distribution:")
        for strategy, count in strategy_counts.items():
            print(f"   {strategy}: {count}")
    
    print(f"\n❌ Failed Tests:")
    for result in results:
        if result['status'] != 'success':
            print(f"   • {result['test']}: {result['status']}")
    
    return results

if __name__ == "__main__":
    test_with_real_wardrobe_structure()



