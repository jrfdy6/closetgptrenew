#!/usr/bin/env python3
"""
Check wardrobe data in Firestore for debugging
"""

import os
import sys
import json
from datetime import datetime

# Add the backend src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

try:
    from firebase_admin import credentials, firestore, initialize_app
    from config.firebase import get_firestore_client
    
    print("🔍 Checking wardrobe data in Firestore...")
    
    # Initialize Firebase
    try:
        # Try to get existing app
        app = initialize_app()
    except ValueError:
        # App already exists
        pass
    
    db = get_firestore_client()
    
    # Check wardrobe collection
    print("\n📁 Checking wardrobe collection...")
    wardrobe_ref = db.collection('wardrobe')
    
    # Get all documents
    docs = wardrobe_ref.stream()
    total_docs = 0
    user_docs = 0
    user_items = []
    
    for doc in docs:
        total_docs += 1
        data = doc.to_dict()
        
        if data.get('userId') == 'dANqjiI0CKgaitxzYtw1bhtvQrG3':
            user_docs += 1
            user_items.append({
                'id': doc.id,
                'name': data.get('name', 'Unknown'),
                'type': data.get('type', 'Unknown'),
                'color': data.get('color', 'Unknown'),
                'createdAt': data.get('createdAt', 'Unknown')
            })
    
    print(f"📊 Total wardrobe documents: {total_docs}")
    print(f"👤 Documents for user dANqjiI0CKgaitxzYtw1bhtvQrG3: {user_docs}")
    
    if user_items:
        print(f"\n👕 User's wardrobe items:")
        for i, item in enumerate(user_items[:10]):  # Show first 10
            print(f"  {i+1}. {item['name']} ({item['type']}) - {item['color']}")
        
        if len(user_items) > 10:
            print(f"  ... and {len(user_items) - 10} more items")
    else:
        print("❌ No wardrobe items found for user dANqjiI0CKgaitxzYtw1bhtvQrG3")
    
    # Check outfits collection too
    print("\n👗 Checking outfits collection...")
    outfits_ref = db.collection('outfits')
    outfit_docs = outfits_ref.where('userId', '==', 'dANqjiI0CKgaitxzYtw1bhtvQrG3').stream()
    
    outfit_count = 0
    for doc in outfit_docs:
        outfit_count += 1
    
    print(f"👗 Outfits for user: {outfit_count}")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"  - Wardrobe items: {user_docs}")
    print(f"  - Outfits: {outfit_count}")
    
    if user_docs == 0:
        print("\n❌ PROBLEM: User has no wardrobe items!")
        print("   This explains why the dashboard is failing.")
        print("   The backend returns empty stats when there are no items.")
    else:
        print(f"\n✅ User has {user_docs} wardrobe items - data should be available")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()