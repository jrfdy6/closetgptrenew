#!/usr/bin/env python3

import os
import firebase_admin
from firebase_admin import auth as firebase_auth
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize Firebase
from src.config.firebase import initialize_firebase
initialize_firebase()

def test_firebase_auth():
    """Test Firebase authentication with a simple token."""
    try:
        print("Testing Firebase authentication...")
        
        # Test with a simple invalid token to see if Firebase responds
        test_token = "invalid_token_for_testing"
        
        start_time = time.time()
        try:
            # This should fail quickly if Firebase is working
            firebase_auth.verify_id_token(test_token)
            print("ERROR: Invalid token was accepted!")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"Firebase responded in {elapsed:.2f} seconds")
            print(f"Error (expected): {e}")
            
            if "Invalid ID token" in str(e):
                print("✅ Firebase authentication is working correctly")
                return True
            else:
                print(f"❌ Unexpected error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Firebase test failed: {e}")
        return False

if __name__ == "__main__":
    test_firebase_auth()
