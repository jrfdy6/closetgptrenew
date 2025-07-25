import firebase_admin
from firebase_admin import credentials, firestore
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_wardrobe():
    try:
        # Initialize Firebase Admin
        cred = credentials.Certificate("service-account-key.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        # Get reference to wardrobe collection
        wardrobe_ref = db.collection('wardrobe')
        
        # Get all documents
        docs = wardrobe_ref.stream()
        
        # Delete each document
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
            logger.info(f"Deleted item: {doc.id}")
        
        logger.info(f"Successfully deleted {deleted_count} items from wardrobe")
        
    except Exception as e:
        logger.error(f"Error clearing wardrobe: {str(e)}")
        raise

if __name__ == "__main__":
    clear_wardrobe() 