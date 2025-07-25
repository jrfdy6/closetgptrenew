#!/usr/bin/env python3
"""
Check outfits for a specific user ID using the new user_id field.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app
import json

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

def check_specific_user_outfits(user_id: str):
    """Check outfits for a specific user ID."""
    print(f"🔍 Checking outfits for user: {user_id}")
    print("=" * 60)
    
    try:
        # Check outfits with new user_id field
        outfits_with_user_id = list(db.collection('outfits').where('user_id', '==', user_id).stream())
        print(f"📊 Outfits with 'user_id' field: {len(outfits_with_user_id)}")
        
        # Check outfits with old userId field (just in case)
        outfits_with_userId = list(db.collection('outfits').where('userId', '==', user_id).stream())
        print(f"📊 Outfits with 'userId' field: {len(outfits_with_userId)}")
        
        # Get all outfits and check manually
        all_outfits = list(db.collection('outfits').stream())
        print(f"📊 Total outfits in database: {len(all_outfits)}")
        
        # Manual check for the specific user
        user_outfits = []
        for doc in all_outfits:
            data = doc.to_dict()
            if data.get('user_id') == user_id or data.get('userId') == user_id:
                user_outfits.append(doc)
        
        print(f"📊 Total outfits for user {user_id}: {len(user_outfits)}")
        
        if user_outfits:
            print(f"\n📋 Outfit details:")
            for i, doc in enumerate(user_outfits[:10]):  # Show first 10
                data = doc.to_dict()
                print(f"  {i+1}. {data.get('name', 'No name')}")
                print(f"     - ID: {doc.id}")
                print(f"     - Occasion: {data.get('occasion', 'No occasion')}")
                print(f"     - Created: {data.get('createdAt', 'No date')}")
                print(f"     - Items: {len(data.get('items', []))}")
                print(f"     - user_id: {data.get('user_id', 'Not set')}")
                print(f"     - userId: {data.get('userId', 'Not set')}")
                print()
            
            if len(user_outfits) > 10:
                print(f"  ... and {len(user_outfits) - 10} more outfits")
        else:
            print(f"❌ No outfits found for user {user_id}")
        
        # Also check if user exists
        user_doc = db.collection('users').document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            print(f"\n👤 User exists:")
            print(f"  - Email: {user_data.get('email', 'No email')}")
            print(f"  - Display Name: {user_data.get('displayName', 'No name')}")
            print(f"  - Created: {user_data.get('createdAt', 'No date')}")
        else:
            print(f"\n❌ User {user_id} not found in users collection")
        
        return len(user_outfits)
        
    except Exception as e:
        print(f"❌ Error checking outfits: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    count = check_specific_user_outfits(user_id)
    print(f"\n🎯 Final count: {count} outfits for user {user_id}") 