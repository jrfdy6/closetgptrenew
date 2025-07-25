#!/usr/bin/env python3
"""
Migrate wardrobe files from Firebase Storage to Firestore documents.
This will create Firestore documents for each wardrobe item found in Storage.
"""

import firebase_admin
from firebase_admin import credentials, initialize_app, storage, firestore
import json
import os
from datetime import datetime
import uuid

BUCKET_NAME = 'closetgptrenew.firebasestorage.app'
USER_ID = 'dANqjiI0CKgaitxzYtw1bhtvQrG3'

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('service-account-key.json')
    initialize_app(cred, {'storageBucket': BUCKET_NAME})

bucket = storage.bucket()
db = firestore.client()

def get_file_metadata(blob):
    """Extract metadata from a storage blob."""
    metadata = {
        'id': blob.name.split('/')[-1].split('.')[0],  # Extract filename without extension
        'fileName': blob.name.split('/')[-1],
        'imageUrl': f"gs://{BUCKET_NAME}/{blob.name}",
        'storagePath': blob.name,
        'size': blob.size,
        'contentType': blob.content_type,
        'createdAt': blob.time_created,
        'updatedAt': blob.updated,
        'userId': USER_ID
    }
    
    # Try to extract more info from filename
    filename = blob.name.split('/')[-1]
    if '_' in filename:
        parts = filename.split('_')
        if len(parts) >= 2:
            try:
                timestamp = int(parts[0])
                metadata['uploadTimestamp'] = timestamp
            except:
                pass
    
    return metadata

def create_wardrobe_document(metadata):
    """Create a Firestore document for a wardrobe item."""
    doc_data = {
        'id': metadata['id'],
        'fileName': metadata['fileName'],
        'imageUrl': metadata['imageUrl'],
        'storagePath': metadata['storagePath'],
        'userId': metadata['userId'],
        'createdAt': metadata['createdAt'],
        'updatedAt': metadata['updatedAt'],
        'size': metadata['size'],
        'contentType': metadata['contentType'],
        'uploadTimestamp': metadata.get('uploadTimestamp'),
        'migratedFromStorage': True,
        'migrationDate': firestore.SERVER_TIMESTAMP
    }
    
    # Add basic wardrobe item fields
    doc_data.update({
        'name': f"Wardrobe Item {metadata['id'][:8]}",  # Generate a name
        'type': 'unknown',  # Will need to be updated later
        'status': 'active'
    })
    
    return doc_data

def migrate_wardrobe_files():
    """Migrate all wardrobe files from Storage to Firestore."""
    print(f"🔄 Migrating wardrobe files for user: {USER_ID}")
    print("=" * 60)
    
    # Get user document reference
    user_ref = db.collection('users').document(USER_ID)
    
    # Check if user document exists, create if not
    user_doc = user_ref.get()
    if not user_doc.exists:
        print(f"Creating user document for {USER_ID}")
        user_ref.set({
            'id': USER_ID,
            'uid': USER_ID,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP,
            'wardrobeCount': 0,
            'migratedFromStorage': True
        })
    
    # Get wardrobe subcollection reference
    wardrobe_ref = user_ref.collection('wardrobe')
    
    # Migration counters
    total_files = 0
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    # Storage paths to check
    storage_paths = [
        f'users/{USER_ID}/wardrobe/',
        f'wardrobe/{USER_ID}/',
        f'clothing-images/{USER_ID}/'
    ]
    
    for storage_path in storage_paths:
        print(f"\n📁 Processing: {storage_path}")
        
        try:
            blobs = list(bucket.list_blobs(prefix=storage_path))
            print(f"Found {len(blobs)} files")
            
            for blob in blobs:
                total_files += 1
                
                try:
                    # Skip if it's a directory marker
                    if blob.name.endswith('/'):
                        continue
                    
                    # Get metadata from blob
                    metadata = get_file_metadata(blob)
                    
                    # Check if document already exists
                    existing_doc = wardrobe_ref.document(metadata['id']).get()
                    if existing_doc.exists:
                        print(f"  ⚠️  Skipping {metadata['fileName']} (already exists)")
                        skipped_count += 1
                        continue
                    
                    # Create Firestore document
                    doc_data = create_wardrobe_document(metadata)
                    
                    # Save to Firestore
                    wardrobe_ref.document(metadata['id']).set(doc_data)
                    
                    print(f"  ✅ Migrated: {metadata['fileName']}")
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"  ❌ Error migrating {blob.name}: {e}")
                    error_count += 1
                    
        except Exception as e:
            print(f"❌ Error processing {storage_path}: {e}")
            error_count += 1
    
    # Update user document with final count
    final_count = len(list(wardrobe_ref.stream()))
    user_ref.update({
        'wardrobeCount': final_count,
        'lastMigration': firestore.SERVER_TIMESTAMP
    })
    
    print(f"\n🎉 Migration Complete!")
    print("=" * 40)
    print(f"Total files found: {total_files}")
    print(f"Successfully migrated: {migrated_count}")
    print(f"Skipped (already exists): {skipped_count}")
    print(f"Errors: {error_count}")
    print(f"Final wardrobe count: {final_count}")
    
    return {
        'total_files': total_files,
        'migrated': migrated_count,
        'skipped': skipped_count,
        'errors': error_count,
        'final_count': final_count
    }

def verify_migration():
    """Verify the migration by checking Firestore documents."""
    print(f"\n🔍 Verifying Migration:")
    print("=" * 40)
    
    user_ref = db.collection('users').document(USER_ID)
    wardrobe_ref = user_ref.collection('wardrobe')
    
    # Get all wardrobe documents
    docs = list(wardrobe_ref.stream())
    print(f"Total wardrobe documents: {len(docs)}")
    
    if len(docs) > 0:
        print(f"Sample documents:")
        for i, doc in enumerate(docs[:5]):
            data = doc.to_dict()
            print(f"  {i+1}. {data.get('fileName', 'No filename')}")
            print(f"     ID: {data.get('id', 'No ID')}")
            print(f"     Storage: {data.get('storagePath', 'No path')}")
            print(f"     Size: {data.get('size', 'No size')} bytes")
            print()
    
    # Check user document
    user_doc = user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        print(f"User document:")
        print(f"  Wardrobe count: {user_data.get('wardrobeCount', 'Not set')}")
        print(f"  Last migration: {user_data.get('lastMigration', 'Not set')}")

if __name__ == "__main__":
    # Run migration
    results = migrate_wardrobe_files()
    
    # Verify results
    verify_migration()
    
    print(f"\n💡 Next Steps:")
    print("=" * 30)
    print("1. The wardrobe items are now in Firestore")
    print("2. You may want to update the 'type' field for each item")
    print("3. Add additional metadata like 'name', 'style', etc.")
    print("4. Update the backend code to use the correct collection structure")
    print("5. Test outfit generation with the migrated data") 