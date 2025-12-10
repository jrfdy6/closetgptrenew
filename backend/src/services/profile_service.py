"""
Profile Service - Handles user profile updates including location/timezone data
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from ..config.firebase import db

logger = logging.getLogger(__name__)


async def update_user_location_data(user_id: str, location_data: Dict[str, Any]) -> bool:
    """
    Update user profile with location and timezone data from weather API.
    
    Args:
        user_id: User ID
        location_data: Dict containing:
            - timezone_offset: Seconds from UTC
            - timezone: IANA timezone string (e.g., "America/New_York")
            - coordinates: {"lat": float, "lon": float}
            - country: Country code
            - city_name: Official city name
            - last_location: Location string used in request
            - last_weather_fetch: ISO timestamp
    
    Returns:
        True if successful, False otherwise
    """
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            logger.warning(f"User {user_id} not found, cannot update location data")
            return False
        
        # Prepare update data
        update_data = {
            'location_data': {
                'timezone_offset': location_data.get('timezone_offset'),
                'timezone': location_data.get('timezone'),
                'coordinates': location_data.get('coordinates'),
                'country': location_data.get('country'),
                'city_name': location_data.get('city_name'),
                'last_location': location_data.get('last_location'),
                'last_weather_fetch': location_data.get('last_weather_fetch'),
                'updated_at': datetime.now().isoformat()
            },
            'updatedAt': int(datetime.now().timestamp() * 1000)
        }
        
        # Update user document (Firestore is synchronous)
        user_ref.update(update_data)
        
        logger.info(f"✅ Updated location data for user {user_id}: timezone={location_data.get('timezone')}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating user location data: {e}", exc_info=True)
        return False

