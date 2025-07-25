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

async def check_failed_outfit_items():
    """Check if failed outfits still have their items saved"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"🔍 Checking failed outfits for user: {user_id}")
    
    # Get recent outfits for this user
    outfits_ref = db.collection('outfits')
    user_outfits = outfits_ref.where('user_id', '==', user_id).stream()
    
    failed_outfits = []
    successful_outfits = []
    
    for outfit_doc in user_outfits:
        outfit_data = outfit_doc.to_dict()
        outfit_id = outfit_doc.id
        
        was_successful = outfit_data.get('wasSuccessful', True)
        items = outfit_data.get('items', [])
        pieces = outfit_data.get('pieces', [])
        validation_errors = outfit_data.get('validationErrors', [])
        
        outfit_info = {
            'id': outfit_id,
            'name': outfit_data.get('name', 'Unknown'),
            'wasSuccessful': was_successful,
            'items_count': len(items),
            'pieces_count': len(pieces),
            'validation_errors': validation_errors,
            'items': items,
            'pieces': pieces
        }
        
        if was_successful:
            successful_outfits.append(outfit_info)
        else:
            failed_outfits.append(outfit_info)
    
    print(f"\n📊 Analysis Results:")
    print(f"   - Total outfits checked: {len(failed_outfits) + len(successful_outfits)}")
    print(f"   - Successful outfits: {len(successful_outfits)}")
    print(f"   - Failed outfits: {len(failed_outfits)}")
    
    print(f"\n✅ Successful Outfits:")
    for outfit in successful_outfits[:3]:  # Show first 3
        print(f"   - {outfit['name']}")
        print(f"     Items: {outfit['items_count']}, Pieces: {outfit['pieces_count']}")
        if outfit['items']:
            print(f"     Item IDs: {outfit['items'][:3]}...")
    
    print(f"\n❌ Failed Outfits:")
    for outfit in failed_outfits[:5]:  # Show first 5
        print(f"   - {outfit['name']}")
        print(f"     Items: {outfit['items_count']}, Pieces: {outfit['pieces_count']}")
        print(f"     Success: {outfit['wasSuccessful']}")
        if outfit['validation_errors']:
            print(f"     Errors: {outfit['validation_errors'][:2]}...")
        if outfit['items']:
            print(f"     Item IDs: {outfit['items'][:3]}...")
        else:
            print(f"     ⚠️  NO ITEMS SAVED!")
        print()
    
    # Check the most recent failed outfit in detail
    if failed_outfits:
        latest_failed = failed_outfits[0]
        print(f"\n🔍 Latest Failed Outfit Details:")
        print(f"   ID: {latest_failed['id']}")
        print(f"   Name: {latest_failed['name']}")
        print(f"   Items count: {latest_failed['items_count']}")
        print(f"   Pieces count: {latest_failed['pieces_count']}")
        print(f"   Was successful: {latest_failed['wasSuccessful']}")
        
        if latest_failed['items']:
            print(f"   Items saved: {latest_failed['items']}")
        else:
            print(f"   ⚠️  No items saved!")
            
        if latest_failed['pieces']:
            print(f"   Pieces saved: {len(latest_failed['pieces'])} pieces")
            for piece in latest_failed['pieces'][:2]:
                print(f"     - {piece.get('name', 'Unknown')} ({piece.get('type', 'Unknown')})")
        else:
            print(f"   ⚠️  No pieces saved!")

if __name__ == "__main__":
    asyncio.run(check_failed_outfit_items()) 