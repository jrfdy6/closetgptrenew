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

async def fix_profile_data_structure():
    """Fix profile data structure by converting string preferences to lists"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"🔧 Fixing profile data structure for user: {user_id}")
    
    # Get user profile
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        print("❌ User profile not found")
        return
    
    user_data = user_doc.to_dict()
    print(f"📋 Current user data: {user_data}")
    
    # Check if preferences need fixing
    preferences = user_data.get('preferences', {})
    needs_fix = False
    
    # Check formality
    if 'formality' in preferences and isinstance(preferences['formality'], str):
        print(f"🔧 Converting formality from string '{preferences['formality']}' to list")
        preferences['formality'] = [preferences['formality']]
        needs_fix = True
    
    # Check budget
    if 'budget' in preferences and isinstance(preferences['budget'], str):
        print(f"🔧 Converting budget from string '{preferences['budget']}' to list")
        preferences['budget'] = [preferences['budget']]
        needs_fix = True
    
    # Check other preference fields that might be strings
    for key in ['style', 'colors', 'patterns']:
        if key in preferences and isinstance(preferences[key], str):
            print(f"🔧 Converting {key} from string '{preferences[key]}' to list")
            preferences[key] = [preferences[key]]
            needs_fix = True
    
    if needs_fix:
        # Update the user profile
        user_data['preferences'] = preferences
        user_data['updatedAt'] = datetime.now().timestamp()
        
        user_ref.update(user_data)
        print("✅ Profile data structure fixed!")
        print(f"📋 Updated preferences: {preferences}")
    else:
        print("✅ Profile data structure is already correct")
    
    # Also check and fix any wardrobe items that might have similar issues
    print("\n🔍 Checking wardrobe items for data structure issues...")
    
    wardrobe_ref = db.collection('wardrobe')
    wardrobe_items = wardrobe_ref.where('userId', '==', user_id).stream()
    
    wardrobe_fixes = 0
    for item_doc in wardrobe_items:
        item_data = item_doc.to_dict()
        item_needs_fix = False
        
        # Check if colors is a string instead of list
        if 'colors' in item_data and isinstance(item_data['colors'], str):
            print(f"🔧 Converting item {item_doc.id} colors from string to list")
            item_data['colors'] = [item_data['colors']]
            item_needs_fix = True
        
        # Check if patterns is a string instead of list
        if 'patterns' in item_data and isinstance(item_data['patterns'], str):
            print(f"🔧 Converting item {item_doc.id} patterns from string to list")
            item_data['patterns'] = [item_data['patterns']]
            item_needs_fix = True
        
        if item_needs_fix:
            item_doc.reference.update(item_data)
            wardrobe_fixes += 1
    
    print(f"✅ Fixed {wardrobe_fixes} wardrobe items")

if __name__ == "__main__":
    asyncio.run(fix_profile_data_structure()) 