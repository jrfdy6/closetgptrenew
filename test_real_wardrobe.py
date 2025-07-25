#!/usr/bin/env python3
"""
Test script to generate an outfit with the actual wardrobe data from the logs.
"""

import requests
import json
from datetime import datetime

def test_real_wardrobe_outfit():
    """Test outfit generation with the actual wardrobe data."""
    
    # Real wardrobe data from the logs
    test_data = {
        "occasion": "Wedding Guest",
        "mood": "confident",
        "style": "Classic",
        "description": "A classic outfit for a wedding guest",
        "wardrobe": [
            {
                "id": "i2r5pnmysbmby67mf9",
                "name": "A woven, smooth shoes",
                "type": "shoes",
                "color": "Brown",
                "season": ["fall", "winter", "spring", "summer"],
                "imageUrl": "https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F5429b2c8-4fad-47c6-ab03-409b1c4962f2.jpg?alt=media&token=438f8d7b-2485-433d-b772-88f6819390d3",
                "dominantColors": [{"hex": "#8B4513", "rgb": [139, 69, 19], "name": "Brown"}],
                "metadata": {
                    "visualAttributes": {
                        "fabricWeight": "Medium",
                        "formalLevel": "Casual",
                        "bodyTypeCompatibility": {},
                        "skinToneCompatibility": {},
                        "materialCompatibility": {},
                        "pattern": "Solid",
                        "material": "Leather",
                        "outfitScoring": {"versatility": 5, "trendiness": 5, "formality": 5, "seasonality": 5, "quality": 5},
                        "fit": "Slim",
                        "backgroundRemoved": False,
                        "textureStyle": "Smooth",
                        "genderTarget": "Unisex",
                        "temperatureCompatibility": {}
                    }
                },
                "matchingColors": [{"hex": "#000000", "rgb": [0, 0, 0], "name": "Black"}],
                "bodyTypeCompatibility": ["Hourglass", "Pear", "Rectangle"],
                "style": ["Casual", "Business Casual", "Smart Casual"],
                "subType": "loafers",
                "tags": ["Business Casual", "Casual", "Brunch", "Dinner"],
                "weatherCompatibility": ["Spring", "Summer", "Fall"],
                "colorName": None,
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "backgroundRemoved": False,
                "createdAt": 1750151680961,
                "occasion": ["Business Casual", "Casual", "Brunch", "Dinner"],
                "gender": "male",
                "mood": ["Relaxed"],
                "updatedAt": "2025-06-17T23:27:17.084000Z"
            },
            {
                "id": "nwm4i2vpeclmby5xr0c",
                "name": "A slim, solid, smooth pants",
                "type": "pants",
                "color": "Beige",
                "season": ["fall", "spring", "summer"],
                "imageUrl": "https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F5429b2c8-4fad-47c6-ab03-409b1c4962f2.jpg?alt=media&token=438f8d7b-2485-433d-b772-88f6819390d3",
                "dominantColors": [{"hex": "#F5F5DC", "rgb": [245, 245, 220], "name": "Beige"}],
                "metadata": {
                    "visualAttributes": {
                        "fabricWeight": "Medium",
                        "formalLevel": "Casual",
                        "bodyTypeCompatibility": {},
                        "skinToneCompatibility": {},
                        "materialCompatibility": {},
                        "pattern": "Solid",
                        "material": "Cotton",
                        "outfitScoring": {"versatility": 5, "trendiness": 5, "formality": 5, "seasonality": 5, "quality": 5},
                        "fit": "Slim",
                        "backgroundRemoved": False,
                        "textureStyle": "Smooth",
                        "genderTarget": "Unisex",
                        "temperatureCompatibility": {}
                    }
                },
                "matchingColors": [{"hex": "#000080", "rgb": [0, 0, 128], "name": "Navy"}, {"hex": "#FFFFFF", "rgb": [255, 255, 255], "name": "White"}],
                "bodyTypeCompatibility": ["Hourglass", "Pear", "Rectangle"],
                "style": ["Casual", "Athleisure", "Urban", "Minimalist", "Smart Casual", "Streetwear", "Sporty", "Techwear"],
                "subType": "chinos",
                "tags": ["Smart Casual", "Casual"],
                "weatherCompatibility": ["Hot", "Warm", "Summer", "Spring", "Fall"],
                "colorName": None,
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "backgroundRemoved": False,
                "createdAt": 1750151681016,
                "occasion": ["Business Casual", "Beach", "Casual", "Brunch", "Vacation", "Dinner"],
                "gender": "male",
                "mood": ["Relaxed"],
                "updatedAt": "2025-06-17T23:27:26.625000Z"
            },
            {
                "id": "b5unze22dtmby5z2z0",
                "name": "A loose, short, ribbed, ribbed knit sweater",
                "type": "sweater",
                "color": "Gray",
                "season": ["fall", "winter"],
                "imageUrl": "https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F2a3dda71-d3d3-409e-a975-e34c94b0e4a1.jpg?alt=media&token=20f95772-6442-413e-8ca7-99e546ee9697",
                "dominantColors": [{"hex": "#BEBEBE", "rgb": [190, 190, 190], "name": "Gray"}, {"hex": "#F5F5DC", "rgb": [245, 245, 220], "name": "Beige"}],
                "metadata": {
                    "visualAttributes": {
                        "fabricWeight": "Medium",
                        "formalLevel": "Casual",
                        "bodyTypeCompatibility": {},
                        "skinToneCompatibility": {},
                        "materialCompatibility": {},
                        "pattern": "Ribbed knit",
                        "material": "Cotton blend",
                        "outfitScoring": {"versatility": 5, "trendiness": 5, "formality": 5, "seasonality": 5, "quality": 5},
                        "fit": "Loose",
                        "backgroundRemoved": False,
                        "textureStyle": "Ribbed",
                        "genderTarget": "Unisex",
                        "temperatureCompatibility": {}
                    }
                },
                "matchingColors": [{"name": "Black", "rgb": [0, 0, 0], "hex": "#000000"}, {"name": "White", "rgb": [255, 255, 255], "hex": "#FFFFFF"}, {"name": "Denim Blue", "rgb": [58, 87, 149], "hex": "#3A5795"}],
                "bodyTypeCompatibility": ["Rectangle", "Apple"],
                "style": ["Cozy", "Minimalist", "Casual", "Casual Cool", "Athleisure", "Sporty"],
                "subType": "knit sweater",
                "tags": ["Casual"],
                "weatherCompatibility": ["Hot", "Warm", "Summer", "Fall", "Winter"],
                "colorName": None,
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "backgroundRemoved": False,
                "createdAt": 1750151680993,
                "occasion": ["Beach", "Vacation", "Casual", "Brunch", "Dinner"],
                "gender": "male",
                "mood": ["Relaxed"],
                "updatedAt": "2025-06-17T23:27:22.341000Z"
            }
        ],
        "weather": {
            "temperature": 78.5,
            "condition": "sunny",
            "humidity": 65,
            "windSpeed": 8
        },
        "user_profile": {
            "bodyType": "average",
            "skinTone": "neutral",
            "gender": "male",
            "measurements": {},
            "colorPalette": None,
            "materialPreferences": None,
            "fitPreferences": None,
            "comfortLevel": None,
            "preferredBrands": None
        }
    }
    
    print("🧪 Testing outfit generation with real wardrobe data...")
    print(f"📊 Wardrobe items: {len(test_data['wardrobe'])}")
    for item in test_data['wardrobe']:
        print(f"   - {item['name']} ({item['type']}) - {item['color']}")
    
    try:
        response = requests.post(
            "http://localhost:3001/api/outfit/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Outfit generated successfully!")
            print(f"📋 Outfit ID: {result.get('id', 'N/A')}")
            print(f"📋 Outfit name: {result.get('name', 'N/A')}")
            print(f"📋 Items count: {len(result.get('items', []))}")
            print(f"📋 Items: {result.get('items', [])}")
            
            if len(result.get('items', [])) > 0:
                print("✅ Items were selected!")
            else:
                print("❌ No items were selected!")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_real_wardrobe_outfit() 