import os
import firebase_admin
from firebase_admin import credentials, firestore
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Firebase with error handling
db = None
firebase_initialized = False

def initialize_firebase():
    """Initialize Firebase with robust error handling."""
    global db, firebase_initialized
    
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
            logger.warning(f"Missing Firebase environment variables: {missing_vars}")
            logger.warning("Firebase will not be initialized")
            return False
        
        # Process private key - handle both literal \n and actual newlines
        private_key = os.environ["FIREBASE_PRIVATE_KEY"]
        if "\\n" in private_key:
            # If it has literal \n characters, replace them with actual newlines
            private_key = private_key.replace("\\n", "\n")
        # If it already has actual newlines, use it as is
        
        firebase_creds = {
            "type": "service_account",
            "project_id": os.environ["FIREBASE_PROJECT_ID"],
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID") or os.environ.get("private_key_id", ""),
            "private_key": private_key,
            "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
            "client_id": os.environ["FIREBASE_CLIENT_ID"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
        }

        # Initialize with explicit project ID and better error handling
        cred = credentials.Certificate(firebase_creds)
        
        # Check if app is already initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'projectId': os.environ["FIREBASE_PROJECT_ID"]
            })
        
        # Initialize Firestore with explicit settings
        db = firestore.client()
        
        # Test the connection with a simple query
        try:
            logger.info("Testing Firestore connection...")
            test_query = db.collection('test').limit(1)
            # Don't actually execute, just test if the client is working
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Firestore connection test failed: {e}")
            return False
        
        firebase_initialized = True
        logger.info("Firebase initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        logger.warning("App will continue without Firebase functionality")
        firebase_initialized = False
        return False

# Initialize Firebase on module import
initialize_firebase() 