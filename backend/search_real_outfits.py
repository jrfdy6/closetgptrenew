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

async def search_real_outfits():
    """Search for outfits that might be real user-created outfits"""
    
    print("Searching for potential real outfits...")
    
    # Query all outfits
    outfits_ref = db.collection('outfits')
    outfit_docs = outfits_ref.stream()
    
    potential_real_outfits = []
    recent_outfits = []
    
    for doc in outfit_docs:
        outfit_data = doc.to_dict()
        name = outfit_data.get('name', '')
        description = outfit_data.get('description', '')
        created_at = outfit_data.get('createdAt', 0)
        user_id = outfit_data.get('user_id', '')
        
        # Check for outfits with custom descriptions
        if description and len(description) > 20:
            potential_real_outfits.append({
                'id': doc.id,
                'name': name,
                'description': description[:100] + '...' if len(description) > 100 else description,
                'user_id': user_id,
                'created_at': created_at
            })
        
        # Check for recent outfits (last 30 days)
        if created_at > 1704067200:  # Jan 1, 2024
            recent_outfits.append({
                'id': doc.id,
                'name': name,
                'user_id': user_id,
                'created_at': created_at
            })
    
    print(f"\nFound {len(potential_real_outfits)} outfits with custom descriptions:")
    for outfit in potential_real_outfits[:10]:  # Show first 10
        print(f"  {outfit['name']} (User: {outfit['user_id']})")
        print(f"    Description: {outfit['description']}")
        print()
    
    print(f"\nFound {len(recent_outfits)} outfits created in 2024:")
    for outfit in recent_outfits[:10]:  # Show first 10
        created_date = datetime.fromtimestamp(outfit['created_at'])
        print(f"  {outfit['name']} (User: {outfit['user_id']}) - {created_date}")
    
    # Check if there are any outfits with feedback
    outfits_with_feedback = []
    for doc in outfit_docs:
        outfit_data = doc.to_dict()
        if outfit_data.get('userFeedback') or outfit_data.get('feedback_summary'):
            outfits_with_feedback.append({
                'id': doc.id,
                'name': outfit_data.get('name', ''),
                'user_id': outfit_data.get('user_id', ''),
                'feedback': outfit_data.get('userFeedback') or outfit_data.get('feedback_summary')
            })
    
    print(f"\nFound {len(outfits_with_feedback)} outfits with user feedback:")
    for outfit in outfits_with_feedback[:5]:  # Show first 5
        print(f"  {outfit['name']} (User: {outfit['user_id']})")
        print(f"    Feedback: {outfit['feedback']}")

if __name__ == "__main__":
    asyncio.run(search_real_outfits()) 