#!/usr/bin/env python3
"""
Test Complex Metadata with Wardrobe Preprocessor

This test uses the wardrobe preprocessor to convert your 28-field complex
metadata into the format the system expects, enabling sophisticated
personalization without breaking the core system.
"""

import requests
import json
import sys
import os

# Add backend to path for imports
sys.path.append('backend/src')

def test_complex_metadata_preprocessed():
    """Test outfit generation with preprocessed complex metadata"""
    
    # Import the wardrobe preprocessor
    try:
        from services.wardrobe_preprocessor import wardrobe_preprocessor
        print("✅ Wardrobe preprocessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wardrobe preprocessor: {e}")
        return
    
    url = 'https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate'
    headers = {'Authorization': 'Bearer test', 'Content-Type': 'application/json'}
    
    # Your FULL complex wardrobe structure with all 28 metadata fields
    complex_wardrobe = [
        {
            # Core fields
            'id': '006crwqcyyl7kmby62lrf',
            'name': 'A loose, short, textured, ribbed sweater by Abercrombie & Fitch',
            'type': 'sweater',
            'color': 'Gray',
            'imageUrl': 'https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F006crwqcyyl7kmby62lrf.jpg',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            
            # Complex metadata fields (all 28)
            'brand': 'Abercrombie & Fitch',
            'occasion': ['casual', 'business'],
            'season': ['fall', 'winter'],
            'style': ['classic', 'preppy'],
            'mood': ['relaxed', 'professional'],
            'gender': 'Male',
            'matchingColors': ['Black', 'Navy', 'White'],
            'dominantColors': ['Gray', 'Charcoal'],
            'colorName': 'Heather Gray',
            'tags': ['ribbed', 'textured', 'loose', 'short'],
            'subType': 'cardigan',
            'bodyTypeCompatibility': ['Average', 'Athletic', 'Slim'],
            'weatherCompatibility': ['cool', 'mild', 'cold'],
            'favorite': True,
            'usage_count': 15,
            'wearCount': 12,
            'lastWorn': '2024-01-15T10:30:00Z',
            'last_used_at': '2024-01-15T10:30:00Z',
            'createdAt': '2023-12-01T00:00:00Z',
            'updatedAt': '2024-01-15T10:30:00Z',
            'backgroundRemoved': True,
            'metadata': {
                'quality': 'high',
                'material': 'cotton-blend',
                'care_instructions': 'machine_wash'
            }
        },
        {
            # Core fields
            'id': '009d5hmyg8dgmby6a7tf',
            'name': 'A woven, smooth shoes',
            'type': 'shoes',
            'color': 'Brown',
            'imageUrl': 'https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F009d5hmyg8dgmby6a7tf.jpg',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            
            # Complex metadata fields
            'brand': 'Cole Haan',
            'occasion': ['business', 'formal'],
            'season': ['fall', 'winter'],
            'style': ['classic', 'professional'],
            'mood': ['professional', 'formal'],
            'gender': 'Male',
            'matchingColors': ['Black', 'Navy', 'Gray'],
            'dominantColors': ['Brown', 'Tan'],
            'colorName': 'Cognac Brown',
            'tags': ['woven', 'smooth', 'dress', 'oxford'],
            'subType': 'oxford',
            'bodyTypeCompatibility': ['Average', 'Athletic'],
            'weatherCompatibility': ['mild', 'cool'],
            'favorite': False,
            'usage_count': 8,
            'wearCount': 6,
            'lastWorn': '2024-01-10T09:00:00Z',
            'last_used_at': '2024-01-10T09:00:00Z',
            'createdAt': '2023-11-15T00:00:00Z',
            'updatedAt': '2024-01-10T09:00:00Z',
            'backgroundRemoved': True,
            'metadata': {
                'quality': 'premium',
                'material': 'leather',
                'care_instructions': 'polish_only'
            }
        },
        {
            # Core fields
            'id': '0100b030-8f95-4a50-82f7-7c02c7b745ba',
            'name': 'Pants jeans light blue by Levi\'s',
            'type': 'pants',
            'color': 'Light Blue',
            'imageUrl': 'https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F0100b030-8f95-4a50-82f7-7c02c7b745ba.jpg',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            
            # Complex metadata fields
            'brand': 'Levi\'s',
            'occasion': ['casual', 'everyday'],
            'season': ['spring', 'summer', 'fall'],
            'style': ['casual', 'relaxed'],
            'mood': ['relaxed', 'comfortable'],
            'gender': 'Male',
            'matchingColors': ['White', 'Gray', 'Navy'],
            'dominantColors': ['Light Blue', 'Denim'],
            'colorName': 'Light Wash',
            'tags': ['denim', 'jeans', 'light', 'blue'],
            'subType': 'jeans',
            'bodyTypeCompatibility': ['Average', 'Athletic', 'Slim'],
            'weatherCompatibility': ['mild', 'warm'],
            'favorite': False,
            'usage_count': 25,
            'wearCount': 20,
            'lastWorn': '2024-01-12T14:00:00Z',
            'last_used_at': '2024-01-12T14:00:00Z',
            'createdAt': '2023-10-01T00:00:00Z',
            'updatedAt': '2024-01-12T14:00:00Z',
            'backgroundRemoved': True,
            'metadata': {
                'quality': 'medium',
                'material': 'denim',
                'care_instructions': 'machine_wash_cold'
            }
        }
    ]
    
    # Preprocess the complex wardrobe
    print("🔄 PREPROCESSING: Converting complex metadata to system format")
    print("=" * 80)
    
    try:
        preprocessed_wardrobe = wardrobe_preprocessor.preprocess_wardrobe(complex_wardrobe)
        print(f"✅ PREPROCESSING SUCCESSFUL: {len(preprocessed_wardrobe)} items converted")
        
        # Show preprocessing results
        for i, item in enumerate(preprocessed_wardrobe, 1):
            print(f"   {i}. {item['name']}")
            print(f"      Occasions: {item['occasion']}")
            print(f"      Styles: {item['style']}")
            print(f"      Tags: {len(item['tags'])} tags")
            if '_complex_metadata' in item:
                complex_meta = item['_complex_metadata']
                print(f"      Complex metadata: brand={complex_meta.get('brand')}, favorite={complex_meta.get('favorite')}")
        
    except Exception as e:
        print(f"❌ PREPROCESSING FAILED: {e}")
        return
    
    print("\\n" + "=" * 80)
    
    test_cases = [
        {
            'name': 'Business + Classic (Preprocessed Complex Metadata)',
            'occasion': 'Business',
            'style': 'Classic',
            'mood': 'Professional',
            'weather': {'temperature': 70.0, 'condition': 'clear'},
            'user_profile': {
                'bodyType': 'Average',
                'height': '5\'8\" - 5\'11\"',
                'weight': '150-200 lbs',
                'gender': 'Male',
                'skinTone': 'Medium',
                'preferredBrands': ['Abercrombie & Fitch', 'Cole Haan', 'Levi\'s']
            }
        },
        {
            'name': 'Casual + Relaxed (Preprocessed Complex Metadata)',
            'occasion': 'Casual',
            'style': 'Casual',
            'mood': 'Relaxed',
            'weather': {'temperature': 75.0, 'condition': 'sunny'},
            'user_profile': {
                'bodyType': 'Average',
                'height': '5\'8\" - 5\'11\"',
                'weight': '150-200 lbs',
                'gender': 'Male',
                'skinTone': 'Medium',
                'preferredBrands': ['Abercrombie & Fitch', 'Cole Haan', 'Levi\'s']
            }
        },
        {
            'name': 'Missing Weather Data (Preprocessed Complex Metadata)',
            'occasion': 'Business',
            'style': 'Classic',
            'mood': 'Professional',
            'weather': None,  # Missing weather data
            'user_profile': {
                'bodyType': 'Average',
                'height': '5\'8\" - 5\'11\"',
                'weight': '150-200 lbs',
                'gender': 'Male',
                'skinTone': 'Medium',
                'preferredBrands': ['Abercrombie & Fitch', 'Cole Haan', 'Levi\'s']
            }
        }
    ]
    
    print("🚀 TESTING WITH PREPROCESSED COMPLEX METADATA")
    print("=" * 80)
    print(f"Preprocessed Wardrobe: {len(preprocessed_wardrobe)} items")
    print(f"Test Cases: {len(test_cases)}")
    print("=" * 80)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n🧪 TEST {i}/{len(test_cases)}: {test_case['name']}")
        print(f"📋 Config: {test_case['occasion']} + {test_case['style']}")
        print(f"   Weather: {test_case['weather']}")
        print(f"   Profile: {test_case['user_profile']['bodyType']} body, {test_case['user_profile']['skinTone']} skin")
        
        data = {
            'occasion': test_case['occasion'],
            'style': test_case['style'],
            'mood': test_case['mood'],
            'weather': test_case['weather'],
            'wardrobe': preprocessed_wardrobe,  # Use preprocessed wardrobe
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
    print("\\n" + "=" * 80)
    print("📊 PREPROCESSED COMPLEX METADATA TEST SUMMARY")
    print("=" * 80)
    
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
        
        print(f"\\n🎯 Strategy Distribution:")
        for strategy, count in strategy_counts.items():
            print(f"   {strategy}: {count}")
    
    print(f"\\n❌ Failed Tests:")
    for result in results:
        if result['status'] != 'success':
            print(f"   • {result['test']}: {result['status']}")
    
    return results

if __name__ == "__main__":
    test_complex_metadata_preprocessed()



