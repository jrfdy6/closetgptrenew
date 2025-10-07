#!/usr/bin/env python3
"""
Simple backfill script that can be triggered via API endpoint
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.firebase import db
from utils.semantic_normalization import normalize_item_metadata
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_backfill(dry_run=True, max_items=None):
    """Run backfill with simple controls"""
    mode = "DRY RUN" if dry_run else "PRODUCTION"
    logger.info(f"🚀 Starting backfill [{mode}]")
    
    if not db:
        logger.error("❌ Firebase not initialized")
        return {"success": False, "error": "Firebase not initialized"}
    
    stats = {
        'processed': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    try:
        # Get all wardrobe items
        query = db.collection('wardrobe')
        if max_items:
            query = query.limit(max_items)
        
        items = query.stream()
        
        for doc in items:
            item = doc.to_dict()
            stats['processed'] += 1
            
            # Skip if already normalized
            if 'normalized' in item:
                stats['skipped'] += 1
                logger.info(f"⏭️  Skipped {doc.id} (already normalized)")
                continue
            
            # Normalize
            try:
                normalized = normalize_item_metadata(item)
                normalized_fields = {
                    'style': normalized.get('style', []),
                    'occasion': normalized.get('occasion', []),
                    'mood': normalized.get('mood', []),
                    'season': normalized.get('season', []),
                    'normalized_at': datetime.utcnow().isoformat(),
                    'normalized_version': '1.0'
                }
                
                if dry_run:
                    logger.info(f"🔍 DRY RUN: Would update {doc.id}")
                    stats['updated'] += 1
                else:
                    db.collection('wardrobe').document(doc.id).update({
                        'normalized': normalized_fields
                    })
                    logger.info(f"✅ Updated {doc.id}")
                    stats['updated'] += 1
                    
            except Exception as e:
                logger.error(f"❌ Error processing {doc.id}: {e}")
                stats['errors'] += 1
        
        logger.info(f"\n{'='*50}")
        logger.info(f"📊 RESULTS:")
        logger.info(f"   Processed: {stats['processed']}")
        logger.info(f"   Updated: {stats['updated']}")
        logger.info(f"   Skipped: {stats['skipped']}")
        logger.info(f"   Errors: {stats['errors']}")
        logger.info(f"{'='*50}\n")
        
        return {"success": True, "stats": stats}
        
    except Exception as e:
        logger.error(f"❌ Backfill failed: {e}")
        return {"success": False, "error": str(e), "stats": stats}

if __name__ == "__main__":
    # Run dry run on first 10 items
    result = run_backfill(dry_run=True, max_items=10)
    print(f"\n✅ Result: {result}")

