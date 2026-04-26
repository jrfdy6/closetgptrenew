#!/usr/bin/env python3
"""
Simple script to start the backend with Firebase environment variables
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

def start_backend():
    """Start the backend with environment variables set"""
    print("🔧 Setting up Firebase environment...")
    
    # Set environment variables
    service_account = load_service_account()
    if not service_account:
        return False
    
    set_environment_variables(service_account)
    
    print("🚀 Starting backend on port 8080...")
    os.environ.setdefault("PORT", "8080")
    
    # Start the backend
    try:
        subprocess.run([sys.executable, 'run.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_backend()
