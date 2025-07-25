#!/usr/bin/env python3
"""
Manual Fashion Trends Fetch Script

This script manually triggers a fashion trends fetch for testing purposes.

Usage:
    python manual_fetch_trends.py

This will:
- Fetch current fashion trends from Google Trends
- Store them in Firestore
- Display the results
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

async def main():
    try:
        from services.fashion_trends_service import FashionTrendsService
        
        print("🔄 Manually fetching fashion trends...")
        print("-" * 50)
        
        # Create service instance
        trends_service = FashionTrendsService()
        
        # Fetch trends
        result = await trends_service.fetch_and_store_trends()
        
        # Display results
        print(f"📊 Fetch Result: {result['status']}")
        
        if result["status"] == "success":
            print(f"✅ Successfully fetched {result['trends_fetched']} trends")
            print(f"⏰ Timestamp: {result['timestamp']}")
            
            # Get and display some trending styles
            print("\n🎨 Current Trending Styles:")
            trending_styles = await trends_service.get_trending_styles()
            
            for i, style in enumerate(trending_styles[:10], 1):
                print(f"{i:2d}. {style['name']} (Popularity: {style['popularity']})")
                print(f"    {style['description']}")
                print(f"    Trend: {style['trend_direction']}")
                print()
                
        elif result["status"] == "skipped":
            print(f"⏭️ Skipped: {result['reason']}")
            
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Check for Firebase credentials
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠️  Warning: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("Please set the path to your Firebase service account key file")
        print("Example: export GOOGLE_APPLICATION_CREDENTIALS='path/to/serviceAccountKey.json'")
        print()
    
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 