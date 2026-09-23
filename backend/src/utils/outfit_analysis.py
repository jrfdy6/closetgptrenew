"""Factual styling notes from the final owned garments and requested context."""
from typing import Any, Dict, List, Optional

from .recommendation_fidelity import pattern_kind, visual_attributes, minimalist_subtle_cues


def _minimalist_subtle_note(items, req):
    """Describe supported facts without treating partial cues as a match score."""
    evidence = [(item, minimalist_subtle_cues(item)) for item in items]
    graphics = [item for item, cues in evidence if cues['pattern'] == 'graphic']
    statements = [item for item, cues in evidence if cues['mood'] == 'statement']
    accents = [item for item, cues in evidence if cues['palette'] == 'accent']
    unknown = any(cues['pattern'] == 'unknown' or cues['palette'] == 'unknown'
                  for _, cues in evidence)
    required = getattr(req, 'baseItemId', None)
    note = {'requestedStyle': 'Minimalist', 'requestedMood': 'Subtle'}
    if graphics:
        pieces, compromise = graphics, 'graphic_detail'
        insight = (f"{graphics[0].get('name') or 'One piece'} has graphic detail, so this is a partial "
                   "match for Minimalist. A plain alternative would make the look more restrained.")
    elif statements:
        pieces, compromise = statements, 'statement_detail'
        insight = (f"{statements[0].get('name') or 'One piece'} adds a statement detail, so this is a partial "
                   "match for Subtle. A quieter alternative would be closer to that direction.")
    elif accents:
        pieces, compromise = accents, 'color_accent'
        # A named non-neutral color is an accent, not proof of brightness,
        # saturation, boldness or an incompatible garment.
        insight = (f"{accents[0].get('name') or 'One piece'} brings a color accent to this look. "
                   "A neutral alternative would make the palette more restrained.")
    elif not evidence or unknown:
        note.update(insight="There is not enough recorded color and pattern detail to assess the whole look against Minimalist and Subtle.",
                    compromise='insufficient_detail')
        return note
    else:
        note['insight'] = 'The plain pieces and neutral palette support the restrained direction you requested.'
        return note
    if required and any(item.get('id') == required for item in pieces):
        insight += ' Your required piece is included.'
    if unknown:
        insight += ' Some pieces have incomplete color or pattern details.'
    note.update(insight=insight, compromise=compromise)
    return note


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
    mood = str(getattr(req, 'mood', '') or '')
    if style.strip().lower() == 'minimalist' and mood.strip().lower() == 'subtle':
        analysis['styleSynergy'] = _minimalist_subtle_note(items, req)
    elif style.lower() == 'minimalist':
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
