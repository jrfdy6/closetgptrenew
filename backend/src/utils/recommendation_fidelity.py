"""Bounded style preferences and factual context shared by existing generators."""
import math
import re
from typing import Any

from .outfit_admission import classify_garment
from .garment_metadata import normalize_garment_metadata


def read(item: Any, key: str, default=None):
    return item.get(key, default) if isinstance(item, dict) else getattr(item, key, default)


def visual_attributes(item: Any) -> dict:
    record = item if isinstance(item, dict) else item.model_dump() if hasattr(item, 'model_dump') else vars(item)
    return normalize_garment_metadata(record).get('metadata', {}).get('visualAttributes', {})



def _pattern_kind(attrs, name):
    saved_pattern = attrs.get('pattern')
    if saved_pattern is not None and saved_pattern != '' and not isinstance(saved_pattern, str):
        # Populated unknown/invalid corrections (including False and zero) are
        # not permission to resurrect an older graphic name or prediction.
        return 'unknown'
    pattern = str(saved_pattern or '').strip().lower()
    # An explicit saved correction takes precedence over the original photo/name.
    if pattern in {'solid', 'plain', 'unpatterned', 'none'}:
        return 'plain'
    description = pattern or str(name).lower()
    if re.search(r'\b(graphic|graphics|logo|logos|slogan|printed|print)\b', description):
        return 'graphic'
    return 'unknown'


def pattern_kind(item: Any) -> str:
    return _pattern_kind(visual_attributes(item), read(item, 'name', ''))


_NEUTRAL_COLORS = frozenset({
    'black', 'white', 'off white', 'off-white', 'ivory', 'cream', 'beige', 'tan',
    'taupe', 'brown', 'camel', 'khaki', 'gray', 'grey', 'light gray', 'light grey',
    'dark gray', 'dark grey', 'charcoal', 'navy', 'navy blue', 'dark navy',
})
_ACCENT_COLORS = frozenset({
    'red', 'burgundy', 'maroon', 'pink', 'hot pink', 'rose', 'purple', 'violet',
    'lavender', 'lilac', 'orange', 'coral', 'yellow', 'gold', 'green', 'olive',
    'olive green', 'forest green', 'sage', 'mint', 'teal', 'turquoise', 'cyan',
    'blue', 'light blue', 'dark blue', 'royal blue', 'cobalt', 'sky blue',
})


def _palette(value):
    if not isinstance(value, str) or not value.strip():
        return 'unknown'
    colors = [part.strip() for part in re.split(r'\s+and\s+|[,/&]', value.strip().lower())]
    if not colors or any(color not in _NEUTRAL_COLORS | _ACCENT_COLORS for color in colors):
        return 'unknown'
    return 'accent' if any(color in _ACCENT_COLORS for color in colors) else 'neutral'


def _mood_cue(value):
    values = value if isinstance(value, (list, tuple)) else [value]
    labels = {v.strip().lower() for v in values if isinstance(v, str)}
    subtle = bool(labels & {'subtle', 'understated', 'restrained'})
    statement = bool(labels & {'statement', 'bold', 'dramatic', 'expressive'})
    return 'statement' if statement else 'subtle' if subtle else 'unknown'


def minimalist_subtle_cues(item: Any) -> dict:
    """Saved evidence only; an accent is non-neutral, not necessarily bright.

    Palette evidence requires a saved root color, matching admission's treatment
    of missing color as unknown. Explicit mood corrections outrank older analysis.
    Plain and neutral require positive evidence; names/brands never establish
    palette or mood. This same contract is used by factual notes.
    """
    record = item if isinstance(item, dict) else item.model_dump() if hasattr(item, 'model_dump') else vars(item)
    normalized = normalize_garment_metadata(record)
    metadata = normalized.get('metadata') or {}
    attrs = metadata.get('visualAttributes') or {}
    color = record.get('color')
    mood = next((record[key] for key in ('mood', 'moodTags')
                 if record.get(key) not in (None, '', [], {})), None)
    if mood is None:
        mood = metadata.get('moodTags')
    tag_cue, statement_cue = _mood_cue(mood), 'unknown'
    statement = attrs.get('statementLevel')
    if type(statement) in (int, float) and math.isfinite(statement) and 0 <= statement <= 10:
        # Zero is synthesized by older analysis paths; it is not affirmative
        # evidence. Higher saved levels can still identify statement detail.
        statement_cue = 'statement' if statement >= 6 else 'subtle' if 0 < statement <= 2 else 'unknown'
    elif isinstance(statement, str):
        statement = statement.strip().lower()
        statement_cue = ('subtle' if statement in {'low', 'minimal', 'subtle', 'understated'} else
                         'statement' if statement in {'high', 'bold', 'statement', 'dramatic'} else 'unknown')
    cue = ('statement' if 'statement' in (tag_cue, statement_cue) else
           'subtle' if 'subtle' in (tag_cue, statement_cue) else 'unknown')
    pattern, palette = _pattern_kind(attrs, read(item, 'name', '')), _palette(color)
    return {'pattern': pattern, 'palette': palette, 'mood': cue,
            'supported': pattern == 'plain' and palette == 'neutral' and cue != 'statement'}


def _preferred_cues(alternative, current, *, subtle):
    if alternative['pattern'] == 'plain' and current['pattern'] == 'graphic':
        return True
    if subtle:
        return alternative['supported'] and not current['supported']
    return False


def prefer_plain_candidates(candidates, style, *, mood=None, category=classify_garment, eligible=None):
    """Promote plain alternatives without dropping fallbacks or trading practicality.

    Runs after diversity/strategy ordering. Minimalist+Subtle also favors known
    plain neutral pieces over less-supported visual cues. Only same-category
    alternatives with no worse practical scores move; every fallback remains.
    """
    result = list(candidates)
    if str(style).strip().lower() != 'minimalist':
        return result
    subtle = str(mood).strip().lower() == 'subtle'
    # Normalize each garment once per ordering pass, not for every comparison.
    features = {}
    for _, scores in result:
        item = scores['item']
        if id(item) not in features:
            features[id(item)] = {
                **(minimalist_subtle_cues(item) if subtle else {'pattern': pattern_kind(item)}),
                'category': category(item),
            }
    for index in range(len(result)):
        for later in range(index + 1, len(result)):
            _, current = result[index]
            item = current['item']
            _, alternative = result[later]
            plain = alternative['item']
            preferred, existing = features[id(plain)], features[id(item)]
            if (preferred['category'] != existing['category'] or not _preferred_cues(
                    preferred, existing, subtle=subtle)):
                continue
            if eligible and not eligible(plain):
                continue
            if alternative.get('composite_score', 0) <= -1:
                continue
            if any(alternative.get(key, 0) < current.get(key, 0)
                   for key in ('weather_score', 'compatibility_score', 'occasion_score')):
                continue
            result.insert(index, result.pop(later))
            if not subtle:
                break
    return result


def generation_weather(weather):
    """Persist the same context used for scoring, including fallback provenance."""
    context = dict(weather) if isinstance(weather, dict) else {}
    temperature = context.get('temperature')
    if not isinstance(temperature, (int, float)) or isinstance(temperature, bool):
        context.update(temperature=72, condition=context.get('condition') or 'Clear',
                       fallback=True, source='fallback')
    elif context.get('fallback') or context.get('source') in {'fallback', 'estimated'}:
        context['fallback'] = True
    return context


def fallback_weather_score(item, weather):
    """Conservative saved-attribute tie breaker for the occasion-only fallback."""
    attrs = visual_attributes(item)
    temperature = weather.get('temperature', 72)
    compatibility = attrs.get('temperatureCompatibility') or read(item, 'temperatureCompatibility', {}) or {}
    minimum, maximum = read(compatibility, 'minTemp'), read(compatibility, 'maxTemp')
    if isinstance(minimum, (int, float)) and isinstance(maximum, (int, float)):
        return 1 if minimum <= temperature <= maximum else -1
    warmth = str(attrs.get('warmthFactor') or '').lower()
    if temperature < 50:
        return 1 if warmth in {'heavy', 'insulated', 'warm'} else -1 if warmth in {'light', 'minimal'} else 0
    if temperature > 75:
        return 1 if warmth in {'light', 'minimal', 'breathable'} else -1 if warmth in {'heavy', 'insulated', 'warm'} else 0
    return 0
