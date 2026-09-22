"""Bounded style preferences and factual context shared by existing generators."""
import re
from typing import Any

from .outfit_admission import classify_garment
from .garment_metadata import normalize_garment_metadata


def read(item: Any, key: str, default=None):
    return item.get(key, default) if isinstance(item, dict) else getattr(item, key, default)


def visual_attributes(item: Any) -> dict:
    record = item if isinstance(item, dict) else item.model_dump() if hasattr(item, 'model_dump') else vars(item)
    return normalize_garment_metadata(record).get('metadata', {}).get('visualAttributes', {})



def pattern_kind(item: Any) -> str:
    attrs = visual_attributes(item)
    pattern = str(attrs.get('pattern') or '').strip().lower()
    # An explicit saved correction takes precedence over the original photo/name.
    if pattern in {'solid', 'plain', 'unpatterned', 'none'}:
        return 'plain'
    description = pattern or str(read(item, 'name', '')).lower()
    if re.search(r'\b(graphic|graphics|logo|logos|slogan|printed|print)\b', description):
        return 'graphic'
    return 'unknown'


def prefer_plain_candidates(candidates, style, *, category=classify_garment, eligible=None):
    """Promote plain alternatives without dropping fallbacks or trading practicality.

    Runs after diversity/strategy ordering. Only same-category candidates with no
    worse weather/compatibility scores can move ahead of a graphic. Unknown
    attributes never become an invented plain garment.
    """
    result = list(candidates)
    if str(style).strip().lower() != 'minimalist':
        return result
    for index in range(len(result)):
        _, current = result[index]
        item = current['item']
        if pattern_kind(item) != 'graphic':
            continue
        for later in range(index + 1, len(result)):
            _, alternative = result[later]
            plain = alternative['item']
            if pattern_kind(plain) != 'plain' or category(plain) != category(item):
                continue
            if eligible and not eligible(plain):
                continue
            if alternative.get('composite_score', 0) <= -1:
                continue
            if any(alternative.get(key, 0) < current.get(key, 0)
                   for key in ('weather_score', 'compatibility_score')):
                continue
            result.insert(index, result.pop(later))
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
