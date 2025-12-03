#!/usr/bin/env python3
"""
Fetch actual jacket metadata to show how jackets are represented.
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def get_firestore_client():
    """Initialize and return Firestore client."""
    if not firebase_admin._apps:
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        else:
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    return firestore.client()

def get_jacket_metadata(user_id: str = "dANqjiI0CKgaitxzYtw1bhtvQrG3"):
    """Get metadata for jackets."""
    db = get_firestore_client()
    
    # Find jackets
    wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
    items = list(wardrobe_ref.stream())
    
    jackets = []
    for doc in items:
        data = doc.to_dict()
        item_type = data.get('type', '').lower()
        item_name = data.get('name', '').lower()
        
        if 'jacket' in item_type or 'jacket' in item_name or 'blazer' in item_type or 'blazer' in item_name:
            jackets.append({
                'id': doc.id,
                'data': data
            })
    
    print(f"🔍 Found {len(jackets)} jacket items\n")
    
    # Show the two jackets from the outfit
    target_jackets = [
        "A slim, long, solid, smooth jacket",  # Dark Teal
        "A slim, long, solid, smooth jacket by The Savile Row Company"  # Charcoal
    ]
    
    for i, jacket in enumerate(jackets[:5]):  # Show first 5 jackets
        data = jacket['data']
        name = data.get('name', 'Unknown')
        
        print("=" * 80)
        print(f"JACKET {i+1}: {name}")
        print("=" * 80)
        
        # Show key fields
        print(f"\n📋 CORE FIELDS:")
        print(f"  id: {jacket['id']}")
        print(f"  type: {data.get('type')}")
        print(f"  subtype: {data.get('subtype')}")
        print(f"  name: {data.get('name')}")
        print(f"  color: {data.get('color')}")
        
        # Show metadata fields
        metadata = data.get('metadata', {})
        print(f"\n📦 METADATA FIELDS:")
        print(f"  metadata.visualAttributes: {metadata.get('visualAttributes') is not None}")
        
        if metadata.get('visualAttributes'):
            va = metadata['visualAttributes']
            print(f"    wearLayer: {va.get('wearLayer')}")
            print(f"    sleeveLength: {va.get('sleeveLength')}")
            print(f"    fit: {va.get('fit')}")
            print(f"    pattern: {va.get('pattern')}")
            print(f"    formalLevel: {va.get('formalLevel')}")
        
        # Show normalized fields
        if metadata.get('normalized'):
            norm = metadata['normalized']
            print(f"\n  metadata.normalized:")
            print(f"    occasion: {norm.get('occasion')}")
            print(f"    style: {norm.get('style')}")
            print(f"    layer: {norm.get('layer')}")
        
        # Show root-level fields
        print(f"\n🎯 ROOT-LEVEL FIELDS:")
        print(f"  occasion: {data.get('occasion')}")
        print(f"  style: {data.get('style')}")
        print(f"  season: {data.get('season')}")
        print(f"  mood: {data.get('mood')}")
        
        # Full JSON (abbreviated)
        print(f"\n📄 FULL METADATA STRUCTURE:")
        
        # Create abbreviated version
        abbreviated = {
            'id': jacket['id'],
            'type': data.get('type'),
            'subtype': data.get('subtype'),
            'name': data.get('name'),
            'color': data.get('color'),
            'occasion': data.get('occasion'),
            'style': data.get('style'),
            'season': data.get('season'),
            'mood': data.get('mood'),
            'metadata': {
                'visualAttributes': metadata.get('visualAttributes', {}),
                'normalized': metadata.get('normalized', {})
            }
        }
        
        print(json.dumps(abbreviated, indent=2))
        print("\n")
    
    # Save full jacket data
    with open('jacket_metadata_examples.json', 'w') as f:
        json.dump([j['data'] for j in jackets[:5]], f, indent=2, default=str)
    
    print("=" * 80)
    print("✅ Full jacket metadata saved to: jacket_metadata_examples.json")
    print("=" * 80)

if __name__ == "__main__":
    get_jacket_metadata()

