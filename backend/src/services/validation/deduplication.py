#!/usr/bin/env python3
"""
Item Deduplication
==================

Functions to remove duplicate items from outfit selections.
"""

import logging
from typing import List, Any

logger = logging.getLogger(__name__)


def deduplicate_items(
    items: List[Any],
    safe_get_item_attr_func: callable,
    safe_get_item_name_func: callable,
    context: Any = None
) -> List[Any]:
    """
    Remove duplicate items (by id or name) from the final outfit selection.
    
    Args:
        items: List of clothing items
        safe_get_item_attr_func: Function to safely get item attributes
        safe_get_item_name_func: Function to safely get item names
        context: Optional generation context for metadata tracking
    
    Returns:
        List of unique items
    """
    seen_keys = set()
    unique_items = []
    deduped_keys = []
    
    for item in items:
        item_id = safe_get_item_attr_func(item, 'id', None)
        fallback_name = safe_get_item_name_func(item)
        key = item_id or fallback_name
        
        if key not in seen_keys:
            seen_keys.add(key)
            unique_items.append(item)
        else:
            deduped_keys.append(key)
    
    if deduped_keys:
        logger.info(f"🔁 DEDUPLICATION: Removed {len(deduped_keys)} duplicate items: {deduped_keys[:5]}{'...' if len(deduped_keys) > 5 else ''}")
        if context and hasattr(context, "metadata_notes") and isinstance(context.metadata_notes, dict):
            context.metadata_notes.setdefault("deduplicated_items", []).extend(deduped_keys)
    
    return unique_items

