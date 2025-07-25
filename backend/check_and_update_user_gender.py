#!/usr/bin/env python3
"""
Script to check and update user gender in profile.
This helps with gender-specific trend filtering.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import sys

# Initialize Firebase
try:
    cred = credentials.Certificate("service-account-key.json")
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    sys.exit(1)

db = firestore.client()

def check_user_profile(user_id: str):
    """Check the current user profile."""
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            print(f"❌ User profile not found for ID: {user_id}")
            return None
        
        user_data = user_doc.to_dict()
        print(f"👤 User Profile for {user_data.get('name', 'Unknown')}:")
        print(f"   Email: {user_data.get('email', 'N/A')}")
        print(f"   Gender: {user_data.get('gender', 'NOT SET')}")
        print(f"   Body Type: {user_data.get('bodyType', 'N/A')}")
        
        return user_data
    except Exception as e:
        print(f"❌ Error checking user profile: {e}")
        return None

def update_user_gender(user_id: str, gender: str):
    """Update the user's gender in their profile."""
    if gender not in ['male', 'female']:
        print("❌ Gender must be 'male' or 'female'")
        return False
    
    try:
        user_ref = db.collection('users').document(user_id)
        user_ref.update({
            'gender': gender,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        print(f"✅ Successfully updated gender to '{gender}' for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Error updating user gender: {e}")
        return False

def main():
    print("🔍 User Gender Checker & Updater")
    print("=" * 40)
    
    # You can replace this with your actual user ID
    user_id = input("Enter your user ID (or press Enter to use 'dANqjiI0CKgaitxzYtw1bhtvQrG3'): ").strip()
    if not user_id:
        user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print(f"\n📋 Checking profile for user: {user_id}")
    user_data = check_user_profile(user_id)
    
    if user_data:
        current_gender = user_data.get('gender')
        
        if not current_gender:
            print("\n⚠️  No gender set in profile!")
            print("This is why you're seeing all trends (including ballet flats for men).")
            
            new_gender = input("\nEnter your gender (male/female): ").strip().lower()
            if new_gender in ['male', 'female']:
                if update_user_gender(user_id, new_gender):
                    print(f"\n🎉 Gender updated! You should now see {new_gender}-specific trends.")
                    print("Please refresh your dashboard to see the changes.")
            else:
                print("❌ Invalid gender. Please run the script again with 'male' or 'female'.")
        else:
            print(f"\n✅ Gender is already set to: {current_gender}")
            print("If you're still seeing inappropriate trends, try refreshing the dashboard.")
            
            change_gender = input("\nDo you want to change your gender? (y/n): ").strip().lower()
            if change_gender == 'y':
                new_gender = input("Enter new gender (male/female): ").strip().lower()
                if new_gender in ['male', 'female']:
                    update_user_gender(user_id, new_gender)
                else:
                    print("❌ Invalid gender.")

if __name__ == "__main__":
    main() 