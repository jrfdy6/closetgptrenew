#!/usr/bin/env python3
"""
Backfill Rollback Script
Safely rolls back normalized fields from wardrobe items
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add backend src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

try:
    from config.firebase import db
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root and Firebase is configured")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackfillRollback:
    def __init__(self, batch_size: int = 500, dry_run: bool = False):
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.stats = {
            'total_processed': 0,
            'total_rolled_back': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def log_stats(self):
        """Log current statistics"""
        logger.info(f"📊 Rollback Stats: {self.stats['total_processed']} processed, "
                   f"{self.stats['total_rolled_back']} rolled back, "
                   f"{self.stats['total_skipped']} skipped, "
                   f"{self.stats['total_errors']} errors")
    
    def get_next_batch(self, cursor: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get next batch of normalized items"""
        try:
            query = db.collection('wardrobe')\
                .where('normalized', '!=', None)\
                .order_by('id')\
                .limit(self.batch_size)
            
            if cursor:
                query = query.start_after({'id': cursor})
            
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
    
    def rollback_item(self, item: Dict[str, Any]) -> bool:
        """Rollback normalized fields from an item"""
        try:
            doc_id = item.get('doc_id')
            if not doc_id:
                logger.error(f"❌ No doc_id found for item {item.get('id', 'unknown')}")
                return False
            
            if self.dry_run:
                logger.info(f"🔍 DRY RUN: Would rollback {doc_id} (remove normalized fields)")
                return True
            
            # Remove normalized fields
            db.collection('wardrobe').document(doc_id).update({
                'normalized': None
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error rolling back item {item.get('id', 'unknown')}: {e}")
            return False
    
    def process_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, int]:
        """Process a batch of items for rollback"""
        batch_stats = {
            'processed': 0,
            'rolled_back': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for item in batch:
            try:
                batch_stats['processed'] += 1
                self.stats['total_processed'] += 1
                
                # Check if item has normalized fields
                if 'normalized' not in item:
                    batch_stats['skipped'] += 1
                    self.stats['total_skipped'] += 1
                    continue
                
                # Rollback the item
                if self.rollback_item(item):
                    batch_stats['rolled_back'] += 1
                    self.stats['total_rolled_back'] += 1
                    logger.debug(f"✅ Rolled back item {item.get('id', 'unknown')}")
                else:
                    batch_stats['errors'] += 1
                    self.stats['total_errors'] += 1
                
            except Exception as e:
                logger.error(f"❌ Error processing item {item.get('id', 'unknown')}: {e}")
                batch_stats['errors'] += 1
                self.stats['total_errors'] += 1
        
        return batch_stats
    
    def run_rollback(self):
        """Run the complete rollback process"""
        logger.info(f"🚀 Starting wardrobe rollback (batch_size: {self.batch_size}, dry_run: {self.dry_run})")
        self.stats['start_time'] = datetime.utcnow()
        
        cursor = None
        batch_number = 0
        
        try:
            while True:
                batch_number += 1
                logger.info(f"📦 Processing batch {batch_number}...")
                
                # Get next batch
                batch = self.get_next_batch(cursor)
                
                if not batch:
                    logger.info("✅ No more items to rollback")
                    break
                
                # Process batch
                batch_stats = self.process_batch(batch)
                
                # Log batch results
                logger.info(f"📊 Batch {batch_number} complete: "
                           f"{batch_stats['processed']} processed, "
                           f"{batch_stats['rolled_back']} rolled back, "
                           f"{batch_stats['skipped']} skipped, "
                           f"{batch_stats['errors']} errors")
                
                # Update cursor
                if batch:
                    cursor = batch[-1].get('id')
                
                # Log overall stats every 10 batches
                if batch_number % 10 == 0:
                    self.log_stats()
                
                # Small delay to avoid overwhelming the database
                import time
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("⏹️  Rollback interrupted by user")
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            raise
        finally:
            self.stats['end_time'] = datetime.utcnow()
            self.log_final_stats()
    
    def log_final_stats(self):
        """Log final statistics"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        logger.info("=" * 60)
        logger.info("📊 ROLLBACK COMPLETE - FINAL STATISTICS")
        logger.info("=" * 60)
        logger.info(f"⏱️  Duration: {duration}")
        logger.info(f"📦 Total processed: {self.stats['total_processed']}")
        logger.info(f"🔄 Total rolled back: {self.stats['total_rolled_back']}")
        logger.info(f"⏭️  Total skipped: {self.stats['total_skipped']}")
        logger.info(f"❌ Total errors: {self.stats['total_errors']}")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['total_rolled_back'] / self.stats['total_processed']) * 100
            logger.info(f"📈 Success rate: {success_rate:.1f}%")
        
        logger.info("=" * 60)
        
        # Save stats to file
        stats_file = f"rollback_stats_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)
        logger.info(f"💾 Stats saved to {stats_file}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rollback normalized fields from wardrobe items')
    parser.add_argument('--batch-size', type=int, default=500, help='Batch size for processing')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no updates)')
    parser.add_argument('--environment', choices=['development', 'staging', 'production'], 
                       default='staging', help='Target environment')
    
    args = parser.parse_args()
    
    # Environment safety check
    if args.environment == 'production' and not args.dry_run:
        confirm = input("⚠️  You are about to run rollback on PRODUCTION. Are you sure? (yes/no): ")
        if confirm.lower() != 'yes':
            logger.info("❌ Production rollback cancelled")
            return 1
    
    # Create and run rollback
    rollback = BackfillRollback(
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )
    
    try:
        rollback.run_rollback()
        return 0
    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
