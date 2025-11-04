"""
Outfit Analysis Utility
Generates detailed educational insights about outfit composition.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


async def generate_outfit_analysis(items: List[Dict], req: Any, outfit_score: Dict, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate detailed outfit analysis for educational insights.
    
    Args:
        items: List of outfit items
        req: Request object with style/occasion/mood
        outfit_score: Outfit scoring information
        metadata: Optional metadata dict containing generation_strategy or other strategy info
    """
    analysis = {
        "textureAnalysis": None,
        "patternBalance": None,
        "colorStrategy": None,
        "styleSynergy": None
    }
    
    try:
        # Extract actual generation strategy from metadata if available
        # Check for strategy in metadata (could be in metadata.get('metadata') or directly)
        actual_strategy = None
        if metadata:
            # Try nested metadata first
            nested_meta = metadata.get('metadata', {})
            if isinstance(nested_meta, dict):
                actual_strategy = nested_meta.get('generation_strategy') or nested_meta.get('strategy')
            # Try direct metadata
            if not actual_strategy:
                actual_strategy = metadata.get('generation_strategy') or metadata.get('strategy')
        # Extract metadata from items
        textures = []
        patterns = []
        colors = []
        styles_list = []
        item_details = []
        
        for item in items:
            metadata = item.get('metadata', {}) or {}
            visual_attrs = metadata.get('visualAttributes', {}) or {}
            
            # Convert item type to string (handle enums like ClothingType.SHORTS)
            raw_type = item.get('type', 'piece')
            item_type = str(raw_type).split('.')[-1].lower() if raw_type else 'piece'
            
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
                # Only say "pop of color" if the actual generation strategy was color_pop
                # Otherwise, use more generic language
                if len(bold_colors) == 1 and actual_strategy and 'color_pop' in str(actual_strategy).lower():
                    # This outfit was actually generated using the color_pop strategy (8% of outfits)
                    analysis["colorStrategy"] = {
                        "insight": f"{bold_colors[0]['color'].title()} {bold_colors[0]['type']} provides a pop of color against neutral base",
                        "popColor": bold_colors[0]['color'],
                        "popItem": bold_colors[0]['type'],
                        "neutrals": [n['type'] for n in neutrals],
                        "strategy": "color_pop"
                    }
                elif len(bold_colors) == 1:
                    # Has one bold color but wasn't generated with color_pop strategy
                    analysis["colorStrategy"] = {
                        "insight": f"{bold_colors[0]['color'].title()} {bold_colors[0]['type']} adds vibrant contrast to the neutral {', '.join([n['type'] for n in neutrals[:2]])}",
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
                if hasattr(req, 'style') and req.style.lower() in [s.lower() for s in unique_styles]:
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

