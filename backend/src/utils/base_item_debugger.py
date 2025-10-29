"""
Base Item Debugging Utility

This module helps diagnose where base items are being filtered out
during the outfit generation process.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class BaseItemTracker:
    """Track base item through the entire outfit generation pipeline"""
    
    def __init__(self, base_item_id: Optional[str] = None):
        self.base_item_id = base_item_id
        self.checkpoints = []
        self.base_item_found = False
        self.last_seen_stage = None
        
    def checkpoint(self, stage: str, items: List[Any], context: str = "") -> bool:
        """
        Track base item at a specific stage in the pipeline.
        
        Args:
            stage: Name of the pipeline stage (e.g., "initial_wardrobe", "after_filtering")
            items: List of items at this stage
            context: Additional context about this checkpoint
            
        Returns:
            bool: True if base item is present, False otherwise
        """
        if not self.base_item_id:
            return True  # No base item to track
            
        base_item_present = False
        item_count = len(items) if items else 0
        
        # Check if base item is in the list
        for item in items:
            item_id = None
            if isinstance(item, dict):
                item_id = item.get('id')
            elif hasattr(item, 'id'):
                item_id = getattr(item, 'id', None)
            elif isinstance(item, tuple) and len(item) >= 2:
                # Handle (item_id, score_data) tuples
                item_id = item[0]
                
            if item_id == self.base_item_id:
                base_item_present = True
                self.base_item_found = True
                self.last_seen_stage = stage
                break
        
        checkpoint_data = {
            'stage': stage,
            'item_count': item_count,
            'base_item_present': base_item_present,
            'context': context
        }
        
        self.checkpoints.append(checkpoint_data)
        
        # Log the checkpoint
        status_icon = "✅" if base_item_present else "❌"
        logger.info(f"{status_icon} BASE ITEM TRACKER [{stage}]: {item_count} items, base_item_present={base_item_present} {context}")
        
        if not base_item_present and self.last_seen_stage:
            logger.error(f"🚨 BASE ITEM LOST: Was present in '{self.last_seen_stage}', not found in '{stage}'")
        
        return base_item_present
    
    def checkpoint_with_scores(self, stage: str, item_scores: Dict[str, Any], context: str = "") -> bool:
        """
        Track base item in scored items dictionary.
        
        Args:
            stage: Name of the pipeline stage
            item_scores: Dictionary mapping item_id to score data
            context: Additional context
            
        Returns:
            bool: True if base item is present in scores
        """
        if not self.base_item_id:
            return True
            
        base_item_present = self.base_item_id in item_scores
        item_count = len(item_scores)
        
        checkpoint_data = {
            'stage': stage,
            'item_count': item_count,
            'base_item_present': base_item_present,
            'context': context
        }
        
        self.checkpoints.append(checkpoint_data)
        
        # Log with score details if present
        if base_item_present and item_scores:
            score_data = item_scores[self.base_item_id]
            composite_score = score_data.get('composite_score', 0)
            logger.info(f"✅ BASE ITEM TRACKER [{stage}]: Present with composite_score={composite_score:.2f} {context}")
        else:
            status_icon = "❌"
            logger.error(f"{status_icon} BASE ITEM TRACKER [{stage}]: NOT FOUND in {item_count} scored items {context}")
            if self.last_seen_stage:
                logger.error(f"🚨 BASE ITEM LOST: Was present in '{self.last_seen_stage}', not found in '{stage}'")
        
        if base_item_present:
            self.base_item_found = True
            self.last_seen_stage = stage
        
        return base_item_present
    
    def get_report(self) -> Dict[str, Any]:
        """
        Generate a diagnostic report showing where base item was lost.
        
        Returns:
            Dict containing the full tracking history
        """
        if not self.base_item_id:
            return {
                'tracking_enabled': False,
                'message': 'No base item specified'
            }
        
        # Find where base item was lost
        lost_at_stage = None
        for i, checkpoint in enumerate(self.checkpoints):
            if not checkpoint['base_item_present'] and i > 0:
                lost_at_stage = checkpoint['stage']
                break
        
        return {
            'tracking_enabled': True,
            'base_item_id': self.base_item_id,
            'base_item_ever_found': self.base_item_found,
            'last_seen_stage': self.last_seen_stage,
            'lost_at_stage': lost_at_stage,
            'checkpoints': self.checkpoints,
            'total_checkpoints': len(self.checkpoints)
        }
    
    def print_summary(self):
        """Print a human-readable summary to logs"""
        report = self.get_report()
        
        if not report['tracking_enabled']:
            logger.info("🔍 BASE ITEM TRACKER: No base item specified, tracking disabled")
            return
        
        logger.info("=" * 80)
        logger.info("🔍 BASE ITEM TRACKING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Base Item ID: {report['base_item_id']}")
        logger.info(f"Ever Found: {report['base_item_ever_found']}")
        logger.info(f"Last Seen: {report['last_seen_stage']}")
        logger.info(f"Lost At: {report['lost_at_stage'] or 'Not lost / Still present'}")
        logger.info("-" * 80)
        logger.info(f"Pipeline Checkpoints ({report['total_checkpoints']}):")
        
        for i, checkpoint in enumerate(report['checkpoints'], 1):
            status = "✅ PRESENT" if checkpoint['base_item_present'] else "❌ MISSING"
            logger.info(f"  {i}. [{checkpoint['stage']}] {status} - {checkpoint['item_count']} items - {checkpoint['context']}")
        
        logger.info("=" * 80)
        
        # Provide diagnostic suggestions
        if report['lost_at_stage']:
            logger.error(f"🚨 DIAGNOSTIC: Base item was lost at stage '{report['lost_at_stage']}'")
            logger.error(f"💡 SUGGESTION: Check filtering/scoring logic in that stage")
        elif not report['base_item_ever_found']:
            logger.error(f"🚨 DIAGNOSTIC: Base item was NEVER found in any stage")
            logger.error(f"💡 SUGGESTION: Check if base item ID exists in initial wardrobe")
        else:
            logger.info(f"✅ DIAGNOSTIC: Base item successfully tracked through all stages")


def track_base_item_in_generation(
    base_item_id: Optional[str],
    wardrobe: List[Any],
    occasion_filtered: List[Any] = None,
    style_filtered: List[Any] = None,
    scored_items: Dict[str, Any] = None,
    final_outfit_items: List[Any] = None
) -> BaseItemTracker:
    """
    Convenience function to track base item through common pipeline stages.
    
    Args:
        base_item_id: ID of the base item to track
        wardrobe: Initial wardrobe items
        occasion_filtered: Items after occasion filtering
        style_filtered: Items after style filtering
        scored_items: Items after scoring
        final_outfit_items: Final outfit items
        
    Returns:
        BaseItemTracker with complete tracking history
    """
    tracker = BaseItemTracker(base_item_id)
    
    tracker.checkpoint("initial_wardrobe", wardrobe, "Starting wardrobe")
    
    if occasion_filtered is not None:
        tracker.checkpoint("after_occasion_filter", occasion_filtered, "After occasion filtering")
    
    if style_filtered is not None:
        tracker.checkpoint("after_style_filter", style_filtered, "After style filtering")
    
    if scored_items is not None:
        tracker.checkpoint_with_scores("after_scoring", scored_items, "After scoring phase")
    
    if final_outfit_items is not None:
        tracker.checkpoint("final_outfit", final_outfit_items, "Final outfit items")
    
    tracker.print_summary()
    
    return tracker

