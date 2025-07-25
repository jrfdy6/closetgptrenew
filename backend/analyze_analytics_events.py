#!/usr/bin/env python3

import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate('service-account-key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

async def analyze_analytics_events():
    """Analyze analytics events in detail"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"Analyzing analytics events for user: {user_id}")
    
    # Get all analytics events for this user
    analytics_ref = db.collection('analytics_events')
    analytics_query = analytics_ref.where('user_id', '==', user_id)
    
    analytics_docs = analytics_query.stream()
    
    # Analyze event types
    event_types = defaultdict(int)
    outfit_events = defaultdict(list)
    events_with_items = []
    
    for doc in analytics_docs:
        event_data = doc.to_dict()
        event_type = event_data.get('event_type', 'unknown')
        outfit_id = event_data.get('outfit_id')
        item_id = event_data.get('item_id')
        
        event_types[event_type] += 1
        
        if outfit_id:
            outfit_events[outfit_id].append(event_data)
        
        if item_id:
            events_with_items.append({
                'event_type': event_type,
                'item_id': item_id,
                'outfit_id': outfit_id,
                'timestamp': event_data.get('timestamp'),
                'metadata': event_data.get('metadata', {})
            })
    
    print(f"\nEvent type breakdown:")
    for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {event_type}: {count}")
    
    print(f"\nFound {len(outfit_events)} unique outfit IDs with events")
    print(f"Found {len(events_with_items)} events with item IDs")
    
    # Show some examples of events with items
    print(f"\nSample events with items:")
    for event in events_with_items[:10]:
        print(f"  {event['event_type']} - Item: {event['item_id'][:8]}... - Outfit: {event['outfit_id'][:8] if event['outfit_id'] else 'None'}...")
    
    # Look for events that might contain outfit data
    print(f"\nLooking for events with detailed outfit information...")
    
    detailed_outfit_events = []
    for doc in analytics_docs:
        event_data = doc.to_dict()
        metadata = event_data.get('metadata', {})
        
        # Look for events with outfit-related metadata
        if any(key in str(metadata).lower() for key in ['outfit', 'occasion', 'items', 'generation']):
            detailed_outfit_events.append({
                'event_type': event_data.get('event_type'),
                'outfit_id': event_data.get('outfit_id'),
                'metadata': metadata,
                'timestamp': event_data.get('timestamp')
            })
    
    print(f"Found {len(detailed_outfit_events)} events with detailed outfit metadata:")
    
    for event in detailed_outfit_events[:10]:
        print(f"  {event['event_type']} - Outfit: {event['outfit_id'][:8] if event['outfit_id'] else 'None'}...")
        print(f"    Metadata: {event['metadata']}")
        print()
    
    # Check for any events that might contain item lists
    print(f"\nLooking for events that might contain item lists...")
    
    events_with_item_lists = []
    for doc in analytics_docs:
        event_data = doc.to_dict()
        metadata = event_data.get('metadata', {})
        
        # Look for metadata that might contain item information
        if isinstance(metadata, dict):
            for key, value in metadata.items():
                if 'item' in key.lower() and isinstance(value, (list, str)):
                    events_with_item_lists.append({
                        'event_type': event_data.get('event_type'),
                        'outfit_id': event_data.get('outfit_id'),
                        'key': key,
                        'value': value,
                        'timestamp': event_data.get('timestamp')
                    })
    
    print(f"Found {len(events_with_item_lists)} events with potential item lists:")
    
    for event in events_with_item_lists[:10]:
        print(f"  {event['event_type']} - Outfit: {event['outfit_id'][:8] if event['outfit_id'] else 'None'}...")
        print(f"    {event['key']}: {event['value']}")
        print()
    
    # Check for any backup or export collections that might contain outfit data
    print(f"\nChecking for any other collections that might contain outfit data...")
    
    # List all collections
    collections = db.collections()
    collection_names = [col.id for col in collections]
    
    outfit_related_collections = [name for name in collection_names if 'outfit' in name.lower() or 'wardrobe' in name.lower()]
    
    print(f"Found {len(outfit_related_collections)} outfit-related collections:")
    for collection_name in outfit_related_collections:
        print(f"  {collection_name}")
        
        # Check if this collection has data for our user
        try:
            collection_ref = db.collection(collection_name)
            if 'user_id' in collection_ref.document().get().to_dict() if collection_ref.document().get().exists else {}:
                user_docs = collection_ref.where('user_id', '==', user_id).stream()
                count = sum(1 for _ in user_docs)
                print(f"    {count} documents for user {user_id}")
            else:
                # Just count total documents
                docs = collection_ref.stream()
                count = sum(1 for _ in docs)
                print(f"    {count} total documents")
        except Exception as e:
            print(f"    Error checking collection: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_analytics_events()) 