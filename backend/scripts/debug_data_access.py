#!/usr/bin/env python3
"""
Debug script to check Firebase authentication and data access.
This will help identify why wardrobe items and users aren't showing up.
"""

import firebase_admin
from firebase_admin import firestore, initialize_app, credentials
import json
import os

def debug_firebase_connection():
    """Debug Firebase connection and authentication."""
    print("🔍 Firebase Connection Debug")
    print("=" * 50)
    
    # Check service account file
    service_account_path = "service-account-key.json"
    if os.path.exists(service_account_path):
        print(f"✅ Service account file found: {service_account_path}")
        try:
            with open(service_account_path, 'r') as f:
                service_account = json.load(f)
                project_id = service_account.get('project_id')
                client_email = service_account.get('client_email')
                print(f"   Project ID: {project_id}")
                print(f"   Client Email: {client_email}")
        except Exception as e:
            print(f"❌ Error reading service account: {e}")
    else:
        print(f"❌ Service account file not found: {service_account_path}")
        return
    
    # Check Firebase initialization
    try:
        if not firebase_admin._apps:
            initialize_app()
            print("✅ Firebase initialized successfully")
        else:
            print("✅ Firebase already initialized")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return
    
    # Test Firestore connection
    try:
        db = firestore.client()
        print("✅ Firestore client created successfully")
    except Exception as e:
        print(f"❌ Firestore client creation failed: {e}")
        return
    
    # Test basic operations
    print(f"\n🔍 Testing Basic Operations:")
    print("-" * 30)
    
    collections = ['wardrobe', 'outfits', 'users', 'analytics_events']
    
    for collection in collections:
        try:
            # Try to get a single document
            docs = list(db.collection(collection).limit(1).stream())
            count = len(docs)
            print(f"✅ {collection}: {count} document(s) accessible")
            
            if count > 0:
                # Show sample document structure
                doc_data = docs[0].to_dict()
                print(f"   Sample keys: {list(doc_data.keys())[:5]}...")
                
                # Check for userId field if present
                if 'userId' in doc_data:
                    print(f"   User ID: {doc_data['userId']}")
                
        except Exception as e:
            print(f"❌ {collection}: Error - {e}")
    
    # Check for authentication issues
    print(f"\n🔐 Authentication Debug:")
    print("-" * 30)
    
    try:
        # Try to write a test document
        test_ref = db.collection('_debug_test').document('test')
        test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP, 'test': True})
        print("✅ Write permission: OK")
        
        # Try to read it back
        test_doc = test_ref.get()
        if test_doc.exists:
            print("✅ Read permission: OK")
            # Clean up
            test_ref.delete()
            print("✅ Delete permission: OK")
        else:
            print("⚠️  Read permission: Test document not found")
            
    except Exception as e:
        print(f"❌ Permission test failed: {e}")
    
    # Check for different project configurations
    print(f"\n🌐 Project Configuration Check:")
    print("-" * 40)
    
    # Check if there are multiple service account files
    possible_keys = [
        "service-account-key.json",
        "../service-account-key.json",
        "frontend/serviceAccountKey.json",
        "frontend/scripts/service-account-key.json"
    ]
    
    for key_path in possible_keys:
        if os.path.exists(key_path):
            try:
                with open(key_path, 'r') as f:
                    key_data = json.load(f)
                    key_project = key_data.get('project_id')
                    print(f"✅ Found key: {key_path} -> Project: {key_project}")
            except:
                print(f"⚠️  Found key but can't read: {key_path}")
    
    # Check environment variables
    print(f"\n🔧 Environment Variables:")
    print("-" * 30)
    
    env_vars = [
        'GOOGLE_APPLICATION_CREDENTIALS',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_SERVICE_ACCOUNT_KEY'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"ℹ️  {var}: Not set")

def check_alternative_connections():
    """Check if data might be in a different project."""
    print(f"\n🔄 Alternative Connection Check:")
    print("=" * 50)
    
    # List all possible service account files
    service_account_files = []
    for root, dirs, files in os.walk('..'):
        for file in files:
            if 'service' in file.lower() and file.endswith('.json'):
                service_account_files.append(os.path.join(root, file))
    
    if service_account_files:
        print(f"Found {len(service_account_files)} potential service account files:")
        for file_path in service_account_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    project_id = data.get('project_id', 'unknown')
                    print(f"   {file_path} -> Project: {project_id}")
            except:
                print(f"   {file_path} -> (unreadable)")
    else:
        print("No additional service account files found")

if __name__ == "__main__":
    debug_firebase_connection()
    check_alternative_connections()
    
    print(f"\n💡 Troubleshooting Tips:")
    print("=" * 50)
    print("1. Check if you're connected to the right Firebase project")
    print("2. Verify the service account has proper permissions")
    print("3. Check if data exists in a different environment (dev vs prod)")
    print("4. Look for environment-specific configuration files")
    print("5. Check if there are multiple Firebase projects for this app") 