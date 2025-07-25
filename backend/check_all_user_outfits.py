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

async def check_all_user_outfits():
    """Check all outfits for the user to see what's actually in the database"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"Checking ALL outfits for user: {user_id}")
    
    # Get all outfits for this user
    outfits_ref = db.collection('outfits')
    user_outfits = outfits_ref.where('user_id', '==', user_id).stream()
    
    all_outfits = []
    
    for doc in user_outfits:
        outfit_data = doc.to_dict()
        all_outfits.append({
            'id': doc.id,
            'name': outfit_data.get('name', 'Unknown'),
            'items': outfit_data.get('items', []),
            'occasion': outfit_data.get('occasion'),
            'mood': outfit_data.get('mood'),
            'style': outfit_data.get('style'),
            'description': outfit_data.get('description'),
            'createdAt': outfit_data.get('createdAt'),
            'user_id': outfit_data.get('user_id')
        })
    
    print(f"\nFound {len(all_outfits)} total outfits for user {user_id}")
    
    # Sort by name for easier reading
    all_outfits.sort(key=lambda x: x['name'].lower())
    
    outfits_with_items = []
    outfits_without_items = []
    
    for outfit in all_outfits:
        if outfit['items']:
            outfits_with_items.append(outfit)
        else:
            outfits_without_items.append(outfit)
    
    print(f"\nOutfits WITH items: {len(outfits_with_items)}")
    for outfit in outfits_with_items:
        print(f"  {outfit['name']} - {len(outfit['items'])} items")
        print(f"    Occasion: {outfit['occasion']}")
        print(f"    Style: {outfit['style']}")
        print(f"    Mood: {outfit['mood']}")
        print()
    
    print(f"\nOutfits WITHOUT items: {len(outfits_without_items)}")
    for outfit in outfits_without_items:
        print(f"  {outfit['name']} - 0 items")
        print(f"    Occasion: {outfit['occasion']}")
        print(f"    Style: {outfit['style']}")
        print(f"    Mood: {outfit['mood']}")
        print(f"    Description: {outfit['description']}")
        print()
    
    # Check if any outfits have "School" or "Avant-Garde" in any field
    print(f"\nSearching for outfits with 'School' or 'Avant-Garde' in any field...")
    
    school_related = []
    avant_garde_related = []
    
    for outfit in all_outfits:
        # Check name, occasion, style, description
        searchable_text = f"{outfit['name']} {outfit['occasion']} {outfit['style']} {outfit['description']}".lower()
        
        if 'school' in searchable_text:
            school_related.append(outfit)
        
        if 'avant-garde' in searchable_text or 'avant garde' in searchable_text:
            avant_garde_related.append(outfit)
    
    print(f"Found {len(school_related)} outfits related to 'School':")
    for outfit in school_related:
        print(f"  {outfit['name']} - {len(outfit['items'])} items")
        print(f"    Occasion: {outfit['occasion']}")
        print(f"    Style: {outfit['style']}")
        print()
    
    print(f"Found {len(avant_garde_related)} outfits related to 'Avant-Garde':")
    for outfit in avant_garde_related:
        print(f"  {outfit['name']} - {len(outfit['items'])} items")
        print(f"    Occasion: {outfit['occasion']}")
        print(f"    Style: {outfit['style']}")
        print()
    
    # Check if there are any outfits with "relaxed" mood
    print(f"\nSearching for outfits with 'relaxed' mood...")
    
    relaxed_outfits = [outfit for outfit in all_outfits if outfit.get('mood', '').lower() == 'relaxed']
    
    print(f"Found {len(relaxed_outfits)} outfits with 'relaxed' mood:")
    for outfit in relaxed_outfits:
        print(f"  {outfit['name']} - {len(outfit['items'])} items")
        print(f"    Occasion: {outfit['occasion']}")
        print(f"    Style: {outfit['style']}")
        print()

if __name__ == "__main__":
    asyncio.run(check_all_user_outfits()) 