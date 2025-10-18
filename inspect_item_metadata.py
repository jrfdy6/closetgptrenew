#!/usr/bin/env python3
"""
Inspect Individual Item Metadata
=================================

Quick tool to check metadata for a specific wardrobe item.
Useful for spot-checking and debugging.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from google.cloud import firestore
import json

db = firestore.Client()
USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"


def inspect_item(search_term):
    """Search for and inspect an item by name."""
    
    print(f"\n🔍 Searching for: '{search_term}'")
    print("=" * 100)
    
    # Get all wardrobe items
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', USER_ID)
    docs = wardrobe_ref.stream()
    
    # Find matching items
    matches = []
    for doc in docs:
        item_data = doc.to_dict()
        item_name = item_data.get('name', '').lower()
        if search_term.lower() in item_name:
            matches.append((doc.id, item_data))
    
    if not matches:
        print(f"❌ No items found matching '{search_term}'")
        return
    
    print(f"✅ Found {len(matches)} matching item(s)\n")
    
    # Display each match
    for idx, (doc_id, item) in enumerate(matches, 1):
        print(f"\n{'=' * 100}")
        print(f"ITEM #{idx}: {item.get('name', 'Unknown')}")
        print(f"{'=' * 100}")
        
        # Basic info
        print(f"\n📋 BASIC INFO:")
        print(f"  ID:         {doc_id}")
        print(f"  Name:       {item.get('name', 'N/A')}")
        print(f"  Type:       {item.get('type', 'N/A')}")
        print(f"  Color:      {item.get('color', 'N/A')}")
        print(f"  Brand:      {item.get('brand', 'N/A')}")
        
        # Tags vs Structured Fields
        print(f"\n🏷️  TAGS vs STRUCTURED FIELDS:")
        print(f"  tags:       {item.get('tags', [])}")
        print(f"  -----")
        print(f"  occasion:   {item.get('occasion', [])} {'✅' if item.get('occasion') else '❌ EMPTY'}")
        print(f"  style:      {item.get('style', [])} {'✅' if item.get('style') else '❌ EMPTY'}")
        print(f"  mood:       {item.get('mood', [])} {'✅' if item.get('mood') else '❌ EMPTY'}")
        print(f"  season:     {item.get('season', [])} {'✅' if item.get('season') else '❌ EMPTY'}")
        
        # Metadata object
        metadata = item.get('metadata', {})
        if not metadata:
            print(f"\n❌ NO METADATA OBJECT")
        else:
            print(f"\n✅ METADATA OBJECT EXISTS")
            
            # Visual Attributes
            visual_attrs = metadata.get('visualAttributes', {})
            if not visual_attrs:
                print(f"\n  ❌ NO VISUAL ATTRIBUTES")
            else:
                print(f"\n  ✅ VISUAL ATTRIBUTES:")
                print(f"    wearLayer:      {visual_attrs.get('wearLayer', 'N/A')}")
                print(f"    sleeveLength:   {visual_attrs.get('sleeveLength', 'N/A')}")
                print(f"    pattern:        {visual_attrs.get('pattern', 'N/A')}")
                print(f"    material:       {visual_attrs.get('material', 'N/A')}")
                print(f"    fit:            {visual_attrs.get('fit', 'N/A')}")
                print(f"    formalLevel:    {visual_attrs.get('formalLevel', 'N/A')}")
                print(f"    fabricWeight:   {visual_attrs.get('fabricWeight', 'N/A')}")
                print(f"    textureStyle:   {visual_attrs.get('textureStyle', 'N/A')}")
                print(f"    silhouette:     {visual_attrs.get('silhouette', 'N/A')}")
                print(f"    length:         {visual_attrs.get('length', 'N/A')}")
            
            # Normalized metadata
            normalized = metadata.get('normalized', {})
            if not normalized:
                print(f"\n  ⚠️  NO NORMALIZED METADATA")
            else:
                print(f"\n  ✅ NORMALIZED METADATA:")
                print(f"    occasion:   {normalized.get('occasion', 'N/A')}")
                print(f"    style:      {normalized.get('style', 'N/A')}")
                print(f"    mood:       {normalized.get('mood', 'N/A')}")
            
            # Natural description
            natural_desc = metadata.get('naturalDescription')
            if natural_desc:
                print(f"\n  ✅ NATURAL DESCRIPTION:")
                print(f"    {natural_desc}")
        
        # Compatibility scores
        print(f"\n📊 COMPATIBILITY SCORES:")
        body_comp = item.get('bodyTypeCompatibility')
        weather_comp = item.get('weatherCompatibility')
        print(f"  bodyTypeCompatibility:   {body_comp if body_comp else '❌ Not set'}")
        print(f"  weatherCompatibility:    {weather_comp if weather_comp else '❌ Not set'}")
        
        # Usage stats
        print(f"\n📈 USAGE STATS:")
        print(f"  wearCount:      {item.get('wearCount', 0)}")
        print(f"  lastWorn:       {item.get('lastWorn', 'Never')}")
        print(f"  favorite_score: {item.get('favorite_score', 0)}")
        
        # Outfit Generation Assessment
        print(f"\n🎯 OUTFIT GENERATION READINESS:")
        
        checks = {
            'Has occasion field': bool(item.get('occasion')),
            'Has style field': bool(item.get('style')),
            'Has metadata object': bool(metadata),
            'Has visualAttributes': bool(metadata.get('visualAttributes')) if metadata else False,
            'Has wearLayer': bool(metadata.get('visualAttributes', {}).get('wearLayer')) if metadata else False,
            'Has sleeveLength': bool(metadata.get('visualAttributes', {}).get('sleeveLength')) if metadata else False,
            'Has pattern': bool(metadata.get('visualAttributes', {}).get('pattern')) if metadata else False,
            'Has material': bool(metadata.get('visualAttributes', {}).get('material')) if metadata else False,
        }
        
        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        
        for check, status in checks.items():
            symbol = "✅" if status else "❌"
            print(f"  {symbol} {check}")
        
        print(f"\n  READINESS SCORE: {passed}/{total} ({passed/total*100:.0f}%)")
        
        if passed == total:
            print(f"  🎉 FULLY READY for outfit generation!")
        elif passed >= 6:
            print(f"  ✅ GOOD - Will work in outfit generation")
        elif passed >= 4:
            print(f"  ⚠️  PARTIAL - May have limited compatibility")
        else:
            print(f"  ❌ NOT READY - Needs metadata backfill")
        
        # Export option
        if len(matches) == 1:
            print(f"\n💾 EXPORT:")
            export_file = f"item_{doc_id[:8]}_metadata.json"
            with open(export_file, 'w') as f:
                json.dump(item, f, indent=2, default=str)
            print(f"  Full data exported to: {export_file}")


def list_recent_items(limit=10):
    """List recent items for inspection."""
    
    print(f"\n📋 SAMPLE ITEMS (First {limit}):")
    print("=" * 100)
    
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', USER_ID).limit(limit)
    docs = wardrobe_ref.stream()
    
    items = []
    for doc in docs:
        item_data = doc.to_dict()
        items.append({
            'name': item_data.get('name', 'Unknown')[:50],
            'type': item_data.get('type', 'N/A'),
            'has_occasion': bool(item_data.get('occasion')),
            'has_style': bool(item_data.get('style')),
            'has_metadata': bool(item_data.get('metadata')),
        })
    
    print(f"\nFound {len(items)} items:\n")
    for idx, item in enumerate(items, 1):
        occ = "✅" if item['has_occasion'] else "❌"
        sty = "✅" if item['has_style'] else "❌"
        meta = "✅" if item['has_metadata'] else "❌"
        print(f"{idx:2}. {item['name']:50} ({item['type']:15}) | Occ:{occ} Sty:{sty} Meta:{meta}")
    
    print(f"\nTo inspect an item, run: python3 inspect_item_metadata.py 'item name'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # No search term provided, list recent items
        list_recent_items()
    else:
        # Search for specific item
        search_term = ' '.join(sys.argv[1:])
        inspect_item(search_term)

