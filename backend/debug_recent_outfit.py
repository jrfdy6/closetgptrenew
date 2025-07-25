#!/usr/bin/env python3
"""Debug script to extract generation trace from recent outfit."""

import asyncio
from src.config.firebase import db
from src.services.outfit_service import OutfitService

async def debug_recent_outfit():
    """Extract generation trace from the most recent outfit."""
    outfit_service = OutfitService()
    
    # Get the specific outfit ID from the logs
    outfit_id = "52849360-d8ba-4f83-85a4-ff9d43087977"
    
    print(f"🔍 Debugging outfit: {outfit_id}")
    print("=" * 50)
    
    try:
        # Get the outfit
        outfit = await outfit_service.get_outfit(outfit_id)
        
        if not outfit:
            print("❌ Outfit not found")
            return
        
        print(f"📋 Outfit Details:")
        print(f"  - Name: {outfit.name}")
        print(f"  - Occasion: {outfit.occasion}")
        print(f"  - Style: {outfit.style}")
        print(f"  - Items: {len(outfit.items)}")
        print(f"  - Generation Method: {outfit.generation_method}")
        print(f"  - Was Successful: {outfit.wasSuccessful}")
        
        if hasattr(outfit, 'generation_trace') and outfit.generation_trace:
            print(f"\n🔍 Generation Trace ({len(outfit.generation_trace)} steps):")
            print("=" * 50)
            
            for i, step in enumerate(outfit.generation_trace, 1):
                print(f"\n📝 Step {i}:")
                print(f"  - Phase: {step.get('phase', 'unknown')}")
                print(f"  - Method: {step.get('method', 'unknown')}")
                print(f"  - Success: {step.get('success', 'unknown')}")
                
                if 'params' in step and step['params']:
                    print(f"  - Params: {step['params']}")
                
                if 'result' in step and step['result']:
                    result = step['result']
                    if isinstance(result, dict):
                        if 'items_selected' in result:
                            print(f"  - Items Selected: {result['items_selected']}")
                        if 'filtered_count' in result:
                            print(f"  - Filtered Count: {result['filtered_count']}")
                        if 'errors' in result:
                            print(f"  - Errors: {result['errors']}")
                    else:
                        print(f"  - Result: {result}")
                
                if 'duration' in step and step['duration'] is not None:
                    print(f"  - Duration: {step['duration']:.3f}s")
        
        if hasattr(outfit, 'validation_details') and outfit.validation_details:
            print(f"\n⚠️ Validation Details:")
            print("=" * 50)
            for key, value in outfit.validation_details.items():
                print(f"  - {key}: {value}")
        
        if hasattr(outfit, 'wardrobe_snapshot') and outfit.wardrobe_snapshot:
            print(f"\n👕 Wardrobe Snapshot:")
            print("=" * 50)
            wardrobe = outfit.wardrobe_snapshot
            print(f"  - Total Items: {len(wardrobe.get('items', []))}")
            
            # Show first few items
            items = wardrobe.get('items', [])
            for i, item in enumerate(items[:5]):
                print(f"  - Item {i+1}: {item.get('name', 'unknown')} ({item.get('type', 'unknown')})")
            
            if len(items) > 5:
                print(f"  - ... and {len(items) - 5} more items")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_recent_outfit()) 