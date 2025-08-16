from firebase_admin import firestore
from src.config.firebase import db
from src.types.style_discovery import StyleDiscoveryProfile
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds

logger = logging.getLogger(__name__)

async def create_user_profile(user_id: str, name: str, email: str) -> bool:
    """Create a new user profile in Firestore."""
    try:
        logger.info(f"Creating user profile for user {user_id}")
        
        # Create user profile document
        user_profile = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp(),
            "preferences": {
                "style": [],
                "colors": [],
                "occasions": []
            },
            "measurements": {
                "height": None,
                "weight": None,
                "bodyType": None
            },
            "stylePreferences": [],
            "bodyType": None
        }
        
        # Save to Firestore
        doc_ref = db.collection('users').document(user_id)
        doc_ref.set(user_profile)
        
        # Create default style discovery profile
        await create_default_style_profile(user_id)
        
        logger.info(f"Successfully created user profile for {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}", exc_info=True)
        return False

async def get_style_discovery_profile(user_id: str) -> Optional[StyleDiscoveryProfile]:
    """Get user's style discovery profile from Firestore."""
    try:
        logger.info(f"Attempting to get style discovery profile for user {user_id}")
        
        # Get document from Firestore
        doc_ref = db.collection('style_discovery_profiles').document(user_id)
        logger.info(f"Querying Firestore document: style_discovery_profiles/{user_id}")
        
        doc = doc_ref.get()
        logger.info(f"Document exists: {doc.exists}")
        
        if not doc.exists:
            logger.warning(f"No style discovery profile found for user {user_id}")
            return None
        
        # Convert Firestore data to StyleDiscoveryProfile
        data = doc.to_dict()
        logger.info(f"Retrieved data from Firestore: {data}")
        
        # Convert timestamps before creating the profile
        if data.get('quiz_result') and data['quiz_result'].get('completed_at'):
            completed_at = data['quiz_result']['completed_at']
            logger.info(f"Quiz result completed_at type: {type(completed_at)}")
            if isinstance(completed_at, DatetimeWithNanoseconds):
                # Keep the DatetimeWithNanoseconds object as is
                data['quiz_result']['completed_at'] = completed_at
            elif isinstance(completed_at, (int, float)):
                data['quiz_result']['completed_at'] = datetime.fromtimestamp(completed_at)
            else:
                logger.warning(f"Unexpected type for completed_at: {type(completed_at)}")
        
        if data.get('style_evolution'):
            for evolution in data['style_evolution']:
                if evolution.get('timestamp'):
                    timestamp = evolution['timestamp']
                    logger.info(f"Style evolution timestamp type: {type(timestamp)}")
                    if isinstance(timestamp, DatetimeWithNanoseconds):
                        # Keep the DatetimeWithNanoseconds object as is
                        evolution['timestamp'] = timestamp
                    elif isinstance(timestamp, (int, float)):
                        evolution['timestamp'] = datetime.fromtimestamp(timestamp)
                    else:
                        logger.warning(f"Unexpected type for timestamp: {type(timestamp)}")
        
        try:
            profile = StyleDiscoveryProfile(**data)
            logger.info(f"Successfully created StyleDiscoveryProfile object")
            return profile
        except Exception as e:
            logger.error(f"Error creating StyleDiscoveryProfile: {str(e)}", exc_info=True)
            return None
    
    except Exception as e:
        logger.error(f"Error getting style discovery profile: {str(e)}", exc_info=True)
        return None

async def save_style_discovery_profile(profile: StyleDiscoveryProfile) -> bool:
    """Save user's style discovery profile to Firestore."""
    try:
        logger.info(f"Attempting to save style discovery profile for user {profile.user_id}")
        
        # Convert datetime objects to timestamps
        data = profile.dict()
        if profile.quiz_result and profile.quiz_result.completed_at:
            if isinstance(profile.quiz_result.completed_at, (datetime, DatetimeWithNanoseconds)):
                data["quiz_result"]["completed_at"] = profile.quiz_result.completed_at.timestamp()
        
        for evolution in data["style_evolution"]:
            if evolution.get("timestamp"):
                if isinstance(evolution["timestamp"], (datetime, DatetimeWithNanoseconds)):
                    evolution["timestamp"] = evolution["timestamp"].timestamp()
        
        # Save to Firestore
        doc_ref = db.collection('style_discovery_profiles').document(profile.user_id)
        logger.info(f"Saving data to Firestore: {data}")
        doc_ref.set(data)
        
        logger.info(f"Successfully saved style discovery profile")
        return True
    
    except Exception as e:
        logger.error(f"Error saving style discovery profile: {str(e)}", exc_info=True)
        return False

async def create_default_style_profile(user_id: str) -> bool:
    """Create a default style profile for a user."""
    try:
        logger.info(f"Creating default style profile for user {user_id}")
        
        default_profile = {
            "user_id": user_id,
            "style_preferences": [],
            "style_evolution": [],
            "quiz_result": None,
            "style_formula": None,
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp()
        }
        
        doc_ref = db.collection('style_discovery_profiles').document(user_id)
        doc_ref.set(default_profile)
        
        logger.info(f"Successfully created default style profile")
        return True
    
    except Exception as e:
        logger.error(f"Error creating default style profile: {str(e)}", exc_info=True)
        return False

async def list_all_style_profiles() -> Dict[str, Any]:
    """List all style profiles in the database."""
    try:
        logger.info("Listing all style profiles")
        
        profiles = {}
        docs = db.collection('style_discovery_profiles').stream()
        
        for doc in docs:
            data = doc.to_dict()
            profiles[doc.id] = data
        
        logger.info(f"Found {len(profiles)} style profiles")
        return profiles
    
    except Exception as e:
        logger.error(f"Error listing style profiles: {str(e)}", exc_info=True)
        return {}

async def delete_style_profile(user_id: str) -> bool:
    """Delete a style profile from the database."""
    try:
        logger.info(f"Deleting style profile for user {user_id}")
        
        doc_ref = db.collection('style_discovery_profiles').document(user_id)
        doc_ref.delete()
        
        logger.info(f"Successfully deleted style profile")
        return True
    
    except Exception as e:
        logger.error(f"Error deleting style profile: {str(e)}", exc_info=True)
        return False 