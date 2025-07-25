#!/usr/bin/env python3
"""
Script to add schema versioning to outfits collection.
This fixes the missing schema_version field identified in the audit.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app
import time

# Initialize Firebase
if not firebase_admin._apps:
    initialize_app()
db = firestore.client()

SCHEMA_VERSION = "1.0.0"

def fix_outfits_schema():
    """Add schema versioning to outfits collection."""
    outfits_ref = db.collection('outfits')
    docs = list(outfits_ref.stream())
    total = len(docs)
    updated = 0
    errors = 0

    print(f"Found {total} outfit documents.")
    
    for doc in docs:
        outfit = doc.to_dict()
        outfit_id = doc.id
        
        try:
            update_data = {}
            
            # Add schema version if missing
            if 'schema_version' not in outfit:
                update_data['schema_version'] = SCHEMA_VERSION
                print(f"[ADDING SCHEMA] {outfit.get('name', 'Unknown Outfit')} ({outfit_id})")
            
            # Add updatedAt timestamp if missing
            if 'updatedAt' not in outfit:
                update_data['updatedAt'] = int(time.time())
                print(f"[ADDING TIMESTAMP] {outfit.get('name', 'Unknown Outfit')} ({outfit_id})")
            
            # Update the document if needed
            if update_data:
                doc.reference.update(update_data)
                updated += 1
                
        except Exception as e:
            print(f"[ERROR] {outfit_id}: {e}")
            errors += 1

    print("\n--- Outfits Schema Fix Summary ---")
    print(f"Total outfits: {total}")
    print(f"Updated: {updated}")
    print(f"Errors: {errors}")
    
    if updated > 0:
        print(f"✅ Successfully added schema versioning to {updated} outfit documents")
    else:
        print("ℹ️  No outfits needed schema versioning updates")

if __name__ == "__main__":
    fix_outfits_schema() 