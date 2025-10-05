"""
Utility functions for outfit generation and management.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def safe_get_metadata(obj: Dict[str, Any], key: str, default=None):
    """Safely get a value from metadata, handling None metadata."""
    if obj is None:
        return default
    metadata = obj.get("metadata") or {}
    return (metadata.get(key, default) if metadata else default)


def log_generation_strategy(outfit_response: Dict[str, Any], user_id: str = "unknown", 
                          generation_time: float = 0.0, validation_time: float = 0.0,
                          failed_rules: List[str] = None, fallback_reason: str = None):
    """Log generation strategy usage and record metrics for monitoring."""
    strategy = safe_get_metadata(outfit_response, "generation_strategy", "unknown")
    outfit_id = (outfit_response.get("id", "unknown") if outfit_response else "unknown")
    occasion = (outfit_response.get("occasion", "unknown") if outfit_response else "unknown")
    style = (outfit_response.get("style", "unknown") if outfit_response else "unknown")
    mood = (outfit_response.get("mood", "unknown") if outfit_response else "unknown")
    item_count = len((outfit_response.get("items", []) if outfit_response else []))
    
    # CRITICAL DEBUG: Log what strategy we're about to log
    logger.info(f"🔍 DEBUG LOG_GENERATION_STRATEGY: About to log strategy = {strategy}")
    print(f"🔍 DEBUG LOG_GENERATION_STRATEGY: About to log strategy = {strategy}")
    
    # Define which strategies are considered "complex" vs "fallback"
    complex_strategies = ["cohesive_composition", "body_type_optimized", "style_profile_matched", "weather_adapted", "rule_based"]
    fallback_strategies = ["fallback_simple", "emergency_default"]
    
    # Determine if this was a successful generation
    success = strategy in complex_strategies
    
    # Record metrics
    try:
        from ..services.generation_metrics_service import generation_metrics
        generation_metrics.record_generation(
            strategy=strategy,
            occasion=occasion,
            style=style,
            mood=mood,
            user_id=user_id,
            generation_time=generation_time,
            validation_time=validation_time,
            failed_rules=failed_rules or [],
            fallback_reason=fallback_reason,
            success=success
        )
    except Exception as e:
        logger.warning(f"Failed to record generation metrics: {e}")
    
    # Enhanced logging with segmentation and failed rules
    if strategy in fallback_strategies or not success:
        failed_rules_str = ", ".join(failed_rules) if failed_rules else "none"
        logger.warning(
            f"[GENERATION][FALLBACK] strategy={strategy} user={user_id} "
            f"occasion={occasion} style={style} mood={mood} items={item_count} "
            f"failed_rules=[{failed_rules_str}] reason={fallback_reason or 'unknown'}"
        )
    elif strategy in complex_strategies:
        logger.info(
            f"[GENERATION][SUCCESS] strategy={strategy} user={user_id} "
            f"occasion={occasion} style={style} mood={mood} items={item_count}"
        )
    else:
        logger.warning(
            f"[GENERATION][UNKNOWN] strategy={strategy} user={user_id} "
            f"occasion={occasion} style={style} mood={mood} items={item_count}"
        )


# Import for Firestore timestamp handling
try:
    from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds
    from google.cloud.firestore_v1.base_document import DocumentSnapshot
    FIRESTORE_TIMESTAMP_AVAILABLE = True
except ImportError:
    FIRESTORE_TIMESTAMP_AVAILABLE = False


def normalize_ts(value):
    """
    Normalize Firestore timestamps to Python datetime objects.
    Handles Firestore Timestamp, datetime, string, and None values.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if hasattr(value, "to_datetime"):  # Firestore Timestamp
        return value.to_datetime()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return None
    return None


def clean_for_firestore(obj):
    """Convert Pydantic or nested objects into Firestore-safe dicts."""
    # CRITICAL DEBUG: Log strategy before cleaning
    if isinstance(obj, dict) and 'metadata' in obj:
        strategy_before = safe_get_metadata(obj, 'generation_strategy', 'unknown')
        logger.info(f"🔍 DEBUG CLEAN_FOR_FIRESTORE BEFORE: strategy = {strategy_before}")
        print(f"🔍 DEBUG CLEAN_FOR_FIRESTORE BEFORE: strategy = {strategy_before}")
    
    # Handle Pydantic models
    if hasattr(obj, "dict"):  # Pydantic v1
        obj = obj.dict()
    elif hasattr(obj, "model_dump"):  # Pydantic v2
        obj = obj.model_dump()
    
    # Handle different data types
    if isinstance(obj, dict):
        safe = {}
        for k, v in obj.items():
            # Skip None values
            if v is None:
                continue
                
            # Handle datetime objects
            if isinstance(v, datetime):
                safe[k] = v  # Firestore can store datetime directly
            # Handle nested Pydantic objects
            elif hasattr(v, "dict"):  # Pydantic v1
                safe[k] = clean_for_firestore(v.dict())
            elif hasattr(v, "model_dump"):  # Pydantic v2
                safe[k] = clean_for_firestore(v.model_dump())
            # Handle nested dictionaries
            elif isinstance(v, dict):
                safe[k] = clean_for_firestore(v)
            # Handle lists
            elif isinstance(v, list):
                safe[k] = [clean_for_firestore(i) for i in v if i is not None]
            # Handle basic types that Firebase supports
            elif isinstance(v, (str, int, float, bool)):
                safe[k] = v
            # Skip complex objects that Firebase can't handle
            else:
                logger.warning(f"Skipping non-serializable field {k}: {type(v)}")
                continue
        
        # CRITICAL DEBUG: Log strategy after cleaning
        if 'metadata' in safe:
            strategy_after = safe_get_metadata(safe, 'generation_strategy', 'unknown')
            logger.info(f"🔍 DEBUG CLEAN_FOR_FIRESTORE AFTER: strategy = {strategy_after}")
            print(f"🔍 DEBUG CLEAN_FOR_FIRESTORE AFTER: strategy = {strategy_after}")
        
        return safe
    elif isinstance(obj, list):
        return [clean_for_firestore(i) for i in obj if i is not None]
    else:
        return obj
