#!/usr/bin/env python3
"""
Item Hydration Utility
=====================

Ensures wardrobe items have all required fields before Pydantic validation.
"""

import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Required fields for ClothingItem Pydantic model
REQUIRED_KEYS = ["imageUrl", "userId", "dominantColors", "matchingColors", "createdAt", "updatedAt", "type"]

def normalize_type(t: str) -> str:
    """Normalize clothing type to lowercase"""
    if not t: 
        return "other"
    return t.lower()

def hydrate_item_ref(item_ref: Dict[str, Any], firestore_client=None) -> Dict[str, Any]:
    """
    If item_ref appears to be a reference (only id or minimal fields),
    fetch the full doc; otherwise return item_ref normalized.
    """
    if isinstance(item_ref, dict) and item_ref.get("id") and len(item_ref.keys()) <= 3:
        logger.debug("Hydrating item id=%s", item_ref.get("id"))
        if firestore_client:
            try:
                full = firestore_client.get_item_by_id(item_ref["id"])
                if full:
                    logger.debug("Successfully hydrated item %s", item_ref["id"])
                    return full
                else:
                    logger.warning("Could not hydrate item %s - returning original ref", item_ref["id"])
            except Exception as e:
                logger.warning("Failed to hydrate item %s: %s", item_ref["id"], e)
        return item_ref

    # Already a full-ish dict: normalize minimal fields
    item = dict(item_ref)
    
    # Normalize type
    item["type"] = normalize_type(
        item.get("type") or 
        item.get("originalType") or 
        item.get("metadata", {}).get("originalType")
    )
    
    # Ensure timestamps
    ts = item.get("createdAt") or int(time.time() * 1000)
    item.setdefault("createdAt", ts)
    item.setdefault("updatedAt", ts)
    
    # Ensure arrays exist
    item.setdefault("dominantColors", item.get("dominantColors") or [])
    item.setdefault("matchingColors", item.get("matchingColors") or [])
    
    # Ensure required string fields
    item.setdefault("imageUrl", item.get("imageUrl") or "")
    item.setdefault("userId", item.get("userId") or "")
    
    # Ensure metadata exists
    if "metadata" not in item:
        item["metadata"] = {}
    
    # Ensure metadata has required fields
    metadata = item["metadata"]
    metadata.setdefault("analysisTimestamp", ts)
    metadata.setdefault("originalType", item["type"])
    metadata.setdefault("colorAnalysis", {"dominant": [], "matching": []})
    
    logger.debug("Normalized item %s: type=%s, imageUrl=%s, userId=%s", 
                item.get("id", "unknown"), item["type"], item["imageUrl"], item["userId"])
    
    return item

def hydrate_outfit_items(items: List[Dict[str, Any]], firestore_client=None) -> List[Dict[str, Any]]:
    """Hydrate a list of outfit items"""
    hydrated = []
    for raw in items:
        try:
            item = hydrate_item_ref(raw, firestore_client)
            hydrated.append(item)
            logger.debug("Successfully hydrated item: %s", item.get("id", "unknown"))
        except Exception as e:
            logger.exception("Failed to hydrate item: %s", raw)
            # Add minimal fallback
            fallback_item = {
                "id": raw.get("id", f"fallback-{int(time.time())}"),
                "name": raw.get("name", "Unknown Item"),
                "type": normalize_type(raw.get("type", "other")),
                "color": raw.get("color", "unknown"),
                "imageUrl": "",
                "userId": "",
                "dominantColors": [],
                "matchingColors": [],
                "createdAt": int(time.time() * 1000),
                "updatedAt": int(time.time() * 1000),
                "metadata": {
                    "analysisTimestamp": int(time.time() * 1000),
                    "originalType": normalize_type(raw.get("type", "other")),
                    "colorAnalysis": {"dominant": [], "matching": []}
                }
            }
            hydrated.append(fallback_item)
    
    logger.info("Hydrated %d items successfully", len(hydrated))
    return hydrated

def validate_item_completeness(item: Dict[str, Any]) -> bool:
    """Check if item has all required fields"""
    missing_fields = []
    for key in REQUIRED_KEYS:
        if key not in item or item[key] is None:
            missing_fields.append(key)
    
    if missing_fields:
        logger.warning("Item %s missing required fields: %s", item.get("id", "unknown"), missing_fields)
        return False
    
    # Check metadata completeness
    metadata = item.get("metadata", {})
    required_metadata = ["analysisTimestamp", "originalType", "colorAnalysis"]
    missing_metadata = [key for key in required_metadata if key not in metadata]
    
    if missing_metadata:
        logger.warning("Item %s missing required metadata: %s", item.get("id", "unknown"), missing_metadata)
        return False
    
    return True
