"""
Outfit management endpoints - Single canonical generator with bulletproof consistency.
All outfits are generated and saved through the same pipeline.
"""

import logging
import urllib.parse
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["outfits"]
)
security = HTTPBearer()

# Firebase imports with graceful fallback
try:
    from ..config.firebase import db, firebase_initialized
    from ..auth.auth_service import get_current_user_optional
    from ..custom_types.profile import UserProfile
    from ..custom_types.outfit import OutfitGeneratedOutfit
    FIREBASE_AVAILABLE = True
    logger.info("✅ Firebase modules imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Firebase import failed: {e}")
    FIREBASE_AVAILABLE = False
    db = None
    firebase_initialized = False
    # Create a mock get_current_user_optional function
    def get_current_user_optional():
        return None
else:
    try:
        from firebase_admin import firestore
        db = firestore.client()
        firebase_initialized = True
        FIREBASE_AVAILABLE = True
        logger.info("✅ Firebase successfully imported and initialized")
    except Exception as e:
        logger.error(f"❌ Firebase import error: {e}")
        FIREBASE_AVAILABLE = False
        db = None
        firebase_initialized = False
        # Create a mock get_current_user_optional function
        def get_current_user_optional():
            return None

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

# Real outfit generation logic with AI and user wardrobe
async def generate_outfit_logic(req: OutfitRequest, user_id: str) -> Dict[str, Any]:
    """Real outfit generation logic using user's wardrobe and AI recommendations."""
    logger.info(f"🎨 Generating outfit for user {user_id}: {req.style}, {req.mood}, {req.occasion}")
    
    try:
        # 1. Get user's wardrobe items from Firestore
        wardrobe_items = await get_user_wardrobe(user_id)
        logger.info(f"📦 Found {len(wardrobe_items)} items in user's wardrobe")
        
        # 2. Get user's style profile
        user_profile = await get_user_profile(user_id)
        logger.info(f"👤 Retrieved user profile for {user_id}")
        
        # ENHANCED: Validate style-gender compatibility
        if user_profile and user_profile.get('gender'):
            style_validation = await validate_style_gender_compatibility(req.style, user_profile.get('gender'))
            if not style_validation.get('is_compatible'):
                logger.warning(f"⚠️ Style-gender compatibility issue: {style_validation.get('warning')}")
                # For now, we'll continue but log the warning
                # In the future, we could suggest alternatives or reject the request
        
        # 3. Generate outfit using AI logic
        logger.info(f"🔍 DEBUG: About to call generate_ai_outfit with {len(wardrobe_items)} items")
        outfit = await generate_ai_outfit(wardrobe_items, user_profile, req)
        logger.info(f"✨ Generated outfit: {outfit['name']}")
        logger.info(f"🔍 DEBUG: Outfit items count: {len(outfit.get('items', []))}")
        
        return outfit
        
    except Exception as e:
        logger.warning(f"⚠️ Outfit generation failed, using fallback: {e}")
        # Fallback to basic generation if AI fails
        return await generate_fallback_outfit(req, user_id)

async def validate_style_gender_compatibility(style: str, user_gender: str) -> Dict[str, Any]:
    """Validate if the requested style is appropriate for the user's gender."""
    logger.info(f"🔍 DEBUG: Validating style '{style}' for gender '{user_gender}'")
    
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

async def validate_outfit_composition(items: List[Dict], occasion: str) -> List[Dict]:
    """Validate and ensure outfit has required components."""
    logger.info(f"🔍 DEBUG: Validating outfit composition for {occasion} occasion")
    
    # Define required categories for different occasions
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
    
    # Get default requirements
    default_required = ["top", "bottom"]
    required = required_categories.get(occasion.lower(), default_required)
    
    logger.info(f"🔍 DEBUG: Required categories for {occasion}: {required}")
    
    # Categorize items
    categorized_items = {}
    for item in items:
        item_type = item.get('type', '').lower()
        category = get_item_category(item_type)
        
        if category not in categorized_items:
            categorized_items[category] = []
        categorized_items[category].append(item)
    
    logger.info(f"🔍 DEBUG: Categorized items: {list(categorized_items.keys())}")
    
    # Check if we have required categories
    missing_categories = []
    for category in required:
        if category not in categorized_items or len(categorized_items[category]) == 0:
            missing_categories.append(category)
    
    if missing_categories:
        logger.warning(f"⚠️ Missing required categories: {missing_categories}")
        # Try to find items from missing categories in the full wardrobe
        # This would require access to the full wardrobe, but for now we'll work with what we have
    
    # Build validated outfit with required categories
    validated_outfit = []
    
    # ENHANCED: Smart initial selection to ensure category diversity
    for category in required:
        if category in categorized_items and categorized_items[category]:
            # Take the first item from this category
            validated_outfit.append(categorized_items[category][0])
            logger.info(f"🔍 DEBUG: Added {category} item: {categorized_items[category][0].get('name', 'unnamed')}")
    
    # ENHANCED: If we're missing required categories, try to find alternatives
    if len(validated_outfit) < len(required):
        logger.warning(f"⚠️ Missing required categories, trying to find alternatives")
        missing_categories = [cat for cat in required if cat not in [get_item_category(item.get('type', '')) for item in validated_outfit]]
        
        for missing_cat in missing_categories:
            # Try to find items that could serve as alternatives
            for category, category_items in categorized_items.items():
                if len(validated_outfit) >= len(required):
                    break
                # For missing bottoms, tops can sometimes work (e.g., long tops with leggings)
                if missing_cat == "bottom" and category == "top":
                    # Look for long tops that could work as bottoms
                    for item in category_items:
                        if any(long_word in item.get('name', '').lower() for long_word in ['long', 'tunic', 'oversized', 'maxi']):
                            validated_outfit.append(item)
                            logger.info(f"🔍 DEBUG: Added alternative {missing_cat} item: {item.get('name', 'unnamed')}")
                            break
                # For missing shoes, accessories might work
                elif missing_cat == "shoes" and category == "accessory":
                    for item in category_items:
                        if any(shoe_word in item.get('name', '').lower() for shoe_word in ['boots', 'sneakers', 'shoes']):
                            validated_outfit.append(item)
                            logger.info(f"🔍 DEBUG: Added alternative {missing_cat} item: {item.get('name', 'unnamed')}")
                            break
    
    # Add additional items to fill out the outfit (up to 6 total)
    remaining_slots = 6 - len(validated_outfit)
    additional_items = []
    
    # ENHANCED: Smart category balancing to prevent all-same-category outfits
    category_limits = {
        "top": 3,      # Maximum 3 tops (including base top)
        "bottom": 1,   # Maximum 1 bottom (prevent shorts + pants conflicts)
        "shoes": 1,    # Maximum 1 pair of shoes
        "accessory": 2, # Maximum 2 accessories
        "dress": 1     # Maximum 1 dress
    }
    
    # Count current items per category
    current_category_counts = {}
    for item in validated_outfit:
        category = get_item_category(item.get('type', ''))
        current_category_counts[category] = current_category_counts.get(category, 0) + 1
    
    logger.info(f"🔍 DEBUG: Current category counts: {current_category_counts}")
    
    # ENHANCED: Check for bottom type conflicts (shorts + pants, skirts + pants, etc.)
    bottom_items = [item for item in validated_outfit if get_item_category(item.get('type', '')) == 'bottom']
    if len(bottom_items) > 1:
        logger.warning(f"⚠️ Multiple bottom items detected: {[item.get('name', 'unnamed') for item in bottom_items]}")
        # Keep only the first bottom item to prevent conflicts
        conflicting_bottoms = bottom_items[1:]
        for item in conflicting_bottoms:
            validated_outfit.remove(item)
            logger.info(f"🔍 DEBUG: Removed conflicting bottom: {item.get('name', 'unnamed')}")
        # Update category counts
        current_category_counts['bottom'] = 1
    
    # Prioritize layering items for certain occasions
    layering_priority = ["formal", "business", "date", "party"]
    if occasion.lower() in layering_priority:
        # Add layering items first for formal occasions
        for category, category_items in categorized_items.items():
            if len(additional_items) >= remaining_slots:
                break
            # Check category limits
            current_count = current_category_counts.get(category, 0)
            if current_count >= category_limits.get(category, 2):
                continue
            # Prioritize layering categories
            if category in ["top"] and len(additional_items) < remaining_slots:
                for item in category_items[1:]:  # Skip first item as it's already added
                    if len(additional_items) < remaining_slots and is_layer_item(item.get('type', '')):
                        additional_items.append(item)
                        current_category_counts[category] = current_category_counts.get(category, 0) + 1
                        logger.info(f"🔍 DEBUG: Added layering item: {item.get('name', 'unnamed')}")
                        break
    
    # Fill remaining slots with balanced category distribution
    for category, category_items in categorized_items.items():
        if len(additional_items) >= remaining_slots:
            break
        # Check category limits
        current_count = current_category_counts.get(category, 0)
        if current_count >= category_limits.get(category, 2):
            continue
        
        # ENHANCED: Special handling for bottoms to prevent conflicts
        if category == "bottom" and current_count >= 1:
            logger.info(f"🔍 DEBUG: Skipping additional bottom to prevent conflicts")
            continue
            
        # Add items from this category
        for item in category_items[1:]:  # Skip first item as it's already added
            if len(additional_items) < remaining_slots:
                additional_items.append(item)
                current_category_counts[category] = current_category_counts.get(category, 0) + 1
                logger.info(f"🔍 DEBUG: Added additional {category} item: {item.get('name', 'unnamed')}")
                break
    
    validated_outfit.extend(additional_items)
    
    # ENHANCED: Final duplicate check and removal
    final_outfit = []
    seen_items = set()
    for item in validated_outfit:
        item_id = item.get('id', '')
        if item_id not in seen_items:
            final_outfit.append(item)
            seen_items.add(item_id)
            logger.info(f"🔍 DEBUG: Final outfit item: {item.get('name', 'unnamed')} ({item.get('type', 'unknown')})")
        else:
            logger.warning(f"⚠️ Removed duplicate item: {item.get('name', 'unnamed')}")
    
    logger.info(f"🔍 DEBUG: Final validated outfit: {len(final_outfit)} items (duplicates removed)")
    
    return final_outfit

async def validate_layering_rules(items: List[Dict], occasion: str) -> Dict[str, Any]:
    """Validate layering rules for the outfit."""
    logger.info(f"🔍 DEBUG: Validating layering rules for {occasion} occasion")
    
    # Count layering items
    layer_items = [item for item in items if is_layer_item(item.get('type', ''))]
    layer_count = len(layer_items)
    
    logger.info(f"🔍 DEBUG: Found {layer_count} layering items: {[item.get('name', 'unnamed') for item in layer_items]}")
    
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
    layer_types = [item.get('type', '').lower() for item in layer_items]
    
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
    
    logger.info(f"🔍 DEBUG: Layering validation complete: {len(warnings)} warnings")
    
    return {
        "layer_count": layer_count,
        "layer_items": [item.get('name', 'unnamed') for item in layer_items],
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
        item_colors = item.get('dominantColors', []) or item.get('colors', []) or item.get('color', [])
        if isinstance(item_colors, str):
            item_colors = [item_colors]
        elif not isinstance(item_colors, list):
            item_colors = []
        
        # Extract materials (handle different field names)
        item_material = item.get('material', '') or item.get('fabric', '') or ''
        
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

async def calculate_outfit_score(items: List[Dict], req: OutfitRequest, layering_validation: Dict, color_material_validation: Dict) -> Dict[str, Any]:
    """Calculate comprehensive outfit score across multiple dimensions."""
    logger.info(f"🔍 DEBUG: Calculating outfit score for {len(items)} items")
    
    # Initialize component scores
    scores = {}
    
    # 1. Composition Score (20% weight) - Basic outfit structure
    composition_score = calculate_composition_score(items, req.occasion)
    scores["composition_score"] = composition_score
    logger.info(f"🔍 DEBUG: Composition score: {composition_score}")
    
    # 2. Layering Score (15% weight) - Smart layering and conflicts
    layering_score = calculate_layering_score(layering_validation)
    scores["layering_score"] = layering_score
    logger.info(f"🔍 DEBUG: Layering score: {layering_score}")
    
    # 3. Color Harmony Score (15% weight) - Color theory and psychology
    color_score = calculate_color_score(color_material_validation.get("colors", {}))
    scores["color_score"] = color_score
    logger.info(f"🔍 DEBUG: Color score: {color_score}")
    
    # 4. Material Compatibility Score (10% weight) - Fabric and texture harmony
    material_score = calculate_material_score(color_material_validation.get("materials", {}))
    scores["material_score"] = material_score
    logger.info(f"🔍 DEBUG: Material score: {material_score}")
    
    # 5. Style Coherence Score (15% weight) - Style and mood alignment
    style_score = calculate_style_coherence_score(items, req.style, req.mood)
    scores["style_score"] = style_score
    logger.info(f"🔍 DEBUG: Style score: {style_score}")
    
    # 6. Wardrobe Intelligence Score (25% weight) - Favorites, wear history, diversity
    wardrobe_score = await calculate_wardrobe_intelligence_score(items)
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
    
    required = required_categories.get(occasion.lower(), ["top", "bottom"])
    
    # Categorize items
    categorized_items = {}
    for item in items:
        item_type = item.get('type', '').lower()
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
    
    warnings = layering_validation.get('warnings', [])
    layer_count = layering_validation.get('layer_count', 0)
    
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
    
    total_colors = color_analysis.get('total_colors', 0)
    palette_type = color_analysis.get('palette_type', 'neutral')
    
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
    
    material_quality = material_analysis.get('material_quality', 'mixed')
    natural_count = material_analysis.get('natural_materials', 0)
    luxury_count = material_analysis.get('luxury_materials', 0)
    
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

async def calculate_wardrobe_intelligence_score(items: List[Dict]) -> float:
    """Calculate score based on wardrobe intelligence: favorites, wear history, diversity."""
    logger.info(f"🔍 DEBUG: Calculating wardrobe intelligence score for {len(items)} items")
    
    # Get current user ID from the hardcoded user (for now)
    current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    total_score = 0.0
    item_scores = []
    
    for item in items:
        item_score = 0.0
        item_id = item.get('id', '')
        
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
                is_favorite = analytics_data.get('is_favorite', False)
                
                # Also check wardrobe collection for favorite status
                try:
                    wardrobe_ref = db.collection('wardrobe').document(item_id)
                    wardrobe_doc = wardrobe_ref.get()
                    if wardrobe_doc.exists:
                        wardrobe_data = wardrobe_doc.to_dict()
                        if wardrobe_data.get('isFavorite', False):
                            is_favorite = True
                except Exception as e:
                    logger.warning(f"⚠️ Could not check wardrobe favorite status for item {item_id}: {e}")
                
                if is_favorite:
                    item_score += 25
                    logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +25 favorite bonus")
                else:
                    # Bonus for non-favorited items that perform well in outfits
                    outfit_performance_bonus = min(10, outfit_performance_score)  # Up to 10 bonus points
                    item_score += outfit_performance_bonus
                    logger.info(f"🔍 DEBUG: Non-favorited item {item.get('name', 'Unknown')} gets +{outfit_performance_bonus} performance bonus")
                
                # 2. Wear Count Scoring (up to 20 points)
                wear_count = analytics_data.get('wear_count', 0)
                
                # Fallback to wardrobe collection if no analytics data
                if wear_count == 0:
                    try:
                        wardrobe_ref = db.collection('wardrobe').document(item_id)
                        wardrobe_doc = wardrobe_ref.get()
                        if wardrobe_doc.exists:
                            wardrobe_data = wardrobe_doc.to_dict()
                            wear_count = wardrobe_data.get('wearCount', 0)
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get wear count from wardrobe for item {item_id}: {e}")
                
                if wear_count == 0:
                    item_score += 20  # Bonus for unworn items
                    logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +20 unworn bonus")
                elif wear_count <= 3:
                    item_score += 15  # Good for moderately worn items
                    logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +15 moderately worn bonus")
                elif wear_count <= 7:
                    item_score += 10  # Acceptable for frequently worn items
                    logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +10 frequently worn bonus")
                else:
                    item_score += 5   # Minimal points for over-worn items
                    logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +5 over-worn bonus")
                
                # 3. Recent Wear Penalty (up to -15 points)
                last_worn = analytics_data.get('last_worn')
                
                # Fallback to wardrobe collection if no analytics data
                if not last_worn:
                    try:
                        wardrobe_ref = db.collection('wardrobe').document(item_id)
                        wardrobe_doc = wardrobe_ref.get()
                        if wardrobe_doc.exists:
                            wardrobe_data = wardrobe_doc.to_dict()
                            last_worn = wardrobe_data.get('lastWorn')
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
                            logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets -15 penalty (worn yesterday)")
                        elif days_since_worn <= 3:
                            item_score -= 10  # Penalty for worn this week
                            logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets -10 penalty (worn this week)")
                        elif days_since_worn <= 7:
                            item_score -= 5   # Light penalty for worn this month
                            logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets -5 penalty (worn this month)")
                        else:
                            item_score += 5   # Bonus for items not worn recently
                            logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +5 bonus (not worn recently)")
                    
                    except Exception as e:
                        logger.warning(f"⚠️ Could not parse last_worn date for item {item_id}: {e}")
                        item_score += 5  # Neutral score if date parsing fails
                
                # 4. User Feedback Bonus (up to 15 points)
                feedback_rating = analytics_data.get('average_feedback_rating', 0)
                if feedback_rating >= 4.5:
                    item_score += 15  # Excellent feedback
                    logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +15 feedback bonus (rating: {feedback_rating})")
                elif feedback_rating >= 4.0:
                    item_score += 10  # Good feedback
                    logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +10 feedback bonus (rating: {feedback_rating})")
                elif feedback_rating >= 3.5:
                    item_score += 5   # Average feedback
                    logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +5 feedback bonus (rating: {feedback_rating})")
                
                # 5. Style Preference Match (up to 10 points)
                style_match = analytics_data.get('style_preference_score', 0.5)
                item_score += style_match * 10
                logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +{style_match * 10:.1f} style preference bonus")
                
                # 6. Outfit Performance Bonus (up to 20 points) - NEW!
                outfit_performance_score = await calculate_outfit_performance_score(item_id, current_user_id)
                item_score += outfit_performance_score
                logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +{outfit_performance_score} outfit performance bonus")
                
                # 7. Wardrobe Diversity Bonus (up to 5 points) - NEW!
                diversity_bonus = await calculate_wardrobe_diversity_bonus(item_id, current_user_id)
                item_score += diversity_bonus
                logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets +{diversity_bonus} diversity bonus")
                
            else:
                # No analytics data - neutral score
                item_score = 50
                logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} gets neutral score (no analytics data)")
            
        except Exception as e:
            logger.error(f"❌ Error calculating wardrobe intelligence for item {item_id}: {e}")
            item_score = 50  # Neutral score on error
        
        # Ensure score stays within bounds
        item_score = max(0, min(100, item_score))
        item_scores.append(item_score)
        total_score += item_score
        
        logger.info(f"🔍 DEBUG: Item {item.get('name', 'Unknown')} final wardrobe score: {item_score}")
    
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
        outfits_ref = db.collection('outfits').where('userId', '==', user_id)
        outfits_docs = outfits_ref.stream()
        
        total_score = 0.0
        outfit_count = 0
        high_rated_outfits = 0
        worn_outfits = 0
        
        for outfit_doc in outfits_docs:
            outfit_data = outfit_doc.to_dict()
            outfit_items = outfit_data.get('items', [])
            
            # Check if this item is in this outfit
            item_in_outfit = any(item.get('id') == item_id for item in outfit_items)
            if not item_in_outfit:
                continue
            
            outfit_count += 1
            
            # 1. Outfit Rating Bonus (up to 10 points)
            outfit_rating = outfit_data.get('rating', 0)
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
            outfit_wear_count = outfit_data.get('wearCount', 0)
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
            outfit_liked = outfit_data.get('isLiked', False)
            outfit_disliked = outfit_data.get('isDisliked', False)
            
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
        wardrobe_doc = wardrobe_ref.get()
        
        if not wardrobe_doc.exists:
            return 0.0
        
        current_item = wardrobe_doc.to_dict()
        current_type = current_item.get('type', '').lower()
        current_color = current_item.get('color', '').lower()
        
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
    layer_types = ["shirt", "t-shirt", "blouse", "sweater", "jacket", "coat", "blazer", "cardigan", "hoodie"]
    return item_type_lower in layer_types

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
            items.append(item_data)
        
        logger.info(f"✅ Retrieved {len(items)} wardrobe items")
        return items
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch wardrobe for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch wardrobe: {e}")

async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user's style profile from Firestore."""
    try:
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
        profile_doc = profile_ref.get()
        
        if profile_doc.exists:
            profile_data = profile_doc.to_dict()
            logger.info(f"✅ Retrieved profile for user {user_id}")
            
            # CRITICAL: Ensure gender is set - if missing or null, default to male
            if not profile_data.get('gender'):
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

async def generate_ai_outfit(wardrobe_items: List[Dict], user_profile: Dict, req: OutfitRequest) -> Dict[str, Any]:
    """Generate outfit using AI logic and user's wardrobe."""
    try:
        logger.info(f"🤖 Generating AI outfit with {len(wardrobe_items)} items")
        
        # For now, implement basic outfit selection logic
        # TODO: Integrate with OpenAI GPT for more sophisticated generation
        
                # ENHANCED: Sophisticated style preference filtering with scoring
        suitable_items = []
        item_scores = {}  # Track scores for each item
        
        logger.info(f"🔍 DEBUG: Filtering {len(wardrobe_items)} items for style: {req.style}, occasion: {req.occasion}")
        logger.info(f"🔍 DEBUG: User profile style preferences: {user_profile.get('stylePreferences', []) if user_profile else 'None'}")
        
        for item in wardrobe_items:
            item_style = item.get('style', '') or ''
            item_occasion = item.get('occasion', '') or ''
            item_color = item.get('color', '') or ''
            item_material = item.get('material', '') or ''
            
            # Convert to string if it's a list
            if isinstance(item_style, list):
                item_style = ' '.join(item_style).lower()
            else:
                item_style = str(item_style).lower()
                
            if isinstance(item_occasion, list):
                item_occasion = ' '.join(item_occasion).lower()
            else:
                item_occasion = str(item_occasion).lower()
            
            logger.info(f"🔍 DEBUG: Item {item.get('name', 'unnamed')} - style: '{item_style}', occasion: '{item_occasion}', color: '{item_color}'")
            
            # ENHANCED: Multi-dimensional style preference scoring
            item_score = 0
            is_suitable = False
            
            # 1. Core Style Matching (Primary filter - must pass)
            if (req.style.lower() in item_style or 
                req.occasion.lower() in item_occasion or
                'versatile' in item_style):
                
                is_suitable = True
                item_score += 50  # Base score for passing core criteria
                
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
                    preferred_colors = color_palette.get('primary', []) + color_palette.get('secondary', [])
                    avoid_colors = color_palette.get('avoid', [])
                    
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
                    preferred_materials = material_prefs.get('preferred', [])
                    avoid_materials = material_prefs.get('avoid', [])
                    
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
                    if 'classic' in item_style and personality_scores.get('classic', 0) > 0.6:
                        item_score += personality_scores['classic'] * 12
                        logger.info(f"🔍 DEBUG: Classic personality match: +{personality_scores['classic'] * 12:.1f} points")
                    
                    if 'modern' in item_style and personality_scores.get('modern', 0) > 0.6:
                        item_score += personality_scores['modern'] * 12
                        logger.info(f"🔍 DEBUG: Modern personality match: +{personality_scores['modern'] * 12:.1f} points")
                    
                    if 'creative' in item_style and personality_scores.get('creative', 0) > 0.6:
                        item_score += personality_scores['creative'] * 12
                        logger.info(f"🔍 DEBUG: Creative personality match: +{personality_scores['creative'] * 12:.1f} points")
                
                # 6. Business/Formal Enhancement (Existing logic enhanced)
                if req.occasion.lower() in ['business', 'formal', 'office']:
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
                    item_gender = item.get('gender', '').lower()
                    
                    # Gender-specific style filtering with scoring
                    if user_gender == 'male':
                        feminine_styles = ['french girl', 'romantic', 'pinup', 'boho', 'cottagecore']
                        if req.style.lower() in feminine_styles:
                            logger.info(f"🔍 DEBUG: Skipping feminine style '{req.style}' for male user: {item.get('name', 'unnamed')}")
                            continue
                    
                    elif user_gender == 'female':
                        masculine_styles = ['techwear', 'grunge', 'streetwear']
                        if req.style.lower() in masculine_styles:
                            logger.info(f"🔍 DEBUG: Skipping masculine style '{req.style}' for female user: {item.get('name', 'unnamed')}")
                            continue
                    
                    # Item gender compatibility with scoring
                    if item_gender and item_gender not in ['unisex', user_gender]:
                        logger.info(f"🔍 DEBUG: Skipping gender-incompatible item: {item.get('name', 'unnamed')} (item: {item_gender}, user: {user_gender})")
                        continue
                    
                    # Gender preference bonus
                    if item_gender == user_gender:
                        item_score += 8
                        logger.info(f"🔍 DEBUG: Gender preference match: +8 points")
                    elif item_gender == 'unisex':
                        item_score += 5
                        logger.info(f"🔍 DEBUG: Unisex item: +5 points")
                
                # Store item with its score
                item_scores[item.get('id', item.get('name', 'unknown'))] = item_score
                suitable_items.append(item)
                logger.info(f"🔍 DEBUG: Item {item.get('name', 'unnamed')} is suitable with score: {item_score}")
            else:
                logger.info(f"🔍 DEBUG: Item {item.get('name', 'unnamed')} failed core style/occasion criteria")
        
        # ENHANCED: Sort items by preference score for better selection
        if suitable_items and item_scores:
            suitable_items.sort(key=lambda item: item_scores.get(item.get('id', item.get('name', 'unknown')), 0), reverse=True)
            logger.info(f"🔍 DEBUG: Sorted {len(suitable_items)} suitable items by preference score")
            for item in suitable_items[:5]:  # Log top 5 scores
                score = item_scores.get(item.get('id', item.get('name', 'unknown')), 0)
                logger.info(f"🔍 DEBUG: Top item: {item.get('name', 'unnamed')} - Score: {score}")
        
        logger.info(f"🔍 DEBUG: Found {len(suitable_items)} suitable items")
        
        # ENHANCED: Add randomization to prevent same outfit generation
        import random
        import time
        
        # ENHANCED: Ensure we have enough diverse items for outfit generation
        if len(suitable_items) < 10:
            # Add more items to ensure variety
            additional_items = [item for item in wardrobe_items if item not in suitable_items]
            random.shuffle(additional_items)
            suitable_items.extend(additional_items[:10])
            logger.info(f"🔍 DEBUG: Extended suitable items to {len(suitable_items)} for variety")
        
        # If no suitable items, use any available items
        if not suitable_items:
            logger.info(f"🔍 DEBUG: No suitable items found, using first 4 items")
            suitable_items = wardrobe_items[:4]  # Take first 4 items
        # Use timestamp as seed for different randomization each time
        random.seed(int(time.time() * 1000) % 1000000)
        random.shuffle(suitable_items)
        logger.info(f"🔍 DEBUG: Randomized suitable items order with seed")
        
        # Validate and ensure complete outfit composition
        validated_items = await validate_outfit_composition(suitable_items, req.occasion)
        logger.info(f"🔍 DEBUG: After validation: {len(validated_items)} items")
        
        # Apply layering validation rules
        layering_validation = await validate_layering_rules(validated_items, req.occasion)
        logger.info(f"🔍 DEBUG: Layering validation: {layering_validation}")
        
        # Apply color theory and material matching
        color_material_validation = await validate_color_material_harmony(validated_items, req.style, req.mood)
        logger.info(f"🔍 DEBUG: Color/material validation: {color_material_validation}")
        
        # Adjust outfit based on validation rules
        if layering_validation.get('warnings'):
            logger.info(f"🔍 DEBUG: Layering warnings: {layering_validation['warnings']}")
        if color_material_validation.get('warnings'):
            logger.info(f"🔍 DEBUG: Color/material warnings: {color_material_validation['warnings']}")
        
        # Create outfit
        outfit_name = f"{req.style.title()} {req.mood.title()} Look"
        
        # Ensure items have proper structure with imageUrl
        outfit_items = []
        for item in validated_items:
            # Convert Firebase Storage gs:// URLs to https:// URLs
            raw_image_url = item.get('imageUrl', '') or item.get('image_url', '') or item.get('image', '')
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
                "id": item.get('id', ''),
                "name": item.get('name', ''),
                "type": item.get('type', ''),
                "color": item.get('color', ''),
                "imageUrl": image_url
            }
            outfit_items.append(outfit_item)
            logger.info(f"🔍 DEBUG: Item {outfit_item['name']} - Original URL: {raw_image_url}")
            logger.info(f"🔍 DEBUG: Item {outfit_item['name']} - Converted URL: {image_url}")
            logger.info(f"🔍 DEBUG: Item {outfit_item['name']} - Full item data: {outfit_item}")
        
        # Calculate comprehensive outfit score
        outfit_score = await calculate_outfit_score(outfit_items, req, layering_validation, color_material_validation)
        logger.info(f"🔍 DEBUG: Calculated outfit score: {outfit_score}")
        
        return {
            "name": outfit_name,
            "style": req.style,
            "mood": req.mood,
            "items": outfit_items,
            "occasion": req.occasion,
            "confidence_score": outfit_score["total_score"],
            "score_breakdown": outfit_score,
            "reasoning": f"Generated {len(outfit_items)} items forming a complete {req.occasion} outfit with {req.style} style. Includes required categories: {', '.join(set([get_item_category(item.get('type', '')) for item in outfit_items]))}",
            "createdAt": int(datetime.now().timestamp())
        }
        
    except Exception as e:
        logger.error(f"❌ AI outfit generation failed: {e}")
        # Fall back to basic generation
        return await generate_fallback_outfit(req, "unknown")

async def generate_fallback_outfit(req: OutfitRequest, user_id: str) -> Dict[str, Any]:
    """Generate basic fallback outfit when AI generation fails."""
    logger.info(f"🔄 Generating fallback outfit for {user_id}")
    
    outfit_name = f"{req.style.title()} {req.mood.title()} Look"
    
    return {
        "name": outfit_name,
        "style": req.style,
        "mood": req.mood,
        "items": [
            {"id": "fallback-1", "name": f"{req.style} Top", "type": "shirt", "imageUrl": None},
            {"id": "fallback-2", "name": f"{req.mood} Pants", "type": "pants", "imageUrl": None},
            {"id": "fallback-3", "name": f"{req.occasion} Shoes", "type": "shoes", "imageUrl": None}
        ],
        "occasion": req.occasion,
        "confidence_score": 0.5,
        "reasoning": f"Basic {req.style} outfit for {req.occasion} (fallback generation)",
        "createdAt": int(datetime.now().timestamp())
    }

# Real Firestore operations
async def save_outfit(user_id: str, outfit_id: str, outfit_record: Dict[str, Any]) -> bool:
    """Save outfit to Firestore."""
    try:
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, skipping save")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
            
        logger.info(f"💾 Saving outfit {outfit_id} for user {user_id}")
        
        # Save to main outfits collection with user_id field (consistent with fetching)
        outfits_ref = db.collection('outfits')
        outfits_ref.document(outfit_id).set(outfit_record)
        
        logger.info(f"✅ Successfully saved outfit {outfit_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save outfit {outfit_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save outfit: {e}")

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
                resolved_items.append(item)
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
            # Item is already a complete object
            resolved_items.append(item)
        elif isinstance(item, str):
            if wardrobe_cache and item in wardrobe_cache:
                # Use cached item
                resolved_items.append(wardrobe_cache[item])
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

async def get_user_outfits(user_id: str, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
    """Get user outfits from Firestore with pagination."""
    logger.info(f"🔍 DEBUG: Fetching outfits for user {user_id} (limit={limit}, offset={offset})")
    logger.info(f"🔍 DEBUG: FIREBASE_AVAILABLE: {FIREBASE_AVAILABLE}")
    logger.info(f"🔍 DEBUG: firebase_initialized: {firebase_initialized}")
    
    try:
        if not FIREBASE_AVAILABLE or not firebase_initialized:
            logger.warning("⚠️ Firebase not available, returning empty outfits")
            raise HTTPException(status_code=503, detail="Firebase service unavailable")
            
        logger.info(f"📚 DEBUG: About to query Firestore collection('outfits') with user_id == '{user_id}'")
        
        # FIXED: Query main outfits collection with user_id filter (not subcollection)
        # This matches where outfits are actually stored: outfits collection with user_id field
        outfits_ref = db.collection("outfits").where("user_id", "==", user_id)
        
        # Try Firestore ordering, fallback to client-side if index missing
        use_firestore_ordering = True
        try:
            outfits_ref = outfits_ref.order_by("createdAt", direction=db.Query.DESCENDING)
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
        
        # Execute query
        logger.info(f"🔍 DEBUG: Executing Firestore query with .stream()...")
        docs = outfits_ref.stream()
        logger.info(f"🔍 DEBUG: Firestore query executed successfully, processing results...")
        
        # First pass: collect outfit data
        outfits = []
        for doc in docs:
            outfit_data = doc.to_dict()
            outfit_data['id'] = doc.id
            outfits.append(outfit_data)
            created_at = outfit_data.get('createdAt', 'Unknown')
            logger.info(f"🔍 DEBUG: Found outfit: {outfit_data.get('name', 'unnamed')} (ID: {doc.id}, Created: {created_at})")
        
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
        
        # Second pass: resolve items using cache and normalize timestamps
        for outfit_data in outfits:
            if 'items' in outfit_data and outfit_data['items']:
                logger.info(f"🔍 DEBUG: Resolving {len(outfit_data['items'])} items for outfit {outfit_data.get('name', 'unnamed')}")
                outfit_data['items'] = await resolve_item_ids_to_objects(outfit_data['items'], user_id, wardrobe_cache)
                logger.info(f"✅ DEBUG: Resolved items to full objects")
            
            # Normalize timestamps to ensure consistent sorting
            created_at = outfit_data.get('createdAt')
            if created_at:
                if isinstance(created_at, (int, float)):
                    # Convert Unix timestamp to ISO string
                    outfit_data['createdAt'] = datetime.fromtimestamp(created_at).isoformat() + 'Z'
                    logger.info(f"🔍 DEBUG: Converted Unix timestamp {created_at} to ISO format")
                elif isinstance(created_at, str) and not created_at.endswith('Z'):
                    # Ensure ISO string has Z suffix
                    if 'T' in created_at and not created_at.endswith('Z'):
                        outfit_data['createdAt'] = created_at + 'Z'
        
        # Check if we need client-side sorting (when Firestore ordering failed)
        if not use_firestore_ordering:
            logger.info("🔄 DEBUG: Applying client-side sorting since Firestore ordering failed")
            outfits.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
            # Apply pagination after sorting
            start_idx = offset
            end_idx = offset + limit
            outfits = outfits[start_idx:end_idx]
            logger.info(f"✅ DEBUG: Client-side sorted and paginated to {len(outfits)} outfits")
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
        raise HTTPException(status_code=500, detail=f"Failed to fetch user outfits: {e}")

# Health and debug endpoints (MUST be before parameterized routes)
@router.get("/health", response_model=dict)
async def outfits_health_check():
    """Health check for outfits router."""
    logger.info("🔍 DEBUG: Outfits health check called")
    return {
        "status": "healthy", 
        "router": "outfits", 
        "message": "Outfits router is working!",
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
                "name": outfit_data.get('name', 'unknown'),
                "user_id": outfit_data.get('user_id', 'unknown')
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

@router.get("/debug-user", response_model=dict)
async def debug_user_outfits(
    current_user: UserProfile = Depends(get_current_user_optional)
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
                                "name": outfit_data.get('name', 'unnamed'),
                                "user_id": outfit_data.get('user_id', outfit_data.get('userId', 'no_user_id')),
                                "created_at": outfit_data.get('createdAt', outfit_data.get('created_at', 'no_date')),
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
):
    """
    Generate an outfit using decision logic, save it to Firestore,
    and return the standardized response.
    """
    try:
        # Get real user ID from request context
        current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Your actual user ID
        logger.info(f"Using real user ID: {current_user_id}")
        
        logger.info(f"🎨 Generating outfit for user: {current_user_id}")
        
        # 1. Run generation logic (GPT + rules + metadata validation)
        outfit = await generate_outfit_logic(req, current_user_id)

        # 2. Wrap with metadata
        outfit_id = str(uuid4())
        outfit_record = {
            "id": outfit_id,
            "user_id": current_user_id,
            "generated_at": datetime.utcnow().isoformat(),
            **outfit
        }

        # 3. Save to Firestore
        await save_outfit(current_user_id, outfit_id, outfit_record)

        # 4. Return standardized outfit response
        logger.info(f"✅ Successfully generated and saved outfit {outfit_id}")
        return OutfitResponse(**outfit_record)

    except Exception as e:
        logger.error(f"❌ Outfit generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate outfit")


@router.post("", response_model=OutfitGeneratedOutfit)
async def create_outfit(
    request: CreateOutfitRequest
):
    """
    Create a custom outfit by manually selecting items from the user's wardrobe.
    REST endpoint: POST /api/outfits
    """
    try:
        logger.info(f"🎨 Creating custom outfit: {request.name}")
        # Reduced logging to prevent rate limits
        
        # Use the same user ID pattern as the generate route
        current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Your actual user ID
        
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
            "user_id": current_user_id,
            "createdAt": request.createdAt or int(time.time()),
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
        
        # Save using the same unified save_outfit function
        outfit_id = outfit_data["id"]
        await save_outfit(current_user_id, outfit_id, outfit_data)
        
        # Enhanced logging for debugging
        logger.info(f"✅ Outfit created: {outfit_id} for user {current_user_id}")
        logger.info(f"🔍 DEBUG: Created outfit name='{outfit_data['name']}' style='{outfit_data['style']}' occasion='{outfit_data['occasion']}'")
        logger.info(f"📊 DEBUG: Outfit contains {len(outfit_data['items'])} items")
        
        return outfit_data
        
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
        current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Your actual user ID
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
                "id": outfit.get("id", "unknown"),
                "name": outfit.get("name", "unknown"),
                "style": outfit.get("style", "unknown"),
                "occasion": outfit.get("occasion", "unknown"),
                "createdAt": outfit.get("createdAt", "unknown"),
                "user_id": outfit.get("user_id", "unknown"),
                "item_count": len(outfit.get("items", []))
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
        current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        outfits = await get_user_outfits(current_user_id, 5, 0)
        
        return {
            "total_outfits": len(outfits),
            "outfits": [
                {
                    "id": o.get("id"),
                    "name": o.get("name"),
                    "createdAt": o.get("createdAt"),
                    "user_id": o.get("user_id")
                } for o in outfits
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/rate")
async def rate_outfit(
    rating_data: dict,
    current_user: UserProfile = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Rate an outfit and update analytics for individual wardrobe items.
    This ensures the scoring system has accurate feedback data.
    """
    try:
        logger.info(f"📊 Rating outfit request received")
        
        current_user_id = current_user.id if current_user else "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        outfit_id = rating_data.get('outfitId')
        rating = rating_data.get('rating')
        is_liked = rating_data.get('isLiked', False)
        is_disliked = rating_data.get('isDisliked', False)
        feedback = rating_data.get('feedback', '')
        
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
        outfit_ref = db.collection('outfits').document(outfit_id)
        outfit_doc = outfit_ref.get()
        
        if not outfit_doc.exists:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        outfit_data = outfit_doc.to_dict()
        # Check both possible user ID field names for compatibility
        outfit_user_id = outfit_data.get('userId') or outfit_data.get('user_id')
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
            outfit_data.get('items', []), 
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
            item_id = item.get('id')
            if not item_id:
                continue
            
            try:
                # Check if analytics document exists for this item
                analytics_ref = db.collection('item_analytics').document(f"{user_id}_{item_id}")
                analytics_doc = analytics_ref.get()
                
                if analytics_doc.exists:
                    # Update existing analytics
                    current_data = analytics_doc.to_dict()
                    
                    # Update feedback ratings
                    feedback_ratings = current_data.get('feedback_ratings', [])
                    feedback_ratings.append({
                        'rating': rating,
                        'outfit_rating': rating,
                        'is_liked': is_liked,
                        'is_disliked': is_disliked,
                        'feedback': feedback,
                        'timestamp': current_time
                    })
                    
                    # Calculate new average rating
                    total_rating = sum(fr.get('rating', 0) for fr in feedback_ratings)
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
        current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # TEMPORARY: Your actual user ID
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
    current_user: UserProfile = Depends(get_current_user_optional)
):
    """
    Fetch a user's outfit history from Firestore.
    """
    try:
        # TEMPORARY FIX: Use the actual user ID from your database
        # TODO: Fix authentication to get real user ID
        if current_user:
            current_user_id = current_user.id
            logger.info(f"📚 Fetching outfits for authenticated user: {current_user_id}")
        else:
            # Use the actual user ID from your database where the 1000+ outfits are stored
            current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # TEMPORARY: Your actual user ID
            logger.info(f"📚 No authenticated user, using hardcoded user ID: {current_user_id}")
        
        logger.info(f"📚 Fetching outfits for user: {current_user_id}")
        
        outfits = await get_user_outfits(current_user_id, limit, offset)
        
        # Enhanced logging for debugging
        logger.info(f"📥 Fetch returned {len(outfits)} outfits for user {current_user_id}")
        if outfits:
            # Log the most recent outfit for debugging
            latest = outfits[0]
            logger.info(f"🔍 DEBUG: Latest outfit: '{latest.get('name', 'Unknown')}' created at {latest.get('createdAt', 'Unknown')}")
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
    current_user: UserProfile = Depends(get_current_user_optional)
):
    """
    Fetch a user's outfit history from Firestore (no trailing slash).
    """
    try:
        # TEMPORARY FIX: Use the actual user ID from your database
        # TODO: Fix authentication to get real user ID
        if current_user:
            current_user_id = current_user.id
            logger.info(f"📚 Fetching outfits for authenticated user: {current_user_id}")
        else:
            # Use the actual user ID from your database where the 1000+ outfits are stored
            current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # TEMPORARY: Your actual user ID
            logger.info(f"📚 No authenticated user, using hardcoded user ID: {current_user_id}")
        
        logger.info(f"📚 Fetching outfits for user: {current_user_id}")
        
        outfits = await get_user_outfits(current_user_id, limit, offset)
        
        # Enhanced logging for debugging
        logger.info(f"📥 Fetch returned {len(outfits)} outfits for user {current_user_id}")
        if outfits:
            # Log the most recent outfit for debugging
            latest = outfits[0]
            logger.info(f"🔍 DEBUG: Latest outfit: '{latest.get('name', 'Unknown')}' created at {latest.get('createdAt', 'Unknown')}")
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
    current_user: UserProfile = Depends(get_current_user_optional)
):
    """
    Get outfit statistics for user.
    """
    try:
        # TEMPORARY FIX: Use the actual user ID from your database
        # TODO: Fix authentication to get real user ID
        if current_user:
            current_user_id = current_user.id
            logger.info(f"📊 Getting outfit stats for authenticated user {current_user_id}")
        else:
            # Use the actual user ID from your database where the 1000+ outfits are stored
            current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # TEMPORARY: Your actual user ID
            logger.info(f"📊 No authenticated user, using hardcoded user ID: {current_user_id}")
        
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
            occasion = outfit.get('occasion', 'Unknown')
            stats['occasions'][occasion] = stats['occasions'].get(occasion, 0) + 1
            
            style = outfit.get('style', 'Unknown')
            stats['styles'][style] = stats['styles'].get(style, 0) + 1
        
        # Add recent activity
        if outfits:
            stats['recentActivity'] = [
                {
                    'id': o['id'],
                    'name': o['name'],
                    'lastUpdated': o.get('createdAt', datetime.now())
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