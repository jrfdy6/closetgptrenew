#!/usr/bin/env python3
"""
Debug Firestore field names to check for exact matches.
This script will examine the actual field names in your Firestore documents.
"""

import firebase_admin
from firebase_admin import firestore
import json

def check_firestore_field_names():
    """Check the exact field names in Firestore documents."""
    print("🔍 Checking Firestore Field Names")
    print("=" * 60)
    
    try:
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            print("🔍 Initializing Firebase...")
            firebase_admin.initialize_app()
        
        # Get Firestore client
        db = firestore.client()
        print("✅ Firestore client created successfully")
        
        # Check outfits collection
        print("\n📊 Checking 'outfits' collection...")
        outfits_ref = db.collection('outfits')
        outfits_docs = outfits_ref.limit(10).stream()
        outfits_list = list(outfits_docs)
        
        print(f"📄 Found {len(outfits_list)} outfit documents")
        
        # Analyze field names in outfits
        field_names = set()
        user_id_variations = set()
        
        for i, doc in enumerate(outfits_list):
            data = doc.to_dict()
            doc_fields = list(data.keys())
            field_names.update(doc_fields)
            
            print(f"\n📄 Document {i+1}: {doc.id}")
            print(f"   Fields: {doc_fields}")
            
            # Check for user ID related fields
            user_fields = [field for field in doc_fields if 'user' in field.lower()]
            if user_fields:
                print(f"   User-related fields: {user_fields}")
                user_id_variations.update(user_fields)
                
                # Show exact values for user fields
                for field in user_fields:
                    value = data.get(field)
                    print(f"   {field}: '{value}' (type: {type(value)})")
                    if value:
                        print(f"   {field} length: {len(str(value))}")
                        print(f"   {field} starts with: '{str(value)[:20]}...'")
            else:
                print(f"   ⚠️ No user-related fields found")
        
        print(f"\n📊 Summary of field names found:")
        print(f"   Total unique fields: {len(field_names)}")
        print(f"   All fields: {sorted(list(field_names))}")
        
        print(f"\n🔍 User ID field variations found:")
        if user_id_variations:
            for field in sorted(user_id_variations):
                print(f"   - '{field}'")
        else:
            print("   ⚠️ No user ID related fields found!")
        
        # Check for exact matches
        exact_matches = {
            'user_id': 'user_id' in field_names,
            'userId': 'userId' in field_names,
            'user': 'user' in field_names,
            'uid': 'uid' in field_names,
        }
        
        print(f"\n✅ Exact field name matches:")
        for field, exists in exact_matches.items():
            status = "✅" if exists else "❌"
            print(f"   {status} '{field}': {exists}")
        
        # Check for similar field names (case variations, spaces, etc.)
        print(f"\n🔍 Checking for similar field names...")
        for field in field_names:
            if 'user' in field.lower():
                print(f"   Found: '{field}'")
                # Check for common variations
                variations = [
                    field.lower(),
                    field.upper(),
                    field.strip(),
                    field.replace(' ', ''),
                    field.replace('_', ''),
                    field.replace('-', '_'),
                ]
                for var in variations:
                    if var != field and var in field_names:
                        print(f"     ⚠️ Similar field exists: '{var}'")
        
        # Test queries with different field names
        print(f"\n🧪 Testing queries with different field names...")
        test_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        
        for field_name in ['user_id', 'userId', 'user', 'uid']:
            try:
                query = outfits_ref.where(field_name, '==', test_user_id)
                results = list(query.limit(5).stream())
                print(f"   Query '{field_name} == {test_user_id}': {len(results)} results")
                if results:
                    print(f"     First result ID: {results[0].id}")
            except Exception as e:
                print(f"   Query '{field_name} == {test_user_id}': ERROR - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_wardrobe_field_names():
    """Check field names in wardrobe collection."""
    print("\n" + "=" * 60)
    print("🔍 Checking 'wardrobe' collection field names...")
    
    try:
        db = firestore.client()
        wardrobe_ref = db.collection('wardrobe')
        wardrobe_docs = wardrobe_ref.limit(5).stream()
        wardrobe_list = list(wardrobe_docs)
        
        print(f"📄 Found {len(wardrobe_list)} wardrobe documents")
        
        field_names = set()
        user_id_variations = set()
        
        for i, doc in enumerate(wardrobe_list):
            data = doc.to_dict()
            doc_fields = list(data.keys())
            field_names.update(doc_fields)
            
            print(f"\n👕 Wardrobe Item {i+1}: {doc.id}")
            print(f"   Fields: {doc_fields}")
            
            # Check for user ID related fields
            user_fields = [field for field in doc_fields if 'user' in field.lower()]
            if user_fields:
                print(f"   User-related fields: {user_fields}")
                user_id_variations.update(user_fields)
                
                # Show exact values for user fields
                for field in user_fields:
                    value = data.get(field)
                    print(f"   {field}: '{value}' (type: {type(value)})")
            else:
                print(f"   ⚠️ No user-related fields found")
        
        print(f"\n🔍 Wardrobe User ID field variations found:")
        if user_id_variations:
            for field in sorted(user_id_variations):
                print(f"   - '{field}'")
        else:
            print("   ⚠️ No user ID related fields found!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking wardrobe: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Firestore Field Name Debug")
    print("This will check the exact field names in your Firestore documents")
    print()
    
    # Check outfits collection
    outfits_success = check_firestore_field_names()
    
    # Check wardrobe collection
    wardrobe_success = check_wardrobe_field_names()
    
    print("\n" + "=" * 60)
    if outfits_success and wardrobe_success:
        print("✅ Field name check completed successfully!")
        print("\n📝 Next steps:")
        print("1. Check the exact field names found above")
        print("2. Verify 'user_id' field exists and is spelled correctly")
        print("3. Check for any trailing spaces or case mismatches")
        print("4. Update your queries to use the exact field name")
    else:
        print("❌ Some checks failed. Check the errors above.")
    
    print("\n🔍 Key things to look for:")
    print("- Exact field name: 'user_id' (lowercase, underscore)")
    print("- No trailing spaces: 'user_id ' vs 'user_id'")
    print("- Case sensitivity: 'userId' vs 'user_id'")
    print("- Special characters: 'user-id' vs 'user_id'") 