#!/usr/bin/env python3
"""
Minimal test to isolate the robust service issue
"""

import requests
import json

def test_minimal_robust():
    url = 'https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate'
    headers = {'Authorization': 'Bearer test', 'Content-Type': 'application/json'}

    # Minimal data to test robust service
    data = {
        'occasion': 'Casual',
        'style': 'Casual', 
        'mood': 'Relaxed',
        'weather': {'temperature': 70.0, 'condition': 'clear'},
        'wardrobe': [
            {
                'id': 'minimal_test_1',
                'name': 'Basic Shirt',
                'type': 'shirt',
                'color': 'White',
                'imageUrl': 'test.jpg',
                'userId': 'test-user'
            },
            {
                'id': 'minimal_test_2', 
                'name': 'Basic Pants',
                'type': 'pants',
                'color': 'Black',
                'imageUrl': 'test.jpg',
                'userId': 'test-user'
            },
            {
                'id': 'minimal_test_3',
                'name': 'Basic Shoes', 
                'type': 'shoes',
                'color': 'White',
                'imageUrl': 'test.jpg',
                'userId': 'test-user'
            }
        ],
        'user_profile': {
            'bodyType': 'Average',
            'height': 'Average',
            'weight': 'Average', 
            'gender': 'Unspecified',
            'skinTone': 'Medium'
        }
    }

    print('🔍 MINIMAL TEST: Basic outfit generation')
    print('=' * 50)
    print(f'Wardrobe: {len(data["wardrobe"])} items')
    print(f'Profile: {data["user_profile"]}')
    print('=' * 50)

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ SUCCESS!')
            result = response.json()
            print(f'Strategy: {result.get("metadata", {}).get("generation_strategy", "unknown")}')
            print(f'Items: {len(result.get("items", []))}')
            for i, item in enumerate(result.get("items", [])):
                print(f'  {i+1}. {item.get("name", "Unknown")} ({item.get("type", "unknown")})')
        else:
            print(f'❌ FAILED: {response.text}')
            
    except Exception as e:
        print(f'❌ EXCEPTION: {e}')

if __name__ == '__main__':
    test_minimal_robust()



