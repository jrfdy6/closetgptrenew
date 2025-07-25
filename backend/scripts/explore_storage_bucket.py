#!/usr/bin/env python3
"""
Explore the storage bucket to find all files and user folders.
"""

import firebase_admin
from firebase_admin import credentials, initialize_app, storage
import json

BUCKET_NAME = 'closetgptrenew.firebasestorage.app'

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('service-account-key.json')
    initialize_app(cred, {'storageBucket': BUCKET_NAME})

bucket = storage.bucket()

print(f"Exploring bucket: gs://{BUCKET_NAME}")
print("=" * 60)

# List all blobs in the bucket
blobs = list(bucket.list_blobs())
print(f"Total files in bucket: {len(blobs)}")

if len(blobs) == 0:
    print("No files found in bucket")
    exit()

# Group files by directory structure
directories = {}
for blob in blobs:
    path = blob.name
    parts = path.split('/')
    
    if len(parts) >= 2:
        top_dir = parts[0]
        if top_dir not in directories:
            directories[top_dir] = []
        directories[top_dir].append(path)

print(f"\n📁 Top-level directories found:")
print("=" * 40)

for directory, files in directories.items():
    print(f"\n📂 {directory}/ ({len(files)} files)")
    
    # Show sample files
    for i, file_path in enumerate(files[:5]):
        print(f"  {i+1}. {file_path}")
    
    if len(files) > 5:
        print(f"  ... and {len(files) - 5} more")
    
    # If this is a Users directory, look for specific user
    if directory == 'Users':
        print(f"\n  🔍 Looking for user dANqjiI0CKgaitxzYtw1bhtvQrG3:")
        user_files = [f for f in files if f.startswith(f'Users/dANqjiI0CKgaitxzYtw1bhtvQrG3/')]
        print(f"    Found {len(user_files)} files for this user")
        
        if user_files:
            print(f"    Sample files:")
            for i, file_path in enumerate(user_files[:5]):
                print(f"      {i+1}. {file_path}")
        else:
            # Look for any user folders
            user_ids = set()
            for file_path in files:
                parts = file_path.split('/')
                if len(parts) >= 2:
                    user_ids.add(parts[1])
            
            print(f"    Found {len(user_ids)} users in Users directory:")
            for user_id in user_ids:
                user_files = [f for f in files if f.startswith(f'Users/{user_id}/')]
                print(f"      - {user_id}: {len(user_files)} files")

print(f"\n💡 Summary:")
print("=" * 30)
print("This shows the complete structure of your Firebase Storage bucket.")
print("Look for the correct user ID and wardrobe folder path.") 