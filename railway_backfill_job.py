#!/usr/bin/env python3
"""
Railway One-Time Backfill Job
This script runs the production database backfill as a Railway deployment
"""

import os
import sys
import json
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Set up paths
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Initialize Firebase directly
import firebase_admin
from firebase_admin import credentials, firestore

# Load normalization utilities
import importlib.util
norm_spec = importlib.util.spec_from_file_location(
    "semantic_normalization",
    os.path.join(backend_dir, 'src', 'utils', 'semantic_normalization.py')
)
norm_module = importlib.util.module_from_spec(norm_spec)
norm_spec.loader.exec_module(norm_module)
normalize_item_metadata = norm_module.normalize_item_metadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase connection"""
    try:
        if not firebase_admin._apps:
            # Railway provides Firebase credentials via environment variables
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        logger.info("✅ Firebase initialized successfully")
        return db
        
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {e}")
        return None

def get_next_batch(db, cursor: Optional[str] = None, batch_size: int = 500) -> List[Dict[str, Any]]:
    """Get next batch of wardrobe items"""
    try:
        query = db.collection('wardrobe').order_by('id').limit(batch_size)
        
        if cursor:
            cursor_doc = db.collection('wardrobe').document(cursor).get()
            if cursor_doc.exists:
                query = query.start_after(cursor_doc)
        
        docs = query.stream()
        batch = []
        
        for doc in docs:
            item_data = doc.to_dict()
            item_data['doc_id'] = doc.id
            batch.append(item_data)
        
        return batch
        
    except Exception as e:
        logger.error(f"❌ Error fetching batch: {e}")
        return []

def normalize_item_safely(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Safely normalize item metadata"""
    try:
        # Check if already normalized
        if 'normalized' in item:
            return None
        
        # Normalize the item
        normalized = normalize_item_metadata(item)
        
        # Create normalized fields structure
        normalized_fields = {
            'style': normalized.get('style', []),
            'occasion': normalized.get('occasion', []),
            'mood': normalized.get('mood', []),
            'season': normalized.get('season', []),
            'normalized_at': datetime.utcnow().isoformat(),
            'normalized_version': '1.0'
        }
        
        return normalized_fields
        
    except Exception as e:
        logger.error(f"❌ Error normalizing item {item.get('id', 'unknown')}: {e}")
        return None

def update_item(db, doc_id: str, normalized_fields: Dict[str, Any], dry_run: bool = False) -> bool:
    """Update item with normalized fields"""
    try:
        if dry_run:
            logger.info(f"🔍 DRY RUN: Would update {doc_id}")
            return True
        
        # Update the document with normalized fields
        db.collection('wardrobe').document(doc_id).update({
            'normalized': normalized_fields
        })
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating item {doc_id}: {e}")
        return False

def run_backfill(dry_run: bool = True):
    """Run the complete backfill process"""
    mode = "DRY RUN" if dry_run else "PRODUCTION"
    logger.info(f"🚀 Starting wardrobe backfill [{mode}]")
    
    # Initialize Firebase
    db = initialize_firebase()
    if not db:
        logger.error("❌ Cannot proceed without Firebase connection")
        return False
    
    stats = {
        'total_processed': 0,
        'total_updated': 0,
        'total_skipped': 0,
        'total_errors': 0,
        'start_time': datetime.utcnow()
    }
    
    cursor = None
    batch_number = 0
    batch_size = 500
    
    try:
        while True:
            batch_number += 1
            logger.info(f"\n📦 Processing batch {batch_number}...")
            
            # Get next batch
            batch = get_next_batch(db, cursor, batch_size)
            
            if not batch:
                logger.info("✅ No more items to process")
                break
            
            # Process batch
            batch_stats = {
                'processed': 0,
                'updated': 0,
                'skipped': 0,
                'errors': 0
            }
            
            for item in batch:
                try:
                    batch_stats['processed'] += 1
                    stats['total_processed'] += 1
                    
                    # Normalize the item
                    normalized_fields = normalize_item_safely(item)
                    
                    if normalized_fields is None:
                        batch_stats['skipped'] += 1
                        stats['total_skipped'] += 1
                        continue
                    
                    # Update the item
                    doc_id = item.get('doc_id')
                    if doc_id and update_item(db, doc_id, normalized_fields, dry_run):
                        batch_stats['updated'] += 1
                        stats['total_updated'] += 1
                    else:
                        batch_stats['errors'] += 1
                        stats['total_errors'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error processing item: {e}")
                    batch_stats['errors'] += 1
                    stats['total_errors'] += 1
            
            # Log batch results
            logger.info(f"   Batch {batch_number}: "
                       f"{batch_stats['processed']} processed, "
                       f"{batch_stats['updated']} updated, "
                       f"{batch_stats['skipped']} skipped, "
                       f"{batch_stats['errors']} errors")
            
            # Update cursor
            if batch:
                cursor = batch[-1].get('doc_id')
            
            # Log progress every 5 batches
            if batch_number % 5 == 0:
                logger.info(f"\n📊 Progress: {stats['total_processed']} items processed so far")
            
            # Small delay to avoid overwhelming the database
            if not dry_run:
                time.sleep(0.2)
            
    except Exception as e:
        logger.error(f"❌ Backfill failed: {e}", exc_info=True)
        return False
    finally:
        # Log final stats
        stats['end_time'] = datetime.utcnow()
        duration = stats['end_time'] - stats['start_time']
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 BACKFILL COMPLETE - FINAL STATISTICS")
        logger.info("=" * 70)
        logger.info(f"⏱️  Duration: {duration}")
        logger.info(f"📦 Total processed: {stats['total_processed']}")
        logger.info(f"✅ Total updated: {stats['total_updated']}")
        logger.info(f"⏭️  Total skipped: {stats['total_skipped']}")
        logger.info(f"❌ Total errors: {stats['total_errors']}")
        
        if stats['total_processed'] > 0:
            success_rate = (stats['total_updated'] / stats['total_processed']) * 100
            logger.info(f"📈 Success rate: {success_rate:.1f}%")
        
        logger.info("=" * 70)
        
        # Save stats to file
        stats_file = f"backfill_stats_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        logger.info(f"💾 Stats saved to {stats_file}")
    
    return True

def main():
    """Main function - Railway will call this"""
    logger.info("🎯 Railway Backfill Job Starting...")
    
    # Check if this is a dry run or production run
    dry_run = os.environ.get('BACKFILL_DRY_RUN', 'true').lower() == 'true'
    
    if dry_run:
        logger.info("🔍 Running in DRY RUN mode (no database changes)")
    else:
        logger.info("⚠️  Running in PRODUCTION mode (will modify database)")
    
    # Run the backfill
    success = run_backfill(dry_run=dry_run)
    
    if success:
        logger.info("✅ Backfill job completed successfully!")
        return 0
    else:
        logger.error("❌ Backfill job failed!")
        return 1

if __name__ == "__main__":
    exit(main())
