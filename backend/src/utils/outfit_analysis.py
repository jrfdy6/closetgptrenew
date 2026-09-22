"""Factual styling notes from the final owned garments and requested context."""
from typing import Any, Dict, List, Optional

from .recommendation_fidelity import pattern_kind, visual_attributes


async def generate_outfit_analysis(items: List[Dict], req: Any, outfit_score: Dict,
                                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # Scores/strategy names are diagnostic information, not evidence of quality.
    analysis = {'textureAnalysis': None, 'patternBalance': None,
                'colorStrategy': None, 'styleSynergy': None}
    textures, colors, plain, graphics = [], [], [], []
    for item in items:
        attrs = visual_attributes(item)
        texture = attrs.get('textureStyle')
        if isinstance(texture, str) and texture.strip():
            textures.append(texture.strip())
        color = item.get('color')
        if isinstance(color, str) and color.strip() and color.lower() not in {'unknown', 'other'}:
            colors.append(color.strip().lower())
        name = item.get('name') or 'This piece'
        if pattern_kind(item) == 'plain':
            plain.append(name)
        elif pattern_kind(item) == 'graphic':
            graphics.append(name)

    colors = list(dict.fromkeys(colors))
    textures = list(dict.fromkeys(textures))
    if len(colors) > 1:
        analysis['colorStrategy'] = {'insight': f"The palette combines {', '.join(colors[:-1])} and {colors[-1]}."}
    elif colors:
        analysis['colorStrategy'] = {'insight': f"The recorded colors share a {colors[0]} base."}
    if len(textures) > 1:
        analysis['textureAnalysis'] = {'insight': f"{textures[0].capitalize()} and {textures[1]} textures add contrast."}
    if plain and graphics:
        analysis['patternBalance'] = {'insight': f"{plain[0]} keeps the background simple alongside the graphic detail on {graphics[0]}."}

    style = str(getattr(req, 'style', '') or '')
    if style.lower() == 'minimalist':
        if graphics:
            required = getattr(req, 'baseItemId', None)
            graphic_ids = {item.get('id') for item in items if pattern_kind(item) == 'graphic'}
            reason = ' Your required piece is included.' if required in graphic_ids else ''
            analysis['styleSynergy'] = {
                'insight': f"{graphics[0]} has graphic detail, so this is a partial match for Minimalist.{reason} A plain alternative would make the look more restrained.",
                'requestedStyle': style, 'compromise': 'graphic_detail',
            }
        elif plain:
            analysis['styleSynergy'] = {'insight': 'The plain pieces support the restrained detail requested for Minimalist.', 'requestedStyle': style}
    elif style:
        analysis['styleSynergy'] = {'insight': f"Requested direction: {style} for {getattr(req, 'occasion', 'this occasion')}."}
    return analysis
