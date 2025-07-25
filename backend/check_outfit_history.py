#!/usr/bin/env python3
"""
Script to check outfit history in the database
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.outfit_service import OutfitService

async def check_outfit_history():
    """Check outfit history in the database"""
    try:
        outfit_service = OutfitService()
        
        # Get all outfits (before user filtering)
        print("🔍 Checking all outfits in database...")
        all_outfits = await outfit_service.get_outfits()
        print(f"📊 Total outfits in database: {len(all_outfits)}")
        
        if all_outfits:
            print("\n📋 Sample outfits:")
            for i, outfit in enumerate(all_outfits[:5]):  # Show first 5
                print(f"  {i+1}. {outfit.name} (ID: {outfit.id})")
                print(f"     - Created: {outfit.createdAt}")
                print(f"     - Occasion: {outfit.occasion}")
                print(f"     - Items: {len(outfit.items)}")
                if hasattr(outfit, 'user_id'):
                    print(f"     - User ID: {outfit.user_id}")
                else:
                    print(f"     - User ID: NOT SET")
                print()
        
        # Check for outfits with user_id field
        outfits_with_user_id = [o for o in all_outfits if hasattr(o, 'user_id') and o.user_id]
        print(f"🎯 Outfits with user_id field: {len(outfits_with_user_id)}")
        
        # Check for outfits without user_id field
        outfits_without_user_id = [o for o in all_outfits if not hasattr(o, 'user_id') or not o.user_id]
        print(f"⚠️  Outfits without user_id field: {len(outfits_without_user_id)}")
        
        # Check recent outfits (last 7 days)
        import time
        cutoff_time = time.time() - (7 * 24 * 60 * 60)
        recent_outfits = [o for o in all_outfits if o.createdAt >= cutoff_time]
        print(f"📅 Recent outfits (last 7 days): {len(recent_outfits)}")
        
        # Check successful vs failed outfits
        successful_outfits = [o for o in all_outfits if hasattr(o, 'wasSuccessful') and o.wasSuccessful]
        failed_outfits = [o for o in all_outfits if hasattr(o, 'wasSuccessful') and not o.wasSuccessful]
        print(f"✅ Successful outfits: {len(successful_outfits)}")
        print(f"❌ Failed outfits: {len(failed_outfits)}")
        
    except Exception as e:
        print(f"❌ Error checking outfit history: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_outfit_history()) 