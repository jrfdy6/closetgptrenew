"""
Semantic Normalization Utilities
Handles normalization of item metadata for semantic filtering
"""

from typing import List, Optional, Any, Dict


def normalize_array_strings(arr: Optional[List[str]]) -> List[str]:
    """Normalize array of strings to lowercase and filter empty values."""
    if not isinstance(arr, list):
        return []
    return [
        s.strip().lower() 
        for s in arr 
        if isinstance(s, str) and s.strip()
    ]


def canonicalize_style(s: str) -> str:
    """Canonicalize a style string to lowercase."""
    return s.strip().lower()


def normalize_item_metadata(item: Any) -> Dict[str, Any]:
    """Normalize item metadata for semantic filtering."""
    # Handle both dict and object types
    if hasattr(item, '__dict__'):
        base_data = item.__dict__.copy()
        # For objects, use getattr
        style_data = getattr(item, 'style', [])
        occasion_data = getattr(item, 'occasion', [])
        mood_data = getattr(item, 'mood', [])
        season_data = getattr(item, 'season', [])
    elif isinstance(item, dict):
        base_data = item.copy()
        # For dictionaries, use get method
        style_data = item.get('style', [])
        occasion_data = item.get('occasion', [])
        mood_data = item.get('mood', [])
        season_data = item.get('season', [])
    else:
        base_data = {}
        style_data = occasion_data = mood_data = season_data = []
    
    return {
        **base_data,
        'style': normalize_array_strings(style_data),
        'occasion': normalize_array_strings(occasion_data),
        'mood': normalize_array_strings(mood_data),
        'season': normalize_array_strings(season_data),
    }
