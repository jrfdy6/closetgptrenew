import firebase_admin
from firebase_admin import credentials, firestore
import logging
import sys
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase with credentials."""
    try:
        # Get the absolute path to the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cred_path = os.path.join(backend_dir, 'service-account-key.json')
        
        # Initialize Firebase
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase initialized successfully")
        return firestore.client()
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        sys.exit(1)

def update_wardrobe_items():
    """Update wardrobe items to add missing id fields."""
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get all wardrobe items
        wardrobe_ref = db.collection('wardrobe')
        docs = wardrobe_ref.stream()
        
        # Counter for statistics
        total_items = 0
        updated_items = 0
        skipped_items = 0
        
        # Process each document
        for doc in docs:
            total_items += 1
            doc_id = doc.id
            item_data = doc.to_dict()
            
            # Check if id field exists and matches document ID
            if 'id' not in item_data or item_data['id'] != doc_id:
                try:
                    # Update the document with the correct id
                    wardrobe_ref.document(doc_id).update({
                        'id': doc_id
                    })
                    updated_items += 1
                    logger.info(f"Updated item {doc_id}")
                except Exception as e:
                    logger.error(f"Error updating item {doc_id}: {str(e)}")
                    skipped_items += 1
            else:
                skipped_items += 1
                logger.info(f"Skipped item {doc_id} (already has correct id)")
        
        # Log summary
        logger.info("\nUpdate Summary:")
        logger.info(f"Total items processed: {total_items}")
        logger.info(f"Items updated: {updated_items}")
        logger.info(f"Items skipped: {skipped_items}")
        
    except Exception as e:
        logger.error(f"Error in update_wardrobe_items: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Starting wardrobe items update...")
    update_wardrobe_items()
    logger.info("Update completed!") 