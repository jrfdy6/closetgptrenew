#!/usr/bin/env python3
"""
Compatibility Matrix Service
============================

Semantic compatibility scoring based on occasion, style, and mood combinations.
Replaces crude string matching with intelligent metadata-based scoring.
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CompatibilityResult:
    """Result of compatibility check"""
    is_compatible: bool
    score: float
    reason: str
    hard_rejection: bool = False

class CompatibilityMatrixService:
    """Service for semantic compatibility scoring"""
    
    def __init__(self):
        self.compatibility_matrix = self._load_compatibility_matrix()
        self.hard_incompatibilities = self._load_hard_incompatibilities()
    
    def _load_compatibility_matrix(self) -> Dict:
        """Load the compatibility matrix from configuration"""
        return {
            "Business": {
                "Classic": {
                    "Professional": 1.0,
                    "Casual": 0.2,
                    "Playful": 0.0
                },
                "Business Casual": {
                    "Professional": 0.8,
                    "Casual": 1.0,
                    "Playful": 0.1
                },
                "Preppy": {
                    "Professional": 0.7,
                    "Casual": 0.9,
                    "Playful": 0.2
                }
            },
            "Casual": {
                "Casual": {
                    "Professional": 0.1,
                    "Casual": 1.0,
                    "Playful": 0.8
                },
                "Boho": {
                    "Professional": 0.0,
                    "Casual": 0.8,
                    "Playful": 1.0
                },
                "Streetwear": {
                    "Professional": 0.0,
                    "Casual": 0.9,
                    "Playful": 1.0
                }
            },
            "Party": {
                "Trendy": {
                    "Professional": 0.0,
                    "Casual": 0.5,
                    "Playful": 1.0
                },
                "Romantic": {
                    "Professional": 0.0,
                    "Casual": 0.4,
                    "Playful": 1.0
                }
            },
            "Athletic": {
                "Casual": {
                    "Professional": 0.0,
                    "Casual": 0.8,
                    "Playful": 0.7
                },
                "Sporty": {
                    "Professional": 0.0,
                    "Casual": 1.0,
                    "Playful": 0.9
                }
            }
        }
    
    def _load_hard_incompatibilities(self) -> Dict:
        """Load hard incompatibility rules"""
        return {
            "Business Formal": {
                "not_allowed": ["Athletic", "Beach", "Swimwear"]
            },
            "Athletic": {
                "not_allowed": ["Business Formal", "Evening Wear"]
            },
            "Beach": {
                "not_allowed": ["Business Formal", "Business Casual"]
            },
            "Swimwear": {
                "not_allowed": ["Business Formal", "Business Casual", "Formal"]
            }
        }
    
    def check_compatibility(self, item, target_occasion: str, target_style: str, target_mood: str) -> CompatibilityResult:
        """
        Check compatibility between item and target context
        
        Args:
            item: ClothingItem with style, occasion, mood arrays
            target_occasion: Target occasion (e.g., "Athletic")
            target_style: Target style (e.g., "Classic") 
            target_mood: Target mood (e.g., "Bold")
        
        Returns:
            CompatibilityResult with score and reasoning
        """
        
        # Extract item metadata
        item_styles = getattr(item, 'style', [])
        item_occasions = getattr(item, 'occasion', [])
        item_moods = getattr(item, 'mood', [])
        
        # Normalize to lists
        if isinstance(item_styles, str):
            item_styles = [item_styles]
        if isinstance(item_occasions, str):
            item_occasions = [item_occasions]
        if isinstance(item_moods, str):
            item_moods = [item_moods]
        
        # Step 1: Check hard incompatibilities
        hard_result = self._check_hard_incompatibilities(
            item_styles, item_occasions, target_occasion
        )
        if hard_result.hard_rejection:
            return hard_result
        
        # Step 2: Calculate soft compatibility score
        soft_score = self._calculate_soft_compatibility(
            item_styles, item_occasions, item_moods,
            target_occasion, target_style, target_mood
        )
        
        return CompatibilityResult(
            is_compatible=True,
            score=soft_score,
            reason=f"Soft compatibility: {soft_score:.2f}"
        )
    
    def _check_hard_incompatibilities(self, item_styles: List[str], item_occasions: List[str], target_occasion: str) -> CompatibilityResult:
        """Check for hard incompatibilities that should reject items"""
        
        # Check if any item style/occasion is incompatible with target occasion
        for style in item_styles:
            for occasion in item_occasions:
                # Create composite key (e.g., "Business Casual")
                composite_key = f"{style} {occasion}" if style != occasion else style
                
                # Check against hard incompatibilities
                for incompatible_category, rules in self.hard_incompatibilities.items():
                    if target_occasion in rules.get("not_allowed", []):
                        # Check if item matches the incompatible category
                        if (style.lower() in incompatible_category.lower() or 
                            occasion.lower() in incompatible_category.lower() or
                            composite_key.lower() in incompatible_category.lower()):
                            
                            return CompatibilityResult(
                                is_compatible=False,
                                score=0.0,
                                reason=f"Hard incompatibility: {composite_key} not allowed for {target_occasion}",
                                hard_rejection=True
                            )
        
        return CompatibilityResult(is_compatible=True, score=1.0, reason="No hard incompatibilities")
    
    def _calculate_soft_compatibility(self, item_styles: List[str], item_occasions: List[str], item_moods: List[str],
                                   target_occasion: str, target_style: str, target_mood: str) -> float:
        """Calculate soft compatibility score using the matrix"""
        
        best_score = 0.0
        best_match = ""
        
        # Try to find matches in the compatibility matrix
        for item_style in item_styles:
            for item_occasion in item_occasions:
                # Look for exact matches in matrix
                if target_occasion in self.compatibility_matrix:
                    occasion_matrix = self.compatibility_matrix[target_occasion]
                    
                    # Try exact style match
                    if item_style in occasion_matrix:
                        style_matrix = occasion_matrix[item_style]
                        if target_mood in style_matrix:
                            score = style_matrix[target_mood]
                            if score > best_score:
                                best_score = score
                                best_match = f"{item_style} + {target_mood}"
                    
                    # Try partial matches (e.g., "Business Casual" contains "Business")
                    for matrix_style in occasion_matrix.keys():
                        if (item_style.lower() in matrix_style.lower() or 
                            matrix_style.lower() in item_style.lower()):
                            style_matrix = occasion_matrix[matrix_style]
                            if target_mood in style_matrix:
                                score = style_matrix[target_mood] * 0.8  # Partial match penalty
                                if score > best_score:
                                    best_score = score
                                    best_match = f"{matrix_style} (partial) + {target_mood}"
        
        # If no matrix match found, use fallback scoring
        if best_score == 0.0:
            best_score = self._fallback_compatibility_scoring(
                item_styles, item_occasions, target_occasion, target_style
            )
            best_match = "fallback scoring"
        
        return best_score
    
    def _fallback_compatibility_scoring(self, item_styles: List[str], item_occasions: List[str], 
                                      target_occasion: str, target_style: str) -> float:
        """Fallback scoring when no matrix match is found"""
        
        # Basic compatibility rules
        if target_occasion.lower() == "athletic":
            athletic_indicators = ["sporty", "athletic", "casual", "active"]
            business_indicators = ["business", "professional", "formal", "preppy"]
            
            for style in item_styles:
                if any(indicator in style.lower() for indicator in athletic_indicators):
                    return 0.8
                elif any(indicator in style.lower() for indicator in business_indicators):
                    return 0.2
            
            return 0.5  # Neutral
        
        elif target_occasion.lower() == "business":
            business_indicators = ["business", "professional", "formal", "preppy", "classic"]
            casual_indicators = ["casual", "athletic", "sporty"]
            
            for style in item_styles:
                if any(indicator in style.lower() for indicator in business_indicators):
                    return 0.9
                elif any(indicator in style.lower() for indicator in casual_indicators):
                    return 0.3
            
            return 0.6  # Neutral
        
        # Default neutral score
        return 0.5
