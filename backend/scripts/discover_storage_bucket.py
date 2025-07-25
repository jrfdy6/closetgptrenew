#!/usr/bin/env python3
"""
Discover the correct storage bucket name by trying different patterns.
"""

import firebase_admin
from firebase_admin import credentials, initialize_app, storage
import json

# Read the service account to get project ID
with open('service-account-key.json', 'r') as f:
    service_account = json.load(f)
    project_id = service_account['project_id']

print(f"Project ID from service account: {project_id}")

# Common bucket name patterns to try
bucket_patterns = [
    f"{project_id}.appspot.com",
    f"{project_id}.firebaseapp.com", 
    f"{project_id}.firebasestorage.app",
    f"{project_id}-storage",
    f"{project_id}-default",
    "closetgptrenew.appspot.com",
    "closetgptrenew.firebaseapp.com",
    "closetgptrenew.firebasestorage.app"
]

print(f"\nTrying bucket patterns:")
print("=" * 50)

# Initialize Firebase without specifying bucket first
if not firebase_admin._apps:
    cred = credentials.Certificate('service-account-key.json')
    initialize_app(cred)

# Try each bucket pattern
for bucket_name in bucket_patterns:
    try:
        print(f"Testing: {bucket_name}")
        bucket = storage.bucket(bucket_name)
        
        # Try to list a few blobs to see if bucket exists
        blobs = list(bucket.list_blobs(max_results=1))
        print(f"  ✅ Bucket exists! Found {len(blobs)} files")
        
        # If it exists, try to list files in the user's wardrobe
        user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        wardrobe_prefix = f"Users/{user_id}/wardrobe/"
        
        wardrobe_blobs = list(bucket.list_blobs(prefix=wardrobe_prefix, max_results=5))
        print(f"  📁 Wardrobe files: {len(wardrobe_blobs)}")
        
        if wardrobe_blobs:
            print(f"  Sample files:")
            for blob in wardrobe_blobs[:3]:
                print(f"    - {blob.name}")
        
        print(f"  🎯 This appears to be the correct bucket!")
        break
        
    except Exception as e:
        print(f"  ❌ {str(e)[:50]}...")

print(f"\n💡 If no bucket was found, check your Firebase Console for the correct bucket name.") 