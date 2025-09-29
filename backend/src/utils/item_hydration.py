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

def fallback_convert_minimal_to_full(minimal: Dict[str, Any]) -> Dict[str, Any]:
    """Convert minimal wardrobe item to full item with all required fields"""
    now = int(time.time() * 1000)
    
    # Extract type with fallback options
    item_type = (
        minimal.get("type") or 
        minimal.get("originalType") or 
        minimal.get("metadata", {}).get("originalType") or 
        "other"
    )
    
    # Extract name with fallback options
    item_name = (
        minimal.get("name") or 
        minimal.get("title") or 
        minimal.get("itemName") or 
        "Unknown item"
    )
    
    # Extract ID with fallback options
    item_id = (
        minimal.get("id") or 
        minimal.get("itemId") or 
        minimal.get("_id") or 
        f"generated-{now}"
    )
    
    # Extract image URL with fallback options
    image_url = (
        minimal.get("imageUrl") or 
        minimal.get("storagePath") or 
        minimal.get("imagePath") or 
        minimal.get("photoUrl") or 
        ""
    )
    
    # Extract user ID with fallback options
    user_id = (
        minimal.get("userId") or 
        minimal.get("ownerId") or 
        minimal.get("user_id") or 
        minimal.get("createdBy") or 
        "unknown"
    )
    
    full = {
        "id": item_id,
        "name": item_name,
        "type": normalize_type(item_type),
        "color": minimal.get("color", "unknown"),
        "imageUrl": image_url,
        "style": minimal.get("style", []),
        "occasion": minimal.get("occasion", ["casual"]),
        "season": minimal.get("season", ["all"]),
        "userId": user_id,
        "dominantColors": minimal.get("dominantColors", []),
        "matchingColors": minimal.get("matchingColors", []),
        "createdAt": minimal.get("createdAt", now),
        "updatedAt": minimal.get("updatedAt", now),
        "brand": minimal.get("brand"),
        "wearCount": minimal.get("wearCount", 0),
        "favorite_score": minimal.get("favorite_score", 0.0),
        "tags": minimal.get("tags", []),
        "subType": minimal.get("subType"),
        "colorName": minimal.get("colorName"),
        "backgroundRemoved": minimal.get("backgroundRemoved"),
        "embedding": minimal.get("embedding"),
        "metadata": {
            "analysisTimestamp": now,
            "originalType": normalize_type(item_type),
            "originalSubType": minimal.get("subType"),
            "styleTags": minimal.get("style", []),
            "occasionTags": minimal.get("occasion", ["casual"]),
            "brand": minimal.get("brand"),
            "imageHash": minimal.get("imageHash"),
            "colorAnalysis": {
                "dominant": minimal.get("dominantColors", []),
                "matching": minimal.get("matchingColors", [])
            },
            "basicMetadata": minimal.get("basicMetadata"),
            "visualAttributes": minimal.get("visualAttributes"),
            "itemMetadata": minimal.get("itemMetadata"),
            "naturalDescription": minimal.get("naturalDescription"),
            "temperatureCompatibility": minimal.get("temperatureCompatibility"),
            "materialCompatibility": minimal.get("materialCompatibility"),
            "bodyTypeCompatibility": minimal.get("bodyTypeCompatibility"),
            "skinToneCompatibility": minimal.get("skinToneCompatibility"),
            "outfitScoring": minimal.get("outfitScoring"),
            **minimal.get("metadata", {})  # Preserve any existing metadata
        },
        # Keep everything else that wasn't explicitly handled
        **{k: v for k, v in minimal.items() if k not in {
            "id", "name", "type", "color", "imageUrl", "style", "occasion", "season",
            "userId", "dominantColors", "matchingColors", "createdAt", "updatedAt",
            "brand", "wearCount", "favorite_score", "tags", "subType", "colorName",
            "backgroundRemoved", "embedding", "metadata", "originalType", "title",
            "itemId", "storagePath", "ownerId", "user_id", "createdBy", "imagePath",
            "photoUrl", "imageHash"
        }}
    }
    
    logger.debug("Converted minimal item %s to full item with %d fields", item_id, len(full))
    return full

def hydrate_item_ref(item_ref: Dict[str, Any], firestore_client=None) -> Dict[str, Any]:
    """
    If item_ref appears to be a reference (only id or minimal fields),
    fetch the full doc; otherwise return item_ref normalized using fallback conversion.
    """
    if isinstance(item_ref, dict) and item_ref.get("id") and len(item_ref.keys()) <= 3:
        logger.debug("Hydrating item id=%s", item_ref.get("id"))
        if firestore_client:
            try:
                full = firestore_client.get_item_by_id(item_ref["id"])
                if full:
                    logger.debug("Successfully hydrated item %s from database", item_ref["id"])
                    return fallback_convert_minimal_to_full(full)  # Ensure it's complete
                else:
                    logger.warning("Could not hydrate item %s from database - using fallback conversion", item_ref["id"])
            except Exception as e:
                logger.warning("Failed to hydrate item %s from database: %s - using fallback conversion", item_ref["id"], e)
        
        # Fallback: use minimal item with fallback conversion
        return fallback_convert_minimal_to_full(item_ref)

    # Already a full-ish dict: use fallback conversion to ensure completeness
    return fallback_convert_minimal_to_full(item_ref)

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
                "imageUrl": "https://placeholder.com/image.jpg",
                "userId": "unknown-user",
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
