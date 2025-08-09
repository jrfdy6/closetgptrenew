#!/usr/bin/env python3
"""
Script to set up Firebase environment variables for testing
"""

import json
import os
import subprocess
import sys

def load_service_account():
    """Load the service account key file"""
    try:
        with open('service-account-key.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ service-account-key.json not found")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON in service-account-key.json")
        return None

def set_environment_variables(service_account):
    """Set environment variables from service account"""
    env_vars = {
        'FIREBASE_PROJECT_ID': service_account['project_id'],
        'FIREBASE_PRIVATE_KEY_ID': service_account['private_key_id'],
        'FIREBASE_PRIVATE_KEY': service_account['private_key'],
        'FIREBASE_CLIENT_EMAIL': service_account['client_email'],
        'FIREBASE_CLIENT_ID': service_account['client_id'],
        'FIREBASE_CLIENT_X509_CERT_URL': service_account['client_x509_cert_url']
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ Set {key}")
    
    return env_vars

def run_test_with_env():
    """Run the communication test with environment variables set"""
    print("🚀 Running test with Firebase environment variables...")
    
    # Set environment variables
    service_account = load_service_account()
    if not service_account:
        return False
    
    set_environment_variables(service_account)
    
    # Run the test
    try:
        result = subprocess.run([
            sys.executable, 'test_frontend_backend_communication.py'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Setting up Firebase environment for testing...")
    success = run_test_with_env()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
