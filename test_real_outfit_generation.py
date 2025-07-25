#!/usr/bin/env python3
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json
from datetime import datetime
import re

# Allowed material values
ALLOWED_MATERIALS = {
    'cotton', 'wool', 'silk', 'linen', 'denim', 'leather', 'synthetic', 'knit', 'fleece', 'other'
}

# Initialize Firebase Admin
cred = credentials.Certificate("backend/service-account-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def clean_material(value):
    if not isinstance(value, str):
        return 'other'
    v = value.strip().lower()
    if v in ALLOWED_MATERIALS:
        return v
    # Map common blends/unknowns
    if any(x in v for x in ['blend', 'mesh', 'canvas', 'cashmere', 'chinos', 'polyester', 'rubber', 'corduroy', 'light', 'synthetic', 'other']):
        return 'other'
    return v if v in ALLOWED_MATERIALS else 'other'

def clean_temp(value, default=32):
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        # Extract first number
        match = re.search(r'-?\d+', value)
        if match:
            return int(match.group(0))
    return default

def ensure_list(val):
    if isinstance(val, list):
        return val
    if val is None:
        return []
    return [val]

def clean_wardrobe_item(item):
    # Clean material fields
    meta = item.get('metadata', {})
    vis = meta.get('visualAttributes', {})
    # Clean material
    if 'material' in vis:
        vis['material'] = clean_material(vis['material'])
    # Clean materialCompatibility
    mat_compat = vis.get('materialCompatibility', {})
    # compatibleMaterials: list of allowed materials
    if 'compatibleMaterials' in mat_compat:
        mat_compat['compatibleMaterials'] = [clean_material(m) for m in ensure_list(mat_compat['compatibleMaterials'])]
    else:
        mat_compat['compatibleMaterials'] = []
    # weatherAppropriate: should be a dict of lists of allowed materials
    wa = mat_compat.get('weatherAppropriate')
    if isinstance(wa, dict):
        cleaned_wa = {}
        for season, mats in wa.items():
            cleaned_wa[season] = [clean_material(m) for m in ensure_list(mats)]
        mat_compat['weatherAppropriate'] = cleaned_wa
    else:
        # If it's a list or string, replace with empty dict
        mat_compat['weatherAppropriate'] = {}
    vis['materialCompatibility'] = mat_compat
    # Clean temperatureCompatibility
    temp_compat = vis.get('temperatureCompatibility', {})
    # minTemp/maxTemp: numbers
    for key in ['minTemp', 'maxTemp']:
        if key in temp_compat:
            temp_compat[key] = clean_temp(temp_compat[key], 32 if key == 'minTemp' else 85)
        else:
            temp_compat[key] = 32 if key == 'minTemp' else 85
    # recommendedLayers: list
    if 'recommendedLayers' not in temp_compat or not isinstance(temp_compat['recommendedLayers'], list):
        temp_compat['recommendedLayers'] = []
    # materialPreferences: list of allowed materials
    if 'materialPreferences' in temp_compat:
        temp_compat['materialPreferences'] = [clean_material(m) for m in ensure_list(temp_compat['materialPreferences'])]
    else:
        temp_compat['materialPreferences'] = []
    vis['temperatureCompatibility'] = temp_compat
    meta['visualAttributes'] = vis
    item['metadata'] = meta
    # Ensure required nested fields
    # bodyTypeCompatibility
    btc = vis.get('bodyTypeCompatibility', {})
    for sub in ['recommendedFits', 'styleRecommendations']:
        for bodytype in ['apple', 'hourglass', 'pear', 'rectangle', 'inverted_triangle']:
            if bodytype not in btc:
                btc[bodytype] = {}
            if sub not in btc[bodytype]:
                btc[bodytype][sub] = []
    # Top-level required fields for bodyTypeCompatibility
    if 'recommendedFits' not in btc:
        btc['recommendedFits'] = {}
    if 'styleRecommendations' not in btc:
        btc['styleRecommendations'] = {}
    vis['bodyTypeCompatibility'] = btc
    # skinToneCompatibility
    stc = vis.get('skinToneCompatibility', {})
    for sub in ['compatibleColors', 'recommendedPalettes']:
        for tone in ['warm', 'neutral', 'cool']:
            if tone not in stc:
                stc[tone] = {}
            if sub not in stc[tone]:
                stc[tone][sub] = []
    # Top-level required fields for skinToneCompatibility
    if 'compatibleColors' not in stc:
        stc['compatibleColors'] = {}
    if 'recommendedPalettes' not in stc:
        stc['recommendedPalettes'] = {}
    vis['skinToneCompatibility'] = stc
    meta['visualAttributes'] = vis
    item['metadata'] = meta
    return item

def clean_wardrobe(wardrobe):
    return [clean_wardrobe_item(item) for item in wardrobe]

def clean_user_profile(profile):
    # Ensure list fields
    for key in ['stylePreferences', 'colorPreferences', 'brandPreferences']:
        if key in profile:
            profile[key] = ensure_list(profile[key])
    # Preferences subfields
    prefs = profile.get('preferences', {})
    for key in ['fit', 'size', 'formality']:
        if key in prefs:
            prefs[key] = ensure_list(prefs[key])
    profile['preferences'] = prefs
    # Timestamps
    for key in ['createdAt', 'updatedAt']:
        val = profile.get(key)
        if isinstance(val, str):
            try:
                profile[key] = int(datetime.fromisoformat(val.replace('Z', '+00:00')).timestamp())
            except Exception:
                profile[key] = int(datetime.now().timestamp())
        elif isinstance(val, (int, float)):
            profile[key] = int(val)
        else:
            profile[key] = int(datetime.now().timestamp())
    return profile

def convert_firestore_timestamps(obj):
    """Convert Firestore timestamp objects to regular timestamps"""
    if isinstance(obj, dict):
        converted = {}
        for key, value in obj.items():
            if hasattr(value, 'timestamp'):
                # Convert Firestore timestamp to Unix timestamp
                converted[key] = int(value.timestamp())
            else:
                converted[key] = convert_firestore_timestamps(value)
        return converted
    elif isinstance(obj, list):
        return [convert_firestore_timestamps(item) for item in obj]
    else:
        return obj

def fetch_real_wardrobe(user_id: str):
    """Fetch real wardrobe items from Firestore"""
    wardrobe_ref = db.collection('wardrobe')
    query = wardrobe_ref.where('userId', '==', user_id)
    docs = query.stream()
    items = []
    for doc in docs:
        item_data = doc.to_dict()
        item_data['id'] = doc.id
        # Convert timestamps
        item_data = convert_firestore_timestamps(item_data)
        items.append(item_data)
    return items

def fetch_user_profile(user_id: str):
    """Fetch user profile from Firestore"""
    profile_ref = db.collection('users')
    doc = profile_ref.document(user_id).get()
    if doc.exists:
        profile_data = doc.to_dict()
        profile_data['id'] = doc.id
        # Convert timestamps
        profile_data = convert_firestore_timestamps(profile_data)
        return profile_data
    else:
        # Create a default profile if none exists
        return {
            "id": user_id,
            "name": "Test User",
            "email": "test@example.com",
            "gender": "male",
            "age": 25,
            "height": 175,
            "weight": 70,
            "bodyType": "average",
            "stylePreferences": ["Casual", "Classic"],
            "colorPreferences": ["Blue", "White"],
            "brandPreferences": ["Nike", "Adidas"],
            "budget": "medium",
            "location": "New York",
            "climate": "temperate",
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp())
        }

def test_real_outfit_generation():
    """Test outfit generation with real wardrobe data"""
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print("🔍 Fetching real wardrobe data...")
    wardrobe = fetch_real_wardrobe(user_id)
    print(f"📦 Found {len(wardrobe)} wardrobe items")
    wardrobe = clean_wardrobe(wardrobe)
    
    print("👤 Fetching user profile...")
    user_profile = fetch_user_profile(user_id)
    print(f"✅ User profile: {user_profile.get('name', 'Unknown')}")
    user_profile = clean_user_profile(user_profile)
    
    # Test payload with real data
    payload = {
        "occasion": "Wedding Guest",
        "mood": "confident", 
        "style": "Casual Cool",
        "description": "",
        "gender": "male",
        "wardrobe": wardrobe,
        "user_profile": user_profile,
        "weather": {
            "temperature": 22.0,
            "condition": "sunny",
            "humidity": 60,
            "wind_speed": 10,
            "location": "New York"
        },
        "likedOutfits": [],
        "trendingStyles": [],
        "preferences": {},
        "outfitHistory": [],
        "randomSeed": 0.5,
        "season": "spring",
        "baseItem": None
    }
    
    try:
        print("\n🚀 Testing outfit generation with real wardrobe...")
        response = requests.post(
            "http://localhost:3001/api/outfit/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Outfit generation worked with real data!")
            print(f"🎯 Generated outfit ID: {result.get('id', 'N/A')}")
            print(f"👕 Outfit name: {result.get('name', 'N/A')}")
            print(f"📋 Number of items selected: {len(result.get('items', []))}")
            print(f"🎨 Color harmony: {result.get('colorHarmony', 'N/A')}")
            print(f"📝 Style notes: {result.get('styleNotes', 'N/A')}")
            
            # Show selected items
            items = result.get('items', [])
            if items:
                print("\n👔 Selected items:")
                for i, item in enumerate(items, 1):
                    print(f"  {i}. {item.get('name', 'Unknown')} ({item.get('type', 'Unknown')})")
            else:
                print("\n⚠️  No items were selected for this outfit")
                
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    success = test_real_outfit_generation()
    if success:
        print("\n🎉 Real outfit generation test completed successfully!")
    else:
        print("\n💥 There's an issue with the real outfit generation.") 