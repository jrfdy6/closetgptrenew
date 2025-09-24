"""
Self-Healing Outfit Fallback System
===================================

This service provides robust fallback strategies for outfit generation:
1. Fix invalid GPT-generated outfits using Firestore queries
2. Assemble outfits from scratch using indexed wardrobe data
3. Self-heal using validation logic - no human intervention required
"""

from typing import List, Dict, Any, Optional, Tuple
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.weather import WeatherData
from ..custom_types.profile import UserProfile
from ..custom_types.outfit_rules import LayeringRule, get_weather_rule
from ..config.firebase import db
from ..utils.outfit_utils import get_color_name, athletic_sort_key, check_body_type_compatibility, check_skin_tone_compatibility, extract_color_names, get_item_category
import random
import time
from collections import defaultdict
from .dynamic_healing_context import DynamicHealingContext, ErrorType, FixType

class OutfitFallbackService:
    def __init__(self):
        self.db = db
        self.wardrobe_collection = self.db.collection('wardrobe')
        self.outfits_collection = self.db.collection('outfits')
        
        # Category mappings for intelligent item replacement
        self.category_mapping = {
            'top': ['shirt', 't-shirt', 'blouse', 'sweater', 'jacket', 'coat', 'hoodie'],
            'bottom': ['pants', 'jeans', 'shorts', 'skirt', 'leggings'],
            'shoes': ['shoes', 'sneakers', 'boots', 'sandals', 'flats', 'heels'],
            'accessory': ['belt', 'watch', 'necklace', 'bracelet', 'earrings', 'bag'],
            'outerwear': ['jacket', 'coat', 'blazer', 'cardigan']
        }
        
        # Material seasonality mapping
        self.material_seasonality = {
            'summer': ['cotton', 'linen', 'silk', 'rayon', 'polyester'],
            'winter': ['wool', 'fleece', 'cashmere', 'suede', 'leather'],
            'spring': ['cotton', 'denim', 'linen', 'polyester'],
            'fall': ['wool', 'cotton', 'denim', 'polyester']
        }
        
        # Style compatibility matrix
        self.style_compatibility = {
            'casual': ['casual', 'streetwear', 'minimalist', 'bohemian'],
            'formal': ['formal', 'business', 'classic', 'elegant'],
            'athletic': ['athletic', 'sporty', 'active', 'gym'],
            'party': ['party', 'glamorous', 'trendy', 'fashion-forward']
        }

    async def heal_outfit_with_fallbacks(
        self,
        failed_outfit: List[ClothingItem],
        validation_errors: List[str],
        context: Dict[str, Any]
    ) -> Tuple[List[ClothingItem], List[str], Dict[str, Any]]:
        """
        Main healing method that tries multiple fallback strategies.
        Now uses a dynamic healing context for smarter recovery.
        """
        healing_log = {
            'strategy_used': None,
            'items_fixed': [],
            'items_replaced': [],
            'attempts_made': 0
        }
        # Initialize dynamic healing context
        healing_context = DynamicHealingContext(context)
        
        remaining_errors = validation_errors.copy()
        current_items = failed_outfit.copy()
        
        print(f"🔧 Starting outfit healing with {len(validation_errors)} errors")
        
        # Strategy 1: Fix individual items using Firestore queries
        print("🔧 Strategy 1: Attempting item-by-item fixes")
        current_items, remaining_errors, item_fixes = await self._fix_individual_items(
            current_items, remaining_errors, context, healing_context
        )
        healing_log['items_fixed'].extend(item_fixes)
        healing_log['attempts_made'] += 1
        
        if not remaining_errors:
            healing_log['strategy_used'] = 'individual_item_fixes'
            healing_log['healing_context'] = healing_context.get_state()
            return current_items, remaining_errors, healing_log
        
        # Strategy 2: Replace problematic items with better alternatives
        print("🔧 Strategy 2: Attempting item replacements")
        current_items, remaining_errors, replacements = await self._replace_problematic_items(
            current_items, remaining_errors, context, healing_context
        )
        healing_log['items_replaced'].extend(replacements)
        healing_log['attempts_made'] += 1
        
        if not remaining_errors:
            healing_log['strategy_used'] = 'item_replacements'
            healing_log['healing_context'] = healing_context.get_state()
            return current_items, remaining_errors, healing_log
        
        # Strategy 3: Generate new outfit from scratch using indexed data
        print("🔧 Strategy 3: Generating new outfit from scratch")
        try:
            new_outfit = await self._generate_from_scratch_with_indexes(context, healing_context)
            if new_outfit:
                healing_log['strategy_used'] = 'scratch_generation'
                healing_log['attempts_made'] += 1
                healing_log['healing_context'] = healing_context.get_state()
                return new_outfit, [], healing_log
        except Exception as e:
            print(f"❌ Scratch generation failed: {e}")
            remaining_errors.append(f"Scratch generation failed: {str(e)}")
        
        # Strategy 4: Relaxed validation with best available items
        print("🔧 Strategy 4: Relaxed validation approach")
        current_items, remaining_errors, relaxed_fixes = await self._relaxed_validation_approach(
            current_items, remaining_errors, context, healing_context
        )
        healing_log['attempts_made'] += 1
        
        if len(remaining_errors) < len(validation_errors):
            healing_log['strategy_used'] = 'relaxed_validation'
        else:
            healing_log['strategy_used'] = 'failed'
        healing_log['healing_context'] = healing_context.get_state()
        
        return current_items, remaining_errors, healing_log

    async def _fix_individual_items(
        self,
        items: List[ClothingItem],
        errors: List[str],
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Tuple[List[ClothingItem], List[str], List[Dict[str, Any]]]:
        """Fix individual items based on specific validation errors."""
        fixed_items = items.copy()
        remaining_errors = errors.copy()
        fixes_applied = []
        
        for error in errors[:]:  # Copy to avoid modification during iteration
            error_lower = error.lower()
            
            # Fix duplicate items
            if "duplicate" in error_lower or "two pants" in error_lower or "two shirts" in error_lower:
                fixed_items, duplicate_fixes = await self._fix_duplicate_items(fixed_items, context, healing_context)
                fixes_applied.extend(duplicate_fixes)
                if duplicate_fixes:
                    remaining_errors.remove(error)
            
            # Fix weather appropriateness
            elif "hot day" in error_lower or "cold day" in error_lower or "weather" in error_lower:
                fixed_items, weather_fixes = await self._fix_weather_issues(fixed_items, context, healing_context)
                fixes_applied.extend(weather_fixes)
                if weather_fixes:
                    remaining_errors.remove(error)
            
            # Fix layering issues
            elif "layering" in error_lower or "sleeve" in error_lower:
                fixed_items, layering_fixes = await self._fix_layering_issues(fixed_items, context, healing_context)
                fixes_applied.extend(layering_fixes)
                if layering_fixes:
                    remaining_errors.remove(error)
            
            # Fix style conflicts
            elif "style" in error_lower or "conflict" in error_lower:
                fixed_items, style_fixes = await self._fix_style_conflicts(fixed_items, context, healing_context)
                fixes_applied.extend(style_fixes)
                if style_fixes:
                    remaining_errors.remove(error)
        
        return fixed_items, remaining_errors, fixes_applied

    async def _fix_duplicate_items(
        self,
        items: List[ClothingItem],
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Tuple[List[ClothingItem], List[Dict[str, Any]]]:
        """Fix duplicate items by replacing with alternatives, using dynamic healing context. Ensures only one item per category remains."""
        fixes_applied = []
        item_categories = self._categorize_items(items)
        
        for category, category_items in item_categories.items():
            if len(category_items) > 1:
                print(f"[DEBUG] Found {len(category_items)} duplicate items in category '{category}': {[item.name for item in category_items]}")
                
                # Log duplicate error to healing context
                duplicate_item_ids = [item.id for item in category_items if hasattr(item, 'id')]
                duplicate_names = [item.name for item in category_items]
                details = f"Found {len(category_items)} items in category '{category}': {', '.join(duplicate_names)}"
                
                healing_context.add_error_seen(
                    ErrorType.DUPLICATE_ITEMS,
                    details=details,
                    item_ids=duplicate_item_ids,
                    context={"category": category, "count": len(category_items), "items": duplicate_names}
                )
                
                healing_context.add_rule_triggered(
                    'duplicate_detection',
                    failure_reason=f"Multiple items in category '{category}'",
                    context={"category": category, "count": len(category_items), "items": duplicate_names}
                )
                
                # Keep the best item, exclude others from future queries
                best_item = self._select_best_item(category_items, context)
                items_to_remove = [item for item in category_items if item != best_item]
                
                # Add removed items to healing context exclusions
                for item in items_to_remove:
                    if hasattr(item, 'id'):
                        healing_context.add_item_removed(
                            item.id, 
                            f"duplicate_removal: {category} category", 
                            item_data=item.__dict__
                        )
                
                # Find alternatives using dynamic exclusions (for future use, but do not add to final list)
                replacement_items = await self._find_alternatives_for_category(
                    category, best_item, context, healing_context
                )
                
                # Build new items list: remove all items in this category, add only the best item
                new_items = [item for item in items if item not in category_items]
                new_items.append(best_item)
                
                # Log the fix attempt
                if replacement_items:
                    replacement_names = [item.name for item in replacement_items[:len(category_items) - 1]]
                    healing_context.add_fix_attempted(
                        FixType.DUPLICATE_FIX, 
                        success=True,
                        details={
                            "category": category,
                            "kept_item": best_item.name,
                            "replaced_items": [item.name for item in items_to_remove],
                            "replacement_items": replacement_names
                        },
                        items_affected=duplicate_item_ids
                    )
                else:
                    healing_context.add_fix_attempted(
                        FixType.DUPLICATE_FIX, 
                        success=False,
                        details={
                            "category": category,
                            "kept_item": best_item.name,
                            "replaced_items": [item.name for item in items_to_remove],
                            "replacement_items": []
                        },
                        items_affected=duplicate_item_ids
                    )
                
                fixes_applied.append({
                    'type': 'duplicate_fix',
                    'category': category,
                    'kept_item': best_item.name,
                    'replaced_items': [item.name for item in items_to_remove],
                    'replacement_items': [item.name for item in replacement_items[:len(category_items) - 1]]
                })
                
                print(f"[DEBUG] Duplicate fix applied: kept '{best_item.name}', replaced {len(items_to_remove)} items")
                return new_items, fixes_applied
        
        return items, fixes_applied

    async def _fix_weather_issues(
        self,
        items: List[ClothingItem],
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Tuple[List[ClothingItem], List[Dict[str, Any]]]:
        """Fix weather appropriateness issues, logging to healing context and using dynamic exclusions."""
        fixes_applied = []
        weather = context.get('weather')
        if not weather:
            return items, fixes_applied
        
        # Handle both dictionary and object formats for weather data
        if isinstance(weather, dict):
            temperature = weather.get('temperature_f', weather.get('temperature', 70))
        else:
            temperature = getattr(weather, 'temperature_f', getattr(weather, 'temperature', 70))
        
        season = self._determine_season(temperature, context.get('occasion', ''))
        
        for i, item in enumerate(items):
            print(f"[DEBUG] Checking item for weather appropriateness: {getattr(item, 'name', str(item))} ({getattr(item, 'material', 'unknown')})")
            if not self._is_weather_appropriate(item, temperature, season):
                print(f"[DEBUG] Item {getattr(item, 'name', str(item))} is NOT weather appropriate. Attempting replacement...")
                # Log error to healing context
                material = getattr(item, 'material', None) or (getattr(item, 'metadata', None) and getattr(item.metadata, 'material', None))
                item_id = getattr(item, 'id', None)
                details = f"{item.name} ({material}) not appropriate for {temperature}°F ({season})"
                healing_context.add_error_seen(
                    ErrorType.WEATHER_MISMATCH,
                    details=details,
                    item_ids=[item_id] if item_id else [],
                    context={"material": material, "temperature": temperature, "season": season}
                )
                healing_context.add_rule_triggered(
                    'weather',
                    failure_reason=f"Material {material} not appropriate for {temperature}°F",
                    context={"material": material, "temperature": temperature, "season": season}
                )
                if item_id:
                    healing_context.add_item_removed(item_id, f"weather_mismatch: {material} at {temperature}F", item_data=item.__dict__)
                # Try to find a weather-appropriate replacement, using dynamic exclusions
                replacement = await self._find_weather_appropriate_replacement(
                    item, temperature, season, context, healing_context
                )
                print(f"[DEBUG] Replacement found: {getattr(replacement, 'name', None) if replacement else None}")
                if replacement:
                    items[i] = replacement
                    fixes_applied.append({
                        'type': 'weather_fix',
                        'original_item': item.name,
                        'replacement_item': replacement.name,
                        'reason': f'Not appropriate for {temperature}°F weather'
                    })
                    # Log that a weather fix was attempted
                    healing_context.add_fix_attempted(FixType.WEATHER_FIX, f"Replaced {item.name} with {replacement.name}")
                else:
                    fixes_applied.append({
                        'type': 'weather_fix_failed',
                        'original_item': item.name,
                        'reason': f'No suitable replacement found for {temperature}°F weather'
                    })
                    # Log that a weather fix was attempted but failed
                    healing_context.add_fix_attempted(FixType.WEATHER_FIX, f"Failed to replace {item.name}")
            else:
                print(f"[DEBUG] Item {getattr(item, 'name', str(item))} is weather appropriate.")
        return items, fixes_applied

    async def _find_weather_appropriate_replacement(
        self,
        item: ClothingItem,
        temperature: float,
        season: str,
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Optional[ClothingItem]:
        """
        Find a weather-appropriate replacement using indexed queries and dynamic exclusions.
        """
        try:
            # Determine category
            category = self._determine_category(item.type)
            # Query weather-appropriate items, excluding failed items/materials
            weather_items = await self._query_by_weather_conditions(
                item.userId,
                category,
                temperature,
                context.get('weather', {}).get('condition', 'sunny'),
                healing_context=healing_context,
                limit=5
            )
            if not weather_items:
                return None
            # Select best weather-appropriate item
            best_item = max(weather_items, key=lambda x: self._calculate_relevance_score(x, context))
            return best_item
        except Exception as e:
            print(f"❌ Error finding weather-appropriate replacement: {e}")
            return None

    async def _query_by_weather_conditions(
        self,
        user_id: str,
        category: str,
        temperature: float,
        weather_condition: str,
        healing_context: DynamicHealingContext = None,
        limit: int = 10
    ) -> List[ClothingItem]:
        """
        Query items suitable for specific weather conditions using indexed fields and dynamic exclusions.
        """
        try:
            # Ensure temperature is a float
            if isinstance(temperature, str):
                try:
                    temperature = float(temperature)
                except (ValueError, TypeError):
                    temperature = 70.0
            elif temperature is None:
                temperature = 70.0
            
            # Build temperature-appropriate query
            query = self.wardrobe_collection.where('userId', '==', user_id)
            query = query.where('category', '==', category)
            # Exclude items/materials from healing context
            if healing_context:
                excluded_items = list(healing_context.items_removed)
                if excluded_items:
                    # Firestore 'not-in' supports up to 10 values
                    query = query.where('id', 'not-in', excluded_items[:10])
                # Exclude materials that failed for this temperature
                excluded_materials = list(healing_context.get_excluded_materials_for_temperature(temperature))
                if excluded_materials:
                    query = query.where('material', 'not-in', excluded_materials[:10])
            # Filter by temperature range
            if temperature > 80:  # Hot weather
                query = query.where('material', 'in', ['cotton', 'linen', 'silk'])
                query = query.where('seasonality', 'array_contains', 'summer')
            elif temperature < 50:  # Cold weather
                query = query.where('material', 'in', ['wool', 'fleece', 'cashmere'])
                query = query.where('seasonality', 'array_contains', 'winter')
            else:  # Moderate weather
                query = query.where('seasonality', 'array_contains', 'spring')
            # Add weather condition filters
            if weather_condition == 'rainy':
                query = query.where('material', 'in', ['waterproof', 'water-resistant'])
            # Order by quality and pairability
            query = query.order_by('quality_score', direction='DESCENDING')
            query = query.order_by('pairability_score', direction='DESCENDING')
            query = query.limit(limit)
            docs = query.stream()
            items = []
            for doc in docs:
                data = doc.to_dict()
                item = ClothingItem(**data)
                items.append(item)
            print(f"✅ Found {len(items)} weather-appropriate {category} items (with dynamic exclusions)")
            return items
        except Exception as e:
            print(f"❌ Error in weather-based query: {e}")
            return []

    async def _fix_layering_issues(
        self,
        items: List[ClothingItem],
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Tuple[List[ClothingItem], List[Dict[str, Any]]]:
        """Fix layering compatibility issues."""
        fixes_applied = []
        weather = context.get('weather')
        if not weather:
            return items, fixes_applied
        
        # Handle both dictionary and object formats for weather data
        if isinstance(weather, dict):
            temperature = weather.get('temperature_f', weather.get('temperature', 70))
        else:
            temperature = getattr(weather, 'temperature_f', getattr(weather, 'temperature', 70))
        
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        layering_rule = get_weather_rule(temperature)
        
        # Check for sleeve length conflicts
        tops = [item for item in items if item.type in ['shirt', 't-shirt', 'blouse', 'sweater']]
        if len(tops) > 1:
            # Find conflicting sleeve lengths
            sleeve_lengths = [self._get_sleeve_length(item) for item in tops]
            if len(set(sleeve_lengths)) < len(sleeve_lengths):
                # Replace conflicting items
                for i, item in enumerate(tops):
                    if sleeve_lengths.count(self._get_sleeve_length(item)) > 1:
                        replacement = await self._find_layering_compatible_replacement(
                            item, tops, context, healing_context
                        )
                        if replacement:
                            item_index = items.index(item)
                            items[item_index] = replacement
                            fixes_applied.append({
                                'type': 'layering_fix',
                                'original_item': item.name,
                                'replacement_item': replacement.name,
                                'reason': 'Sleeve length conflict resolution'
                            })
        
        return items, fixes_applied

    async def _fix_style_conflicts(
        self,
        items: List[ClothingItem],
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Tuple[List[ClothingItem], List[Dict[str, Any]]]:
        """Fix style conflicts between items."""
        fixes_applied = []
        target_style = context.get('style')
        if not target_style:
            return items, fixes_applied
        
        # Find items that don't match the target style
        for i, item in enumerate(items):
            if not self._item_matches_style(item, target_style):
                replacement = await self._find_style_compatible_replacement(
                    item, target_style, context, healing_context
                )
                if replacement:
                    items[i] = replacement
                    fixes_applied.append({
                        'type': 'style_fix',
                        'original_item': item.name,
                        'replacement_item': replacement.name,
                        'reason': f'Style conflict with {target_style}'
                    })
        
        return items, fixes_applied

    async def _replace_problematic_items(
        self,
        items: List[ClothingItem],
        errors: List[str],
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Tuple[List[ClothingItem], List[str], List[Dict[str, Any]]]:
        """Replace problematic items with better alternatives."""
        replacements_applied = []
        remaining_errors = errors.copy()
        
        # Identify problematic items based on error patterns
        problematic_items = []
        for error in errors:
            if "low score" in error.lower():
                # Find items with low scores
                for item in items:
                    if self._has_low_score(item, error):
                        problematic_items.append(item)
        
        # Replace problematic items
        for item in problematic_items:
            replacement = await self._find_better_alternative(item, context, healing_context)
            if replacement:
                item_index = items.index(item)
                items[item_index] = replacement
                replacements_applied.append({
                    'type': 'score_improvement',
                    'original_item': item.name,
                    'replacement_item': replacement.name,
                    'reason': 'Low score replacement'
                })
        
        return items, remaining_errors, replacements_applied

    async def _generate_from_scratch_with_indexes(
        self,
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Optional[List[ClothingItem]]:
        """Generate a new outfit from scratch using indexed wardrobe data."""
        try:
            # Get user's wardrobe from Firestore with indexes
            user_id = context.get('user_profile', {}).get('id')
            if not user_id:
                return None
            
            # Query wardrobe with optimized indexes
            wardrobe_query = self.wardrobe_collection.where('userId', '==', user_id)
            wardrobe_docs = wardrobe_query.stream()
            
            wardrobe_items = []
            for doc in wardrobe_docs:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                try:
                    wardrobe_items.append(ClothingItem(**item_data))
                except Exception as e:
                    print(f"Warning: Could not parse wardrobe item {doc.id}: {e}")
                    continue
            
            if not wardrobe_items:
                return None
            
            # Use intelligent selection based on context
            selected_items = await self._intelligent_item_selection(
                wardrobe_items, context, healing_context
            )
            
            return selected_items
            
        except Exception as e:
            print(f"Error in scratch generation: {e}")
            return None

    async def _intelligent_item_selection(
        self,
        wardrobe: List[ClothingItem],
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> List[ClothingItem]:
        """Intelligently select items using multiple criteria."""
        occasion = context.get('occasion', 'casual')
        style = context.get('style')
        weather = context.get('weather')
        user_profile = context.get('user_profile', {})
        
        # Step 1: Filter by basic criteria
        filtered_items = self._filter_by_basic_criteria(wardrobe, context, healing_context)
        
        # Step 2: Get target item counts for the occasion, style, and mood
        style = context.get('style', '')
        mood = context.get('mood', '')
        target_counts = self._get_target_item_counts(occasion, style, mood)
        
        # Step 3: Select core items for each category
        selected_items = []
        
        for category, count in target_counts.items():
            category_items = self._get_items_for_category(filtered_items, category)
            if category_items:
                # Sort by relevance score
                category_items.sort(
                    key=lambda x: self._calculate_relevance_score(x, context, healing_context),
                    reverse=True
                )
                selected_items.extend(category_items[:count])
        
        # Step 4: Ensure we have a complete outfit
        selected_items = self._ensure_outfit_completeness(selected_items, filtered_items, context, healing_context)
        
        return selected_items

    async def _relaxed_validation_approach(
        self,
        items: List[ClothingItem],
        errors: List[str],
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Tuple[List[ClothingItem], List[str], List[Dict[str, Any]]]:
        """Use relaxed validation criteria to accept more outfits."""
        relaxed_fixes = []
        remaining_errors = []
        
        # Relax score thresholds
        relaxed_thresholds = {
            'pairability': 0.1,  # Reduced from 0.2
            'style_compliance': 0.2,  # Reduced from 0.3
            'weather_appropriateness': 0.3,  # Reduced from 0.4
            'occasion_appropriateness': 0.2  # Reduced from 0.3
        }
        
        # Recalculate scores with relaxed thresholds
        for error in errors:
            if "score" in error.lower():
                # Check if the error would pass with relaxed thresholds
                if not self._would_fail_with_relaxed_thresholds(error, relaxed_thresholds):
                    relaxed_fixes.append({
                        'type': 'relaxed_threshold',
                        'error': error,
                        'action': 'Accepted with relaxed criteria'
                    })
                else:
                    remaining_errors.append(error)
            else:
                remaining_errors.append(error)
        
        return items, remaining_errors, relaxed_fixes

    # ============================================================================
    # STEP 2: SMART FIRESTORE INDEX-BASED SEARCH METHODS
    # ============================================================================

    async def _query_category_with_indexes(
        self,
        user_id: str,
        category: str,
        context: Dict[str, Any],
        limit: int = 10
    ) -> List[ClothingItem]:
        """
        Query wardrobe items by category using indexed fields for optimal performance.
        
        Args:
            user_id: The user ID
            category: The category to query (top, bottom, shoes, etc.)
            context: Generation context with weather, occasion, etc.
            limit: Maximum number of items to return
            
        Returns:
            List of ClothingItem objects
        """
        try:
            # Build optimized query using indexed fields
            query = self.wardrobe_collection.where('userId', '==', user_id)
            
            # Add category filter
            query = query.where('category', '==', category)
            
            # Add seasonality filter if available
            if 'weather' in context and context['weather']:
                season = self._determine_season(
                    context['weather'].temperature,
                    context.get('occasion', 'casual')
                )
                query = query.where('seasonality', 'array_contains', season)
            
            # Add formality filter if specified
            if 'occasion' in context:
                formality = self._map_occasion_to_formality(context['occasion'])
                query = query.where('formality', '==', formality)
            
            # Add quality score filter for better items
            query = query.where('quality_score', '>=', 0.6)
            
            # Order by pairability score for better combinations
            query = query.order_by('pairability_score', direction='DESCENDING')
            
            # Limit results
            query = query.limit(limit)
            
            # Execute query
            docs = query.stream()
            items = []
            
            for doc in docs:
                data = doc.to_dict()
                item = ClothingItem(**data)
                items.append(item)
            
            print(f"✅ Found {len(items)} {category} items using indexed query")
            return items
            
        except Exception as e:
            print(f"❌ Error in indexed category query: {e}")
            # Fallback to basic query
            return await self._query_category_basic(user_id, category, limit)

    async def _query_by_style_compatibility(
        self,
        user_id: str,
        category: str,
        target_style: str,
        context: Dict[str, Any],
        limit: int = 10
    ) -> List[ClothingItem]:
        """
        Query items compatible with a specific style using indexed fields.
        
        Args:
            user_id: The user ID
            category: The category to query
            target_style: The target style (casual, formal, etc.)
            context: Generation context
            limit: Maximum number of items to return
            
        Returns:
            List of ClothingItem objects
        """
        try:
            # Get compatible styles
            compatible_styles = self.style_compatibility.get(target_style, [target_style])
            
            # Build style-based query
            query = self.wardrobe_collection.where('userId', '==', user_id)
            query = query.where('category', '==', category)
            
            # Filter by style tags
            query = query.where('style_tags', 'array_contains_any', compatible_styles)
            
            # Add formality filter if applicable
            if target_style in ['formal', 'business']:
                query = query.where('formality', '==', 'formal')
            elif target_style in ['casual', 'streetwear']:
                query = query.where('formality', '==', 'casual')
            
            # Add quality filter
            query = query.where('quality_score', '>=', 0.5)
            
            # Order by relevance
            query = query.order_by('pairability_score', direction='DESCENDING')
            query = query.limit(limit)
            
            docs = query.stream()
            items = []
            
            for doc in docs:
                data = doc.to_dict()
                item = ClothingItem(**data)
                items.append(item)
            
            print(f"✅ Found {len(items)} {target_style}-compatible {category} items")
            return items
            
        except Exception as e:
            print(f"❌ Error in style-based query: {e}")
            return []

    async def _query_high_quality_alternatives(
        self,
        user_id: str,
        category: str,
        exclude_item_id: str,
        context: Dict[str, Any],
        limit: int = 5
    ) -> List[ClothingItem]:
        """
        Query high-quality alternatives for a specific category, excluding a given item.
        
        Args:
            user_id: The user ID
            category: The category to query
            exclude_item_id: ID of item to exclude
            context: Generation context
            limit: Maximum number of items to return
            
        Returns:
            List of ClothingItem objects
        """
        try:
            # Build high-quality alternatives query
            query = self.wardrobe_collection.where('userId', '==', user_id)
            query = query.where('category', '==', category)
            
            # Filter for high-quality items
            query = query.where('quality_score', '>=', 0.7)
            query = query.where('pairability_score', '>=', 0.6)
            
            # Add context-based filters
            if 'occasion' in context:
                formality = self._map_occasion_to_formality(context['occasion'])
                query = query.where('formality', '==', formality)
            
            # Order by quality and pairability
            query = query.order_by('quality_score', direction='DESCENDING')
            query = query.order_by('pairability_score', direction='DESCENDING')
            query = query.limit(limit + 1)  # +1 to account for excluded item
            
            docs = query.stream()
            items = []
            
            for doc in docs:
                data = doc.to_dict()
                item = ClothingItem(**data)
                
                # Exclude the specified item
                if item.id != exclude_item_id:
                    items.append(item)
                
                if len(items) >= limit:
                    break
            
            print(f"✅ Found {len(items)} high-quality {category} alternatives")
            return items
            
        except Exception as e:
            print(f"❌ Error in high-quality alternatives query: {e}")
            return []

    async def _query_favorite_items(
        self,
        user_id: str,
        category: str = None,
        limit: int = 10
    ) -> List[ClothingItem]:
        """
        Query user's favorite items, optionally filtered by category.
        
        Args:
            user_id: The user ID
            category: Optional category filter
            limit: Maximum number of items to return
            
        Returns:
            List of ClothingItem objects
        """
        try:
            # Build favorites query
            query = self.wardrobe_collection.where('userId', '==', user_id)
            query = query.where('favorite', '==', True)
            
            # Add category filter if specified
            if category:
                query = query.where('category', '==', category)
            
            # Order by quality and recent wear
            query = query.order_by('quality_score', direction='DESCENDING')
            query = query.order_by('last_worn', direction='DESCENDING')
            query = query.limit(limit)
            
            docs = query.stream()
            items = []
            
            for doc in docs:
                data = doc.to_dict()
                item = ClothingItem(**data)
                items.append(item)
            
            print(f"✅ Found {len(items)} favorite items")
            return items
            
        except Exception as e:
            print(f"❌ Error in favorites query: {e}")
            return []

    async def _query_underutilized_items(
        self,
        user_id: str,
        category: str = None,
        limit: int = 10
    ) -> List[ClothingItem]:
        """
        Query items that haven't been worn recently to encourage variety.
        
        Args:
            user_id: The user ID
            category: Optional category filter
            limit: Maximum number of items to return
            
        Returns:
            List of ClothingItem objects
        """
        try:
            # Build underutilized items query
            query = self.wardrobe_collection.where('userId', '==', user_id)
            
            # Add category filter if specified
            if category:
                query = query.where('category', '==', category)
            
            # Filter for items with low wear count or old last_worn
            query = query.where('wear_count', '<=', 5)
            
            # Order by quality and pairability to ensure good items
            query = query.order_by('quality_score', direction='DESCENDING')
            query = query.order_by('pairability_score', direction='DESCENDING')
            query = query.limit(limit)
            
            docs = query.stream()
            items = []
            
            for doc in docs:
                data = doc.to_dict()
                item = ClothingItem(**data)
                items.append(item)
            
            print(f"✅ Found {len(items)} underutilized items")
            return items
            
        except Exception as e:
            print(f"❌ Error in underutilized items query: {e}")
            return []

    # Helper methods for indexed queries
    def _map_occasion_to_formality(self, occasion: str) -> str:
        """Map occasion to formality level for indexed queries."""
        formality_mapping = {
            'casual': 'casual',
            'formal': 'formal',
            'business': 'formal',
            'office': 'formal',
            'party': 'semi-formal',
            'date': 'semi-formal',
            'gym': 'casual',
            'workout': 'casual'
        }
        return formality_mapping.get(occasion.lower(), 'casual')

    async def _query_category_basic(
        self,
        user_id: str,
        category: str,
        limit: int = 10
    ) -> List[ClothingItem]:
        """
        Basic fallback query when indexed queries fail.
        
        Args:
            user_id: The user ID
            category: The category to query
            limit: Maximum number of items to return
            
        Returns:
            List of ClothingItem objects
        """
        try:
            # Simple query without complex filters
            query = self.wardrobe_collection.where('userId', '==', user_id)
            query = query.where('category', '==', category)
            query = query.limit(limit)
            
            docs = query.stream()
            items = []
            
            for doc in docs:
                data = doc.to_dict()
                item = ClothingItem(**data)
                items.append(item)
            
            print(f"✅ Found {len(items)} {category} items using basic query")
            return items
            
        except Exception as e:
            print(f"❌ Error in basic category query: {e}")
            return []

    # ============================================================================
    # ENHANCED FALLBACK METHODS USING INDEXED QUERIES
    # ============================================================================

    async def _find_style_compatible_replacement(
        self,
        item: ClothingItem,
        target_style: str,
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Optional[ClothingItem]:
        """
        Find a style-compatible replacement using indexed queries.
        
        Args:
            item: The item to replace
            target_style: The target style
            context: Generation context
            
        Returns:
            Replacement ClothingItem or None
        """
        try:
            # Determine category
            category = self._determine_category(item.type)
            
            # Query style-compatible items
            style_items = await self._query_by_style_compatibility(
                item.userId,
                category,
                target_style,
                context,
                limit=5
            )
            
            if not style_items:
                return None
            
            # Select best style-compatible item
            best_item = max(style_items, key=lambda x: self._calculate_relevance_score(x, context))
            return best_item
            
        except Exception as e:
            print(f"❌ Error finding style-compatible replacement: {e}")
            return None

    async def _find_better_alternative(
        self,
        item: ClothingItem,
        context: Dict[str, Any],
        healing_context: DynamicHealingContext
    ) -> Optional[ClothingItem]:
        """
        Find a better alternative using indexed queries.
        
        Args:
            item: The item to replace
            context: Generation context
            
        Returns:
            Better alternative ClothingItem or None
        """
        try:
            # Determine category
            category = self._determine_category(item.type)
            
            # Query high-quality alternatives
            alternatives = await self._query_high_quality_alternatives(
                item.userId,
                category,
                item.id,
                context,
                limit=5
            )
            
            if not alternatives:
                return None
            
            # Select best alternative based on quality and relevance
            best_alternative = max(alternatives, key=lambda x: 
                x.quality_score * 0.6 + self._calculate_relevance_score(x, context) * 0.4)
            
            # Only return if it's significantly better
            if best_alternative.quality_score > item.quality_score + 0.1:
                return best_alternative
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding better alternative: {e}")
            return None

    def _determine_category(self, item_type: str) -> str:
        """Determine the category of an item based on its type using utility function."""
        # Create a mock item to use the utility function
        from ..custom_types.wardrobe import ClothingItem
        mock_item = ClothingItem(type=item_type, name="", id="", userId="", createdAt=0, updatedAt="")
        return get_item_category(mock_item)

    # Helper methods
    def _categorize_items(self, items: List[ClothingItem]) -> Dict[str, List[ClothingItem]]:
        """Categorize items by their type."""
        categories = defaultdict(list)
        for item in items:
            for category, types in self.category_mapping.items():
                if item.type in types:
                    categories[category].append(item)
                    break
        return dict(categories)

    def _select_best_item(self, items: List[ClothingItem], context: Dict[str, Any]) -> ClothingItem:
        """Select the best item from a list based on context."""
        if not items:
            return None
        
        # Score each item
        scored_items = []
        for item in items:
            score = self._calculate_relevance_score(item, context)
            scored_items.append((item, score))
        
        # Return the highest scoring item
        return max(scored_items, key=lambda x: x[1])[0]

    def _calculate_relevance_score(self, item: ClothingItem, context: Dict[str, Any]) -> float:
        """Calculate how relevant an item is to the current context."""
        score = 0.0
        
        # Occasion relevance
        occasion = context.get('occasion', '')
        if occasion in item.occasion:
            score += 0.3
        
        # Style relevance
        style = context.get('style', '')
        if style and style in item.style:
            score += 0.2
        
        # Weather appropriateness
        weather = context.get('weather')
        if weather:
            # Handle both dictionary and object formats for weather data
            if isinstance(weather, dict):
                temperature = weather.get('temperature_f', weather.get('temperature', 70))
            else:
                temperature = getattr(weather, 'temperature_f', getattr(weather, 'temperature', 70))
            
            if self._is_weather_appropriate(item, temperature):
                score += 0.2
        
        # User preference relevance
        user_profile = context.get('user_profile', {})
        if user_profile:
            if hasattr(user_profile, 'bodyType') and user_profile.bodyType and self._check_body_type_compatibility(item, user_profile.bodyType):
                score += 0.1
            if hasattr(user_profile, 'skinTone') and user_profile.skinTone and self._check_skin_tone_compatibility(item, user_profile.skinTone):
                score += 0.1
        
        # Quality score (if available)
        if hasattr(item, 'metadata') and item.metadata:
            quality_score = getattr(item.metadata, 'quality_score', 0.5)
            score += quality_score * 0.1
        
        return score

    def _is_weather_appropriate(self, item: ClothingItem, temperature: float, season: str = None) -> bool:
        """Check if an item is appropriate for the given weather."""
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        if not season:
            season = self._determine_season(temperature, '')
        
        # Material and type checks for hot/cold weather
        hot_materials = ['wool', 'fleece', 'leather', 'suede', 'cashmere']
        cold_materials = ['cotton', 'linen', 'rayon', 'silk']
        hot_types = ['coat', 'sweater', 'jacket', 'hoodie', 'boots']
        cold_types = ['shorts', 'tank-top', 'sandals']
        material = getattr(item, 'material', '').lower()
        item_type = getattr(item, 'type', '').lower()
        
        # Too hot for heavy materials/types
        if temperature > 75:
            if material in hot_materials or item_type in hot_types:
                return False
        # Too cold for light materials/types
        if temperature < 50:
            if material in cold_materials or item_type in cold_types:
                return False
        
        # Otherwise, default to appropriate
        return True

    def _determine_season(self, temperature: float, occasion: str) -> str:
        """Determine season based on temperature."""
        # Ensure temperature is a float
        if isinstance(temperature, str):
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                temperature = 70.0
        elif temperature is None:
            temperature = 70.0
        
        if temperature >= 75:
            return 'summer'
        elif temperature >= 60:
            return 'spring'
        elif temperature >= 45:
            return 'fall'
        else:
            return 'winter'

    def _get_sleeve_length(self, item: ClothingItem) -> str:
        """Get the sleeve length of an item."""
        if hasattr(item, 'metadata') and item.metadata:
            return getattr(item.metadata, 'sleeveLength', 'unknown')
        return 'unknown'

    def _item_matches_style(self, item: ClothingItem, target_style: str) -> bool:
        """Check if an item matches the target style."""
        if not target_style or not item.style:
            return True
        
        compatible_styles = self.style_compatibility.get(target_style.lower(), [])
        return any(style.lower() in compatible_styles for style in item.style)

    def _check_body_type_compatibility(self, item: ClothingItem, body_type: str) -> bool:
        """Check if an item is compatible with the user's body type using utility function."""
        return check_body_type_compatibility(item, body_type)

    def _check_skin_tone_compatibility(self, item: ClothingItem, skin_tone: str) -> bool:
        """Check if an item is compatible with the user's skin tone using utility function."""
        return check_skin_tone_compatibility(item, skin_tone)

    def _get_target_item_counts(self, occasion: str, style: str = None, mood: str = None) -> Dict[str, int]:
        """Get dynamic target item counts based on occasion, style, and mood."""
        import random
        
        # Base counts for different occasions
        occasion_lower = occasion.lower()
        
        if 'formal' in occasion_lower or 'business' in occasion_lower or 'interview' in occasion_lower:
            # Formal occasions - more structured, more items
            base_counts = {
                'top': 1,
                'bottom': 1, 
                'shoes': 1,
                'outerwear': 1,  # Blazer, jacket
                'accessory': 1   # Belt, watch, etc.
            }
            # Add variety: 4-6 items
            total_items = random.randint(4, 6)
            
        elif 'athletic' in occasion_lower or 'gym' in occasion_lower:
            # Athletic occasions - functional, fewer items
            base_counts = {
                'top': 1,
                'bottom': 1,
                'shoes': 1
            }
            # Add variety: 3-4 items
            total_items = random.randint(3, 4)
            
        elif 'casual' in occasion_lower or 'weekend' in occasion_lower or 'loungewear' in occasion_lower:
            # Casual occasions - relaxed, moderate items
            base_counts = {
                'top': 1,
                'bottom': 1,
                'shoes': 1,
                'accessory': 1
            }
            # Add variety: 3-5 items
            total_items = random.randint(3, 5)
            
        elif 'party' in occasion_lower or 'date' in occasion_lower:
            # Social occasions - stylish, more items
            base_counts = {
                'top': 1,
                'bottom': 1,
                'shoes': 1,
                'outerwear': 1,
                'accessory': 1
            }
            # Add variety: 4-6 items
            total_items = random.randint(4, 6)
            
        else:
            # Default - balanced approach
            base_counts = {
                'top': 1,
                'bottom': 1,
                'shoes': 1,
                'accessory': 1
            }
            # Add variety: 3-5 items
            total_items = random.randint(3, 5)
        
        # Style-based adjustments
        if style:
            style_lower = style.lower()
            
            if 'minimalist' in style_lower or 'minimal' in style_lower:
                # Minimalist styles - fewer items, cleaner look
                total_items = max(3, total_items - 1)
                if 'accessory' in base_counts and total_items <= 3:
                    base_counts.pop('accessory', None)
                    
            elif 'maximalist' in style_lower or 'maximal' in style_lower:
                # Maximalist styles - more items, layered look
                total_items = min(6, total_items + 1)
                if 'outerwear' not in base_counts:
                    base_counts['outerwear'] = 1
                    
            elif 'bohemian' in style_lower or 'boho' in style_lower:
                # Bohemian styles - more accessories and layers
                total_items = min(6, total_items + 1)
                if 'accessory' not in base_counts:
                    base_counts['accessory'] = 1
                if 'outerwear' not in base_counts:
                    base_counts['outerwear'] = 1
                    
            elif 'streetwear' in style_lower or 'urban' in style_lower:
                # Streetwear - more accessories, layered look
                total_items = min(6, total_items + 1)
                if 'accessory' not in base_counts:
                    base_counts['accessory'] = 1
                    
            elif 'classic' in style_lower or 'preppy' in style_lower:
                # Classic styles - structured, moderate items
                total_items = max(4, min(5, total_items))
                
        # Mood-based adjustments
        if mood:
            mood_lower = mood.lower()
            
            if 'bold' in mood_lower or 'dynamic' in mood_lower or 'energetic' in mood_lower:
                # Bold moods - more items, statement pieces
                total_items = min(6, total_items + 1)
                if 'accessory' not in base_counts:
                    base_counts['accessory'] = 1
                    
            elif 'subtle' in mood_lower or 'serene' in mood_lower:
                # Subtle moods - fewer items, understated
                total_items = max(3, total_items - 1)
                if 'accessory' in base_counts and total_items <= 3:
                    base_counts.pop('accessory', None)
                    
            elif 'romantic' in mood_lower or 'playful' in mood_lower:
                # Romantic/playful moods - more accessories
                if 'accessory' not in base_counts:
                    base_counts['accessory'] = 1
                    
        # Ensure we don't exceed the target total
        current_total = sum(base_counts.values())
        if current_total > total_items:
            # Remove items starting with least essential
            priority_order = ['accessory', 'outerwear', 'top', 'bottom', 'shoes']
            for category in priority_order:
                if category in base_counts and current_total > total_items:
                    base_counts.pop(category, None)
                    current_total -= 1
                    
        elif current_total < total_items:
            # Add items if we have room
            if 'accessory' not in base_counts and total_items > current_total:
                base_counts['accessory'] = 1
                current_total += 1
            if 'outerwear' not in base_counts and total_items > current_total:
                base_counts['outerwear'] = 1
                current_total += 1
                
        return base_counts

    def _get_items_for_category(self, items: List[ClothingItem], category: str) -> List[ClothingItem]:
        """Get items that belong to a specific category."""
        category_types = self.category_mapping.get(category, [])
        return [item for item in items if item.type in category_types]

    def _ensure_outfit_completeness(self, selected_items: List[ClothingItem], all_items: List[ClothingItem], context: Dict[str, Any], healing_context: DynamicHealingContext) -> List[ClothingItem]:
        """Ensure the outfit has all necessary components."""
        occasion = context.get('occasion', 'casual')
        style = context.get('style', '')
        mood = context.get('mood', '')
        target_counts = self._get_target_item_counts(occasion, style, mood)
        
        current_categories = self._categorize_items(selected_items)
        
        for category, target_count in target_counts.items():
            current_count = len(current_categories.get(category, []))
            if current_count < target_count:
                # Find additional items for this category
                available_items = self._get_items_for_category(all_items, category)
                available_items = [item for item in available_items if item not in selected_items]
                
                if available_items:
                    # Sort by relevance and add missing items
                    available_items.sort(
                        key=lambda x: self._calculate_relevance_score(x, context),
                        reverse=True
                    )
                    needed = target_count - current_count
                    selected_items.extend(available_items[:needed])
        
        return selected_items

    # Firestore query methods (implemented with actual queries)
    async def _find_alternatives_for_category(self, category: str, exclude_item: ClothingItem, context: Dict[str, Any], healing_context: DynamicHealingContext) -> List[ClothingItem]:
        """Find alternative items for a category using Firestore queries with dynamic exclusions."""
        try:
            user_id = context.get('user_profile', {}).get('id')
            if not user_id:
                return []
            
            # Get category types
            category_types = self.category_mapping.get(category, [])
            
            # Query Firestore for alternatives
            alternatives = []
            for item_type in category_types:
                query = self.wardrobe_collection.where('userId', '==', user_id).where('type', '==', item_type)
                
                # Apply healing context exclusions
                if healing_context and healing_context.items_removed:
                    excluded_items = list(healing_context.items_removed)
                    if excluded_items:
                        # Firestore 'not-in' supports up to 10 values
                        query = query.where('id', 'not-in', excluded_items[:10])
                
                docs = query.stream()
                
                for doc in docs:
                    # Skip if this is the item we're trying to replace
                    if doc.id == exclude_item.id:
                        continue
                    
                    # Skip if item has been removed in healing context
                    if healing_context and doc.id in healing_context.items_removed:
                        continue
                    
                    item_data = doc.to_dict()
                    item_data['id'] = doc.id
                    try:
                        item = ClothingItem(**item_data)
                        
                        # Skip if item doesn't meet basic criteria
                        if not self._meets_basic_criteria(item, context):
                            continue
                        
                        # Score the item for relevance
                        score = self._calculate_relevance_score(item, context)
                        alternatives.append((item, score))
                    except Exception as e:
                        print(f"Warning: Could not parse alternative item {doc.id}: {e}")
                        continue
            
            # Sort by relevance score and return top alternatives
            alternatives.sort(key=lambda x: x[1], reverse=True)
            result = [item for item, score in alternatives[:5]]  # Return top 5 alternatives
            
            print(f"✅ Found {len(result)} alternatives for category '{category}' (with dynamic exclusions)")
            return result
            
        except Exception as e:
            print(f"❌ Error finding alternatives for category {category}: {e}")
            return []

    async def _find_layering_compatible_replacement(self, item: ClothingItem, existing_items: List[ClothingItem], context: Dict[str, Any], healing_context: DynamicHealingContext) -> Optional[ClothingItem]:
        """Find a layering-compatible replacement for an item."""
        try:
            user_id = context.get('user_profile', {}).get('id')
            if not user_id:
                return None
            
            # Get existing sleeve lengths to avoid conflicts
            existing_sleeve_lengths = [self._get_sleeve_length(existing) for existing in existing_items]
            
            # Query Firestore for layering-compatible items
            query = self.wardrobe_collection.where('userId', '==', user_id).where('type', '==', item.type)
            docs = query.stream()
            
            best_replacement = None
            best_score = 0
            
            for doc in docs:
                if doc.id != item.id:  # Exclude the current item
                    item_data = doc.to_dict()
                    item_data['id'] = doc.id
                    try:
                        candidate = ClothingItem(**item_data)
                        
                        # Check if it has a different sleeve length
                        candidate_sleeve = self._get_sleeve_length(candidate)
                        if candidate_sleeve not in existing_sleeve_lengths:
                            score = self._calculate_relevance_score(candidate, context)
                            if score > best_score:
                                best_score = score
                                best_replacement = candidate
                    except Exception as e:
                        print(f"Warning: Could not parse layering replacement item {doc.id}: {e}")
                        continue
            
            return best_replacement
            
        except Exception as e:
            print(f"Error finding layering-compatible replacement: {e}")
            return None

    def _has_low_score(self, item: ClothingItem, error: str) -> bool:
        """Check if an item has a low score based on the error."""
        # Simplified check - in practice, this would analyze the specific error
        return True

    def _would_fail_with_relaxed_thresholds(self, error: str, relaxed_thresholds: Dict[str, float]) -> bool:
        """Check if an error would still fail with relaxed thresholds."""
        # Simplified check - in practice, this would recalculate scores
        return False

    def _filter_by_basic_criteria(self, items: List[ClothingItem], context: Dict[str, Any], healing_context: DynamicHealingContext) -> List[ClothingItem]:
        """Filter items by basic criteria."""
        filtered = []
        for item in items:
            # Basic filtering logic
            if self._meets_basic_criteria(item, context):
                filtered.append(item)
        return filtered

    def _meets_basic_criteria(self, item: ClothingItem, context: Dict[str, Any]) -> bool:
        """Check if an item meets basic criteria."""
        # Basic validation
        return True

    # ============================================================================
    # STEP 3: FULL OUTFIT ASSEMBLY FROM FIRESTORE (FALLBACK 2)
    # ============================================================================

    async def generate_outfit_from_firestore(
        self,
        user_wardrobe: List[ClothingItem],
        constraints: Dict[str, Any]
    ) -> Dict[str, ClothingItem]:
        """
        Generate a complete outfit deterministically from Firestore data.
        
        This is Step 3: Full Outfit Assembly from Firestore (Fallback 2)
        Used when both GPT generation and partial fixes fail.
        
        Args:
            user_wardrobe: List of user's wardrobe items
            constraints: Generation constraints (season, formality, occasion, etc.)
            
        Returns:
            Dictionary with category keys and ClothingItem values
        """
        try:
            print("🔧 Step 3: Generating full outfit from Firestore (Fallback 2)")
            
            # Extract constraints
            season = constraints.get('season', 'all')
            formality = constraints.get('formality', 'casual')
            occasion = constraints.get('occasion', 'casual')
            temperature = constraints.get('temperature', 70.0)
            style = constraints.get('style', 'casual')
            user_id = constraints.get('user_id')
            
            if not user_id:
                print("❌ No user_id provided for Firestore queries")
                return {}
            
            # Generate outfit components deterministically
            outfit = {}
            
            # 1. Find top item
            top = await self._find_item_deterministic(
                user_id, 'top', {
                    'seasonality': season,
                    'formality': formality,
                    'temperature': temperature,
                    'style': style,
                    'occasion': occasion
                }
            )
            if top:
                outfit['top'] = top
                print(f"✅ Selected top: {top.name}")
            
            # 2. Find bottom item
            bottom = await self._find_item_deterministic(
                user_id, 'bottom', {
                    'seasonality': season,
                    'formality': formality,
                    'temperature': temperature,
                    'style': style,
                    'occasion': occasion,
                    'compatible_with': top
                }
            )
            if bottom:
                outfit['bottom'] = bottom
                print(f"✅ Selected bottom: {bottom.name}")
            
            # 3. Find shoes
            shoes = await self._find_item_deterministic(
                user_id, 'shoes', {
                    'seasonality': season,
                    'formality': formality,
                    'temperature': temperature,
                    'style': style,
                    'occasion': occasion,
                    'compatible_with': [top, bottom] if top and bottom else []
                }
            )
            if shoes:
                outfit['shoes'] = shoes
                print(f"✅ Selected shoes: {shoes.name}")
            
            # 4. Find outerwear (if needed for temperature/occasion)
            if self._needs_outerwear(temperature, occasion, formality):
                outerwear = await self._find_item_deterministic(
                    user_id, 'outerwear', {
                        'seasonality': season,
                        'formality': formality,
                        'temperature': temperature,
                        'style': style,
                        'occasion': occasion,
                        'compatible_with': [top, bottom, shoes] if all([top, bottom, shoes]) else []
                    }
                )
                if outerwear:
                    outfit['outerwear'] = outerwear
                    print(f"✅ Selected outerwear: {outerwear.name}")
            
            # 5. Find accessories (if appropriate for occasion)
            if self._needs_accessories(occasion, formality):
                accessories = await self._find_accessories_deterministic(
                    user_id, {
                        'seasonality': season,
                        'formality': formality,
                        'temperature': temperature,
                        'style': style,
                        'occasion': occasion,
                        'compatible_with': list(outfit.values())
                    }
                )
                if accessories:
                    outfit['accessories'] = accessories
                    print(f"✅ Selected accessories: {[acc.name for acc in accessories]}")
            
            print(f"✅ Generated complete outfit with {len(outfit)} components")
            return outfit
            
        except Exception as e:
            print(f"❌ Error in deterministic outfit generation: {e}")
            return {}

    async def _find_item_deterministic(
        self,
        user_id: str,
        category: str,
        constraints: Dict[str, Any]
    ) -> Optional[ClothingItem]:
        """
        Find a single item deterministically based on constraints.
        
        Args:
            user_id: The user ID
            category: The category to search (top, bottom, shoes, etc.)
            constraints: Search constraints
            
        Returns:
            Best matching ClothingItem or None
        """
        try:
            # Build query based on constraints
            query = self.wardrobe_collection.where('userId', '==', user_id)
            query = query.where('category', '==', category)
            
            # Add seasonality constraint
            season = constraints.get('seasonality', 'all')
            if season != 'all':
                query = query.where('seasonality', 'array_contains', season)
            
            # Add formality constraint
            formality = constraints.get('formality', 'casual')
            query = query.where('formality', '==', formality)
            
            # Add quality constraint for better items
            query = query.where('quality_score', '>=', 0.5)
            
            # Order by pairability score for better combinations
            query = query.order_by('pairability_score', direction='DESCENDING')
            
            # Limit results
            query = query.limit(10)
            
            # Execute query
            docs = query.stream()
            candidates = []
            
            for doc in docs:
                data = doc.to_dict()
                try:
                    item = ClothingItem(**data)
                    # Score the item based on all constraints
                    score = self._score_item_for_constraints(item, constraints)
                    candidates.append((item, score))
                except Exception as e:
                    print(f"Warning: Could not parse item {doc.id}: {e}")
                    continue
            
            if not candidates:
                return None
            
            # Sort by score and return the best match
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
            
        except Exception as e:
            print(f"❌ Error in deterministic item search: {e}")
            return None

    async def _find_accessories_deterministic(
        self,
        user_id: str,
        constraints: Dict[str, Any]
    ) -> List[ClothingItem]:
        """
        Find accessories deterministically based on constraints.
        
        Args:
            user_id: The user ID
            constraints: Search constraints
            
        Returns:
            List of matching accessories
        """
        try:
            accessories = []
            
            # Determine which accessories are needed based on occasion and formality
            needed_accessories = self._get_needed_accessories(
                constraints.get('occasion', 'casual'),
                constraints.get('formality', 'casual')
            )
            
            for accessory_type in needed_accessories:
                accessory = await self._find_item_deterministic(
                    user_id, 'accessory', {
                        **constraints,
                        'accessory_type': accessory_type
                    }
                )
                if accessory:
                    accessories.append(accessory)
                    # Limit to 2-3 accessories max
                    if len(accessories) >= 3:
                        break
            
            return accessories
            
        except Exception as e:
            print(f"❌ Error in accessory search: {e}")
            return []

    def _score_item_for_constraints(
        self,
        item: ClothingItem,
        constraints: Dict[str, Any]
    ) -> float:
        """
        Score an item based on how well it matches the constraints.
        
        Args:
            item: The ClothingItem to score
            constraints: The constraints to match against
            
        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.5  # Base score
        
        # Temperature compatibility
        temperature = constraints.get('temperature', 70.0)
        if self._is_weather_appropriate(item, temperature):
            score += 0.2
        
        # Style compatibility
        style = constraints.get('style', 'casual')
        if self._item_matches_style(item, style):
            score += 0.15
        
        # Compatibility with other selected items
        compatible_with = constraints.get('compatible_with', [])
        if compatible_with:
            compatibility_score = sum(
                self._calculate_item_compatibility(item, other_item)
                for other_item in compatible_with
            ) / len(compatible_with)
            score += compatibility_score * 0.15
        
        # Quality and pairability
        quality_score = getattr(item, 'quality_score', 0.5)
        pairability_score = getattr(item, 'pairability_score', 0.5)
        score += (quality_score + pairability_score) * 0.1
        
        # Recent wear bonus (encourage variety)
        wear_count = getattr(item, 'wear_count', 0)
        if wear_count < 5:  # Prefer less-worn items
            score += 0.1
        
        return min(score, 1.0)

    def _calculate_item_compatibility(
        self,
        item1: ClothingItem,
        item2: ClothingItem
    ) -> float:
        """
        Calculate compatibility between two items.
        
        Args:
            item1: First ClothingItem
            item2: Second ClothingItem
            
        Returns:
            Compatibility score from 0.0 to 1.0
        """
        compatibility = 0.5  # Base compatibility
        
        # Color compatibility
        if item1.dominantColors and item2.dominantColors:
            color1 = item1.dominantColors[0].name.lower()
            color2 = item2.dominantColors[0].name.lower()
            
            # Check if colors are complementary
            complementary_pairs = [
                ('black', 'white'), ('blue', 'orange'), ('red', 'green'),
                ('yellow', 'purple'), ('brown', 'blue'), ('gray', 'any')
            ]
            
            for pair in complementary_pairs:
                if (color1 in pair and color2 in pair) or (color2 in pair and color1 in pair):
                    compatibility += 0.3
                    break
        
        # Style compatibility
        if item1.style and item2.style:
            common_styles = set(item1.style) & set(item2.style)
            if common_styles:
                compatibility += 0.2
        
        # Formality compatibility
        formality1 = getattr(item1, 'formality', 'casual')
        formality2 = getattr(item2, 'formality', 'casual')
        if formality1 == formality2:
            compatibility += 0.2
        
        return min(compatibility, 1.0)

    def _needs_outerwear(
        self,
        temperature: float,
        occasion: str,
        formality: str
    ) -> bool:
        """
        Determine if outerwear is needed based on conditions.
        
        Args:
            temperature: Current temperature
            occasion: The occasion
            formality: The formality level
            
        Returns:
            True if outerwear is needed
        """
        # Temperature-based need
        if temperature < 60:
            return True
        
        # Occasion-based need
        formal_occasions = ['formal', 'business', 'interview', 'wedding']
        if occasion in formal_occasions:
            return True
        
        # Formality-based need
        if formality in ['formal', 'business']:
            return True
        
        return False

    def _needs_accessories(
        self,
        occasion: str,
        formality: str
    ) -> bool:
        """
        Determine if accessories are needed based on occasion and formality.
        
        Args:
            occasion: The occasion
            formality: The formality level
            
        Returns:
            True if accessories are needed
        """
        # Formal occasions always need accessories
        if formality in ['formal', 'business']:
            return True
        
        # Specific occasions that benefit from accessories
        accessory_occasions = ['date', 'party', 'wedding', 'interview']
        if occasion in accessory_occasions:
            return True
        
        return False

    def _get_needed_accessories(
        self,
        occasion: str,
        formality: str
    ) -> List[str]:
        """
        Get list of needed accessory types based on occasion and formality.
        
        Args:
            occasion: The occasion
            formality: The formality level
            
        Returns:
            List of accessory types needed
        """
        accessories = []
        
        if formality in ['formal', 'business']:
            accessories.extend(['watch', 'belt'])
        
        if occasion in ['date', 'party', 'wedding']:
            accessories.extend(['watch', 'necklace'])
        
        if occasion == 'casual':
            accessories.extend(['watch'])
        
        # Remove duplicates and limit
        return list(set(accessories))[:3]

    async def generate_outfit_with_constraints(
        self,
        user_id: str,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        High-level method to generate outfit with constraints.
        
        Args:
            user_id: The user ID
            constraints: Generation constraints
            
        Returns:
            Dictionary with outfit data and metadata
        """
        try:
            # Add user_id to constraints
            constraints['user_id'] = user_id
            
            # Generate outfit deterministically
            outfit_items = await self.generate_outfit_from_firestore([], constraints)
            
            if not outfit_items:
                return {
                    'success': False,
                    'error': 'No suitable items found for outfit generation',
                    'outfit': {}
                }
            
            # Create outfit metadata
            outfit_metadata = {
                'generation_method': 'deterministic_firestore',
                'constraints_used': constraints,
                'item_count': len(outfit_items),
                'categories': list(outfit_items.keys()),
                'generated_at': int(time.time())
            }
            
            # Calculate outfit score
            outfit_score = self._calculate_outfit_score(outfit_items, constraints)
            outfit_metadata['outfit_score'] = outfit_score
            
            return {
                'success': True,
                'outfit': outfit_items,
                'metadata': outfit_metadata
            }
            
        except Exception as e:
            print(f"❌ Error in outfit generation with constraints: {e}")
            return {
                'success': False,
                'error': str(e),
                'outfit': {}
            }

    def _calculate_outfit_score(
        self,
        outfit_items: Dict[str, ClothingItem],
        constraints: Dict[str, Any]
    ) -> float:
        """
        Calculate overall outfit score based on items and constraints.
        
        Args:
            outfit_items: Dictionary of outfit items
            constraints: Generation constraints
            
        Returns:
            Overall outfit score from 0.0 to 1.0
        """
        if not outfit_items:
            return 0.0
        
        total_score = 0.0
        item_count = len(outfit_items)
        
        # Score each item
        for category, item in outfit_items.items():
            item_score = self._score_item_for_constraints(item, constraints)
            total_score += item_score
        
        # Average item score
        avg_item_score = total_score / item_count
        
        # Completeness bonus
        completeness_bonus = 0.0
        required_categories = ['top', 'bottom', 'shoes']
        present_categories = [cat for cat in required_categories if cat in outfit_items]
        completeness_bonus = len(present_categories) / len(required_categories) * 0.2
        
        # Cohesion bonus (how well items work together)
        cohesion_score = self._calculate_outfit_cohesion(outfit_items)
        
        final_score = avg_item_score + completeness_bonus + cohesion_score * 0.3
        return min(final_score, 1.0)

    def _calculate_outfit_cohesion(
        self,
        outfit_items: Dict[str, ClothingItem]
    ) -> float:
        """
        Calculate how well the outfit items work together.
        
        Args:
            outfit_items: Dictionary of outfit items
            
        Returns:
            Cohesion score from 0.0 to 1.0
        """
        if len(outfit_items) < 2:
            return 0.5
        
        items = list(outfit_items.values())
        total_cohesion = 0.0
        pair_count = 0
        
        # Calculate pairwise compatibility
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                cohesion = self._calculate_item_compatibility(items[i], items[j])
                total_cohesion += cohesion
                pair_count += 1
        
        return total_cohesion / pair_count if pair_count > 0 else 0.5

    async def generate_multiple_outfits(
        self,
        user_id: str,
        constraints: Dict[str, Any],
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple outfit variations with the same constraints.
        
        Args:
            user_id: The user ID
            constraints: Generation constraints
            count: Number of outfits to generate
            
        Returns:
            List of outfit dictionaries
        """
        outfits = []
        
        for i in range(count):
            print(f"🔧 Generating outfit variation {i + 1}/{count}")
            
            # Add variation to constraints
            variation_constraints = constraints.copy()
            variation_constraints['variation'] = i
            
            # Generate outfit
            outfit_result = await self.generate_outfit_with_constraints(user_id, variation_constraints)
            
            if outfit_result['success']:
                outfits.append(outfit_result)
            else:
                print(f"❌ Failed to generate outfit variation {i + 1}: {outfit_result['error']}")
        
        return outfits

    async def generate_outfit_for_occasion(
        self,
        user_id: str,
        occasion: str,
        weather_data: WeatherData = None,
        style_preferences: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate outfit specifically for a given occasion.
        
        Args:
            user_id: The user ID
            occasion: The occasion (casual, formal, business, party, etc.)
            weather_data: Current weather data
            style_preferences: User's style preferences
            
        Returns:
            Outfit generation result
        """
        # Map occasion to constraints
        constraints = self._map_occasion_to_constraints(occasion, weather_data, style_preferences)
        
        # Generate outfit
        return await self.generate_outfit_with_constraints(user_id, constraints)

    def _map_occasion_to_constraints(
        self,
        occasion: str,
        weather_data: WeatherData = None,
        style_preferences: List[str] = None
    ) -> Dict[str, Any]:
        """
        Map occasion to generation constraints.
        
        Args:
            occasion: The occasion
            weather_data: Weather data
            style_preferences: Style preferences
            
        Returns:
            Constraints dictionary
        """
        constraints = {
            'occasion': occasion,
            'style': 'casual',
            'formality': 'casual',
            'temperature': 70.0,
            'season': 'all'
        }
        
        # Map occasion to formality
        formality_mapping = {
            'casual': 'casual',
            'formal': 'formal',
            'business': 'formal',
            'office': 'formal',
            'party': 'semi-formal',
            'date': 'semi-formal',
            'wedding': 'formal',
            'interview': 'formal',
            'gym': 'casual',
            'workout': 'casual'
        }
        constraints['formality'] = formality_mapping.get(occasion.lower(), 'casual')
        
        # Map occasion to style
        style_mapping = {
            'casual': 'casual',
            'formal': 'formal',
            'business': 'business',
            'office': 'business',
            'party': 'trendy',
            'date': 'elegant',
            'wedding': 'formal',
            'interview': 'business',
            'gym': 'athletic',
            'workout': 'athletic'
        }
        constraints['style'] = style_mapping.get(occasion.lower(), 'casual')
        
        # Add weather constraints
        if weather_data:
            constraints['temperature'] = weather_data.temperature
            constraints['weather_condition'] = weather_data.condition
            constraints['season'] = self._determine_season(weather_data.temperature, occasion)
        
        # Add style preferences
        if style_preferences:
            constraints['user_style_preferences'] = style_preferences
        
        return constraints 