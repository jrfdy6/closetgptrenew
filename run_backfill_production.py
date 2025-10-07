#!/usr/bin/env python3
"""
Production Database Backfill Script
Safely migrates existing wardrobe items to include normalized fields for semantic filtering
"""

import os
import sys
import json
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Set up paths before any imports
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Direct imports to avoid __init__.py relative import issues
import importlib.util

# Initialize Firebase directly with service account
import firebase_admin
from firebase_admin import credentials, firestore

db = None

# Try to initialize Firebase
try:
    # Check if already initialized
    if not firebase_admin._apps:
        service_account_path = os.path.join(backend_dir, 'service-account-key.json')
        if os.path.exists(service_account_path):
            print(f"🔐 Using service account: {service_account_path}")
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        else:
            print("❌ Service account key not found")
            print(f"   Expected at: {service_account_path}")
            sys.exit(1)
    
    db = firestore.client()
    print("✅ Firebase initialized successfully")
    
except Exception as e:
    print(f"❌ Firebase initialization failed: {e}")
    sys.exit(1)

# Load normalization utilities
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
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backfill_production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionBackfill:
    def __init__(self, batch_size: int = 500, dry_run: bool = False):
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.stats = {
            'total_processed': 0,
            'total_updated': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def get_next_batch(self, cursor: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get next batch of wardrobe items"""
        try:
            query = db.collection('wardrobe').order_by('id').limit(self.batch_size)
            
            if cursor:
                # Get the document to use as start point
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
    
    def normalize_item_safely(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
    
    def update_item(self, doc_id: str, normalized_fields: Dict[str, Any]) -> bool:
        """Update item with normalized fields"""
        try:
            if self.dry_run:
                logger.info(f"🔍 DRY RUN: Would update {doc_id}")
                logger.debug(f"   Normalized: {json.dumps(normalized_fields, indent=2)}")
                return True
            
            # Update the document with normalized fields
            db.collection('wardrobe').document(doc_id).update({
                'normalized': normalized_fields
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating item {doc_id}: {e}")
            return False
    
    def process_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, int]:
        """Process a batch of items"""
        batch_stats = {
            'processed': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for item in batch:
            try:
                batch_stats['processed'] += 1
                self.stats['total_processed'] += 1
                
                # Normalize the item
                normalized_fields = self.normalize_item_safely(item)
                
                if normalized_fields is None:
                    batch_stats['skipped'] += 1
                    self.stats['total_skipped'] += 1
                    continue
                
                # Update the item
                doc_id = item.get('doc_id')
                if doc_id and self.update_item(doc_id, normalized_fields):
                    batch_stats['updated'] += 1
                    self.stats['total_updated'] += 1
                else:
                    batch_stats['errors'] += 1
                    self.stats['total_errors'] += 1
                
            except Exception as e:
                logger.error(f"❌ Error processing item: {e}")
                batch_stats['errors'] += 1
                self.stats['total_errors'] += 1
        
        return batch_stats
    
    def run(self):
        """Run the complete backfill process"""
        mode = "DRY RUN" if self.dry_run else "PRODUCTION"
        logger.info(f"🚀 Starting wardrobe backfill [{mode}]")
        logger.info(f"   Batch size: {self.batch_size}")
        
        if not self.dry_run:
            confirm = input("\n⚠️  You are about to modify PRODUCTION data. Type 'YES' to continue: ")
            if confirm != 'YES':
                logger.info("❌ Backfill cancelled")
                return
        
        self.stats['start_time'] = datetime.utcnow()
        
        cursor = None
        batch_number = 0
        
        try:
            while True:
                batch_number += 1
                logger.info(f"\n📦 Processing batch {batch_number}...")
                
                # Get next batch
                batch = self.get_next_batch(cursor)
                
                if not batch:
                    logger.info("✅ No more items to process")
                    break
                
                # Process batch
                batch_stats = self.process_batch(batch)
                
                # Log batch results
                logger.info(f"   Batch {batch_number}: "
                           f"{batch_stats['processed']} processed, "
                           f"{batch_stats['updated']} updated, "
                           f"{batch_stats['skipped']} skipped, "
                           f"{batch_stats['errors']} errors")
                
                # Update cursor to last item's doc_id
                if batch:
                    cursor = batch[-1].get('doc_id')
                
                # Log overall progress every 5 batches
                if batch_number % 5 == 0:
                    logger.info(f"\n📊 Progress: {self.stats['total_processed']} items processed so far")
                
                # Small delay to avoid overwhelming the database
                if not self.dry_run:
                    time.sleep(0.2)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️  Backfill interrupted by user")
        except Exception as e:
            logger.error(f"\n❌ Backfill failed: {e}", exc_info=True)
            raise
        finally:
            self.stats['end_time'] = datetime.utcnow()
            self.log_final_stats()
    
    def log_final_stats(self):
        """Log final statistics"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 BACKFILL COMPLETE - FINAL STATISTICS")
        logger.info("=" * 70)
        logger.info(f"⏱️  Duration: {duration}")
        logger.info(f"📦 Total processed: {self.stats['total_processed']}")
        logger.info(f"✅ Total updated: {self.stats['total_updated']}")
        logger.info(f"⏭️  Total skipped: {self.stats['total_skipped']}")
        logger.info(f"❌ Total errors: {self.stats['total_errors']}")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['total_updated'] / self.stats['total_processed']) * 100
            logger.info(f"📈 Success rate: {success_rate:.1f}%")
        
        logger.info("=" * 70)
        
        # Save stats to file
        stats_file = f"backfill_stats_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)
        logger.info(f"💾 Stats saved to {stats_file}\n")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Production database backfill for semantic filtering')
    parser.add_argument('--batch-size', type=int, default=500, help='Batch size for processing')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no updates)')
    parser.add_argument('--environment', type=str, default='production', help='Environment (for logging)')
    
    args = parser.parse_args()
    
    logger.info(f"Environment: {args.environment}")
    
    # Create and run backfill
    backfill = ProductionBackfill(
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )
    
    try:
        backfill.run()
        return 0
    except Exception as e:
        logger.error(f"❌ Backfill failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

