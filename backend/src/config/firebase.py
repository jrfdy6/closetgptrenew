import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase with error handling
db = None
firebase_initialized = False

try:
    # Check if required environment variables are present
    required_vars = [
        "FIREBASE_PROJECT_ID",
        "FIREBASE_PRIVATE_KEY", 
        "FIREBASE_CLIENT_EMAIL",
        "FIREBASE_CLIENT_ID",
        "FIREBASE_CLIENT_X509_CERT_URL"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"DEBUG: Missing Firebase environment variables: {missing_vars}")
        print("DEBUG: Firebase will not be initialized")
    else:
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
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        firebase_initialized = True
        print("DEBUG: Firebase initialized successfully")
        
except Exception as e:
    print(f"DEBUG: Firebase initialization failed: {e}")
    print("DEBUG: App will continue without Firebase functionality")
    firebase_initialized = False 