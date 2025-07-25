p#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from custom_types.wardrobe import ClothingItem, ClothingType, Color
from services.outfit_service import OutfitService

def test_deduplication():
    """Test that deduplication works correctly for shorts."""
    
    # Create test items
    shorts1 = ClothingItem(
        id="shorts1",
        name="A loose, solid, smooth casual shorts",
        type="shorts",
        style=["casual", "streetwear"],
        dominantColors=[Color(name="blue", hex="#0000FF")],
        tags=["casual", "comfortable"]
    )
    
    shorts2 = ClothingItem(
        id="shorts2", 
        name="Another loose, solid, smooth casual shorts",
        type="shorts",
        style=["casual", "streetwear"],
        dominantColors=[Color(name="black", hex="#000000")],
        tags=["casual", "comfortable"]
    )
    
    shirt = ClothingItem(
        id="shirt1",
        name="A slim, long, solid, smooth button up shirt",
        type="shirt", 
        style=["casual", "streetwear"],
        dominantColors=[Color(name="white", hex="#FFFFFF")],
        tags=["casual", "comfortable"]
    )
    
    # Test items with duplicate shorts
    test_items = [shorts1, shorts2, shirt]
    
    print("🔍 Testing deduplication with items:")
    for item in test_items:
        print(f"   - {item.name} (type: {item.type})")
    
    # Create outfit service and test deduplication
    outfit_service = OutfitService()
    
    # Test the deduplication function directly
    deduplicated = outfit_service._deduplicate_by_category(test_items, None)
    
    print(f"\n✅ After deduplication ({len(deduplicated)} items):")
    for item in deduplicated:
        print(f"   - {item.name} (type: {item.type})")
    
    # Check if we have duplicate shorts
    shorts_count = sum(1 for item in deduplicated if item.type == "shorts")
    print(f"\n📊 Shorts count: {shorts_count}")
    
    if shorts_count > 1:
        print("❌ ERROR: Still have duplicate shorts!")
        return False
    else:
        print("✅ SUCCESS: No duplicate shorts!")
        return True

if __name__ == "__main__":
    success = test_deduplication()
    sys.exit(0 if success else 1) 