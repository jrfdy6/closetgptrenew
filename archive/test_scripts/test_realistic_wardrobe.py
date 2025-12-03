#!/usr/bin/env python3
"""
Realistic Wardrobe Testing - Test with proper wardrobe structure
"""

import requests
import json
import time

def test_realistic_wardrobe():
    """Test outfit generation with realistic wardrobe data"""
    
    url = 'https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate'
    headers = {'Authorization': 'Bearer test', 'Content-Type': 'application/json'}
    
    # Realistic wardrobe with proper metadata structure
    realistic_wardrobe = [
        {
            'id': 'shirt_1',
            'name': 'Classic Blue Button-Down Shirt',
            'type': 'shirt',
            'color': 'Blue',
            'imageUrl': 'https://example.com/shirt1.jpg',
            'userId': 'test-user',
            'occasion': ['business', 'casual'],
            'style': ['classic', 'professional'],
            'tags': ['button-down', 'cotton']
        },
        {
            'id': 'pants_1',
            'name': 'Black Dress Pants',
            'type': 'pants',
            'color': 'Black',
            'imageUrl': 'https://example.com/pants1.jpg',
            'userId': 'test-user',
            'occasion': ['business', 'formal'],
            'style': ['classic', 'professional'],
            'tags': ['dress', 'wool']
        },
        {
            'id': 'shoes_1',
            'name': 'Black Oxford Shoes',
            'type': 'shoes',
            'color': 'Black',
            'imageUrl': 'https://example.com/shoes1.jpg',
            'userId': 'test-user',
            'occasion': ['business', 'formal'],
            'style': ['classic', 'professional'],
            'tags': ['oxford', 'leather']
        },
        {
            'id': 'jacket_1',
            'name': 'Gray Blazer',
            'type': 'jacket',
            'color': 'Gray',
            'imageUrl': 'https://example.com/jacket1.jpg',
            'userId': 'test-user',
            'occasion': ['business', 'formal'],
            'style': ['classic', 'professional'],
            'tags': ['blazer', 'wool']
        },
        {
            'id': 'casual_shirt',
            'name': 'White T-Shirt',
            'type': 'shirt',
            'color': 'White',
            'imageUrl': 'https://example.com/tshirt.jpg',
            'userId': 'test-user',
            'occasion': ['casual', 'athletic'],
            'style': ['casual', 'athletic'],
            'tags': ['cotton', 'basic']
        },
        {
            'id': 'jeans',
            'name': 'Blue Jeans',
            'type': 'pants',
            'color': 'Blue',
            'imageUrl': 'https://example.com/jeans.jpg',
            'userId': 'test-user',
            'occasion': ['casual', 'everyday'],
            'style': ['casual', 'relaxed'],
            'tags': ['denim', 'comfortable']
        },
        {
            'id': 'sneakers',
            'name': 'White Sneakers',
            'type': 'shoes',
            'color': 'White',
            'imageUrl': 'https://example.com/sneakers.jpg',
            'userId': 'test-user',
            'occasion': ['casual', 'athletic'],
            'style': ['casual', 'athletic'],
            'tags': ['sporty', 'comfortable']
        },
        {
            'id': 'party_dress',
            'name': 'Black Party Dress',
            'type': 'dress',
            'color': 'Black',
            'imageUrl': 'https://example.com/dress.jpg',
            'userId': 'test-user',
            'occasion': ['party', 'formal'],
            'style': ['elegant', 'trendy'],
            'tags': ['evening', 'sophisticated']
        }
    ]
    
    test_cases = [
        {
            'name': 'Business + Classic',
            'occasion': 'Business',
            'style': 'Classic',
            'mood': 'Bold',
            'weather': {'temperature': 70.0, 'condition': 'clear'},
            'user_profile': {
                'bodyType': 'Average',
                'height': 'Average',
                'weight': 'Average',
                'gender': 'Unspecified',
                'skinTone': 'Medium'
            }
        },
        {
            'name': 'Casual + Casual',
            'occasion': 'Casual',
            'style': 'Casual',
            'mood': 'Relaxed',
            'weather': {'temperature': 75.0, 'condition': 'sunny'},
            'user_profile': {
                'bodyType': 'Average',
                'height': 'Average',
                'weight': 'Average',
                'gender': 'Unspecified',
                'skinTone': 'Medium'
            }
        },
        {
            'name': 'Party + Elegant',
            'occasion': 'Party',
            'style': 'Elegant',
            'mood': 'Confident',
            'weather': {'temperature': 68.0, 'condition': 'clear'},
            'user_profile': {
                'bodyType': 'Hourglass',
                'height': '5\'4\" - 5\'7\"',
                'weight': '100-150 lbs',
                'gender': 'Female',
                'skinTone': 'Warm'
            }
        },
        {
            'name': 'Missing Weather Data',
            'occasion': 'Business',
            'style': 'Classic',
            'mood': 'Bold',
            'weather': None,  # Missing weather data
            'user_profile': {
                'bodyType': 'Average',
                'height': 'Average',
                'weight': 'Average',
                'gender': 'Unspecified',
                'skinTone': 'Medium'
            }
        },
        {
            'name': 'Empty User Profile',
            'occasion': 'Casual',
            'style': 'Casual',
            'mood': 'Relaxed',
            'weather': {'temperature': 70.0, 'condition': 'clear'},
            'user_profile': None  # Empty user profile
        }
    ]
    
    print("🚀 REALISTIC WARDROBE TESTING")
    print("=" * 60)
    print(f"Wardrobe: {len(realistic_wardrobe)} items")
    print(f"Test Cases: {len(test_cases)}")
    print("=" * 60)
    
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
            'wardrobe': realistic_wardrobe,
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
    print("\n" + "=" * 60)
    print("📊 REALISTIC WARDROBE TEST SUMMARY")
    print("=" * 60)
    
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
    test_realistic_wardrobe()



