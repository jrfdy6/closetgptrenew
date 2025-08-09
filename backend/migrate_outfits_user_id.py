#!/usr/bin/env python3
"""
Migration script to update outfit user_id fields to use actual Firebase user IDs.
This script will:
1. Try to detect the current user's Firebase UID from common patterns
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
        # Try to get from environment variable first
        env_user_id = os.environ.get("CURRENT_USER_ID")
        if env_user_id:
            print(f"Using user ID from environment variable: {env_user_id}")
            return env_user_id
        
        # Common user ID patterns - these are typical Firebase UID formats
        # You can add your actual user ID here if you know it
        common_user_ids = [
            # Add your actual user ID here if you know it
            # "your-actual-firebase-uid-here",
        ]
        
        if common_user_ids:
            print("Found common user IDs. Please select one:")
            for i, uid in enumerate(common_user_ids, 1):
                print(f"{i}. {uid}")
            
            try:
                choice = int(input("Enter the number of your user ID (or 0 to enter manually): "))
                if 1 <= choice <= len(common_user_ids):
                    return common_user_ids[choice - 1]
            except ValueError:
                pass
        
        # Manual entry as fallback
        print("\nPlease enter your Firebase user ID:")
        print("You can find this by:")
        print("1. Going to http://localhost:3000/debug-user")
        print("2. Looking at the browser console for '🔍 USER ID FOR MIGRATION:'")
        print("3. Copying the ID and pasting it here:")
        
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
