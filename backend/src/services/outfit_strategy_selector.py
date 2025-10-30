"""
Outfit Strategy Selector
========================

Selects outfit composition strategies to create diverse, interesting outfits
while respecting context (occasion, style, mood) and special rules.
"""

import logging
import random
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class OutfitStrategy(Enum):
    """Available outfit composition strategies"""
    TRADITIONAL = "traditional"           # All items match target formality/style
    HIGH_LOW = "high_low"                # Formal + casual intentional contrast
    LAYERING_CONTRAST = "layering_contrast"  # Different formality in layers
    STATEMENT_PIECE = "statement_piece"  # One bold item, rest neutral
    GRADUATED = "graduated"              # Smooth formality progression
    MONOCHROME = "monochrome"            # Color harmony priority
    COLOR_POP = "color_pop"              # Neutral base + ONE bright accent
    TEXTURE_PLAY = "texture_play"        # Mix smooth + textured + patterned
    PROPORTIONS = "proportions"          # Fitted + loose balance
    ERA_BLEND = "era_blend"              # Mix vintage + modern


@dataclass
class StrategyWeights:
    """Strategy selection weights"""
    traditional: float = 0.30  # 30% - safe, always works
    high_low: float = 0.10
    layering_contrast: float = 0.08
    statement_piece: float = 0.10
    graduated: float = 0.08
    monochrome: float = 0.10
    color_pop: float = 0.08
    texture_play: float = 0.06
    proportions: float = 0.06
    era_blend: float = 0.04


class OutfitStrategySelector:
    """Selects outfit strategies based on context and rotation"""
    
    def __init__(self):
        self.default_weights = StrategyWeights()
    
    def select_strategy(
        self,
        occasion: str,
        style: str,
        mood: str,
        user_outfit_count: int,
        has_base_item: bool = False
    ) -> OutfitStrategy:
        """
        Select outfit strategy using weighted rotation with context awareness.
        
        Args:
            occasion: Target occasion (Interview, Weekend, etc.)
            style: Target style (Urban Professional, Casual, etc.)
            mood: Target mood (Bold, Subtle, etc.)
            user_outfit_count: Total outfits user has generated (for rotation)
            has_base_item: Whether a base item is specified
            
        Returns:
            Selected OutfitStrategy
        """
        occasion_lower = occasion.lower() if occasion else ""
        style_lower = style.lower() if style else ""
        mood_lower = mood.lower() if mood else ""
        
        logger.info(f"🎨 STRATEGY SELECTOR: Selecting for {occasion} + {style} + {mood}, outfit #{user_outfit_count}")
        
        # Get context-appropriate strategies
        allowed_strategies = self._filter_strategies_by_context(
            occasion_lower, style_lower, mood_lower, has_base_item
        )
        
        logger.info(f"   📋 Context allows {len(allowed_strategies)} strategies: {[s.value for s in allowed_strategies]}")
        
        # Get weights for allowed strategies
        strategy_weights = self._get_strategy_weights(allowed_strategies, style_lower, mood_lower)
        
        # Use rotation index to add deterministic variety
        rotation_index = user_outfit_count % len(allowed_strategies)
        
        # Combine rotation with weighted random for controlled diversity
        # 70% rotation (predictable), 30% weighted random (surprise)
        use_rotation = random.random() < 0.7
        
        if use_rotation:
            # Deterministic rotation through allowed strategies
            selected = allowed_strategies[rotation_index]
            logger.info(f"   🔄 ROTATION: Selected strategy #{rotation_index + 1}/{len(allowed_strategies)}: {selected.value}")
        else:
            # Weighted random selection
            selected = random.choices(
                allowed_strategies,
                weights=[strategy_weights[s] for s in allowed_strategies],
                k=1
            )[0]
            logger.info(f"   🎲 WEIGHTED RANDOM: Selected {selected.value}")
        
        logger.info(f"✅ STRATEGY: {selected.value.upper().replace('_', ' ')}")
        return selected
    
    def _filter_strategies_by_context(
        self,
        occasion: str,
        style: str,
        mood: str,
        has_base_item: bool
    ) -> List[OutfitStrategy]:
        """Filter strategies based on occasion, style, mood constraints"""
        
        # Start with all strategies
        all_strategies = list(OutfitStrategy)
        allowed = all_strategies.copy()
        
        # OCCASION-BASED FILTERING
        if occasion in ['interview', 'business', 'formal', 'conference']:
            # Conservative - no risky strategies
            allowed = [s for s in allowed if s in [
                OutfitStrategy.TRADITIONAL,
                OutfitStrategy.GRADUATED,
                OutfitStrategy.MONOCHROME,
                OutfitStrategy.PROPORTIONS
            ]]
            logger.debug(f"   🔒 Conservative occasion: Limited to safe strategies")
        
        elif occasion in ['gym', 'athletic', 'workout']:
            # Athletic - ONLY traditional (special rules)
            allowed = [OutfitStrategy.TRADITIONAL]
            logger.debug(f"   🏃 Athletic occasion: Only traditional allowed")
        
        elif occasion in ['party', 'date', 'night out', 'club']:
            # Creative - ALL strategies allowed, boost statement
            logger.debug(f"   🎉 Party/Date: All strategies allowed")
        
        elif occasion in ['casual', 'weekend', 'loungewear']:
            # Relaxed - favor creative strategies
            logger.debug(f"   😌 Casual occasion: Favor creative strategies")
        
        # STYLE-BASED FILTERING
        if style in ['minimalist', 'scandinavian']:
            # Clean aesthetics - remove busy strategies
            allowed = [s for s in allowed if s not in [
                OutfitStrategy.STATEMENT_PIECE,
                OutfitStrategy.TEXTURE_PLAY,
                OutfitStrategy.ERA_BLEND
            ]]
            logger.debug(f"   🧘 Minimalist style: Removed busy strategies")
        
        elif style in ['maximalist', 'avant-garde', 'artsy']:
            # Bold aesthetics - favor creative strategies
            allowed = [s for s in allowed if s in [
                OutfitStrategy.HIGH_LOW,
                OutfitStrategy.STATEMENT_PIECE,
                OutfitStrategy.LAYERING_CONTRAST,
                OutfitStrategy.TEXTURE_PLAY,
                OutfitStrategy.COLOR_POP,
                OutfitStrategy.ERA_BLEND,
                OutfitStrategy.GRADUATED
            ]]
            logger.debug(f"   🎨 Maximalist style: Favor bold strategies")
        
        elif style in ['classic', 'preppy', 'old money']:
            # Timeless aesthetics - favor structured strategies
            allowed = [s for s in allowed if s in [
                OutfitStrategy.TRADITIONAL,
                OutfitStrategy.GRADUATED,
                OutfitStrategy.MONOCHROME,
                OutfitStrategy.PROPORTIONS
            ]]
            logger.debug(f"   👔 Classic style: Favor structured strategies")
        
        # MOOD-BASED ADJUSTMENTS
        if mood in ['bold', 'energetic', 'playful']:
            # Bold moods - ensure at least one creative strategy available
            if OutfitStrategy.STATEMENT_PIECE in all_strategies and OutfitStrategy.STATEMENT_PIECE not in allowed:
                allowed.append(OutfitStrategy.STATEMENT_PIECE)
            if OutfitStrategy.COLOR_POP in all_strategies and OutfitStrategy.COLOR_POP not in allowed:
                allowed.append(OutfitStrategy.COLOR_POP)
        
        elif mood in ['subtle', 'serene', 'relaxed']:
            # Subtle moods - avoid statement strategies
            allowed = [s for s in allowed if s not in [
                OutfitStrategy.STATEMENT_PIECE,
                OutfitStrategy.COLOR_POP
            ]]
        
        # Ensure we always have at least Traditional as fallback
        if not allowed or len(allowed) == 0:
            allowed = [OutfitStrategy.TRADITIONAL]
            logger.warning(f"   ⚠️ All strategies filtered out, using Traditional fallback")
        
        return allowed
    
    def _get_strategy_weights(
        self,
        allowed_strategies: List[OutfitStrategy],
        style: str,
        mood: str
    ) -> dict:
        """Get weights for allowed strategies, adjusted by style/mood"""
        weights = {}
        
        for strategy in allowed_strategies:
            # Start with default weight
            base_weight = getattr(self.default_weights, strategy.value, 0.1)
            
            # Adjust based on style
            if style in ['maximalist', 'avant-garde'] and strategy in [
                OutfitStrategy.STATEMENT_PIECE,
                OutfitStrategy.COLOR_POP,
                OutfitStrategy.TEXTURE_PLAY
            ]:
                base_weight *= 1.5  # Boost creative strategies for creative styles
            
            elif style in ['minimalist', 'scandinavian'] and strategy in [
                OutfitStrategy.TRADITIONAL,
                OutfitStrategy.MONOCHROME
            ]:
                base_weight *= 1.5  # Boost clean strategies for minimal styles
            
            # Adjust based on mood
            if mood in ['bold', 'energetic'] and strategy in [
                OutfitStrategy.STATEMENT_PIECE,
                OutfitStrategy.HIGH_LOW,
                OutfitStrategy.COLOR_POP
            ]:
                base_weight *= 1.3  # Boost bold strategies for bold moods
            
            elif mood in ['subtle', 'serene'] and strategy in [
                OutfitStrategy.TRADITIONAL,
                OutfitStrategy.MONOCHROME,
                OutfitStrategy.GRADUATED
            ]:
                base_weight *= 1.3  # Boost subtle strategies for subtle moods
            
            weights[strategy] = base_weight
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        weights = {s: w / total_weight for s, w in weights.items()}
        
        return weights
    
    def get_strategy_description(self, strategy: OutfitStrategy) -> str:
        """Get human-readable description of what each strategy does"""
        descriptions = {
            OutfitStrategy.TRADITIONAL: "All items match your target style and formality",
            OutfitStrategy.HIGH_LOW: "Mixing dressy and casual pieces for modern sophistication",
            OutfitStrategy.LAYERING_CONTRAST: "Contrasting formality levels through layering",
            OutfitStrategy.STATEMENT_PIECE: "One standout item with supporting neutral pieces",
            OutfitStrategy.GRADUATED: "Smooth formality progression from casual to dressy",
            OutfitStrategy.MONOCHROME: "Cohesive color story across all pieces",
            OutfitStrategy.COLOR_POP: "Neutral foundation with one vibrant accent piece",
            OutfitStrategy.TEXTURE_PLAY: "Mixing smooth, textured, and patterned fabrics",
            OutfitStrategy.PROPORTIONS: "Balancing fitted and loose silhouettes",
            OutfitStrategy.ERA_BLEND: "Blending vintage classics with modern pieces"
        }
        return descriptions.get(strategy, "Custom outfit composition")


# Singleton instance
_strategy_selector_instance = None

def get_strategy_selector() -> OutfitStrategySelector:
    """Get singleton instance of strategy selector"""
    global _strategy_selector_instance
    if _strategy_selector_instance is None:
        _strategy_selector_instance = OutfitStrategySelector()
    return _strategy_selector_instance

