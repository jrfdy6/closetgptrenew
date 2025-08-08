#!/usr/bin/env python3
"""
Migration script to update outfit user_id fields to use actual Firebase user IDs.
This script will:
1. Get the current user's Firebase UID from authentication
2. Update all outfits that have the old test user ID to use the real user ID
3. Also update any outfits that have no user_id field
"""

import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Firebase
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

def get_user_firebase_uid():
    """Get the current user's Firebase UID by checking recent authentication."""
    try:
        # This is a simplified approach - in a real scenario, you'd get this from the frontend
        # For now, we'll use a common pattern or ask the user
        print("Please enter your Firebase user ID (you can find this in your browser's developer tools):")
        print("1. Open your browser's developer tools (F12)")
        print("2. Go to the Console tab")
        print("3. Type: firebase.auth().currentUser.uid")
        print("4. Copy the result and paste it here:")
        
        user_id = input().strip()
        if not user_id:
            print("No user ID provided. Exiting.")
            return None
        
        return user_id
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return None

def migrate_outfits_user_id():
    """Migrate all outfits to use the correct user ID."""
    db = initialize_firebase()
    if not db:
        print("Failed to initialize Firebase. Exiting.")
        return
    
    user_id = get_user_firebase_uid()
    if not user_id:
        print("No valid user ID provided. Exiting.")
        return
    
    print(f"Starting migration for user ID: {user_id}")
    
    # Get all outfits
    outfits_ref = db.collection('outfits')
    outfits = outfits_ref.stream()
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for outfit_doc in outfits:
        try:
            outfit_data = outfit_doc.to_dict()
            current_user_id = outfit_data.get('user_id')
            
            # Check if this outfit needs updating
            needs_update = False
            reason = ""
            
            if not current_user_id:
                needs_update = True
                reason = "no user_id field"
            elif current_user_id == "dANqjiI0CKgaitxzYtw1bhtvQrG3":
                needs_update = True
                reason = "old test user ID"
            elif current_user_id != user_id:
                needs_update = True
                reason = f"different user ID (current: {current_user_id})"
            
            if needs_update:
                print(f"Updating outfit {outfit_doc.id} ({outfit_data.get('name', 'Unknown')}) - {reason}")
                
                # Update the outfit with the correct user ID
                outfit_data['user_id'] = user_id
                outfit_data['updatedAt'] = int(datetime.now().timestamp())
                
                outfits_ref.document(outfit_doc.id).set(outfit_data)
                updated_count += 1
            else:
                print(f"Skipping outfit {outfit_doc.id} ({outfit_data.get('name', 'Unknown')}) - already has correct user ID")
                skipped_count += 1
                
        except Exception as e:
            print(f"Error updating outfit {outfit_doc.id}: {e}")
            error_count += 1
    
    print(f"\nMigration completed!")
    print(f"Updated: {updated_count} outfits")
    print(f"Skipped: {skipped_count} outfits")
    print(f"Errors: {error_count} outfits")
    
    if updated_count > 0:
        print(f"\nAll outfits have been updated to use user ID: {user_id}")
        print("You should now see your outfits in the app!")

if __name__ == "__main__":
    migrate_outfits_user_id()
