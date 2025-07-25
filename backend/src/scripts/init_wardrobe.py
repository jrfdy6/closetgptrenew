import firebase_admin
from firebase_admin import credentials, firestore
import random
from datetime import datetime
import uuid
from ..custom_types.wardrobe import (
    ClothingType,
    Season,
    StyleType,
    Color,
    ClothingItem
)

def init_wardrobe():
    # Initialize Firebase Admin
    cred = credentials.Certificate("service-account-key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Sample items to add to wardrobe
    sample_items = [
        {
            "id": str(uuid.uuid4()),
            "name": "Blue Denim Jacket",
            "type": ClothingType.JACKET,
            "color": "blue",
            "season": [Season.SPRING, Season.FALL],
            "imageUrl": "https://via.placeholder.com/400x600/1E3A8A/FFFFFF?text=Denim+Jacket",
            "tags": ["denim", "casual", "jacket"],
            "style": [StyleType.CASUAL, StyleType.STREETWEAR],
            "userId": "test-user",
            "dominantColors": [{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
            "matchingColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
            "occasion": ["casual", "daily"],
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp())
        },
        {
            "id": str(uuid.uuid4()),
            "name": "White T-Shirt",
            "type": ClothingType.SHIRT,
            "color": "white",
            "season": [Season.SPRING, Season.SUMMER, Season.FALL],
            "imageUrl": "https://via.placeholder.com/400x600/FFFFFF/000000?text=T-Shirt",
            "tags": ["basic", "casual", "tshirt"],
            "style": [StyleType.CASUAL, StyleType.MINIMALIST],
            "userId": "test-user",
            "dominantColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
            "matchingColors": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
            "occasion": ["casual", "daily"],
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp())
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Black Jeans",
            "type": ClothingType.PANTS,
            "color": "black",
            "season": [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
            "imageUrl": "https://via.placeholder.com/400x600/000000/FFFFFF?text=Jeans",
            "tags": ["denim", "casual", "pants"],
            "style": [StyleType.CASUAL, StyleType.MINIMALIST],
            "userId": "test-user",
            "dominantColors": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
            "matchingColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
            "occasion": ["casual", "daily"],
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp())
        },
        {
            "id": str(uuid.uuid4()),
            "name": "White Sneakers",
            "type": ClothingType.SNEAKERS,
            "color": "white",
            "season": [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
            "imageUrl": "https://via.placeholder.com/400x600/FFFFFF/000000?text=Sneakers",
            "tags": ["casual", "sneakers"],
            "style": [StyleType.CASUAL, StyleType.MINIMALIST],
            "userId": "test-user",
            "dominantColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
            "matchingColors": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
            "occasion": ["casual", "daily"],
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp())
        }
    ]

    # Add items to Firestore
    wardrobe_ref = db.collection('wardrobe')
    for item in sample_items:
        doc_ref = wardrobe_ref.document(item['id'])
        doc_ref.set(item)
        print(f"Added item: {item['name']}")

if __name__ == "__main__":
    init_wardrobe() 