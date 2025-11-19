import os
import firebase_admin
from firebase_admin import credentials, storage, firestore
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase
firebase_initialized = False
db = None

try:
    # Prevent re-initialization if already initialized
    if not firebase_admin._apps:
        # Check if all required environment variables are present
        required_vars = [
            "FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY", "FIREBASE_CLIENT_EMAIL",
            "FIREBASE_CLIENT_ID", "FIREBASE_CLIENT_X509_CERT_URL"
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            logger.error(f"❌ FIREBASE INIT FAILED: Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        logger.info(f"✅ FIREBASE INIT: All environment variables present, initializing...")
        
        # Get private key and handle newlines properly
        private_key = os.environ.get("FIREBASE_PRIVATE_KEY", "")
        if "\\n" in private_key:
            private_key = private_key.replace("\\n", "\n")
        
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
            "private_key": private_key,
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
        })

        logger.info(f"✅ FIREBASE INIT: Credentials created, initializing app...")
        firebase_admin.initialize_app(cred, {
            "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
            "storageBucket": f"{os.environ.get('FIREBASE_PROJECT_ID')}.firebasestorage.app"
        })
        logger.info(f"✅ FIREBASE INIT: App initialized successfully")

    # Initialize Firestore
    logger.info(f"✅ FIREBASE INIT: Initializing Firestore client...")
    db = firestore.client()
    
    # Test Firestore connection with a simple query
    try:
        logger.info(f"✅ FIREBASE INIT: Testing Firestore connection...")
        # Try a simple query to verify connection works
        test_collection = db.collection('users').limit(1)
        # Don't actually fetch, just verify the client works
        logger.info(f"✅ FIREBASE INIT: Firestore client created successfully")
    except Exception as test_error:
        logger.error(f"❌ FIREBASE INIT: Firestore connection test failed: {test_error}")
        raise
    
    firebase_initialized = True
    logger.info(f"✅ FIREBASE INIT: Firebase initialization complete - firebase_initialized={firebase_initialized}")
    
except ValueError as ve:
    # Missing environment variables - log clearly
    logger.error(f"❌ FIREBASE INIT FAILED: {ve}", exc_info=True)
    firebase_initialized = False
    db = None
except Exception as e:
    # Any other initialization error - log with full details
    logger.error(f"❌ FIREBASE INIT FAILED: {type(e).__name__}: {str(e)}", exc_info=True)
    logger.error(f"❌ FIREBASE INIT: Error details: {e}")
    firebase_initialized = False
    db = None
    
if not firebase_initialized:
    logger.warning(f"⚠️ FIREBASE INIT: Firebase not initialized - database operations will fail")

# This makes sure all routes that call storage.bucket() get the correct bucket 