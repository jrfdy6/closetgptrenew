import os
import firebase_admin
from firebase_admin import credentials, storage, firestore

# Initialize Firebase
firebase_initialized = False
db = None

try:
    # Prevent re-initialization if already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.environ["FIREBASE_PROJECT_ID"],
            "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
            "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
            "client_id": os.environ["FIREBASE_CLIENT_ID"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
        })

        firebase_admin.initialize_app(cred, {
            "projectId": os.environ["FIREBASE_PROJECT_ID"],
            "storageBucket": f"{os.environ['FIREBASE_PROJECT_ID']}.firebasestorage.app"
        })

    # Initialize Firestore
    db = firestore.client()
    firebase_initialized = True
    
except Exception as e:
    print(f"Firebase initialization failed: {e}")
    firebase_initialized = False
    db = None

# This makes sure all routes that call storage.bucket() get the correct bucket 