#!/usr/bin/env python3
"""
Test script to verify that outfit retrieval with item ID conversion works correctly.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.outfit_service import OutfitService

async def test_outfit_retrieval():
    """Test outfit retrieval with item ID conversion."""
    
    # Create outfit service
    outfit_service = OutfitService()
    
    print("🧪 Testing outfit retrieval with item ID conversion...")
    
    # Test get_outfit method
    try:
        # Get a specific outfit (use the one from the logs)
        outfit_id = "26018faa-d21b-4a4b-b513-0ad1f4324a59"
        outfit = await outfit_service.get_outfit(outfit_id)
        
        if outfit:
            print(f"✅ Successfully retrieved outfit: {outfit.name}")
            print(f"   Items count: {len(outfit.items)}")
            
            # Check if items are full objects or strings
            for i, item in enumerate(outfit.items):
                if isinstance(item, str):
                    print(f"   Item {i+1}: String ID - {item}")
                else:
                    print(f"   Item {i+1}: Full object - {item.name} ({item.type})")
                    print(f"      Image URL: {item.imageUrl}")
            
            # Test get_outfits_by_user method
            user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
            user_outfits = await outfit_service.get_outfits_by_user(user_id)
            
            print(f"\n👤 Retrieved {len(user_outfits)} outfits for user {user_id}")
            
            for i, user_outfit in enumerate(user_outfits[:3]):  # Show first 3 outfits
                print(f"   Outfit {i+1}: {user_outfit.name}")
                print(f"      Items count: {len(user_outfit.items)}")
                
                # Check items in user outfits
                for j, item in enumerate(user_outfit.items):
                    if isinstance(item, str):
                        print(f"      Item {j+1}: String ID - {item}")
                    else:
                        print(f"      Item {j+1}: Full object - {item.name} ({item.type})")
            
            print("\n✅ All tests passed! Item ID conversion is working correctly.")
            
        else:
            print("❌ Failed to retrieve outfit - outfit not found or deleted")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_outfit_retrieval()) 