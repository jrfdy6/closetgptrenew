"""
Backfill waistband type for existing wardrobe items.

This script analyzes existing pants/shorts in the wardrobe and adds waistband type
metadata based on item names and existing attributes.

Usage:
    python backfill_waistband_type.py --dry-run  # Preview changes without applying
    python backfill_waistband_type.py --live     # Apply changes to production
"""

import os
import sys
import logging
import argparse
from typing import Dict, Any, List, Optional
from google.cloud import firestore
from datetime import datetime

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_firebase():
    """Initialize Firestore using Google Cloud SDK credentials"""
    try:
        # Use Google Cloud SDK default credentials (matches backfill_metadata_no_ai.py)
        # This uses GOOGLE_APPLICATION_CREDENTIALS env var or default credentials
        db = firestore.Client()
        logger.info("✅ Firestore initialized successfully")
        return db
    except Exception as e:
        logger.error(f"❌ Firestore initialization failed: {e}")
        logger.error("   Make sure GOOGLE_APPLICATION_CREDENTIALS is set or gcloud auth is configured")
        sys.exit(1)


def infer_waistband_type(item: Dict[str, Any]) -> Optional[str]:
    """
    Infer waistband type from item name, type, and metadata.
    
    Returns:
        waistband type: "belt_loops", "elastic", "drawstring", "elastic_drawstring", "button_zip", "none"
    """
    item_name = item.get('name', '').lower()
    item_type = item.get('type', '').lower()
    
    # Only analyze bottoms (pants, shorts, skirts)
    bottom_types = ['pants', 'shorts', 'pant', 'short', 'trouser', 'jogger', 'sweatpants', 'jeans']
    
    # Exclude tops that might have "short" in name (like "short sleeve")
    top_types = ['shirt', 'blouse', 'top', 'sweater', 'jacket', 'coat', 'dress', 'vest']
    
    is_bottom = False
    is_top = item_type in top_types
    
    # Don't classify tops as bottoms
    if is_top:
        return 'none'
    
    if item_type in bottom_types:
        is_bottom = True
    elif any(bottom_type in item_name for bottom_type in bottom_types):
        is_bottom = True
    
    # Non-bottoms get "none"
    if not is_bottom:
        return 'none'
    
    # Elastic waistband indicators
    elastic_keywords = [
        'sweatpants', 'sweat pants', 'sweatshort', 'sweat short', 'jogger', 'joggers', 'athletic pants',
        'track pants', 'lounge pants', 'elastic waist', 'elasticized'
    ]
    
    # Drawstring indicators
    drawstring_keywords = [
        'drawstring', 'draw string', 'tie waist'
    ]
    
    # Belt loops indicators (formal/structured pants)
    belt_loop_keywords = [
        'dress pants', 'slacks', 'chinos', 'chino', 'khaki', 'trousers', 'trouser',
        'jean', 'denim', 'cargo', 'work pants', 'formal pants',
        'dress shorts', 'dockers', 'pleated'
    ]
    
    # Priority 1: Check occasion tags first (most reliable for athletic/loungewear)
    occasion_tags = item.get('occasion', [])
    occasion_tags_lower = [tag.lower() for tag in occasion_tags] if occasion_tags else []
    
    if any(occ in occasion_tags_lower for occ in ['athletic', 'gym', 'sports', 'workout']):
        return 'elastic_drawstring'
    if any(occ in occasion_tags_lower for occ in ['loungewear', 'lounge', 'sleep', 'relaxed']):
        return 'elastic_drawstring'
    
    # Priority 2: Check for elastic + drawstring keywords in name
    has_elastic = any(keyword in item_name for keyword in elastic_keywords)
    has_drawstring = any(keyword in item_name for keyword in drawstring_keywords)
    
    if has_elastic and has_drawstring:
        return 'elastic_drawstring'
    elif has_elastic:
        return 'elastic'
    elif has_drawstring:
        return 'drawstring'
    
    # Priority 3: Check for belt loop keywords in name OR type
    if any(keyword in item_name for keyword in belt_loop_keywords):
        return 'belt_loops'
    if item_type in ['jeans', 'jean', 'denim', 'chinos', 'khakis', 'trousers']:
        return 'belt_loops'
    
    # Priority 4: Check metadata formality level
    metadata = item.get('metadata', {})
    visual_attrs = metadata.get('visualAttributes', {}) if isinstance(metadata, dict) else {}
    formal_level = visual_attrs.get('formalLevel', '') if isinstance(visual_attrs, dict) else ''
    
    if formal_level in ['Formal', 'Semi-Formal', 'Business Casual']:
        return 'belt_loops'
    elif formal_level == 'Casual':
        # Default casual pants to belt loops (like casual jeans)
        return 'belt_loops'
    
    # Default for ambiguous bottoms - use button_zip as neutral default
    return 'button_zip'


def backfill_waistband_types(dry_run: bool = True) -> Dict[str, Any]:
    """
    Backfill waistband types for all wardrobe items.
    
    Args:
        dry_run: If True, only preview changes without applying
    
    Returns:
        Statistics about the backfill operation
    """
    db = initialize_firebase()
    
    stats = {
        'total_items': 0,
        'items_updated': 0,
        'items_skipped': 0,
        'waistband_types': {},
        'errors': []
    }
    
    try:
        logger.info(f"Starting waistband type backfill (dry_run={dry_run})")
        
        # Query the main wardrobe collection (same as backfill_metadata_no_ai.py)
        wardrobe_ref = db.collection('wardrobe')
        items = wardrobe_ref.stream()
        
        for item_doc in items:
            stats['total_items'] += 1
            item_data = item_doc.to_dict()
            item_id = item_doc.id
            item_type = item_data.get('type', 'unknown')
            
            # Skip items with unknown type (unanalyzed items)
            if item_type == 'unknown':
                logger.debug(f"Skipping unanalyzed item {item_id} with type: unknown")
                stats['items_skipped'] += 1
                continue
            
            # Check if waistband type already exists
            metadata = item_data.get('metadata', {})
            if not isinstance(metadata, dict):
                metadata = {}
            
            visual_attrs = metadata.get('visualAttributes', {})
            if not isinstance(visual_attrs, dict):
                visual_attrs = {}
            
            existing_waistband = visual_attrs.get('waistbandType')
            
            # Skip if already has a waistband type that's NOT "none"
            # (Re-analyze items marked as "none" to catch pants/shorts)
            if existing_waistband and existing_waistband != 'none':
                logger.debug(f"Item {item_id} already has waistband type: {existing_waistband}")
                stats['items_skipped'] += 1
                continue
            
            # Infer waistband type
            waistband_type = infer_waistband_type(item_data)
            
            if waistband_type:
                # Count waistband types
                stats['waistband_types'][waistband_type] = stats['waistband_types'].get(waistband_type, 0) + 1
                
                item_name = item_data.get('name', 'Unknown')
                logger.info(f"  Item: {item_name} → waistband type: {waistband_type}")
                
                if not dry_run:
                    # Update the item
                    visual_attrs['waistbandType'] = waistband_type
                    metadata['visualAttributes'] = visual_attrs
                    
                    wardrobe_ref.document(item_id).update({
                        'metadata': metadata,
                        'updatedAt': firestore.SERVER_TIMESTAMP
                    })
                    
                    logger.info(f"    ✅ Updated item {item_id}")
                else:
                    logger.info(f"    [DRY RUN] Would update item {item_id}")
                
                stats['items_updated'] += 1
        
        logger.info("Backfill completed successfully")
        logger.info(f"Total items: {stats['total_items']}")
        logger.info(f"Items updated: {stats['items_updated']}")
        logger.info(f"Items skipped: {stats['items_skipped']}")
        logger.info(f"Waistband types distribution: {stats['waistband_types']}")
        
    except Exception as e:
        logger.error(f"Error during backfill: {str(e)}")
        stats['errors'].append(str(e))
        raise
    
    return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Backfill waistband types for wardrobe items')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without applying them')
    parser.add_argument('--live', action='store_true',
                       help='Apply changes to production database')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.live:
        logger.error("Please specify either --dry-run or --live")
        sys.exit(1)
    
    if args.live:
        logger.warning("⚠️  LIVE MODE: Changes will be applied to production database!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Cancelled by user")
            sys.exit(0)
    
    dry_run = args.dry_run or not args.live
    
    try:
        stats = backfill_waistband_types(dry_run=dry_run)
        
        # Save stats to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stats_file = f'backfill_waistband_stats_{timestamp}.json'
        
        import json
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Stats saved to {stats_file}")
        
    except Exception as e:
        logger.error(f"Backfill failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

