import firebase_admin
from firebase_admin import credentials, firestore
import json
import logging
from datetime import datetime
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase with credentials."""
    try:
        cred = credentials.Certificate("service-account-key.json")
        firebase_admin.initialize_app(cred)
        logger.info("Firebase initialized successfully")
        return firestore.client()
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        raise

def create_test_item():
    """Create a test clothing item with all possible metadata."""
    return {
        "id": str(uuid.uuid4()),
        "name": "Test Item",
        "type": "shirt",
        "subType": "t-shirt",
        "color": "blue",
        "colorName": "navy blue",
        "season": ["spring", "summer"],
        "imageUrl": "https://example.com/test.jpg",
        "tags": ["casual", "basic"],
        "style": ["Casual", "Basic"],
        "userId": "test_user",
        "dominantColors": [
            {
                "name": "navy blue",
                "hex": "#000080",
                "rgb": [0, 0, 128]
            }
        ],
        "matchingColors": [
            {
                "name": "white",
                "hex": "#FFFFFF",
                "rgb": [255, 255, 255]
            }
        ],
        "occasion": ["Casual", "Everyday"],
        "brand": "Test Brand",
        "createdAt": int(datetime.now().timestamp()),
        "updatedAt": int(datetime.now().timestamp()),
        "metadata": {
            "basicMetadata": {
                "width": 800,
                "height": 600,
                "orientation": "portrait",
                "dateTaken": "2024-03-20T10:00:00Z",
                "deviceModel": "iPhone 14",
                "gps": {
                    "latitude": 37.7749,
                    "longitude": -122.4194
                },
                "flashUsed": False
            },
            "visualAttributes": {
                "material": "cotton",
                "pattern": "solid",
                "textureStyle": "smooth",
                "fabricWeight": "light",
                "fit": "regular",
                "silhouette": "relaxed",
                "length": "regular",
                "genderTarget": "unisex",
                "sleeveLength": "short",
                "hangerPresent": False,
                "backgroundRemoved": True,
                "wearLayer": "base",
                "formalLevel": "casual"
            },
            "itemMetadata": {
                "priceEstimate": "$20-30",
                "careInstructions": "Machine wash cold, tumble dry low",
                "tags": ["cotton", "basic", "everyday"]
            }
        }
    }

def store_test_item(db, test_item):
    """Store the test item in Firestore."""
    try:
        # Reference to the wardrobe collection
        wardrobe_ref = db.collection('wardrobe')
        
        # Add the test item
        doc_ref = wardrobe_ref.document(test_item['id'])
        doc_ref.set(test_item)
        
        logger.info(f"Test item stored successfully with ID: {test_item['id']}")
        return doc_ref
    except Exception as e:
        logger.error(f"Error storing test item: {str(e)}")
        raise

def verify_stored_item(db, item_id):
    """Verify the stored item in Firestore."""
    try:
        # Get the document
        doc_ref = db.collection('wardrobe').document(item_id)
        doc = doc_ref.get()
        
        if doc.exists:
            stored_data = doc.to_dict()
            logger.info("Stored item retrieved successfully")
            logger.info("Stored data:")
            logger.info(json.dumps(stored_data, indent=2))
            
            # Verify all fields are present
            required_fields = ["id", "name", "type", "color", "season", "imageUrl", "userId", "createdAt", "updatedAt"]
            missing_fields = [field for field in required_fields if field not in stored_data]
            
            if missing_fields:
                logger.error(f"Missing required fields: {missing_fields}")
                return False
            
            # Verify metadata structure
            if "metadata" in stored_data:
                metadata = stored_data["metadata"]
                metadata_sections = ["basicMetadata", "visualAttributes", "itemMetadata"]
                missing_sections = [section for section in metadata_sections if section not in metadata]
                
                if missing_sections:
                    logger.error(f"Missing metadata sections: {missing_sections}")
                    return False
            
            return True
        else:
            logger.error("Document does not exist")
            return False
    except Exception as e:
        logger.error(f"Error verifying stored item: {str(e)}")
        return False

def main():
    """Main function to run the test."""
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Create test item
        test_item = create_test_item()
        logger.info("Test item created")
        
        # Store test item
        doc_ref = store_test_item(db, test_item)
        
        # Verify stored item
        verification_result = verify_stored_item(db, test_item['id'])
        
        if verification_result:
            logger.info("Test completed successfully")
        else:
            logger.error("Test failed")
            
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    main() 