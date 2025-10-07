"""
Enhanced Debug Output Format
Implements the final debug output format with human-readable semantic matching information
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

def format_debug_reason(
    reason: str, 
    semantic_mode: bool, 
    requested_style: str = "", 
    requested_occasion: str = "", 
    requested_mood: str = "",
    item_styles: List[str] = None,
    item_occasions: List[str] = None,
    item_moods: List[str] = None
) -> str:
    """Format debug reason with semantic matching information"""
    if not semantic_mode:
        return reason
    
    # Enhanced formatting for semantic mode
    if "Occasion mismatch" in reason:
        if item_occasions:
            # Check for semantic compatibility
            occasion_compat = _check_occasion_compatibility(requested_occasion, item_occasions)
            if occasion_compat:
                return f"Occasion near-match: requested={requested_occasion}, item_occasions={item_occasions} (compat: {occasion_compat}) ✅"
            else:
                return f"Occasion mismatch: requested={requested_occasion}, item_occasions={item_occasions} ❌"
    
    elif "Style mismatch" in reason:
        if item_styles:
            # Check for semantic compatibility
            style_compat = _check_style_compatibility(requested_style, item_styles)
            if style_compat:
                return f"Style near-match: requested={requested_style}, item_styles={item_styles} (compat: {style_compat}) ✅"
            else:
                return f"Style mismatch: requested={requested_style}, item_styles={item_styles} ❌"
    
    elif "Mood mismatch" in reason:
        if item_moods:
            # Check for semantic compatibility
            mood_compat = _check_mood_compatibility(requested_mood, item_moods)
            if mood_compat:
                return f"Mood compatible: requested={requested_mood}, item_moods={item_moods} (compat: {mood_compat}) ✅"
            else:
                return f"Mood mismatch: requested={requested_mood}, item_moods={item_moods} ❌"
    
    return reason

def _check_style_compatibility(requested_style: str, item_styles: List[str]) -> Optional[str]:
    """Check if item styles are semantically compatible with requested style"""
    if not requested_style or not item_styles:
        return None
    
    # Import compatibility functions
    try:
        from .semantic_compatibility import style_matches
        if style_matches(requested_style, item_styles):
            # Find the specific compatible style
            for item_style in item_styles:
                if _are_styles_compatible(requested_style, item_style):
                    return f"{requested_style}↔{item_style}"
    except ImportError:
        pass
    
    return None

def _check_occasion_compatibility(requested_occasion: str, item_occasions: List[str]) -> Optional[str]:
    """Check if item occasions are semantically compatible with requested occasion"""
    if not requested_occasion or not item_occasions:
        return None
    
    try:
        from .semantic_compatibility import occasion_matches
        if occasion_matches(requested_occasion, item_occasions):
            # Find the specific compatible occasion
            for item_occasion in item_occasions:
                if _are_occasions_compatible(requested_occasion, item_occasion):
                    return f"{requested_occasion}↔{item_occasion}"
    except ImportError:
        pass
    
    return None

def _check_mood_compatibility(requested_mood: str, item_moods: List[str]) -> Optional[str]:
    """Check if item moods are semantically compatible with requested mood"""
    if not requested_mood or not item_moods:
        return None
    
    try:
        from .semantic_compatibility import mood_matches
        if mood_matches(requested_mood, item_moods):
            # Find the specific compatible mood
            for item_mood in item_moods:
                if _are_moods_compatible(requested_mood, item_mood):
                    return f"{requested_mood}↔{item_mood}"
    except ImportError:
        pass
    
    return None

def _are_styles_compatible(style1: str, style2: str) -> bool:
    """Check if two styles are compatible"""
    # Simplified compatibility check
    compatibility_map = {
        'classic': ['casual', 'business casual', 'business'],
        'casual': ['classic', 'streetwear', 'athleisure'],
        'business': ['business casual', 'formal', 'classic'],
        'formal': ['business', 'elegant'],
        'athletic': ['casual', 'sporty'],
        'streetwear': ['casual', 'urban'],
    }
    
    style1_lower = style1.lower()
    style2_lower = style2.lower()
    
    # Direct match
    if style1_lower == style2_lower:
        return True
    
    # Check compatibility map
    compatible_styles = compatibility_map.get(style1_lower, [])
    return style2_lower in compatible_styles

def _are_occasions_compatible(occasion1: str, occasion2: str) -> bool:
    """Check if two occasions are compatible"""
    # Simplified compatibility check
    compatibility_map = {
        'athletic': ['casual', 'everyday'],
        'casual': ['everyday', 'weekend'],
        'business': ['business casual', 'formal'],
        'formal': ['business', 'elegant'],
    }
    
    occasion1_lower = occasion1.lower()
    occasion2_lower = occasion2.lower()
    
    # Direct match
    if occasion1_lower == occasion2_lower:
        return True
    
    # Check compatibility map
    compatible_occasions = compatibility_map.get(occasion1_lower, [])
    return occasion2_lower in compatible_occasions

def _are_moods_compatible(mood1: str, mood2: str) -> bool:
    """Check if two moods are compatible"""
    # Simplified compatibility check
    compatibility_map = {
        'bold': ['confident', 'statement', 'vibrant'],
        'relaxed': ['calm', 'laidback', 'casual'],
        'romantic': ['soft', 'elegant'],
        'professional': ['confident', 'polished'],
    }
    
    mood1_lower = mood1.lower()
    mood2_lower = mood2.lower()
    
    # Direct match
    if mood1_lower == mood2_lower:
        return True
    
    # Check compatibility map
    compatible_moods = compatibility_map.get(mood1_lower, [])
    return mood2_lower in compatible_moods

def create_enhanced_debug_output(
    debug_analysis: List[Dict[str, Any]],
    semantic_mode: bool,
    requested_style: str = "",
    requested_occasion: str = "",
    requested_mood: str = ""
) -> List[Dict[str, Any]]:
    """Create enhanced debug output with human-readable semantic information"""
    
    enhanced_debug = []
    
    for item in debug_analysis:
        enhanced_item = {
            "id": item.get("id", "unknown"),
            "name": item.get("name", "Unknown"),
            "valid": item.get("valid", False),
            "reasons": []
        }
        
        # Process reasons with enhanced formatting
        original_reasons = item.get("reasons", [])
        for reason in original_reasons:
            enhanced_reason = format_debug_reason(
                reason=reason,
                semantic_mode=semantic_mode,
                requested_style=requested_style,
                requested_occasion=requested_occasion,
                requested_mood=requested_mood,
                item_styles=item.get("item_data", {}).get("style", []),
                item_occasions=item.get("item_data", {}).get("occasion", []),
                item_moods=item.get("item_data", {}).get("mood", [])
            )
            enhanced_item["reasons"].append(enhanced_reason)
        
        # Add semantic match information for valid items
        if enhanced_item["valid"] and semantic_mode:
            enhanced_item["semantic_match_info"] = {
                "style_compatibility": _check_style_compatibility(requested_style, item.get("item_data", {}).get("style", [])),
                "occasion_compatibility": _check_occasion_compatibility(requested_occasion, item.get("item_data", {}).get("occasion", [])),
                "mood_compatibility": _check_mood_compatibility(requested_mood, item.get("item_data", {}).get("mood", []))
            }
        
        enhanced_debug.append(enhanced_item)
    
    return enhanced_debug

def format_final_debug_response(
    outfits: List[Dict[str, Any]],
    debug_analysis: List[Dict[str, Any]],
    semantic_mode: bool,
    requested_style: str = "",
    requested_occasion: str = "",
    requested_mood: str = "",
    debug_output: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Format the final debug response with enhanced semantic information"""
    
    # Create enhanced debug analysis
    enhanced_debug = create_enhanced_debug_output(
        debug_analysis=debug_analysis,
        semantic_mode=semantic_mode,
        requested_style=requested_style,
        requested_occasion=requested_occasion,
        requested_mood=requested_mood
    )
    
    # Build final response
    response = {
        "outfits": outfits,
        "debug": enhanced_debug
    }
    
    # Add debug output if available
    if debug_output:
        response["debug_output"] = debug_output
    
    # Add semantic mode indicator
    response["semantic_mode"] = semantic_mode
    
    # Add summary statistics
    total_items = len(enhanced_debug)
    valid_items = sum(1 for item in enhanced_debug if item["valid"])
    response["summary"] = {
        "total_items": total_items,
        "valid_items": valid_items,
        "rejected_items": total_items - valid_items,
        "filter_pass_rate": valid_items / total_items if total_items > 0 else 0,
        "semantic_mode_active": semantic_mode
    }
    
    return response
