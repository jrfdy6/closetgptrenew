#!/usr/bin/env python3

import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
import requests

def remove_july_17_outfits():
    """Remove all outfits created on July 17, 2024."""
    
    # Initialize Firebase with service account key
    if not firebase_admin._apps:
        cred = credentials.Certificate('service-account-key.json')
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    print("🔍 Removing outfits created on July 17, 2024")
    print("=" * 50)
    
    # Define July 17, 2024 date range (in milliseconds)
    # July 17, 2024 starts at 2024-07-17 00:00:00 UTC
    # July 17, 2024 ends at 2024-07-17 23:59:59 UTC
    july_17_start = datetime(2024, 7, 17, 0, 0, 0, tzinfo=timezone.utc).timestamp() * 1000
    july_17_end = datetime(2024, 7, 17, 23, 59, 59, tzinfo=timezone.utc).timestamp() * 1000
    
    print(f"🔍 Looking for outfits created between:")
    print(f"   Start: {datetime.fromtimestamp(july_17_start / 1000).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   End: {datetime.fromtimestamp(july_17_end / 1000).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get all outfits
    outfits_ref = db.collection('outfits')
    all_outfits = outfits_ref.stream()
    
    outfits_to_delete = []
    total_outfits = 0
    
    for doc in all_outfits:
        total_outfits += 1
        outfit_data = doc.to_dict()
        outfit_id = doc.id
        created_at = outfit_data.get('createdAt')
        
        # Convert createdAt to timestamp if it's a string
        if isinstance(created_at, str):
            try:
                # Try to parse as timestamp
                created_at = float(created_at)
            except ValueError:
                print(f"⚠️  Skipping outfit {outfit_id} - invalid createdAt format: {created_at}")
                continue
        
        # Check if outfit was created on July 17, 2024
        if isinstance(created_at, (int, float)):
            if july_17_start <= created_at <= july_17_end:
                outfit_info = {
                    'id': outfit_id,
                    'name': outfit_data.get('name', 'Unknown'),
                    'createdAt': created_at,
                    'createdAt_formatted': datetime.fromtimestamp(created_at / 1000).strftime('%Y-%m-%d %H:%M:%S')
                }
                outfits_to_delete.append(outfit_info)
                print(f"🗑️  Found outfit to delete: {outfit_info['name']} (ID: {outfit_id})")
                print(f"    Created: {outfit_info['createdAt_formatted']}")
    
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY:")
    print(f"Total outfits in database: {total_outfits}")
    print(f"Outfits created on July 17, 2024: {len(outfits_to_delete)}")
    
    if not outfits_to_delete:
        print("✅ No outfits found from July 17, 2024")
        return
    
    print("\n" + "=" * 50)
    print("🗑️  OUTFITS TO DELETE:")
    for outfit in outfits_to_delete:
        print(f"  • {outfit['name']} (ID: {outfit['id']})")
        print(f"    Created: {outfit['createdAt_formatted']}")
    
    # Ask for confirmation
    print("\n" + "=" * 50)
    response = input(f"❓ Are you sure you want to delete {len(outfits_to_delete)} outfits? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Deletion cancelled")
        return
    
    # Delete the outfits
    print("\n🗑️  DELETING OUTFITS...")
    deleted_count = 0
    
    for outfit in outfits_to_delete:
        try:
            db.collection('outfits').document(outfit['id']).delete()
            print(f"✅ Deleted: {outfit['name']} (ID: {outfit['id']})")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Failed to delete {outfit['name']} (ID: {outfit['id']}): {e}")
    
    print("\n" + "=" * 50)
    print(f"✅ DELETION COMPLETE:")
    print(f"Successfully deleted: {deleted_count}/{len(outfits_to_delete)} outfits")

if __name__ == "__main__":
    remove_july_17_outfits() 