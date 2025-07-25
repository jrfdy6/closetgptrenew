#!/usr/bin/env python3
"""
Explore all collections and data structures in the database.
This will help identify where the data might be stored.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app
import json

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

def list_all_collections():
    """List all collections in the database."""
    print("🔍 Exploring All Collections")
    print("=" * 50)
    
    try:
        # Get all collections
        collections = db.collections()
        collection_list = list(collections)
        
        print(f"Found {len(collection_list)} collections:")
        for i, collection in enumerate(collection_list):
            print(f"  {i+1}. {collection.id}")
        
        return [col.id for col in collection_list]
        
    except Exception as e:
        print(f"❌ Error listing collections: {e}")
        return []

def explore_collection_details(collections):
    """Explore details of each collection."""
    print(f"\n📊 Collection Details:")
    print("=" * 50)
    
    for collection_name in collections:
        print(f"\n📁 {collection_name.upper()}:")
        print("-" * 30)
        
        try:
            # Get all documents in collection
            docs = list(db.collection(collection_name).stream())
            print(f"  Total documents: {len(docs)}")
            
            if len(docs) > 0:
                # Analyze first document structure
                first_doc = docs[0].to_dict()
                print(f"  Document ID: {docs[0].id}")
                print(f"  Fields: {list(first_doc.keys())}")
                
                # Show sample data for key fields
                key_fields = ['name', 'type', 'userId', 'user_id', 'email', 'createdAt', 'created_at']
                for field in key_fields:
                    if field in first_doc:
                        value = first_doc[field]
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"    {field}: {value}")
                
                # Check for nested structures
                for key, value in first_doc.items():
                    if isinstance(value, dict):
                        print(f"    {key}: {dict} with keys: {list(value.keys())[:5]}")
                    elif isinstance(value, list):
                        print(f"    {key}: [list] with {len(value)} items")
                
                # Show a few more documents if they exist
                if len(docs) > 1:
                    print(f"  Sample of other documents:")
                    for i, doc in enumerate(docs[1:4]):  # Show next 3
                        data = doc.to_dict()
                        doc_id = doc.id
                        name = data.get('name', 'No name')
                        print(f"    {i+2}. {doc_id}: {name}")
                
            else:
                print("  No documents found")
                
        except Exception as e:
            print(f"  ❌ Error exploring {collection_name}: {e}")

def check_for_alternative_structures():
    """Check for alternative data structures or naming conventions."""
    print(f"\n🔍 Checking for Alternative Structures:")
    print("=" * 50)
    
    # Check for common alternative names
    alternative_names = {
        'wardrobe': ['clothes', 'items', 'clothing', 'garments'],
        'users': ['user', 'accounts', 'profiles'],
        'outfits': ['outfit', 'combinations', 'ensembles']
    }
    
    for standard_name, alternatives in alternative_names.items():
        print(f"\n🔎 Looking for {standard_name} alternatives:")
        for alt_name in alternatives:
            try:
                docs = list(db.collection(alt_name).stream())
                if len(docs) > 0:
                    print(f"  ✅ Found '{alt_name}': {len(docs)} documents")
                    # Show sample
                    sample = docs[0].to_dict()
                    print(f"    Sample keys: {list(sample.keys())[:5]}")
                else:
                    print(f"  ❌ '{alt_name}': No documents")
            except:
                print(f"  ❌ '{alt_name}': Collection doesn't exist")

def check_for_subcollections():
    """Check if data is stored in subcollections."""
    print(f"\n📂 Checking for Subcollections:")
    print("=" * 50)
    
    # Check if there are any documents that might have subcollections
    collections_to_check = ['users', 'wardrobe', 'outfits']
    
    for collection_name in collections_to_check:
        try:
            docs = list(db.collection(collection_name).limit(5).stream())
            if len(docs) > 0:
                print(f"\n🔍 Checking subcollections in {collection_name}:")
                for doc in docs:
                    try:
                        # Try to list subcollections
                        subcollections = list(doc.reference.collections())
                        if subcollections:
                            print(f"  Document {doc.id} has subcollections:")
                            for subcol in subcollections:
                                sub_docs = list(subcol.limit(3).stream())
                                print(f"    - {subcol.id}: {len(sub_docs)} documents")
                        else:
                            print(f"  Document {doc.id}: No subcollections")
                    except Exception as e:
                        print(f"  Document {doc.id}: Error checking subcollections - {e}")
        except Exception as e:
            print(f"❌ Error checking {collection_name}: {e}")

if __name__ == "__main__":
    collections = list_all_collections()
    explore_collection_details(collections)
    check_for_alternative_structures()
    check_for_subcollections()
    
    print(f"\n💡 Summary:")
    print("=" * 30)
    print("This will help identify:")
    print("1. All available collections")
    print("2. Data structure and field names")
    print("3. Alternative collection names")
    print("4. Subcollection structures")
    print("5. Where the missing data might be stored") 