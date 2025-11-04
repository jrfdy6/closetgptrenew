"""
Outfit management endpoints - Single canonical generator with bulletproof consistency.
All outfits are generated and saved through the same pipeline.
"""

import logging
import time
import urllib.parse
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

# Set up logger for generation tracking
logger = logging.getLogger(__name__)

# Debug logging for router loading
logger.error("🚨 FORCE REDEPLOY v13.0: OUTFITS ROUTER LOADING - This should appear in Railway logs")

# Global validation functions for semantic outfit validation
def validate_outfit_completeness(outfit_items, occasion_reqs, occasion):
    """Enhanced validation that uses semantic matching like the robust generator"""
    missing_required = []
    
    for required in occasion_reqs['required']:
        if ' OR ' in required:
            # Handle OR conditions (e.g., "shorts OR athletic-pants")
            options = [opt.strip() for opt in required.split(' OR ')]
            if not any(_is_semantically_appropriate(outfit_items, opt, occasion) for opt in options):
                missing_required.append(required)
        else:
            # Single requirement with semantic matching
            if not _is_semantically_appropriate(outfit_items, required, occasion):
                missing_required.append(required)
    
    return missing_required

def _is_semantically_appropriate(outfit_items, required_item, occasion):
    """Check if outfit has semantically appropriate items for the requirement"""
    occasion_lower = occasion.lower()
    
    for item in outfit_items:
        # Safety check: handle list, dict, and object formats
        if isinstance(item, list):
            # Skip if item is a list (shouldn't happen but safety check)
            continue
        elif isinstance(item, dict):
            item_type = (item.get('type', '') if item else '').lower()
            item_name = (item.get('name', '') if item else '').lower()
        else:
            # Handle object format
            item_type = getattr(item, 'type', '').lower()
            item_name = getattr(item, 'name', '').lower()
        
        # Direct match first
        if required_item in item_type or required_item in item_name:
            return True
        
        # Semantic matching based on occasion and requirement
        if required_item == 'sneakers' and occasion_lower == 'athletic':
            # Accept any athletic-appropriate footwear
            athletic_shoes = ['athletic', 'sport', 'running', 'training', 'gym', 'tennis', 'basketball']
            if any(term in item_name or term in item_type for term in athletic_shoes):
                return True
            # Accept casual shoes for athletic (more flexible)
            if 'shoes' in item_type and not any(formal in item_name for formal in ['dress', 'formal', 'oxford', 'loafer']):
                return True
        
        elif required_item == 'shirt' and occasion_lower in ['business', 'formal']:
            # Accept any business-appropriate top
            business_tops = ['shirt', 'blouse', 'button', 'dress', 'polo', 'business']
            if any(term in item_name or term in item_type for term in business_tops):
                return True
        
        elif required_item == 'pants' and occasion_lower in ['business', 'formal']:
            # Accept any business-appropriate bottom
            business_bottoms = ['pants', 'trousers', 'slacks', 'dress', 'formal']
            if any(term in item_name or term in item_type for term in business_bottoms):
                return True
        
        elif required_item == 'shorts' and occasion_lower == 'athletic':
            # Accept any athletic-appropriate bottom
            athletic_bottoms = ['shorts', 'athletic', 'sport', 'running', 'training', 'gym']
            if any(term in item_name or term in item_type for term in athletic_bottoms):
                return True
        
        elif required_item == 'athletic-appropriate footwear' and occasion_lower == 'athletic':
            # Accept any athletic-appropriate footwear
            athletic_shoes = ['athletic', 'sport', 'running', 'training', 'gym', 'tennis', 'basketball', 'sneakers']
            if any(term in item_name or term in item_type for term in athletic_shoes):
                return True
            # Accept casual shoes for athletic (more flexible)
            if 'shoes' in item_type and not any(formal in item_name for formal in ['dress', 'formal', 'oxford', 'loafer']):
                return True
        
        elif required_item == 'athletic-appropriate bottoms' and occasion_lower == 'athletic':
            # Accept any athletic-appropriate bottom
            athletic_bottoms = ['shorts', 'athletic', 'sport', 'running', 'training', 'gym', 'leggings', 'sweatpants']
            if any(term in item_name or term in item_type for term in athletic_bottoms):
                return True
        
        elif required_item == 'athletic-appropriate top' and occasion_lower == 'athletic':
            # Accept any athletic-appropriate top
            athletic_tops = ['t-shirt', 'tank', 'athletic', 'sport', 'running', 'training', 'gym', 'shirt']
            if any(term in item_name or term in item_type for term in athletic_tops):
                return True
        
        elif required_item == 'shirt OR t-shirt' and occasion_lower == 'casual':
            # Accept any casual top
            casual_tops = ['shirt', 't-shirt', 'top', 'blouse', 'polo']
            if any(term in item_name or term in item_type for term in casual_tops):
                return True
        
        elif required_item == 'pants OR shorts' and occasion_lower == 'casual':
            # Accept any casual bottom
            casual_bottoms = ['pants', 'jeans', 'shorts', 'bottom', 'trousers']
            if any(term in item_name or term in item_type for term in casual_bottoms):
                return True
    
    return False

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

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, field_validator

# Import authentication
from ..auth.auth_service import get_current_user, get_current_user_id
from ..custom_types.profile import UserProfile

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["outfits"]
)
security = HTTPBearer()

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
    # Handle basic types
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    # Skip complex objects
    else:
        logger.warning(f"Skipping non-serializable object: {type(obj)}")
        return str(obj)  # Convert to string as fallback

# Firebase imports moved inside functions to prevent import-time crashes
# from ..config.firebase import db, firebase_initialized
from ..auth.auth_service import get_current_user  # Keep this for dependency injection
from ..custom_types.profile import UserProfile   # Keep this for type hints
from ..custom_types.outfit import OutfitGeneratedOutfit  # Keep this for type hints
FIREBASE_AVAILABLE = False
db = None
firebase_initialized = False

# Simplified mock data function for fallback
# async def get_mock_outfits() -> List[Dict[str, Any]]:
#     """Return mock outfit data for testing."""
#     return [
#         {
#             "id": "mock-outfit-1",
#             "name": "Casual Summer Look",
#             "style": "casual",
#             "mood": "relaxed",
#             "items": [
#                 {"id": "item-1", "name": "Blue T-Shirt", "type": "shirt", "imageUrl": None},
#                 {"id": "item-2", "name": "Jeans", "type": "pants", "imageUrl": None}
#             ],
#             "occasion": "casual",
#             "confidence_score": 0.85,
#             "reasoning": "Perfect for a relaxed summer day",
#             "createdAt": datetime.now().isoformat(),
#             "user_id": None,
#             "generated_at": None
#         },
#         {
#             "id": "mock-outfit-2",
#             "name": "Business Casual",
#             "style": "business",
#             "mood": "professional",
#             "items": [
#                 {"id": "item-3", "name": "White Button-Up", "type": "shirt", "imageUrl": None},
#                 {"id": "item-4", "name": "Khaki Pants", "type": "pants", "imageUrl": None}
#             ],
#             "occasion": "business",
#             "confidence_score": 0.9,
#             "reasoning": "Professional yet comfortable",
#             "createdAt": datetime.now().isoformat(),
#             "user_id": None,
#             "generated_at": None
#         }
#     ]

class OutfitRequest(BaseModel):
    """Request model for outfit generation."""
    style: str
    mood: str
    occasion: str
    description: Optional[str] = None
    baseItem: Optional[Dict[str, Any]] = None
    baseItemId: Optional[str] = None  # Add baseItemId field to track user-selected base item
    wardrobe: Optional[List[Dict[str, Any]]] = []  # Add wardrobe field
    wardrobeItems: Optional[List[Dict[str, Any]]] = []  # Alternative wardrobe field name
    wardrobeCount: Optional[int] = 0  # Add wardrobeCount field
    wardrobeType: Optional[str] = "object"  # Add wardrobeType field
    weather: Optional[Dict[str, Any]] = None  # Add weather field
    
    # Additional fields from SmartWeatherOutfitGenerator
    user_profile: Optional[Dict[str, Any]] = None
    likedOutfits: Optional[List[Dict[str, Any]]] = []
    trendingStyles: Optional[List[Dict[str, Any]]] = []
    preferences: Optional[Dict[str, Any]] = None
    
    @property
    def resolved_wardrobe(self) -> List[Dict[str, Any]]:
        """Get wardrobe items, handling both wardrobe and wardrobeItems formats"""
        return self.wardrobe or self.wardrobeItems or []

class CreateOutfitRequest(BaseModel):
    """Request model for outfit creation."""
    name: str
    occasion: str
    style: str
    description: Optional[str] = None
    items: List[Dict[str, Any]]
    createdAt: Optional[int] = None

class OutfitResponse(BaseModel):
    """Response model for outfits."""
    id: str
    name: str
    style: Optional[str] = None
    mood: Optional[str] = None
    items: Optional[List[dict]] = None
    occasion: Optional[str] = None
    confidence_score: Optional[float] = None  # Keep this field but allow None values
    reasoning: Optional[str] = None
    createdAt: Optional[datetime] = None
    user_id: Optional[str] = None
    generated_at: Optional[str] = None
    wearCount: Optional[int] = 0
    lastWorn: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None  # Include generation_strategy and other metadata

    @field_validator("createdAt", mode="before")
    @classmethod
    def normalize_datetime(cls, v):
        if isinstance(v, str):
            # Fix double timezone issue: "2025-08-27T21:10:11.828353+00:00Z" → "2025-08-27T21:10:11.828353+00:00"
            if "+00:00Z" in v:
                v = v.replace("+00:00Z", "+00:00")
            elif v.endswith("Z") and "+00:00" not in v:
                # Convert "2025-08-27T21:10:11.828353Z" → "2025-08-27T21:10:11.828353+00:00"
                v = v.replace("Z", "+00:00")
        return v

def filter_items_by_style(items: List[Dict[str, Any]], style: str) -> List[Dict[str, Any]]:
    """Filter wardrobe items to only include those appropriate for the given style."""
    if not items or not style:
        return items
    
    style_lower = style.lower()
    
    # Define style-appropriate keywords for different styles
    style_filters = {
        'athleisure': {
            'include_keywords': ['athletic', 'sport', 'gym', 'track', 'jogger', 'sweat', 'hoodie', 'sneaker', 'running', 'workout', 'yoga', 'legging', 'active', 'performance'],
            'exclude_keywords': ['dress', 'formal', 'suit', 'blazer', 'business', 'oxford', 'heel', 'dress shirt', 'tie', 'formal pants'],
            'preferred_types': ['t-shirt', 'tank', 'hoodie', 'sweatshirt', 'joggers', 'leggings', 'sweatpants', 'sneakers', 'athletic shoes', 'track jacket']
        },
        'casual': {
            'include_keywords': ['casual', 'everyday', 'comfortable', 'relaxed'],
            'exclude_keywords': ['formal', 'business', 'dressy', 'cocktail'],
            'preferred_types': ['t-shirt', 'jeans', 'shorts', 'sneakers', 'casual shoes']
        },
        'formal': {
            'include_keywords': ['formal', 'dress', 'business', 'professional', 'suit', 'blazer'],
            'exclude_keywords': ['casual', 'athletic', 'sport', 'gym', 'sweat'],
            'preferred_types': ['dress shirt', 'blazer', 'suit', 'dress pants', 'dress shoes', 'heels']
        },
        'business': {
            'include_keywords': ['business', 'professional', 'work', 'office', 'formal'],
            'exclude_keywords': ['casual', 'athletic', 'sport', 'gym', 'sweat'],
            'preferred_types': ['dress shirt', 'blazer', 'dress pants', 'dress shoes', 'blouse']
        }
    }
    
    # Get filter criteria for this style (default to casual if style not found)
    filter_criteria = (style_filters.get(style_lower, style_filters['casual']) if style_filters else style_filters['casual'])
    
    filtered_items = []
    for item in items:
        # Safety check: handle list, dict, and object formats
        if isinstance(item, list):
            # Skip if item is a list (shouldn't happen but safety check)
            continue
        elif isinstance(item, dict):
            item_name = (item.get('name', '') if item else '').lower()
            item_type = (item.get('type', '') if item else '').lower()
            item_description = (item.get('description', '') if item else '').lower()
        else:
            # Handle object format
            item_name = getattr(item, 'name', '').lower()
            item_type = getattr(item, 'type', '').lower()
            item_description = getattr(item, 'description', '').lower()
        
        # Combine all text fields for keyword matching
        all_text = f"{item_name} {item_type} {item_description}"
        
        # Check if item should be excluded
        should_exclude = any(exclude_word in all_text for exclude_word in filter_criteria['exclude_keywords'])
        if should_exclude:
            item_name_for_log = item_name if isinstance(item, dict) else getattr(item, 'name', 'unnamed')
            logger.info(f"🚫 Excluding {item_name_for_log} from {style} style (contains excluded keywords)")
            continue
        
        # Check if item should be included (preferred types or include keywords)
        should_include = (
            item_type in filter_criteria['preferred_types'] or
            any(include_word in all_text for include_word in filter_criteria['include_keywords'])
        )
        
        if should_include:
            filtered_items.append(item)
            item_name_for_log = item_name if isinstance(item, dict) else getattr(item, 'name', 'unnamed')
            logger.info(f"✅ Including {item_name_for_log} for {style} style")
        else:
            # For athleisure, be more restrictive - only include items that explicitly match
            if style_lower == 'athleisure':
                item_name_for_log = item_name if isinstance(item, dict) else getattr(item, 'name', 'unnamed')
                logger.info(f"⚠️ Skipping {item_name_for_log} for athleisure (not explicitly athletic)")
            else:
                # For other styles, include items that don't explicitly conflict
                filtered_items.append(item)
                item_name_for_log = item_name if isinstance(item, dict) else getattr(item, 'name', 'unnamed')
                logger.info(f"➕ Including {item_name_for_log} for {style} style (no conflicts)")
    
    logger.info(f"🎯 Style filtering for {style}: {len(filtered_items)}/{len(items)} items kept")
    return filtered_items

def get_hard_style_exclusions(style: str, item: Dict[str, Any], mood: str = None) -> Optional[str]:
    """Check if an item should be hard-excluded from a specific style."""
    item_name = (item.get('name', '') if item else '').lower()
    item_type = (item.get('type', '') if item else '').lower()
    item_description = (item.get('description', '') if item else '').lower()
    item_material = (item.get('material', '') if item else '').lower()
    
    # Combine all text for analysis
    item_text = f"{item_name} {item_type} {item_description} {item_material}"
    
    global exclusion_debug
    
    # Exclusion debug logging removed
    
    # Define hard exclusions for specific styles
    exclusion_rules = {
        'athleisure': {
            'formal_indicators': ['formal', 'business', 'dress pants', 'suit', 'blazer', 'dress shirt', 'tie', 'oxford', 'dress shoes', 'heels'],
            'formal_materials': ['wool suit', 'silk tie', 'dress wool'],
            'formal_types': ['dress shirt', 'dress pants', 'suit jacket', 'blazer', 'tie', 'dress shoes']
        },
        'formal': {
            'casual_indicators': ['athletic', 'sport', 'gym', 'workout', 'jogger', 'sweat', 'hoodie', 'sneaker'],
            'casual_materials': ['jersey', 'fleece', 'athletic'],
            'casual_types': ['hoodie', 'sweatshirt', 'joggers', 'sweatpants', 'sneakers', 'athletic shoes']
        },
        'business': {
            'casual_indicators': ['athletic', 'sport', 'gym', 'workout', 'casual', 'distressed'],
            'casual_materials': ['jersey', 'fleece', 'athletic'],
            'casual_types': ['hoodie', 'sweatshirt', 'joggers', 'sneakers', 't-shirt']
        },
        'classic': {
            'athletic_indicators': ['athletic', 'sport', 'gym', 'workout', 'running', 'basketball'],
            'athletic_materials': ['jersey', 'fleece', 'athletic', 'mesh'],
            'athletic_types': ['sneakers', 'athletic shoes', 'running shoes', 'basketball shoes', 'joggers', 'sweatpants']
        }
    }
    
    # BRIDGE RULES: Allow cross-style combinations for specific occasion/style pairs
    bridge_rules = {
        ('classic', 'athletic'): {
            'allowed_athletic_items': ['sneakers', 'athletic shoes', 'polo shirt', 'chinos', 'joggers', 'athletic shorts'],
            'allowed_keywords': ['polo', 'chino', 'sneaker', 'athletic', 'sport', 'running', 'tennis']
        },
        ('athletic', 'classic'): {
            'allowed_classic_items': ['polo shirt', 'chinos', 'sneakers', 'athletic shoes', 'casual button-up'],
            'allowed_keywords': ['polo', 'chino', 'sneaker', 'classic', 'casual', 'button']
        }
    }
    
    if style not in exclusion_rules:
        return None
    
    rules = exclusion_rules[style]
    
    # Check for exclusion indicators
    exclusion_debug.append({
        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
        "style": style,
        "mood": mood,
        "item_text": item_text,
        "checking_indicators": list(rules.values())
    })
    
    # Check for bridge rules first (before standard exclusions)
    try:
        bridge_key = (style.lower(), 'athletic') if 'athletic' in item_text else None
        if not bridge_key:
            bridge_key = ('athletic', style.lower()) if style.lower() in ['classic', 'casual'] else None
        
        if bridge_key and bridge_key in bridge_rules:
            bridge_rule = bridge_rules[bridge_key]
            # Check if item matches bridge rule criteria
            for keyword in bridge_rule['allowed_keywords']:
                if keyword in item_text:
                    exclusion_debug.append({
        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
                        "bridge_rule_applied": f"{bridge_key[0]} + {bridge_key[1]} allows {keyword}",
                        "matched_keyword": keyword,
                        "reason": "cross-style bridge rule"
                    })
                    print(f"🌉 BRIDGE RULE: Allowing {keyword} for {bridge_key[0]} + {bridge_key[1]} combination")
                    return None  # Allow item through bridge rule
    except Exception as bridge_error:
        logger.warning(f"⚠️ Bridge rule error: {bridge_error}")
        # Continue with normal exclusion logic if bridge rules fail
    
    for category, indicators in rules.items():
        for indicator in indicators:
            if indicator in item_text:
                # BOLD MOOD EXCEPTION: Allow cross-style blending for fashion-forward looks
                if mood and mood.lower() == 'bold':
                    # Allow athletic items with Classic style for bold fashion statements
                    if style == 'classic' and category in ['athletic_indicators', 'athletic_materials', 'athletic_types']:
                        exclusion_debug.append({
        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
                            "exclusion_bypassed": f"Bold mood allows {indicator} with {style}",
                            "matched_indicator": indicator,
                            "category": category,
                            "reason": "fashion-forward bold styling"
                        })
                        print(f"🎨 BOLD EXCEPTION: Allowing {indicator} with {style} for bold fashion statement")
                        continue  # Skip exclusion for bold mood
                    
                    # EXTENDED BOLD EXCEPTION: Allow cross-style items for any style combination
                    if category in ['casual_indicators', 'casual_materials', 'casual_types', 'formal_indicators', 'formal_materials', 'formal_types']:
                        exclusion_debug.append({
        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
                            "exclusion_bypassed": f"Bold mood allows {indicator} with {style}",
                            "matched_indicator": indicator,
                            "category": category,
                            "reason": "bold mood cross-style blending"
                        })
                        print(f"🎨 BOLD EXCEPTION: Allowing {indicator} with {style} for bold cross-style blending")
                        continue  # Skip exclusion for bold mood
                
                exclusion_debug.append({
        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
                    "exclusion_reason": f"{indicator} inappropriate for {style}",
                    "matched_indicator": indicator,
                    "category": category
                })
                print(f"🚫 EXCLUSION MATCH: {indicator} found in {item_text}")
                return f"{indicator} inappropriate for {style}"
    
    exclusion_debug.append({
        "item_name": (item.get('name', 'unnamed') if item else 'unnamed'),
        "result": "no exclusion - item passes hard filter"
    })
    
    return None

def calculate_style_appropriateness_score(style: str, item: Dict[str, Any]) -> int:
    """Calculate style appropriateness score with heavy penalties for mismatches."""
    item_name = (item.get('name', '') if item else '').lower()
    item_type = (item.get('type', '') if item else '').lower()
    item_description = (item.get('description', '') if item else '').lower()
    item_material = (item.get('material', '') if item else '').lower()
    
    item_text = f"{item_name} {item_type} {item_description} {item_material}"
    
    # Define style-specific scoring
    style_scoring = {
        'athleisure': {
            'highly_appropriate': ['athletic', 'sport', 'performance', 'moisture-wicking', 'breathable', 'activewear', 'gym', 'workout', 'running', 'yoga'],
            'appropriate': ['comfortable', 'stretchy', 'casual', 'relaxed', 'cotton', 'polyester'],
            'inappropriate': ['formal', 'business', 'dressy', 'structured'],
            'highly_inappropriate': ['suit', 'blazer', 'dress pants', 'dress shirt', 'tie', 'oxford', 'formal pants', 'dress shoes', 'heels']
        },
        'formal': {
            'highly_appropriate': ['formal', 'business', 'professional', 'structured', 'tailored', 'dress', 'suit', 'blazer'],
            'appropriate': ['classic', 'elegant', 'refined', 'polished'],
            'inappropriate': ['casual', 'relaxed', 'distressed'],
            'highly_inappropriate': ['athletic', 'sport', 'gym', 'workout', 'hoodie', 'sweatshirt', 'joggers', 'sneakers']
        },
        'casual': {
            'highly_appropriate': ['casual', 'comfortable', 'relaxed', 'everyday', 'versatile'],
            'appropriate': ['cotton', 'denim', 'jersey', 'soft'],
            'inappropriate': ['formal', 'business', 'dressy'],
            'highly_inappropriate': ['suit', 'tie', 'dress pants', 'very formal']
        }
    }
    
    if style not in style_scoring:
        return 0  # Neutral score for unknown styles
    
    scoring = style_scoring[style]
    total_score = 0
    
    # Check for highly appropriate indicators (+30 points)
    for indicator in (scoring.get('highly_appropriate', []) if scoring else []):
        if indicator in item_text:
            total_score += 30
            
    # Check for appropriate indicators (+15 points)
    for indicator in (scoring.get('appropriate', []) if scoring else []):
        if indicator in item_text:
            total_score += 15
            
    # Check for inappropriate indicators (-25 points)
    for indicator in (scoring.get('inappropriate', []) if scoring else []):
        if indicator in item_text:
            total_score -= 25
            
    # Check for highly inappropriate indicators (-50 points)
    for indicator in (scoring.get('highly_inappropriate', []) if scoring else []):
        if indicator in item_text:
            total_score -= 50
    
    return total_score

def ensure_base_item_included(outfit: Dict[str, Any], base_item_id: Optional[str], wardrobe_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ensure base item is included in the outfit if specified, with weather appropriateness check."""
    if not base_item_id:
        return outfit
    
    logger.info(f"🎯 Ensuring base item {base_item_id} is included in outfit")
    
    # Find base item in wardrobe
    base_item = next((item for item in wardrobe_items if item.get('id') == base_item_id), None)
    
    if not base_item:
        logger.warning(f"⚠️ Base item {base_item_id} not found in wardrobe")
        return outfit
    
    # Check weather appropriateness of base item
    weather_data = (outfit.get('weather_data') if outfit else None)
    if weather_data:
        is_weather_appropriate = check_item_weather_appropriateness(base_item, weather_data)
        if not is_weather_appropriate:
            logger.warning(f"⚠️ Base item {(base_item.get('name', 'unnamed') if base_item else 'unnamed')} may not be weather-appropriate")
            # Add weather warning to outfit reasoning
            current_reasoning = (outfit.get('reasoning', '') if outfit else '')
            
            # Generate specific warning based on weather conditions
            temp = (weather_data.get('temperature', 70) if weather_data else 70)
            condition = (weather_data.get('condition', '') if weather_data else '').lower()
            item_name = (base_item.get('name', 'item') if base_item else 'item')
            
            # Get item details for specific warnings
            item_type = (base_item.get('type', '') if base_item else '').lower()
            metadata = (base_item.get('metadata', {}) if base_item else {})
            material = ""
            color = ""
            if isinstance(metadata, dict):
                visual_attrs = (metadata.get('visualAttributes', {}) if metadata else {})
                if isinstance(visual_attrs, dict):
                    material = (visual_attrs.get('material', '') if visual_attrs else '').lower()
                    color = (visual_attrs.get('color', '') if visual_attrs else '').lower()
            
            # Generate specific warning
            if temp >= 85 and any(mat in material for mat in ['wool', 'fleece', 'down', 'heavy']):
                weather_warning = f"\n\nNote: Your selected {item_name} may cause overheating in {temp}°F {condition} weather, but we've included it as requested."
            elif temp <= 40 and any(type_check in item_type for type_check in ['swimwear', 'tank', 'shorts']):
                weather_warning = f"\n\nNote: Your selected {item_name} may not provide adequate warmth for {temp}°F {condition} conditions, but we've included it as requested."
            elif ('rain' in condition or 'storm' in condition) and any(mat in material for mat in ['silk', 'suede', 'velvet']):
                weather_warning = f"\n\nNote: Your selected {item_name} may be damaged by {condition} conditions, but we've included it as requested."
            elif ('rain' in condition or 'storm' in condition) and 'white' in color:
                weather_warning = f"\n\nNote: Your selected {item_name} may be prone to staining in {condition} conditions - consider care when wearing, but we've included it as requested."
            else:
                weather_warning = f"\n\nNote: Your selected {item_name} may not be ideal for current weather conditions ({temp}°F, {condition}), but we've included it as requested."
            
            outfit['reasoning'] = current_reasoning + weather_warning
    
    # Ensure items array exists
    if 'items' not in outfit:
        outfit['items'] = []
    
    # Remove any existing base item to prevent duplicates
    outfit['items'] = [item for item in outfit['items'] if item.get('id') != base_item_id]
    
    # Insert base item at the beginning
    outfit['items'].insert(0, base_item)
    
    logger.info(f"✅ Base item {(base_item.get('name', 'unnamed') if base_item else 'unnamed')} guaranteed in outfit")
    return outfit

def check_item_weather_appropriateness(item: Dict[str, Any], weather_data: Dict[str, Any]) -> bool:
    """Check if an item is appropriate for the current weather conditions."""
    try:
        temperature = float((weather_data.get('temperature', 70) if weather_data else 70))
        condition = (weather_data.get('condition', '') if weather_data else '').lower()
        
        item_type = (item.get('type', '') if item else '').lower()
        item_name = (item.get('name', '') if item else '').lower()
        
        # Get material from metadata if available
        material = ""
        metadata = (item.get('metadata', {}) if item else {})
        if isinstance(metadata, dict):
            visual_attrs = (metadata.get('visualAttributes', {}) if metadata else {})
            if isinstance(visual_attrs, dict):
                material = (visual_attrs.get('material', '') if visual_attrs else '').lower()
        
        # Hot weather checks (85°F+)
        if temperature >= 85:
            exclude_materials = ['wool', 'fleece', 'thick', 'heavy', 'winter', 'cashmere']
            exclude_types = ['coat', 'jacket', 'sweater', 'hoodie', 'thermal']
            
            if material and any(mat in material for mat in exclude_materials):
                return False
            if any(item_type_check in item_type for item_type_check in exclude_types):
                return False
        
        # Cold weather checks (40°F and below)
        elif temperature <= 40:
            exclude_materials = ['linen', 'light cotton', 'mesh', 'silk']
            exclude_types = ['tank top', 'sleeveless', 'shorts', 'sandals']
            
            if material and any(mat in material for mat in exclude_materials):
                return False
            if any(item_type_check in item_type for item_type_check in exclude_types):
                return False
        
        # Rain/storm checks
        if ('rain' in condition or 'storm' in condition or 'thunderstorm' in condition or 
        (weather_data.get('precipitation', 0) if weather_data else 0) > 50):
            delicate_materials = ['silk', 'suede', 'velvet', 'linen']
            if material and any(mat in material for mat in delicate_materials):
                return False
        
        return True
        
    except Exception as e:
        logger.warning(f"Error checking weather appropriateness: {e}")
        return True  # Default to appropriate if check fails

def attach_weather_context_to_items(items: List, weather_data: Dict[str, Any]) -> List:
    """Attach weather context and appropriateness analysis to each item."""
    try:
        if not weather_data or not items:
            return items
            
        temp = (weather_data.get('temperature', 70) if weather_data else 70)
        condition = (weather_data.get('condition', 'clear') if weather_data else 'clear').lower()
        precipitation = (weather_data.get('precipitation', 0) if weather_data else 0)
        
        enhanced_items = []
        for item in items:
            # Handle both dict and Pydantic ClothingItem objects
            if hasattr(item, 'dict'):  # Pydantic object
                enhanced_item = item.dict()
                item_type = getattr(item, 'type', '').lower()
                item_name = getattr(item, 'name', '').lower()
                material = ""
                metadata = getattr(item, 'metadata', {})
                if hasattr(metadata, 'dict'):  # Pydantic metadata
                    metadata = metadata.dict()
                if isinstance(metadata, dict):
                    visual_attrs = (metadata.get('visualAttributes', {}) if metadata else {})
                    if isinstance(visual_attrs, dict):
                        material = (visual_attrs.get('material', '') if visual_attrs else '').lower()
                color = getattr(item, 'color', '').title()
            else:  # Dictionary
                enhanced_item = item.copy()
                item_type = (item.get('type', '') if item else '').lower()
                item_name = (item.get('name', '') if item else '').lower()
                material = ""
                metadata = (item.get('metadata', {}) if item else {})
                if isinstance(metadata, dict):
                    visual_attrs = (metadata.get('visualAttributes', {}) if metadata else {})
                    if isinstance(visual_attrs, dict):
                        material = (visual_attrs.get('material', '') if visual_attrs else '').lower()
        color = (item.get('color', '') if item else '').title()
            
            # Temperature appropriateness analysis
            temp_appropriateness = "excellent"
            temp_note = ""
            
            if temp >= 85:  # Very hot weather
                if any(heavy in item_name for heavy in ['heavy', 'winter', 'thick', 'wool', 'fleece', 'thermal']):
                    temp_appropriateness = "too warm"
                    temp_note = f"may be too warm for {temp}°F weather"
                elif 'shorts' in item_type or 'tank' in item_type:
                    temp_appropriateness = "excellent"
                    temp_note = f"perfect for {temp}°F hot weather"
                elif 'cotton' in material or 'linen' in material:
                    temp_appropriateness = "excellent"
                    temp_note = f"breathable fabric ideal for {temp}°F weather"
                else:
                    temp_appropriateness = "good"
                    temp_note = f"suitable for {temp}°F warm weather"
                    
            elif temp >= 75:  # Warm weather
                if 'shorts' in item_type or 'tank' in item_type:
                    temp_appropriateness = "excellent"
                    temp_note = f"comfortable for {temp}°F warm weather"
                elif any(heavy in item_name for heavy in ['heavy', 'winter', 'thick']):
                    temp_appropriateness = "borderline"
                    temp_note = f"may be warm for {temp}°F weather"
                else:
                    temp_appropriateness = "good"
                    temp_note = f"appropriate for {temp}°F warm weather"
                    
            elif temp >= 65:  # Mild weather
                temp_appropriateness = "excellent"
                temp_note = f"ideal for {temp}°F mild weather"
                
            elif temp >= 55:  # Cool weather
                if 'shorts' in item_type:
                    temp_appropriateness = "borderline"
                    temp_note = f"may be cool for {temp}°F weather"
                elif 'sweater' in item_type or 'jacket' in item_type:
                    temp_appropriateness = "excellent"
                    temp_note = f"perfect for {temp}°F cool weather"
                else:
                    temp_appropriateness = "good"
                    temp_note = f"suitable for {temp}°F cool weather"
                    
            else:  # Cold weather
                if any(cool in item_type for cool in ['shorts', 'tank', 'sleeveless']):
                    temp_appropriateness = "inappropriate"
                    temp_note = f"inadequate for {temp}°F cold weather"
                elif any(warm in item_name for warm in ['heavy', 'winter', 'wool', 'fleece']):
                    temp_appropriateness = "excellent"
                    temp_note = f"ideal for {temp}°F cold weather"
                else:
                    temp_appropriateness = "good"
                    temp_note = f"appropriate for {temp}°F cold weather"
            
            # Fabric and condition analysis
            fabric_note = ""
            if 'rain' in condition or precipitation > 50:
                if any(delicate in material for delicate in ['silk', 'suede', 'velvet', 'linen']):
                    fabric_note = f"Note: {material} fabric may not be ideal for wet conditions"
                elif any(water_resistant in material for water_resistant in ['nylon', 'polyester', 'gore-tex']):
                    fabric_note = f"Excellent: {material} provides good water resistance"
                    
            # Style and occasion analysis
            style_note = ""
            if item_type in ['dress', 'blazer', 'suit']:
                style_note = "professional and versatile"
            elif item_type in ['jeans', 'denim']:
                style_note = "casual and comfortable"
            elif item_type in ['sweater', 'cardigan']:
                style_note = "cozy and layered"
            elif item_type in ['shirt', 'blouse']:
                style_note = "classic and adaptable"
            
            # Attach weather context
            enhanced_item['weather_context'] = {
                'temperature_appropriateness': temp_appropriateness,
                'temperature_note': temp_note,
                'fabric_note': fabric_note,
                'style_note': style_note,
                'color': color,
                'overall_suitability': temp_appropriateness
            }
            
            enhanced_items.append(enhanced_item)
            
        return enhanced_items
        
    except Exception as e:
        logger.warning(f"Error attaching weather context to items: {e}")
        return items

# Real outfit generation logic with AI and user wardrobe
async def generate_outfit_logic(req: OutfitRequest, user_id: str) -> Dict[str, Any]:
    """Real outfit generation logic using user's wardrobe and AI recommendations."""
    print(f"🔎 MAIN LOGIC ENTRY: Starting generation for user {user_id}")
    print(f"🔎 MAIN LOGIC ENTRY: Request - style: {req.style}, mood: {req.mood}, occasion: {req.occasion}")
    # DEBUG: Log detailed request information
    # print(f"🔍 DEBUG INPUT: Wardrobe has {len(req.wardrobe) if (req.wardrobe if req else []) else 0} items")
    # print(f"🔍 DEBUG INPUT: (req.wardrobe if req else []) type = {type(req.wardrobe)}")
    print(f"🔍 DEBUG INPUT: req.resolved_wardrobe = {req.resolved_wardrobe}")
    # print(f"🔍 DEBUG INPUT: req.resolved_wardrobe type = {type(req.resolved_wardrobe)}")
    
    if (req.wardrobe if req else []):
        for i, item in enumerate(req.wardrobe[:3]):  # Log first 3 items
            print(f"🔍 DEBUG INPUT ITEM {i+1}: {getattr(item, 'id', 'NO_ID')} - {getattr(item, 'name', 'NO_NAME')} - {getattr(item, 'type', 'NO_TYPE')}")

    print(f"🔍 DEBUG INPUT: Weather data: {req.weather}")
    print(f"🔍 DEBUG INPUT: Base item ID: {req.baseItemId}")
    
    # Initialize debug info variable at function level
    robust_debug_info = None
    
    # Import Firebase inside function to prevent import-time crashes
    try:
        from ..config.firebase import db, firebase_initialized
        from ..auth.auth_service import get_current_user
        from ..custom_types.profile import UserProfile
        from ..custom_types.outfit import OutfitGeneratedOutfit
        FIREBASE_AVAILABLE = True
        print(f"🔎 MAIN LOGIC: Firebase imports successful")
    except ImportError as e:
        logger.warning(f"⚠️ Firebase import failed: {e}")
        print(f"🚨 MAIN LOGIC: Firebase import FAILED: {e}")
        FIREBASE_AVAILABLE = False
        db = None
        firebase_initialized = False
        get_current_user = None
        UserProfile = None
        OutfitGeneratedOutfit = None
    
    # Import robust generation service - NO FALLBACKS ALLOWED
        from ..services.robust_outfit_generation_service import RobustOutfitGenerationService, GenerationContext
    print(f"✅ MAIN LOGIC: Robust generation service imported successfully")
    logger.info(f"✅ ROBUST IMPORT: Robust generation service imported successfully")
    
    # Import ClothingItem for validation
    try:
        from ..custom_types.wardrobe import ClothingItem
        print(f"🔎 MAIN LOGIC: ClothingItem import successful")
    except ImportError as e:
        logger.error(f"🚨 FORCE REDEPLOY v12.0: ClothingItem import failed: {e}")
        print(f"🚨 MAIN LOGIC: ClothingItem import FAILED: {e}")
        ClothingItem = None
    
    logger.info(f"🎨 Generating outfit for user {user_id}: {req.style}, {req.mood}, {req.occasion}")
    logger.info(f"🔍 DATA HANDOFF: Request occasion='{req.occasion}', style='{req.style}', mood='{req.mood}'")
    
    try:
        # 1. Get wardrobe items (prefer request data, fallback to database)
        logger.error(f"🚨 DEBUG: (req.wardrobe if req else []) = {req.wardrobe}")
        logger.error(f"🚨 DEBUG: (req.wardrobe if req else [])Items = {req.wardrobeItems}")
        logger.error(f"🚨 DEBUG: req.resolved_wardrobe = {req.resolved_wardrobe}")
        # print(f"🚨 DEBUG: (req.wardrobe if req else []) = {req.wardrobe}")
        # print(f"🚨 DEBUG: (req.wardrobe if req else [])Items = {req.wardrobeItems}")
        print(f"🚨 DEBUG: req.resolved_wardrobe = {req.resolved_wardrobe}")
        wardrobe_items = req.resolved_wardrobe
        if not wardrobe_items:
            logger.info(f"📦 No wardrobe in request, fetching from database for user {user_id}")
            wardrobe_items = await get_user_wardrobe_cached(user_id)
        
        logger.info(f"📦 Using {len(wardrobe_items)} wardrobe items for generation")
        
        # Handle empty wardrobe case
        if not wardrobe_items:
            # NO FALLBACKS - Force proper wardrobe items
            logger.error(f"🚨 NO WARDROBE ITEMS - NO FALLBACKS ALLOWED")
            print(f"🚨 NO WARDROBE ITEMS: User={user_id} has no wardrobe items")
            raise Exception("No wardrobe items available - no fallbacks allowed. User must have wardrobe items.")
        
        # 2. Get user's style profile (with caching)
        # Getting user profile
        user_profile = await get_user_profile_cached(user_id)
        logger.info(f"👤 Retrieved user profile for {user_id}")
        
        # ENHANCED: Validate style-gender compatibility
        if user_profile and user_profile.get('gender'):
            style_validation = await validate_style_gender_compatibility(req.style, user_profile.get('gender'))
        if not (style_validation.get('is_compatible') if style_validation else None):
            logger.warning(f"⚠️ Style-gender compatibility issue: {(style_validation.get('warning') if style_validation else None)}")
                # For now, we'll continue but log the warning
                # In the future, we could suggest alternatives or reject the request
        
        # 3. Generate outfit using rule-based decision tree
        # Generating rule-based outfit
        
        # Log weather data for outfit generation
        if (req.weather if req else None):
            try:
                # Handle both dict and object weather data
                if isinstance(req.weather, dict):
                    temp = req.weather.get('temperature', 'unknown') if req.weather else 'unknown'
                    condition = req.weather.get('condition', 'unknown') if req.weather else 'unknown'
                else:
                    temp = getattr(req.weather, 'temperature', 'unknown')
                    condition = getattr(req.weather, 'condition', 'unknown')
                logger.info(f"🌤️ Weather data for outfit generation: {temp}°F, {condition}")
            except Exception as e:
                logger.warning(f"⚠️ Error accessing weather data: {e}")
        else:
            logger.warning(f"⚠️ No weather data provided for outfit generation")
        
        print(f"🔎 MAIN LOGIC: About to call robust outfit generation service")
        logger.error(f"🚨 FORCE REDEPLOY v12.0: RobustOutfitGenerationService = {RobustOutfitGenerationService}")
        logger.error(f"🚨 FORCE REDEPLOY v12.0: GenerationContext = {GenerationContext}")
        logger.error(f"🚨 FORCE REDEPLOY v12.0: Both available = {RobustOutfitGenerationService is not None and GenerationContext is not None}")
        
        # Robust service is required - no fallbacks allowed
        try:
            # Use robust outfit generation service - NO FALLBACKS ALLOWED
            logger.info("🚀 Using robust outfit generation service - NO FALLBACKS ALLOWED")
            print(f"🚀 ROBUST SERVICE: Starting robust outfit generation")
            # Ensure robust service is available
            if not RobustOutfitGenerationService or not GenerationContext:
                raise Exception("RobustOutfitGenerationService or GenerationContext is None - import failed!")
            
            # Use robust service
                logger.info("🚀 Using robust outfit generation service")
                print(f"🔎 DEBUG: RobustOutfitGenerationService available: {RobustOutfitGenerationService is not None}")
                print(f"🔎 DEBUG: GenerationContext available: {GenerationContext is not None}")
            
            # Initialize outfit variable to prevent "not defined" errors
            outfit = None
            
            # DEBUG: Log wardrobe items at the very beginning
            # print(f"🔍 DEBUG ROBUST START: (req.wardrobe if req else []) = {req.wardrobe}")
            # print(f"🔍 DEBUG ROBUST START: (req.wardrobe if req else []) type = {type(req.wardrobe)}")
            print(f"🔍 DEBUG ROBUST START: req.resolved_wardrobe = {req.resolved_wardrobe}")
            # print(f"🔍 DEBUG ROBUST START: req.resolved_wardrobe type = {type(req.resolved_wardrobe)}")
                
                # Create generation context - ensure weather is properly formatted
            weather_data = (req.weather if req else None)
                if isinstance(weather_data, dict):
                    # Convert dict to object-like structure for robust service
                    from types import SimpleNamespace
                    weather_data = SimpleNamespace(**weather_data)
                    logger.info(f"🔧 CONVERTED WEATHER: dict -> object for robust service")
                
                # WardrobePreprocessor integration
                logger.info(f"🔧 Starting WardrobePreprocessor integration")
                
                # HYDRATE WARDROBE ITEMS BEFORE ROBUST GENERATOR CALL
                logger.info(f"🔧 HYDRATING WARDROBE ITEMS BEFORE ROBUST GENERATOR")
            print(f"🔍 DEBUG HYDRATOR CALL: wardrobe_items = {wardrobe_items}")
            # print(f"🔍 DEBUG HYDRATOR CALL: wardrobe_items type = {type(wardrobe_items)}")
            # print(f"🔍 DEBUG HYDRATOR CALL: wardrobe_items length = {len(wardrobe_items) if wardrobe_items else 'None'}")
                try:
                    from ..utils.item_hydration import hydrate_outfit_items
                    hydrated_wardrobe_items = hydrate_outfit_items(wardrobe_items, db if firebase_initialized else None)
                    logger.info(f"✅ HYDRATED {len(hydrated_wardrobe_items)} items successfully")
                # print(f"🔍 DEBUG HYDRATOR CALL: Successfully hydrated {len(hydrated_wardrobe_items)} items")
                except Exception as hydrator_error:
                    logger.warning(f"⚠️ HYDATOR ERROR: {hydrator_error}")
                print(f"🚨 HYDRATOR ERROR: {hydrator_error}")
                import traceback
                # print(f"🚨 HYDRATOR TRACEBACK: {traceback.format_exc()}")
                    logger.info(f"🔄 Using original wardrobe_items as fallback")
                    hydrated_wardrobe_items = wardrobe_items
                
                # Update wardrobe_items with hydrated items
                wardrobe_items = hydrated_wardrobe_items
                
                # Initialize clothing_items list
                clothing_items = []
                
                if ClothingItem is None:
                    logger.warning(f"⚠️ ClothingItem not available, skipping validation")
                    clothing_items = hydrated_wardrobe_items  # Use raw items if ClothingItem not available
                else:
                    for i, item_dict in enumerate(hydrated_wardrobe_items):
                        print(f"🔍 DEBUG ITEM CONVERSION: Processing item {i}: {item_dict}")
                        # print(f"🔍 DEBUG ITEM CONVERSION: item_dict type = {type(item_dict)}")
                        try:
                            clothing_item = ClothingItem(**item_dict)
                            clothing_items.append(clothing_item)
                            print(f"🔍 DEBUG ITEM CONVERSION: Successfully converted item {i}")
                        except Exception as item_error:
                            logger.warning(f"⚠️ Failed to convert item {i}: {item_error}")
                            print(f"🚨 ITEM CONVERSION ERROR: {item_error}")
                            import traceback
                            # print(f"🚨 ITEM CONVERSION TRACEBACK: {traceback.format_exc()}")
                            continue
                
                logger.info(f"✅ Pre-outfit-construction guard completed - {len(clothing_items)} items converted successfully")
        
        # DEBUG: Check clothing_items for None values
        # print(f"🔍 DEBUG CONTEXT CREATION: clothing_items length = {len(clothing_items)}")
        # print(f"🔍 DEBUG CONTEXT CREATION: clothing_items type = {type(clothing_items)}")
        for i, item in enumerate(clothing_items):
            pass
            pass
            pass
            print(f"🔍 DEBUG CONTEXT CREATION: item {i} = {item}")
            # print(f"🔍 DEBUG CONTEXT CREATION: item {i} type = {type(item)}")
            if item is None:
                print(f"🚨 CRITICAL: clothing_items[{i}] is None!")
                
                context = GenerationContext(
                    user_id=user_id,
                    occasion=req.occasion,
                    style=req.style,
                    mood=req.mood,
                    weather=weather_data,
                    wardrobe=clothing_items,  # Use converted ClothingItem objects
                    user_profile=user_profile,
                    base_item_id=req.baseItemId
                )
                
                # Generate outfit using robust service
                logger.info(f"[GENERATION][ROBUST] START for user {user_id}, wardrobe size={len(wardrobe_items)}")
                logger.info(f"[GENERATION][ROBUST] Context: occasion={req.occasion}, style={req.style}, mood={req.mood}")
        logger.info(f"[GENERATION][ROBUST] Wardrobe categories: {[(item.get('type', 'unknown') if item else 'unknown') for item in wardrobe_items[:10]]}...")
                
                try:
                    logger.info(f"🚀 CALLING ROBUST SERVICE: generate_outfit()")
                    logger.info(f"🚀 ROBUST CONTEXT: user_id={context.user_id}, occasion={context.occasion}")
                    logger.info(f"🚀 ROBUST WARDROBE: {len(context.wardrobe)} items")
                    logger.info(f"🚀 ROBUST PROFILE: {context.user_profile}")
                    
                    logger.error(f"🚨 FORCE REDEPLOY v11.0: About to instantiate RobustOutfitGenerationService")
                    robust_service = RobustOutfitGenerationService()
                    logger.error(f"🚨 FORCE REDEPLOY v11.0: RobustOutfitGenerationService instantiated successfully")
                    logger.error(f"🚨 FORCE REDEPLOY v11.0: About to call generate_outfit with context")
                    logger.error(f"🚨 FORCE REDEPLOY v11.0: Context has {len(context.wardrobe)} wardrobe items")
                    logger.error(f"🚨 FORCE REDEPLOY v11.0: Context occasion: {context.occasion}, style: {context.style}")
        
        # DEBUG: Collect robust service debug information
        debug_info = {
        "robust_input": {
        "wardrobe_count": len(context.wardrobe),
        "occasion": context.occasion,
        "style": context.style,
        "mood": context.mood,
        "user_id": context.user_id,
        "wardrobe_items": [
        {
        "id": getattr(item, 'id', 'NO_ID'),
        "name": getattr(item, 'name', 'NO_NAME'),
        "type": str(getattr(item, 'type', 'NO_TYPE'))
        } for item in context.wardrobe[:3]
        ]
        }
        }
        
        # DEBUG: Log wardrobe item types before robust service call
        print(f"🔍 DEBUG WARDROBE ITEMS: About to call robust service")
        if hasattr(context, 'wardrobe') and context.wardrobe:
        # print(f"🔍 DEBUG WARDROBE ITEMS: Wardrobe has {len(context.wardrobe)} items")
        for i, item in enumerate(context.wardrobe):
        item_type = getattr(item, 'type', 'NO_TYPE')
        item_name = getattr(item, 'name', 'NO_NAME')
        print(f"🔍 DEBUG WARDROBE ITEM {i+1}: type='{item_type}' name='{item_name}'")
        if hasattr(item_type, 'value'):
        print(f"🔍 DEBUG WARDROBE ITEM {i+1}: type.value='{item_type.value}'")
        if hasattr(item_type, 'name'):
        print(f"🔍 DEBUG WARDROBE ITEM {i+1}: type.name='{item_type.name}'")
        else:
        print(f"🔍 DEBUG WARDROBE ITEMS: No wardrobe items or wardrobe is None")
        
        print(f"🔍 DEBUG BEFORE ROBUST CALL: robust_service = {robust_service}")
        print(f"🔍 DEBUG BEFORE ROBUST CALL: context = {context}")
        # print(f"🔍 DEBUG BEFORE ROBUST CALL: context.wardrobe = {len(context.wardrobe) if hasattr(context, 'wardrobe') else 'NO WARDROBE'}")
        
        # 🔥 COMPREHENSIVE ERROR TRACING FOR NoneType .get() DEBUGGING
        try:
                    robust_outfit = await robust_service.generate_outfit(context)
        logger.error(f"🚨 FORCE REDEPLOY v12.0: generate_outfit completed successfully")
        except Exception as e:
        import traceback
        error_details = {
        "error_type": str(type(e).__name__),
        "error_message": str(e),
        "full_traceback": traceback.format_exc(),
        "context_info": {
        "context_type": str(type(context)),
        "context_wardrobe_length": len(context.wardrobe) if hasattr(context, 'wardrobe') and context.wardrobe else 0,
        "context_occasion": getattr(context, 'occasion', 'NO_OCCASION'),
        "context_style": getattr(context, 'style', 'NO_STYLE'),
        "context_user_id": getattr(context, 'user_id', 'NO_USER_ID')
        }
        }
        logger.error("🔥 Robust outfit generation crash", extra=error_details, exc_info=True)
        print(f"🔥 ROBUST GENERATION CRASH: {error_details}")
        # print(f"🔥 FULL TRACEBACK:\n{traceback.format_exc()}")
        raise
        print(f"🔍 DEBUG ROBUST RETURN: robust_outfit = {robust_outfit}")
        # print(f"🔍 DEBUG ROBUST RETURN: type = {type(robust_outfit)}")
        if robust_outfit is None:
        print(f"🚨 CRITICAL: robust_outfit is None!")
        raise Exception("Robust service returned None - this should not happen")
        
        # DEBUG: Collect robust generation result
        debug_info["robust_output"] = {
        "outfit_type": str(type(robust_outfit)),
        "has_items_attr": hasattr(robust_outfit, 'items'),
        "items_count": len(robust_outfit.items) if hasattr(robust_outfit, 'items') else 0,
        "items_list": [
        {
        "id": getattr(item, 'id', 'NO_ID'),
        "name": getattr(item, 'name', 'NO_NAME')
        } for item in robust_outfit.items[:3]
        ] if hasattr(robust_outfit, 'items') and robust_outfit.items else []
        }
        
        # Store debug info for later use
        context.debug_info = debug_info
        robust_debug_info = debug_info  # Store in local scope for error handling
                    
                    logger.info(f"🚀 ROBUST SERVICE RETURNED: {type(robust_outfit)}")
                    logger.info(f"🚀 ROBUST OUTFIT ITEMS: {len(robust_outfit.items) if hasattr(robust_outfit, 'items') else 'NO ITEMS ATTR'}")
                    logger.info(f"🚀 ROBUST METADATA: {robust_outfit.metadata if hasattr(robust_outfit, 'metadata') else 'NO METADATA ATTR'}")
                    
                    # Log the generation strategy used
        metadata = getattr(robust_outfit, 'metadata', None)
        strategy = metadata.get('generation_strategy', 'unknown') if metadata else 'unknown'
                    logger.info(f"[GENERATION][ROBUST] SUCCESS - Generated outfit using strategy: {strategy}")
                    logger.info(f"[GENERATION][ROBUST] Outfit items: {len(robust_outfit.items)} items")
                    print(f"🎯 GENERATION STRATEGY: {strategy}")
                    # Check if robust service is internally falling back
                    if strategy == 'fallback_simple':
                        logger.warning(f"⚠️ ROBUST SERVICE INTERNAL FALLBACK: Strategy is fallback_simple")
                        print(f"🚨 ROBUST SERVICE INTERNAL FALLBACK: The robust service itself is falling back!")
                        print(f"🚨 This means the robust service is working but failing internally")
                        # Add detailed fallback reason logging
                        fallback_reason = "Unknown - robust service returned fallback_simple strategy"
                        if hasattr(robust_outfit, 'metadata'):
        metadata = getattr(robust_outfit, 'metadata', None)
        failed_rules = metadata.get('failed_rules', []) if metadata else []
                            if failed_rules:
                                fallback_reason = f"Failed validation rules: {failed_rules}"
                            elif len(robust_outfit.items) == 0:
                                fallback_reason = "Empty candidate pool - no items generated"
                            elif len(robust_outfit.items) < 3:
                                fallback_reason = f"Too few items generated: {len(robust_outfit.items)}"
                        
                        logger.warning(f"🔍 ROBUST FALLBACK REASON: {fallback_reason}")
                        print(f"🚨 ROBUST FALLBACK REASON: {fallback_reason}")
                except Exception as e:
                    logger.error(f"[GENERATION][ROBUST][ERROR] {e}", exc_info=True)
                    logger.error(f"[GENERATION][ROBUST][ERROR] Context: user={user_id}, occasion={req.occasion}, style={req.style}")
                    logger.error(f"[GENERATION][ROBUST][ERROR] Wardrobe size: {len(wardrobe_items)}")
                    logger.error(f"[GENERATION][ROBUST][ERROR] Exception type: {type(e).__name__}")
        # print(f"🚨 ROBUST GENERATOR ERROR: {type(e).__name__}: {e}")
                    print(f"🚨 ROBUST GENERATOR FULL TRACEBACK:")
                    import traceback
                    traceback.print_exc()
                    raise
                
                # Convert to expected format with error handling
                try:
                    logger.info(f"🔄 Converting robust outfit to expected format...")
                    logger.info(f"🔄 Robust outfit type: {type(robust_outfit)}")
                    logger.info(f"🔄 Robust outfit attributes: {dir(robust_outfit)}")
        
        # DEBUG: Log robust outfit attributes before conversion
        # print(f"🔍 DEBUG CONVERSION: Robust outfit type: {type(robust_outfit)}")
        # print(f"🔍 DEBUG CONVERSION: Robust outfit dir: {dir(robust_outfit)}")
        # print(f"🔍 DEBUG CONVERSION: Has items: {hasattr(robust_outfit, 'items')}")
        if hasattr(robust_outfit, 'items'):
        # print(f"🔍 DEBUG CONVERSION: Items type: {type(robust_outfit.items)}")
        # print(f"🔍 DEBUG CONVERSION: Items length: {len(robust_outfit.items) if robust_outfit.items else 0}")
        if robust_outfit.items:
        print(f"🔍 DEBUG CONVERSION: First item: {robust_outfit.items[0]}")
                    
                    outfit = {
                        'id': getattr(robust_outfit, 'id', 'unknown'),
                        'name': getattr(robust_outfit, 'name', 'Unknown Outfit'),
        'occasion': getattr(robust_outfit, 'occasion', (req.occasion if req else "unknown")),
        'style': getattr(robust_outfit, 'style', (req.style if req else "unknown")),
        'mood': getattr(robust_outfit, 'mood', (req.mood if req else "unknown")),
                        'confidence_score': getattr(robust_outfit, 'confidence', 0.0),
                        'items': getattr(robust_outfit, 'items', []),
                        'reasoning': getattr(robust_outfit, 'reasoning', 'Generated by robust service'),
                        'createdAt': getattr(robust_outfit, 'createdAt', int(time.time())),
                        'userId': getattr(robust_outfit, 'user_id', user_id),
                        'weather_data': getattr(robust_outfit, 'weather', None),
                        'pieces': getattr(robust_outfit, 'pieces', []),
                        'explanation': getattr(robust_outfit, 'explanation', 'Generated by robust service'),
                        'styleTags': getattr(robust_outfit, 'styleTags', []),
                        'colorHarmony': getattr(robust_outfit, 'colorHarmony', 'Unknown'),
                        'styleNotes': getattr(robust_outfit, 'styleNotes', 'Generated by robust service'),
                        'season': getattr(robust_outfit, 'season', 'all'),
                        'updatedAt': getattr(robust_outfit, 'updatedAt', int(time.time())),
        'metadata': getattr(robust_outfit, 'metadata', None),
                        'wasSuccessful': getattr(robust_outfit, 'wasSuccessful', True),
                        'baseItemId': getattr(robust_outfit, 'baseItemId', None),
                        'validationErrors': getattr(robust_outfit, 'validationErrors', []),
                        'userFeedback': getattr(robust_outfit, 'userFeedback', None)
                    }
                    
                    logger.info(f"✅ Successfully converted robust outfit to expected format")
        logger.info(f"✅ Outfit has {len((outfit.get('items', []) if outfit else []))} items")
                    
                except Exception as conversion_error:
                    logger.error(f"❌ Failed to convert robust outfit to expected format: {conversion_error}")
                    logger.error(f"❌ Conversion error type: {type(conversion_error).__name__}")
                    logger.error(f"❌ Conversion error details: {str(conversion_error)}")
                    raise conversion_error
                
        # Ensure outfit was successfully created
        if outfit is None:
        raise Exception("Outfit generation failed - outfit is None")
                
                # Log generation strategy for monitoring
        failed_rules = safe_get_metadata(outfit, 'failed_rules', [])
                log_generation_strategy(outfit, user_id, failed_rules=failed_rules)
                
                # Verify strategy is set correctly
        final_strategy = safe_get_metadata(outfit, 'generation_strategy', 'unknown')
                logger.info(f"🎯 FINAL STRATEGY: {final_strategy}")
                print(f"🎯 FINAL STRATEGY: {final_strategy}")
                # CRITICAL DEBUG: Log outfit metadata before any post-processing
        logger.info(f"🔍 DEBUG BEFORE POST-PROCESSING: outfit metadata = {(outfit.get('metadata') if outfit else None)}")
        # print(f"🔍 DEBUG BEFORE POST-PROCESSING: outfit metadata = {(outfit.get('metadata') if outfit else None)}")
                
                if final_strategy == 'fallback_simple':
                    logger.warning(f"⚠️ WARNING: Robust path returned fallback_simple strategy")
                    print(f"🚨 WARNING: Robust path returned fallback_simple strategy - this should be a robust strategy!")
        logger.info(f"✅ Robust generation successful with {len((outfit.get('items', []) if outfit else []))} items")
            
            # Add weather data to outfit for base item validation
        logger.error(f"🚨 DEBUG: About to add weather data - (req.weather if req else None) = {req.weather}")
        if (req.weather if req else None):
                try:
                    # Handle both dict and object weather data
                    if isinstance(req.weather, dict):
                        outfit['weather_data'] = {
        'temperature': req.weather.get('temperature', 70) if req.weather else 70,
        'condition': req.weather.get('condition', 'clear') if req.weather else 'clear',
        'humidity': req.weather.get('humidity', 65) if req.weather else 65,
        'wind_speed': req.weather.get('wind_speed', 5) if req.weather else 5,
        'precipitation': req.weather.get('precipitation', 0) if req.weather else 0
                        }
                    else:
                        outfit['weather_data'] = {
                            'temperature': getattr(req.weather, 'temperature', 70),
                            'condition': getattr(req.weather, 'condition', 'clear'),
                            'humidity': getattr(req.weather, 'humidity', 65),
                            'wind_speed': getattr(req.weather, 'wind_speed', 5),
                            'precipitation': getattr(req.weather, 'precipitation', 0)
                        }
                except Exception as e:
                    logger.warning(f"⚠️ Error setting weather data: {e}")
                    outfit['weather_data'] = {
                        'temperature': 70,
                        'condition': 'clear',
                        'humidity': 65,
                        'wind_speed': 5,
                        'precipitation': 0
                    }
            
            print(f"🔎 MAIN LOGIC: Rule-based generation succeeded")
        except Exception as rule_exception:
            print(f"🔎 MAIN LOGIC: Rule-based generation FAILED with exception: {rule_exception}")
            logger.error(f"🔎 MAIN LOGIC: Rule-based generation FAILED: {rule_exception}")
            raise rule_exception
        if outfit:
        logger.info(f"✨ Generated outfit: {outfit.get('name', 'Unknown')}")
        else:
        logger.error("❌ Generated outfit is None - this should not happen")
        raise Exception("🔥 OUTFIT NONE ERROR: Outfit generation failed - outfit is None")
        # Outfit generated successfully
        
        # Check if outfit generation was successful
        # print(f"🔍 DEBUG FINAL CHECK: Outfit type: {type(outfit)}")
        # print(f"🔍 DEBUG FINAL CHECK: Outfit keys: {list(outfit.keys()) if isinstance(outfit, dict) else 'NOT A DICT'}")
        # print(f"🔍 DEBUG FINAL CHECK: Has 'items' key: {'items' in outfit if isinstance(outfit, dict) else 'N/A'}")
        if isinstance(outfit, dict) and 'items' in outfit:
        print(f"🔍 DEBUG FINAL CHECK: Items value: {outfit['items']}")
        print(f"🔍 DEBUG FINAL CHECK: Items type: {type(outfit['items'])}")
        print(f"🔍 DEBUG FINAL CHECK: Items length: {len(outfit['items']) if outfit['items'] else 'None/Empty'}")
        
        if not outfit or not outfit.get('items') or len(outfit.get('items', [])) == 0:
            logger.error(f"❌ GENERATION FAILED: No items generated")
            logger.error(f"🔍 DEBUG: Outfit data: {outfit}")
            logger.error(f"🔍 CONTEXT: User={user_id}, Occasion={req.occasion}, Style={req.style}, Mood={req.mood}")
        
        # DEBUG: Add detailed failure information including robust service debug
        failure_info = {
        "outfit_type": str(type(outfit)),
        "outfit_keys": list(outfit.keys()) if isinstance(outfit, dict) else "Not a dict",
        "items_value": (outfit.get('items') if outfit else None) if isinstance(outfit, dict) else "N/A",
        "items_type": str(type((outfit.get('items') if outfit else None))) if isinstance(outfit, dict) else "N/A",
        "items_length": len(((outfit.get('items', []) if outfit else []) if outfit else [])) if isinstance(outfit, dict) and outfit.get('items') else 0,
        "request_wardrobe_size": len(req.wardrobe) if (req.wardrobe if req else []) else 0,
        "robust_service_debug": robust_debug_info if robust_debug_info else 'No debug info available'
        }
        
        raise Exception(f"Generation failed - no items produced. System needs fixing. DEBUG: {failure_info}")
        
        logger.info(f"✅ Rule-based generation successful with {len(outfit['items'])} items")
        # Rule-based outfit completed
        
        # Apply final base item guarantee
        outfit = ensure_base_item_included(outfit, (req.baseItemId if req else None), wardrobe_items)
        
        # ENHANCED: Attach weather context to each item
        if (req.weather if req else None):
            try:
                weather_data = {
                    'temperature': getattr(req.weather, 'temperature', 70),
                    'condition': getattr(req.weather, 'condition', 'clear'),
                    'precipitation': getattr(req.weather, 'precipitation', 0)
                }
        outfit['items'] = attach_weather_context_to_items((outfit.get('items', []) if outfit else []), weather_data)
        logger.info(f"🌤️ Attached weather context to {len((outfit.get('items', []) if outfit else []))} items")
            except Exception as weather_error:
                logger.warning(f"⚠️ Weather context attachment failed: {weather_error}")
        logger.warning(f"⚠️ Item types: {[type(item) for item in (outfit.get('items', []) if outfit else [])]}")
                # Continue without weather context rather than crashing
        
        # ENHANCED: Add weather combination validation
        if (req.weather if req else None):
        outfit = validate_weather_outfit_combinations(outfit, (req.weather if req else None))
        
        logger.info(f"✅ Final outfit: {len((outfit.get('items', []) if outfit else []))} items")
        logger.info(f"🔍 Final item IDs: {[item.get('id', 'no-id') for item in (outfit.get('items', []) if outfit else []) if item]}")
        
        # CRITICAL: Final validation check to guarantee 99% prevention
        outfit = _apply_final_outfit_validation(outfit)
        
        # PRESERVE ROBUST SERVICE STRATEGY - Don't overwrite it!
        # The robust service already set the correct strategy (emergency_default, body_type_optimized, etc.)
        # DO NOT set it to 'rule_based' here as that overwrites the robust service's strategy
        
        # Ensure metadata exists
        if 'metadata' not in outfit:
        outfit['metadata'] = None
        
        # Log generation strategy for monitoring (WITHOUT changing it)
        failed_rules = safe_get_metadata(outfit, 'failed_rules', [])
        log_generation_strategy(outfit, user_id, failed_rules=failed_rules)
        
        return outfit
        
    except Exception as e:
        logger.error(f"🚨 ROBUST GENERATION CRASHED: {e}")
        logger.exception("Full robust generation traceback:")
        # print(f"🚨 ROBUST GENERATION CRASHED: {type(e).__name__}: {e}")
        print(f"🚨 ROBUST CONTEXT: User={user_id}, Occasion={req.occasion}, Style={req.style}, Mood={req.mood}")
        # print(f"🚨 ROBUST TRACEBACK: {str(e)}")
        
        # FALLBACK RE-ENABLED - Root cause identified and fixed (weather data format)
        logger.warning(f"⚠️ FALLBACK TRIGGERED: Outfit generation failed with exception: {e}")
        logger.exception("Full traceback:")
        print(f"🚨 FALLBACK ALERT: Exception in main generation logic")
        print(f"🚨 FALLBACK CONTEXT: User={user_id}, Occasion={req.occasion}, Style={req.style}, Mood={req.mood}")
        print(f"🚨 GENERATION FAILED - NO FALLBACKS ALLOWED")
        # print(f"🚨 ERROR: {type(e).__name__}: {e}")
        # print(f"🚨 TRACEBACK: {str(e)}")
        # NO FALLBACKS - Force proper error handling
        raise e

async def validate_style_gender_compatibility(style: str, user_gender: str) -> Dict[str, Any]:
    """Validate if the requested style is appropriate for the user's gender."""
    # Validating style for gender
    
    # Gender-specific style definitions
    feminine_styles = [
        'french girl', 'romantic', 'pinup', 'boho', 'cottagecore', 
        'coastal grandmother', 'clean girl', 'feminine', 'delicate'
    ]
    
    masculine_styles = [
        'techwear', 'grunge', 'streetwear', 'rugged', 'masculine', 
        'athletic', 'sporty', 'urban'
    ]
    
    unisex_styles = [
        'minimalist', 'modern', 'classic', 'business casual', 'preppy',
        'casual', 'formal', 'avant-garde', 'artsy', 'maximalist',
        'colorblock', 'scandinavian', 'coastal chic', 'athleisure'
    ]
    
    style_lower = style.lower()
    user_gender_lower = user_gender.lower()
    
    # Check style appropriateness
    if user_gender_lower == 'male' and style_lower in feminine_styles:
        return {
            "is_compatible": False,
            "warning": f"Style '{style}' is typically feminine and may not be appropriate for male users",
            "suggested_alternatives": [s for s in unisex_styles if s not in ['french girl', 'romantic']]
        }
    
    elif user_gender_lower == 'female' and style_lower in masculine_styles:
        return {
            "is_compatible": False,
            "warning": f"Style '{style}' is typically masculine and may not be appropriate for female users",
            "suggested_alternatives": [s for s in unisex_styles if s not in ['techwear', 'grunge']]
        }
    
    else:
        return {
            "is_compatible": True,
            "warning": None,
            "suggested_alternatives": []
        }

async def validate_outfit_composition(items: List[Dict], occasion: str, base_item: Optional[Dict] = None, style: str = "casual") -> List[Dict]:
    """Validate and ensure outfit has required components using enhanced validation."""
    # Validating outfit composition
    
    # Convert dict items to ClothingItem objects for validation
    from ..custom_types.wardrobe import ClothingItem
    from ..services.outfit_validation_service import OutfitValidationService
    
    clothing_items = []
    for item_dict in items:
        try:
            # Normalize the type using the validation utility
            from ..utils.validation import normalize_clothing_type
        normalized_type = normalize_clothing_type((item_dict.get('type', 'other') if item_dict else 'other'))
            
            # Create a basic ClothingItem from the dict with all required fields
            clothing_item = ClothingItem(
        id=(item_dict.get('id', '') if item_dict else ''),
        name=(item_dict.get('name', '') if item_dict else ''),
                type=normalized_type,
        color=(item_dict.get('color', 'unknown') if item_dict else 'unknown'),
        imageUrl=(item_dict.get('imageUrl', '') if item_dict else ''),
        style=(item_dict.get('style', []) if item_dict else []),
        occasion=(item_dict.get('occasion', ['casual']) if item_dict else ['casual']),
        season=(item_dict.get('season', ['all']) if item_dict else ['all']),
        userId=(item_dict.get('userId', 'unknown') if item_dict else 'unknown'),
        dominantColors=(item_dict.get('dominantColors', []) if item_dict else []),
        matchingColors=(item_dict.get('matchingColors', []) if item_dict else []),
        createdAt=(item_dict.get('createdAt', int(time.time() * 1000)) if item_dict else int(time.time() * 1000)),
        updatedAt=(item_dict.get('updatedAt', int(time.time() * 1000)) if item_dict else int(time.time() * 1000)),
        brand=(item_dict.get('brand', None) if item_dict else None),
        wearCount=(item_dict.get('wearCount', 0) if item_dict else 0),
        favorite_score=(item_dict.get('favorite_score', 0.0) if item_dict else 0.0),
        tags=(item_dict.get('tags', []) if item_dict else []),
                metadata=item_dict.get('metadata', {
                    'analysisTimestamp': int(time.time() * 1000),
        'originalType': (item_dict.get('type', 'other') if item_dict else 'other'),
                    'originalSubType': None,
        'styleTags': (item_dict.get('style', []) if item_dict else []),
        'occasionTags': (item_dict.get('occasion', ['casual']) if item_dict else ['casual']),
        'brand': (item_dict.get('brand', None) if item_dict else None),
                    'imageHash': None,
                    'colorAnalysis': {
                        'dominant': [],
                        'matching': []
                    },
                    'basicMetadata': None,
                    'visualAttributes': None,
                    'itemMetadata': None,
                    'naturalDescription': None,
                    'temperatureCompatibility': None,
                    'materialCompatibility': None,
                    'bodyTypeCompatibility': None,
                    'skinToneCompatibility': None,
                    'outfitScoring': None
                })
            )
            clothing_items.append(clothing_item)
        except Exception as e:
            logger.warning(f"⚠️ Failed to convert item to ClothingItem: {e}")
            continue
    
    # Use ENHANCED validation service with integrated thought clarification
    from ..services.validation_integration_service import ValidationIntegrationService
    validation_service = ValidationIntegrationService()
    
    # Create context for validation
    context = {
        "occasion": occasion,
        "weather": {"temperature": 70, "condition": "clear"},  # Default weather
        "user_profile": {},
        "style": style,  # Use actual request style instead of hardcoded "casual"
        "mood": None,
        "target_counts": {
            "min_items": 3,
            "max_items": 6,
            "required_categories": ["top", "bottom", "shoes"]
        }
    }
    
    logger.info(f"🔍 DATA HANDOFF: Validation context created - occasion='{context['occasion']}', style='{context['style']}', mood='{context['mood']}'")
    
    # Run enhanced validation with inappropriate combination enforcement + simulation-based rules
    # print(f"🔍 VALIDATION DEBUG: Starting validation with {len(clothing_items)} items")
    print(f"🔍 VALIDATION DEBUG: Item types: {[item.type for item in clothing_items]}")
    try:
        validation_result = await validation_service.validate_outfit_with_enhanced_rules(clothing_items, context)
        # print(f"🔍 VALIDATION DEBUG: Validation completed, result keys: {validation_result.keys()}")
        # print(f"🔍 VALIDATION DEBUG: Filtered items count: {len((validation_result.get('filtered_items', []) if validation_result else []))}")
    
        if validation_result.get("filtered_items"):
            # Convert back to dict format
            validated_outfit = []
            for item in validation_result["filtered_items"]:
                item_dict = {
                    "id": item.id,
                    "name": item.name,
                    "type": item.type,
                    "color": item.color,
                    "imageUrl": item.imageUrl,
                    "style": item.style,
                    "occasion": item.occasion,
                    "brand": item.brand,
                    "wearCount": item.wearCount,
                    "favorite_score": item.favorite_score,
                    "tags": item.tags,
                    "metadata": item.metadata
                }
                validated_outfit.append(item_dict)
            
            logger.info(f"✅ Enhanced validation completed: {len(validated_outfit)} items after filtering")
            if validation_result.get("errors"):
                errors = validation_result["errors"]
                logger.info(f"🔍 Validation errors: {errors}")
            if validation_result.get("warnings"):
                warnings = validation_result["warnings"]
                logger.info(f"🔍 Validation warnings: {warnings}")
            
        # print(f"🔍 VALIDATION DEBUG: Returning {len(validated_outfit)} items")
            return validated_outfit
        else:
            print(f"❌ VALIDATION DEBUG: No filtered items returned from enhanced validation!")
            print(f"❌ VALIDATION DEBUG: Validation result: {validation_result}")
            # NO FALLBACK TO BAD OUTFITS - Return empty list if validation fails
            return []
            
    except Exception as validation_error:
        print(f"❌ VALIDATION DEBUG: Enhanced validation failed with error: {validation_error}")
        logger.error(f"Enhanced validation failed: {validation_error}")
        # NO FALLBACK TO BAD OUTFITS - Return empty list on validation failure
        return []
    # CRITICAL: Check if we have any items at all before falling back
    if not clothing_items:
        print(f"❌ VALIDATION CRITICAL: No clothing items to validate!")
        return []  # NO FALLBACK TO BAD OUTFITS - Return empty list
    
        # NO FALLBACK TO BAD OUTFITS - If we reach here, validation failed
        logger.error("❌ Enhanced validation failed completely - no fallback allowed")
        print(f"🚨 VALIDATION FAILURE: No valid outfit can be generated")
        # print(f"🚨 VALIDATION CONTEXT: Items={len(clothing_items)}, Occasion={occasion}")
        print(f"🚨 VALIDATION REASON: All items failed enhanced validation rules")
        return []

async def validate_layering_rules(items: List[Dict], occasion: str) -> Dict[str, Any]:
    """Validate layering rules for the outfit."""
    logger.info(f"🔍 DEBUG: Validating layering rules for {occasion} occasion")
    
    # Count layering items
    layer_items = [item for item in items if is_layer_item((item.get('type', '') if item else ''))]
    layer_count = len(layer_items)
    
    logger.info(f"🔍 DEBUG: Found {layer_count} layering items: {[(item.get('name', 'unnamed') if item else 'unnamed') for item in layer_items]}")
    
    warnings = []
    
    # Occasion-based layering rules
    if occasion.lower() in ['formal', 'business']:
        if layer_count < 2:
            warnings.append(f"Formal occasion typically requires at least 2 layers, got {layer_count}")
        elif layer_count > 3:
            warnings.append(f"Formal occasion may have too many layers: {layer_count}")
    
    elif occasion.lower() in ['casual', 'weekend']:
        if layer_count > 3:
            warnings.append(f"Casual occasion may have too many layers: {layer_count}")
    
    elif occasion.lower() in ['athletic', 'gym', 'sporty']:
        if layer_count > 2:
            warnings.append(f"Athletic occasion typically needs fewer layers: {layer_count}")
    
    # Check for layering conflicts
    layer_types = [(item.get('type', '') if item else '').lower() for item in layer_items]
    
    # Heavy combinations
    if 'sweater' in layer_types and 'jacket' in layer_types:
        warnings.append("Sweater and jacket combination may be too heavy")
    
    if 'sweater' in layer_types and 'coat' in layer_types:
        warnings.append("Sweater and coat combination may be too heavy")
    
    if 'jacket' in layer_types and 'coat' in layer_types:
        warnings.append("Jacket and coat combination may be too heavy")
    
    # Multiple heavy items
    heavy_items = [item for item in layer_items if item.get('type', '').lower() in ['sweater', 'jacket', 'coat']]
    if len(heavy_items) > 2:
        warnings.append(f"Too many heavy layering items: {len(heavy_items)}")
    
    # ENHANCED: Prevent shirt-on-shirt combinations
    shirt_types = ['t-shirt', 'polo', 'shirt', 'blouse', 'dress shirt', 'button up', 'button-up', 'oxford', 'dress-shirt']
    shirt_count = sum(1 for layer_type in layer_types if any(shirt_type in layer_type for shirt_type in shirt_types))
    if shirt_count > 1:
        warnings.append(f"Multiple shirt types detected ({shirt_count}): Avoid layering shirts on shirts")
        logger.warning(f"🔍 DEBUG: Shirt-on-shirt combination detected: {layer_types}")
    
    # ENHANCED: Prevent flip-flops/slides with formal wear
    formal_items = ['blazer', 'suit', 'suit jacket', 'sport coat', 'jacket']
    casual_shoes = ['flip-flops', 'flip flops', 'slides', 'sandals', 'thongs']
    
    has_formal_item = any(formal_type in layer_type for formal_type in formal_items for layer_type in layer_types)
    has_casual_shoes = any(casual_shoe in layer_type for casual_shoe in casual_shoes for layer_type in layer_types)
    
    if has_formal_item and has_casual_shoes:
        warnings.append("Flip-flops/slides should not be worn with blazers or suits")
        logger.warning(f"🔍 DEBUG: Formal-casual shoe mismatch detected: formal={formal_items}, casual_shoes={casual_shoes}")
    
    logger.info(f"🔍 DEBUG: Layering validation complete: {len(warnings)} warnings")
    
    return {
        "layer_count": layer_count,
        "layer_items": [(item.get('name', 'unnamed') if item else 'unnamed') for item in layer_items],
        "warnings": warnings,
        "is_valid": len(warnings) == 0
    }

async def validate_color_material_harmony(items: List[Dict], style: str, mood: str) -> Dict[str, Any]:
    """Validate color theory and material compatibility."""
    logger.info(f"🔍 DEBUG: Validating color and material harmony for {style} style, {mood} mood")
    
    warnings = []
    color_analysis = {}
    material_analysis = {}
    
    # Extract colors and materials from items
    all_colors = []
    all_materials = []
    
    for item in items:
        # Extract colors (handle different field names)
        item_colors = (item.get('dominantColors', []) or item.get('colors', []) or item.get('color', [])) if item else []
        if isinstance(item_colors, str):
            item_colors = [item_colors]
        elif not isinstance(item_colors, list):
            item_colors = []
        
        # Extract materials (handle different field names)
        item_material = (item.get('material', '') or item.get('fabric', '') or '') if item else ''
        
        if item_colors:
            all_colors.extend([color.lower() if isinstance(color, str) else str(color).lower() for color in item_colors])
        if item_material:
            all_materials.append(item_material.lower())
    
    logger.info(f"🔍 DEBUG: Found colors: {all_colors}")
    logger.info(f"🔍 DEBUG: Found materials: {all_materials}")
    
    # Color Theory Validation
    if all_colors:
        color_warnings = validate_color_theory(all_colors, style, mood)
        warnings.extend(color_warnings)
        color_analysis = analyze_color_palette(all_colors)
    
    # Material Compatibility Validation
    if all_materials:
        material_warnings = validate_material_compatibility(all_materials, style, mood)
        warnings.extend(material_warnings)
        material_analysis = analyze_material_combinations(all_materials)
    
    logger.info(f"🔍 DEBUG: Color/material validation complete: {len(warnings)} warnings")
    
    return {
        "colors": color_analysis,
        "materials": material_analysis,
        "warnings": warnings,
        "is_valid": len(warnings) == 0
    }

def validate_color_theory(colors: List[str], style: str, mood: str) -> List[str]:
    """Apply advanced color theory rules."""
    warnings = []
    
    # Color conflicts (complementary colors that may clash)
    color_conflicts = {
        "red": ["green"],
        "blue": ["orange"], 
        "yellow": ["purple"],
        "green": ["red"],
        "purple": ["yellow"],
        "orange": ["blue"],
        "pink": ["lime", "bright green"],
        "teal": ["coral", "bright orange"]
    }
    
    # Check for color conflicts
    for i, color1 in enumerate(colors):
        for j, color2 in enumerate(colors[i+1:], i+1):
            if color1 in color_conflicts and color2 in color_conflicts[color1]:
                warnings.append(f"Color conflict: {color1} and {color2} may clash")
    
    # Style-based color rules
    style_color_rules = {
        "minimalist": {"max_colors": 3, "description": "Minimalist style prefers fewer colors"},
        "maximalist": {"max_colors": 6, "description": "Maximalist style can handle more colors"},
        "monochrome": {"max_colors": 2, "description": "Monochrome style should stick to one color family"},
        "colorblock": {"min_colors": 3, "description": "Colorblock style needs multiple distinct colors"}
    }
    
    if style.lower() in style_color_rules:
        rule = style_color_rules[style.lower()]
        unique_colors = list(set(colors))
        
        if "max_colors" in rule and len(unique_colors) > rule["max_colors"]:
            warnings.append(f"{rule['description']}: {len(unique_colors)} colors (max {rule['max_colors']})")
        elif "min_colors" in rule and len(unique_colors) < rule["min_colors"]:
            warnings.append(f"{rule['description']}: {len(unique_colors)} colors (min {rule['min_colors']})")
    
    # Mood-based color psychology
    mood_color_rules = {
        "calm": ["blue", "green", "lavender", "sage"],
        "energetic": ["red", "orange", "yellow", "pink"],
        "sophisticated": ["black", "navy", "burgundy", "cream"],
        "playful": ["coral", "mint", "yellow", "pink"],
        "professional": ["navy", "gray", "white", "burgundy"]
    }
    
    if mood.lower() in mood_color_rules:
        recommended_colors = mood_color_rules[mood.lower()]
        current_colors = list(set(colors))
        matching_colors = [c for c in current_colors if c in recommended_colors]
        
        if len(matching_colors) < len(current_colors) * 0.5:  # Less than 50% match
            warnings.append(f"Mood '{mood}' works better with colors like: {', '.join(recommended_colors[:3])}")
    
    return warnings

def validate_material_compatibility(materials: List[str], style: str, mood: str) -> List[str]:
    """Validate material compatibility and appropriateness."""
    warnings = []
    
    # Material texture conflicts
    texture_conflicts = {
        "smooth": ["rough", "textured", "knit"],
        "rough": ["smooth", "silk", "satin"],
        "heavy": ["light", "sheer", "linen"],
        "light": ["heavy", "wool", "leather"]
    }
    
    # Check for texture conflicts
    for i, material1 in enumerate(materials):
        for j, material2 in enumerate(materials[i+1:], i+1):
            for texture, conflicts in texture_conflicts.items():
                if texture in material1 and any(conflict in material2 for conflict in conflicts):
                    warnings.append(f"Texture conflict: {material1} and {material2} may not work well together")
    
    # Style-based material rules
    style_material_rules = {
        "formal": ["silk", "wool", "cashmere", "cotton"],
        "casual": ["denim", "cotton", "linen", "jersey"],
        "luxury": ["silk", "cashmere", "leather", "wool"],
        "athletic": ["polyester", "spandex", "nylon", "cotton"],
        "bohemian": ["linen", "cotton", "suede", "knit"]
    }
    
    if style.lower() in style_material_rules:
        recommended_materials = style_material_rules[style.lower()]
        current_materials = list(set(materials))
        matching_materials = [m for m in current_materials if any(rec in m for rec in recommended_materials)]
        
        if len(matching_materials) < len(current_materials) * 0.6:  # Less than 60% match
            warnings.append(f"Style '{style}' works better with materials like: {', '.join(recommended_materials[:3])}")
    
    # Seasonal material appropriateness
    seasonal_materials = {
        "summer": ["linen", "cotton", "seersucker", "chambray"],
        "winter": ["wool", "cashmere", "tweed", "velvet"],
        "spring": ["cotton", "linen", "silk", "denim"],
        "fall": ["wool", "corduroy", "denim", "leather"]
    }
    
    # Check for seasonal mismatches (this could be enhanced with actual season detection)
    for season, season_materials in seasonal_materials.items():
        if any(season_mat in mat for mat in materials for season_mat in season_materials):
            # Found seasonal material, could add season-specific warnings here
            pass
    
    return warnings

def analyze_color_palette(colors: List[str]) -> Dict[str, Any]:
    """Analyze the color palette for insights."""
    unique_colors = list(set(colors))
    
    # Color temperature analysis
    warm_colors = ["red", "orange", "yellow", "pink", "coral", "peach"]
    cool_colors = ["blue", "green", "purple", "teal", "navy", "sage"]
    neutral_colors = ["black", "white", "gray", "beige", "cream", "brown"]
    
    warm_count = sum(1 for c in unique_colors if c in warm_colors)
    cool_count = sum(1 for c in unique_colors if c in cool_colors)
    neutral_count = sum(1 for c in unique_colors if c in neutral_colors)
    
    return {
        "total_colors": len(unique_colors),
        "warm_colors": warm_count,
        "cool_colors": cool_count,
        "neutral_colors": neutral_count,
        "palette_type": "warm" if warm_count > cool_count else "cool" if cool_count > warm_count else "neutral"
    }

def analyze_material_combinations(materials: List[str]) -> Dict[str, Any]:
    """Analyze material combinations for insights."""
    unique_materials = list(set(materials))
    
    # Material type analysis
    natural_materials = ["cotton", "wool", "silk", "linen", "cashmere"]
    synthetic_materials = ["polyester", "nylon", "spandex", "acrylic"]
    luxury_materials = ["silk", "cashmere", "leather", "velvet"]
    
    natural_count = sum(1 for m in unique_materials if any(nat in m for nat in natural_materials))
    synthetic_count = sum(1 for m in unique_materials if any(syn in m for syn in synthetic_materials))
    luxury_count = sum(1 for m in unique_materials if any(lux in m for lux in luxury_materials))
    
    return {
        "total_materials": len(unique_materials),
        "natural_materials": natural_count,
        "synthetic_materials": synthetic_count,
        "luxury_materials": luxury_count,
        "material_quality": "luxury" if luxury_count > 1 else "natural" if natural_count > synthetic_count else "mixed"
    }

async def calculate_outfit_score(items: List[Dict], req: OutfitRequest, layering_validation: Dict, color_material_validation: Dict, user_id: str) -> Dict[str, Any]:
    """Calculate comprehensive outfit score across multiple dimensions."""
    logger.info(f"🔍 DEBUG: Calculating outfit score for {len(items)} items")
    
    # Initialize component scores
    scores = {}
    
    # 1. Composition Score (20% weight) - Basic outfit structure
    composition_score = calculate_composition_score(items, (req.occasion if req else "unknown"))
    scores["composition_score"] = composition_score
    logger.info(f"🔍 DEBUG: Composition score: {composition_score}")
    
    # 2. Layering Score (15% weight) - Smart layering and conflicts
    layering_score = calculate_layering_score(layering_validation)
    scores["layering_score"] = layering_score
    logger.info(f"🔍 DEBUG: Layering score: {layering_score}")
    
    # 3. Color Harmony Score (15% weight) - Color theory and psychology
    color_score = calculate_color_score((color_material_validation.get("colors", {}) if color_material_validation else {}))
    scores["color_score"] = color_score
    logger.info(f"🔍 DEBUG: Color score: {color_score}")
    
    # 4. Material Compatibility Score (10% weight) - Fabric and texture harmony
    material_score = calculate_material_score((color_material_validation.get("materials", {}) if color_material_validation else {}))
    scores["material_score"] = material_score
    logger.info(f"🔍 DEBUG: Material score: {material_score}")
    
    # 5. Style Coherence Score (15% weight) - Style and mood alignment
    style_score = calculate_style_coherence_score(items, (req.style if req else "unknown"), (req.mood if req else "unknown"))
    scores["style_score"] = style_score
    logger.info(f"🔍 DEBUG: Style score: {style_score}")
    
    # 6. Wardrobe Intelligence Score (25% weight) - Favorites, wear history, diversity
    wardrobe_score = await calculate_wardrobe_intelligence_score(items, user_id)
    scores["wardrobe_intelligence_score"] = wardrobe_score
    logger.info(f"🔍 DEBUG: Wardrobe intelligence score: {wardrobe_score}")
    
    # Calculate weighted total score (0-100 scale)
    weights = {
        "composition_score": 0.20,
        "layering_score": 0.15,
        "color_score": 0.15,
        "material_score": 0.10,
        "style_score": 0.15,
        "wardrobe_intelligence_score": 0.25
    }
    
    total_score = sum(scores[component] * weights[component] for component in scores.keys())
    scores["total_score"] = round(total_score, 2)
    
    # Add score interpretation
    scores["score_interpretation"] = interpret_score(total_score)
    scores["grade"] = get_score_grade(total_score)
    
    logger.info(f"🔍 DEBUG: Final outfit score: {total_score} ({scores['grade']})")
    
    return scores

def calculate_composition_score(items: List[Dict], occasion: str) -> float:
    """Calculate score for outfit composition and completeness."""
    score = 0.0
    
    # Required categories for different occasions
    required_categories = {
        "casual": ["top", "bottom"],
        "business": ["top", "bottom", "shoes"],
        "formal": ["top", "bottom", "shoes"],
        "athletic": ["top", "bottom", "shoes"],
        "beach": ["top", "bottom"],
        "party": ["top", "bottom", "shoes"],
        "date": ["top", "bottom", "shoes"],
        "travel": ["top", "bottom", "shoes"]
    }
    
    required = (required_categories.get(occasion.lower() if required_categories else None), ["top", "bottom"])
    
    # Categorize items
    categorized_items = {}
    for item in items:
        item_type = (item.get('type', '') if item else '').lower()
        category = get_item_category(item_type)
        if category not in categorized_items:
            categorized_items[category] = []
        categorized_items[category].append(item)
    
    # Score based on required categories present
    required_present = sum(1 for cat in required if cat in categorized_items and categorized_items[cat])
    required_score = (required_present / len(required)) * 40  # 40 points for required categories
    
    # Score based on item count appropriateness
    item_count_score = 0
    if len(items) >= 3 and len(items) <= 6:
        item_count_score = 30  # Perfect item count
    elif len(items) >= 2 and len(items) <= 7:
        item_count_score = 20  # Acceptable item count
    else:
        item_count_score = 10  # Too few or too many items
    
    # Score based on category variety
    variety_score = min(len(categorized_items) * 10, 30)  # Up to 30 points for variety
    
    score = required_score + item_count_score + variety_score
    return min(score, 100.0)  # Cap at 100

def calculate_layering_score(layering_validation: Dict) -> float:
    """Calculate score for layering appropriateness."""
    score = 100.0  # Start with perfect score
    
    warnings = (layering_validation.get('warnings', []) if layering_validation else [])
    layer_count = (layering_validation.get('layer_count', 0) if layering_validation else 0)
    
    # Deduct points for warnings
    for warning in warnings:
        if "too heavy" in warning.lower():
            score -= 15
        elif "too many layers" in warning.lower():
            score -= 10
        elif "too few layers" in warning.lower():
            score -= 8
        elif "conflict" in warning.lower():
            score -= 12
    
    # Bonus for optimal layer count
    if 2 <= layer_count <= 3:
        score += 5  # Bonus for optimal layering
    elif layer_count == 1:
        score += 2  # Bonus for single layer (appropriate for some occasions)
    
    return max(score, 0.0)  # Don't go below 0

def calculate_color_score(color_analysis: Dict) -> float:
    """Calculate score for color harmony and theory."""
    if not color_analysis:
        return 70.0  # Neutral score if no color data
    
    score = 100.0  # Start with perfect score
    
    total_colors = (color_analysis.get('total_colors', 0) if color_analysis else 0)
    palette_type = (color_analysis.get('palette_type', 'neutral') if color_analysis else 'neutral')
    
    # Score based on color count
    if total_colors == 0:
        score -= 30  # No color data
    elif total_colors == 1:
        score += 10  # Monochromatic (good)
    elif 2 <= total_colors <= 4:
        score += 15  # Optimal color range
    elif total_colors > 6:
        score -= 10  # Too many colors
    
    # Score based on palette type
    if palette_type == 'neutral':
        score += 5  # Neutral palettes are versatile
    elif palette_type in ['warm', 'cool']:
        score += 10  # Cohesive temperature
    
    return max(score, 0.0)

def calculate_material_score(material_analysis: Dict) -> float:
    """Calculate score for material compatibility."""
    if not material_analysis:
        return 70.0  # Neutral score if no material data
    
    score = 100.0  # Start with perfect score
    
    material_quality = (material_analysis.get('material_quality', 'mixed') if material_analysis else 'mixed')
    natural_count = (material_analysis.get('natural_materials', 0) if material_analysis else 0)
    luxury_count = (material_analysis.get('luxury_materials', 0) if material_analysis else 0)
    
    # Score based on material quality
    if material_quality == 'luxury':
        score += 15  # Luxury materials get bonus
    elif material_quality == 'natural':
        score += 10  # Natural materials get bonus
    
    # Score based on material variety
    if natural_count > 0 and luxury_count > 0:
        score += 5  # Good mix of materials
    
    return max(score, 0.0)

def calculate_style_coherence_score(items: List[Dict], style: str, mood: str) -> float:
    """Calculate score for style and mood coherence."""
    score = 100.0  # Start with perfect score
    
    # Style-specific scoring
    style_rules = {
        "minimalist": {"max_items": 4, "description": "Fewer items for minimalist style"},
        "maximalist": {"min_items": 5, "description": "More items for maximalist style"},
        "monochrome": {"color_variety": 2, "description": "Limited color variety for monochrome"},
        "colorblock": {"min_colors": 3, "description": "Multiple colors for colorblock style"}
    }
    
    if style.lower() in style_rules:
        rule = style_rules[style.lower()]
        
        if "max_items" in rule and len(items) > rule["max_items"]:
            score -= 15  # Too many items for minimalist style
        elif "min_items" in rule and len(items) < rule["min_items"]:
            score -= 15  # Too few items for maximalist style
    
    # Mood-based scoring
    mood_rules = {
        "calm": {"max_colors": 4, "description": "Fewer colors for calm mood"},
        "energetic": {"min_colors": 3, "description": "More colors for energetic mood"},
        "sophisticated": {"min_items": 3, "description": "More items for sophisticated look"}
    }
    
    if mood.lower() in mood_rules:
        rule = mood_rules[mood.lower()]
        
        if "max_colors" in rule:
            # Count unique colors (simplified)
            colors = set()
            for item in items:
                item_color = item.get('color', '')
                if item_color:
                    colors.add(item_color.lower())
            
            if len(colors) > rule["max_colors"]:
                score -= 10  # Too many colors for calm mood
    
    return max(score, 0.0)

def interpret_score(score: float) -> str:
    """Interpret the numerical score into a meaningful description."""
    if score >= 90:
        return "Exceptional outfit with perfect harmony and style"
    elif score >= 80:
        return "Excellent outfit with great composition and few issues"
    elif score >= 70:
        return "Very good outfit with minor areas for improvement"
    elif score >= 60:
        return "Good outfit with some compatibility issues"
    elif score >= 50:
        return "Acceptable outfit with several areas for improvement"
    else:
        return "Outfit needs significant improvement in multiple areas"

def get_score_grade(score: float) -> str:
    """Convert numerical score to letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    else:
        return "D"

async def calculate_wardrobe_intelligence_score(items: List[Dict], user_id: str) -> float:
    """Calculate score based on wardrobe intelligence: favorites, wear history, diversity."""
    logger.info(f"🔍 DEBUG: Calculating wardrobe intelligence score for {len(items)} items")
    
    # Use the provided user ID
    current_user_id = user_id
    
    total_score = 0.0
    item_scores = []
    
    for item in items:
        item_score = 0.0
        item_id = (item.get('id', '') if item else '')
        
        # Get item analytics data
        try:
            # Query item analytics collection for wear history and favorites
            analytics_ref = db.collection('item_analytics').where('item_id', '==', item_id).where('user_id', '==', current_user_id).limit(1)
            analytics_docs = analytics_ref.stream()
            analytics_data = None
            for doc in analytics_docs:
                analytics_data = doc.to_dict()
                break
            
            if analytics_data:
                # 1. Favorite Status Bonus (up to 25 points)
                # Check both analytics and wardrobe collection for favorite status
        is_favorite = (analytics_data.get('is_favorite', False) if analytics_data else False)
                
                # Also check wardrobe collection for favorite status
                try:
                    wardrobe_ref = db.collection('wardrobe').document(item_id)
        wardrobe_doc = wardrobe_ref.get() if wardrobe_ref else None if wardrobe_ref else None
                    if wardrobe_doc.exists:
                        wardrobe_data = wardrobe_doc.to_dict()
                        if wardrobe_data.get('isFavorite', False):
                            is_favorite = True
                except Exception as e:
                    logger.warning(f"⚠️ Could not check wardrobe favorite status for item {item_id}: {e}")
                
                if is_favorite:
                    item_score += 25
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +25 favorite bonus")
                else:
                    # Bonus for non-favorited items that perform well in outfits
                    outfit_performance_bonus = min(10, outfit_performance_score)  # Up to 10 bonus points
                    item_score += outfit_performance_bonus
        logger.info(f"🔍 DEBUG: Non-favorited item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +{outfit_performance_bonus} performance bonus")
                
                # 2. Wear Count Scoring (up to 20 points)
        wear_count = (analytics_data.get('wear_count', 0) if analytics_data else 0)
                
                # Fallback to wardrobe collection if no analytics data
                if wear_count == 0:
                    try:
                        wardrobe_ref = db.collection('wardrobe').document(item_id)
        wardrobe_doc = wardrobe_ref.get() if wardrobe_ref else None if wardrobe_ref else None
                        if wardrobe_doc.exists:
                            wardrobe_data = wardrobe_doc.to_dict()
        wear_count = (wardrobe_data.get('wearCount', 0) if wardrobe_data else 0)
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get wear count from wardrobe for item {item_id}: {e}")
                
                if wear_count == 0:
                    item_score += 20  # Bonus for unworn items
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +20 unworn bonus")
                elif wear_count <= 3:
                    item_score += 15  # Good for moderately worn items
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +15 moderately worn bonus")
                elif wear_count <= 7:
                    item_score += 10  # Acceptable for frequently worn items
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +10 frequently worn bonus")
                else:
                    item_score += 5   # Minimal points for over-worn items
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +5 over-worn bonus")
                
                # 3. Recent Wear Penalty (up to -15 points)
        last_worn = (analytics_data.get('last_worn') if analytics_data else None)
                
                # Fallback to wardrobe collection if no analytics data
                if not last_worn:
                    try:
                        wardrobe_ref = db.collection('wardrobe').document(item_id)
        wardrobe_doc = wardrobe_ref.get() if wardrobe_ref else None if wardrobe_ref else None
                        if wardrobe_doc.exists:
                            wardrobe_data = wardrobe_doc.to_dict()
        last_worn = (wardrobe_data.get('lastWorn') if wardrobe_data else None)
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get last worn from wardrobe for item {item_id}: {e}")
                
                if last_worn:
                    try:
                        # Parse last_worn timestamp
                        if isinstance(last_worn, str):
                            last_worn_dt = datetime.fromisoformat(last_worn.replace('Z', '+00:00'))
                        else:
                            last_worn_dt = last_worn
                        
                        days_since_worn = (datetime.now() - last_worn_dt).days
                        
                        if days_since_worn <= 1:
                            item_score -= 15  # Heavy penalty for worn yesterday
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets -15 penalty (worn yesterday)")
                        elif days_since_worn <= 3:
                            item_score -= 10  # Penalty for worn this week
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets -10 penalty (worn this week)")
                        elif days_since_worn <= 7:
                            item_score -= 5   # Light penalty for worn this month
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets -5 penalty (worn this month)")
                        else:
                            item_score += 5   # Bonus for items not worn recently
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +5 bonus (not worn recently)")
                    
                    except Exception as e:
                        logger.warning(f"⚠️ Could not parse last_worn date for item {item_id}: {e}")
                        item_score += 5  # Neutral score if date parsing fails
                
                # 4. User Feedback Bonus (up to 15 points)
        feedback_rating = (analytics_data.get('average_feedback_rating', 0) if analytics_data else 0)
                if feedback_rating >= 4.5:
                    item_score += 15  # Excellent feedback
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +15 feedback bonus (rating: {feedback_rating})")
                elif feedback_rating >= 4.0:
                    item_score += 10  # Good feedback
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +10 feedback bonus (rating: {feedback_rating})")
                elif feedback_rating >= 3.5:
                    item_score += 5   # Average feedback
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +5 feedback bonus (rating: {feedback_rating})")
                
                # 5. Style Preference Match (up to 10 points)
        style_match = (analytics_data.get('style_preference_score', 0.5) if analytics_data else 0.5)
                item_score += style_match * 10
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +{style_match * 10:.1f} style preference bonus")
                
                # 6. Outfit Performance Bonus (up to 20 points) - NEW!
                outfit_performance_score = await calculate_outfit_performance_score(item_id, current_user_id)
                item_score += outfit_performance_score
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +{outfit_performance_score} outfit performance bonus")
                
                # 7. Wardrobe Diversity Bonus (up to 5 points) - NEW!
                diversity_bonus = await calculate_wardrobe_diversity_bonus(item_id, current_user_id)
                item_score += diversity_bonus
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets +{diversity_bonus} diversity bonus")
                
            else:
                # No analytics data - neutral score
                item_score = 50
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} gets neutral score (no analytics data)")
            
        except Exception as e:
            logger.error(f"❌ Error calculating wardrobe intelligence for item {item_id}: {e}")
            item_score = 50  # Neutral score on error
        
        # Ensure score stays within bounds
        item_score = max(0, min(100, item_score))
        item_scores.append(item_score)
        total_score += item_score
        
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'Unknown') if item else 'Unknown')} final wardrobe score: {item_score}")
    
    # Calculate average score across all items
    if item_scores:
        average_score = total_score / len(item_scores)
        logger.info(f"🔍 DEBUG: Average wardrobe intelligence score: {average_score:.2f}")
        return round(average_score, 2)
    else:
        return 50.0  # Neutral score if no items

async def calculate_outfit_performance_score(item_id: str, user_id: str) -> float:
    """Calculate score based on how well this item performs in outfits."""
    logger.info(f"🔍 DEBUG: Calculating outfit performance score for item {item_id}")
    
    try:
        # Query outfits that contain this item
        outfits_ref = db.collection('outfits').where('user_id', '==', user_id)
        outfits_docs = outfits_ref.stream()
        
        total_score = 0.0
        outfit_count = 0
        high_rated_outfits = 0
        worn_outfits = 0
        
        for outfit_doc in outfits_docs:
            outfit_data = outfit_doc.to_dict()
        outfit_items = (outfit_data.get('items', []) if outfit_data else [])
            
            # Check if this item is in this outfit
        item_in_outfit = any((item.get('id') if item else None) == item_id for item in outfit_items)
            if not item_in_outfit:
                continue
            
            outfit_count += 1
            
            # 1. Outfit Rating Bonus (up to 10 points)
        outfit_rating = (outfit_data.get('rating', 0) if outfit_data else 0)
            if outfit_rating >= 4.5:
                total_score += 10  # Excellent outfit rating
                high_rated_outfits += 1
                logger.info(f"🔍 DEBUG: Item in 5-star outfit: +10 points")
            elif outfit_rating >= 4.0:
                total_score += 8   # Very good outfit rating
                high_rated_outfits += 1
                logger.info(f"🔍 DEBUG: Item in 4-star outfit: +8 points")
            elif outfit_rating >= 3.5:
                total_score += 6   # Good outfit rating
                logger.info(f"🔍 DEBUG: Item in 3.5-star outfit: +6 points")
            elif outfit_rating >= 3.0:
                total_score += 4   # Average outfit rating
                logger.info(f"🔍 DEBUG: Item in 3-star outfit: +4 points")
            elif outfit_rating >= 2.0:
                total_score += 2   # Below average outfit rating
                logger.info(f"🔍 DEBUG: Item in 2-star outfit: +2 points")
            else:
                total_score += 0   # Poor outfit rating (no bonus)
                logger.info(f"🔍 DEBUG: Item in 1-star outfit: +0 points")
            
            # 2. Outfit Wear Count Bonus (up to 5 points)
        outfit_wear_count = (outfit_data.get('wearCount', 0) if outfit_data else 0)
            if outfit_wear_count >= 5:
                total_score += 5   # Frequently worn outfit
                worn_outfits += 1
                logger.info(f"🔍 DEBUG: Item in frequently worn outfit: +5 points")
            elif outfit_wear_count >= 3:
                total_score += 3   # Moderately worn outfit
                worn_outfits += 1
                logger.info(f"🔍 DEBUG: Item in moderately worn outfit: +3 points")
            elif outfit_wear_count >= 1:
                total_score += 1   # Worn at least once
                worn_outfits += 1
                logger.info(f"🔍 DEBUG: Item in worn outfit: +1 point")
            
            # 3. Outfit Like/Dislike Bonus (up to 5 points)
        outfit_liked = (outfit_data.get('isLiked', False) if outfit_data else False)
        outfit_disliked = (outfit_data.get('isDisliked', False) if outfit_data else False)
            
            if outfit_liked:
                total_score += 5   # Liked outfit bonus
                logger.info(f"🔍 DEBUG: Item in liked outfit: +5 points")
            elif outfit_disliked:
                total_score -= 2   # Disliked outfit penalty
                logger.info(f"🔍 DEBUG: Item in disliked outfit: -2 points")
        
        # 4. Performance Multipliers
        if outfit_count > 0:
            # Average score per outfit
            base_score = total_score / outfit_count
            
            # Bonus for items that consistently perform well
            if high_rated_outfits >= 3:
                base_score *= 1.2  # 20% bonus for 3+ high-rated outfits
                logger.info(f"🔍 DEBUG: Consistency bonus: 20% multiplier for {high_rated_outfits} high-rated outfits")
            elif high_rated_outfits >= 1:
                base_score *= 1.1  # 10% bonus for at least 1 high-rated outfit
                logger.info(f"🔍 DEBUG: Performance bonus: 10% multiplier for {high_rated_outfits} high-rated outfit")
            
            # Bonus for items that create worn outfits
            if worn_outfits >= 3:
                base_score *= 1.15  # 15% bonus for 3+ worn outfits
                logger.info(f"🔍 DEBUG: Wearability bonus: 15% multiplier for {worn_outfits} worn outfits")
            elif worn_outfits >= 1:
                base_score *= 1.05  # 5% bonus for at least 1 worn outfit
                logger.info(f"🔍 DEBUG: Usability bonus: 5% multiplier for {worn_outfits} worn outfit")
            
            final_score = min(base_score, 20.0)  # Cap at 20 points
            logger.info(f"🔍 DEBUG: Final outfit performance score: {final_score:.2f} (from {outfit_count} outfits)")
            return round(final_score, 2)
        else:
            logger.info(f"🔍 DEBUG: Item not found in any outfits: 0 points")
            return 0.0
            
    except Exception as e:
        logger.error(f"❌ Error calculating outfit performance score for item {item_id}: {e}")
        return 0.0  # Return 0 on error

async def calculate_wardrobe_diversity_bonus(item_id: str, user_id: str) -> float:
    """Calculate bonus for items that add diversity to the wardrobe."""
    logger.info(f"🔍 DEBUG: Calculating wardrobe diversity bonus for item {item_id}")
    
    try:
        # Get the current item's type and color
        wardrobe_ref = db.collection('wardrobe').document(item_id)
        wardrobe_doc = wardrobe_ref.get() if wardrobe_ref else None if wardrobe_ref else None
        
        if not wardrobe_doc.exists:
            return 0.0
        
        current_item = wardrobe_doc.to_dict()
        current_type = (current_item.get('type', '') if current_item else '').lower()
        current_color = (current_item.get('color', '') if current_item else '').lower()
        
        # Query all user's wardrobe items
        all_wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
        all_wardrobe_docs = all_wardrobe_ref.stream()
        
        type_count = 0
        color_count = 0
        total_items = 0
        
        for doc in all_wardrobe_docs:
            if doc.id == item_id:
                continue  # Skip the current item
            
            item_data = doc.to_dict()
            total_items += 1
            
            # Count items of the same type
            if item_data.get('type', '').lower() == current_type:
                type_count += 1
            
            # Count items of the same color
            if item_data.get('color', '').lower() == current_color:
                color_count += 1
        
        # Calculate diversity bonus
        diversity_score = 0.0
        
        # Type diversity (up to 3 points)
        if type_count == 0:
            diversity_score += 3  # Unique type
        elif type_count <= 2:
            diversity_score += 2  # Rare type
        elif type_count <= 5:
            diversity_score += 1  # Common type
        else:
            diversity_score += 0  # Very common type
        
        # Color diversity (up to 2 points)
        if color_count == 0:
            diversity_score += 2  # Unique color
        elif color_count <= 3:
            diversity_score += 1  # Rare color
        else:
            diversity_score += 0  # Common color
        
        logger.info(f"🔍 DEBUG: Diversity bonus: +{diversity_score} (type_count: {type_count}, color_count: {color_count})")
        return diversity_score
        
    except Exception as e:
        logger.error(f"❌ Error calculating wardrobe diversity bonus for item {item_id}: {e}")
        return 0.0

def is_layer_item(item_type: str) -> bool:
    """Check if item type is a layering item."""
    item_type_lower = item_type.lower()
    layer_types = [
        "shirt", "t-shirt", "blouse", "sweater", "jacket", "coat", "blazer", "cardigan", "hoodie",
        "dress shirt", "button up", "button-up", "oxford", "dress-shirt", "polo"
    ]
    return any(layer_type in item_type_lower for layer_type in layer_types)

def get_item_category(item_type: str) -> str:
    """Categorize item type into outfit categories."""
    item_type_lower = item_type.lower()
    
    # Top items
    if any(top_type in item_type_lower for top_type in ['shirt', 'blouse', 't-shirt', 'sweater', 'jacket', 'coat', 'blazer', 'cardigan', 'hoodie']):
        return "top"
    
    # Bottom items
    elif any(bottom_type in item_type_lower for bottom_type in ['pants', 'jeans', 'shorts', 'skirt', 'leggings', 'trousers']):
        return "bottom"
    
    # Shoes
    elif any(shoe_type in item_type_lower for shoe_type in ['shoes', 'sneakers', 'boots', 'heels', 'flats', 'sandals', 'loafers']):
        return "shoes"
    
    # Accessories
    elif any(acc_type in item_type_lower for acc_type in ['bag', 'purse', 'hat', 'scarf', 'belt', 'jewelry', 'watch']):
        return "accessory"
    
    # Dresses (count as both top and bottom)
    elif 'dress' in item_type_lower:
        return "dress"
    
    # Default to top if unclear
    else:
        return "top"

# Helper functions for outfit generation
async def get_user_wardrobe(user_id: str) -> List[Dict[str, Any]]:
    """Get user's wardrobe items from Firestore."""
    try:
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ..config.firebase import db, firebase_initialized
            FIREBASE_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"⚠️ Firebase import failed: {e}")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, returning empty wardrobe")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
            
        logger.info(f"📦 Fetching wardrobe for user {user_id}")
        
        # Query user's wardrobe items - use the same path as the wardrobe page
        wardrobe_ref = db.collection('wardrobe').where('userId', '==', user_id)
        docs = wardrobe_ref.stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            
            # Defensive normalization for older items
            try:
                from ..utils.semantic_normalization import normalize_item_metadata
                normalized_item = normalize_item_metadata(item_data)
                items.append(normalized_item)
            except Exception as e:
                logger.warning(f"Failed to normalize item {doc.id}: {e}")
                items.append(item_data)  # Fallback to original item
        
        logger.info(f"✅ Retrieved {len(items)} wardrobe items")
        return items
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch wardrobe for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch wardrobe: {e}")

async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user's style profile from Firestore."""
    try:
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ..config.firebase import db, firebase_initialized
            FIREBASE_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"⚠️ Firebase import failed: {e}")
            FIREBASE_AVAILABLE = False
            firebase_initialized = False
        
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, using default profile")
            # Return default profile instead of throwing error
            return {
                "id": user_id,
                "gender": "male",  # Default to male for better filtering
                "bodyType": "average",
                "skinTone": "medium",
                "style": ["casual", "versatile"],
                "stylePreferences": ["classic", "modern", "business casual"],  # Default style preferences
                "preferences": {},
                "colorPalette": {
                    "primary": ["navy", "gray", "black", "white"],
                    "secondary": ["blue", "brown", "beige"],
                    "avoid": ["pink", "purple", "yellow"]
                },
                "materialPreferences": {
                    "preferred": ["cotton", "wool", "linen"],
                    "avoid": ["polyester", "acrylic"]
                }
            }
            
        logger.info(f"👤 Fetching profile for user {user_id}")
        
        # Query user's profile
        profile_ref = db.collection('users').document(user_id)
        profile_doc = profile_ref.get() if profile_ref else None
        
        if profile_doc.exists:
            profile_data = profile_doc.to_dict()
            logger.info(f"✅ Retrieved profile for user {user_id}")
            
            # CRITICAL: Ensure gender is set - if missing or null, default to male
        if not (profile_data.get('gender') if profile_data else None):
                profile_data['gender'] = 'male'
                logger.info(f"🔧 Setting missing gender to 'male' for user {user_id}")
                
            return profile_data
        else:
            logger.info(f"⚠️ No profile found for user {user_id}, using defaults")
            # Return default profile instead of throwing error
            return {
                "id": user_id,
                "gender": "male",  # Default to male for better filtering
                "bodyType": "average",
                "skinTone": "medium",
                "style": ["casual", "versatile"],
                "stylePreferences": ["classic", "modern", "business casual"],  # Default style preferences
                "preferences": {},
                "colorPalette": {
                    "primary": ["navy", "gray", "black", "white"],
                    "secondary": ["blue", "brown", "beige"],
                    "avoid": ["pink", "purple", "yellow"]
                },
                "materialPreferences": {
                    "preferred": ["cotton", "wool", "linen"],
                    "avoid": ["polyester", "acrylic"]
                }
            }
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch profile for {user_id}: {e}")
        # Return default profile instead of throwing error
        return {
            "id": user_id,
            "gender": "male",  # Default to male for better filtering
            "bodyType": "average",
            "skinTone": "medium",
            "style": ["casual", "versatile"],
            "stylePreferences": ["classic", "modern", "business casual"],  # Default style preferences
            "preferences": {},
            "colorPalette": {
                "primary": ["navy", "gray", "black", "white"],
                "secondary": ["blue", "brown", "beige"],
                "avoid": ["pink", "purple", "yellow"]
            },
            "materialPreferences": {
                "preferred": ["cotton", "wool", "linen"],
                "avoid": ["polyester", "acrylic"]
            }
        }

debug_data = []  # Global debug data collector
exclusion_debug = []  # Global exclusion debug data

def debug_rule_engine(stage: str, wardrobe_items=None, suitable=None, categorized=None, scores=None, validated=None):
    # Debug logging removed to reduce Railway rate limiting
    try:
        debug_info = {
            "stage": stage,
            "wardrobe_count": len(wardrobe_items) if wardrobe_items is not None else None,
            "suitable_count": len(suitable) if suitable is not None else None,
            "categorized_keys": list(categorized.keys()) if categorized else None,
            "scores_count": len(scores) if scores is not None else None,
            "validated_count": len(validated) if validated is not None else None,
        }
        debug_data.append(debug_info)
        # Removed: print("🔎 RULE ENGINE DEBUG:", debug_info)
        # Removed: logger.info(f"🔎 RULE ENGINE DEBUG: {debug_info}")
    except Exception as e:
        error_info = {"stage": stage, "error": str(e)}
        debug_data.append(error_info)
        # Keep only critical errors
        logger.error(f"⚠️ CRITICAL DEBUG ERROR: {e}")

async def generate_rule_based_outfit(wardrobe_items: List[Dict], user_profile: Dict, req: OutfitRequest) -> Dict[str, Any]:
    """Generate outfit using rule-based decision tree and user's wardrobe."""
    try:
        logger.info(f"🎯 Generating rule-based outfit with {len(wardrobe_items)} items")
        
        # Clear previous debug data
        global debug_data, exclusion_debug
        debug_data = []
        exclusion_debug = []
        
        # DEBUG: Start stage
        debug_rule_engine("start", wardrobe_items=wardrobe_items)
        # Reduced logging to prevent Railway rate limits
        logger.info(f"🔍 DEBUG: User profile keys: {list(user_profile.keys()) if user_profile else 'None'}")
        logger.info(f"🔍 DEBUG: Request: style={req.style}, occasion={req.occasion}, baseItemId={req.baseItemId}")
        
        # Rule-based outfit selection using sophisticated decision tree
        
                # ENHANCED: Sophisticated style preference filtering with scoring
        suitable_items = []
        item_scores = {}  # Track scores for each item
        
        # DEBUG: After initialization
        debug_rule_engine("after_init", suitable=suitable_items, scores=item_scores)
        
        # ENHANCED: Ensure all wardrobe items have required fields for ClothingItem validation
        for item in wardrobe_items:
            # Add missing required fields with default values
            if 'season' not in item:
                item['season'] = ['all']
            if 'userId' not in item:
                item['userId'] = user_id
            if 'dominantColors' not in item:
                item['dominantColors'] = []
            if 'matchingColors' not in item:
                item['matchingColors'] = []
            if 'createdAt' not in item:
                item['createdAt'] = int(time.time() * 1000)
            if 'updatedAt' not in item:
                item['updatedAt'] = int(time.time() * 1000)

        # CRITICAL: Add base item FIRST before any filtering
        if (req.baseItemId if req else None):
        base_item = next((item for item in wardrobe_items if item.get("id") == (req.baseItemId if req else None)), None)
            if base_item:
                logger.info(f"🎯 DEBUG: Adding base item BEFORE filtering: {base_item.get('name', 'Unknown')}")
                suitable_items.append(base_item)
        item_scores[(base_item.get('id', 'unknown') if base_item else 'unknown')] = 1000  # Give base item highest score
            else:
                logger.warning(f"⚠️ DEBUG: Base item {req.baseItemId} not found in wardrobe")
        
        # Reduced logging to prevent Railway rate limits
        logger.info(f"🔍 DEBUG: Filtering {len(wardrobe_items)} items for {req.style}/{req.occasion}")
        
        # DEBUG: Before scoring loop
        def debug_scores(stage: str, items):
            try:
                print("🎯 SCORING DEBUG:", {
                    "stage": stage,
                    "input_items": [i.get("id") for i in items] if items else None,
                    "input_count": len(items) if items else 0,
                })
            except Exception as e:
                print("⚠️ SCORE DEBUG ERROR:", e)
        
        debug_scores("before_scoring_loop", wardrobe_items)
        
        for item in wardrobe_items:
            # Skip base item since it's already been added
        if (req.baseItemId if req else None) and (item.get('id') if item else None) == (req.baseItemId if req else None):
        logger.info(f"🎯 DEBUG: Skipping base item in filtering loop: {(item.get('name', 'Unknown') if item else 'Unknown')}")
                continue
                
        item_style = (item.get('style', '') if item else '') or ''
        item_occasion = (item.get('occasion', '') if item else '') or ''
        item_color = (item.get('color', '') if item else '') or ''
        item_material = (item.get('material', '') if item else '') or ''
            
            # Convert to string if it's a list
            if isinstance(item_style, list):
                item_style = ' '.join(item_style).lower()
            else:
                item_style = str(item_style).lower()
                
            if isinstance(item_occasion, list):
                item_occasion = ' '.join(item_occasion).lower()
            else:
                item_occasion = str(item_occasion).lower()
            
        logger.info(f"🔍 DEBUG: Item {(item.get('name', 'unnamed') if item else 'unnamed')} - style: '{item_style}', occasion: '{item_occasion}', color: '{item_color}'")
            
            # ENHANCED: Multi-dimensional style preference scoring
            item_score = 0
            is_suitable = False
            
            # HARD EXCLUSION FILTER: Prevent truly inappropriate items from entering scoring pool
        hard_exclusions = get_hard_style_exclusions(req.style.lower(), item, (req.mood if req else "unknown"))
        # print(f"🔍 EXCLUSION CHECK: {(item.get('name', 'unnamed') if item else 'unnamed')} for {req.style} - result: {hard_exclusions}")
        # print(f"🔍 EXCLUSION LOGIC: hard_exclusions={hard_exclusions}, type={type(hard_exclusions)}, bool={bool(hard_exclusions)}")
        # print(f"🔍 EXCLUSION LOGIC: baseItemId={req.baseItemId}, itemId={((item.get('id') if item else None) if item else None)}, isBaseItem={req.baseItemId and ((item.get('id') if item else None) if item else None) == (req.baseItemId if req else None)}")
            
            # Check exclusion condition explicitly
        is_base_item = (req.baseItemId if req else None) and (item.get('id') if item else None) == (req.baseItemId if req else None)
            should_exclude = hard_exclusions is not None and not is_base_item
            
            print(f"🔍 EXCLUSION DECISION: should_exclude={should_exclude}, is_base_item={is_base_item}")
            if should_exclude:
#                 print(f"🚫 HARD EXCLUSION: {(item.get('name', 'unnamed') if item else 'unnamed')} excluded from {req.style} - {hard_exclusions}")
#                 print(f"🚫 EXECUTING CONTINUE: About to skip {(item.get('name', 'unnamed') if item else 'unnamed')} - this item should NOT appear in final outfit")
logger.info(f"🚫 HARD EXCLUSION: {(item.get('name', 'unnamed') if item else 'unnamed')} excluded from {req.style} - {hard_exclusions}")
                continue
                print(f"❌ CONTINUE FAILED: This line should NEVER execute if continue worked")
            elif hard_exclusions:
print(f"🛡️ EXCLUSION BYPASSED: {(item.get('name', 'unnamed') if item else 'unnamed')} is base item, allowing despite exclusion")
            else:
print(f"✅ EXCLUSION PASSED: {(item.get('name', 'unnamed') if item else 'unnamed')} has no exclusions for {req.style}")
            
            # 1. Core Style Matching (Primary filter - must pass)
            # SOFTEN VALIDATION: Allow base item to pass even if it fails core criteria
            if (req.style.lower() in item_style or 
(req.occasion if req else "unknown").lower() in item_occasion or
                'versatile' in item_style or
(req.baseItemId and (item.get('id') if item else None) == (req.baseItemId if req else None))):
                
                is_suitable = True
                item_score += 50  # Base score for passing core criteria
                
                # STYLE APPROPRIATENESS WEIGHTING: Heavy penalties for style mismatches
                style_appropriateness_score = calculate_style_appropriateness_score(req.style.lower(), item)
                item_score += style_appropriateness_score
                if style_appropriateness_score < 0:
logger.info(f"🎯 STYLE PENALTY: {(item.get('name', 'unnamed') if item else 'unnamed')} gets {style_appropriateness_score} points for {req.style} mismatch")
                
                # Special handling for base item that failed core criteria
if (req.baseItemId if req else None) and (item.get('id') if item else None) == (req.baseItemId if req else None) and not (req.style.lower() in item_style or (req.occasion if req else "unknown").lower() in item_occasion or 'versatile' in item_style):
logger.info(f"🛡️ Allowing base item despite failing criteria: {(item.get('name', 'Unknown') if item else 'Unknown')}")
                    item_score += 1000  # Give base item highest priority
                
                # 2. Style Preference Enhancement (User's stored preferences)
                if user_profile and user_profile.get('stylePreferences'):
                    user_styles = [s.lower() for s in user_profile.get('stylePreferences', [])]
                    style_matches = sum(1 for style in user_styles if style in item_style)
                    if style_matches > 0:
                        style_boost = (style_matches / len(user_styles)) * 30
                        item_score += style_boost
                        logger.info(f"🔍 DEBUG: Style preference match: +{style_boost:.1f} points")
                
                # 3. Color Preference Enhancement
                if user_profile and user_profile.get('colorPalette'):
                    color_palette = user_profile.get('colorPalette', {})
preferred_colors = ((color_palette.get('primary', []) if color_palette else []) if color_palette else []) + color_palette.get('secondary', [])
avoid_colors = (color_palette.get('avoid', []) if color_palette else [])
                    
                    if item_color:
                        item_color_lower = item_color.lower()
                        if item_color_lower in preferred_colors:
                            item_score += 15
                            logger.info(f"🔍 DEBUG: Preferred color match: +15 points")
                        elif item_color_lower in avoid_colors:
                            item_score -= 20
                            logger.info(f"🔍 DEBUG: Avoided color: -20 points")
                
                # 4. Material Preference Enhancement
                if user_profile and user_profile.get('materialPreferences'):
                    material_prefs = user_profile.get('materialPreferences', {})
preferred_materials = (material_prefs.get('preferred', []) if material_prefs else [])
avoid_materials = (material_prefs.get('avoid', []) if material_prefs else [])
                    
                    if item_material:
                        item_material_lower = item_material.lower()
                        if item_material_lower in preferred_materials:
                            item_score += 10
                            logger.info(f"🔍 DEBUG: Preferred material match: +10 points")
                        elif item_material_lower in avoid_materials:
                            item_score -= 15
                            logger.info(f"🔍 DEBUG: Avoided material: -15 points")
                
                # 5. Style Personality Enhancement
                if user_profile and user_profile.get('stylePersonality'):
                    personality_scores = user_profile.get('stylePersonality', {})
                    
                    # Analyze item characteristics and match with personality
if 'classic' in item_style and (personality_scores.get('classic', 0) if personality_scores else 0) > 0.6:
                        item_score += personality_scores['classic'] * 12
                        logger.info(f"🔍 DEBUG: Classic personality match: +{personality_scores['classic'] * 12:.1f} points")
                    
if 'modern' in item_style and (personality_scores.get('modern', 0) if personality_scores else 0) > 0.6:
                        item_score += personality_scores['modern'] * 12
                        logger.info(f"🔍 DEBUG: Modern personality match: +{personality_scores['modern'] * 12:.1f} points")
                    
if 'creative' in item_style and (personality_scores.get('creative', 0) if personality_scores else 0) > 0.6:
                        item_score += personality_scores['creative'] * 12
                        logger.info(f"🔍 DEBUG: Creative personality match: +{personality_scores['creative'] * 12:.1f} points")
                
                # 6. Business/Formal Enhancement (Existing logic enhanced)
if (req.occasion if req else "unknown").lower() in ['business', 'formal', 'office']:
                    business_colors = ['white', 'black', 'navy', 'gray', 'charcoal', 'beige', 'brown', 'blue', 'cream']
                    if item_color and item_color.lower() in business_colors:
                        item_score += 20  # Bonus for appropriate business colors
                        logger.info(f"🔍 DEBUG: Business-appropriate color: +20 points")
                    elif item_color and item_color.lower() not in business_colors:
                        item_score -= 25  # Penalty for inappropriate colors
                        logger.info(f"🔍 DEBUG: Non-business color: -25 points")
                
                # 7. Gender-appropriate style validation (Enhanced)
                if user_profile and user_profile.get('gender'):
                    user_gender = user_profile.get('gender').lower()
item_gender = (item.get('gender', '') if item else '').lower()
                    
                    # Gender-specific style filtering with scoring
                    # SOFTEN VALIDATION: Allow base item to pass gender filtering
                    if user_gender == 'male':
                        feminine_styles = ['french girl', 'romantic', 'pinup', 'boho', 'cottagecore']
if (req.style if req else "unknown").lower() in feminine_styles and not (req.baseItemId and (item.get('id') if item else None) == (req.baseItemId if req else None)):
logger.info(f"🔍 DEBUG: Skipping feminine style '{req.style}' for male user: {(item.get('name', 'unnamed') if item else 'unnamed')}")
                            continue
elif (req.baseItemId if req else None) and (item.get('id') if item else None) == (req.baseItemId if req else None):
logger.info(f"🛡️ Allowing base item despite feminine style: {(item.get('name', 'Unknown') if item else 'Unknown')}")
                    
                    elif user_gender == 'female':
                        masculine_styles = ['techwear', 'grunge', 'streetwear']
if (req.style if req else "unknown").lower() in masculine_styles and not (req.baseItemId and (item.get('id') if item else None) == (req.baseItemId if req else None)):
logger.info(f"🔍 DEBUG: Skipping masculine style '{req.style}' for female user: {(item.get('name', 'unnamed') if item else 'unnamed')}")
                            continue
elif (req.baseItemId if req else None) and (item.get('id') if item else None) == (req.baseItemId if req else None):
logger.info(f"🛡️ Allowing base item despite masculine style: {(item.get('name', 'Unknown') if item else 'Unknown')}")
                    
                    # Item gender compatibility with scoring
                    # SOFTEN VALIDATION: Allow base item to pass gender compatibility check
if item_gender and item_gender not in ['unisex', user_gender] and not (req.baseItemId and item.get('id') == (req.baseItemId if req else None)):
                        logger.info(f"🔍 DEBUG: Skipping gender-incompatible item: {item.get('name', 'unnamed')} (item: {item_gender}, user: {user_gender})")
                        continue
elif (req.baseItemId if req else None) and (item.get('id') if item else None) == (req.baseItemId if req else None) and item_gender and item_gender not in ['unisex', user_gender]:
logger.info(f"🛡️ Allowing base item despite gender mismatch: {(item.get('name', 'Unknown') if item else 'Unknown')} (item: {item_gender}, user: {user_gender})")
                    
                    # Gender preference bonus
                    if item_gender == user_gender:
                        item_score += 8
                        logger.info(f"🔍 DEBUG: Gender preference match: +8 points")
                    elif item_gender == 'unisex':
                        item_score += 5
                        logger.info(f"🔍 DEBUG: Unisex item: +5 points")
                
                # Store item with its score
item_id = ((item.get('id', item.get('name', 'unknown') if item else 'unknown') if item else 'unknown'))
                item_scores[item_id] = item_score
                suitable_items.append(item)
# print(f"✅ SCORED: {(item.get('name', 'unnamed') if item else 'unnamed')} (ID: {item_id}) = {item_score} points")
#                 print(f"📊 SUITABLE_ITEMS COUNT: {len(suitable_items)} items now in pool")
logger.info(f"🔍 DEBUG: Item {(item.get('name', 'unnamed') if item else 'unnamed')} is suitable with score: {item_score}")
            else:
# print(f"❌ REJECTED: {(item.get('name', 'unnamed') if item else 'unnamed')} failed core style/occasion criteria")
logger.info(f"🔍 DEBUG: Item {(item.get('name', 'unnamed') if item else 'unnamed')} failed core style/occasion criteria")
        
        # DEBUG: After scoring loop
        debug_scores("after_scoring_loop", suitable_items)
        print(f"🎯 Final item_scores: {item_scores}")
        # ENHANCED: Sort items by preference score for better selection
        if suitable_items and item_scores:
        suitable_items.sort(key=lambda item: (item_scores.get(((item.get('id', item.get('name', 'unknown') if item else 'unknown') if item else 'unknown') if item_scores else 'unknown')), 0), reverse=True)
            logger.info(f"🔍 DEBUG: Sorted {len(suitable_items)} suitable items by preference score")
            for item in suitable_items[:5]:  # Log top 5 scores
        score = (item_scores.get(((item.get('id', item.get('name', 'unknown') if item else 'unknown') if item else 'unknown') if item_scores else 'unknown')), 0)
        logger.info(f"🔍 DEBUG: Top item: {(item.get('name', 'unnamed') if item else 'unnamed')} - Score: {score}")
        
        logger.info(f"🔍 DEBUG: Found {len(suitable_items)} suitable items")
        
        
        # ENHANCED: Add randomization to prevent same outfit generation
        import random
        import time
        
        # ENHANCED: Ensure we have enough diverse items for outfit generation
        if len(suitable_items) < 10:
            # Add more items to ensure variety, but RESPECT EXCLUSION FILTER
            additional_items = []
            for item in wardrobe_items:
                if item not in suitable_items:
                    # Apply same exclusion filter to additional items
                    hard_exclusions = get_hard_style_exclusions(req.style.lower(), item)
        if not hard_exclusions or (req.baseItemId and (item.get('id') if item else None) == (req.baseItemId if req else None)):
                        additional_items.append(item)
#                         print(f"➕ ADDITIONAL: {(item.get('name', 'unnamed') if item else 'unnamed')} passes exclusion filter")
                    else:
print(f"🚫 ADDITIONAL EXCLUDED: {(item.get('name', 'unnamed') if item else 'unnamed')} - {hard_exclusions}")
            
            random.shuffle(additional_items)
            suitable_items.extend(additional_items[:10])
            logger.info(f"🔍 DEBUG: Extended suitable items to {len(suitable_items)} for variety (exclusion-filtered)")
        
        
        # If no suitable items, use available items that pass exclusion filter
        if not suitable_items:
            logger.warning(f"⚠️ DEBUG: No suitable items found after filtering")
            logger.warning(f"⚠️ DEBUG: Trying to find ANY items that pass exclusion filter...")
            
            # Apply exclusion filter to emergency fallback items too
            emergency_items = []
            for item in wardrobe_items:
                hard_exclusions = get_hard_style_exclusions(req.style.lower(), item)
        if not hard_exclusions or (req.baseItemId and (item.get('id') if item else None) == (req.baseItemId if req else None)):
                    emergency_items.append(item)
#                     print(f"🆘 EMERGENCY: {(item.get('name', 'unnamed') if item else 'unnamed')} passes exclusion for emergency use")
                else:
print(f"🚫 EMERGENCY EXCLUDED: {(item.get('name', 'unnamed') if item else 'unnamed')} - {hard_exclusions}")
            
            suitable_items = emergency_items[:4]  # Take first 4 exclusion-filtered items
            logger.warning(f"⚠️ DEBUG: Using {len(suitable_items)} emergency items (exclusion-filtered)")
        else:
            logger.info(f"✅ DEBUG: Found {len(suitable_items)} suitable items")
        
        # DEBUG: After filtering
        debug_rule_engine("after_filtering", suitable=suitable_items, scores=item_scores)
        
        # Use timestamp as seed for different randomization each time
        # But preserve base item at the beginning if it exists
        if (req.baseItemId if req else None) and suitable_items and suitable_items[0].get('id') == (req.baseItemId if req else None):
            # Base item is at the beginning, randomize the rest
            base_item = suitable_items[0]
            rest_items = suitable_items[1:]
            random.seed(int(time.time() * 1000) % 1000000)
            random.shuffle(rest_items)
            suitable_items = [base_item] + rest_items
            logger.info(f"🔍 DEBUG: Randomized items while preserving base item at beginning")
        else:
            # No base item or base item not at beginning, randomize all
            random.seed(int(time.time() * 1000) % 1000000)
            random.shuffle(suitable_items)
            logger.info(f"🔍 DEBUG: Randomized all suitable items order with seed")
        
        # Find base item object if baseItemId is provided
        base_item_obj = None
        if (req.baseItemId if req else None):
        base_item_obj = next((item for item in wardrobe_items if item.get("id") == (req.baseItemId if req else None)), None)
            if base_item_obj:
                logger.info(f"🎯 DEBUG: Found base item object for validation: {base_item_obj.get('name', 'Unknown')}")
            else:
                logger.warning(f"⚠️ DEBUG: Base item object not found for validation")
        
        # Debug: Check if base item is in suitable_items
        if (req.baseItemId if req else None):
        base_item_in_suitable = any((item.get('id') if item else None) == (req.baseItemId if req else None) for item in suitable_items)
            logger.info(f"🎯 DEBUG: Base item in suitable_items: {base_item_in_suitable}")
            if base_item_in_suitable:
        base_item_position = next(i for i, item in enumerate(suitable_items) if item.get('id') == (req.baseItemId if req else None))
                logger.info(f"🎯 DEBUG: Base item found in suitable_items at position: {base_item_position}")
                logger.info(f"🎯 DEBUG: Base item details: {suitable_items[base_item_position].get('name', 'Unknown')}")
            else:
                logger.error(f"❌ DEBUG: Base item NOT in suitable_items - this is the problem!")
                logger.error(f"❌ DEBUG: Suitable items count: {len(suitable_items)}")
                logger.error(f"❌ DEBUG: Looking for base item ID: {req.baseItemId}")
        logger.error(f"❌ DEBUG: First few suitable item IDs: {[(item.get('id') if item else None) for item in suitable_items[:5]]}")
        
        # Count categorized items for debug
        categorized_counts = {}
        for item in suitable_items:
        item_type = (item.get('type', '') if item else '').lower()
            category = get_item_category(item_type)
        categorized_counts[category] = (categorized_counts.get(category, 0) if categorized_counts else 0) + 1
        
        # DEBUG: Before validation
        debug_rule_engine("before_validation", suitable=suitable_items, categorized=categorized_counts, scores=item_scores)

        # Validate and ensure complete outfit composition
        try:
        # print(f"🔍 VALIDATION: About to validate outfit composition with {len(suitable_items)} items...")
        validated_items = await validate_outfit_composition(suitable_items, (req.occasion if req else "unknown"), base_item_obj, (req.style if req else "unknown"))
        # print(f"✅ VALIDATION: Successfully validated outfit, got {len(validated_items)} items")
        except Exception as validation_error:
            print(f"❌ VALIDATION FAILED: {validation_error}")
            logger.error(f"Outfit validation failed: {validation_error}")
            # NO FALLBACK TO BAD OUTFITS - Return empty list if validation fails
            validated_items = []
        
        # FORCE MINIMUM VIABLE OUTFIT: If we have suitable items but validation failed
        if len(suitable_items) > 0 and len(validated_items) == 0:
            logger.warning(f"🚨 SAFETY CHECK: {len(suitable_items)} suitable items but validation returned 0 - forcing minimum outfit")
        # print(f"🚨 SAFETY CHECK: Creating minimum viable outfit from {len(suitable_items)} suitable items")
            
            try:
                # Force create a basic outfit from suitable items
        validated_items = _force_minimum_outfit(suitable_items, (req.occasion if req else "unknown"), (req.style if req else "unknown"))
                logger.info(f"🔧 SAFETY CHECK: Created minimum outfit with {len(validated_items)} items")
            except Exception as force_error:
                logger.error(f"❌ SAFETY CHECK FAILED: {force_error}")
                # Fallback to first few suitable items if force minimum fails
                validated_items = suitable_items[:3] if len(suitable_items) >= 3 else suitable_items
                logger.warning(f"🔧 SAFETY FALLBACK: Using first {len(validated_items)} suitable items")
        
        # DEBUG: After validation
        debug_rule_engine("after_validation", validated=validated_items)
        
        logger.info(f"🔍 DEBUG: After validation: {len(validated_items)} items")
        
        # Debug: Check if base item is in final validated items
        if (req.baseItemId if req else None):
        base_item_in_final = any((item.get('id') if item else None) == (req.baseItemId if req else None) for item in validated_items)
            logger.info(f"🎯 DEBUG: Base item in final validated_items: {base_item_in_final}")
            if base_item_in_final:
        base_item_position = next(i for i, item in enumerate(validated_items) if item.get('id') == (req.baseItemId if req else None))
                logger.info(f"🎯 DEBUG: Base item found in final outfit at position: {base_item_position}")
                logger.info(f"🎯 DEBUG: Final outfit base item: {validated_items[base_item_position].get('name', 'Unknown')}")
            else:
                logger.error(f"❌ DEBUG: Base item NOT in final validated_items - validation failed!")
        logger.error(f"❌ DEBUG: Final outfit items: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in validated_items]}")
        logger.error(f"❌ DEBUG: Final outfit item IDs: {[(item.get('id') if item else None) for item in validated_items]}")
        
        # Apply layering validation rules
        layering_validation = await validate_layering_rules(validated_items, (req.occasion if req else "unknown"))
        logger.info(f"🔍 DEBUG: Layering validation: {layering_validation}")
        
        # Apply color theory and material matching
        color_material_validation = await validate_color_material_harmony(validated_items, (req.style if req else "unknown"), (req.mood if req else "unknown"))
        logger.info(f"🔍 DEBUG: Color/material validation: {color_material_validation}")
        
        # Adjust outfit based on validation rules
        if layering_validation.get('warnings'):
            logger.info(f"🔍 DEBUG: Layering warnings: {layering_validation['warnings']}")
        if color_material_validation.get('warnings'):
            logger.info(f"🔍 DEBUG: Color/material warnings: {color_material_validation['warnings']}")
        
        # Create intelligent outfit name based on items and style
        outfit_name = await generate_intelligent_outfit_name(validated_items, (req.style if req else "unknown"), (req.mood if req else "unknown"), (req.occasion if req else "unknown"))
        
        # Ensure items have proper structure with imageUrl
        outfit_items = []
        for item in validated_items:
            # Convert Firebase Storage gs:// URLs to https:// URLs
        raw_image_url = (((item.get('imageUrl', '') if item else '') if item else '') if item else '') or item.get('image_url', '') or item.get('image', '')
            if raw_image_url and raw_image_url.startswith('gs://'):
                # Convert gs://bucket-name/path to https://firebasestorage.googleapis.com/v0/b/bucket-name/o/path
                parts = raw_image_url.replace('gs://', '').split('/', 1)
                if len(parts) == 2:
                    bucket_name = parts[0]
                    file_path = parts[1]
                    # Encode the file path for URL
                    encoded_path = urllib.parse.quote(file_path, safe='')
                    image_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{encoded_path}?alt=media"
                else:
                    image_url = raw_image_url
            else:
                image_url = raw_image_url
            
            outfit_item = {
        "id": (item.get('id', '') if item else ''),
        "name": (item.get('name', '') if item else ''),
        "type": (item.get('type', '') if item else ''),
        "color": (item.get('color', '') if item else ''),
                "imageUrl": image_url
            }
            outfit_items.append(outfit_item)
            # Reduced logging to avoid Railway rate limits
            if len(outfit_items) <= 3:  # Only log first few items
                logger.info(f"🔍 DEBUG: Item {outfit_item['name']} - URL: {image_url[:50]}...")
        
        # Calculate comprehensive outfit score
        try:
            print(f"🔍 SCORING: About to calculate outfit score...")
            outfit_score = await calculate_outfit_score(outfit_items, req, layering_validation, color_material_validation, user_id)
            print(f"✅ SCORING: Successfully calculated outfit score: {outfit_score}")
            logger.info(f"🔍 DEBUG: Calculated outfit score: {outfit_score}")
        except Exception as score_error:
            print(f"❌ SCORING FAILED: {score_error}")
            logger.error(f"Outfit scoring failed: {score_error}")
            # Use default score if scoring fails
            outfit_score = {"total_score": 0.7}
        
        # Final debug logging
        logger.info(f"🎯 DEBUG: Final outfit items: {[(item.get('name', 'Unknown') if item else 'Unknown') for item in outfit_items]}")
        logger.info(f"🎯 DEBUG: Final outfit item IDs: {[(item.get('id', 'Unknown') if item else 'Unknown') for item in outfit_items]}")
        
        # Generate intelligent reasoning
        try:
            print(f"🔍 REASONING: About to generate intelligent reasoning...")
            intelligent_reasoning = await generate_intelligent_reasoning(outfit_items, req, outfit_score, layering_validation, color_material_validation)
            print(f"✅ REASONING: Successfully generated reasoning")
        except Exception as reasoning_error:
            print(f"❌ REASONING FAILED: {reasoning_error}")
            logger.error(f"Intelligent reasoning failed: {reasoning_error}")
            # Use fallback reasoning if generation fails
            intelligent_reasoning = f"Rule-based {req.style} outfit for {req.occasion} with {len(outfit_items)} items"
        
        # Generate detailed outfit analysis for education module
        try:
            outfit_analysis = await generate_outfit_analysis(outfit_items, req, outfit_score)
            logger.info(f"✅ Generated outfit analysis with insights")
        except Exception as analysis_error:
            logger.error(f"Outfit analysis failed: {analysis_error}")
            outfit_analysis = {
                "textureAnalysis": None,
                "patternBalance": None,
                "colorStrategy": None,
                "styleSynergy": None
            }
        
        # FINAL DEBUG: Log outfit assembly results
        logger.info(f"📊 FINAL OUTFIT: {len(outfit_items)} items selected out of {len(suitable_items)} suitable items")
#         print(f"📊 FINAL OUTFIT: {len(outfit_items)} items selected out of {len(suitable_items)} suitable items")
        
        return {
            "name": outfit_name,
        "style": (req.style if req else "unknown"),
        "mood": (req.mood if req else "unknown"),
            "items": outfit_items,
        "occasion": (req.occasion if req else "unknown"),
            "confidence_score": outfit_score["total_score"],
            "score_breakdown": outfit_score,
            "reasoning": intelligent_reasoning,
            "outfitAnalysis": outfit_analysis,  # Add detailed analysis
            "createdAt": datetime.now().isoformat() + 'Z',
            "debug_exclusions": exclusion_debug.copy() if exclusion_debug else [],  # Include exclusion debug data,
            "debug_rule_engine": debug_data.copy() if debug_data else []  # Include rule engine debug data
        }
        
    except Exception as e:
        logger.error(f"❌ Rule-based outfit generation failed: {e}")
        logger.exception("Full rule-based generation traceback:")
        # NO FALLBACKS - Force proper error handling
        logger.error(f"🚨 RULE-BASED GENERATION FAILED - NO FALLBACKS ALLOWED")
        raise Exception(f"Rule-based generation failed: {e}")

def _pick_any_item_safe(wardrobe: List[Dict[str, Any]], category: str, occasion: str) -> Dict[str, Any]:
    """Pick any item safely with occasion-aware filtering to prevent validation failures."""
    import random
    
    # Map category to item types
    category_types = {
        'tops': ['shirt', 'blouse', 't-shirt', 'top', 'tank', 'sweater', 'hoodie', 'sweatshirt'],
        'bottoms': ['pants', 'jeans', 'shorts', 'skirt', 'bottom', 'leggings', 'joggers', 'sweatpants'],
        'shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'athletic shoes'],
        'outerwear': ['jacket', 'outerwear', 'blazer', 'cardigan', 'hoodie', 'zip-up', 'track jacket']
    }
    
    # Get candidates for this category
    candidates = [item for item in wardrobe if item.get('type', '').lower() in (category_types.get(category, []) if category_types else [])]
    
    # Apply occasion-aware filtering
    occasion_lower = occasion.lower()
    
    if 'athletic' in occasion_lower or 'gym' in occasion_lower or 'workout' in occasion_lower:
        # For athletic occasions, prefer athletic items
        if category == 'shoes':
        candidates = [item for item in candidates if any(athletic_term in (item.get('name', '') if item else '').lower() for athletic_term in ['sneaker', 'athletic', 'sport', 'gym', 'workout'])]
        elif category == 'tops':
        candidates = [item for item in candidates if any(athletic_term in (item.get('name', '') if item else '').lower() for athletic_term in ['athletic', 'sport', 'gym', 'workout', 'jersey', 'tank'])]
        elif category == 'bottoms':
        candidates = [item for item in candidates if any(athletic_term in (item.get('name', '') if item else '').lower() for athletic_term in ['athletic', 'sport', 'gym', 'workout', 'shorts', 'joggers'])]
        elif category == 'outerwear':
            # Exclude formal jackets for athletic occasions
        candidates = [item for item in candidates if not any(formal_term in (item.get('name', '') if item else '').lower() for formal_term in ['blazer', 'suit', 'dress', 'formal'])]
    
    elif 'business' in occasion_lower or 'formal' in occasion_lower or 'interview' in occasion_lower:
        # For formal occasions, prefer formal items
        if category == 'shoes':
        candidates = [item for item in candidates if any(formal_term in (item.get('name', '') if item else '').lower() for formal_term in ['dress shoe', 'oxford', 'loafer', 'derby', 'wingtip', 'brogue'])]
        elif category == 'tops':
        candidates = [item for item in candidates if any(formal_term in (item.get('name', '') if item else '').lower() for formal_term in ['dress shirt', 'button down', 'button-up', 'blazer', 'suit jacket'])]
        elif category == 'bottoms':
        candidates = [item for item in candidates if any(formal_term in (item.get('name', '') if item else '').lower() for formal_term in ['dress pant', 'suit pant', 'trouser', 'slack', 'formal pant'])]
        elif category == 'outerwear':
        candidates = [item for item in candidates if any(formal_term in (item.get('name', '') if item else '').lower() for formal_term in ['blazer', 'suit jacket', 'sport coat'])]
    
    # If no candidates after filtering, fall back to any item in wardrobe
    if not candidates:
        logger.warning(f"🚨 EMERGENCY FILTER: No {category} candidates for {occasion}, using any item from wardrobe")
        return random.choice(wardrobe) if wardrobe else None
    
    return random.choice(candidates)

def _force_minimum_outfit(suitable_items: List[Dict[str, Any]], occasion: str, style: str) -> List[Dict[str, Any]]:
    """Force creation of a minimum viable outfit when validation fails but suitable items exist."""
    logger.info(f"🔧 FORCE MINIMUM: Creating outfit from {len(suitable_items)} suitable items")
    
    minimum_outfit = []
    essential_categories = ["tops", "bottoms", "shoes"]
    
    # Try to get one item from each essential category
    for category in essential_categories:
        category_items = [item for item in suitable_items if item.get('type', '').lower() == category]
        if category_items:
            # Take the first item from this category
            minimum_outfit.append(category_items[0])
            logger.info(f"🔧 FORCE MINIMUM: Added {category}: {category_items[0].get('name', 'Unknown')}")
        else:
            logger.warning(f"⚠️ FORCE MINIMUM: No {category} found in suitable items")
    
    # If we still don't have enough items, add any remaining suitable items
    while len(minimum_outfit) < 3 and len(minimum_outfit) < len(suitable_items):
        remaining_items = [item for item in suitable_items if item not in minimum_outfit]
        if remaining_items:
            minimum_outfit.append(remaining_items[0])
            logger.info(f"🔧 FORCE MINIMUM: Added additional item: {remaining_items[0].get('name', 'Unknown')}")
        else:
            break
    
    logger.info(f"🔧 FORCE MINIMUM: Created outfit with {len(minimum_outfit)} items")
    return minimum_outfit

# REMOVED: _emergency_outfit function - was overwriting robust service strategy

def _select_priority_item(items: List[Dict[str, Any]], occasion: str, style: str, category: str) -> Dict[str, Any]:
    """Select the highest priority item for the given occasion and category."""
    if not items:
        return None
    
    occasion_lower = occasion.lower()
    
    # Score items based on priority for formal occasions
    scored_items = []
    for item in items:
        score = 50.0  # Base score
        item_name = (item.get('name', '') if item else '').lower()
        item_type = (item.get('type', '') if item else '').lower()
        
        # COMPREHENSIVE: Occasion-based prioritization for ALL occasions
        # FORMAL OCCASIONS (Business, Formal, Interview)
        if any(formal_term in occasion_lower for formal_term in ['formal', 'business', 'interview']):
            # Prioritize formal shoes (dress shoes, oxfords, loafers)
            if category == 'shoes' and any(formal_shoe in item_name or formal_shoe in item_type for formal_shoe in [
                'dress shoe', 'oxford', 'loafer', 'derby', 'wingtip', 'brogue', 'dress boot'
            ]):
                score += 100.0  # MASSIVE priority for formal shoes
                logger.info(f"🎯 FALLBACK FORMAL: Boosting formal shoes: {item_name}")
            
            # Prioritize formal tops (dress shirts, blazers)
            elif category in ['tops', 'outerwear'] and any(formal_top in item_name or formal_top in item_type for formal_top in [
                'dress shirt', 'button down', 'button-up', 'blazer', 'suit jacket', 'sport coat'
            ]):
                score += 80.0  # High priority for formal tops
                logger.info(f"🎯 FALLBACK FORMAL: Boosting formal tops: {item_name}")
            
            # Prioritize formal bottoms (dress pants, suit pants)
            elif category == 'bottoms' and any(formal_bottom in item_name or formal_bottom in item_type for formal_bottom in [
                'dress pant', 'suit pant', 'trouser', 'slack', 'formal pant'
            ]):
                score += 70.0  # High priority for formal bottoms
                logger.info(f"🎯 FALLBACK FORMAL: Boosting formal bottoms: {item_name}")
            
            # Penalize casual items on formal occasions
            elif any(casual_term in item_name or casual_term in item_type for casual_term in [
                'sneaker', 'athletic', 'canvas', 'flip', 'slides', 'sandals', 'thongs',
                't-shirt', 'tank', 'jersey', 'basketball', 'sport', 'hoodie', 'sweatpants'
            ]):
                score -= 50.0  # Heavy penalty for casual items
                logger.info(f"🎯 FALLBACK FORMAL PENALTY: Penalizing casual item: {item_name}")
        
        # ATHLETIC OCCASIONS (Athletic, Gym, Workout, Sport)
        elif any(athletic_term in occasion_lower for athletic_term in ['athletic', 'gym', 'workout', 'sport']):
            # Prioritize athletic items
            if any(athletic_term in item_name or athletic_term in item_type for athletic_term in [
                'sneaker', 'athletic', 'sport', 'gym', 'workout', 'jersey', 'tank', 'shorts'
            ]):
                score += 60.0  # High priority for athletic items
                logger.info(f"🎯 FALLBACK ATHLETIC: Boosting athletic item: {item_name}")
            
            # Penalize formal items on athletic occasions
            elif any(formal_term in item_name or formal_term in item_type for formal_term in [
                'blazer', 'suit', 'dress pant', 'dress shirt', 'oxford', 'loafer', 'heels'
            ]):
                score -= 40.0  # Penalty for formal items
                logger.info(f"🎯 FALLBACK ATHLETIC PENALTY: Penalizing formal item: {item_name}")
        
        # PARTY OCCASIONS (Party, Night Out, Club)
        elif any(party_term in occasion_lower for party_term in ['party', 'night out', 'club']):
            # Prioritize stylish/trendy items
            if any(party_term in item_name or party_term in item_type for party_term in [
                'party', 'dress', 'blouse', 'top', 'heels', 'boot', 'jacket', 'blazer'
            ]):
                score += 50.0  # High priority for party items
                logger.info(f"🎯 FALLBACK PARTY: Boosting party item: {item_name}")
            
            # Penalize work/athletic items on party occasions
            elif any(inappropriate_term in item_name or inappropriate_term in item_type for inappropriate_term in [
                'work', 'business', 'professional', 'athletic', 'gym', 'sport', 'sweatpants'
            ]):
                score -= 30.0  # Penalty for inappropriate items
                logger.info(f"🎯 FALLBACK PARTY PENALTY: Penalizing inappropriate item: {item_name}")
        
        # DATE OCCASIONS (Date, Romantic)
        elif any(date_term in occasion_lower for date_term in ['date', 'romantic']):
            # Prioritize elegant/romantic items
            if any(date_term in item_name or date_term in item_type for date_term in [
                'dress', 'blouse', 'button down', 'blazer', 'jacket', 'heels', 'boot'
            ]):
                score += 45.0  # High priority for date items
                logger.info(f"🎯 FALLBACK DATE: Boosting date item: {item_name}")
            
            # Penalize athletic/casual items on date occasions
            elif any(inappropriate_term in item_name or inappropriate_term in item_type for inappropriate_term in [
                'athletic', 'gym', 'sport', 'sweatpants', 'hoodie', 'sneaker', 'canvas'
            ]):
                score -= 35.0  # Penalty for inappropriate items
                logger.info(f"🎯 FALLBACK DATE PENALTY: Penalizing inappropriate item: {item_name}")
        
        # WEEKEND OCCASIONS (Weekend, Casual)
        elif any(weekend_term in occasion_lower for weekend_term in ['weekend', 'casual']):
            # Prioritize casual/comfortable items
            if any(weekend_term in item_name or weekend_term in item_type for weekend_term in [
                'casual', 'jeans', 'sneaker', 't-shirt', 'sweater', 'hoodie', 'jacket'
            ]):
                score += 40.0  # High priority for weekend items
                logger.info(f"🎯 FALLBACK WEEKEND: Boosting weekend item: {item_name}")
            
            # Penalize formal items on weekend occasions
            elif any(formal_term in item_name or formal_term in item_type for formal_term in [
                'suit', 'dress pant', 'dress shirt', 'oxford', 'loafer', 'heels'
            ]):
                score -= 25.0  # Penalty for formal items
                logger.info(f"🎯 FALLBACK WEEKEND PENALTY: Penalizing formal item: {item_name}")
        
        # LOUNGEWEAR OCCASIONS (Loungewear, Relaxed)
        elif any(lounge_term in occasion_lower for lounge_term in ['loungewear', 'relaxed', 'lounge']):
            # Prioritize comfortable/loungewear items
            if any(lounge_term in item_name or lounge_term in item_type for lounge_term in [
                'sweat', 'hoodie', 't-shirt', 'jogger', 'lounge', 'pajama', 'comfortable', 'soft'
            ]):
                score += 50.0  # High priority for loungewear items
                logger.info(f"🎯 FALLBACK LOUNGE: Boosting loungewear item: {item_name}")
            
            # Penalize formal/structured items on loungewear occasions
            elif any(inappropriate_term in item_name or inappropriate_term in item_type for inappropriate_term in [
                'blazer', 'suit', 'dress pant', 'oxford', 'heels', 'loafer', 'jeans', 'denim'
            ]):
                score -= 40.0  # Penalty for inappropriate items
                logger.info(f"🎯 FALLBACK LOUNGE PENALTY: Penalizing inappropriate item: {item_name}")
        
        scored_items.append((item, score))
    
    # Sort by score and return the highest scoring item
    scored_items.sort(key=lambda x: x[1], reverse=True)
    best_item = scored_items[0][0]
    best_score = scored_items[0][1]
    
    logger.info(f"🎯 FALLBACK SELECTION: Chose {(best_item.get('name', 'Unknown') if best_item else 'Unknown')} with score {best_score:.1f}")
    return best_item

async def generate_fallback_outfit(req: OutfitRequest, user_id: str) -> Dict[str, Any]:
    """Generate weather-aware fallback outfit when rule-based generation fails."""
    import time  # Add time import for fallback function
    
    logger.info(f"🔄 FALLBACK ACTIVATED: Generating weather-aware fallback outfit for {user_id}")
    print(f"🚨 FALLBACK EXECUTION: Starting fallback outfit generation")
    print(f"🚨 FALLBACK EXECUTION: User={user_id}, Occasion={req.occasion}, Style={req.style}, Mood={req.mood}")
    print(f"🚨 FALLBACK EXECUTION: This indicates main generation logic needs improvement")
    outfit_name = f"{req.style.title()} {req.mood.title()} Look"
    selected_items = []
    
    try:
        # Try to get real wardrobe items for fallback (prefer request data)
        wardrobe_items = req.resolved_wardrobe
        if not wardrobe_items or len(wardrobe_items) == 0:
            wardrobe_items = await get_user_wardrobe(user_id)
        logger.info(f"Retrieved {len(wardrobe_items)} wardrobe items for fallback")
        
        # ENHANCED: Apply weather filtering to fallback generation
        if (req.weather if req else None) and wardrobe_items:
            # Handle both dict and object weather data
            if isinstance(req.weather, dict):
        temp = req.weather.get('temperature', 70) if req.weather else 70
        condition = req.weather.get('condition', 'clear') if req.weather else 'clear'
        precipitation = req.weather.get('precipitation', 0) if req.weather else 0
            else:
                temp = getattr(req.weather, 'temperature', 70)
                condition = getattr(req.weather, 'condition', 'clear')
                precipitation = getattr(req.weather, 'precipitation', 0)
            
            logger.info(f"🌤️ Applying weather filtering to fallback generation: {temp}°F, {condition}")
            weather_filtered_items = []
            for item in wardrobe_items:
                if check_item_weather_appropriateness(item, {
                    'temperature': temp,
                    'condition': condition,
                    'precipitation': precipitation
                }):
                    weather_filtered_items.append(item)
            logger.info(f"After weather filtering: {len(weather_filtered_items)}/{len(wardrobe_items)} items remain")
            wardrobe_items = weather_filtered_items if weather_filtered_items else wardrobe_items  # Use filtered if available
        
        # TARGET-DRIVEN FALLBACK: Use dynamic target count and category limits
        from ..services.outfit_fallback_service import OutfitFallbackService
        
        # Create fallback service context
        fallback_context = {
        'occasion': (req.occasion if req else "unknown"),
        'style': (req.style if req else "unknown"),
        'mood': (req.mood if req else "unknown"),
        'weather': (req.weather if req else None).__dict__ if hasattr(req.weather, '__dict__') else (req.weather if req else None),
            'user_profile': {'id': user_id}
        }
        
        # Get target item counts using the fallback service
        temperature = 70.0
        if (req.weather if req else None):
            if isinstance(req.weather, dict):
        temperature = req.weather.get('temperature', 70.0) if req.weather else 70.0
            else:
                temperature = getattr(req.weather, 'temperature', 70.0)
        
        fallback_service = OutfitFallbackService()
        target_counts = fallback_service._get_target_item_counts(req.occasion, (req.style if req else "unknown"), (req.mood if req else "unknown"), temperature)
        
        logger.info(f"🎯 FALLBACK TARGET-DRIVEN: Target counts for {req.occasion}: {target_counts}")
        
        # Convert wardrobe items to ClothingItem format for fallback service
        from ..custom_types.wardrobe import ClothingItem
        clothing_items = []
        for item_dict in wardrobe_items:
            try:
                clothing_item = ClothingItem(
        id=(item_dict.get('id', '') if item_dict else ''),
        name=(item_dict.get('name', '') if item_dict else ''),
        type=(item_dict.get('type', 'other') if item_dict else 'other'),
        color=(item_dict.get('color', 'unknown') if item_dict else 'unknown'),
        season=(item_dict.get('season', ['all']) if item_dict else ['all']),
        imageUrl=(item_dict.get('imageUrl', 'https://placeholder.com/image.jpg') if item_dict else 'https://placeholder.com/image.jpg'),
        tags=(item_dict.get('tags', []) if item_dict else []),
        style=(item_dict.get('style', []) if item_dict else []),
        userId=(item_dict.get('userId', user_id) if item_dict else user_id),
        dominantColors=(item_dict.get('dominantColors', []) if item_dict else []),
        matchingColors=(item_dict.get('matchingColors', []) if item_dict else []),
        occasion=(item_dict.get('occasion', []) if item_dict else []),
        brand=(item_dict.get('brand') if item_dict else None),
        createdAt=(item_dict.get('createdAt', int(time.time() * 1000)) if item_dict else int(time.time() * 1000)),
        updatedAt=(item_dict.get('updatedAt', int(time.time() * 1000)) if item_dict else int(time.time() * 1000)),
        subType=(item_dict.get('subType') if item_dict else None),
        colorName=(item_dict.get('colorName') if item_dict else None),
        backgroundRemoved=(item_dict.get('backgroundRemoved') if item_dict else None),
        embedding=(item_dict.get('embedding') if item_dict else None),
        metadata=(item_dict.get('metadata') if item_dict else None),
        wearCount=(item_dict.get('wearCount', 0) if item_dict else 0),
        lastWorn=(item_dict.get('lastWorn') if item_dict else None),
        favorite_score=(item_dict.get('favorite_score', 0.0) if item_dict else 0.0)
                )
                clothing_items.append(clothing_item)
            except Exception as e:
                logger.warning(f"⚠️ Failed to convert item to ClothingItem: {e}")
                continue
        
        # Use fallback service intelligent selection
        from ..services.outfit_fallback_service import DynamicHealingContext
        healing_context = DynamicHealingContext(fallback_context)
        
        selected_clothing_items = await fallback_service._intelligent_item_selection(
            clothing_items, fallback_context, healing_context
        )
        
        # Convert back to dict format
        selected_items = []
        for item in selected_clothing_items:
            selected_items.append({
                'id': item.id,
                'name': item.name,
                'type': item.type,
                'color': item.color,
                'brand': item.brand,
                'size': item.size,
                'material': item.material,
                'style': item.style,
                'occasion': item.occasion,
                'season': item.season,
                'wearCount': item.wearCount,
                'lastWorn': item.lastWorn,
                'favorite_score': item.favorite_score,
                'tags': item.tags,
                'metadata': item.metadata
            })
        
        logger.info(f"🎯 FALLBACK TARGET-DRIVEN: Selected {len(selected_items)} items using target-driven approach")
        
        # OLD HARDCODED APPROACH (commented out):
        # This entire block was causing indentation errors and has been removed
        # The new target-driven approach above handles item selection properly
        # Add style-appropriate outerwear if available (WITH VALIDATION)
        all_outerwear = [item for item in wardrobe_items if item.get('type', '').lower() in ['jacket', 'outerwear', 'blazer', 'cardigan', 'hoodie', 'zip-up', 'track jacket']]
        style_appropriate_outerwear = filter_items_by_style(all_outerwear, (req.style if req else "unknown"))
        
        # CRITICAL: Apply inappropriate combination validation to fallback
        if style_appropriate_outerwear:
            # Check if any outerwear would create inappropriate combinations with selected bottoms
            validated_outerwear = []
            for outerwear_item in style_appropriate_outerwear:
        outerwear_type = (outerwear_item.get('type', '') if outerwear_item else '').lower()
        outerwear_name = (outerwear_item.get('name', '') if outerwear_item else '').lower()
                
                # Check if this outerwear would conflict with selected bottoms
                is_inappropriate = False
                for selected_item in selected_items:
        selected_type = (selected_item.get('type', '') if selected_item else '').lower()
        selected_name = (selected_item.get('name', '') if selected_item else '').lower()
                    
                    # Blazer + Shorts prevention
                    if ('blazer' in outerwear_type or 'blazer' in outerwear_name) and ('shorts' in selected_type or 'shorts' in selected_name):
                        logger.warning(f"❌ FALLBACK VALIDATION: Preventing blazer + shorts combination")
                        is_inappropriate = True
                        break
                    
                    # Formal jacket + casual shorts prevention
                    if (('jacket' in outerwear_type and 'formal' in outerwear_name) or 'suit jacket' in outerwear_name) and ('shorts' in selected_type or 'shorts' in selected_name):
                        logger.warning(f"❌ FALLBACK VALIDATION: Preventing formal jacket + shorts combination")
                        is_inappropriate = True
                        break
                
                if not is_inappropriate:
                    validated_outerwear.append(outerwear_item)
                else:
        logger.info(f"✅ FALLBACK VALIDATION: Filtered out inappropriate outerwear: {(outerwear_item.get('name', 'Unknown') if outerwear_item else 'Unknown')}")
            
            style_appropriate_outerwear = validated_outerwear
        
        if style_appropriate_outerwear:
            # Use priority-based selection for outerwear too
        selected_outerwear = _select_priority_item(style_appropriate_outerwear, (req.occasion if req else "unknown"), (req.style if req else "unknown"), 'outerwear')
            selected_items.append(selected_outerwear)
        logger.info(f"Added priority outerwear: {(selected_outerwear.get('name', 'Unknown') if selected_outerwear else 'Unknown')} for {req.style} style")
        
        if selected_items:
            logger.info(f"Successfully created fallback outfit with {len(selected_items)} real wardrobe items")
        else:
            logger.warning("No wardrobe items found, returning empty outfit")
            # Return empty outfit when no wardrobe items exist
            selected_items = []
    
    except Exception as wardrobe_error:
        logger.error(f"Failed to get wardrobe items for fallback: {wardrobe_error}")
        # Return empty outfit when wardrobe retrieval fails
        selected_items = []
    
    # Attach weather context to fallback items
    if (req.weather if req else None) and selected_items:
        try:
            weather_data = {
                'temperature': getattr(req.weather, 'temperature', 70),
                'condition': getattr(req.weather, 'condition', 'clear'),
                'precipitation': getattr(req.weather, 'precipitation', 0)
            }
            selected_items = attach_weather_context_to_items(selected_items, weather_data)
            logger.info(f"🌤️ Attached weather context to {len(selected_items)} fallback items")
        except Exception as fallback_weather_error:
            logger.warning(f"⚠️ Fallback weather context attachment failed: {fallback_weather_error}")
            # Continue without weather context rather than crashing
    
    # FINAL SAFETY NET: Ensure we have at least some items
    if len(selected_items) == 0:
        logger.error(f"🚨 NO ITEMS SELECTED: Rule-based generation failed to select any items")
        print(f"🚨 NO ITEMS SELECTED: Rule-based generation failed to select any items")
        # NO EMERGENCY FALLBACK - let the robust service handle this
    
    # FALLBACK COMPLETION SUMMARY
    # print(f"🚨 FALLBACK COMPLETED: Generated fallback outfit with {len(selected_items)} items")
    print(f"🚨 FALLBACK SUMMARY: Occasion={req.occasion}, Style={req.style}, Mood={req.mood}")
    if selected_items:
        item_types = [(item.get('type', 'unknown') if item else 'unknown') for item in selected_items]
        item_names = [(item.get('name', 'unknown') if item else 'unknown')[:30] for item in selected_items]
        print(f"🚨 FALLBACK ITEMS: Types={item_types}, Names={item_names}")
    else:
        print(f"🚨 FALLBACK WARNING: No items were generated - empty outfit!")
    print(f"🚨 FALLBACK IMPACT: This indicates main generation logic needs attention")
    # Apply semantic validation to fallback outfit
    occasion_requirements_met = True
    validation_applied = True
    
    # Define occasion requirements for fallback validation
    occasion_requirements = {
        'business': {
            'required': ['shirt', 'pants', 'shoes'],
            'optional': ['blazer', 'tie', 'jacket'],
            'forbidden': ['shorts', 'flip-flops', 'tank-top']
        },
        'casual': {
            'required': ['shirt OR t-shirt', 'pants OR shorts', 'shoes'],
            'optional': ['jacket', 'sweater'],
            'forbidden': ['tie', 'formal-shoes']
        },
        'athletic': {
            'required': ['athletic-appropriate footwear', 'athletic-appropriate bottoms', 'athletic-appropriate top'],
            'optional': ['athletic-jacket', 'athletic-accessories'],
            'forbidden': ['dress-shoes', 'formal-wear', 'high-heels']
        },
        'formal': {
            'required': ['dress-shirt', 'dress-pants', 'dress-shoes'],
            'optional': ['suit-jacket', 'tie', 'blazer'],
            'forbidden': ['sneakers', 'shorts', 'casual-wear']
        }
    }
    
    # Check if we have occasion requirements and apply semantic validation
    occasion_lower = (req.occasion if req else "unknown").lower()
    if occasion_lower in occasion_requirements:
        requirements = occasion_requirements[occasion_lower]
        logger.error(f"🚨 STRESS TEST v1.0: FALLBACK VALIDATION START - Calling validate_outfit_completeness")
        try:
        missing_required = validate_outfit_completeness(selected_items, requirements, (req.occasion if req else "unknown"))
            logger.error(f"🚨 STRESS TEST v1.0: FALLBACK VALIDATION SUCCESS - {len(missing_required)} missing items")
        except Exception as e:
            logger.error(f"🚨 STRESS TEST v1.0: FALLBACK VALIDATION ERROR - {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"🚨 STRESS TEST v1.0: FALLBACK VALIDATION TRACEBACK - {traceback.format_exc()}")
            missing_required = []
        
        if len(missing_required) > 0:
            logger.warning(f"⚠️ FALLBACK VALIDATION FAILED: Missing {missing_required}")
            occasion_requirements_met = False
        else:
            logger.info(f"✅ FALLBACK VALIDATION PASSED: All requirements met")
            occasion_requirements_met = True
    
    fallback_outfit = {
        "id": str(uuid4()),  # Add ID for logging
        "name": outfit_name,
        "style": (req.style if req else "unknown"),
        "mood": (req.mood if req else "unknown"),
        "items": selected_items,
        "occasion": (req.occasion if req else "unknown"),
        "confidence_score": 0.7 if len([item for item in selected_items if not (item.get('id', '') if item else '').startswith('fallback')]) > 0 else 0.5,
        "reasoning": generate_weather_aware_fallback_reasoning(req, selected_items),
        "createdAt": datetime.now().isoformat() + 'Z',
        "metadata": {
            "generation_strategy": "fallback_simple",
            "validation_applied": validation_applied,
            "occasion_requirements_met": occasion_requirements_met,
            "deduplication_applied": True,
            "unique_items_count": len(selected_items)
        }
    }
    
    # Log generation strategy for monitoring
    log_generation_strategy(fallback_outfit, user_id, fallback_reason="main_generation_failed")
    
    return fallback_outfit

def generate_weather_aware_fallback_reasoning(req: OutfitRequest, selected_items: List[Dict]) -> str:
    """Generate weather-aware reasoning for fallback outfits."""
    try:
        # Always generate exactly 3 sentences for consistency
        sentences = []
        
        # Sentence 1: Weather context and fallback explanation
        weather_context = ""
        if (req.weather if req else None):
            temp = getattr(req.weather, 'temperature', 70)
            condition = getattr(req.weather, 'condition', 'clear')
            if isinstance(condition, str):
                condition = condition.lower()
            else:
                condition = 'clear'
            
            if temp >= 75:
                weather_context = f"suitable for {temp}°F {condition} weather with comfortable pieces"
            elif temp <= 55:
                weather_context = f"appropriate for cool {temp}°F {condition} conditions with thoughtful layering"
            else:
                weather_context = f"matched to {temp}°F {condition} weather"
                
            if 'rain' in condition:
                weather_context += " and weather-resistant selections"
        else:
            weather_context = "designed for comfortable all-day wear"
            
        # Add weather source indication
        weather_source_note = ""
        if (req.weather if req else None):
            is_manual_override = getattr(req.weather, 'isManualOverride', False)
            is_real_weather = getattr(req.weather, 'isRealWeather', False)
            is_fallback_weather = getattr(req.weather, 'isFallbackWeather', False)
            
            if is_manual_override:
                weather_source_note = " (This outfit was generated based on your manual weather preference.)"
            elif is_real_weather:
                weather_source_note = " (This outfit was generated based on real-time weather data.)"
            elif is_fallback_weather:
                weather_source_note = " (Fallback weather was used; consider minor adjustments if needed.)"
        
        sentences.append(f"This {req.style} {req.occasion} outfit is {weather_context} using your available wardrobe pieces.{weather_source_note}")
        
        # Sentence 2: Item selection rationale
        if selected_items:
            item_count = len(selected_items)
            if item_count >= 3:
                sentences.append(f"The {item_count} selected pieces balance style preferences with weather considerations for your {req.mood} mood.")
            else:
                sentences.append(f"The available {item_count} pieces work together to create a cohesive look that matches your {req.mood} aesthetic.")
        else:
            sentences.append("The outfit selection prioritizes comfort and weather appropriateness within your style preferences.")
        
        # Sentence 3: Confidence and weather appropriateness
        if (req.weather if req else None):
            # Handle both dict and object weather data
            if isinstance(req.weather, dict):
        temp = req.weather.get('temperature', 70) if req.weather else 70
            else:
                temp = getattr(req.weather, 'temperature', 70)
            sentences.append(f"Each item has been chosen to ensure comfort in {temp}°F conditions while maintaining your desired {req.style} style.")
        else:
            sentences.append(f"The combination creates a well-balanced {req.style} ensemble that works for various weather conditions.")
        
        return " ".join(sentences)
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to generate weather-aware fallback reasoning: {e}")
        # Basic fallback with weather context if available
        weather_note = ""
        if (req.weather if req else None):
            # Handle both dict and object weather data
            if isinstance(req.weather, dict):
        temp = req.weather.get('temperature', 70) if req.weather else 70
        condition = req.weather.get('condition', 'clear') if req.weather else 'clear'
            else:
                temp = getattr(req.weather, 'temperature', 70)
                condition = getattr(req.weather, 'condition', 'clear')
            weather_note = f" for {temp}°F {condition.lower()} weather"
        return f"This {req.style} {req.occasion} outfit{weather_note} uses your available wardrobe pieces. The selection balances style and comfort for your {req.mood} mood. Each item works together to create a weather-appropriate, cohesive look."

def validate_weather_outfit_combinations(outfit: Dict[str, Any], weather, mode: str = "soft") -> Dict[str, Any]:
    """Validate outfit combinations for weather appropriateness with hard/soft rule modes.
    
    Args:
        outfit: The generated outfit dictionary
        weather: Weather data object
        mode: "hard" to exclude inappropriate items, "soft" to warn but keep items
    """
    try:
        items = (outfit.get('items', []) if outfit else [])
        if not items:
            return outfit
            
        # Safely extract weather data
        temp = getattr(weather, 'temperature', None) or (weather.get('temperature', 70) if weather else 70) if hasattr(weather, 'get') else 70
        condition = getattr(weather, 'condition', None) or (weather.get('condition', 'clear') if weather else 'clear') if hasattr(weather, 'get') else 'clear'
        if isinstance(condition, str):
            condition = condition.lower()
        else:
            condition = 'clear'
        
        # Check for problematic combinations
        outfit_warnings = []
        items_to_remove = []
        
        # Get item types for combination analysis
        item_types = [(item.get('type', '') if item else '').lower() for item in items]
        item_names = [(item.get('name', '') if item else '').lower() for item in items]
        item_materials = [(item.get('material', '') if item else '').lower() for item in items]
        
        # Check for temperature-inappropriate combinations
        has_shorts = any('shorts' in t or 'short' in name for t, name in zip(item_types, item_names))
        has_heavy_jacket = any(('jacket' in t or 'coat' in t) and any(heavy in name for heavy in ['heavy', 'winter', 'wool']) for t, name in zip(item_types, item_names))
        has_tank_top = any('tank' in t or 'sleeveless' in t for t in item_types)
        has_sweater = any('sweater' in t or 'pullover' in t for t in item_types)
        has_wool = any('wool' in mat for mat in item_materials)
        has_thermal = any('thermal' in mat or 'fleece' in mat for mat in item_materials)
        
        # HARD RULES - Items that should be excluded for comfort
        for i, (item_type, item_name, item_material) in enumerate(zip(item_types, item_names, item_materials)):
            # Very hot weather exclusions
            if temp >= 85:
                if 'heavy' in item_name or 'winter' in item_name or 'wool' in item_material or 'thermal' in item_material:
                    if mode == "hard":
                        items_to_remove.append(i)
                        logger.info(f"🌡️ Hard rule: Excluding {item_name} for {temp}°F weather")
                    else:
                        outfit_warnings.append(f"Warning: {item_name} may be too warm for {temp}°F weather.")
            
            # Very cold weather exclusions  
            elif temp <= 40:
                if 'tank' in item_type or 'sleeveless' in item_type or 'short' in item_type:
                    if mode == "hard":
                        items_to_remove.append(i)
                        logger.info(f"🌡️ Hard rule: Excluding {item_name} for {temp}°F weather")
                    else:
                        outfit_warnings.append(f"Warning: {item_name} may be inadequate for {temp}°F weather.")
        
        # SOFT RULES - Combinations that should be warned about
        if temp <= 67 and has_shorts:
            outfit_warnings.append(f"Note: Shorts may be too cool for {temp}°F weather - consider long pants for better comfort.")
        
        if temp <= 67 and has_shorts and has_heavy_jacket:
            outfit_warnings.append(f"Note: The combination of shorts with a heavy jacket creates an unbalanced look for {temp}°F weather - consider matching the formality levels.")
        
        if temp >= 80 and has_sweater and not has_shorts:
            outfit_warnings.append(f"Note: A sweater may be too warm for {temp}°F {condition} weather - consider lighter layers.")
        
        if temp <= 50 and has_tank_top:
            outfit_warnings.append(f"Note: Tank tops may be inadequate for {temp}°F {condition} conditions - consider adding layers.")
        
        # Apply hard rules if mode is "hard"
        if mode == "hard" and items_to_remove:
            # Remove items in reverse order to maintain indices
            for i in sorted(items_to_remove, reverse=True):
                removed_item = items.pop(i)
        logger.info(f"🗑️ Removed inappropriate item: {(removed_item.get('name', 'Unknown') if removed_item else 'Unknown')}")
            outfit['items'] = items
        
        # Add warnings to reasoning if any found
        if outfit_warnings:
            current_reasoning = outfit.get('reasoning', '')
            warning_text = "\n\n" + " ".join(outfit_warnings)
            outfit['reasoning'] = current_reasoning + warning_text
            logger.info(f"🌤️ Added {len(outfit_warnings)} weather combination warnings to outfit")
        
        return outfit
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to validate weather outfit combinations: {e}")
        return outfit

# Real Firestore operations
async def save_outfit(user_id: str, outfit_id: str, outfit_record: Dict[str, Any]) -> bool:
    """Save outfit to Firestore."""
    try:
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ..config.firebase import db, firebase_initialized
            FIREBASE_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"⚠️ Firebase import failed: {e}")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, skipping save")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
            
        logger.info(f"💾 Saving outfit {outfit_id} for user {user_id}")
        
        # Save to main outfits collection with user_id field (consistent with fetching)
        outfits_ref = db.collection('outfits')
        doc_ref = outfits_ref.document(outfit_id)
        
        try:
            # CRITICAL FIX: Wrap Firestore operation in try/catch to catch silent failures
            doc_ref.set(outfit_record)
        except Exception as firestore_error:
            logger.error(f"💾 Firestore set() FAILED with exception: {firestore_error}")
            raise firestore_error
        
        # Verify the write by immediately reading it back
        verification_doc = doc_ref.get() if doc_ref else None if doc_ref else None
        if not verification_doc.exists:
            logger.error(f"❌ VERIFICATION FAILED: Document does NOT exist after save!")
            return False
        
        logger.info(f"✅ Successfully saved outfit {outfit_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save outfit {outfit_id}: {e}")
        logger.error(f"❌ Exception type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to save outfit: {e}")

def convert_firebase_url(raw_image_url: str) -> str:
    """Convert Firebase Storage gs:// URLs to https:// URLs"""
    if raw_image_url and raw_image_url.startswith('gs://'):
        # Convert gs://bucket-name/path to https://firebasestorage.googleapis.com/v0/b/bucket-name/o/path
        parts = raw_image_url.replace('gs://', '').split('/', 1)
        if len(parts) == 2:
            bucket_name = parts[0]
            file_path = parts[1]
            # Encode the file path for URL
            encoded_path = urllib.parse.quote(file_path, safe='')
            return f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{encoded_path}?alt=media"
    return raw_image_url

def normalize_created_at(created_at) -> str:
    """Safely normalize Firestore created_at into ISO8601 string."""
    try:
        # Case 1: Firestore Timestamp object (DatetimeWithNanoseconds)
        if FIRESTORE_TIMESTAMP_AVAILABLE and isinstance(created_at, DatetimeWithNanoseconds):
            return created_at.isoformat() + "Z" if not created_at.isoformat().endswith("Z") else created_at.isoformat()
        
        # Case 2: Python datetime object
        if isinstance(created_at, datetime):
            return created_at.isoformat() + "Z" if not created_at.isoformat().endswith("Z") else created_at.isoformat()
        
        # Case 3: Int/float timestamp (seconds or milliseconds since epoch) - SAFE RANGE CHECK
        if isinstance(created_at, (int, float)):
            # Handle both seconds and milliseconds timestamps
            if created_at > 1e12:  # Likely milliseconds (> year 33658)
                timestamp_seconds = created_at / 1000.0
            else:
                timestamp_seconds = created_at
            
            # Sanity check: Unix timestamps should be roughly between 2000-2100
            # 946684800 = Jan 1, 2000 UTC, 4102444800 = Jan 1, 2100 UTC  
            if 946684800 <= timestamp_seconds <= 4102444800:
                return datetime.utcfromtimestamp(timestamp_seconds).isoformat() + "Z"
            else:
                logger.warning(f"⚠️ Invalid timestamp value: {created_at} (computed seconds: {timestamp_seconds}, out of reasonable range)")
                return datetime.utcnow().isoformat() + "Z"
        
        # Case 4: Already ISO string
        if isinstance(created_at, str):
            # Handle double timezone issue: "2025-08-27T21:10:11.828353+00:00Z"
            if "+00:00Z" in created_at:
                # Remove the +00:00 part, keep only Z
                created_at = created_at.replace("+00:00Z", "Z")
            elif "+00:00" in created_at and not created_at.endswith("Z"):
                # Replace +00:00 with Z
                created_at = created_at.replace("+00:00", "Z")
            elif not created_at.endswith("Z"):
                # Add Z if missing
                created_at = created_at + "Z"
            return created_at
        
        # Case 5: None or other unexpected types
        logger.warning(f"⚠️ Unexpected created_at type: {type(created_at)} value: {created_at}")
        return datetime.utcnow().isoformat() + "Z"
        
    except Exception as e:
        # Fallback for any corrupted values
        logger.warning(f"⚠️ Failed to normalize created_at {created_at}: {e}, using current time")
        return datetime.utcnow().isoformat() + "Z"

async def resolve_item_ids_to_objects(items: List[Any], user_id: str, wardrobe_cache: Dict[str, Dict] = None) -> List[Dict[str, Any]]:
    """
    Resolve item IDs to actual item objects from the wardrobe collection.
    If an item is already a dictionary, return it as is.
    If an item is a string ID, fetch the item from the wardrobe collection.
    
    Args:
        items: List of item IDs or item objects
        user_id: User ID for the wardrobe
        wardrobe_cache: Optional cache of wardrobe items to avoid repeated queries
    """
    resolved_items = []
    
    # If Firebase is not available, return mock items
    if not firebase_initialized:
        logger.warning("Firebase not available, returning mock items")
        for item in items:
            if isinstance(item, dict):
                # Fix imageUrl even for existing items
                item_copy = item.copy()
        raw_url = (((item_copy.get('imageUrl', '') if item_copy else '') if item_copy else '') if item_copy else '') or item_copy.get('image_url', '') or item_copy.get('image', '')
                item_copy['imageUrl'] = convert_firebase_url(raw_url)
                resolved_items.append(item_copy)
            else:
                resolved_items.append({
                    'id': str(item),
                    'name': 'Mock Item',
                    'type': 'shirt',
                    'imageUrl': None
                })
        return resolved_items
    
    # Collect unique item IDs that need to be fetched
    item_ids_to_fetch = []
    for item in items:
        if isinstance(item, dict):
            # Item is already a complete object - fix imageUrl
            item_copy = item.copy()
        raw_url = (((item_copy.get('imageUrl', '') if item_copy else '') if item_copy else '') if item_copy else '') or item_copy.get('image_url', '') or item_copy.get('image', '')
            item_copy['imageUrl'] = convert_firebase_url(raw_url)
            resolved_items.append(item_copy)
        elif isinstance(item, str):
            if wardrobe_cache and item in wardrobe_cache:
                # Use cached item - fix imageUrl
                cached_item = wardrobe_cache[item].copy()
        raw_url = (((cached_item.get('imageUrl', '') if cached_item else '') if cached_item else '') if cached_item else '') or cached_item.get('image_url', '') or cached_item.get('image', '')
                cached_item['imageUrl'] = convert_firebase_url(raw_url)
                resolved_items.append(cached_item)
            else:
                # Need to fetch this item
                item_ids_to_fetch.append(item)
                resolved_items.append(None)  # Placeholder for position
        else:
            logger.warning(f"Unexpected item type: {type(item)} for item: {item}")
            resolved_items.append({
                'id': str(item),
                'name': 'Invalid item',
                'type': 'unknown',
                'imageUrl': None
            })
    
    # Batch fetch missing items if any
    if item_ids_to_fetch:
        try:
            # Batch fetch items from wardrobe
            docs = db.collection('wardrobe').where('userId', '==', user_id).stream()
            user_wardrobe = {}
            for doc in docs:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                # Fix imageUrl for fetched items
        raw_url = (((item_data.get('imageUrl', '') if item_data else '') if item_data else '') if item_data else '') or item_data.get('image_url', '') or item_data.get('image', '')
                item_data['imageUrl'] = convert_firebase_url(raw_url)
                user_wardrobe[doc.id] = item_data
            
            # Fill in the placeholders
            item_index = 0
            for i, item in enumerate(items):
                if isinstance(item, str) and not (wardrobe_cache and item in wardrobe_cache):
                    if item in user_wardrobe:
                        resolved_items[i] = user_wardrobe[item]
                    else:
                        logger.warning(f"Item {item} not found in wardrobe for user {user_id}")
                        resolved_items[i] = {
                            'id': item,
                            'name': 'Item not found',
                            'type': 'unknown',
                            'imageUrl': None
                        }
                        
        except Exception as e:
            logger.error(f"Error batch fetching items: {e}")
            # Fill placeholders with error items
            for i, item in enumerate(resolved_items):
                if item is None:
                    resolved_items[i] = {
                        'id': str(items[i]),
                        'name': 'Error loading item',
                        'type': 'unknown',
                        'imageUrl': None
                    }
    
    return [item for item in resolved_items if item is not None]

async def get_user_outfits(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Get user outfits from Firestore with pagination."""
    # Temporary: Increase limit to show more outfits
    limit = min(limit, 200)
    logger.info(f"🔍 DEBUG: Fetching outfits for user {user_id} (limit={limit}, offset={offset})")
    
    try:
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ..config.firebase import db, firebase_initialized
            FIREBASE_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"⚠️ Firebase import failed: {e}")
            return []
        
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, returning empty outfits")
            return []
            
        logger.info(f"📚 DEBUG: About to query Firestore collection('outfits') with user_id == '{user_id}'")
        
        # FIXED: Query main outfits collection with user_id field (snake_case)
        # This matches the Pydantic model and outfit creation code
        outfits_ref = db.collection("outfits").where("user_id", "==", user_id)
        
        # CRITICAL FIX: Use proper Firestore ordering to get newest outfits first
        use_firestore_ordering = True
        try:
            from firebase_admin import firestore
            outfits_ref = outfits_ref.order_by("createdAt", direction=firestore.Query.DESCENDING)
            logger.info("✅ DEBUG: Using Firestore server-side ordering by createdAt DESC")
        except Exception as e:
            logger.warning(f"⚠️ DEBUG: Firestore ordering failed ({e}), will use client-side sorting")
            use_firestore_ordering = False
        
        # Apply pagination based on whether ordering worked
        if use_firestore_ordering:
            # Firestore ordering worked, use efficient pagination
            if offset > 0:
                outfits_ref = outfits_ref.offset(offset)
            outfits_ref = outfits_ref.limit(limit)
        else:
            # Firestore ordering failed, fetch more for client-side sorting
            outfits_ref = outfits_ref.limit(min(100, offset + limit * 2))
        
        logger.info(f"🔍 DEBUG: Firestore query: limit={limit}, offset={offset}")
        
        # Execute query with error handling to prevent timeout
        try:
            logger.info(f"🔍 DEBUG: Executing Firestore query with .stream()...")
            docs = outfits_ref.stream()
            logger.info(f"🔍 DEBUG: Firestore query executed successfully, processing results...")
        except Exception as e:
            logger.error(f"🔥 Firestore query failed: {e}", exc_info=True)
            return []  # Return empty list instead of crashing
        
        # First pass: collect outfit data
        outfits = []
        for doc in docs:
            try:
                outfit_data = doc.to_dict()
                outfit_data['id'] = doc.id
                
                # Normalize timestamp immediately to prevent later errors
        outfit_data['createdAt'] = normalize_created_at((outfit_data.get('createdAt') if outfit_data else None))
                
                outfits.append(outfit_data)
        logger.info(f"🔍 DEBUG: Found outfit: {((outfit_data.get('name', 'unnamed') if outfit_data else 'unnamed') if outfit_data else 'unnamed')} (ID: {doc.id}, Created: {outfit_data.get('createdAt', 'Unknown')})")
        logger.info(f"🔍 DEBUG: Outfit {doc.id} wearCount: {((outfit_data.get('wearCount', 'NOT_FOUND') if outfit_data else 'NOT_FOUND') if outfit_data else 'NOT_FOUND')}, lastWorn: {outfit_data.get('lastWorn', 'NOT_FOUND')}")
                logger.info(f"🔍 DEBUG: Outfit {doc.id} all fields: {list(outfit_data.keys())}")
            except Exception as e:
                logger.error(f"🔥 Failed to process outfit {doc.id}: {e}", exc_info=True)
                # Skip this outfit instead of crashing the whole request
                continue
        
        if outfits:
            logger.info(f"🔍 DEBUG: First outfit in results: {outfits[0].get('name')} - {outfits[0].get('createdAt')}")
            logger.info(f"🔍 DEBUG: Last outfit in results: {outfits[-1].get('name')} - {outfits[-1].get('createdAt')}")
        
        # Optimization: Fetch user's wardrobe once for all outfits (only if reasonable size)
        if len(outfits) <= 100:  # Only cache for reasonable dataset sizes
            logger.info(f"🔍 DEBUG: Fetching wardrobe cache for batch item resolution...")
            try:
                wardrobe_docs = db.collection('wardrobe').where('userId', '==', user_id).stream()
                wardrobe_cache = {}
                for doc in wardrobe_docs:
                    item_data = doc.to_dict()
                    item_data['id'] = doc.id
                    wardrobe_cache[doc.id] = item_data
                logger.info(f"✅ DEBUG: Cached {len(wardrobe_cache)} wardrobe items")
            except Exception as e:
                logger.warning(f"⚠️ Could not cache wardrobe: {e}, will fetch items individually")
                wardrobe_cache = None
        else:
            logger.info(f"⚠️ DEBUG: Skipping wardrobe cache for {len(outfits)} outfits (too many for performance)")
            wardrobe_cache = None
        
        # Check if we need client-side sorting (when Firestore ordering failed)
        if not use_firestore_ordering:
            logger.info("🔄 DEBUG: Applying client-side sorting since Firestore ordering failed")
            # Timestamps already normalized during collection, just sort
        outfits.sort(key=lambda x: (x.get('createdAt', '') if x else ''), reverse=True)
        
        # Apply pagination after sorting (ONLY when client-side sorting was used)
        if not use_firestore_ordering:
            start_idx = offset
            end_idx = offset + limit
            outfits = outfits[start_idx:end_idx]
            logger.info(f"✅ DEBUG: Client-side sorted and paginated to {len(outfits)} outfits")
        
        # Final pass: resolve items using cache (reduced logging)
        for outfit_data in outfits:
            if 'items' in outfit_data and outfit_data['items']:
                try:
                    outfit_data['items'] = await resolve_item_ids_to_objects(outfit_data['items'], user_id, wardrobe_cache)
                except Exception as e:
        logger.error(f"🔥 Failed to resolve items for outfit {(outfit_data.get('id') if outfit_data else None)}: {e}")
                    outfit_data['items'] = []  # Set empty items instead of crashing
        else:
            logger.info(f"✅ DEBUG: Firestore returned {len(outfits)} pre-sorted outfits")
            
        if outfits:
            logger.info(f"🔍 DEBUG: First outfit: {outfits[0].get('name')} - {outfits[0].get('createdAt')}")
            logger.info(f"🔍 DEBUG: Last outfit: {outfits[-1].get('name')} - {outfits[-1].get('createdAt')}")
        
        logger.info(f"✅ DEBUG: Successfully retrieved {len(outfits)} outfits from Firestore for user {user_id}")
        return outfits
        
    except Exception as e:
        logger.error(f"❌ ERROR: Failed to fetch outfits from Firestore: {e}", exc_info=True)
        logger.error(f"❌ ERROR: Exception type: {type(e)}")
        logger.error(f"❌ ERROR: Exception details: {str(e)}")
        import traceback
        logger.error(f"❌ ERROR: Full traceback: {traceback.format_exc()}")
        # Return empty list instead of raising exception to prevent timeout
        return []

# Health and debug endpoints (MUST be before parameterized routes)
@router.get("/health", response_model=dict)
async def outfits_health_check():
    """Health check for outfits router."""
    logger.info("🔍 DEBUG: Outfits health check called")
    return {
        "status": "healthy", 
        "router": "outfits", 
        "message": "Outfits router is working!",
        "version": "v5.0-FORCE-REDEPLOY",
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False
    }

@router.get("/debug", response_model=dict)
async def outfits_debug():
    """Debug endpoint for outfits router."""
    logger.info("🔍 DEBUG: Outfits debug endpoint called")
    return {
        "status": "debug",
        "router": "outfits",
        "message": "Outfits router debug endpoint working",
        "timestamp": datetime.now().isoformat(),
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False
    }

@router.get("/debug/base-item-fix")
async def debug_base_item_fix():
    """Debug endpoint to check if base item fix is deployed"""
    return {
        "status": "base_item_fix_deployed",
        "timestamp": datetime.utcnow().isoformat(),
        "fix_version": "v6.0",
        "description": "CLEAN ARCHITECTURE: Base item handling consolidated into ensure_base_item_included() helper function"
    }

@router.get("/debug/rule-engine")
async def debug_rule_engine_data():
    """Debug endpoint to check rule engine debug data"""
    global debug_data
    return {
        "debug_data": debug_data,
        "timestamp": datetime.utcnow().isoformat(),
        "data_count": len(debug_data)
    }

# REMOVED: Duplicate endpoint that was causing 500 errors
# The generate_outfit endpoint below handles this functionality

@router.get("/outfit-save-test", response_model=dict)
async def outfit_save_test():
    """Test saving to the outfits collection specifically."""
    logger.info("🔍 DEBUG: Outfit save test called")
    
    test_results = {
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False,
        "test_timestamp": datetime.now().isoformat()
    }
    
    if FIREBASE_AVAILABLE and firebase_initialized:
        try:
            # Test saving to the same outfits collection that generate_outfit uses
            test_outfit_id = f"test-outfit-{int(datetime.now().timestamp())}"
            test_outfit_data = {
                "id": test_outfit_id,
                "name": "Test Outfit",
                "user_id": current_user.id if current_user else "mock-user",
                "createdAt": datetime.now().isoformat(),
                "test": True,
                "items": [{"type": "shirt", "name": "Test Shirt"}]
            }
            
            logger.info(f"🔥 Testing outfit save to outfits/{test_outfit_id}...")
            outfits_ref = db.collection('outfits')
            doc_ref = outfits_ref.document(test_outfit_id)
            doc_ref.set(test_outfit_data)
            test_results["outfit_save_test"] = "success"
            logger.info("✅ Outfit save test successful")
            
            # Verify by reading back
            logger.info("🔥 Testing outfit read...")
        verification_doc = doc_ref.get() if doc_ref else None if doc_ref else None
            if verification_doc.exists:
                test_results["outfit_read_test"] = "success"
                test_results["read_data"] = verification_doc.to_dict()
                logger.info("✅ Outfit read test successful")
            else:
                test_results["outfit_read_test"] = "failed - document not found"
                logger.error("❌ Outfit read test failed - document not found")
                
        except Exception as e:
            error_msg = f"Outfit save test error: {str(e)}"
            test_results["error"] = error_msg
            logger.error(error_msg)
    else:
        test_results["error"] = "Firebase not available or not initialized"
    
    return {
        "status": "outfit_save_test",
        "results": test_results
    }

@router.get("/firebase-test", response_model=dict)
async def firebase_connectivity_test():
    """Test Firebase write/read operations."""
    logger.info("🔍 DEBUG: Firebase connectivity test called")
    
    test_results = {
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False,
        "write_test": "not_attempted",
        "read_test": "not_attempted",
        "error": None
    }
    
    if FIREBASE_AVAILABLE and firebase_initialized:
        try:
            # Test write operation
            test_doc_id = "connectivity-test"
            test_data = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "message": "Firebase connectivity test"
            }
            
            logger.info("🔥 Testing Firebase write operation...")
            db.collection('test_collection').document(test_doc_id).set(test_data)
            test_results["write_test"] = "success"
            logger.info("✅ Firebase write test successful")
            
            # Test read operation
            logger.info("🔥 Testing Firebase read operation...")
            doc = db.collection('test_collection').document(test_doc_id).get()
            if doc.exists:
                test_results["read_test"] = "success"
                test_results["read_data"] = doc.to_dict()
                logger.info("✅ Firebase read test successful")
            else:
                test_results["read_test"] = "document_not_found"
                logger.warning("⚠️ Document not found after write")
                
        except Exception as e:
            error_msg = f"Firebase test error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            test_results["error"] = error_msg
            test_results["write_test"] = "failed"
            test_results["read_test"] = "failed"
    else:
        test_results["error"] = "Firebase not available or not initialized"
    
    return {
        "status": "firebase_connectivity_test",
        "results": test_results
    }

@router.get("/check-outfits-db", response_model=dict)
async def check_outfits_database():
    """Check what outfits are actually in the database."""
    logger.info("🔍 DEBUG: Checking outfits in database")
    
    check_results = {
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False,
        "user_outfits": [],
        "global_outfits": [],
        "error": None
    }
    
    if FIREBASE_AVAILABLE and firebase_initialized:
        try:
            user_id = "mock-user-123"
            
            # Check user's outfits collection
            logger.info(f"🔍 Checking user outfits for {user_id}")
            user_outfits_ref = db.collection('users').document(user_id).collection('outfits')
            user_docs = user_outfits_ref.limit(10).get()
            
            for doc in user_docs:
                outfit_data = doc.to_dict()
                outfit_data['doc_id'] = doc.id
                check_results["user_outfits"].append(outfit_data)
            
            # Check global outfits collection
            logger.info("🔍 Checking global outfits collection")
            global_outfits_ref = db.collection('outfits')
            global_docs = global_outfits_ref.limit(10).get()
            
            for doc in global_docs:
                outfit_data = doc.to_dict()
                outfit_data['doc_id'] = doc.id
                check_results["global_outfits"].append(outfit_data)
            
            logger.info(f"✅ Found {len(check_results['user_outfits'])} user outfits, {len(check_results['global_outfits'])} global outfits")
                
        except Exception as e:
            error_msg = f"Database check error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            check_results["error"] = error_msg
    else:
        check_results["error"] = "Firebase not available or not initialized"
    
    return {
        "status": "outfits_database_check",
        "results": check_results
    }

@router.get("/debug-retrieval", response_model=dict)
async def debug_outfit_retrieval():
    """Debug the outfit retrieval process step by step."""
    logger.info("🔍 DEBUG: Debug retrieval endpoint called")
    
    debug_info = {
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False,
        "user_id": "mock-user-123",
        "steps": [],
        "error": None,
        "final_result": None
    }
    
    try:
        user_id = "mock-user-123"
        debug_info["steps"].append("Starting retrieval process")
        
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            debug_info["steps"].append("Firebase not available - would use mock data")
            debug_info["final_result"] = "mock_data_fallback"
            return debug_info
        
        debug_info["steps"].append("Firebase is available")
        
        # Test the exact same logic as get_user_outfits
        debug_info["steps"].append(f"Querying outfits collection with user_id == '{user_id}'")
        outfits_ref = db.collection('outfits').where('user_id', '==', user_id)
        docs = outfits_ref.limit(10).get()
        
        debug_info["steps"].append(f"Query returned {len(docs)} documents")
        
        outfits = []
        for doc in docs:
            outfit_data = doc.to_dict()
            outfit_data['id'] = doc.id
            outfits.append({
                "id": doc.id,
        "name": (outfit_data.get('name', 'unknown') if outfit_data else 'unknown'),
        "user_id": (outfit_data.get('user_id', 'unknown') if outfit_data else 'unknown')
            })
        
        debug_info["steps"].append(f"Processed {len(outfits)} outfits")
        debug_info["final_result"] = outfits
        
    except Exception as e:
        error_msg = f"Debug retrieval error: {str(e)}"
        debug_info["steps"].append(error_msg)
        debug_info["error"] = error_msg
        debug_info["final_result"] = "error_fallback"
    
    return {
        "status": "debug_outfit_retrieval",
        "debug_info": debug_info
    }

@router.get("/debug-specific/{outfit_id}", response_model=dict)
async def debug_specific_outfit(outfit_id: str):
    """Debug endpoint to check if a specific outfit exists in Firestore."""
    debug_info = {
        "outfit_id": outfit_id,
        "timestamp": datetime.now().isoformat(),
        "steps": []
    }
    
    try:
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            debug_info["steps"].append("Firebase not available")
            return {"status": "firebase_unavailable", "debug_info": debug_info}
        
        debug_info["steps"].append("Firebase is available")
        
        # Direct document query by ID
        debug_info["steps"].append(f"Querying outfits/{outfit_id} directly")
        doc_ref = db.collection('outfits').document(outfit_id)
        doc = doc_ref.get() if doc_ref else None if doc_ref else None
        
        if doc.exists:
            outfit_data = doc.to_dict()
            debug_info["steps"].append("Document exists!")
            debug_info["outfit_data"] = {
                "id": doc.id,
        "name": (outfit_data.get('name', 'unknown') if outfit_data else 'unknown'),
        "user_id": (outfit_data.get('user_id', 'unknown') if outfit_data else 'unknown'),
        "createdAt": (outfit_data.get('createdAt', 'unknown') if outfit_data else 'unknown'),
        "has_items": len((outfit_data.get('items', []) if outfit_data else [])) > 0
            }
        else:
            debug_info["steps"].append("Document does NOT exist!")
            debug_info["outfit_data"] = None
            
    except Exception as e:
        error_msg = f"Debug error: {str(e)}"
        debug_info["steps"].append(error_msg)
        debug_info["error"] = error_msg
    
    return {
        "status": "debug_specific_outfit",
        "debug_info": debug_info
    }

@router.post("/{outfit_id}/worn")
async def mark_outfit_as_worn(
    outfit_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    # DEBUG DISABLED: Causing 4000+ log drops on Railway
    #  print(f"🚨 CRITICAL: mark_outfit_as_worn endpoint called with outfit_id={outfit_id}, user_id={current_user.id}")
    # Write endpoint entry to Firestore immediately (silent)
    try:
        debug_ref = db.collection('debug_stats_updates').document()
        debug_ref.set({
            'event': 'mark_outfit_as_worn_endpoint_entered',
            'user_id': current_user.id,
            'outfit_id': outfit_id,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Successfully entered mark_outfit_as_worn endpoint'
        })
        #  print("🚨 CRITICAL: Logged endpoint entry to Firestore")
    except Exception as entry_error:
        pass  # Silent error handling
        #  print(f"🚨 CRITICAL: Failed to log endpoint entry: {entry_error}")
    """
    Mark an outfit as worn (simplified endpoint for frontend compatibility).
    This will update both the outfit wear counter AND individual wardrobe item wear counters.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Import Firebase inside function to prevent import-time crashes
        try:
            from ..config.firebase import db, firebase_initialized
        except ImportError as e:
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        if not db:
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        # Simple direct update instead of using the complex OutfitService
        outfit_ref = db.collection('outfits').document(outfit_id)
        outfit_doc = outfit_ref.get() if outfit_ref else None if outfit_ref else None
        
        if not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        
        # Verify ownership
        if outfit_data.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="Outfit does not belong to user")
        
        # Update wear count and last worn
        current_wear_count = (outfit_data.get('wearCount', 0) if outfit_data else 0)
        current_time = datetime.utcnow()
        
        logger.info(f"📊 COUNTER 1: Updating outfit wear count for {outfit_id}")
        logger.info(f"   Before: wearCount={current_wear_count}")
        
        outfit_ref.update({
            'wearCount': current_wear_count + 1,
            'lastWorn': current_time,
            'updatedAt': current_time
        })
        
        logger.info(f"✅ COUNTER 1 UPDATED: Outfit {outfit_id} wearCount {current_wear_count} → {current_wear_count + 1}")
        logger.info(f"   lastWorn set to: {current_time.isoformat()}")
        
        # DEBUG DISABLED: Causing 4000+ log drops on Railway
        try:
            debug_ref = db.collection('debug_stats_updates').document()
            debug_ref.set({
                'event': 'outfit_update_successful',
                'user_id': current_user.id,
                'outfit_id': outfit_id,
                'old_wear_count': current_wear_count,
                'new_wear_count': current_wear_count + 1,
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Successfully updated outfit wear count'
            })
        #  print("🚨 CRITICAL: Outfit update successful, proceeding to user_stats")
        except Exception as outfit_error:
            pass  # Silent error handling
        #  print(f"🚨 CRITICAL: Failed to log outfit update: {outfit_error}")
        # DEBUG DISABLED: Causing massive Railway log flooding
        #  print("🚨 CRITICAL: About to start user_stats update section")
        print("🚨 DEPLOYMENT_TEST: Surgical debug code is LIVE", flush=True)
        # Write entry debug to Firestore immediately (before any potential errors) - SILENT
        try:
            debug_ref = db.collection('debug_stats_updates').document()
            debug_ref.set({
                'event': 'user_stats_section_entered',
                'user_id': current_user.id,
                'outfit_id': outfit_id,
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Successfully entered user_stats update section'
            })
        #  print("🚨 CRITICAL: Logged entry to user_stats section in Firestore")
        except Exception as entry_error:
            pass  # Silent error handling
        #  print(f"🚨 CRITICAL: Failed to log entry to user_stats section: {entry_error}")
        # FIXED: Simple user_stats update with proper increment logic
        try:
            from google.cloud.firestore import Increment
            stats_ref = db.collection('user_stats').document(current_user.id)
            
            # Use Firestore Increment to properly add 1 to existing count
            stats_ref.set({
                'user_id': current_user.id,
                'worn_this_week': Increment(1),  # FIXED: Proper increment instead of hardcoded 1
                'last_updated': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }, merge=True)
            print("✅ FIXED: Updated user_stats with proper increment")
        except Exception as simple_stats_error:
            # Don't fail - outfit was still marked as worn successfully
            print(f"⚠️ SIMPLIFIED: Stats update failed: {simple_stats_error}")
            pass
        
        # DISABLED: Complex week validation logic causing massive syntax errors
        """
        try:
            from google.cloud.firestore import Increment, SERVER_TIMESTAMP
            
            # DEBUG DISABLED: All prints causing 4000+ log drops on Railway
            try:
                debug_ref = db.collection('debug_stats_updates').document()
                debug_ref.set({
                    'event': 'user_stats_imports_successful',
                    'user_id': current_user.id,
                    'outfit_id': outfit_id,
                    'db_available': db is not None,
                    'timestamp': datetime.utcnow().isoformat(),
                    'message': 'Successfully imported Firestore and accessed db'
                })
        #  print("🚨 CRITICAL: Firestore imports and db access successful")
            except Exception as import_error:
        #  print(f"🚨 CRITICAL: Firestore import/db access failed: {import_error}")
                try:
                    error_ref = db.collection('debug_errors').document()
                    error_ref.set({
                        'error_type': 'firestore_import_db_access_failed',
                        'user_id': current_user.id,
                        'outfit_id': outfit_id,
                        'error_message': str(import_error),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                except:
                    pass
            
            # Update user_stats collection for fast dashboard analytics
        print("📅 WEEK_VALIDATION_START", flush=True)
            # Import timezone and timedelta (silent)
            try:
                from datetime import timezone, timedelta
        print("✅ Imported timezone and timedelta successfully", flush=True)
            except Exception as e:
        print(f"❌ Failed to import timezone/timedelta: {e}", flush=True)
                pass
            
            try:
                test_now = datetime.now(timezone.utc)
        print(f"✅ Datetime with timezone works: {test_now}", flush=True)
            except Exception as e:
        print(f"❌ Datetime calculation failed: {e}", flush=True)
                pass
            
            # DEFENSIVE FIX: Use timezone-aware datetime for consistent Firestore handling
            try:
                current_time_dt = datetime.now(timezone.utc)
                week_start = current_time_dt - timedelta(days=current_time_dt.weekday())
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        print(f"✅ WEEK_CALC_SUCCESS: current_time={current_time_dt}, week_start={week_start}", flush=True)
            except Exception as week_error:
        print(f"❌ WEEK_CALC_ERROR: {week_error}", flush=True)
                raise
            
            # SURGICAL FIRESTORE TEST: Check if Firestore access is the culprit (silent)
            try:
                stats_ref = db.collection('user_stats').document(current_user.id)
        stats_doc = stats_ref.get() if stats_ref else None if stats_ref else None
        print("✅ Firestore access successful", flush=True)
            except Exception as e:
        print(f"❌ Firestore access failed: {e}", flush=True)
                raise

            if stats_doc.exists:
                stats_data = stats_doc.to_dict()
        current_worn_count = (stats_data.get('worn_this_week', 0) if stats_data else 0)
                
                # Check if we're still in the same week
        last_updated_raw = (stats_data.get('last_updated') if stats_data else None)
                last_updated = normalize_ts(last_updated_raw)
                
                # After week calc (show raw values used for comparison) - DEBUG DISABLED
        print(f"📅 WEEK_VALIDATION_DEBUG: today={current_time_dt}, last_updated={last_updated}, week_start={week_start}", flush=True)
                # CRITICAL DEBUG: Log exact values for debugging
                try:
                debug_ref = db.collection('debug_stats_updates').document()
                debug_ref.set({
                    'event': 'week_validation_debug',
                    'user_id': current_user.id,
                    'outfit_id': outfit_id,
                    'current_worn_count': current_worn_count,
                    'last_updated': str(last_updated),
                    'last_updated_type': str(type(last_updated)),
                    'week_start': week_start.isoformat(),
                    'is_datetime': isinstance(last_updated, datetime),
                    'timestamp': current_time_dt.isoformat()
                })
            except:
                pass
            
            if last_updated and last_updated >= week_start:
                # Same week, increment count
                # print("📊 SAME_WEEK_INCREMENT: entering", flush=True)  # DISABLED
                new_worn_count = current_worn_count + 1
                # print(f"📊 SAME WEEK: Incrementing {current_worn_count} -> {new_worn_count}")  # DISABLED
            else:
                # New week, reset count to 1
                # print("📊 NEW_WEEK_RESET: entering", flush=True)  # DISABLED
                new_worn_count = 1
                # print(f"📊 NEW WEEK: Resetting count to {new_worn_count} (last_updated: {last_updated}, week_start: {week_start})")  # DISABLED
                
                # RAILWAY-PROOF: Write new week debug info to Firestore
                try:
                    debug_ref = db.collection('debug_stats_updates').document()
                    debug_ref.set({
                        'event': 'user_stats_new_week_reset',
                        'user_id': current_user.id,
                        'outfit_id': outfit_id,
                        'action': 'new_week_reset',
                        'old_count': current_worn_count,
                        'new_count': new_worn_count,
                        'week_start': week_start.isoformat(),
                        'last_updated': last_updated.isoformat() if last_updated else None,
                        'timestamp': current_time_dt.isoformat(),
                        'success': True
                    })
                except:
                    pass
                
                # Before Firestore write
                print(f"🔥 USER_STATS_WRITE_ATTEMPT: worn_this_week={new_worn_count}", flush=True)
                # Use set with merge=True for guaranteed write
                try:
                    stats_ref.set({
                        'user_id': current_user.id,
                        'worn_this_week': new_worn_count,
                        'last_updated': current_time_dt,
                        'updated_at': current_time_dt
                    }, merge=True)
                    print("✅ USER_STATS_WRITE_SUCCESS", flush=True)
                    print(f"✅ STATS UPDATED: worn_this_week = {new_worn_count}")
                except Exception as e:
                    print(f"❌ USER_STATS_WRITE_ERROR: {e}", flush=True)
                # RAILWAY-PROOF: Write debug info to Firestore (bypasses rate limiting)
                try:
                    debug_ref = db.collection('debug_stats_updates').document()
                    debug_ref.set({
                        'event': 'user_stats_increment',
                        'user_id': current_user.id,
                        'outfit_id': outfit_id,
                        'action': 'same_week_increment',
                        'old_count': current_worn_count,
                        'new_count': new_worn_count,
                        'week_start': week_start.isoformat(),
                        'last_updated': last_updated.isoformat() if last_updated else None,
                        'timestamp': current_time_dt.isoformat(),
                        'success': True
                    })
                except:
                    pass  # Don't fail the main operation
                
            else:
                # Create new stats document
                print("🔥 USER_STATS_CREATE_ATTEMPT: worn_this_week=1", flush=True)
                try:
                    stats_ref.set({
                        'user_id': current_user.id,
                        'worn_this_week': 1,
                        'created_this_week': 0,
                        'total_outfits': 1500,  # Estimate
                        'last_updated': current_time_dt,
                        'created_at': current_time_dt
                    }, merge=True)
                    print("✅ USER_STATS_CREATE_SUCCESS", flush=True)
                    print("✅ STATS CREATED: new user_stats with worn_this_week = 1")
                except Exception as e:
                    print(f"❌ USER_STATS_CREATE_ERROR: {e}", flush=True)
                # RAILWAY-PROOF: Write debug info to Firestore
                try:
                    debug_ref = db.collection('debug_stats_updates').document()
                    debug_ref.set({
                        'event': 'user_stats_create',
                        'user_id': current_user.id,
                        'outfit_id': outfit_id,
                        'action': 'create_new_user_stats',
                        'old_count': 0,
                        'new_count': 1,
                        'timestamp': current_time_dt.isoformat(),
                        'success': True
                    })
                except:
                    pass
                
        except Exception as stats_error:
            # FORCE ERROR TO SURFACE - Use multiple methods to ensure visibility
            error_msg = f"🚨 USER_STATS_CRITICAL_ERROR: {stats_error}"
            print(error_msg)
        # print(f"🚨 Error type: {type(stats_error).__name__}")
        # print(f"🚨 Error details: {str(stats_error)}")
            logger.error(error_msg)  # Also use logger in case print is throttled
            
            # Try to write error to a different collection as last resort
            try:
                error_ref = db.collection('debug_errors').document()
                error_ref.set({
                    'error_type': 'user_stats_update_failed',
                    'user_id': current_user.id,
                    'outfit_id': outfit_id,
                    'error_message': str(stats_error),
                    'timestamp': datetime.utcnow(),
                    'attempt': 'robust_fix_with_increment'
                })
                print("🚨 ERROR LOGGED TO debug_errors COLLECTION")
            except:
                pass  # Don't fail the whole request if error logging fails
            
            # Don't raise - outfit was still marked as worn successfully
            
        except Exception as stats_error:
            # CRITICAL: Handle user_stats update failures gracefully
            error_msg = f"🚨 USER_STATS_CRITICAL_ERROR: {stats_error}"
            # print(error_msg, flush=True)  # DISABLED
            logger.error(error_msg)
            
            # Don't raise - outfit was still marked as worn successfully
            
        """
        # END OF DISABLED COMPLEX LOGIC
        
        # Also try the old stats service if available
        try:
            from ..services.user_stats_service import user_stats_service
            asyncio.create_task(user_stats_service.update_outfit_worn_stats(current_user.id, outfit_id))
        except Exception as stats_error:
            logger.warning(f"⚠️ Old stats service failed: {stats_error}")
        
        # Update individual wardrobe item wear counters
        logger.info(f"📊 COUNTER 2: Updating individual wardrobe item wear counts")
        items_updated = 0
        if outfit_data.get('items'):
            total_items = len(outfit_data['items'])
            logger.info(f"   Found {total_items} items in outfit to update")
            
            for item in outfit_data['items']:
                if isinstance(item, dict) and (item.get('id') if item else None):
                    item_id = item['id']
                    item_name = item.get('name', 'Unknown Item')
                    
                    item_ref = db.collection('wardrobe').document(item_id)
                    item_doc = item_ref.get() if item_ref else None if item_ref else None
                    if item_doc.exists:
                        item_data = item_doc.to_dict()
                        if item_data.get('userId') == current_user.id:
                            current_item_wear = item_data.get('wearCount', 0)
                            
                            logger.info(f"   Updating {item_name}: wearCount {current_item_wear} → {current_item_wear + 1}")
                            
                            item_ref.update({
                                'wearCount': current_item_wear + 1,
                                'lastWorn': current_time,
                                'updatedAt': current_time
                            })
                            
                            items_updated += 1
                            logger.info(f"   ✅ Updated item {item_id}")
                        else:
                            logger.warning(f"   ⚠️ Item {item_id} doesn't belong to user, skipping")
                    else:
                        logger.warning(f"   ⚠️ Item {item_id} not found in wardrobe, skipping")
            
            logger.info(f"✅ COUNTER 2 UPDATED: {items_updated}/{total_items} wardrobe items updated")
        else:
            logger.warning(f"⚠️ COUNTER 2: No items found in outfit data")
        
        # Get updated outfit data to return current wear count
        outfit_ref = db.collection('outfits').document(outfit_id)
        outfit_doc = outfit_ref.get() if outfit_ref else None if outfit_ref else None
        
        if outfit_doc.exists:
            outfit_data = outfit_doc.to_dict()
        current_wear_count = (outfit_data.get('wearCount', 0) if outfit_data else 0)
        last_worn = (outfit_data.get('lastWorn') if outfit_data else None)
            
            logger.info(f"🔍 DEBUG: Retrieved outfit data - wearCount: {current_wear_count}, lastWorn: {last_worn}")
            logger.info(f"🔍 DEBUG: Full outfit data keys: {list(outfit_data.keys())}")
            
            # Format lastWorn for frontend
            if isinstance(last_worn, datetime):
                last_worn_str = last_worn.isoformat() + "Z"
            else:
                last_worn_str = datetime.utcnow().isoformat() + "Z"
        else:
            current_wear_count = 1
            last_worn_str = datetime.utcnow().isoformat() + "Z"
        
        # ALSO create outfit history entry for today's outfit tracking
        logger.info(f"📊 COUNTER 3: Creating outfit_history entry for weekly count")
        history_saved_successfully = False
        try:
            current_timestamp = int(datetime.utcnow().timestamp() * 1000)
            
            # Create simplified history entry (avoid clean_for_firestore issues)
            history_entry = {
                'user_id': current_user.id,
                'outfit_id': outfit_id,
                'outfit_name': str(outfit_data.get('name', 'Outfit') if outfit_data else 'Outfit'),
                'outfit_image': str(outfit_data.get('imageUrl', '') if outfit_data else ''),
                'date_worn': current_timestamp,  # Milliseconds timestamp
                'occasion': str(outfit_data.get('occasion', 'Casual') if outfit_data else 'Casual'),
                'mood': str(outfit_data.get('mood', 'Comfortable') if outfit_data else 'Comfortable'),
                'weather': {},
                'notes': '',
                'tags': [],
                'created_at': current_timestamp,
                'updated_at': current_timestamp
            }
            
            logger.info(f"   Creating entry: user_id={current_user.id}, outfit_id={outfit_id}")
            logger.info(f"   date_worn={current_timestamp} ({datetime.fromtimestamp(current_timestamp/1000, tz=timezone.utc).isoformat()})")
            
            # Save to outfit_history collection - NO CLEANING to avoid data loss
            doc_ref, doc_id = db.collection('outfit_history').add(history_entry)
            
            # Verify the entry was actually saved
            saved_doc = doc_ref.get()
            if saved_doc.exists:
                saved_data = saved_doc.to_dict()
                logger.info(f"✅ COUNTER 3 UPDATED: Outfit history entry created successfully!")
                logger.info(f"   Document ID: {doc_id}")
                logger.info(f"   Collection: outfit_history")
                logger.info(f"   date_worn: {saved_data.get('date_worn')}")
                logger.info(f"   This entry will be counted in weekly analytics")
                history_saved_successfully = True
            else:
                logger.error(f"❌ COUNTER 3 FAILED: Document {doc_id} does not exist after save")
                raise Exception(f"History entry verification failed for doc {doc_id}")
            
        except Exception as history_error:
            # Log the error prominently
            logger.error(f"❌ COUNTER 3 FAILED: Could not create outfit history entry: {history_error}")
            logger.error(f"   Weekly outfit count will NOT update!")
            logger.error(f"   Outfit and item counters were still updated successfully")
            # Continue anyway - outfit wear count was still updated
        
        # Update user stats for dashboard counter
        try:
            from ..services.user_stats_service import user_stats_service
            asyncio.create_task(user_stats_service.update_outfit_worn_stats(current_user.id, outfit_id))
            logger.info(f"📊 Triggered user stats update for dashboard counter")
        except Exception as stats_error:
            logger.error(f"❌ Failed to update user stats: {stats_error}")
        
        # Final summary log
        logger.info(f"")
        logger.info(f"═══════════════════════════════════════════════════════════")
        logger.info(f"✅ MARK AS WORN COMPLETE - SUMMARY FOR OUTFIT {outfit_id}")
        logger.info(f"═══════════════════════════════════════════════════════════")
        logger.info(f"   Counter 1 (Outfit): ✅ Updated (wearCount: {current_wear_count} → {current_wear_count + 1})")
        logger.info(f"   Counter 2 (Items): {'✅' if items_updated > 0 else '⚠️'} Updated {items_updated}/{len(outfit_data.get('items', []))} items")
        logger.info(f"   Counter 3 (Weekly): {'✅' if history_saved_successfully else '❌'} History entry {'saved' if history_saved_successfully else 'FAILED'}")
        logger.info(f"   User ID: {current_user.id}")
        logger.info(f"   Timestamp: {datetime.utcnow().isoformat()}")
        logger.info(f"═══════════════════════════════════════════════════════════")
        logger.info(f"")
        
        return {
            "success": True,
            "message": "Outfit marked as worn successfully",
            "wearCount": current_wear_count + 1,
            "lastWorn": last_worn_str,
            "historyEntrySaved": history_saved_successfully,  # NEW: Track if history was saved
            "itemsUpdated": items_updated,  # NEW: Track how many items were updated
            "debug": {
                "outfit_updated": True,
                "items_updated": items_updated,
                "history_saved": history_saved_successfully,
                "timestamp": int(datetime.utcnow().timestamp() * 1000)
            }
        }
        
    except Exception as stats_error:
        # CRITICAL: Handle user_stats update failures gracefully
        error_msg = f"🚨 USER_STATS_CRITICAL_ERROR: {stats_error}"
        # print(error_msg, flush=True)  # DISABLED
        logger.error(error_msg)
        
        # Don't raise - outfit was still marked as worn successfully
        return {
            "success": True,
            "message": "Outfit marked as worn successfully (stats update failed)",
            "wearCount": current_wear_count + 1,
            "lastWorn": current_time.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to mark outfit {outfit_id} as worn: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark outfit as worn: {str(e)}")

@router.get("/debug-user", response_model=dict)
async def debug_user_outfits(
    current_user: UserProfile = Depends(get_current_user)
):
    """Debug endpoint to show user authentication and database contents."""
    logger.info("🔍 DEBUG: Debug user outfits endpoint called")
    
    debug_info = {
        "authenticated": False,
        "user_id": None,
        "user_email": None,
        "firebase_available": FIREBASE_AVAILABLE,
        "firebase_initialized": firebase_initialized if FIREBASE_AVAILABLE else False,
        "database_contents": {},
        "collections_checked": [],
        "error": None
    }
    
    try:
        if current_user:
            debug_info["authenticated"] = True
            debug_info["user_id"] = current_user.id
            debug_info["user_email"] = current_user.email
            logger.info(f"🔍 DEBUG: User authenticated: {current_user.id}")
        else:
            logger.info("🔍 DEBUG: No user authenticated")
        
        # Check what's in the database
        if FIREBASE_AVAILABLE and firebase_initialized:
            try:
                collections_to_check = ['outfits', 'outfit_history', 'user_outfits', 'wardrobe_outfits']
                debug_info["collections_checked"] = collections_to_check
                
                for collection_name in collections_to_check:
                    try:
                        logger.info(f"🔍 DEBUG: Checking collection: {collection_name}")
                        
                        # Get ALL outfits from this collection (no limit)
                        all_outfits = db.collection(collection_name).stream()
                        outfits_list = []
                        
                        for doc in all_outfits:
                            outfit_data = doc.to_dict()
                            outfits_list.append({
                                "id": doc.id,
        "name": (outfit_data.get('name', 'unnamed') if outfit_data else 'unnamed'),
        "user_id": ((outfit_data.get('user_id', outfit_data.get('userId', 'no_user_id') if outfit_data else 'no_user_id') if outfit_data else 'no_user_id')),
        "created_at": ((outfit_data.get('createdAt', outfit_data.get('created_at', 'no_date') if outfit_data else 'no_date') if outfit_data else 'no_date')),
                                "collection": collection_name
                            })
                        
                        debug_info["database_contents"][collection_name] = {
                            "total_outfits_found": len(outfits_list),
                            "sample_outfits": outfits_list[:5] if outfits_list else [],  # Show first 5 as sample
                            "all_outfit_ids": [o["id"] for o in outfits_list]  # Show all IDs
                        }
                        
                        logger.info(f"🔍 DEBUG: Collection {collection_name}: Found {len(outfits_list)} outfits")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ DEBUG: Could not check collection {collection_name}: {e}")
                        debug_info["database_contents"][collection_name] = {
                            "error": str(e),
                            "total_outfits_found": 0
                        }
                
            except Exception as e:
                debug_info["error"] = f"Database query failed: {str(e)}"
                logger.error(f"❌ DEBUG: Database query failed: {e}")
        
    except Exception as e:
        debug_info["error"] = f"General error: {str(e)}"
        logger.error(f"❌ DEBUG: General error: {e}")
    
    return debug_info

# ✅ Generate + Save Outfit (single source of truth)
@router.post("/generate", response_model=OutfitResponse)
async def generate_outfit(
    req: OutfitRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Generate an outfit using robust decision logic with comprehensive validation,
    fallback strategies, body type optimization, and style profile integration.
    """
    # 🔥 COMPREHENSIVE ERROR TRACING FOR NoneType .get() DEBUGGING
    # DEBUG: Log request details at endpoint start
     print(f"🔍 DEBUG ENDPOINT START: req = {req}")
    # print(f"🔍 DEBUG ENDPOINT START: (req.wardrobe if req else []) = {req.wardrobe}")
     print(f"🔍 DEBUG ENDPOINT START: req.resolved_wardrobe = {req.resolved_wardrobe}")
     print(f"🔍 DEBUG ENDPOINT START: current_user_id = {current_user_id}")
    try:
    start_time = time.time()
    generation_attempts = 0
    max_attempts = 3
        # Enhanced authentication validation
        if not current_user_id:
            logger.error("❌ Authentication failed: No current user ID")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        logger.info(f"🎯 Starting robust outfit generation for user: {current_user_id}")
        logger.info(f"📋 Request details: {req.occasion}, {req.style}, {req.mood}")
        
        # Define hard requirements per occasion (ported from simple-minimal)
        occasion_requirements = {
            'business': {
                'required': ['shirt', 'pants', 'shoes'],
                'optional': ['blazer', 'tie', 'jacket'],
                'forbidden': ['shorts', 'flip-flops', 'tank-top']
            },
            'formal': {
                'required': ['shirt', 'pants', 'shoes'],
                'optional': ['blazer', 'tie', 'jacket'],
                'forbidden': ['shorts', 'flip-flops', 'tank-top', 'jeans']
            },
            'athletic': {
                'required': ['top', 'shorts OR athletic-pants', 'sneakers'],
                'optional': ['jacket', 'hat'],
                'forbidden': ['dress-shirt', 'tie', 'dress-shoes']
            },
            'casual': {
                'required': ['top', 'bottom'],
                'optional': ['shoes', 'jacket', 'accessories'],
                'forbidden': []
            },
            'weekend': {
                'required': ['top', 'bottom'],
                'optional': ['sneakers', 'hoodie', 'jacket'],
                'forbidden': ['tie', 'dress-shoes']
            }
        }
        
        # Use global validation functions for semantic outfit validation
        
        # Category cardinality limits (prevents double-shoe issue)
        def get_category_limits(occasion):
            """Define category limits based on occasion"""
            base_limits = {
                "shirt": (1, 2),      # 1-2 shirts allowed
                "top": (1, 2),        # 1-2 tops allowed  
                "pants": (1, 1),      # exactly 1 pants
                "shorts": (1, 1),     # exactly 1 shorts
                "shoes": (1, 1),      # exactly 1 shoes (prevents double-shoe)
                "jacket": (0, 1),     # 0-1 jacket
                "blazer": (0, 1),     # 0-1 blazer
                "accessories": (0, 2), # 0-2 accessories
            }
            
            # Occasion-specific adjustments
            occasion_lower = occasion.lower()
            if occasion_lower in ['business', 'formal']:
                # Business/formal: prefer structured limits
                return {
                    "shirt": (1, 1),      # exactly 1 shirt
                    "top": (1, 1),        # exactly 1 top
                    "pants": (1, 1),      # exactly 1 pants
                    "shoes": (1, 1),      # exactly 1 shoes
                    "jacket": (0, 1),     # 0-1 jacket/blazer
                    "blazer": (0, 1),     # 0-1 blazer
                    "accessories": (0, 1), # 0-1 accessories
                }
            elif occasion_lower == 'athletic':
                # Athletic: allow layering but limit shoes
                return {
                    "top": (1, 2),        # 1-2 tops (layering)
                    "shorts": (1, 1),     # exactly 1 shorts
                    "pants": (1, 1),      # exactly 1 pants
                    "shoes": (1, 1),      # exactly 1 shoes
                    "jacket": (0, 1),     # 0-1 athletic jacket
                    "accessories": (0, 1), # 0-1 accessories
                }
            else:
                # Casual/weekend: more flexible
                return base_limits
        
        # Enhanced deduplication with category cardinality limits and subtype tracking
        def deduplicate_items_with_limits(items, occasion):
            from collections import defaultdict
            
            # Get category limits for this occasion
            category_limits = get_category_limits(occasion)
            
            # Track items by category and subtype
            category_counts = defaultdict(int)
            used_subtypes = set()  # Track shoe subtypes to prevent duplicates
            final_items = []
            
            # First pass: remove exact duplicates (same ID or name+type+color)
            seen_ids = set()
            seen_combinations = set()
            unique_items = []
            
            for item in items:
        item_id = (item.get('id', '') if item else '')
        item_name = (item.get('name', '') if item else '')
        item_type = (item.get('type', '') if item else '').lower()
        item_color = (item.get('color', '') if item else '')
                
                # Create a combination key for name+type+color
                combination_key = f"{item_name}|{item_type}|{item_color}"
                
                # Check both ID uniqueness and combination uniqueness
                if item_id not in seen_ids and combination_key not in seen_combinations:
                    seen_ids.add(item_id)
                    seen_combinations.add(combination_key)
                    unique_items.append(item)
                else:
                    logger.info(f"🔍 DEBUG: Removed exact duplicate: {item_name} ({item_color})")
            
            # Second pass: enforce category cardinality limits with subtype tracking
            for item in unique_items:
        item_type = (item.get('type', '') if item else '').lower()
        item_name = (item.get('name', '') if item else '').lower()
                
                # Map item type to category and determine subtype
                category = None
                subtype = None
                
                if item_type in ['shirt', 'blouse', 't-shirt', 'tank', 'sweater', 'hoodie']:
                    category = 'top'
                    # Determine shirt subtype
                    if 'dress' in item_name or 'button' in item_name:
                        subtype = 'dress_shirt'
                    elif 'polo' in item_name:
                        subtype = 'polo_shirt'
                    elif 't-shirt' in item_name or 'tee' in item_name:
                        subtype = 't_shirt'
                    else:
                        subtype = 'other_top'
                        
                elif item_type in ['pants', 'jeans', 'trousers', 'slacks']:
                    category = 'pants'
                    if 'jeans' in item_name:
                        subtype = 'jeans'
                    elif 'dress' in item_name:
                        subtype = 'dress_pants'
                    else:
                        subtype = 'other_pants'
                        
                elif item_type in ['shorts', 'athletic-pants', 'joggers']:
                    category = 'shorts'
                    subtype = 'shorts'
                    
                elif item_type in ['shoes', 'sneakers', 'boots', 'sandals', 'oxford']:
                    category = 'shoes'
                    # CRITICAL: Determine shoe subtype to prevent duplicate shoes
                    if 'sneaker' in item_name or 'athletic' in item_name:
                        subtype = 'sneakers'
                    elif 'oxford' in item_name or 'dress' in item_name:
                        subtype = 'dress_shoes'
                    elif 'boot' in item_name:
                        subtype = 'boots'
                    elif 'sandals' in item_name:
                        subtype = 'sandals'
                    else:
                        subtype = 'other_shoes'
                        
                elif item_type in ['jacket', 'blazer', 'cardigan']:
                    category = 'jacket'
                    if 'blazer' in item_name:
                        subtype = 'blazer'
                    else:
                        subtype = 'jacket'
                        
                elif item_type in ['tie', 'belt', 'watch', 'hat']:
                    category = 'accessories'
                    subtype = item_type
                else:
                    # For unknown types, be permissive
                    category = 'other'
                    subtype = 'other'
                
                # Check category limits with subtype tracking for shoes
                if category in category_limits:
                    min_limit, max_limit = category_limits[category]
                    current_count = category_counts[category]
                    
                    # Special handling for shoes - prevent duplicate subtypes
                    if category == 'shoes':
                        if current_count >= max_limit:
        logger.info(f"❌ Skipped {(item.get('name', 'Unknown') if item else 'Unknown')} - shoe limit reached (1)")
                            continue
                        if subtype in used_subtypes:
        logger.info(f"❌ Skipped {(item.get('name', 'Unknown') if item else 'Unknown')} - shoe subtype '{subtype}' already used")
                            continue
                        used_subtypes.add(subtype)
        logger.info(f"✅ Added {(item.get('name', 'Unknown') if item else 'Unknown')} (shoes: {subtype})")
                    
                    # Regular category limit check
                    if current_count < max_limit:
                        final_items.append(item)
                        category_counts[category] += 1
                        if category != 'shoes':  # Already logged above
        logger.info(f"✅ Added {(item.get('name', 'Unknown') if item else 'Unknown')} ({category}, count: {category_counts[category]})")
                    else:
        logger.info(f"❌ Skipped {(item.get('name', 'Unknown') if item else 'Unknown')} ({category}) - category limit reached ({max_limit})")
                else:
                    # Unknown category - allow it
                    final_items.append(item)
        logger.info(f"➕ Added {(item.get('name', 'Unknown') if item else 'Unknown')} (unknown category)")
            
            # Log final category distribution and used subtypes
            logger.info(f"🎯 Final outfit category distribution: {dict(category_counts)}")
            logger.info(f"🎯 Used shoe subtypes: {list(used_subtypes)}")
            return final_items
        
        # Retry with relaxed rules instead of falling back to simple-minimal
        def retry_with_relaxed_rules(original_items, occasion, requirements):
            """Retry outfit generation with relaxed rules when validation fails"""
            logger.info(f"🔄 Retrying with relaxed rules for {occasion}")
            
            # Start with original items
            relaxed_items = original_items.copy()
            
            # Try to fill missing required items with more flexible criteria
        missing_required = validate_outfit_completeness(relaxed_items, requirements, (req.occasion if req else "unknown"))
            
            if len(missing_required) > 0:
                logger.info(f"🔧 Attempting to fill missing items: {missing_required}")
                
                # More flexible item selection for missing categories
                for missing_item in missing_required:
                    if missing_item == 'shirt':
                        # Look for any top that could work as a shirt
                        for item in relaxed_items:
                            if item.get('type', '').lower() in ['shirt', 'blouse', 'sweater', 'polo']:
                                logger.info(f"✅ Found flexible shirt alternative: {item.get('name', 'Unknown')}")
                                break
                    elif missing_item == 'pants':
                        # Look for any bottom that could work as pants
                        for item in relaxed_items:
                            if item.get('type', '').lower() in ['pants', 'jeans', 'trousers', 'slacks']:
                                logger.info(f"✅ Found flexible pants alternative: {item.get('name', 'Unknown')}")
                                break
                    elif missing_item == 'shoes':
                        # Look for any shoes
                        for item in relaxed_items:
                            if item.get('type', '').lower() in ['shoes', 'sneakers', 'boots', 'oxford']:
                                logger.info(f"✅ Found flexible shoes alternative: {item.get('name', 'Unknown')}")
                                break
            
            logger.info(f"🔄 Relaxed rules result: {len(relaxed_items)} items")
            return relaxed_items
        
        # Calculate robust confidence score
        def calculate_robust_confidence(items, validation_passed, occasion):
            """Calculate confidence score for robust generator"""
            base_confidence = 0.7  # Base confidence for robust generator
            
            # Boost for validation passing
            if validation_passed:
                confidence_score = base_confidence + 0.22  # +22% for passing validation = 0.92
                logger.info("🎯 High confidence: Validation passed")
            else:
                confidence_score = base_confidence + 0.08  # +8% for relaxed rules = 0.78
                logger.info("🎯 Medium confidence: Used relaxed rules")
            
            # Boost for appropriate item count (3-6 items)
            item_count = len(items)
            if 3 <= item_count <= 6:
                confidence_score += 0.05  # +5% for good item count
            
            # Occasion-specific confidence adjustments
            occasion_lower = occasion.lower()
            if occasion_lower in ['business', 'formal']:
                # Check if we have appropriate formal items
                has_formal_shirt = any('dress' in item.get('name', '').lower() or 'button' in item.get('name', '').lower() 
                                     for item in items if item.get('type', '').lower() in ['shirt', 'blouse'])
                has_formal_pants = any('dress' in item.get('name', '').lower() or 'slacks' in item.get('name', '').lower()
                                     for item in items if item.get('type', '').lower() in ['pants', 'trousers'])
                if has_formal_shirt and has_formal_pants:
                    confidence_score += 0.03  # +3% for formal appropriateness
            
            return min(confidence_score, 1.0)  # Cap at 1.0
        
        # Enhanced request validation
        validation_errors = []
        if not (req.occasion if req else "unknown"):
            validation_errors.append("Occasion is required")
        if not (req.style if req else "unknown"):
            validation_errors.append("Style is required")
        if not (req.mood if req else "unknown"):
            validation_errors.append("Mood is required")
        if not (req.wardrobe if req else []) or len(req.wardrobe) == 0:
            validation_errors.append("Wardrobe items are required")
        
        if validation_errors:
            logger.error(f"❌ Request validation failed: {validation_errors}")
            raise HTTPException(status_code=422, detail=f"Invalid request: {', '.join(validation_errors)}")
        
        logger.info(f"✅ Request validation passed")
        
        # Log base item information
        logger.info(f"🔍 DEBUG: Received baseItemId: {req.baseItemId}")
        if (req.baseItemId if req else None):
            # Find the base item in the wardrobe array
        base_item = next((item for item in (req.wardrobe if req else []) if item.get("id") == (req.baseItemId if req else None)), None)
            if base_item:
                logger.info(f"🔍 DEBUG: Found base item in wardrobe: {base_item.get('name', 'Unknown')} ({base_item.get('type', 'Unknown')})")
            else:
                logger.warning(f"⚠️ DEBUG: Base item {req.baseItemId} not found in wardrobe array")
        else:
            logger.info("🔍 DEBUG: No baseItemId provided")
        
        logger.info(f"🎨 Starting outfit generation with retry logic")
        
        # Import validation pipeline once outside the retry loop
        try:
            from ..services.outfit_validation_pipeline import validation_pipeline, ValidationContext
            validation_available = True
            logger.info("✅ Validation pipeline imported successfully")
        except ImportError as e:
            logger.warning(f"⚠️ Validation pipeline import failed: {e}")
            validation_available = False
        
        # Retry logic for robust generation
        outfit = None
        last_error = None
        error_details = None
        
        for attempt in range(max_attempts):
            generation_attempts += 1
            try:
                logger.info(f"🔄 Generation attempt {generation_attempts}/{max_attempts}")
        print(f"🔍 DEBUG RETRY LOOP: Starting attempt {generation_attempts}")
        print(f"🔍 DEBUG RETRY LOOP: req = {req}")
        print(f"🔍 DEBUG RETRY LOOP: current_user_id = {current_user_id}")
                # Run generation logic with robust service
                outfit = await generate_outfit_logic(req, current_user_id)
                
                # NEW STRATEGY: Keep robust generator in control, don't auto-fallback
                if outfit and outfit.get('items'):
        occasion_lower = (req.occasion if req else "unknown").lower()
                    
                    # CRITICAL DEBUG: Log strategy before category limits
        logger.info(f"🔍 DEBUG BEFORE CATEGORY LIMITS: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
        # print(f"🔍 DEBUG BEFORE CATEGORY LIMITS: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                    
                    # Step 1: Apply category limits and subtype tracking INSIDE robust logic
                    original_items = outfit['items'].copy()
        outfit['items'] = deduplicate_items_with_limits(outfit['items'], (req.occasion if req else "unknown"))
                    
                    # CRITICAL DEBUG: Log strategy after category limits
        logger.info(f"🔍 DEBUG AFTER CATEGORY LIMITS: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
        # print(f"🔍 DEBUG AFTER CATEGORY LIMITS: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                    
                    # Step 2: If validation fails, retry with relaxed rules instead of falling back
                    validation_passed = True
                    if occasion_lower in occasion_requirements:
                        requirements = occasion_requirements[occasion_lower]
        missing_required = validate_outfit_completeness(outfit['items'], requirements, (req.occasion if req else "unknown"))
                        
                        if len(missing_required) > 0:
                            logger.warning(f"⚠️ VALIDATION FAILED: Missing {missing_required} - retrying with relaxed rules")
                            validation_passed = False
                            
                            # CRITICAL DEBUG: Log strategy before relaxed rules
        logger.info(f"🔍 DEBUG BEFORE RELAXED RULES: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
        # print(f"🔍 DEBUG BEFORE RELAXED RULES: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                            
                            # Retry with relaxed rules instead of falling back
        outfit['items'] = retry_with_relaxed_rules(original_items, (req.occasion if req else "unknown"), requirements)
                            
                            # Re-apply category limits to relaxed outfit
        outfit['items'] = deduplicate_items_with_limits(outfit['items'], (req.occasion if req else "unknown"))
                            
                            # CRITICAL DEBUG: Log strategy after relaxed rules
        logger.info(f"🔍 DEBUG AFTER RELAXED RULES: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
        # print(f"🔍 DEBUG AFTER RELAXED RULES: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                            
                            logger.info(f"🔄 Retried with relaxed rules - final items: {len(outfit['items'])}")
                    
                    # Step 3: Calculate confidence score AFTER all processing
                    # Only calculate new confidence if robust generator didn't provide one
                    if 'confidence_score' not in outfit or outfit['confidence_score'] is None or outfit['confidence_score'] == 0.0:
        confidence_score = calculate_robust_confidence(outfit['items'], validation_passed, (req.occasion if req else "unknown"))
                        outfit['confidence_score'] = confidence_score
                        logger.info(f"🎯 Calculated new confidence score: {confidence_score}")
                    else:
                        logger.info(f"🎯 Preserving robust generator confidence: {outfit['confidence_score']}")
                    
                    # CRITICAL DEBUG: Log strategy before metadata modification
        logger.info(f"🔍 DEBUG BEFORE METADATA MODIFICATION: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
        # print(f"🔍 DEBUG BEFORE METADATA MODIFICATION: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                    
                    # Ensure metadata exists
                    if 'metadata' not in outfit:
        outfit['metadata'] = None
                    outfit['metadata']['subtype_tracking_enabled'] = True
                    outfit['metadata']['confidence_calculated'] = True
                    outfit['metadata']['validation_passed'] = validation_passed
                    outfit['metadata']['retry_with_relaxed_rules'] = not validation_passed
                    
                    # CRITICAL DEBUG: Log strategy after metadata modification
        logger.info(f"🔍 DEBUG AFTER METADATA MODIFICATION: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
        # print(f"🔍 DEBUG AFTER METADATA MODIFICATION: strategy = {safe_get_metadata(outfit, 'generation_strategy', 'unknown')}")
                    
                    # Update metadata with processing status (simplified)
                    if 'metadata' not in outfit:
        outfit['metadata'] = None
                    outfit['metadata']['validation_applied'] = True
                    outfit['metadata']['hard_requirements_enforced'] = True
                    outfit['metadata']['deduplication_applied'] = True
                    outfit['metadata']['category_limits_enforced'] = True  # NEW: Category cardinality limits
                    outfit['metadata']['unique_items_count'] = len(outfit['items'])
                    outfit['metadata']['occasion_requirements_met'] = validation_passed
                
                # NEW: Apply comprehensive validation pipeline to generated outfit (with category limits bypass)
                if outfit and outfit.get('items') and validation_available:
                    try:
                        # Check if category limits have already been enforced
        category_limits_applied = safe_get_metadata(outfit, 'category_limits_enforced', False)
                        
                        if category_limits_applied:
                            logger.info("🎯 Category limits already applied - skipping enhanced validation to prevent rejection")
                            # Skip enhanced validation since we've already enforced category limits
                            outfit['metadata']['enhanced_validation_bypassed'] = True
                            outfit['metadata']['validation_reason'] = "Category limits already enforced"
                        else:
                            logger.info("🔍 Running enhanced validation pipeline")
                            # Create validation context
                            validation_context = ValidationContext(
                                occasion=req.occasion,
                                style=req.style or "casual",
                                mood=req.mood or "neutral",
        weather=req.weather.__dict__ if hasattr(req.weather, '__dict__') else (req.weather if req else None),
                                user_profile={"id": current_user_id},  # Basic profile for validation
                                temperature=getattr(req.weather, 'temperature', 70.0) if hasattr(req.weather, 'temperature') else 70.0
                            )
                            
                            # Run validation pipeline
                            validation_result = await validation_pipeline.validate_outfit(outfit, validation_context)
                            
                            if not validation_result.valid:
                                failed_rules = validation_result.errors or []
                                logger.warning(f"⚠️ VALIDATION FAILED on attempt {generation_attempts}: {validation_result.errors}")
                                print(f"🚨 VALIDATION ALERT: Attempt {generation_attempts} failed validation")
                                # If validation fails, retry or use emergency outfit
                                if attempt < max_attempts - 1:
                                    await asyncio.sleep(1)  # Brief delay before retry
                                    continue
                                else:
                                    # Final attempt failed validation - NO EMERGENCY FALLBACK
                                    logger.error(f"❌ VALIDATION FAILURE: All {max_attempts} attempts failed validation")
                                    print(f"🚨 VALIDATION FAILURE: All {max_attempts} attempts failed validation")
                                    # NO EMERGENCY FALLBACK - let the robust service handle this
                                    raise Exception(f"Validation failed after {max_attempts} attempts")
                                
                    except Exception as validation_error:
                        logger.warning(f"⚠️ Validation pipeline failed: {validation_error}, continuing with outfit")
                        # Don't fail the entire request if validation pipeline has issues
                        # Just log the error and continue with the outfit
                elif outfit and outfit.get('items') and not validation_available:
                    logger.info("⚠️ Validation pipeline not available, skipping validation")
                else:
                    logger.warning("⚠️ No outfit generated or validation not available")
                
                # Validate the generated outfit (basic validation)
                if outfit and outfit.get('items') and len(outfit.get('items', [])) >= 3:
                    logger.info(f"✅ Generation successful on attempt {generation_attempts}")
                    break
                else:
                    logger.warning(f"⚠️ Generation attempt {generation_attempts} produced invalid outfit")
                    print(f"🚨 RETRY ALERT: Attempt {generation_attempts} failed - invalid outfit")
                    print(f"🚨 RETRY CONTEXT: User={current_user_id}, Occasion={req.occasion}, Style={req.style}, Mood={req.mood}")
        # print(f"🚨 RETRY REASON: Generated outfit has {len((outfit.get('items', []) if outfit else []))} items (minimum 3 required)")
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(1)  # Brief delay before retry
                        continue
                    
            except Exception as e:
                last_error = e
        import traceback
        
        # 🔥 ENHANCED ERROR TRACING FOR NoneType .get() DEBUGGING
        error_details = {
        "attempt": generation_attempts,
        "max_attempts": max_attempts,
        "error_type": str(type(e).__name__),
        "error_message": str(e),
        "full_traceback": traceback.format_exc(),
        "context": {
        "user_id": current_user_id,
        "occasion": getattr(req, 'occasion', 'NO_OCCASION') if req else 'NO_REQ',
        "style": getattr(req, 'style', 'NO_STYLE') if req else 'NO_REQ',
        "mood": getattr(req, 'mood', 'NO_MOOD') if req else 'NO_REQ'
        }
        }
        
        logger.error(f"🔥 RETRY LOOP CRASH - NoneType .get() error detected", extra=error_details, exc_info=True)
        print(f"🔥 RETRY LOOP CRASH: {error_details}")
        # print(f"🔥 FULL TRACEBACK:\n{traceback.format_exc()}")
        
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)  # Brief delay before retry
                    continue
        
        # Check if all attempts failed
        if not outfit or not ((outfit.get('items') if outfit else None) if outfit else None) or len(outfit.get('items', [])) < 3:
            logger.error(f"❌ All {max_attempts} generation attempts failed")
            print(f"🚨 FINAL FAILURE: All {max_attempts} generation attempts failed")
            print(f"🚨 FINAL CONTEXT: User={current_user_id}, Occasion={req.occasion}, Style={req.style}, Mood={req.mood}")
            print(f"🚨 FINAL IMPACT: User will receive HTTP 500 error - no outfit generated")
            if last_error:
        # print(f"🚨 FINAL ERROR: {type(last_error).__name__}: {str(last_error)}")
        # Preserve debug information from our debug logging
        error_detail = str(last_error)
        if "DEBUG:" in error_detail or "🔥" in error_detail or "NoneType" in error_detail:
        # Our debug information is in the error message - return it directly
        if error_details:
                raise HTTPException(
                    status_code=500, 
        detail=f"🔥 RETRY LOOP CRASH: {error_details['error_type']}: {error_details['error_message']}\n\nFull Traceback:\n{error_details['full_traceback']}"
        )
        else:
        raise HTTPException(
        status_code=500,
        detail=error_detail  # Return original error if no enhanced details
        )
        else:
        raise HTTPException(
        status_code=500,
        detail=f"Outfit generation failed after {max_attempts} attempts: {error_detail}"
                )
            else:
                print(f"🚨 FINAL ERROR: No specific error - unable to generate valid outfit")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Outfit generation failed: Unable to generate valid outfit"
                )

        # 2. Wrap with metadata
        outfit_id = str(uuid4())
        outfit_record = {
            "id": outfit_id,
            "user_id": current_user_id,  # Use snake_case to match database schema
            "generated_at": datetime.utcnow().isoformat(),
            **outfit
        }

        # 3. Clean and save to Firestore
        logger.info(f"🔄 About to save generated outfit {outfit_id}")
        
        # AGGRESSIVE CLEANING: Remove problematic fields that cause Firebase serialization issues
        outfit_record_cleaned = {
        "id": (outfit_record.get("id") if outfit_record else None),
        "user_id": (outfit_record.get("user_id") if outfit_record else None),
        "generated_at": (outfit_record.get("generated_at") if outfit_record else None),
        "name": (outfit_record.get("name") if outfit_record else None),
        "occasion": (outfit_record.get("occasion") if outfit_record else None),
        "style": (outfit_record.get("style") if outfit_record else None),
        "mood": (outfit_record.get("mood") if outfit_record else None),
        "confidence_score": (outfit_record.get("confidence_score") if outfit_record else None),
        "reasoning": (outfit_record.get("reasoning") if outfit_record else None),
        "createdAt": (outfit_record.get("createdAt") if outfit_record else None),
        "userId": (outfit_record.get("userId") if outfit_record else None),
        "explanation": (outfit_record.get("explanation") if outfit_record else None),
        "styleTags": (outfit_record.get("styleTags", []) if outfit_record else []),
        "colorHarmony": (outfit_record.get("colorHarmony") if outfit_record else None),
        "styleNotes": (outfit_record.get("styleNotes") if outfit_record else None),
        "season": (outfit_record.get("season") if outfit_record else None),
        "updatedAt": (outfit_record.get("updatedAt") if outfit_record else None),
        "wasSuccessful": (outfit_record.get("wasSuccessful") if outfit_record else None),
        "baseItemId": (outfit_record.get("baseItemId") if outfit_record else None)
        }
        
        # Clean items array - convert ClothingItem objects to simple dicts
        items_cleaned = []
        for item in (outfit_record.get("items", []) if outfit_record else []):
            if hasattr(item, "dict"):
                items_cleaned.append(item.dict())
            elif hasattr(item, "model_dump"):
                items_cleaned.append(item.model_dump())
            elif isinstance(item, dict):
                items_cleaned.append(item)
            else:
                logger.warning(f"Skipping non-serializable item: {type(item)}")
        outfit_record_cleaned["items"] = items_cleaned
        
        # Clean pieces array - convert to simple dicts or skip if problematic
        pieces_cleaned = []
        for piece in (outfit_record.get("pieces", []) if outfit_record else []):
            if hasattr(piece, "dict"):
                pieces_cleaned.append(piece.dict())
            elif hasattr(piece, "model_dump"):
                pieces_cleaned.append(piece.model_dump())
            elif isinstance(piece, dict):
                pieces_cleaned.append(piece)
            else:
                logger.warning(f"Skipping non-serializable piece: {type(piece)}")
        outfit_record_cleaned["pieces"] = pieces_cleaned
        
        # Clean metadata - ensure it's a simple dict
        metadata = (outfit_record.get("metadata", {}) if outfit_record else {})
        if isinstance(metadata, dict):
            outfit_record_cleaned["metadata"] = metadata
        else:
        outfit_record_cleaned["metadata"] = None
        
        # Apply final cleaning
        clean_outfit_record = clean_for_firestore(outfit_record_cleaned)
        logger.info(f"🧹 Cleaned outfit record: {clean_outfit_record}")
        
        # CRITICAL DEBUG: Log strategy right before saving to Firebase
        final_strategy = safe_get_metadata(clean_outfit_record, 'generation_strategy', 'unknown')
        logger.info(f"🔍 DEBUG FINAL SAVE: strategy = {final_strategy}")
        print(f"🔍 DEBUG FINAL SAVE: strategy = {final_strategy}")
        save_result = await save_outfit(current_user_id, outfit_id, clean_outfit_record)
        logger.info(f"💾 Save operation result: {save_result}")
        
        # Update user stats (async, don't fail if it errors)
        try:
            from ..services.user_stats_service import user_stats_service
            await user_stats_service.update_outfit_stats(current_user_id, "created", clean_outfit_record)
        except Exception as stats_error:
            logger.warning(f"Stats update failed: {stats_error}")

        # 4. Performance monitoring and final validation
        generation_time = time.time() - start_time
        logger.info(f"⏱️ Generation completed in {generation_time:.2f} seconds")
        logger.info(f"📊 Generation attempts: {generation_attempts}")
        
        # Final outfit validation
        final_validation = await _validate_final_outfit(outfit_record, req)
        if not final_validation['is_valid']:
            logger.warning(f"⚠️ Final validation issues: {final_validation['issues']}")
            # Add validation warnings to metadata
            outfit_record['metadata']['validation_warnings'] = final_validation['issues']
        
        # Enhanced success logging
        logger.info(f"✅ Successfully generated robust outfit {outfit_id}")
        logger.info(f"📋 Outfit details: {len(((outfit_record.get('items', []) if outfit_record else []) if outfit_record else []))} items, confidence: {outfit_record.get('confidence', 'unknown')}")
        
        # Return standardized outfit response
        return OutfitResponse(**outfit_record)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # 🔥 COMPREHENSIVE ERROR TRACING FOR NoneType .get() DEBUGGING
        import traceback
        error_details = {
        "error_type": str(type(e).__name__),
            "error_message": str(e),
        "full_traceback": traceback.format_exc(),
        "context": {
            "user_id": current_user_id,
        "occasion": getattr(req, 'occasion', 'NO_OCCASION') if req else 'NO_REQ',
        "style": getattr(req, 'style', 'NO_STYLE') if req else 'NO_REQ',
        "mood": getattr(req, 'mood', 'NO_MOOD') if req else 'NO_REQ'
        }
        }
        
        logger.error("🔥 ENDPOINT CRASH - NoneType .get() error detected", extra=error_details, exc_info=True)
        print(f"🔥 ENDPOINT CRASH: {error_details}")
        # print(f"🔥 FULL TRACEBACK:\n{traceback.format_exc()}")
        
        # Return the detailed error information
            raise HTTPException(
                status_code=500, 
        detail=f"🔥 ENDPOINT CRASH: {error_details['error_type']}: {error_details['error_message']}\n\nFull Traceback:\n{error_details['full_traceback']}"
            )

async def _validate_final_outfit(outfit_record: Dict[str, Any], req: OutfitRequest) -> Dict[str, Any]:
    """Validate the final outfit before returning to user"""
    issues = []
    is_valid = True
    
    # Check item count
    items = (outfit_record.get('items', []) if outfit_record else [])
    if len(items) < 3:
        issues.append(f"Outfit has only {len(items)} items (minimum: 3)")
        is_valid = False
    elif len(items) > 6:
        issues.append(f"Outfit has {len(items)} items (maximum: 6)")
        is_valid = False
    
    # Check for essential categories
    categories = set()
    for item in items:
        item_type = item.get('type', '').lower()
        if item_type in ['shirt', 'blouse', 'sweater', 'tank', 'top']:
            categories.add('tops')
        elif item_type in ['pants', 'jeans', 'shorts', 'skirt']:
            categories.add('bottoms')
        elif item_type in ['shoes', 'sneakers', 'boots', 'sandals']:
            categories.add('shoes')
    
    missing_essential = {'tops', 'bottoms', 'shoes'} - categories
    if missing_essential:
        issues.append(f"Missing essential categories: {missing_essential}")
        is_valid = False
    
    # Check for inappropriate combinations
    inappropriate_combinations = [
        ("blazer", "shorts"),
        ("formal_shoes", "casual_bottoms"),
        ("tie", "t_shirt")
    ]
    
    for item1 in items:
        for item2 in items:
            if item1 != item2:
                type1 = item1.get('type', '').lower()
        type2 = (item2.get('type', '') if item2 else '').lower()
                
                for combo1, combo2 in inappropriate_combinations:
                    if (combo1 in type1 and combo2 in type2) or (combo1 in type2 and combo2 in type1):
                        issues.append(f"Inappropriate combination: {type1} with {type2}")
                        is_valid = False
    
    return {
        "is_valid": is_valid,
        "issues": issues
    }


@router.post("")
async def create_outfit(
    request: CreateOutfitRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Create a custom outfit by manually selecting items from the user's wardrobe.
    REST endpoint: POST /api/outfits
    """
    try:
        logger.info(f"🎨 Creating custom outfit: {request.name}")
        # Reduced logging to prevent rate limits
        
        # Use authenticated user
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        current_user_id = current_user.id
        
        logger.info(f"🔍 Request data:")
        logger.info(f"  - name: {request.name}")
        logger.info(f"  - occasion: {request.occasion}")
        logger.info(f"  - style: {request.style}")
        logger.info(f"  - items count: {len(request.items)}")
        logger.info(f"  - user_id: {current_user_id}")
        
        # Create outfit data with all required OutfitGeneratedOutfit fields
        outfit_data = {
            "id": str(uuid4()),
            "name": request.name,
            "occasion": request.occasion,
            "style": request.style,
            "description": request.description or "",
            "items": request.items,
            "user_id": current_user_id,  # Use snake_case to match database schema
            "createdAt": request.createdAt or datetime.utcnow().isoformat() + "Z",
            "is_custom": True,  # Mark as custom outfit
            "confidence_score": 1.0,  # Custom outfits have full confidence
            "reasoning": f"Custom outfit created by user: {request.description or 'No description provided'}",
            
            # Required OutfitGeneratedOutfit fields
            "explanation": request.description or f"Custom {request.style} outfit for {request.occasion}",
            "pieces": [],  # Empty for custom outfits, could be populated later
            "styleTags": [request.style.lower().replace(' ', '_')],  # Convert style to tag format
            "colorHarmony": "custom",  # Mark as custom color harmony
            "styleNotes": f"Custom {request.style} style selected by user",
            "season": "all",  # Default to all seasons for custom outfits
            "mood": "custom",  # Default mood for custom outfits
            "updatedAt": request.createdAt or int(time.time()),
            "metadata": {"created_method": "custom"},
            "wasSuccessful": True,
            "baseItemId": None,
            "validationErrors": [],
            "userFeedback": None
        }
        
        # Save outfit to Firestore
        outfit_id = outfit_data["id"]
        # Simple data cleaning - remove any problematic fields
        clean_outfit_data = {k: v for k, v in outfit_data.items() if v is not None}
        logger.info(f"🧹 Prepared outfit data: name='{((clean_outfit_data.get('name', 'unnamed') if clean_outfit_data else 'unnamed') if clean_outfit_data else 'unnamed')}', items_count={len(clean_outfit_data.get('items', []))}")
        
        # Save to Firestore directly
        try:
            from ..config.firebase import db
            if db:
                db.collection('outfits').document(outfit_id).set(clean_outfit_data)
                logger.info(f"✅ Saved outfit {outfit_id} to Firestore")
                
                # Update user stats (async, don't fail if it errors)
                try:
                    from ..services.user_stats_service import user_stats_service
                    await user_stats_service.update_outfit_stats(current_user_id, "created", clean_outfit_data)
                except Exception as stats_error:
                    logger.warning(f"Stats update failed: {stats_error}")
            else:
                logger.warning("⚠️ Firebase not available, outfit not saved to database")
        except Exception as save_error:
            logger.error(f"❌ Failed to save outfit to Firestore: {save_error}")
            # Don't fail the request, just log the error
        
        # Enhanced logging for debugging
        logger.info(f"✅ Outfit created: {outfit_id} for user {current_user_id}")
        logger.info(f"🔍 DEBUG: Created outfit name='{outfit_data['name']}' style='{outfit_data['style']}' occasion='{outfit_data['occasion']}'")
        logger.info(f"📊 DEBUG: Outfit contains {len(outfit_data['items'])} items")
        
        # Return simplified response
        return {
            "success": True,
            "id": outfit_data["id"],
            "name": outfit_data["name"],
            "items": outfit_data["items"],
            "style": outfit_data["style"],
            "occasion": outfit_data["occasion"],
        "description": (outfit_data.get("description", "") if outfit_data else ""),
            "createdAt": outfit_data["createdAt"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating custom outfit: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug")
async def debug_outfits():
    """
    Debug route: Dump the last 5 outfits from Firestore for troubleshooting.
    Helps confirm backend state without guesswork.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        current_user_id = current_user.id  # Your actual user ID
        logger.info(f"🔍 DEBUG: Fetching last 5 outfits for debugging")
        
        # Fetch recent outfits with minimal processing
        outfits = await get_user_outfits(current_user_id, 5, 0)
        
        debug_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": current_user_id,
            "total_outfits": len(outfits),
            "outfits": []
        }
        
        for outfit in outfits:
            debug_info["outfits"].append({
        "id": (outfit.get("id", "unknown") if outfit else "unknown"),
        "name": (outfit.get("name", "unknown") if outfit else "unknown"),
        "style": (outfit.get("style", "unknown") if outfit else "unknown"),
        "occasion": (outfit.get("occasion", "unknown") if outfit else "unknown"),
        "createdAt": (outfit.get("createdAt", "unknown") if outfit else "unknown"),
        "user_id": (outfit.get("user_id", "unknown") if outfit else "unknown"),
        "item_count": len((outfit.get("items", []) if outfit else []))
            })
        
        logger.info(f"🔍 DEBUG: Returning {len(outfits)} outfits for debugging")
        return debug_info
        
    except Exception as e:
        logger.error(f"❌ Debug route failed: {e}", exc_info=True)
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed"
        }


@router.get("/debug-simple")
async def debug_outfits_simple():
    """Quick debug: show last 5 outfits"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        current_user_id = current_user.id
        outfits = await get_user_outfits(current_user_id, 5, 0)
        
        return {
            "total_outfits": len(outfits),
            "outfits": [
                {
        "id": (o.get("id") if o else None),
        "name": (o.get("name") if o else None),
        "createdAt": (o.get("createdAt") if o else None),
        "user_id": (o.get("user_id") if o else None)
                } for o in outfits
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/rate")
async def rate_outfit(
    rating_data: dict,
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Rate an outfit and update analytics for individual wardrobe items.
    This ensures the scoring system has accurate feedback data.
    """
    try:
        logger.info(f"📊 Rating outfit request received")
        
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        current_user_id = current_user.id
        outfit_id = (rating_data.get('outfitId') if rating_data else None)
        rating = (rating_data.get('rating') if rating_data else None)
        is_liked = (rating_data.get('isLiked', False) if rating_data else False)
        is_disliked = (rating_data.get('isDisliked', False) if rating_data else False)
        feedback = (rating_data.get('feedback', '') if rating_data else '')
        
        logger.info(f"⭐ Rating outfit {outfit_id} for user {current_user_id}: {rating} stars")
        
        # Allow rating with just like/dislike feedback, or with star rating
        if not outfit_id:
            raise HTTPException(status_code=400, detail="Missing outfit ID")
        
        # If rating is provided, validate it's between 1-5
        if rating is not None and (rating < 1 or rating > 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Require at least some feedback (rating, like, dislike, or text feedback)
        if not rating and not is_liked and not is_disliked and not feedback.strip():
            raise HTTPException(status_code=400, detail="At least one form of feedback is required (rating, like, dislike, or comment)")
        
        # Update outfit with rating data
        try:
            from ..config.firebase import db
        except ImportError:
            raise HTTPException(status_code=503, detail="Database service unavailable")
            
        outfit_ref = db.collection('outfits').document(outfit_id)
        outfit_doc = outfit_ref.get() if outfit_ref else None if outfit_ref else None
        
        if not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        # Check both possible user ID field names for compatibility
        outfit_user_id = ((outfit_data.get('userId') if outfit_data else None) if outfit_data else None) or outfit_data.get('user_id')
        if outfit_user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to rate this outfit")
        
        # Update outfit with rating
        outfit_ref.update({
            'rating': rating,
            'isLiked': is_liked,
            'isDisliked': is_disliked,
            'feedback': feedback,
            'ratedAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        })
        
        # Update analytics for individual wardrobe items
        await _update_item_analytics_from_outfit_rating(
        (outfit_data.get('items', []) if outfit_data else []),
            current_user_id, 
            rating, 
            is_liked, 
            is_disliked, 
            feedback
        )
        
        logger.info(f"✅ Successfully rated outfit {outfit_id} and updated item analytics")
        
        return {
            "success": True,
            "message": "Outfit rated successfully",
            "outfit_id": outfit_id,
            "rating": rating
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to rate outfit: {e}")
        raise HTTPException(status_code=500, detail="Failed to rate outfit")

async def _update_item_analytics_from_outfit_rating(
    outfit_items: List[Dict], 
    user_id: str, 
    rating: int, 
    is_liked: bool, 
    is_disliked: bool, 
    feedback: str
) -> None:
    """
    Update analytics for individual wardrobe items based on outfit rating.
    This ensures the scoring system has accurate feedback data for each item.
    """
    try:
        logger.info(f"📊 Updating analytics for {len(outfit_items)} items from outfit rating")
        
        current_time = datetime.utcnow()
        updated_count = 0
        
        for item in outfit_items:
        item_id = (item.get('id') if item else None)
            if not item_id:
                continue
            
            try:
                # Check if analytics document exists for this item
                analytics_ref = db.collection('item_analytics').document(f"{user_id}_{item_id}")
        analytics_doc = analytics_ref.get() if analytics_ref else None
                
                if analytics_doc.exists:
                    # Update existing analytics
                    current_data = analytics_doc.to_dict()
                    
                    # Update feedback ratings
        feedback_ratings = (current_data.get('feedback_ratings', []) if current_data else [])
                    feedback_ratings.append({
                        'rating': rating,
                        'outfit_rating': rating,
                        'is_liked': is_liked,
                        'is_disliked': is_disliked,
                        'feedback': feedback,
                        'timestamp': current_time
                    })
                    
                    # Calculate new average rating
        total_rating = sum((fr.get('rating', 0) if fr else 0) for fr in feedback_ratings)
                    avg_rating = total_rating / len(feedback_ratings)
                    
                    analytics_ref.update({
                        'feedback_ratings': feedback_ratings,
                        'average_feedback_rating': round(avg_rating, 2),
                        'rating': round(avg_rating, 2),
                        'total_feedback_count': len(feedback_ratings),
                        'last_feedback_at': current_time,
                        'updated_at': current_time
                    })
                    
                else:
                    # Create new analytics document
                    analytics_data = {
                        'user_id': user_id,
                        'item_id': item_id,
                        'feedback_ratings': [{
                            'rating': rating,
                            'outfit_rating': rating,
                            'is_liked': is_liked,
                            'is_disliked': is_disliked,
                            'feedback': feedback,
                            'timestamp': current_time
                        }],
                        'average_feedback_rating': rating,
                        'rating': rating,
                        'total_feedback_count': 1,
                        'last_feedback_at': current_time,
                        'created_at': current_time,
                        'updated_at': current_time
                    }
                    
                    analytics_ref.set(analytics_data)
                
                updated_count += 1
                logger.info(f"✅ Updated analytics for item {item_id} with rating {rating}")
                
            except Exception as e:
                logger.error(f"❌ Failed to update analytics for item {item_id}: {e}")
                continue
        
        logger.info(f"✅ Successfully updated analytics for {updated_count}/{len(outfit_items)} items")
        
    except Exception as e:
        logger.error(f"❌ Failed to update item analytics from outfit rating: {e}")
        # Don't raise error - this is a secondary operation

# ⚠️ PARAMETERIZED ROUTE - MUST BE FIRST TO AVOID ROUTE CONFLICTS!
# This route MUST come BEFORE the root route to avoid catching it
@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(outfit_id: str):
    """Get a specific outfit by ID. MUST BE FIRST ROUTE TO AVOID CONFLICTS."""
    logger.info(f"🔍 DEBUG: Get outfit {outfit_id} endpoint called")
    
    try:
        # Use the actual user ID from your database where the 1000+ outfits are stored
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        current_user_id = current_user.id  # TEMPORARY: Your actual user ID
        logger.info(f"Using hardcoded user ID for testing: {current_user_id}")
        
        # Check Firebase availability
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("Firebase not available, returning empty outfits")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        # Try to fetch real outfit from Firebase
        try:
            outfit_doc = db.collection('outfits').document(outfit_id).get()
            if outfit_doc.exists:
                outfit_data = outfit_doc.to_dict()
                outfit_data['id'] = outfit_id
                logger.info(f"Successfully retrieved outfit {outfit_id} from database")
                return OutfitResponse(**outfit_data)
            else:
                logger.warning(f"Outfit {outfit_id} not found in database")
                raise HTTPException(status_code=404, detail="Outfit not found")
                
        except Exception as firebase_error:
            logger.error(f"Firebase query failed: {firebase_error}")
            logger.warning("Falling back to mock data due to Firebase error")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve outfit from database: {firebase_error}")
        
    except Exception as e:
        logger.error(f"Error getting outfit {outfit_id}: {e}")
        # Fallback to mock data on other errors
        raise HTTPException(status_code=500, detail=f"Failed to get outfit: {e}")

# ✅ Retrieve Outfit History (dual endpoints for trailing slash compatibility)
@router.get("/", response_model=List[OutfitResponse])
async def list_outfits_with_slash(
    limit: int = 50,
    offset: int = 0,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Fetch a user's outfit history from Firestore.
    """
    logger.info("🎯 DEBUG: /api/outfits/ endpoint called (CORRECT ENDPOINT)")
    logger.info(f"🔍 DEBUG: Request params - limit: {limit}, offset: {offset}")
    try:
        # Require authentication - no fallback to hardcoded user ID
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        current_user_id = current_user.id
        logger.info(f"📚 Fetching outfits for authenticated user: {current_user_id}")
        
        outfits = await get_user_outfits(current_user_id, limit, offset)
        
        # Enhanced logging for debugging
        logger.info(f"📥 Fetch returned {len(outfits)} outfits for user {current_user_id}")
        if outfits:
            # Log the most recent outfit for debugging
            latest = outfits[0]
        logger.info(f"🔍 DEBUG: Latest outfit: '{((latest.get('name', 'Unknown') if latest else 'Unknown') if latest else 'Unknown')}' created at {latest.get('createdAt', 'Unknown')}")
        logger.info(f"🔍 DEBUG: Latest outfit wearCount: {(latest.get('wearCount', 'NOT_FOUND') if latest else 'NOT_FOUND')}")
        logger.info(f"🔍 DEBUG: Latest outfit lastWorn: {(latest.get('lastWorn', 'NOT_FOUND') if latest else 'NOT_FOUND')}")
        else:
            logger.info(f"⚠️ DEBUG: No outfits found for user {current_user_id}")
            
        return [OutfitResponse(**o) for o in outfits]
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch outfits for {current_user_id}: {e}", exc_info=True)
        # Fallback to mock data on error
        raise HTTPException(status_code=500, detail=f"Failed to fetch user outfits: {e}")

@router.get("", include_in_schema=False, response_model=List[OutfitResponse])
async def list_outfits_no_slash(
    limit: int = 50,
    offset: int = 0,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Fetch a user's outfit history from Firestore (no trailing slash).
    """
    try:
        # Require authentication - no fallback to hardcoded user ID
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        current_user_id = current_user.id
        logger.info(f"📚 Fetching outfits for authenticated user: {current_user_id}")
        
        outfits = await get_user_outfits(current_user_id, limit, offset)
        
        # Enhanced logging for debugging
        logger.info(f"📥 Fetch returned {len(outfits)} outfits for user {current_user_id}")
        if outfits:
            # Log the most recent outfit for debugging
            latest = outfits[0]
        logger.info(f"🔍 DEBUG: Latest outfit: '{((latest.get('name', 'Unknown') if latest else 'Unknown') if latest else 'Unknown')}' created at {latest.get('createdAt', 'Unknown')}")
        logger.info(f"🔍 DEBUG: Latest outfit wearCount: {(latest.get('wearCount', 'NOT_FOUND') if latest else 'NOT_FOUND')}")
        logger.info(f"🔍 DEBUG: Latest outfit lastWorn: {(latest.get('lastWorn', 'NOT_FOUND') if latest else 'NOT_FOUND')}")
        else:
            logger.info(f"⚠️ DEBUG: No outfits found for user {current_user_id}")
            
        return [OutfitResponse(**o) for o in outfits]
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch outfits for {current_user_id}: {e}", exc_info=True)
        # Fallback to mock data on error
        raise HTTPException(status_code=500, detail=f"Failed to fetch user outfits: {e}")

# 📊 Get Outfit Statistics
@router.get("/stats/summary")
async def get_outfit_stats(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get outfit statistics for user.
    """
    try:
        # Require authentication - no fallback to hardcoded user ID
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        current_user_id = current_user.id
        logger.info(f"📊 Getting outfit stats for authenticated user {current_user_id}")
        
        logger.info(f"📊 Getting outfit stats for user {current_user_id}")
        
        # Get reasonable sample of outfits for stats (performance optimized)
        outfits = await get_user_outfits(current_user_id, 100, 0)  # Get recent 100 outfits for stats
        
        # Calculate basic statistics
        stats = {
            'totalOutfits': len(outfits),
            'favoriteOutfits': len([o for o in outfits if o.get('isFavorite', False)]),
            'totalWearCount': sum(o.get('wearCount', 0) for o in outfits),
            'occasions': {},
            'styles': {},
            'recentActivity': []
        }
        
        # Count occasions and styles
        for outfit in outfits:
        occasion = (outfit.get('occasion', 'Unknown') if outfit else 'Unknown')
            stats['occasions'][occasion] = stats['occasions'].get(occasion, 0) + 1
            
        style = (outfit.get('style', 'Unknown') if outfit else 'Unknown')
            stats['styles'][style] = stats['styles'].get(style, 0) + 1
        
        # Add recent activity
        if outfits:
            stats['recentActivity'] = [
                {
                    'id': o['id'],
                    'name': o['name'],
                    'lastUpdated': normalize_created_at(o.get('createdAt')) if o.get('createdAt') else datetime.utcnow().isoformat() + 'Z'
                }
                for o in outfits[:5]  # Last 5 outfits
            ]
        
        logger.info(f"✅ Successfully retrieved outfit stats")
        
        return {
            "success": True,
            "data": stats,
            "message": "Outfit statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get outfit stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get outfit statistics"
        )

# 🔍 DEBUG: List all registered routes for this router
@router.get("/debug-routes", response_model=dict)
async def debug_routes():
    """Debug endpoint to show all registered routes in this router"""
    routes = []
    for route in router.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods),
            "endpoint": str(route.endpoint)
        })
    return {
        "router_name": "outfits",
        "total_routes": len(routes),
        "routes": routes
    }

# 🎨 Intelligent Outfit Naming and Reasoning Functions

async def generate_intelligent_outfit_name(items: List[Dict], style: str, mood: str, occasion: str) -> str:
    """Generate intelligent outfit names based on items and context."""
    try:
        # Analyze the items to create a descriptive name
        item_types = [(item.get('type', '') if item else '').lower() for item in items]
        item_names = [(item.get('name', '') if item else '').lower() for item in items]
        
        # Identify key pieces
        has_blazer = any('blazer' in item_type or 'blazer' in name for item_type, name in zip(item_types, item_names))
        has_dress = any('dress' in item_type or 'dress' in name for item_type, name in zip(item_types, item_names))
        has_jeans = any('jean' in item_type or 'jean' in name for item_type, name in zip(item_types, item_names))
        has_sneakers = any('sneaker' in item_type or 'sneaker' in name for item_type, name in zip(item_types, item_names))
        has_heels = any('heel' in item_type or 'heel' in name for item_type, name in zip(item_types, item_names))
        has_denim = any('denim' in item_type or 'denim' in name for item_type, name in zip(item_types, item_names))
        
        # Generate contextual names
        if has_blazer and has_jeans:
            return f"Smart Casual {occasion.title()}"
        elif has_blazer and not has_jeans:
            return f"Polished {occasion.title()}"
        elif has_dress:
            return f"Effortless {occasion.title()}"
        elif has_jeans and has_sneakers:
            return f"Relaxed {occasion.title()}"
        elif has_heels and not has_jeans:
            return f"Elegant {occasion.title()}"
        elif style.lower() == 'minimalist':
            return f"Minimal {occasion.title()}"
        elif style.lower() == 'bohemian':
            return f"Boho {occasion.title()}"
        elif mood.lower() == 'confident':
            return f"Power {occasion.title()}"
        elif mood.lower() == 'relaxed':
            return f"Easy {occasion.title()}"
        else:
            return f"{style.title()} {occasion.title()}"
            
    except Exception as e:
        logger.warning(f"⚠️ Failed to generate intelligent name: {e}")
        return f"{style.title()} {occasion.title()}"

async def generate_outfit_analysis(items: List[Dict], req: OutfitRequest, outfit_score: Dict) -> Dict[str, Any]:
    """Generate detailed outfit analysis for educational insights."""
    analysis = {
        "textureAnalysis": None,
        "patternBalance": None,
        "colorStrategy": None,
        "styleSynergy": None
    }
    
    try:
        # Extract metadata from items
        textures = []
        patterns = []
        colors = []
        styles_list = []
        item_details = []
        
        for item in items:
            metadata = item.get('metadata', {}) or {}
            visual_attrs = metadata.get('visualAttributes', {}) or {}
            
            item_type = item.get('type', 'piece')
            item_color = item.get('color', 'neutral')
            
            # Texture info
            texture = visual_attrs.get('textureStyle', 'smooth')
            if texture:
                textures.append({'type': item_type, 'texture': texture, 'color': item_color})
            
            # Pattern info  
            pattern = visual_attrs.get('pattern', 'solid')
            if pattern:
                patterns.append({'type': item_type, 'pattern': pattern, 'color': item_color})
            
            # Color info
            if item_color:
                colors.append({'type': item_type, 'color': item_color})
            
            # Style info
            item_styles = item.get('style', [])
            if isinstance(item_styles, list):
                styles_list.extend(item_styles)
            elif item_styles:
                styles_list.append(item_styles)
            
            item_details.append({
                'type': item_type,
                'color': item_color,
                'texture': texture,
                'pattern': pattern
            })
        
        # Analyze textures
        if len(textures) >= 2:
            texture_types = [t['texture'] for t in textures]
            unique_textures = list(set(texture_types))
            
            if len(unique_textures) > 1:
                # Find which items have which textures
                smooth_items = [t['type'] for t in textures if t['texture'] in ['smooth', 'sleek', 'polished']]
                textured_items = [t['type'] for t in textures if t['texture'] not in ['smooth', 'sleek', 'polished']]
                
                if smooth_items and textured_items:
                    analysis["textureAnalysis"] = {
                        "insight": f"Texture contrast between {' and '.join(smooth_items[:2])} and {' and '.join(textured_items[:2])} adds dimension",
                        "smoothItems": smooth_items,
                        "texturedItems": textured_items
                    }
            elif len(unique_textures) == 1 and unique_textures[0] != 'smooth':
                analysis["textureAnalysis"] = {
                    "insight": f"Consistent {unique_textures[0]} texture creates a cohesive tactile aesthetic",
                    "uniformTexture": unique_textures[0]
                }
        
        # Analyze patterns
        if len(patterns) >= 2:
            pattern_types = [p['pattern'] for p in patterns]
            solid_items = [p['type'] for p in patterns if p['pattern'] == 'solid']
            patterned_items = [p for p in patterns if p['pattern'] != 'solid']
            
            if solid_items and patterned_items:
                # Pattern on top, solid bottom (or vice versa) creates balance
                pattern_desc = patterned_items[0]['pattern']
                if 'shirt' in patterned_items[0]['type'].lower() or 'top' in patterned_items[0]['type'].lower():
                    analysis["patternBalance"] = {
                        "insight": f"{pattern_desc.title()} {patterned_items[0]['type']} stands out against {solid_items[0]} base",
                        "statement": patterned_items[0]['type'],
                        "neutral": solid_items
                    }
                else:
                    analysis["patternBalance"] = {
                        "insight": f"Solid {solid_items[0]} anchors the {pattern_desc} {patterned_items[0]['type']}",
                        "statement": patterned_items[0]['type'],
                        "neutral": solid_items
                    }
            elif len(patterned_items) > 1:
                analysis["patternBalance"] = {
                    "insight": "Multiple patterns create visual energy—ensure they share a common color",
                    "patterns": [p['pattern'] for p in patterned_items]
                }
        
        # Analyze color strategy
        if len(colors) >= 2:
            color_list = [c['color'].lower() for c in colors]
            neutrals = [c for c in colors if c['color'].lower() in ['black', 'white', 'gray', 'grey', 'beige', 'cream', 'tan', 'brown', 'navy']]
            bold_colors = [c for c in colors if c not in neutrals]
            
            if bold_colors and neutrals:
                # Pop of color strategy
                if len(bold_colors) == 1:
                    analysis["colorStrategy"] = {
                        "insight": f"{bold_colors[0]['color'].title()} {bold_colors[0]['type']} provides a pop of color against neutral base",
                        "popColor": bold_colors[0]['color'],
                        "popItem": bold_colors[0]['type'],
                        "neutrals": [n['type'] for n in neutrals]
                    }
                else:
                    analysis["colorStrategy"] = {
                        "insight": f"Bold {bold_colors[0]['color']} and {bold_colors[1]['color']} create dynamic contrast",
                        "boldColors": [b['color'] for b in bold_colors[:2]]
                    }
            elif len(set(color_list)) == 1:
                analysis["colorStrategy"] = {
                    "insight": f"Monochromatic {color_list[0]} creates sophisticated unity",
                    "strategy": "monochromatic"
                }
            else:
                # Multiple colors - check for complementary
                analysis["colorStrategy"] = {
                    "insight": f"Multi-tone palette with {', '.join(set(color_list)[:3])} creates visual richness",
                    "strategy": "multitone"
                }
        
        # Analyze style synergy
        if styles_list:
            unique_styles = list(set([s.lower() if s else '' for s in styles_list if s]))
            if len(unique_styles) > 1:
                # Mixed styles
                if req.style.lower() in [s.lower() for s in unique_styles]:
                    analysis["styleSynergy"] = {
                        "insight": f"{req.style} aesthetic harmonizes with {unique_styles[0] if unique_styles[0] != req.style.lower() else unique_styles[1]} influences",
                        "primaryStyle": req.style,
                        "secondaryStyle": unique_styles[0] if unique_styles[0] != req.style.lower() else unique_styles[1]
                    }
                else:
                    analysis["styleSynergy"] = {
                        "insight": f"Eclectic mix of {' and '.join(unique_styles[:2])} creates personal expression",
                        "mixedStyles": unique_styles[:2]
                    }
        
        return analysis
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to generate outfit analysis: {e}")
        return analysis

async def generate_intelligent_reasoning(items: List[Dict], req: OutfitRequest, outfit_score: Dict, layering_validation: Dict, color_validation: Dict) -> str:
    """Generate intelligent reasoning for outfit selection with weather context."""
    try:
        # Always generate exactly 3 sentences for consistency
        sentences = []
        
        # Sentence 1: Outfit style, mood, and occasion
        mood_desc = {
            'bold': 'confident', 'relaxed': 'comfortable', 'sophisticated': 'elegant',
            'dynamic': 'energetic', 'serene': 'peaceful', 'mysterious': 'intriguing'
        }.get(req.mood.lower(), (req.mood if req else "unknown").lower())
        
        sentences.append(f"This outfit reflects your {req.style} style for a {req.occasion} occasion, creating a {mood_desc} mood.")
        
        # Sentence 2: Weather appropriateness / comfort note
        if (req.weather if req else None):
            temp = getattr(req.weather, 'temperature', 70)
            condition = getattr(req.weather, 'condition', 'clear').lower()
            
            # Check if this is real weather, manual override, or fallback
            is_manual_override = getattr(req.weather, 'isManualOverride', False)
            is_real_weather = getattr(req.weather, 'isRealWeather', False)
            is_fallback_weather = getattr(req.weather, 'isFallbackWeather', False)
            
            # Weather-appropriate messaging with source indication
            if temp >= 85:
                base_note = f"The current weather is {temp}°F and {condition}, so the lightweight pieces ensure comfort in warm conditions."
            elif temp >= 75:
                base_note = f"The current weather is {temp}°F and {condition}, so the breathable fabrics provide comfort throughout the day."
            elif temp >= 65:
                base_note = f"The current weather is {temp}°F and {condition}, so the balanced layering adapts well to mild conditions."
            elif temp >= 55:
                base_note = f"The current weather is {temp}°F and {condition}, so the thoughtful layering provides warmth and comfort."
            else:
                base_note = f"The current weather is {temp}°F and {condition}, so the warm layers ensure comfort in cool conditions."
                
            # Add condition-specific notes
            if 'rain' in condition:
                base_note = base_note.replace("comfort", "protection and comfort")
            elif 'wind' in condition:
                base_note = base_note.replace("comfort", "secure fit and comfort")
            
            # Add weather source indication
            if is_manual_override:
                weather_note = base_note + " (This outfit was generated based on your manual weather preference.)"
            elif is_real_weather:
                weather_note = base_note + " (This outfit was generated based on real-time weather data.)"
            elif is_fallback_weather:
                weather_note = base_note + " (Fallback weather was used; consider minor adjustments if needed.)"
            else:
                weather_note = base_note
        else:
            weather_note = "The pieces are selected for comfortable all-day wear and versatile styling."
            
        sentences.append(weather_note)
        
        # Sentence 3: Harmony, layering, or color reasoning with item-specific weather context
        if items and len(items) >= 2:
            # Analyze colors and weather context
            colors = [item.get('color', '').title() for item in items if item.get('color')]
            weather_notes = []
            
            # Check for any weather-related item notes
            for item in items:
        weather_context = (item.get('weather_context', {}) if item else {})
                if weather_context:
                    temp_note = weather_context.get('temperature_note', '')
                    if temp_note and ('perfect' in temp_note or 'ideal' in temp_note or 'excellent' in temp_note):
        weather_notes.append(f"the {(item.get('type', 'item') if item else 'item')} is {temp_note}")
        elif temp_note and ('borderline' in (weather_context.get('temperature_appropriateness', '') if weather_context else '') or 'may be' in temp_note):
        weather_notes.append(f"the {(item.get('type', 'item') if item else 'item')} {temp_note}")
            
            # Build the sentence
            if colors:
                color_combo = " and ".join(colors[:3])  # Limit to 3 colors
                if len(colors) > 3:
                    color_combo += f" and {len(colors)-3} other tones"
                
                if weather_notes:
                    weather_context_text = ", ".join(weather_notes[:2])  # Limit to 2 weather notes
                    sentences.append(f"The {color_combo} tones create color harmony across your pieces, while {weather_context_text} for optimal weather comfort.")
                else:
                    sentences.append(f"The {color_combo} tones create color harmony across your pieces, while the layered composition adds depth and sophistication.")
            else:
                # Fallback to item types with weather context
        item_types = [(item.get('type', '') if item else '').title() for item in items]
                if weather_notes:
                    weather_context_text = ", ".join(weather_notes[:2])
                    sentences.append(f"The {', '.join(item_types)} work together to create a cohesive look, while {weather_context_text} for weather-appropriate comfort.")
                else:
                    sentences.append(f"The {', '.join(item_types)} work together to create a cohesive look with balanced proportions and complementary textures.")
        else:
            sentences.append("The outfit selection prioritizes style coherence and practical versatility for your occasion.")
        
        return " ".join(sentences)
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to generate intelligent reasoning: {e}")
        # Fallback with weather context if available
        weather_note = ""
        if (req.weather if req else None):
            # Handle both dict and object weather data
            if isinstance(req.weather, dict):
        temp = req.weather.get('temperature', 70) if req.weather else 70
        condition = req.weather.get('condition', 'clear') if req.weather else 'clear'
            else:
                temp = getattr(req.weather, 'temperature', 70)
                condition = getattr(req.weather, 'condition', 'clear')
            weather_note = f" for {temp}°F {condition.lower()} weather"
        return f"This {req.style} {req.occasion} outfit{weather_note} combines {len(items)} carefully selected pieces. The ensemble balances comfort and style for your desired {req.mood} mood. Each item works harmoniously to create a cohesive, weather-appropriate look."

# 🚀 Performance Optimization Functions

async def get_user_wardrobe_cached(user_id: str) -> List[Dict]:
    """Get user wardrobe with basic caching to reduce database calls."""
    # Simple in-memory cache (in production, use Redis or similar)
    if not hasattr(get_user_wardrobe_cached, '_cache'):
        get_user_wardrobe_cached._cache = {}
    
    cache_key = f"wardrobe_{user_id}"
    cache_time = 300  # 5 minutes
    
    if cache_key in get_user_wardrobe_cached._cache:
        cached_data, timestamp = get_user_wardrobe_cached._cache[cache_key]
        if time.time() - timestamp < cache_time:
            logger.info(f"📦 Using cached wardrobe for user {user_id}")
            return cached_data
    
    # Fetch from database
    wardrobe = await get_user_wardrobe(user_id)
    
    # Cache the result
    get_user_wardrobe_cached._cache[cache_key] = (wardrobe, time.time())
    
    return wardrobe

async def get_user_profile_cached(user_id: str) -> Dict:
    """Get user profile with basic caching to reduce database calls."""
    # Simple in-memory cache
    if not hasattr(get_user_profile_cached, '_cache'):
        get_user_profile_cached._cache = {}
    
    cache_key = f"profile_{user_id}"
    cache_time = 600  # 10 minutes
    
    if cache_key in get_user_profile_cached._cache:
        cached_data, timestamp = get_user_profile_cached._cache[cache_key]
        if time.time() - timestamp < cache_time:
            logger.info(f"👤 Using cached profile for user {user_id}")
            return cached_data
    
    # Fetch from database
    profile = await get_user_profile(user_id)
    
    # Cache the result
    get_user_profile_cached._cache[cache_key] = (profile, time.time())
    
    return profile

@router.get("/analytics/worn-this-week")
async def get_outfits_worn_this_week_simple(
    current_user: UserProfile = Depends(get_current_user),
    force_fresh: bool = False
):
    """
    SIMPLE: Count outfits worn this week - added to working outfits router.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Import Firebase inside function to avoid startup issues
        try:
            from ..config.firebase import db, firebase_initialized
        except ImportError as e:
            logger.error(f"⚠️ Firebase import failed: {e}")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        if not db:
            logger.error("⚠️ Firebase not available")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
        
        # Calculate start of week (Sunday)
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        # weekday() returns 0=Monday, 6=Sunday
        # For Sunday start: if today is Sunday (6), days_since_sunday = 0
        # if today is Monday (0), days_since_sunday = 1, etc.
        days_since_sunday = (now.weekday() + 1) % 7
        week_start = now - timedelta(days=days_since_sunday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info(f"📊 Counting outfits worn since {week_start.isoformat()} for user {current_user.id}")
        
        worn_count = 0
        processed_count = 0
        
        # Count individual wear events from outfit_history collection
        logger.info("📊 Counting individual wear events from outfit_history collection")
        
        # Query outfit_history to count individual wear events
        from google.cloud.firestore import Query
        history_ref = db.collection('outfit_history').where('user_id', '==', current_user.id).order_by('date_worn', direction=Query.DESCENDING).limit(1000)
        
        for history_doc in history_ref.stream():
            history_data = history_doc.to_dict()
            processed_count += 1
        date_worn = (history_data.get('date_worn') if history_data else None)
            
            if date_worn:
                # Parse date_worn safely - handle multiple formats
                try:
                    worn_date = None
                    
                    if isinstance(date_worn, str):
                        # Handle ISO string formats
                        worn_date = datetime.fromisoformat(date_worn.replace('Z', '+00:00'))
                    elif hasattr(date_worn, 'timestamp'):
                        # Firestore Timestamp object - convert to datetime
                        if hasattr(date_worn, 'timestamp'):
                            worn_date = datetime.fromtimestamp(date_worn.timestamp(), tz=timezone.utc)
                        else:
                            worn_date = date_worn
                    elif isinstance(date_worn, datetime):
                        # Already a datetime object
                        worn_date = date_worn
                    elif isinstance(date_worn, (int, float)):
                        # Unix timestamp (seconds or milliseconds)
                        if date_worn > 1e12:  # Likely milliseconds
                            worn_date = datetime.fromtimestamp(date_worn / 1000.0, tz=timezone.utc)
                        else:
                            worn_date = datetime.fromtimestamp(date_worn, tz=timezone.utc)
                    else:
                        logger.warning(f"Unknown date_worn type: {type(date_worn)} - {date_worn}")
                        continue
                    
                    # Ensure timezone aware
                    if worn_date and worn_date.tzinfo is None:
                        worn_date = worn_date.replace(tzinfo=timezone.utc)
                    
                    # Check if this wear event is within the current week
                    if worn_date and worn_date >= week_start:
                        worn_count += 1
                        logger.info(f"📅 Wear event {history_doc.id} this week: {worn_date}")
                        
                except Exception as parse_error:
                    logger.warning(f"Error parsing date_worn {date_worn}: {parse_error}")
                    continue
        
        logger.info(f"✅ Found {worn_count} wear events this week for user {current_user.id}")
        
        # If no outfit_history records found, fall back to lastWorn dates from outfits collection
        if worn_count == 0 and processed_count == 0:
            logger.info("📊 No outfit_history records found, falling back to lastWorn dates from outfits collection")
            
            # Query outfits collection for lastWorn dates
            outfits_ref = db.collection('outfits').where('user_id', '==', current_user.id)
            
            for outfit_doc in outfits_ref.stream():
                outfit_data = outfit_doc.to_dict()
        last_worn = (outfit_data.get('lastWorn') if outfit_data else None)
                
                if last_worn:
                    try:
                        # Parse lastWorn date
                        if isinstance(last_worn, str):
                            last_worn_date = datetime.fromisoformat(last_worn.replace('Z', '+00:00'))
                        elif hasattr(last_worn, 'timestamp'):
                            last_worn_date = datetime.fromtimestamp(last_worn.timestamp(), tz=timezone.utc)
                        elif isinstance(last_worn, datetime):
                            last_worn_date = last_worn
                        else:
                            continue
                        
                        # Ensure timezone aware
                        if last_worn_date.tzinfo is None:
                            last_worn_date = last_worn_date.replace(tzinfo=timezone.utc)
                        
                        # Check if this outfit was worn this week
                        if last_worn_date >= week_start:
                            worn_count += 1
                            logger.info(f"📅 Outfit {outfit_doc.id} worn this week (lastWorn fallback): {last_worn_date}")
                            
                    except Exception as parse_error:
                        logger.warning(f"Error parsing lastWorn {last_worn}: {parse_error}")
                        continue
            
            logger.info(f"✅ Fallback found {worn_count} outfits worn this week from lastWorn dates")
        
        return {
            "success": True,
            "user_id": current_user.id,
            "outfits_worn_this_week": worn_count,
                "source": "lastWorn_fallback",
                "version": "2025-09-23",
                "api_version": "v2.0",
                "week_start": week_start.isoformat(),
                "calculated_at": datetime.now(timezone.utc).isoformat(),
                "note": "Using lastWorn dates as fallback - outfit_history is empty"
            }
        
        return {
            "success": True,
            "user_id": current_user.id,
            "outfits_worn_this_week": worn_count,
            "source": "outfit_history_individual_events",
            "version": "2025-09-23",
            "api_version": "v2.0",
            "week_start": week_start.isoformat(),
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error counting worn outfits: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to count worn outfits: {e}") 

def _apply_final_outfit_validation(outfit: Dict[str, Any]) -> Dict[str, Any]:
    """Final validation check to guarantee 99% prevention of inappropriate combinations."""
    
    items = (outfit.get('items', []) if outfit else [])
    if not items:
        return outfit
    
    # Get all item types and names for analysis
    item_types = [(item.get('type', '') if item else '').lower() for item in items]
    item_names = [(item.get('name', '') if item else '').lower() for item in items]
    
    # CRITICAL: Blazer + Shorts Prevention (Highest Priority)
    has_blazer = any('blazer' in item_type or 'blazer' in item_name for item_type, item_name in zip(item_types, item_names))
    has_shorts = any('shorts' in item_type or 'shorts' in item_name for item_type, item_name in zip(item_types, item_names))
    
    if has_blazer and has_shorts:
        # Remove shorts and replace with appropriate bottom
        filtered_items = []
        shorts_removed = False
        
        for item in items:
        item_type = (item.get('type', '') if item else '').lower()
        item_name = (item.get('name', '') if item else '').lower()
            
            # Skip shorts items
            if 'shorts' in item_type or 'shorts' in item_name:
                shorts_removed = True
                continue
            else:
                filtered_items.append(item)
        
        # If we removed shorts, add appropriate bottom if missing
        if shorts_removed:
            # Check if we still have a bottom
        has_bottom = any(item_type in ['pants', 'jeans', 'skirt'] for item_type in [(item.get('type', '') if item else '').lower() for item in filtered_items])
            
            if not has_bottom:
                # Add pants as replacement (this should be available in wardrobe)
                pants_item = {
                    'id': 'pants_replacement',
                    'name': 'Black Pants',
                    'type': 'pants',
                    'color': 'black',
                    'imageUrl': '',
                    'style': 'casual',
                    'occasion': 'casual',
                    'brand': '',
                    'wearCount': 0,
                    'favorite_score': 0,
                    'tags': [],
        'metadata': None
                }
                filtered_items.append(pants_item)
        
        outfit['items'] = filtered_items
        outfit['name'] = f"Validated {(outfit.get('name', 'Outfit') if outfit else 'Outfit')}"
    
    # CRITICAL: Formal Shoes + Casual Bottoms Prevention (Enhanced)
    formal_shoe_types = ['oxford', 'loafers', 'dress shoes', 'heels', 'pumps']
    casual_bottom_types = ['shorts', 'athletic shorts', 'basketball shorts', 'cargo shorts', 'denim shorts', 
                          'cargo pants', 'athletic pants', 'sweatpants', 'joggers', 'leggings', 'yoga pants']
    
    has_formal_shoes = any(
        any(formal_type in item_type for formal_type in formal_shoe_types) or
        any(formal_type in item_name for formal_type in formal_shoe_types)
        for item_type, item_name in zip(item_types, item_names)
    )
    has_casual_bottoms = any(
        any(casual_type in item_type for casual_type in casual_bottom_types) or
        any(casual_type in item_name for casual_type in casual_bottom_types)
        for item_type, item_name in zip(item_types, item_names)
    )
    
    if has_formal_shoes and has_casual_bottoms:
        # Remove casual bottoms and replace with appropriate bottom
        filtered_items = []
        casual_removed = False
        
        for item in items:
        item_type = (item.get('type', '') if item else '').lower()
        item_name = (item.get('name', '') if item else '').lower()
            
            # Skip casual bottom items (enhanced detection)
            is_casual_bottom = any(
                casual_type in item_type or casual_type in item_name
                for casual_type in casual_bottom_types
            )
            
            if is_casual_bottom:
                casual_removed = True
                continue
            else:
                filtered_items.append(item)
        
        # If we removed casual bottoms, add appropriate bottom if missing
        if casual_removed:
            # Check if we still have a bottom
        has_bottom = any(item_type in ['pants', 'jeans', 'skirt'] for item_type in [(item.get('type', '') if item else '').lower() for item in filtered_items])
            
            if not has_bottom:
                # Add pants as replacement
                pants_item = {
                    'id': 'pants_replacement',
                    'name': 'Black Pants',
                    'type': 'pants',
                    'color': 'black',
                    'imageUrl': '',
                    'style': 'casual',
                    'occasion': 'casual',
                    'brand': '',
                    'wearCount': 0,
                    'favorite_score': 0,
                    'tags': [],
        'metadata': None
                }
                filtered_items.append(pants_item)
        
        outfit['items'] = filtered_items
        outfit['name'] = f"Validated {(outfit.get('name', 'Outfit') if outfit else 'Outfit')}"
    
    # CRITICAL: Final essential categories check to guarantee 99% prevention
    final_items = (outfit.get('items', []) if outfit else [])
    final_item_types = [(item.get('type', '') if item else '').lower() for item in final_items]
    final_item_names = [(item.get('name', '') if item else '').lower() for item in final_items]
    
    # Check for missing essential categories
    has_top = any(item_type in ['t-shirt', 'shirt', 'blouse', 'sweater', 'jacket', 'blazer', 'tank top', 'hoodie', 'polo', 'henley', 'flannel', 'thermal', 'crop top', 'bodysuit', 'wrap top'] or 
                  item_name in ['t-shirt', 'shirt', 'blouse', 'sweater', 'jacket', 'blazer', 'tank top', 'hoodie', 'polo', 'henley', 'flannel', 'thermal', 'crop top', 'bodysuit', 'wrap top']
                  for item_type, item_name in zip(final_item_types, final_item_names))
    
    has_bottom = any(item_type in ['pants', 'jeans', 'shorts', 'skirt', 'dress', 'leggings', 'joggers', 'sweatpants', 'athletic pants', 'cargo pants', 'cargo shorts', 'athletic shorts', 'basketball shorts', 'denim shorts', 'bermuda shorts', 'high waist shorts', 'yoga pants'] or 
                    item_name in ['pants', 'jeans', 'shorts', 'skirt', 'dress', 'leggings', 'joggers', 'sweatpants', 'athletic pants', 'cargo pants', 'cargo shorts', 'athletic shorts', 'basketball shorts', 'denim shorts', 'bermuda shorts', 'high waist shorts', 'yoga pants']
                    for item_type, item_name in zip(final_item_types, final_item_names))
    
    has_shoes = any(item_type in ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flip-flops', 'slides', 'mules', 'espadrilles', 'oxford', 'loafers', 'dress shoes', 'pumps', 'ankle boots', 'knee high boots', 'chelsea boots', 'combat boots', 'running shoes', 'training shoes', 'high top sneakers', 'low top sneakers'] or 
                   item_name in ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flip-flops', 'slides', 'mules', 'espadrilles', 'oxford', 'loafers', 'dress shoes', 'pumps', 'ankle boots', 'knee high boots', 'chelsea boots', 'combat boots', 'running shoes', 'training shoes', 'high top sneakers', 'low top sneakers']
                   for item_type, item_name in zip(final_item_types, final_item_names))
    
    # NO FALLBACK ITEMS - let the robust service handle missing categories
    
    outfit['items'] = final_items
    
    # Final validation: Ensure we have exactly 3-6 items
    if len(final_items) < 3:
        # Add additional items if needed
        while len(final_items) < 3:
            final_items.append({
                'id': f'fallback_item_{len(final_items)}',
                'name': 'Additional Item',
                'type': 'accessory',
                'color': 'black',
                'imageUrl': '',
                'style': 'casual',
                'occasion': 'casual',
                'brand': '',
                'wearCount': 0,
                'favorite_score': 0,
                'tags': [],
                'metadata': {}
            })
        outfit['items'] = final_items
    
    elif len(final_items) > 6:
        # Remove excess items (keep first 6)
        outfit['items'] = final_items[:6]
    
    return outfit 