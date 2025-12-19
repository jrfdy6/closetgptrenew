"""
Filters Package
===============

This package contains modular filtering logic for outfit generation.

Modules:
- formality_tier_system: Progressive tier-based filtering for formal occasions
- occasion_filters: Occasion-specific hard filters (gym, formal, loungewear, etc.)
"""

from .formality_tier_system import FormalityTierSystem, FormalityTier, OccasionTierConfig
from .occasion_filters import OccasionFilters

__all__ = [
    'FormalityTierSystem',
    'FormalityTier',
    'OccasionTierConfig',
    'OccasionFilters',
]

