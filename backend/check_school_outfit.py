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

async def check_school_outfit():
    """Check the specific School Outfit that shows 0 items"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"Checking School Outfit for user: {user_id}")
    
    # Search for outfits with "School" in the name
    outfits_ref = db.collection('outfits')
    school_outfits = outfits_ref.where('user_id', '==', user_id).stream()
    
    school_outfits_found = []
    
    for doc in school_outfits:
        outfit_data = doc.to_dict()
        name = outfit_data.get('name', '')
        
        if 'school' in name.lower():
            school_outfits_found.append({
                'id': doc.id,
                'name': name,
                'items': outfit_data.get('items', []),
                'occasion': outfit_data.get('occasion'),
                'mood': outfit_data.get('mood'),
                'style': outfit_data.get('style'),
                'description': outfit_data.get('description'),
                'createdAt': outfit_data.get('createdAt'),
                'metadata': outfit_data.get('metadata', {})
            })
    
    print(f"\nFound {len(school_outfits_found)} outfits with 'School' in the name:")
    
    for outfit in school_outfits_found:
        print(f"\nOutfit: {outfit['name']}")
        print(f"  ID: {outfit['id']}")
        print(f"  Items: {len(outfit['items'])} items")
        print(f"  Occasion: {outfit['occasion']}")
        print(f"  Mood: {outfit['mood']}")
        print(f"  Style: {outfit['style']}")
        print(f"  Description: {outfit['description']}")
        print(f"  Created: {outfit['createdAt']}")
        
        if outfit['items']:
            print(f"  Item IDs: {outfit['items']}")
        else:
            print(f"  ⚠️  NO ITEMS FOUND!")
            
            # Check if this outfit ID appears in analytics
            print(f"  Checking analytics for this outfit...")
            analytics_ref = db.collection('analytics_events')
            analytics_query = analytics_ref.where('outfit_id', '==', outfit['id'])
            
            analytics_docs = analytics_query.stream()
            analytics_events = []
            
            for doc in analytics_docs:
                event_data = doc.to_dict()
                analytics_events.append({
                    'event_type': event_data.get('event_type'),
                    'timestamp': event_data.get('timestamp'),
                    'metadata': event_data.get('metadata', {})
                })
            
            print(f"    Found {len(analytics_events)} analytics events for this outfit")
            
            for event in analytics_events:
                print(f"      {event['event_type']} - {event['timestamp']}")
                if event['metadata']:
                    print(f"        Metadata: {event['metadata']}")
            
            # Check feedback collection
            print(f"  Checking feedback for this outfit...")
            feedback_ref = db.collection('outfit_feedback')
            feedback_query = feedback_ref.where('outfit_id', '==', outfit['id'])
            
            feedback_docs = feedback_query.stream()
            feedback_events = []
            
            for doc in feedback_docs:
                feedback_data = doc.to_dict()
                feedback_events.append({
                    'feedback_type': feedback_data.get('feedback_type'),
                    'rating': feedback_data.get('rating'),
                    'outfit_context': feedback_data.get('outfit_context', {})
                })
            
            print(f"    Found {len(feedback_events)} feedback events for this outfit")
            
            for feedback in feedback_events:
                print(f"      {feedback['feedback_type']} - Rating: {feedback['rating']}")
                if feedback['outfit_context']:
                    print(f"        Context: {feedback['outfit_context']}")
    
    # Also check for any outfits with "Avant-Garde" style
    print(f"\nChecking for any outfits with 'Avant-Garde' style...")
    
    avant_garde_outfits = outfits_ref.where('user_id', '==', user_id).stream()
    
    avant_garde_found = []
    
    for doc in avant_garde_outfits:
        outfit_data = doc.to_dict()
        style = outfit_data.get('style', '')
        
        if 'avant-garde' in style.lower() or 'avant garde' in style.lower():
            avant_garde_found.append({
                'id': doc.id,
                'name': outfit_data.get('name', ''),
                'items': outfit_data.get('items', []),
                'style': style
            })
    
    print(f"Found {len(avant_garde_found)} outfits with Avant-Garde style:")
    
    for outfit in avant_garde_found:
        print(f"  {outfit['name']} - {len(outfit['items'])} items")

if __name__ == "__main__":
    asyncio.run(check_school_outfit()) 