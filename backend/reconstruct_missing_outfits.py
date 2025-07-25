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

async def reconstruct_missing_outfits():
    """Try to reconstruct missing outfits from analytics data"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"Attempting to reconstruct missing outfits for user: {user_id}")
    
    # Get all analytics events for this user
    analytics_ref = db.collection('analytics_events')
    analytics_query = analytics_ref.where('user_id', '==', user_id)
    
    analytics_docs = analytics_query.stream()
    
    # Group events by outfit ID
    outfit_events = {}
    
    for doc in analytics_docs:
        event_data = doc.to_dict()
        outfit_id = event_data.get('outfit_id')
        
        if outfit_id:
            if outfit_id not in outfit_events:
                outfit_events[outfit_id] = []
            outfit_events[outfit_id].append(event_data)
    
    print(f"\nFound {len(outfit_events)} unique outfit IDs in analytics")
    
    # Check which outfits are missing from the main collection
    outfits_ref = db.collection('outfits')
    existing_outfit_ids = set()
    
    existing_outfits = outfits_ref.where('user_id', '==', user_id).stream()
    for doc in existing_outfits:
        existing_outfit_ids.add(doc.id)
    
    missing_outfit_ids = set(outfit_events.keys()) - existing_outfit_ids
    
    print(f"  {len(existing_outfit_ids)} outfits exist in main collection")
    print(f"  {len(missing_outfit_ids)} outfits are missing from main collection")
    
    # Try to reconstruct missing outfits
    reconstructed_outfits = []
    
    for outfit_id in missing_outfit_ids:
        events = outfit_events[outfit_id]
        
        # Find the most recent outfit_generated event
        generation_event = None
        feedback_events = []
        view_events = []
        
        for event in events:
            event_type = event.get('event_type', '')
            
            if event_type == 'outfit_generated':
                if not generation_event or event.get('timestamp', '') > generation_event.get('timestamp', ''):
                    generation_event = event
            elif event_type == 'outfit_feedback':
                feedback_events.append(event)
            elif event_type == 'outfit_viewed':
                view_events.append(event)
        
        if generation_event:
            metadata = generation_event.get('metadata', {})
            
            # Try to reconstruct outfit data
            reconstructed_outfit = {
                'id': outfit_id,
                'user_id': user_id,
                'name': f"Reconstructed Outfit {outfit_id[:8]}",
                'occasion': metadata.get('occasion', 'Casual'),
                'items': [],  # We'll need to find items from other events
                'createdAt': generation_event.get('timestamp'),
                'metadata': metadata,
                'feedback_count': len(feedback_events),
                'view_count': len(view_events),
                'reconstructed': True
            }
            
            # Try to find items from item interaction events
            item_ids = set()
            for event in events:
                if event.get('event_type') == 'item_interaction':
                    item_id = event.get('item_id')
                    if item_id:
                        item_ids.add(item_id)
            
            if item_ids:
                reconstructed_outfit['items'] = list(item_ids)
            
            reconstructed_outfits.append(reconstructed_outfit)
    
    print(f"\nSuccessfully reconstructed {len(reconstructed_outfits)} outfits:")
    
    for outfit in reconstructed_outfits[:10]:  # Show first 10
        print(f"  {outfit['name']}")
        print(f"    Occasion: {outfit['occasion']}")
        print(f"    Items: {len(outfit['items'])} items")
        print(f"    Feedback: {outfit['feedback_count']} events")
        print(f"    Views: {outfit['view_count']} events")
        if outfit['items']:
            print(f"    Item IDs: {outfit['items'][:3]}...")  # Show first 3
        print()
    
    # Show some detailed examples
    if reconstructed_outfits:
        print("Detailed example of reconstructed outfit:")
        example = reconstructed_outfits[0]
        print(f"  ID: {example['id']}")
        print(f"  Name: {example['name']}")
        print(f"  Occasion: {example['occasion']}")
        print(f"  Created: {example['createdAt']}")
        print(f"  Items: {example['items']}")
        print(f"  Metadata: {example['metadata']}")
        
        # Check if the items still exist in wardrobe
        if example['items']:
            print(f"\nChecking if items still exist in wardrobe...")
            wardrobe_ref = db.collection('wardrobe')
            
            existing_items = []
            missing_items = []
            
            for item_id in example['items']:
                item_doc = wardrobe_ref.document(item_id).get()
                if item_doc.exists:
                    item_data = item_doc.to_dict()
                    existing_items.append({
                        'id': item_id,
                        'name': item_data.get('name', 'Unknown'),
                        'type': item_data.get('type', 'Unknown')
                    })
                else:
                    missing_items.append(item_id)
            
            print(f"  {len(existing_items)} items still exist in wardrobe:")
            for item in existing_items:
                print(f"    {item['name']} ({item['type']})")
            
            if missing_items:
                print(f"  {len(missing_items)} items missing from wardrobe:")
                for item_id in missing_items[:3]:  # Show first 3
                    print(f"    {item_id}")

if __name__ == "__main__":
    asyncio.run(reconstruct_missing_outfits()) 