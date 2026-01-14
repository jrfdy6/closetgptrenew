#!/usr/bin/env python3
"""
One-time script to initialize wardrobeItemCount for existing users.
This counts their actual wardrobe items and sets the cached count.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.firebase import db, firebase_initialized
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_wardrobe_counts():
    """Initialize wardrobeItemCount for all users who don't have it."""
    
    if not firebase_initialized:
        logger.error("Firebase not initialized!")
        return
    
    logger.info("🚀 Starting wardrobeItemCount initialization...")
    
    # Get all users
    users_ref = db.collection('users')
    users = users_ref.stream()
    
    updated_count = 0
    skipped_count = 0
    
    for user_doc in users:
        user_id = user_doc.id
        user_data = user_doc.to_dict()
        
        # Skip if already has the count field
        if 'wardrobeItemCount' in user_data and user_data['wardrobeItemCount'] is not None:
            logger.info(f"⏭️  User {user_id} already has wardrobeItemCount: {user_data['wardrobeItemCount']}")
            skipped_count += 1
            continue
        
        # Count their wardrobe items
        wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
        items = list(wardrobe_ref.stream())
        item_count = len(items)
        
        # Update the user profile with the count
        user_ref = db.collection('users').document(user_id)
        user_ref.update({
            'wardrobeItemCount': item_count
        })
        
        logger.info(f"✅ User {user_id}: Set wardrobeItemCount to {item_count}")
        updated_count += 1
    
    logger.info(f"\n🎉 Done! Updated {updated_count} users, skipped {skipped_count} users")


if __name__ == "__main__":
    initialize_wardrobe_counts()
