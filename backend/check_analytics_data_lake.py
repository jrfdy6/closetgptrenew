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

async def check_analytics_data_lake():
    """Check the analytics data lake for outfit-related data"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Your user ID
    
    print(f"Checking analytics data lake for user: {user_id}")
    
    # Check analytics_events collection
    analytics_ref = db.collection('analytics_events')
    analytics_query = analytics_ref.where('user_id', '==', user_id)
    
    analytics_docs = analytics_query.stream()
    
    outfit_events = []
    item_events = []
    feedback_events = []
    
    for doc in analytics_docs:
        event_data = doc.to_dict()
        event_type = event_data.get('event_type', '')
        
        if 'outfit' in event_type.lower():
            outfit_events.append({
                'id': doc.id,
                'event_type': event_type,
                'outfit_id': event_data.get('outfit_id'),
                'timestamp': event_data.get('timestamp'),
                'metadata': event_data.get('metadata', {})
            })
        elif 'item' in event_type.lower():
            item_events.append({
                'id': doc.id,
                'event_type': event_type,
                'item_id': event_data.get('item_id'),
                'outfit_id': event_data.get('outfit_id'),
                'timestamp': event_data.get('timestamp')
            })
        elif 'feedback' in event_type.lower():
            feedback_events.append({
                'id': doc.id,
                'event_type': event_type,
                'outfit_id': event_data.get('outfit_id'),
                'rating': event_data.get('feedback_rating'),
                'timestamp': event_data.get('timestamp')
            })
    
    print(f"\nFound {len(outfit_events)} outfit-related events:")
    for event in outfit_events[:5]:  # Show first 5
        print(f"  {event['event_type']} - Outfit: {event['outfit_id']}")
        if event['metadata']:
            print(f"    Metadata: {event['metadata']}")
    
    print(f"\nFound {len(item_events)} item interaction events:")
    for event in item_events[:5]:  # Show first 5
        print(f"  {event['event_type']} - Item: {event['item_id']} - Outfit: {event['outfit_id']}")
    
    print(f"\nFound {len(feedback_events)} feedback events:")
    for event in feedback_events[:5]:  # Show first 5
        print(f"  {event['event_type']} - Outfit: {event['outfit_id']} - Rating: {event['rating']}")
    
    # Check if there are any unique outfit IDs in the analytics
    unique_outfit_ids = set()
    for event in outfit_events + item_events + feedback_events:
        if event.get('outfit_id'):
            unique_outfit_ids.add(event['outfit_id'])
    
    print(f"\nUnique outfit IDs found in analytics: {len(unique_outfit_ids)}")
    for outfit_id in list(unique_outfit_ids)[:10]:  # Show first 10
        print(f"  {outfit_id}")
    
    # Check if any of these outfit IDs exist in the outfits collection
    if unique_outfit_ids:
        print(f"\nChecking if these outfit IDs exist in outfits collection...")
        outfits_ref = db.collection('outfits')
        
        existing_outfits = []
        missing_outfits = []
        
        for outfit_id in unique_outfit_ids:
            outfit_doc = outfits_ref.document(outfit_id).get()
            if outfit_doc.exists:
                outfit_data = outfit_doc.to_dict()
                existing_outfits.append({
                    'id': outfit_id,
                    'name': outfit_data.get('name', 'Unknown'),
                    'user_id': outfit_data.get('user_id', 'Unknown')
                })
            else:
                missing_outfits.append(outfit_id)
        
        print(f"  {len(existing_outfits)} outfits found in outfits collection:")
        for outfit in existing_outfits:
            print(f"    {outfit['name']} (User: {outfit['user_id']})")
        
        print(f"  {len(missing_outfits)} outfits missing from outfits collection:")
        for outfit_id in missing_outfits[:5]:  # Show first 5
            print(f"    {outfit_id}")
    
    # Check for any backup or export files
    print(f"\nChecking for backup/export files...")
    
    # Look for any collections that might contain backup data
    collections = ['outfits_backup', 'outfits_archive', 'outfits_export', 'backup_outfits']
    
    for collection_name in collections:
        try:
            backup_ref = db.collection(collection_name)
            backup_docs = backup_ref.where('user_id', '==', user_id).stream()
            backup_count = 0
            for doc in backup_docs:
                backup_count += 1
            
            if backup_count > 0:
                print(f"  Found {backup_count} outfits in {collection_name} collection")
            else:
                print(f"  No outfits found in {collection_name} collection")
        except Exception as e:
            print(f"  Error checking {collection_name}: {e}")

if __name__ == "__main__":
    asyncio.run(check_analytics_data_lake()) 