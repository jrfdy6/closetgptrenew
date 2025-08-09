#!/usr/bin/env python3
"""
Test script to check outfit retrieval for a specific user ID.
"""

import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def initialize_firebase():
    """Initialize Firebase with environment variables."""
    try:
        firebase_creds = {
            "type": "service_account",
            "project_id": os.environ["FIREBASE_PROJECT_ID"],
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID") or os.environ.get("private_key_id", ""),
            "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
            "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
            "client_id": os.environ["FIREBASE_CLIENT_ID"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
        }
        
        cred = credentials.Certificate(firebase_creds)
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'projectId': os.environ["FIREBASE_PROJECT_ID"]
            })
        
        return firestore.client()
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
        return None

def test_outfit_retrieval():
    """Test outfit retrieval for the specific user ID."""
    db = initialize_firebase()
    if not db:
        print("Failed to initialize Firebase. Exiting.")
        return
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    print(f"Testing outfit retrieval for user ID: {user_id}")
    
    # Test 1: Direct query by user_id field
    print("\n=== Test 1: Query by user_id field ===")
    try:
        outfit_docs = db.collection('outfits').where('user_id', '==', user_id).limit(10).stream()
        outfit_list = list(outfit_docs)
        print(f"Found {len(outfit_list)} outfits with user_id = '{user_id}'")
        
        for i, doc in enumerate(outfit_list[:5]):  # Show first 5
            outfit_data = doc.to_dict()
            print(f"  {i+1}. {outfit_data.get('name', 'Unknown')} (ID: {doc.id})")
            print(f"      Created: {outfit_data.get('createdAt', 'Unknown')}")
            print(f"      Items: {len(outfit_data.get('items', []))}")
    except Exception as e:
        print(f"Error in Test 1: {e}")
    
    # Test 2: Get all outfits and check user_id field
    print("\n=== Test 2: Check all outfits for user_id field ===")
    try:
        all_outfits = db.collection('outfits').limit(20).stream()
        outfit_count = 0
        user_id_count = 0
        other_user_count = 0
        no_user_id_count = 0
        
        for doc in all_outfits:
            outfit_data = doc.to_dict()
            outfit_count += 1
            current_user_id = outfit_data.get('user_id')
            
            if current_user_id == user_id:
                user_id_count += 1
            elif current_user_id is None:
                no_user_id_count += 1
            else:
                other_user_count += 1
        
        print(f"Total outfits checked: {outfit_count}")
        print(f"Outfits with your user_id: {user_id_count}")
        print(f"Outfits with other user_id: {other_user_count}")
        print(f"Outfits with no user_id: {no_user_id_count}")
        
    except Exception as e:
        print(f"Error in Test 2: {e}")
    
    # Test 3: Check recent outfits (last 10)
    print("\n=== Test 3: Check recent outfits ===")
    try:
        all_outfits = db.collection('outfits').order_by('createdAt', direction=firestore.Query.DESCENDING).limit(10).stream()
        
        recent_outfits = []
        for doc in all_outfits:
            outfit_data = doc.to_dict()
            recent_outfits.append({
                'id': doc.id,
                'name': outfit_data.get('name', 'Unknown'),
                'user_id': outfit_data.get('user_id', 'None'),
                'createdAt': outfit_data.get('createdAt', 'Unknown'),
                'items_count': len(outfit_data.get('items', []))
            })
        
        print("Recent outfits:")
        for i, outfit in enumerate(recent_outfits):
            print(f"  {i+1}. {outfit['name']}")
            print(f"      User ID: {outfit['user_id']}")
            print(f"      Created: {outfit['createdAt']}")
            print(f"      Items: {outfit['items_count']}")
            
    except Exception as e:
        print(f"Error in Test 3: {e}")

if __name__ == "__main__":
    test_outfit_retrieval() 