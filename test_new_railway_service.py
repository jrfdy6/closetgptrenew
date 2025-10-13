#!/usr/bin/env python3
"""
Test the new Railway service (closetgptrenew-production.up.railway.app)
to see if region switch broke the cache and deployed new code.
"""

import requests
import json
from google.cloud import firestore

# Initialize Firestore to get wardrobe
db = firestore.Client()
user_id = 'dANqjiI0CKgaitxzYtw1bhtvQrG3'

print("=" * 80)
print("TESTING NEW RAILWAY SERVICE (us-west2 region)")
print("=" * 80)

# Get wardrobe from Firestore
print("\n1. Fetching wardrobe from Firestore...")
items = list(db.collection('wardrobe').where('userId', '==', user_id).stream())
wardrobe = [item.to_dict() for item in items]
print(f"   ✅ Loaded {len(wardrobe)} items")

# Test NEW service
url = "https://closetgptrenew-production.up.railway.app/api/outfits-existing-data/generate-personalized"

payload = {
    "occasion": "Gym",
    "style": "Classic",
    "mood": "Bold",
    "wardrobe": wardrobe,
    "weather": {"temperature": 70, "condition": "Clear"},
    "userId": user_id
}

print(f"\n2. Testing NEW Railway service: {url}")
print(f"   Request: Gym + Classic + Bold")
print(f"   Wardrobe: {len(wardrobe)} items")

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"\n3. Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success! Generated outfit with {len(result.get('items', []))} items")
        print(f"\n   Items:")
        for item in result.get('items', []):
            print(f"     - {item.get('name', 'Unknown')}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   {response.text[:500]}")
        
except Exception as e:
    print(f"\n   ❌ Request failed: {e}")

print("\n" + "=" * 80)
print("NOW: Check Railway HTTP Logs for 'closetgptrenew' service")
print("     Look for: '🔍 HARD FILTER ENTRY' debug messages")
print("=" * 80)

