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
        (minimal.get("type") if minimal else None) or 
        (minimal.get("originalType") if minimal else None) or 
        (minimal.get("metadata", {}) if minimal else {}).get("originalType") or 
        "other"
    )
    
    # Extract name with fallback options
    item_name = (
        (minimal.get("name") if minimal else None) or 
        (minimal.get("title") if minimal else None) or 
        (minimal.get("itemName") if minimal else None) or 
        "Unknown item"
    )
    
    # Extract ID with fallback options
    item_id = (
        (minimal.get("id") if minimal else None) or 
        (minimal.get("itemId") if minimal else None) or 
        (minimal.get("_id") if minimal else None) or 
        f"generated-{now}"
    )
    
    # Extract image URL with fallback options
    image_url = (
        (minimal.get("imageUrl") if minimal else None) or 
        (minimal.get("storagePath") if minimal else None) or 
        (minimal.get("imagePath") if minimal else None) or 
        (minimal.get("photoUrl") if minimal else None) or 
        ""
    )
    
    # Extract user ID with fallback options
    user_id = (
        (minimal.get("userId") if minimal else None) or 
        (minimal.get("ownerId") if minimal else None) or 
        (minimal.get("user_id") if minimal else None) or 
        (minimal.get("createdBy") if minimal else None) or 
        "unknown"
    )
    
    full = {
        "id": item_id,
        "name": item_name,
        "type": normalize_type(item_type),
        "color": (minimal.get("color", "unknown") if minimal else "unknown"),
        "imageUrl": image_url,
        "style": (minimal.get("style", []) if minimal else []),
        "occasion": (minimal.get("occasion", ["casual"]) if minimal else ["casual"]),
        "season": (minimal.get("season", ["all"]) if minimal else ["all"]),
        "userId": user_id,
        "dominantColors": (minimal.get("dominantColors", []) if minimal else []),
        "matchingColors": (minimal.get("matchingColors", []) if minimal else []),
        "createdAt": (minimal.get("createdAt", now) if minimal else now),
        "updatedAt": (minimal.get("updatedAt", now) if minimal else now),
        "brand": (minimal.get("brand") if minimal else None),
        "wearCount": (minimal.get("wearCount", 0) if minimal else 0),
        "favorite_score": (minimal.get("favorite_score", 0.0) if minimal else 0.0),
        "tags": (minimal.get("tags", []) if minimal else []),
        "subType": (minimal.get("subType") if minimal else None),
        "colorName": (minimal.get("colorName") if minimal else None),
        "backgroundRemoved": (minimal.get("backgroundRemoved") if minimal else None),
        "embedding": (minimal.get("embedding") if minimal else None),
        "metadata": {
            "analysisTimestamp": now,
            "originalType": normalize_type(item_type),
            "originalSubType": (minimal.get("subType") if minimal else None),
            "styleTags": (minimal.get("style", []) if minimal else []),
            "occasionTags": (minimal.get("occasion", ["casual"]) if minimal else ["casual"]),
            "brand": (minimal.get("brand") if minimal else None),
            "imageHash": (minimal.get("imageHash") if minimal else None),
            "colorAnalysis": {
                "dominant": (minimal.get("dominantColors", []) if minimal else []),
                "matching": (minimal.get("matchingColors", []) if minimal else [])
            },
            "basicMetadata": (minimal.get("basicMetadata") if minimal else None),
            "visualAttributes": (minimal.get("visualAttributes") if minimal else None),
            "itemMetadata": (minimal.get("itemMetadata") if minimal else None),
            "naturalDescription": (minimal.get("naturalDescription") if minimal else None),
            "temperatureCompatibility": (minimal.get("temperatureCompatibility") if minimal else None),
            "materialCompatibility": (minimal.get("materialCompatibility") if minimal else None),
            "bodyTypeCompatibility": (minimal.get("bodyTypeCompatibility") if minimal else None),
            "skinToneCompatibility": (minimal.get("skinToneCompatibility") if minimal else None),
            "outfitScoring": (minimal.get("outfitScoring") if minimal else None),
            **(minimal.get("metadata", {}) if minimal else {})  # Preserve any existing metadata
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
    if isinstance(item_ref, dict) and (item_ref.get("id") if item_ref else None) and len(item_ref.keys()) <= 3:
        logger.debug("Hydrating item id=%s", (item_ref.get("id") if item_ref else None))
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
            logger.debug("Successfully hydrated item: %s", (item.get("id", "unknown") if item else "unknown"))
        except Exception as e:
            logger.exception("Failed to hydrate item: %s", raw)
            # Add minimal fallback
            fallback_item = {
                "id": (raw.get("id", f"fallback-{int(time.time() if raw else f"fallback-{int(time.time())}"),
                "name": (raw.get("name", "Unknown Item") if raw else "Unknown Item"),
                "type": normalize_type((raw.get("type", "other") if raw else "other")),
                "color": (raw.get("color", "unknown") if raw else "unknown"),
                "imageUrl": "https://placeholder.com/image.jpg",
                "userId": "unknown-user",
                "dominantColors": [],
                "matchingColors": [],
                "createdAt": int(time.time() * 1000),
                "updatedAt": int(time.time() * 1000),
                "metadata": {
                    "analysisTimestamp": int(time.time() * 1000),
                    "originalType": normalize_type((raw.get("type", "other") if raw else "other")),
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
        logger.warning("Item %s missing required fields: %s", (item.get("id", "unknown") if item else "unknown"), missing_fields)
        return False
    
    # Check metadata completeness
    metadata = (item.get("metadata", {}) if item else {})
    required_metadata = ["analysisTimestamp", "originalType", "colorAnalysis"]
    missing_metadata = [key for key in required_metadata if key not in metadata]
    
    if missing_metadata:
        logger.warning("Item %s missing required metadata: %s", (item.get("id", "unknown") if item else "unknown"), missing_metadata)
        return False
    
    return True
