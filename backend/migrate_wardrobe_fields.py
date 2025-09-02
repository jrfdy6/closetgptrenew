#!/usr/bin/env python3
"""
Wardrobe Field Migration Script
==============================

This script standardizes all wardrobe items to use the 'userId' field
instead of various field names like 'uid', 'ownerId', 'user_id'.

Run this once to fix your production database.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.firebase import db, firebase_initialized

def migrate_wardrobe_fields():
    """Migrate all wardrobe items to use consistent 'userId' field."""
    
    if not firebase_initialized or db is None:
        print("❌ Firebase not initialized. Cannot run migration.")
        return False
    
    print("🔄 Starting wardrobe field migration...")
    
    # Get all wardrobe items
    wardrobe_ref = db.collection('wardrobe')
    docs = wardrobe_ref.stream()
    
    migrated_count = 0
    error_count = 0
    
    for doc in docs:
        try:
            data = doc.to_dict()
            doc_id = doc.id
            
            # Check if migration is needed
            needs_migration = False
            user_id = None
            
            # Check for various user ID field names
            for field_name in ['uid', 'ownerId', 'user_id']:
                if field_name in data and data[field_name]:
                    user_id = data[field_name]
                    needs_migration = True
                    break
            
            # If we found a user ID in an alternative field, migrate it
            if needs_migration and user_id:
                print(f"🔄 Migrating document {doc_id}: {data.get('name', 'Unknown')}")
                
                # Update the document to use 'userId' field
                doc_ref = wardrobe_ref.document(doc_id)
                doc_ref.update({
                    'userId': user_id
                })
                
                # Remove the old field (optional - you might want to keep it for backup)
                # doc_ref.update({
                #     'uid': firestore.DELETE_FIELD,
                #     'ownerId': firestore.DELETE_FIELD,
                #     'user_id': firestore.DELETE_FIELD
                # })
                
                migrated_count += 1
                print(f"✅ Migrated {doc_id} to use userId: {user_id}")
            
        except Exception as e:
            print(f"❌ Error migrating document {doc_id}: {e}")
            error_count += 1
    
    print(f"\n🎉 Migration complete!")
    print(f"✅ Migrated: {migrated_count} documents")
    print(f"❌ Errors: {error_count} documents")
    
    return error_count == 0

if __name__ == "__main__":
    print("🚀 Wardrobe Field Migration Script")
    print("=" * 50)
    
    # Confirm before running
    confirm = input("This will modify your production database. Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Migration cancelled.")
        sys.exit(0)
    
    success = migrate_wardrobe_fields()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("Your wardrobe should now work correctly in production.")
    else:
        print("\n❌ Migration completed with errors.")
        print("Check the output above for details.")
    
    sys.exit(0 if success else 1)
