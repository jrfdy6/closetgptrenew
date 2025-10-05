#!/usr/bin/env python3
"""
Debug script to test the robust outfit generation service locally.
"""

import sys
import os
import asyncio
import logging

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_robust_service():
    """Test the robust service with mock data."""
    try:
        print("🔍 Testing robust service imports...")
        
        # Test imports
        try:
            from src.services.robust_outfit_generation_service import RobustOutfitGenerationService, GenerationContext
            print("✅ Robust service imports successful")
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return
        
        # Test ClothingItem import
        try:
            from src.custom_types.wardrobe import ClothingItem
            print("✅ ClothingItem import successful")
        except ImportError as e:
            print(f"❌ ClothingItem import failed: {e}")
            ClothingItem = None
        
        # Create mock wardrobe items
        mock_wardrobe = [
            {
                'id': 'item1',
                'name': 'Blue Dress Shirt',
                'type': 'shirt',
                'color': 'blue',
                'style': 'professional',
                'occasion': 'business'
            },
            {
                'id': 'item2', 
                'name': 'Black Dress Pants',
                'type': 'pants',
                'color': 'black',
                'style': 'professional',
                'occasion': 'business'
            },
            {
                'id': 'item3',
                'name': 'Black Dress Shoes',
                'type': 'shoes',
                'color': 'black',
                'style': 'professional',
                'occasion': 'business'
            }
        ]
        
        # Convert to ClothingItem objects if possible
        clothing_items = []
        if ClothingItem:
            for item_dict in mock_wardrobe:
                try:
                    clothing_item = ClothingItem(**item_dict)
                    clothing_items.append(clothing_item)
                    print(f"✅ Converted item: {item_dict['name']}")
                except Exception as e:
                    print(f"❌ Failed to convert item {item_dict['name']}: {e}")
                    # Use raw dict as fallback
                    clothing_items.append(item_dict)
        else:
            clothing_items = mock_wardrobe
            print("⚠️ Using raw dict items (ClothingItem not available)")
        
        # Create generation context
        context = GenerationContext(
            user_id="test-user",
            occasion="business",
            style="professional", 
            mood="confident",
            weather=None,
            wardrobe=clothing_items,
            base_item_id=None,
            user_profile=None
        )
        
        print(f"✅ Created generation context with {len(clothing_items)} items")
        
        # Test robust service
        robust_service = RobustOutfitGenerationService()
        print("✅ Created robust service instance")
        
        # Try to generate outfit
        print("🎯 Attempting outfit generation...")
        try:
            outfit = await robust_service.generate_outfit(context)
            print(f"✅ Generated outfit: {outfit}")
        except Exception as e:
            print(f"❌ Outfit generation failed: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_robust_service())
