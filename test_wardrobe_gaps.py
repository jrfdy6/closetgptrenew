#!/usr/bin/env python3
"""
Test script to check wardrobe gap analysis
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_wardrobe_gaps():
    try:
        from backend.src.services.wardrobe_analysis_service import WardrobeAnalysisService
        
        print("🔍 Testing wardrobe gap analysis...")
        
        # Create service instance
        service = WardrobeAnalysisService()
        
        # Test with a sample user ID (you can replace this with a real user ID)
        test_user_id = "test_user_123"
        
        print(f"📊 Analyzing gaps for user: {test_user_id}")
        
        # Get wardrobe gaps
        result = await service.get_wardrobe_gaps(test_user_id)
        
        print(f"✅ Analysis completed!")
        print(f"📈 Gaps found: {len(result.get('gaps', []))}")
        print(f"🛍️ Shopping recommendations: {'Yes' if result.get('shopping_recommendations') else 'No'}")
        
        if result.get('gaps'):
            print("\n🔍 Gaps identified:")
            for i, gap in enumerate(result['gaps']):
                print(f"  {i+1}. {gap.get('category', 'Unknown')} - {gap.get('priority', 'Unknown')} priority")
        
        if result.get('shopping_recommendations'):
            recs = result['shopping_recommendations']
            print(f"\n🛍️ Shopping recommendations:")
            print(f"  - Success: {recs.get('success', False)}")
            print(f"  - Total cost: ${recs.get('total_estimated_cost', 0)}")
            print(f"  - Budget range: {recs.get('budget_range', 'Unknown')}")
            print(f"  - Recommendations count: {len(recs.get('recommendations', []))}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing wardrobe gaps: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_wardrobe_gaps())
