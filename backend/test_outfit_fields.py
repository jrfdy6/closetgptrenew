#!/usr/bin/env python3
"""
Test script to check outfit field consistency between creation and retrieval.
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
            "client_id": os.environ.get("FIREBASE_CLIENT_ID", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_CERT_URL", "")
        }
        
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None

def main():
    print("🔍 DEBUG: Starting outfit field analysis...")
    
    # Initialize Firebase
    db = initialize_firebase()
    if not db:
        print("❌ Failed to initialize Firebase")
        return
    
    # Get a few outfits to analyze their fields
    try:
        outfit_docs = db.collection('outfits').limit(5).stream()
        outfit_docs_list = list(outfit_docs)
        
        print(f"🔍 Found {len(outfit_docs_list)} outfits to analyze")
        
        for i, doc in enumerate(outfit_docs_list):
            outfit_data = doc.to_dict()
            print(f"\n📋 Outfit {i+1} (ID: {doc.id}):")
            print(f"   Fields: {list(outfit_data.keys())}")
            print(f"   user_id: {outfit_data.get('user_id', 'NOT_FOUND')}")
            print(f"   name: {outfit_data.get('name', 'NOT_FOUND')}")
            print(f"   style: {outfit_data.get('style', 'NOT_FOUND')}")
            print(f"   mood: {outfit_data.get('mood', 'NOT_FOUND')}")
            print(f"   occasion: {outfit_data.get('occasion', 'NOT_FOUND')}")
            print(f"   createdAt: {outfit_data.get('createdAt', 'NOT_FOUND')}")
            print(f"   items count: {len(outfit_data.get('items', []))}")
            
            # Check if items are strings or objects
            items = outfit_data.get('items', [])
            if items:
                first_item = items[0]
                print(f"   First item type: {type(first_item)}")
                if isinstance(first_item, dict):
                    print(f"   First item keys: {list(first_item.keys())}")
                else:
                    print(f"   First item value: {first_item}")
        
        # Check what the retrieval code expects
        print(f"\n🎯 Retrieval code expects these fields:")
        print(f"   - id (from doc.id)")
        print(f"   - name (from outfit_data.get('name', ''))")
        print(f"   - style (from outfit_data.get('style', ''))")
        print(f"   - mood (from outfit_data.get('mood', ''))")
        print(f"   - items (resolved from outfit_data.get('items', []))")
        print(f"   - occasion (from outfit_data.get('occasion', 'Casual'))")
        print(f"   - confidence_score (from outfit_data.get('confidence_score', 0.0))")
        print(f"   - reasoning (from outfit_data.get('reasoning', ''))")
        print(f"   - createdAt (from outfit_data['createdAt'])")
        
    except Exception as e:
        print(f"❌ Error analyzing outfits: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
