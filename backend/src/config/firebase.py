import os
import logging
from firebase_admin import credentials, initialize_app, firestore
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Global variables to track Firebase state
firebase_initialized = False
db: Optional[firestore.Client] = None

def initialize_firebase():
    """Initialize Firebase with environment variables."""
    global firebase_initialized, db
    
    try:
        # Check if all required environment variables are present
        required_vars = ['FIREBASE_PROJECT_ID', 'FIREBASE_PRIVATE_KEY', 'FIREBASE_CLIENT_EMAIL']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            logger.warning(f"Missing Firebase environment variables: {missing_vars}")
            logger.warning("Firebase will not be initialized")
            
            # Create a mock Firebase client for basic operations
            class MockFirestoreClient:
                def collection(self, name):
                    return MockCollection()
                    
            class MockCollection:
                def document(self, doc_id):
                    return MockDocument()
                def where(self, field, op, value):
                    return MockQuery()
                def stream(self):
                    return []
                def limit(self, limit):
                    return self
                def offset(self, offset):
                    return self
                def order_by(self, field, direction=None):
                    return self
                    
            class MockDocument:
                def get(self):
                    return MockDocumentSnapshot()
                def set(self, data):
                    pass
                def update(self, data):
                    pass
                def delete(self):
                    pass
                    
            class MockDocumentSnapshot:
                def exists(self):
                    return False
                def to_dict(self):
                    return {}
                    
            class MockQuery:
                def stream(self):
                    return []
                def limit(self, limit):
                    return self
                def offset(self, offset):
                    return self
                def order_by(self, field, direction=None):
                    return self
                    
            db = MockFirestoreClient()
            firebase_initialized = True
            logger.info("Mock Firebase client initialized for basic operations")
            return db
            
        firebase_creds = {
            "type": "service_account",
            "project_id": os.environ["FIREBASE_PROJECT_ID"],
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID") or os.environ.get("private_key_id", ""),
            "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
            "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
            "client_id": os.environ.get("FIREBASE_CLIENT_ID", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL", "")
        }
        
        cred = credentials.Certificate(firebase_creds)
        initialize_app(cred)
        
        db = firestore.client()
        firebase_initialized = True
        logger.info("Firebase initialized successfully")
        return db
        
    except Exception as e:
        logger.error(f"Error initializing Firebase: {e}")
        firebase_initialized = False
        return None

# Initialize Firebase when module is imported
db = initialize_firebase() 