#!/usr/bin/env python3
"""
Production Data Seeder for ClosetGPT
Creates realistic wardrobe data with comprehensive metadata for testing all features.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import firebase_admin
from firebase_admin import credentials, firestore
import random
from datetime import datetime, timedelta
import uuid
import time
from typing import List, Dict, Any

# Import types
from src.types.wardrobe import (
    ClothingType, Season, StyleType, Color, ClothingItem,
    Material, BodyType, SkinTone, TemperatureRange
)

class ProductionDataSeeder:
    def __init__(self):
        # Initialize Firebase Admin
        cred = credentials.Certificate("service-account-key.json")
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        
        # Production user IDs (you can replace these with real user IDs)
        self.user_ids = [
            "dANqjiI0CKgaitxzYtw1bhtvQrG3",  # Main test user
            "test_user_2",
            "test_user_3"
        ]
        
        # Realistic image URLs (replace with actual image URLs)
        self.image_urls = {
            "shirt": [
                "https://via.placeholder.com/400x600/4A90E2/FFFFFF?text=Shirt+1",
                "https://via.placeholder.com/400x600/50C878/FFFFFF?text=Shirt+2",
                "https://via.placeholder.com/400x600/FF6B6B/FFFFFF?text=Shirt+3"
            ],
            "pants": [
                "https://via.placeholder.com/400x600/8B4513/FFFFFF?text=Pants+1",
                "https://via.placeholder.com/400x600/2F4F4F/FFFFFF?text=Pants+2",
                "https://via.placeholder.com/400x600/696969/FFFFFF?text=Pants+3"
            ],
            "jacket": [
                "https://via.placeholder.com/400x600/000000/FFFFFF?text=Jacket+1",
                "https://via.placeholder.com/400x600/8B0000/FFFFFF?text=Jacket+2"
            ],
            "dress": [
                "https://via.placeholder.com/400x600/FF69B4/FFFFFF?text=Dress+1",
                "https://via.placeholder.com/400x600/9370DB/FFFFFF?text=Dress+2"
            ],
            "shoes": [
                "https://via.placeholder.com/400x600/8B4513/FFFFFF?text=Shoes+1",
                "https://via.placeholder.com/400x600/000000/FFFFFF?text=Shoes+2"
            ]
        }

    def create_realistic_wardrobe_items(self) -> List[Dict[str, Any]]:
        """Create realistic wardrobe items with comprehensive metadata."""
        
        items = []
        
        # Casual Wardrobe Items
        casual_items = [
            {
                "name": "Classic White T-Shirt",
                "type": ClothingType.SHIRT,
                "color": "white",
                "subType": "crew_neck",
                "brand": "Uniqlo",
                "season": [Season.SPRING, Season.SUMMER, Season.FALL],
                "style": [StyleType.CASUAL, StyleType.MINIMALIST, StyleType.CLASSIC],
                "occasion": ["casual", "daily", "weekend", "errands"],
                "tags": ["basic", "essential", "versatile", "cotton"],
                "dominantColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                "matchingColors": [{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}, {"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "metadata": self._create_metadata("shirt", "crew_neck", "white", "casual", "cotton", "light")
            },
            {
                "name": "Navy Blue Crew Neck Sweater",
                "type": ClothingType.SWEATER,
                "color": "navy",
                "subType": "crew_neck",
                "brand": "J.Crew",
                "season": [Season.FALL, Season.WINTER],
                "style": [StyleType.CASUAL, StyleType.PREPPY, StyleType.CLASSIC],
                "occasion": ["casual", "work", "smart_casual", "weekend"],
                "tags": ["sweater", "navy", "preppy", "wool"],
                "dominantColors": [{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
                "matchingColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}, {"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
                "metadata": self._create_metadata("sweater", "crew_neck", "navy", "smart_casual", "wool", "medium")
            },
            {
                "name": "Dark Wash Denim Jeans",
                "type": ClothingType.PANTS,
                "color": "blue",
                "subType": "straight_leg",
                "brand": "Levi's",
                "season": [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                "style": [StyleType.CASUAL, StyleType.CLASSIC, StyleType.STREETWEAR],
                "occasion": ["casual", "daily", "weekend", "errands"],
                "tags": ["denim", "jeans", "versatile", "straight_leg"],
                "dominantColors": [{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
                "matchingColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}, {"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
                "metadata": self._create_metadata("pants", "straight_leg", "blue", "casual", "denim", "medium")
            },
            {
                "name": "Black Leather Jacket",
                "type": ClothingType.JACKET,
                "color": "black",
                "subType": "motorcycle",
                "brand": "AllSaints",
                "season": [Season.FALL, Season.WINTER],
                "style": [StyleType.STREETWEAR, StyleType.STATEMENT, StyleType.TRENDY],
                "occasion": ["casual", "night_out", "weekend", "concert"],
                "tags": ["leather", "jacket", "edgy", "statement"],
                "dominantColors": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "matchingColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}, {"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
                "metadata": self._create_metadata("jacket", "motorcycle", "black", "casual", "leather", "medium")
            },
            {
                "name": "White Leather Sneakers",
                "type": ClothingType.SNEAKERS,
                "color": "white",
                "subType": "low_top",
                "brand": "Common Projects",
                "season": [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                "style": [StyleType.MINIMALIST, StyleType.CLASSIC, StyleType.CASUAL],
                "occasion": ["casual", "daily", "weekend", "errands"],
                "tags": ["sneakers", "white", "minimalist", "leather"],
                "dominantColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                "matchingColors": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}, {"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
                "metadata": self._create_metadata("shoes", "low_top", "white", "casual", "leather", "medium")
            }
        ]
        
        # Business/Formal Items
        formal_items = [
            {
                "name": "White Oxford Shirt",
                "type": ClothingType.DRESS_SHIRT,
                "color": "white",
                "subType": "oxford",
                "brand": "Brooks Brothers",
                "season": [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                "style": [StyleType.FORMAL, StyleType.BUSINESS, StyleType.CLASSIC],
                "occasion": ["work", "interview", "business_casual", "formal"],
                "tags": ["oxford", "formal", "business", "cotton"],
                "dominantColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                "matchingColors": [{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}, {"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
                "metadata": self._create_metadata("dress_shirt", "oxford", "white", "formal", "cotton", "medium")
            },
            {
                "name": "Navy Blue Suit Pants",
                "type": ClothingType.PANTS,
                "color": "navy",
                "subType": "dress_pants",
                "brand": "J.Crew",
                "season": [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                "style": [StyleType.FORMAL, StyleType.BUSINESS, StyleType.CLASSIC],
                "occasion": ["work", "interview", "business_casual", "formal"],
                "tags": ["dress_pants", "formal", "business", "wool"],
                "dominantColors": [{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
                "matchingColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}, {"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
                "metadata": self._create_metadata("pants", "dress_pants", "navy", "formal", "wool", "medium")
            },
            {
                "name": "Black Oxford Shoes",
                "type": ClothingType.DRESS_SHOES,
                "color": "black",
                "subType": "oxford",
                "brand": "Allen Edmonds",
                "season": [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                "style": [StyleType.FORMAL, StyleType.BUSINESS, StyleType.CLASSIC],
                "occasion": ["work", "interview", "business_casual", "formal"],
                "tags": ["oxford", "formal", "business", "leather"],
                "dominantColors": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "matchingColors": [{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}, {"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
                "metadata": self._create_metadata("dress_shoes", "oxford", "black", "formal", "leather", "medium")
            }
        ]
        
        # Trendy/Statement Items
        trendy_items = [
            {
                "name": "Oversized Blazer",
                "type": ClothingType.JACKET,
                "color": "beige",
                "subType": "oversized",
                "brand": "Zara",
                "season": [Season.SPRING, Season.FALL],
                "style": [StyleType.TRENDY, StyleType.SMART_CASUAL, StyleType.STATEMENT],
                "occasion": ["work", "smart_casual", "weekend", "date_night"],
                "tags": ["blazer", "oversized", "trendy", "linen"],
                "dominantColors": [{"name": "beige", "hex": "#F5F5DC", "rgb": [245, 245, 220]}],
                "matchingColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}, {"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "metadata": self._create_metadata("jacket", "oversized", "beige", "smart_casual", "linen", "light")
            },
            {
                "name": "High-Waisted Wide Leg Pants",
                "type": ClothingType.PANTS,
                "color": "black",
                "subType": "wide_leg",
                "brand": "Aritzia",
                "season": [Season.SPRING, Season.SUMMER, Season.FALL],
                "style": [StyleType.TRENDY, StyleType.STATEMENT, StyleType.SMART_CASUAL],
                "occasion": ["work", "smart_casual", "weekend", "date_night"],
                "tags": ["wide_leg", "high_waisted", "trendy", "polyester"],
                "dominantColors": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                "matchingColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}, {"name": "beige", "hex": "#F5F5DC", "rgb": [245, 245, 220]}],
                "metadata": self._create_metadata("pants", "wide_leg", "black", "smart_casual", "polyester", "medium")
            }
        ]
        
        # Combine all items
        all_items = casual_items + formal_items + trendy_items
        
        # Create items for each user
        for user_id in self.user_ids:
            for item in all_items:
                # Create a copy for each user
                item_copy = item.copy()
                item_copy["id"] = str(uuid.uuid4())
                item_copy["userId"] = user_id
                item_copy["imageUrl"] = self._get_image_url(item_copy["type"])
                item_copy["createdAt"] = int(datetime.now().timestamp())
                item_copy["updatedAt"] = int(datetime.now().timestamp())
                item_copy["backgroundRemoved"] = True
                
                # Add CLIP embedding (simulated)
                item_copy["embedding"] = self._generate_clip_embedding()
                
                items.append(item_copy)
        
        return items

    def _create_metadata(self, item_type: str, sub_type: str, color: str, formality: str, material: str, weight: str) -> Dict[str, Any]:
        """Create comprehensive metadata for an item."""
        
        return {
            "analysisTimestamp": int(datetime.now().timestamp()),
            "originalType": item_type,
            "originalSubType": sub_type,
            "styleTags": [formality, material, weight],
            "occasionTags": ["daily", "casual"] if formality == "casual" else ["work", "formal"],
            "brand": "Brand Name",
            "imageHash": f"hash_{uuid.uuid4().hex[:8]}",
            "colorAnalysis": {
                "dominant": [{"name": color, "hex": "#000000", "rgb": [0, 0, 0]}],
                "matching": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}]
            },
            "basicMetadata": {
                "width": 800,
                "height": 600,
                "orientation": "portrait",
                "dateTaken": datetime.now().isoformat(),
                "deviceModel": "iPhone 12",
                "flashUsed": False
            },
            "visualAttributes": {
                "pattern": "solid",
                "formalLevel": formality,
                "fit": "regular",
                "length": "regular",
                "genderTarget": "unisex",
                "textureStyle": material,
                "backgroundRemoved": True,
                "silhouette": "regular",
                "hangerPresent": False,
                "wearLayer": "outer" if item_type in ["jacket", "sweater"] else "base",
                "material": material,
                "fabricWeight": weight
            },
            "itemMetadata": {
                "priceEstimate": "89.99",
                "careInstructions": "Check care label",
                "tags": [material, formality, weight]
            },
            "naturalDescription": f"A {color} {material} {item_type} with {formality} styling",
            "temperatureCompatibility": {
                "minTemp": 10 if weight == "light" else 0,
                "maxTemp": 30 if weight == "light" else 20,
                "recommendedLayers": ["base"] if item_type in ["shirt", "dress_shirt"] else ["outer"],
                "materialPreferences": [Material.COTTON if material == "cotton" else Material.WOOL]
            },
            "materialCompatibility": {
                "compatibleMaterials": [Material.COTTON, Material.LINEN],
                "weatherAppropriate": {
                    "spring": [Material.COTTON, Material.LINEN],
                    "summer": [Material.COTTON, Material.LINEN],
                    "fall": [Material.WOOL, Material.COTTON],
                    "winter": [Material.WOOL]
                }
            },
            "bodyTypeCompatibility": {
                "recommendedFits": {
                    BodyType.RECTANGLE: ["regular", "loose"],
                    BodyType.HOURGLASS: ["fitted", "regular"],
                    BodyType.PEAR: ["loose", "regular"],
                    BodyType.APPLE: ["loose", "regular"],
                    BodyType.INVERTED_TRIANGLE: ["regular", "fitted"]
                },
                "styleRecommendations": {
                    BodyType.RECTANGLE: ["casual", "minimalist"],
                    BodyType.HOURGLASS: ["classic", "elegant"],
                    BodyType.PEAR: ["casual", "comfortable"],
                    BodyType.APPLE: ["casual", "comfortable"],
                    BodyType.INVERTED_TRIANGLE: ["casual", "classic"]
                }
            },
            "skinToneCompatibility": {
                "compatibleColors": {
                    SkinTone.WARM: ["beige", "brown", "orange"],
                    SkinTone.COOL: ["navy", "gray", "purple"],
                    SkinTone.NEUTRAL: ["white", "black", "gray"]
                },
                "recommendedPalettes": {
                    SkinTone.WARM: ["earth_tones", "warm_neutrals"],
                    SkinTone.COOL: ["cool_neutrals", "jewel_tones"],
                    SkinTone.NEUTRAL: ["monochrome", "neutral_tones"]
                }
            },
            "outfitScoring": {
                "versatility": 8.5,
                "seasonality": 7.2,
                "formality": 6.8,
                "trendiness": 7.0,
                "quality": 8.0
            }
        }

    def _get_image_url(self, item_type: str) -> str:
        """Get a realistic image URL for the item type."""
        type_key = item_type.lower()
        if type_key in self.image_urls:
            return random.choice(self.image_urls[type_key])
        return "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400"

    def _generate_clip_embedding(self) -> List[float]:
        """Generate a simulated CLIP embedding vector."""
        return [random.uniform(-1, 1) for _ in range(512)]

    def seed_wardrobe_data(self):
        """Seed the wardrobe collection with production data."""
        print("🌱 Starting production data seeding...")
        
        # Create wardrobe items
        items = self.create_realistic_wardrobe_items()
        
        # Add items to Firestore
        wardrobe_ref = self.db.collection('wardrobe')
        batch = self.db.batch()
        
        added_count = 0
        for item in items:
            doc_ref = wardrobe_ref.document(item['id'])
            batch.set(doc_ref, item)
            added_count += 1
            
            # Commit batch every 500 operations
            if added_count % 500 == 0:
                batch.commit()
                batch = self.db.batch()
                print(f"✅ Added {added_count} items...")
        
        # Commit remaining items
        if added_count % 500 != 0:
            batch.commit()
        
        print(f"✅ Successfully seeded {added_count} wardrobe items across {len(self.user_ids)} users")
        print(f"📊 Items per user: {len(items) // len(self.user_ids)}")
        
        return added_count

    def seed_user_profiles(self):
        """Seed user profiles with realistic data."""
        print("👤 Seeding user profiles...")
        
        profiles = [
            {
                "id": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
                "name": "Alex Johnson",
                "email": "alex.johnson@example.com",
                "gender": "male",
                "preferences": {
                    "style": ["casual", "minimalist", "classic"],
                    "colors": ["navy", "white", "black", "gray"],
                    "occasions": ["daily", "work", "weekend"]
                },
                "measurements": {
                    "height": 180,
                    "weight": 75,
                    "bodyType": "rectangle",
                    "skinTone": "neutral"
                },
                "stylePreferences": ["casual", "minimalist", "classic"],
                "bodyType": "rectangle",
                "skinTone": "neutral",
                "fitPreference": "regular",
                "createdAt": int(datetime.now().timestamp()),
                "updatedAt": int(datetime.now().timestamp())
            },
            {
                "id": "test_user_2",
                "name": "Sarah Chen",
                "email": "sarah.chen@example.com",
                "gender": "female",
                "preferences": {
                    "style": ["trendy", "smart_casual", "elegant"],
                    "colors": ["beige", "white", "black", "navy"],
                    "occasions": ["work", "smart_casual", "date_night"]
                },
                "measurements": {
                    "height": 165,
                    "weight": 60,
                    "bodyType": "hourglass",
                    "skinTone": "warm"
                },
                "stylePreferences": ["trendy", "smart_casual", "elegant"],
                "bodyType": "hourglass",
                "skinTone": "warm",
                "fitPreference": "fitted",
                "createdAt": int(datetime.now().timestamp()),
                "updatedAt": int(datetime.now().timestamp())
            }
        ]
        
        users_ref = self.db.collection('users')
        batch = self.db.batch()
        
        for profile in profiles:
            doc_ref = users_ref.document(profile['id'])
            batch.set(doc_ref, profile)
        
        batch.commit()
        print(f"✅ Seeded {len(profiles)} user profiles")

    def seed_fashion_trends(self):
        """Seed current fashion trends."""
        print("📈 Seeding fashion trends...")
        
        trends = [
            {
                "id": str(uuid.uuid4()),
                "season": "spring",
                "year": 2024,
                "trends": {
                    "colors": ["sage_green", "soft_pink", "navy", "beige"],
                    "styles": ["minimalist", "coastal_chic", "smart_casual"],
                    "patterns": ["solid", "subtle_stripes", "minimal_prints"],
                    "materials": ["linen", "cotton", "silk"]
                },
                "popularity": 8.5,
                "createdAt": int(datetime.now().timestamp()),
                "updatedAt": int(datetime.now().timestamp())
            },
            {
                "id": str(uuid.uuid4()),
                "season": "summer",
                "year": 2024,
                "trends": {
                    "colors": ["white", "navy", "coral", "yellow"],
                    "styles": ["coastal_grandma", "minimalist", "athleisure"],
                    "patterns": ["solid", "floral", "geometric"],
                    "materials": ["linen", "cotton", "synthetic"]
                },
                "popularity": 8.2,
                "createdAt": int(datetime.now().timestamp()),
                "updatedAt": int(datetime.now().timestamp())
            }
        ]
        
        trends_ref = self.db.collection('fashion_trends')
        batch = self.db.batch()
        
        for trend in trends:
            doc_ref = trends_ref.document(trend['id'])
            batch.set(doc_ref, trend)
        
        batch.commit()
        print(f"✅ Seeded {len(trends)} fashion trends")

    def run_full_seed(self):
        """Run the complete seeding process."""
        print("🚀 Starting complete production data seeding...")
        
        try:
            # Seed user profiles
            self.seed_user_profiles()
            
            # Seed wardrobe data
            item_count = self.seed_wardrobe_data()
            
            # Seed fashion trends
            self.seed_fashion_trends()
            
            print("\n🎉 Production data seeding completed successfully!")
            print(f"📊 Summary:")
            print(f"   - Users: {len(self.user_ids)}")
            print(f"   - Wardrobe items: {item_count}")
            print(f"   - Items per user: {item_count // len(self.user_ids)}")
            print(f"   - Fashion trends: 2")
            
        except Exception as e:
            print(f"❌ Error during seeding: {str(e)}")
            raise

def main():
    """Main function to run the seeder."""
    seeder = ProductionDataSeeder()
    seeder.run_full_seed()

if __name__ == "__main__":
    main() 