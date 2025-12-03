#!/usr/bin/env python3
"""
Quick Outfit Search - Simple command-line tool for searching outfits in Firebase
Usage: python quick_outfit_search.py [user_id] [occasion] [style]
"""

import os
import sys
import argparse
from typing import List, Dict, Any

# Add the backend src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

try:
    from config.firebase import db, firebase_initialized, initialize_firebase
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def search_outfits(user_id: str = None, occasion: str = None, style: str = None, limit: int = 20):
    """Search for outfits with the given criteria"""
    
    if not firebase_initialized:
        print("🔥 Initializing Firebase...")
        if not initialize_firebase():
            print("❌ Failed to initialize Firebase")
            return
    
    print("🔍 Searching for outfits...")
    
    try:
        # Start with the outfits collection
        query = db.collection('outfits')
        
        # Add filters
        if user_id:
            print(f"   Filtering by user ID: {user_id}")
            query = query.where('user_id', '==', user_id)
        
        if occasion:
            print(f"   Filtering by occasion: {occasion}")
            query = query.where('occasion', '==', occasion)
        
        if style:
            print(f"   Filtering by style: {style}")
            query = query.where('style', '==', style)
        
        # Execute query
        outfits = query.limit(limit).stream()
        
        outfit_list = []
        for doc in outfits:
            outfit_data = doc.to_dict()
            outfit_data['id'] = doc.id
            outfit_list.append(outfit_data)
        
        print(f"\n✅ Found {len(outfit_list)} outfits")
        
        if outfit_list:
            print("\n📋 Outfit Details:")
            for i, outfit in enumerate(outfit_list, 1):
                print(f"\n{i}. {outfit.get('name', 'Unnamed Outfit')} (ID: {outfit.get('id', 'N/A')})")
                print(f"   Occasion: {outfit.get('occasion', 'N/A')}")
                print(f"   Style: {outfit.get('style', 'N/A')}")
                print(f"   User ID: {outfit.get('user_id', 'N/A')}")
                print(f"   Items: {len(outfit.get('items', []))}")
                
                # Show first few items
                items = outfit.get('items', [])
                if items:
                    print("   Items:")
                    for j, item in enumerate(items[:3]):  # Show first 3 items
                        if isinstance(item, dict):
                            print(f"     - {item.get('category', 'Unknown')}: {item.get('name', 'Unnamed')}")
                        else:
                            print(f"     - Item ID: {item}")
                    if len(items) > 3:
                        print(f"     ... and {len(items) - 3} more items")
        
        return outfit_list
        
    except Exception as e:
        print(f"❌ Error searching outfits: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Search for outfits in Firebase')
    parser.add_argument('--user-id', '-u', help='User ID to filter by')
    parser.add_argument('--occasion', '-o', help='Occasion to filter by (e.g., casual, formal)')
    parser.add_argument('--style', '-s', help='Style to filter by (e.g., bohemian, classic)')
    parser.add_argument('--limit', '-l', type=int, default=20, help='Maximum number of results (default: 20)')
    parser.add_argument('--all', '-a', action='store_true', help='Show all outfits without filters')
    
    args = parser.parse_args()
    
    if args.all:
        print("🔍 Getting all outfits...")
        search_outfits(limit=args.limit)
    elif args.user_id or args.occasion or args.style:
        search_outfits(
            user_id=args.user_id,
            occasion=args.occasion,
            style=args.style,
            limit=args.limit
        )
    else:
        print("🔍 No filters specified. Use --help for usage information.")
        print("\nExample usage:")
        print("  python quick_outfit_search.py --user-id abc123")
        print("  python quick_outfit_search.py --occasion casual --style bohemian")
        print("  python quick_outfit_search.py --all")

if __name__ == "__main__":
    main()
