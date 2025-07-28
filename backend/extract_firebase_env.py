#!/usr/bin/env python3
"""
Extract Firebase credentials from service account file and format for environment variables
"""

import json
import os

def extract_firebase_env():
    """Extract Firebase credentials from service account file"""
    try:
        # Read the service account file
        with open('service-account-key.json', 'r') as f:
            service_account = json.load(f)
        
        print("🔍 Extracted Firebase credentials:")
        print(f"FIREBASE_PROJECT_ID={service_account['project_id']}")
        print(f"FIREBASE_PRIVATE_KEY_ID={service_account['private_key_id']}")
        print(f"FIREBASE_PRIVATE_KEY={service_account['private_key'].replace(chr(10), '\\n')}")
        print(f"FIREBASE_CLIENT_EMAIL={service_account['client_email']}")
        print(f"FIREBASE_CLIENT_ID={service_account['client_id']}")
        print(f"FIREBASE_CLIENT_X509_CERT_URL={service_account['client_x509_cert_url']}")
        
        print("\n📋 Copy these environment variables to Railway:")
        print("railway variables set FIREBASE_PROJECT_ID=" + service_account['project_id'])
        print("railway variables set FIREBASE_PRIVATE_KEY_ID=" + service_account['private_key_id'])
        print("railway variables set FIREBASE_PRIVATE_KEY=\"" + service_account['private_key'].replace(chr(10), '\\n') + "\"")
        print("railway variables set FIREBASE_CLIENT_EMAIL=" + service_account['client_email'])
        print("railway variables set FIREBASE_CLIENT_ID=" + service_account['client_id'])
        print("railway variables set FIREBASE_CLIENT_X509_CERT_URL=" + service_account['client_x509_cert_url'])
        
        return True
        
    except Exception as e:
        print(f"❌ Error extracting Firebase credentials: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Extracting Firebase credentials from service account file...")
    extract_firebase_env() 