#!/usr/bin/env python3
"""
Debug script to check the data structure being sent to the robust service
"""

import requests
import json

def test_data_structure():
    url = 'https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate'
    headers = {'Authorization': 'Bearer test', 'Content-Type': 'application/json'}

    data = {
        'occasion': 'Business',
        'style': 'Classic', 
        'mood': 'Bold',
        'weather': {'temperature': 70.0, 'condition': 'clear'},
        'wardrobe': [
            {
                'id': 'test1',
                'name': 'Test Shirt',
                'type': 'shirt',
                'color': 'Blue',
                'imageUrl': 'test.jpg',
                'userId': 'test-user',
                'season': ['spring'],
                'dominantColors': [{'name': 'Blue'}],
                'matchingColors': [{'name': 'White'}]
            }
        ],
        'user_profile': {
            'bodyType': 'Hourglass',
            'height': '5\'4" - 5\'7"',
            'weight': '100-150 lbs',
            'gender': 'Female',
            'skinTone': 'Warm'
        }
    }

    print('🔍 DEBUGGING: Data Structure Analysis')
    print('=' * 50)
    print(f'Wardrobe items: {len(data["wardrobe"])}')
    print(f'Wardrobe item structure: {data["wardrobe"][0]}')
    print(f'User profile: {data["user_profile"]}')
    print(f'Weather: {data["weather"]}')
    print('=' * 50)

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ SUCCESS!')
            result = response.json()
            print(f'Strategy: {result.get("metadata", {}).get("generation_strategy", "unknown")}')
            print(f'Items: {len(result.get("items", []))}')
        else:
            print(f'❌ FAILED: {response.text}')
            
    except Exception as e:
        print(f'❌ EXCEPTION: {e}')

if __name__ == '__main__':
    test_data_structure()



