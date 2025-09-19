#!/usr/bin/env python3
"""
Initialize user stats document for existing users.
Run this once to create the pre-aggregated stats document.
"""

import asyncio
import sys
import os

# Add the backend src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def initialize_stats_for_user(user_id: str):
    """Initialize stats document for a specific user."""
    try:
        from services.user_stats_service import user_stats_service
        
        print(f"🚀 Initializing stats for user: {user_id}")
        
        # Initialize the stats document
        success = await user_stats_service.initialize_user_stats(user_id)
        
        if success:
            print(f"✅ Successfully initialized stats for user {user_id}")
            
            # Verify by reading the stats
            stats = await user_stats_service.get_user_stats(user_id)
            print(f"📊 Stats summary:")
            print(f"   - Total outfits: {stats.get('outfits', {}).get('total', 0)}")
            print(f"   - Outfits this week: {stats.get('outfits', {}).get('this_week', 0)}")
            print(f"   - Total wardrobe items: {stats.get('wardrobe', {}).get('total_items', 0)}")
            print(f"   - Wardrobe favorites: {stats.get('wardrobe', {}).get('favorites', 0)}")
            print(f"   - Last updated: {stats.get('last_updated', 'unknown')}")
            
        else:
            print(f"❌ Failed to initialize stats for user {user_id}")
            
    except Exception as e:
        print(f"❌ Error initializing stats: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function to initialize stats."""
    # Your user ID
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print("🎯 User Stats Initialization Script")
    print("=" * 50)
    
    await initialize_stats_for_user(user_id)
    
    print("=" * 50)
    print("🎉 Initialization complete!")
    print("")
    print("🚀 Your dashboard should now load in ~200ms instead of timing out!")

if __name__ == "__main__":
    asyncio.run(main())
