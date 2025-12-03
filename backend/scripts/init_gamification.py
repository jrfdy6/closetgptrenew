"""
One-time script to initialize gamification fields for existing users
Run this after deploying the gamification system
"""

import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.firebase import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_gamification_fields():
    """Add gamification fields to existing users who don't have them"""
    
    try:
        users = db.collection('users').stream()
        updated_count = 0
        skipped_count = 0
        
        for user_doc in users:
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            
            # Check what fields need to be added
            updates = {}
            
            if 'xp' not in user_data:
                updates['xp'] = 0
            if 'level' not in user_data:
                updates['level'] = 1
            if 'ai_fit_score' not in user_data:
                updates['ai_fit_score'] = 0.0
            if 'badges' not in user_data:
                updates['badges'] = []
            if 'current_challenges' not in user_data:
                updates['current_challenges'] = {}
            if 'spending_ranges' not in user_data:
                updates['spending_ranges'] = {
                    "annual_total": "unknown",
                    "shoes": "unknown",
                    "jackets": "unknown",
                    "pants": "unknown",
                    "tops": "unknown",
                    "dresses": "unknown",
                    "activewear": "unknown",
                    "accessories": "unknown"
                }
            
            if updates:
                user_doc.reference.update(updates)
                updated_count += 1
                logger.info(f"✅ Updated user {user_id} with fields: {list(updates.keys())}")
            else:
                skipped_count += 1
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ GAMIFICATION INITIALIZATION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Users updated: {updated_count}")
        logger.info(f"Users skipped (already had fields): {skipped_count}")
        logger.info(f"Total users processed: {updated_count + skipped_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing gamification: {e}", exc_info=True)
        return False


def init_wardrobe_cpw_fields():
    """Add cpw and target_wears fields to existing wardrobe items"""
    
    try:
        items = db.collection('wardrobe').stream()
        updated_count = 0
        
        for item_doc in items:
            item_data = item_doc.to_dict()
            item_id = item_doc.id
            
            updates = {}
            
            if 'cpw' not in item_data:
                updates['cpw'] = None  # Will be calculated on first outfit log
            if 'target_wears' not in item_data:
                updates['target_wears'] = 30
            
            if updates:
                item_doc.reference.update(updates)
                updated_count += 1
                
                if updated_count % 100 == 0:
                    logger.info(f"Processed {updated_count} items...")
        
        logger.info(f"✅ Updated {updated_count} wardrobe items with CPW fields")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating wardrobe items: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logger.info("🚀 Starting gamification initialization...\n")
    
    # Step 1: Initialize user gamification fields
    logger.info("Step 1: Initializing user gamification fields...")
    user_success = init_gamification_fields()
    
    # Step 2: Initialize wardrobe CPW fields
    logger.info("\nStep 2: Initializing wardrobe CPW fields...")
    wardrobe_success = init_wardrobe_cpw_fields()
    
    # Summary
    logger.info(f"\n{'='*60}")
    if user_success and wardrobe_success:
        logger.info("✅ ALL INITIALIZATION COMPLETE!")
        logger.info("Your gamification system is ready to use.")
    else:
        logger.error("❌ Some initialization steps failed. Check logs above.")
    logger.info(f"{'='*60}\n")

