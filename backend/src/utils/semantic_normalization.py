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
    elif isinstance(item, dict):
        base_data = item.copy()
    else:
        base_data = {}
    
    return {
        **base_data,
        'style': normalize_array_strings(getattr(item, 'style', [])),
        'occasion': normalize_array_strings(getattr(item, 'occasion', [])),
        'mood': normalize_array_strings(getattr(item, 'mood', [])),
        'season': normalize_array_strings(getattr(item, 'season', [])),
    }
