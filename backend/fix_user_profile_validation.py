#!/usr/bin/env python3

import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service-account-key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

async def fix_user_profile_validation():
    """Fix remaining UserProfile validation issues"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"🔧 Fixing UserProfile validation issues for user: {user_id}")
    
    # Get user profile
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        print("❌ User profile not found")
        return
    
    user_data = user_doc.to_dict()
    print(f"📋 Current user data structure issues:")
    
    # Fix fitPreferences - should be a dict, not a list
    if 'fitPreferences' in user_data and isinstance(user_data['fitPreferences'], list):
        print(f"🔧 Converting fitPreferences from list to dict")
        user_data['fitPreferences'] = {}
    
    # Fix updatedAt - should be an integer, not a float
    if 'updatedAt' in user_data and isinstance(user_data['updatedAt'], float):
        print(f"🔧 Converting updatedAt from float to int")
        user_data['updatedAt'] = int(user_data['updatedAt'])
    
    # Fix createdAt - should be an integer, not a float
    if 'createdAt' in user_data and isinstance(user_data['createdAt'], float):
        print(f"🔧 Converting createdAt from float to int")
        user_data['createdAt'] = int(user_data['createdAt'])
    
    # Fix any other timestamp fields
    for field in ['lastMigration']:
        if field in user_data and isinstance(user_data[field], float):
            print(f"🔧 Converting {field} from float to int")
            user_data[field] = int(user_data[field])
    
    # Update the user profile
    user_ref.update(user_data)
    print("✅ UserProfile validation issues fixed!")
    
    # Also check and fix wardrobe items
    print("\n🔍 Checking wardrobe items for validation issues...")
    
    wardrobe_ref = db.collection('wardrobe')
    wardrobe_items = wardrobe_ref.where('userId', '==', user_id).stream()
    
    wardrobe_fixes = 0
    for item_doc in wardrobe_items:
        item_data = item_doc.to_dict()
        item_needs_fix = False
        
        # Fix timestamp fields
        for field in ['createdAt', 'updatedAt']:
            if field in item_data and isinstance(item_data[field], float):
                print(f"🔧 Converting item {item_doc.id} {field} from float to int")
                item_data[field] = int(item_data[field])
                item_needs_fix = True
        
        # Fix any other validation issues
        if 'confidence_score' in item_data and item_data['confidence_score'] is None:
            print(f"🔧 Setting item {item_doc.id} confidence_score to 0.0")
            item_data['confidence_score'] = 0.0
            item_needs_fix = True
        
        if item_needs_fix:
            item_doc.reference.update(item_data)
            wardrobe_fixes += 1
    
    print(f"✅ Fixed {wardrobe_fixes} wardrobe items")

if __name__ == "__main__":
    asyncio.run(fix_user_profile_validation()) 