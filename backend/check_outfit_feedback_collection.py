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

async def check_outfit_feedback_collection():
    """Check the outfit_feedback collection for detailed outfit information"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"Checking outfit_feedback collection for user: {user_id}")
    
    # Get all feedback documents for this user
    feedback_ref = db.collection('outfit_feedback')
    feedback_query = feedback_ref.where('user_id', '==', user_id)
    
    feedback_docs = feedback_query.stream()
    
    feedback_data = []
    outfit_ids_in_feedback = set()
    
    for doc in feedback_docs:
        feedback = doc.to_dict()
        outfit_id = feedback.get('outfit_id')
        
        if outfit_id:
            outfit_ids_in_feedback.add(outfit_id)
        
        feedback_data.append({
            'id': doc.id,
            'outfit_id': outfit_id,
            'feedback_type': feedback.get('feedback_type'),
            'rating': feedback.get('rating'),
            'issue_category': feedback.get('issue_category'),
            'timestamp': feedback.get('timestamp'),
            'outfit_context': feedback.get('outfit_context', {}),
            'user_context': feedback.get('user_context', {}),
            'metadata': feedback.get('metadata', {})
        })
    
    print(f"\nFound {len(feedback_data)} feedback documents")
    print(f"Found {len(outfit_ids_in_feedback)} unique outfit IDs in feedback")
    
    # Show some examples
    print(f"\nSample feedback documents:")
    for feedback in feedback_data[:5]:
        print(f"  Outfit ID: {feedback['outfit_id'][:8] if feedback['outfit_id'] else 'None'}...")
        print(f"    Feedback Type: {feedback['feedback_type']}")
        print(f"    Rating: {feedback['rating']}")
        print(f"    Issue Category: {feedback['issue_category']}")
        print(f"    Outfit Context: {feedback['outfit_context']}")
        print()
    
    # Check if any feedback documents contain outfit item information
    print(f"\nLooking for feedback documents with outfit item information...")
    
    feedback_with_items = []
    for feedback in feedback_data:
        outfit_context = feedback.get('outfit_context', {})
        
        # Look for item information in outfit_context
        if 'items' in outfit_context or 'item_ids' in outfit_context or 'outfit_items' in outfit_context:
            feedback_with_items.append(feedback)
    
    print(f"Found {len(feedback_with_items)} feedback documents with item information:")
    
    for feedback in feedback_with_items[:5]:
        print(f"  Outfit ID: {feedback['outfit_id'][:8] if feedback['outfit_id'] else 'None'}...")
        print(f"    Outfit Context: {feedback['outfit_context']}")
        print()
    
    # Check if any of these outfit IDs exist in the main outfits collection
    print(f"\nChecking if feedback outfit IDs exist in main outfits collection...")
    
    outfits_ref = db.collection('outfits')
    existing_outfit_ids = set()
    
    existing_outfits = outfits_ref.where('user_id', '==', user_id).stream()
    for doc in existing_outfits:
        existing_outfit_ids.add(doc.id)
    
    missing_from_main = outfit_ids_in_feedback - existing_outfit_ids
    existing_in_main = outfit_ids_in_feedback & existing_outfit_ids
    
    print(f"  {len(existing_in_main)} outfit IDs exist in both feedback and main collection")
    print(f"  {len(missing_from_main)} outfit IDs exist only in feedback collection")
    
    if missing_from_main:
        print(f"\nOutfit IDs missing from main collection:")
        for outfit_id in list(missing_from_main)[:10]:  # Show first 10
            print(f"  {outfit_id}")
    
    # Check if we can find any outfit generation events that might have item information
    print(f"\nChecking outfit_generated events for item information...")
    
    analytics_ref = db.collection('analytics_events')
    generation_query = analytics_ref.where('user_id', '==', user_id).where('event_type', '==', 'outfit_generated')
    
    generation_docs = generation_query.stream()
    
    generation_events = []
    for doc in generation_docs:
        event_data = doc.to_dict()
        generation_events.append({
            'id': doc.id,
            'outfit_id': event_data.get('outfit_id'),
            'metadata': event_data.get('metadata', {}),
            'timestamp': event_data.get('timestamp')
        })
    
    print(f"Found {len(generation_events)} outfit_generated events:")
    
    for event in generation_events:
        print(f"  Outfit ID: {event['outfit_id'][:8] if event['outfit_id'] else 'None'}...")
        print(f"    Metadata: {event['metadata']}")
        print()
    
    # Check if any generation events have item information
    events_with_items = []
    for event in generation_events:
        metadata = event.get('metadata', {})
        if 'items' in metadata or 'item_ids' in metadata or 'outfit_items' in metadata:
            events_with_items.append(event)
    
    print(f"Found {len(events_with_items)} generation events with item information:")
    
    for event in events_with_items:
        print(f"  Outfit ID: {event['outfit_id'][:8] if event['outfit_id'] else 'None'}...")
        print(f"    Items: {event['metadata']}")
        print()

if __name__ == "__main__":
    asyncio.run(check_outfit_feedback_collection()) 