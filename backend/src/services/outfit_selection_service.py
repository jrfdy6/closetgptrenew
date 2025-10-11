"""
Outfit Selection Service
Smart selection and item categorization logic with layer-aware outfit construction.
"""

from typing import List, Dict, Any, Optional, Tuple
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile
import logging

logger = logging.getLogger(__name__)

class OutfitSelectionService:
    def __init__(self):
        # Define layer hierarchy (order matters!)
        self.layer_hierarchy = ['Base', 'Inner', 'Mid', 'Outer', 'Bottom', 'Footwear', 'Accessory']
        
        # Define sleeve length hierarchy for validation
        self.sleeve_hierarchy = {
            'Sleeveless': 0,
            'None': 0,
            'Short': 1,
            '3/4': 2,
            'Long': 3
        }
        
    def _safe_temperature_convert(self, temperature) -> float:
        """Safely convert temperature to float to prevent string vs float comparison errors."""
        if isinstance(temperature, str):
            try:
                return float(temperature)
            except (ValueError, TypeError):
                return 70.0
        elif temperature is None:
            return 70.0
        else:
            return float(temperature)
            
    def smart_selection_phase(self, filtered_wardrobe: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
        """Phase 3: Layer-aware item selection using wearLayer metadata."""
        if not filtered_wardrobe:
            return []
        
        logger.info(f"🎨 Starting layer-aware selection with {len(filtered_wardrobe)} items")
        
        # Get base item from context
        base_item = (context.get("base_item") if context else None)
        target_count = (context.get("target_counts", {}) if context else {}).get("min_items", 3)
        
        # Use layer-aware selection
        selected_items = self._build_layered_outfit(
            filtered_wardrobe, 
            context, 
            base_item, 
            target_count
        )
        
        logger.info(f"🎯 Layer-aware selection complete: {len(selected_items)} items")
        for i, item in enumerate(selected_items):
            layer = self._get_item_layer(item)
            sleeve = self._get_sleeve_length(item)
            logger.info(f"  {i+1}. {item.name} ({item.type}) - Layer: {layer}, Sleeve: {sleeve}")
        
        return selected_items
    
    def _build_layered_outfit(
        self, 
        wardrobe: List[ClothingItem], 
        context: Dict[str, Any],
        base_item: Optional[ClothingItem],
        target_count: int
    ) -> List[ClothingItem]:
        """
        Build outfit respecting layer hierarchy using wearLayer metadata.
        
        Layer hierarchy: Base → Inner → Mid → Outer → Bottom → Footwear → Accessory
        """
        # Categorize items by layer
        layers = self._categorize_by_layer(wardrobe)
        
        logger.info(f"📊 Layer distribution:")
        for layer in self.layer_hierarchy:
            if layer in layers:
                logger.info(f"  - {layer}: {len(layers[layer])} items")
        
        selected = []
        
        # Always include base item first if provided
        if base_item:
            selected.append(base_item)
            base_layer = self._get_item_layer(base_item)
            logger.info(f"🎯 Base item: {base_item.name} ({base_layer} layer)")
        
        # Get temperature for layer decisions
        weather = context.get("weather") if context else None
        temp = self._safe_temperature_convert(
            weather.temperature if weather and hasattr(weather, 'temperature') else 70.0
        )
        
        # Select essential layers first (Bottom + Top/Outer)
        selected = self._select_essential_layers(selected, layers, base_item, temp)
        
        # Add additional layers based on temperature and target count
        selected = self._add_complementary_layers(
            selected, 
            layers, 
            base_item, 
            temp, 
            target_count
        )
        
        # Validate layer compatibility (sleeve lengths, etc.)
        selected = self._validate_and_fix_layer_conflicts(selected)
        
        return selected
    
    def _categorize_by_layer(self, items: List[ClothingItem]) -> Dict[str, List[ClothingItem]]:
        """Categorize items by their wearLayer metadata."""
        layers = {layer: [] for layer in self.layer_hierarchy}
        
        for item in items:
            layer = self._get_item_layer(item)
            if layer in layers:
                layers[layer].append(item)
            else:
                # Fallback: infer layer from type if metadata is missing
                inferred_layer = self._infer_layer_from_type(item)
                layers[inferred_layer].append(item)
        
        return layers
    
    def _get_item_layer(self, item: ClothingItem) -> str:
        """Extract wearLayer from item metadata."""
        # Try metadata.visualAttributes.wearLayer first
        if hasattr(item, 'metadata') and item.metadata:
            if hasattr(item.metadata, 'visualAttributes'):
                visual_attrs = item.metadata.visualAttributes
                if visual_attrs and hasattr(visual_attrs, 'wearLayer'):
                    return visual_attrs.wearLayer
            # Try dict format
            elif isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    layer = visual_attrs.get('wearLayer')
                    if layer:
                        return layer
        
        # Fallback: infer from type
        return self._infer_layer_from_type(item)
    
    def _infer_layer_from_type(self, item: ClothingItem) -> str:
        """Infer layer from item type if metadata is missing."""
        item_type = item.type.lower() if isinstance(item.type, str) else str(item.type).lower()
        item_name = item.name.lower()
        
        # Base layer items
        if any(term in item_name or term in item_type for term in ['underwear', 'undershirt', 'base layer']):
            return 'Base'
        
        # Inner layer (t-shirts, tank tops, thin shirts)
        if any(term in item_type for term in ['t-shirt', 'tank', 'cami', 'tee']):
            return 'Inner'
        
        # Outer layer (jackets, coats, heavy sweaters)
        if any(term in item_type for term in ['jacket', 'coat', 'blazer', 'cardigan']):
            return 'Outer'
        
        # Mid layer (shirts, light sweaters, hoodies)
        if any(term in item_type for term in ['shirt', 'sweater', 'hoodie', 'sweatshirt', 'blouse']):
            # Special case: short-sleeve sweaters are often outer layers
            if 'sweater' in item_type and self._get_sleeve_length(item) == 'Short':
                return 'Outer'
            return 'Mid'
        
        # Bottom
        if any(term in item_type for term in ['pants', 'jeans', 'shorts', 'skirt', 'trousers']):
            return 'Bottom'
        
        # Footwear
        if any(term in item_type for term in ['shoes', 'sneakers', 'boots', 'sandals', 'heels']):
            return 'Footwear'
        
        # Accessories
        if any(term in item_type for term in ['belt', 'watch', 'scarf', 'hat', 'bag', 'accessory']):
            return 'Accessory'
        
        # Default to Mid for unknown types
        return 'Mid'
    
    def _select_essential_layers(
        self, 
        selected: List[ClothingItem], 
        layers: Dict[str, List[ClothingItem]],
        base_item: Optional[ClothingItem],
        temperature: float
    ) -> List[ClothingItem]:
        """Select essential layers (Bottom + at least one top layer)."""
        selected_ids = {item.id for item in selected}
        
        # Need bottom (unless we have a dress/romper)
        if not any(self._get_item_layer(item) == 'Bottom' for item in selected):
            if layers['Bottom']:
                for bottom in layers['Bottom']:
                    if bottom.id not in selected_ids:
                        selected.append(bottom)
                        selected_ids.add(bottom.id)
                        logger.info(f"  ✅ Essential bottom: {bottom.name}")
                        break
        
        # Need footwear
        if not any(self._get_item_layer(item) == 'Footwear' for item in selected):
            if layers['Footwear']:
                for shoes in layers['Footwear']:
                    if shoes.id not in selected_ids:
                        selected.append(shoes)
                        selected_ids.add(shoes.id)
                        logger.info(f"  ✅ Essential footwear: {shoes.name}")
                break
        
        # Need at least one top layer (Inner, Mid, or Outer)
        has_top = any(
            self._get_item_layer(item) in ['Inner', 'Mid', 'Outer'] 
            for item in selected
        )
        
        if not has_top:
            # Prefer Mid layer for basic coverage
            for layer_name in ['Mid', 'Inner', 'Outer']:
                if layers[layer_name]:
                    for item in layers[layer_name]:
                        if item.id not in selected_ids:
                            selected.append(item)
                            selected_ids.add(item.id)
                            logger.info(f"  ✅ Essential top ({layer_name}): {item.name}")
                            has_top = True
                            break
                if has_top:
                    break
        
        return selected
    
    def _add_complementary_layers(
        self,
        selected: List[ClothingItem],
        layers: Dict[str, List[ClothingItem]],
        base_item: Optional[ClothingItem],
        temperature: float,
        target_count: int
    ) -> List[ClothingItem]:
        """Add complementary layers based on temperature and style."""
        selected_ids = {item.id for item in selected}
        
        # Determine if we need layering based on temperature
        if temperature < 50:
            # Cold: Add outer layer if missing
            if not any(self._get_item_layer(item) == 'Outer' for item in selected):
                if layers['Outer']:
                    for outer in layers['Outer']:
                        if outer.id not in selected_ids and len(selected) < target_count:
                            # Check sleeve compatibility before adding
                            if self._is_layer_compatible_with_outfit(outer, selected):
                                selected.append(outer)
                                selected_ids.add(outer.id)
                                logger.info(f"  🧥 Cold weather outer: {outer.name}")
                                break
        
        elif temperature < 65:
            # Cool: Optional light layer
            if len(selected) < target_count:
                for layer_name in ['Outer', 'Mid']:
                    if layers[layer_name]:
                        for item in layers[layer_name]:
                            if item.id not in selected_ids:
                                if self._is_layer_compatible_with_outfit(item, selected):
                                    selected.append(item)
                                    selected_ids.add(item.id)
                                    logger.info(f"  🍂 Cool weather layer ({layer_name}): {item.name}")
                                    break
                        if len(selected) >= target_count:
                            break
        
        # Add accessories if room
        if len(selected) < target_count and layers['Accessory']:
            for accessory in layers['Accessory']:
                if accessory.id not in selected_ids and len(selected) < target_count:
                    selected.append(accessory)
                    selected_ids.add(accessory.id)
                    logger.info(f"  ✨ Accessory: {accessory.name}")
        
        return selected
    
    def _is_layer_compatible_with_outfit(
        self, 
        new_item: ClothingItem, 
        current_outfit: List[ClothingItem]
    ) -> bool:
        """
        Check if a new layer is compatible with current outfit.
        
        Key rule: Short-sleeve outer layers cannot be worn over long-sleeve inner layers.
        """
        new_layer = self._get_item_layer(new_item)
        new_sleeve = self._get_sleeve_length(new_item)
        
        # Get layer position
        new_layer_pos = self.layer_hierarchy.index(new_layer) if new_layer in self.layer_hierarchy else 99
        
        for existing_item in current_outfit:
            existing_layer = self._get_item_layer(existing_item)
            existing_sleeve = self._get_sleeve_length(existing_item)
            existing_layer_pos = self.layer_hierarchy.index(existing_layer) if existing_layer in self.layer_hierarchy else 99
            
            # Check sleeve length compatibility for layered tops
            if new_layer in ['Mid', 'Outer'] and existing_layer in ['Inner', 'Mid']:
                # If new item is worn OVER existing item
                if new_layer_pos > existing_layer_pos:
                    # Get sleeve hierarchy values
                    new_sleeve_val = self.sleeve_hierarchy.get(new_sleeve, 1)
                    existing_sleeve_val = self.sleeve_hierarchy.get(existing_sleeve, 1)
                    
                    # Rule: Outer layer sleeves must be >= inner layer sleeves
                    # Short-sleeve sweater (Outer) CANNOT go over long-sleeve shirt (Inner/Mid)
                    if new_sleeve_val < existing_sleeve_val:
                        logger.warning(
                            f"  ❌ Sleeve conflict: {new_item.name} ({new_sleeve} sleeve, {new_layer}) "
                            f"cannot layer over {existing_item.name} ({existing_sleeve} sleeve, {existing_layer})"
                        )
                        return False
        
        return True
    
    def _get_sleeve_length(self, item: ClothingItem) -> str:
        """Extract sleeve length from metadata."""
        # Try metadata.visualAttributes.sleeveLength
        if hasattr(item, 'metadata') and item.metadata:
            if hasattr(item.metadata, 'visualAttributes'):
                visual_attrs = item.metadata.visualAttributes
                if visual_attrs and hasattr(visual_attrs, 'sleeveLength'):
                    return visual_attrs.sleeveLength or 'Unknown'
            # Try dict format
            elif isinstance(item.metadata, dict):
                visual_attrs = item.metadata.get('visualAttributes', {})
                if isinstance(visual_attrs, dict):
                    sleeve = visual_attrs.get('sleeveLength')
                    if sleeve:
                        return sleeve
        
        # Fallback: infer from name/type
        item_name = item.name.lower()
        
        if any(term in item_name for term in ['sleeveless', 'tank', 'vest']):
            return 'Sleeveless'
        elif any(term in item_name for term in ['short sleeve', 'short-sleeve', 't-shirt', 'tee']):
            return 'Short'
        elif any(term in item_name for term in ['3/4', 'three quarter']):
            return '3/4'
        elif any(term in item_name for term in ['long sleeve', 'long-sleeve']):
            return 'Long'
        
        return 'Unknown'
    
    def _validate_and_fix_layer_conflicts(
        self, 
        selected: List[ClothingItem]
    ) -> List[ClothingItem]:
        """Validate and fix any layer conflicts in the final outfit."""
        # Sort by layer hierarchy to ensure proper order
        sorted_items = sorted(
            selected,
            key=lambda item: self.layer_hierarchy.index(self._get_item_layer(item)) 
            if self._get_item_layer(item) in self.layer_hierarchy else 99
        )
        
        validated = []
        
        for item in sorted_items:
            if self._is_layer_compatible_with_outfit(item, validated):
                validated.append(item)
            else:
                logger.warning(f"  🚫 Removed {item.name} due to layer conflict")
        
        return validated
        
    def select_core_items(self, filtered_wardrobe: List[ClothingItem], context: Dict[str, Any]) -> List[ClothingItem]:
        """Select core items for the outfit."""
        # For now, select first few items
        return filtered_wardrobe[:3] if len(filtered_wardrobe) >= 3 else filtered_wardrobe
        
    def get_item_categories(self, items: List[ClothingItem]) -> Dict[str, List[ClothingItem]]:
        """Get items categorized by type."""
        categories = {}
        for item in items:
            item_type = item.type.lower()
            if item_type not in categories:
                categories[item_type] = []
            categories[item_type].append(item)
        return categories
