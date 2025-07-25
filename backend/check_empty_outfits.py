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

async def check_empty_outfits():
    """Check the generation details of empty outfits"""
    
    # The two empty outfits we identified
    empty_outfit_ids = [
        "701095da-1b04-4533-ada2-c8d5a573dece",  # Avant-Garde Vacation Outfit
        "da6c285a-5f6c-4178-8642-1400c4107486"   # Edgy Festival Outfit
    ]
    
    for outfit_id in empty_outfit_ids:
        print(f"\n🔍 Checking empty outfit: {outfit_id}")
        
        # Get the outfit document
        outfit_doc = db.collection('outfits').document(outfit_id).get()
        if not outfit_doc.exists:
            print(f"❌ Outfit {outfit_id} not found")
            continue
            
        outfit_data = outfit_doc.to_dict()
        
        print(f"📋 Outfit name: {outfit_data.get('name', 'Unknown')}")
        print(f"   Items count: {len(outfit_data.get('items', []))}")
        print(f"   Pieces count: {len(outfit_data.get('pieces', []))}")
        print(f"   Was successful: {outfit_data.get('wasSuccessful', 'Unknown')}")
        print(f"   Validation errors: {outfit_data.get('validationErrors', [])}")
        print(f"   Generation method: {outfit_data.get('generation_method', 'Unknown')}")
        
        # Check for generation trace
        if 'generation_trace' in outfit_data:
            trace = outfit_data['generation_trace']
            print(f"   Generation trace length: {len(trace) if isinstance(trace, list) else 'Not a list'}")
            
            if isinstance(trace, list):
                print(f"   Trace steps:")
                for i, step in enumerate(trace[:10]):  # Show first 10 steps
                    step_type = step.get('step', 'Unknown')
                    method = step.get('method', 'Unknown')
                    print(f"     {i+1}. {step_type} - {method}")
                if len(trace) > 10:
                    print(f"     ... and {len(trace) - 10} more steps")
        
        # Check for validation details
        if 'validation_details' in outfit_data:
            validation = outfit_data['validation_details']
            print(f"   Validation details:")
            print(f"     Errors: {len(validation.get('errors', []))}")
            print(f"     Fixes: {len(validation.get('fixes', []))}")
        
        # Check for metadata
        if 'metadata' in outfit_data:
            metadata = outfit_data['metadata']
            print(f"   Metadata keys: {list(metadata.keys())}")
            
            if 'healing_log' in metadata:
                healing_log = metadata['healing_log']
                print(f"   Healing log: {healing_log}")

if __name__ == "__main__":
    asyncio.run(check_empty_outfits()) 