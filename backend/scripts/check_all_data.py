#!/usr/bin/env python3
"""
Check for all data in the database without user filtering.
This will help identify if data exists but is filtered by user ID.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app
import json

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

def check_all_data():
    """Check for all data without any filtering."""
    print("🔍 Checking All Data (No User Filtering)")
    print("=" * 50)
    
    collections = ['wardrobe', 'outfits', 'users', 'analytics_events', 'style_profiles']
    
    for collection in collections:
        print(f"\n📁 {collection.upper()} Collection:")
        print("-" * 30)
        
        try:
            # Get ALL documents without any filtering
            docs = list(db.collection(collection).stream())
            total = len(docs)
            
            print(f"Total documents: {total}")
            
            if total > 0:
                # Show first few documents
                for i, doc in enumerate(docs[:5]):  # Show first 5
                    data = doc.to_dict()
                    print(f"  Document {i+1}: {doc.id}")
                    
                    # Show key fields
                    if 'userId' in data:
                        print(f"    User ID: {data['userId']}")
                    if 'name' in data:
                        print(f"    Name: {data['name']}")
                    if 'type' in data:
                        print(f"    Type: {data['type']}")
                    if 'occasion' in data:
                        print(f"    Occasion: {data['occasion']}")
                    if 'createdAt' in data:
                        print(f"    Created: {data['createdAt']}")
                    
                    # Show all keys for first document
                    if i == 0:
                        print(f"    All keys: {list(data.keys())}")
                    
                    print()
                
                if total > 5:
                    print(f"  ... and {total - 5} more documents")
            else:
                print("  No documents found")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def check_user_specific_data():
    """Check if data exists but is filtered by specific user IDs."""
    print(f"\n👤 Checking User-Specific Data:")
    print("=" * 40)
    
    # Check outfits collection for user IDs
    try:
        outfits = list(db.collection('outfits').stream())
        user_ids = set()
        
        for doc in outfits:
            data = doc.to_dict()
            if 'userId' in data:
                user_ids.add(data['userId'])
        
        print(f"Found {len(user_ids)} unique user IDs in outfits:")
        for user_id in user_ids:
            print(f"  - {user_id}")
            
            # Count outfits for this user
            user_outfits = list(db.collection('outfits').where('userId', '==', user_id).stream())
            print(f"    Outfits: {len(user_outfits)}")
            
            # Check if this user has wardrobe items
            user_wardrobe = list(db.collection('wardrobe').where('userId', '==', user_id).stream())
            print(f"    Wardrobe items: {len(user_wardrobe)}")
            
    except Exception as e:
        print(f"❌ Error checking user data: {e}")

def check_collection_rules():
    """Check Firestore security rules that might be filtering data."""
    print(f"\n🔒 Checking Collection Access:")
    print("=" * 40)
    
    collections = ['wardrobe', 'outfits', 'users']
    
    for collection in collections:
        try:
            # Try to get collection metadata
            docs = list(db.collection(collection).limit(1).stream())
            print(f"✅ {collection}: Accessible ({len(docs)} docs)")
            
            if len(docs) > 0:
                # Check if documents have userId field
                doc_data = docs[0].to_dict()
                if 'userId' in doc_data:
                    print(f"   Has userId field: {doc_data['userId']}")
                else:
                    print(f"   No userId field")
                    
        except Exception as e:
            print(f"❌ {collection}: {e}")

if __name__ == "__main__":
    check_all_data()
    check_user_specific_data()
    check_collection_rules()
    
    print(f"\n💡 Analysis:")
    print("=" * 30)
    print("If you see data with specific user IDs, the issue might be:")
    print("1. User authentication not working in the app")
    print("2. Frontend filtering by wrong user ID")
    print("3. Data belongs to different users")
    print("4. Need to check the frontend's user authentication") 