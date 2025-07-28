#!/usr/bin/env python3
"""
Add test outfits to the database for demonstration purposes.
Simple version without external dependencies.
"""

import json
import time
import uuid

def add_test_outfits_simple():
    """Add test outfits to the database using a simple approach."""
    
    # Test user ID (you can change this to your actual user ID)
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"Adding test outfits for user: {user_id}")
    
    # Sample outfits
    test_outfits = [
        {
            "name": "Casual Weekend Look",
            "description": "A comfortable and stylish outfit perfect for weekend activities",
            "occasion": "Casual",
            "style": "Relaxed",
            "mood": "Comfortable",
            "items": [
                {"id": "item1", "name": "Blue Denim Jacket", "type": "outerwear"},
                {"id": "item2", "name": "White T-Shirt", "type": "top"},
                {"id": "item3", "name": "Black Jeans", "type": "bottom"}
            ],
            "confidence_score": 0.9,
            "reasoning": "Perfect combination of comfort and style for casual occasions"
        },
        {
            "name": "Business Professional",
            "description": "A sharp and professional outfit for important meetings",
            "occasion": "Business",
            "style": "Professional",
            "mood": "Confident",
            "items": [
                {"id": "item4", "name": "Navy Blazer", "type": "outerwear"},
                {"id": "item5", "name": "White Dress Shirt", "type": "top"},
                {"id": "item6", "name": "Gray Dress Pants", "type": "bottom"}
            ],
            "confidence_score": 0.95,
            "reasoning": "Classic business attire that conveys professionalism and competence"
        },
        {
            "name": "Evening Out",
            "description": "An elegant outfit for dinner dates and evening events",
            "occasion": "Evening",
            "style": "Elegant",
            "mood": "Sophisticated",
            "items": [
                {"id": "item7", "name": "Black Dress", "type": "dress"},
                {"id": "item8", "name": "Silver Necklace", "type": "accessory"},
                {"id": "item9", "name": "Black Heels", "type": "shoes"}
            ],
            "confidence_score": 0.88,
            "reasoning": "Timeless elegance that's perfect for evening occasions"
        },
        {
            "name": "Athletic Performance",
            "description": "High-performance athletic wear for workouts and sports",
            "occasion": "Athletic",
            "style": "Sporty",
            "mood": "Energetic",
            "items": [
                {"id": "item10", "name": "Moisture-Wicking Shirt", "type": "top"},
                {"id": "item11", "name": "Athletic Shorts", "type": "bottom"},
                {"id": "item12", "name": "Running Shoes", "type": "shoes"}
            ],
            "confidence_score": 0.92,
            "reasoning": "Performance-focused outfit designed for comfort and mobility during physical activity"
        },
        {
            "name": "Creative Artist",
            "description": "A unique and expressive outfit that showcases personal style",
            "occasion": "Creative",
            "style": "Artistic",
            "mood": "Expressive",
            "items": [
                {"id": "item13", "name": "Colorful Sweater", "type": "top"},
                {"id": "item14", "name": "Distressed Jeans", "type": "bottom"},
                {"id": "item15", "name": "Statement Earrings", "type": "accessory"}
            ],
            "confidence_score": 0.85,
            "reasoning": "Bold and creative combination that expresses artistic personality"
        }
    ]
    
    outfits_added = 0
    
    for outfit_data in test_outfits:
        try:
            # Generate unique ID
            outfit_id = str(uuid.uuid4())
            
            # Add required fields
            outfit_data["id"] = outfit_id
            outfit_data["user_id"] = user_id
            outfit_data["createdAt"] = int(time.time())
            outfit_data["updatedAt"] = int(time.time())
            outfit_data["wasSuccessful"] = True
            outfit_data["validationErrors"] = []
            outfit_data["feedback_summary"] = {
                "total_feedback": 0,
                "likes": 0,
                "dislikes": 0,
                "issues": 0,
                "average_rating": 0
            }
            
            print(f"✅ Would add outfit: {outfit_data['name']}")
            print(f"   ID: {outfit_id}")
            print(f"   Items: {len(outfit_data['items'])}")
            outfits_added += 1
            
        except Exception as e:
            print(f"❌ Error with outfit {outfit_data['name']}: {e}")
    
    print(f"\n🎉 Successfully prepared {outfits_added} test outfits!")
    print(f"User ID: {user_id}")
    print("\nTo add these to your database, you can:")
    print("1. Use the Firebase Console to manually add these outfits")
    print("2. Run this script with Firebase Admin SDK installed")
    print("3. Use the outfit generation feature once the backend is updated")
    
    # Save to a JSON file for manual import
    with open('test_outfits.json', 'w') as f:
        json.dump(test_outfits, f, indent=2)
    
    print(f"\n📄 Test outfits saved to 'test_outfits.json' for manual import")

if __name__ == "__main__":
    add_test_outfits_simple() 