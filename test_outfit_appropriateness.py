#!/usr/bin/env python3
"""
Test Outfit Appropriateness and Logic

This test evaluates whether the generated outfits make sense for the requested
scenarios, checking for weather appropriateness, occasion matching, and style coherence.
"""

import requests
import json
import sys
import os

# Add backend to path for imports
sys.path.append('backend/src')

def analyze_outfit_appropriateness(outfit_items, scenario):
    """Analyze if the generated outfit makes sense for the scenario"""
    
    analysis = {
        'scenario': scenario,
        'items': len(outfit_items),
        'issues': [],
        'appropriate': True,
        'score': 100
    }
    
    requested_occasion = scenario.get('occasion', '').lower()
    requested_style = scenario.get('style', '').lower()
    requested_mood = scenario.get('mood', '').lower()
    weather_temp = scenario.get('weather', {}).get('temperature', 70)
    weather_condition = scenario.get('weather', {}).get('condition', 'clear')
    
    for item in outfit_items:
        item_name = item.get('name', '').lower()
        item_type = item.get('type', '').lower()
        
        # Weather appropriateness check
        if item_type == 'sweater' and weather_temp > 70:
            analysis['issues'].append(f"❌ Weather mismatch: {item.get('name')} (sweater) for {weather_temp}°F weather")
            analysis['score'] -= 20
            analysis['appropriate'] = False
        
        if item_type == 'jacket' and weather_temp > 75:
            analysis['issues'].append(f"❌ Weather mismatch: {item.get('name')} (jacket) for {weather_temp}°F weather")
            analysis['score'] -= 15
            analysis['appropriate'] = False
        
        if item_type == 'shorts' and weather_temp < 65:
            analysis['issues'].append(f"❌ Weather mismatch: {item.get('name')} (shorts) for {weather_temp}°F weather")
            analysis['score'] -= 15
            analysis['appropriate'] = False
        
        # Occasion appropriateness check
        if requested_occasion == 'business' and 'jeans' in item_name:
            analysis['issues'].append(f"❌ Occasion mismatch: {item.get('name')} (jeans) for business occasion")
            analysis['score'] -= 15
            analysis['appropriate'] = False
        
        if requested_occasion == 'formal' and item_type == 'sneakers':
            analysis['issues'].append(f"❌ Occasion mismatch: {item.get('name')} (sneakers) for formal occasion")
            analysis['score'] -= 15
            analysis['appropriate'] = False
        
        if requested_occasion == 'casual' and 'oxford' in item_name:
            analysis['issues'].append(f"❌ Occasion mismatch: {item.get('name')} (oxford shoes) for casual occasion")
            analysis['score'] -= 10
            analysis['appropriate'] = False
        
        # Style appropriateness check
        if requested_style == 'casual' and 'formal' in item_name:
            analysis['issues'].append(f"❌ Style mismatch: {item.get('name')} (formal) for casual style")
            analysis['score'] -= 10
            analysis['appropriate'] = False
        
        if requested_style == 'elegant' and 'jeans' in item_name:
            analysis['issues'].append(f"❌ Style mismatch: {item.get('name')} (jeans) for elegant style")
            analysis['score'] -= 10
            analysis['appropriate'] = False
    
    # Check for missing essential items
    item_types = [item.get('type', '') for item in outfit_items]
    
    if requested_occasion in ['business', 'formal']:
        if 'shirt' not in item_types and 'blouse' not in item_types:
            analysis['issues'].append(f"❌ Missing essential: No shirt/blouse for {requested_occasion} occasion")
            analysis['score'] -= 15
            analysis['appropriate'] = False
    
    if 'pants' not in item_types and 'skirt' not in item_types and 'dress' not in item_types:
        analysis['issues'].append("❌ Missing essential: No bottom piece (pants/skirt/dress)")
        analysis['score'] -= 20
        analysis['appropriate'] = False
    
    if 'shoes' not in item_types:
        analysis['issues'].append("❌ Missing essential: No shoes")
        analysis['score'] -= 20
        analysis['appropriate'] = False
    
    return analysis

def test_outfit_appropriateness():
    """Test outfit generation appropriateness across different scenarios"""
    
    # Import the wardrobe preprocessor
    try:
        from services.wardrobe_preprocessor import wardrobe_preprocessor
        print("✅ Wardrobe preprocessor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import wardrobe preprocessor: {e}")
        return
    
    url = 'https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate'
    headers = {'Authorization': 'Bearer test', 'Content-Type': 'application/json'}
    
    # Expanded wardrobe with more diverse items for better testing
    complex_wardrobe = [
        {
            'id': '006crwqcyyl7kmby62lrf',
            'name': 'A loose, short, textured, ribbed sweater by Abercrombie & Fitch',
            'type': 'sweater',
            'color': 'Gray',
            'imageUrl': 'https://example.com/sweater.jpg',
            'userId': 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
            'brand': 'Abercrombie & Fitch',
            'occasion': ['casual', 'business'],
            'season': ['fall', 'winter'],
            'style': ['classic', 'preppy'],
            'mood': ['relaxed', 'professional'],
            'gender': 'Male',
            'matchingColors': ['Black', 'Navy', 'White'],
            'tags': ['ribbed', 'textured', 'loose', 'short']
        },
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
        }
    ]
    
    # Preprocess the wardrobe
    print("🔄 PREPROCESSING: Converting complex metadata")
    preprocessed_wardrobe = wardrobe_preprocessor.preprocess_wardrobe(complex_wardrobe)
    print(f"✅ PREPROCESSING SUCCESSFUL: {len(preprocessed_wardrobe)} items")
    
    # Test scenarios with different appropriateness requirements
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
    
    print("\\n🚀 TESTING OUTFIT APPROPRIATENESS")
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
                
                # Analyze appropriateness
                analysis = analyze_outfit_appropriateness(outfit_items, scenario)
                
                print(f"\\n📊 APPROPRIATENESS ANALYSIS:")
                print(f"   Score: {analysis['score']}/100")
                print(f"   Appropriate: {'✅ YES' if analysis['appropriate'] else '❌ NO'}")
                
                if analysis['issues']:
                    print(f"   Issues:")
                    for issue in analysis['issues']:
                        print(f"     {issue}")
                else:
                    print(f"   Issues: None - Perfect outfit!")
                
                # Show generated outfit
                print(f"\\n👔 GENERATED OUTFIT:")
                for j, item in enumerate(outfit_items, 1):
                    print(f"   {j}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                
                results.append({
                    'scenario': scenario['name'],
                    'success': True,
                    'analysis': analysis,
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
    print("📊 OUTFIT APPROPRIATENESS SUMMARY")
    print("=" * 80)
    
    successful_tests = [r for r in results if r['success']]
    total_tests = len(results)
    
    print(f"Total Scenarios: {total_tests}")
    print(f"✅ Successful Generations: {len(successful_tests)}")
    print(f"❌ Failed Generations: {total_tests - len(successful_tests)}")
    
    if successful_tests:
        appropriate_outfits = [r for r in successful_tests if r['analysis']['appropriate']]
        avg_score = sum(r['analysis']['score'] for r in successful_tests) / len(successful_tests)
        
        print(f"\\n🎯 APPROPRIATENESS METRICS:")
        print(f"✅ Appropriate Outfits: {len(appropriate_outfits)}/{len(successful_tests)}")
        print(f"📊 Average Appropriateness Score: {avg_score:.1f}/100")
        
        print(f"\\n📋 SCENARIO RESULTS:")
        for result in results:
            if result['success']:
                analysis = result['analysis']
                status = "✅ APPROPRIATE" if analysis['appropriate'] else "❌ INAPPROPRIATE"
                print(f"   • {result['scenario']}: {status} (Score: {analysis['score']}/100)")
            else:
                print(f"   • {result['scenario']}: ❌ GENERATION FAILED")
    
    return results

if __name__ == "__main__":
    test_outfit_appropriateness()



