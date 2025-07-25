#!/usr/bin/env python3
"""
Test script to generate an outfit and check if items are being selected.
"""

import requests
import json
from datetime import datetime

def test_outfit_generation():
    """Test outfit generation with the current wardrobe."""
    
    # Test data
    test_data = {
        "occasion": "Wedding Guest",
        "mood": "confident",
        "style": "Classic",
        "description": "A classic outfit for a wedding guest",
        "wardrobe": [
            {
                "id": "i2r5pnmysbmby67mf9",
                "name": "A slim, solid, smooth high top sneakers",
                "type": "shoes",
                "color": "Black",
                "season": ["fall", "winter", "spring", "summer"],
                "imageUrl": "https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F87627d51-06b9-4ca1-a045-7f87ff88c52c.jpg?alt=media&token=b411a0bf-1ae8-4e49-8b7a-ae3ddd347858",
                "tags": ["Sporty", "Casual"],
                "style": ["Edgy", "Y2K", "Casual", "Trendy", "Streetwear", "Sporty", "Grunge"],
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "dominantColors": [
                    {"hex": "#000000", "rgb": [0, 0, 0], "name": "Black"},
                    {"hex": "#FFFFFF", "rgb": [255, 255, 255], "name": "White"},
                    {"hex": "#FF0000", "rgb": [255, 0, 0], "name": "Red"}
                ],
                "matchingColors": [
                    {"hex": "#0000FF", "rgb": [0, 0, 255], "name": "Blue"},
                    {"hex": "#808080", "rgb": [128, 128, 128], "name": "Gray"}
                ],
                "occasion": ["Casual", "Sport", "Brunch", "Dinner"],
                "brand": "Converse",
                "createdAt": 1750151681007,
                "updatedAt": 1750151681007,
                "subType": "high top sneakers",
                "colorName": None,
                "backgroundRemoved": False,
                "metadata": {
                    "analysisTimestamp": 1750151681007,
                    "originalType": "shoes",
                    "colorAnalysis": {
                        "dominantColors": [
                            {"hex": "#000000", "rgb": [0, 0, 0], "name": "Black"},
                            {"hex": "#FFFFFF", "rgb": [255, 255, 255], "name": "White"},
                            {"hex": "#FF0000", "rgb": [255, 0, 0], "name": "Red"}
                        ],
                        "matchingColors": [
                            {"hex": "#0000FF", "rgb": [0, 0, 255], "name": "Blue"},
                            {"hex": "#808080", "rgb": [128, 128, 128], "name": "Gray"}
                        ]
                    },
                    "visualAttributes": {
                        "material": "Canvas",
                        "pattern": "Solid",
                        "textureStyle": "Smooth",
                        "fabricWeight": "Medium",
                        "fit": "Standard",
                        "silhouette": None,
                        "length": None,
                        "genderTarget": "Unisex",
                        "sleeveLength": None,
                        "hangerPresent": False,
                        "backgroundRemoved": False,
                        "wearLayer": "Outer",
                        "formalLevel": "Casual"
                    }
                }
            },
            {
                "id": "1l73w5irshsmby61zf8",
                "name": "A slim, solid, smooth dress pants",
                "type": "pants",
                "color": "Beige",
                "season": ["fall", "winter", "spring", "summer"],
                "imageUrl": "https://firebasestorage.googleapis.com/v0/b/closetgptrenew.firebasestorage.app/o/users%2FdANqjiI0CKgaitxzYtw1bhtvQrG3%2Fwardrobe%2F87627d51-06b9-4ca1-a045-7f87ff88c52c.jpg?alt=media&token=b411a0bf-1ae8-4e49-8b7a-ae3ddd347858",
                "tags": ["Formal", "Business"],
                "style": ["Business", "Preppy", "Business Casual", "Classic", "Urban", "Minimalist", "Streetwear", "Formal", "Techwear"],
                "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "dominantColors": [
                    {"hex": "#F5F5DC", "rgb": [245, 245, 220], "name": "Beige"}
                ],
                "matchingColors": [
                    {"name": "Navy Blue", "rgb": [0, 0, 128], "hex": "#000080"},
                    {"name": "White", "rgb": [255, 255, 255], "hex": "#FFFFFF"},
                    {"name": "Brown", "rgb": [165, 42, 42], "hex": "#A52A2A"},
                    {"name": "Black", "rgb": [0, 0, 0], "hex": "#000000"}
                ],
                "occasion": ["Business", "Beach", "Vacation", "Interview", "Wedding", "Formal", "Funeral", "Conference"],
                "brand": None,
                "createdAt": 1750151680964,
                "updatedAt": 1750151680964,
                "subType": "dress pants",
                "colorName": None,
                "backgroundRemoved": False,
                "metadata": {
                    "analysisTimestamp": 1750151680964,
                    "originalType": "pants",
                    "colorAnalysis": {
                        "dominantColors": [
                            {"hex": "#F5F5DC", "rgb": [245, 245, 220], "name": "Beige"}
                        ],
                        "matchingColors": [
                            {"name": "Navy Blue", "rgb": [0, 0, 128], "hex": "#000080"},
                            {"name": "White", "rgb": [255, 255, 255], "hex": "#FFFFFF"},
                            {"name": "Brown", "rgb": [165, 42, 42], "hex": "#A52A2A"},
                            {"name": "Black", "rgb": [0, 0, 0], "hex": "#000000"}
                        ]
                    },
                    "visualAttributes": {
                        "material": "Cotton",
                        "pattern": "Solid",
                        "textureStyle": "Smooth",
                        "fabricWeight": "Medium",
                        "fit": "Slim",
                        "silhouette": "Straight",
                        "length": "Full-length",
                        "genderTarget": "Men's",
                        "sleeveLength": None,
                        "hangerPresent": True,
                        "backgroundRemoved": False,
                        "wearLayer": "Outer",
                        "formalLevel": "Formal"
                    }
                }
            }
        ],
        "weather": {
            "temperature": 78.5,
            "condition": "sunny",
            "location": "default",
            "humidity": 50,
            "wind_speed": 5,
            "precipitation": 0
        },
        "user_profile": {
            "id": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
            "name": "john",
            "email": "jfeezie@gmail.com",
            "preferences": {},
            "measurements": {
                "skinTone": "neutral"
            },
            "stylePreferences": [],
            "bodyType": "athletic",
            "createdAt": 1750155704479,
            "updatedAt": 1750155704479
        },
        "likedOutfits": [],
        "trendingStyles": [],
        "outfitHistory": [],
        "baseItem": None
    }
    
    try:
        print("🧪 Testing outfit generation...")
        print(f"📊 Wardrobe items: {len(test_data['wardrobe'])}")
        for item in test_data['wardrobe']:
            print(f"   - {item['name']} ({item['type']}) - {item['color']}")
        
        response = requests.post(
            "http://localhost:3001/api/outfit/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Outfit generated successfully!")
            print(f"📋 Outfit ID: {result.get('id')}")
            print(f"📋 Outfit name: {result.get('name')}")
            print(f"📋 Items count: {len(result.get('items', []))}")
            print(f"📋 Items: {result.get('items', [])}")
            
            if result.get('items'):
                print("✅ Items were selected!")
            else:
                print("❌ No items were selected!")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_outfit_generation() 