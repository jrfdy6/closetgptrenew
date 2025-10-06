#!/usr/bin/env python3
"""
Backfill Script: Normalize Existing Wardrobe Items
This script normalizes existing wardrobe items in Firestore to ensure
consistent formatting for semantic filtering.
"""

import sys
import os
import time
from typing import Dict, Any, List

# Add the backend src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

def normalize_array_strings(arr):
    """Normalize array of strings to lowercase and trim."""
    if not arr:
        return []
    return [
        s.strip().lower() 
        for s in arr 
        if isinstance(s, str) and s.strip()
    ]

def canonicalize_style(s):
    """Canonicalize a style string to lowercase."""
    return s.strip().lower()

def normalize_item_metadata(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize item metadata for semantic filtering."""
    # Handle both dict and object types
    if hasattr(item, '__dict__'):
        base_data = item.__dict__.copy()
    elif isinstance(item, dict):
        base_data = item.copy()
    else:
        base_data = {}
    
    return {
        **base_data,
        'style': normalize_array_strings(item.get('style', [])),
        'occasion': normalize_array_strings(item.get('occasion', [])),
        'mood': normalize_array_strings(item.get('mood', [])),
        'season': normalize_array_strings(item.get('season', [])),
    }

def backfill_wardrobe_items():
    """Backfill existing wardrobe items with normalized metadata."""
    try:
        # Import Firebase
        from config.firebase import db, firebase_initialized
        
        if not firebase_initialized:
            print("❌ Firebase not initialized")
            return False
        
        print("🔄 Starting wardrobe items backfill...")
        
        # Get all wardrobe items
        wardrobe_ref = db.collection('wardrobe')
        docs = wardrobe_ref.stream()
        
        total_items = 0
        normalized_items = 0
        errors = 0
        
        for doc in docs:
            total_items += 1
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            
            try:
                # Check if item needs normalization
                needs_normalization = False
                
                # Check style field
                if 'style' in item_data:
                    style = item_data['style']
                    if isinstance(style, list):
                        for s in style:
                            if isinstance(s, str) and (s != s.strip().lower() or s != s.strip()):
                                needs_normalization = True
                                break
                    elif isinstance(style, str) and (style != style.strip().lower() or style != style.strip()):
                        needs_normalization = True
                
                # Check occasion field
                if 'occasion' in item_data:
                    occasion = item_data['occasion']
                    if isinstance(occasion, list):
                        for o in occasion:
                            if isinstance(o, str) and (o != o.strip().lower() or o != o.strip()):
                                needs_normalization = True
                                break
                    elif isinstance(occasion, str) and (occasion != occasion.strip().lower() or occasion != occasion.strip()):
                        needs_normalization = True
                
                # Check season field
                if 'season' in item_data:
                    season = item_data['season']
                    if isinstance(season, list):
                        for s in season:
                            if isinstance(s, str) and (s != s.strip().lower() or s != s.strip()):
                                needs_normalization = True
                                break
                    elif isinstance(season, str) and (season != season.strip().lower() or season != season.strip()):
                        needs_normalization = True
                
                if needs_normalization:
                    # Normalize the item
                    normalized_item = normalize_item_metadata(item_data)
                    
                    # Update the document
                    doc.reference.set(normalized_item)
                    normalized_items += 1
                    
                    print(f"✅ Normalized item {doc.id}: {item_data.get('name', 'Unknown')}")
                else:
                    print(f"⏭️  Item {doc.id} already normalized: {item_data.get('name', 'Unknown')}")
                
            except Exception as e:
                errors += 1
                print(f"❌ Error processing item {doc.id}: {e}")
        
        print(f"\n📊 Backfill Summary:")
        print(f"  Total items processed: {total_items}")
        print(f"  Items normalized: {normalized_items}")
        print(f"  Errors: {errors}")
        print(f"  Success rate: {((total_items - errors) / total_items * 100):.1f}%")
        
        return errors == 0
        
    except Exception as e:
        print(f"❌ Backfill failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Wardrobe Items Normalization Backfill")
    print("=" * 50)
    
    # Confirm before proceeding
    response = input("This will update existing wardrobe items. Continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Backfill cancelled")
        return False
    
    # Run backfill
    success = backfill_wardrobe_items()
    
    if success:
        print("\n🎉 Backfill completed successfully!")
    else:
        print("\n⚠️  Backfill completed with errors")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)