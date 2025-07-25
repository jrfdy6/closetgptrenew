#!/usr/bin/env python3
"""
List all files in the user's wardrobe folder in Firebase Storage.
"""

import firebase_admin
from firebase_admin import credentials, initialize_app, storage
import os

BUCKET_NAME = 'closetgptrenew.firebaseapp.com'  # Correct bucket name
USER_ID = 'dANqjiI0CKgaitxzYtw1bhtvQrG3'
WARDROBE_PREFIX = f'Users/{USER_ID}/wardrobe/'

# Initialize Firebase with storage bucket
if not firebase_admin._apps:
    cred = credentials.Certificate('service-account-key.json')
    initialize_app(cred, {'storageBucket': BUCKET_NAME})

bucket = storage.bucket()

print(f"Listing all files in: gs://{BUCKET_NAME}/{WARDROBE_PREFIX}")

blobs = bucket.list_blobs(prefix=WARDROBE_PREFIX)
file_count = 0
for blob in blobs:
    print(blob.name)
    file_count += 1

print(f"\nTotal files found: {file_count}") 