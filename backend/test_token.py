#!/usr/bin/env python3

import os
import firebase_admin
from firebase_admin import auth as firebase_auth
from dotenv import load_dotenv
import time
import sys

# Load environment variables
load_dotenv()

# Initialize Firebase
from src.config.firebase import initialize_firebase
initialize_firebase()

def test_token_verification(token):
    """Test Firebase token verification."""
    try:
        print(f"Testing token verification for token starting with: {token[:20]}...")
        
        start_time = time.time()
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            elapsed = time.time() - start_time
            print(f"✅ Token verification successful in {elapsed:.2f} seconds")
            print(f"User ID: {decoded_token.get('uid')}")
            print(f"Email: {decoded_token.get('email')}")
            return True
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Token verification failed in {elapsed:.2f} seconds")
            print(f"Error: {e}")
            return False
                
    except Exception as e:
        print(f"❌ Firebase test failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_token.py <token>")
        sys.exit(1)
    
    token = sys.argv[1]
    test_token_verification(token)
