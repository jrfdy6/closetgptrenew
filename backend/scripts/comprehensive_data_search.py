#!/usr/bin/env python3
"""
Comprehensive search for all data across all possible locations.
This will help find the missing 115 wardrobe items, users, and dozens of outfits.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app
import json
import os

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

def search_all_collections():
    """Search all collections and get detailed counts."""
    print("🔍 Comprehensive Data Search")
    print("=" * 60)
    
    try:
        # Get all collections
        collections = db.collections()
        collection_list = list(collections)
        
        print(f"Found {len(collection_list)} collections:")
        for i, collection in enumerate(collection_list):
            print(f"  {i+1}. {collection.id}")
        
        print(f"\n📊 Detailed Collection Analysis:")
        print("=" * 60)
        
        total_docs = 0
        for collection in collection_list:
            try:
                docs = list(collection.stream())
                count = len(docs)
                total_docs += count
                
                print(f"\n📁 {collection.id.upper()}: {count} documents")
                
                if count > 0:
                    # Analyze first document
                    first_doc = docs[0].to_dict()
                    print(f"  Sample fields: {list(first_doc.keys())[:8]}")
                    
                    # Check for key identifiers
                    key_fields = ['userId', 'user_id', 'email', 'name', 'type', 'occasion']
                    found_fields = []
                    for field in key_fields:
                        if field in first_doc:
                            found_fields.append(field)
                    
                    if found_fields:
                        print(f"  Key fields: {found_fields}")
                    
                    # Show sample data for first few docs
                    for i, doc in enumerate(docs[:3]):
                        data = doc.to_dict()
                        doc_id = doc.id
                        name = data.get('name', 'No name')
                        user_id = data.get('userId', data.get('user_id', 'No user'))
                        print(f"    {i+1}. {doc_id}: {name} (User: {user_id})")
                    
                    if count > 3:
                        print(f"    ... and {count - 3} more documents")
                        
            except Exception as e:
                print(f"  ❌ Error analyzing {collection.id}: {e}")
        
        print(f"\n📈 Total documents across all collections: {total_docs}")
        
    except Exception as e:
        print(f"❌ Error listing collections: {e}")

def check_for_environment_specific_data():
    """Check if data might be in environment-specific collections."""
    print(f"\n🌍 Environment-Specific Data Check:")
    print("=" * 60)
    
    # Common environment suffixes
    env_suffixes = ['_dev', '_development', '_prod', '_production', '_test', '_staging']
    
    for suffix in env_suffixes:
        collections_to_check = [
            f'wardrobe{suffix}',
            f'clothingItems{suffix}',
            f'users{suffix}',
            f'outfits{suffix}'
        ]
        
        for collection_name in collections_to_check:
            try:
                docs = list(db.collection(collection_name).stream())
                if len(docs) > 0:
                    print(f"✅ Found {collection_name}: {len(docs)} documents")
                    # Show sample
                    sample = docs[0].to_dict()
                    print(f"   Sample fields: {list(sample.keys())[:5]}")
            except:
                pass

def check_for_subcollections_deep():
    """Deep check for subcollections that might contain the data."""
    print(f"\n📂 Deep Subcollection Search:")
    print("=" * 60)
    
    # Check all collections for subcollections
    try:
        collections = db.collections()
        for collection in collections:
            try:
                docs = list(collection.limit(5).stream())
                if len(docs) > 0:
                    print(f"\n🔍 Checking subcollections in {collection.id}:")
                    for doc in docs:
                        try:
                            subcollections = list(doc.reference.collections())
                            if subcollections:
                                print(f"  Document {doc.id} has subcollections:")
                                for subcol in subcollections:
                                    sub_docs = list(subcol.stream())
                                    print(f"    - {subcol.id}: {len(sub_docs)} documents")
                                    
                                    # If this looks like our data, show details
                                    if len(sub_docs) > 10 and subcol.id in ['wardrobe', 'clothingItems', 'users', 'outfits']:
                                        print(f"      ⭐ This might be our data!")
                                        sample = sub_docs[0].to_dict()
                                        print(f"      Sample fields: {list(sample.keys())[:5]}")
                        except Exception as e:
                            print(f"  Error checking subcollections for {doc.id}: {e}")
            except Exception as e:
                print(f"Error checking {collection.id}: {e}")
    except Exception as e:
        print(f"Error in deep subcollection search: {e}")

def check_for_different_project_configs():
    """Check if there are multiple service account files pointing to different projects."""
    print(f"\n🔧 Multiple Project Configuration Check:")
    print("=" * 60)
    
    # Look for all service account files
    service_account_files = []
    for root, dirs, files in os.walk('..'):
        for file in files:
            if 'service' in file.lower() and file.endswith('.json'):
                service_account_files.append(os.path.join(root, file))
    
    if len(service_account_files) > 1:
        print(f"Found {len(service_account_files)} service account files:")
        for file_path in service_account_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    project_id = data.get('project_id', 'unknown')
                    client_email = data.get('client_email', 'unknown')
                    print(f"  {file_path}")
                    print(f"    Project: {project_id}")
                    print(f"    Client: {client_email}")
            except:
                print(f"  {file_path} (unreadable)")
    else:
        print("Only one service account file found")

def check_environment_variables():
    """Check environment variables that might point to different projects."""
    print(f"\n🔧 Environment Variables Check:")
    print("=" * 60)
    
    env_vars = [
        'GOOGLE_APPLICATION_CREDENTIALS',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_SERVICE_ACCOUNT_KEY',
        'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
        'FIREBASE_PROJECT',
        'GCLOUD_PROJECT'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"ℹ️  {var}: Not set")

def check_for_data_in_outfits():
    """Check if wardrobe data might be embedded in outfits."""
    print(f"\n👕 Checking Outfits for Embedded Wardrobe Data:")
    print("=" * 60)
    
    try:
        outfits = list(db.collection('outfits').stream())
        print(f"Found {len(outfits)} outfits")
        
        if len(outfits) > 0:
            # Check first few outfits for embedded items
            for i, outfit in enumerate(outfits[:5]):
                data = outfit.to_dict()
                print(f"\nOutfit {i+1}: {data.get('name', 'No name')}")
                
                # Check for items arrays
                items_fields = ['items', 'pieces', 'clothingItems', 'wardrobe']
                for field in items_fields:
                    if field in data and isinstance(data[field], list):
                        items = data[field]
                        print(f"  {field}: {len(items)} items")
                        if len(items) > 0:
                            print(f"    Sample: {items[0] if isinstance(items[0], str) else 'object'}")
                
                # Check for userId
                if 'userId' in data:
                    print(f"  User ID: {data['userId']}")
                    
    except Exception as e:
        print(f"❌ Error checking outfits: {e}")

if __name__ == "__main__":
    search_all_collections()
    check_for_environment_specific_data()
    check_for_subcollections_deep()
    check_for_different_project_configs()
    check_environment_variables()
    check_for_data_in_outfits()
    
    print(f"\n💡 Summary:")
    print("=" * 30)
    print("This comprehensive search should find:")
    print("1. All collections and their document counts")
    print("2. Environment-specific data")
    print("3. Data in subcollections")
    print("4. Multiple project configurations")
    print("5. Embedded wardrobe data in outfits")
    print("6. The missing 115 wardrobe items and users") 