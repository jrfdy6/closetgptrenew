"""Explicit profile edits; authority fields never come from request bodies."""
from fastapi import HTTPException
import math

EDITABLE = frozenset('name gender avatarUrl avatar_url bodyType height weight skinTone topSize bottomSize shoeSize chest waist inseam stylePreferences occasions preferredColors formality budget preferredBrands fitPreference sizePreference seasonalPreferences seasonality measurements preferences colorPalette stylePersonality materialPreferences fitPreferences comfortLevel stylePersona spending_ranges heightFeetInches onboardingCompleted onboarding_completed'.split())
LEGACY_INPUT = frozenset('id userId user_id email created_at createdAt updated_at updatedAt'.split())
STRINGS = frozenset('name gender avatarUrl avatar_url bodyType skinTone topSize bottomSize shoeSize formality fitPreference sizePreference heightFeetInches budget'.split())
MAPS = frozenset('measurements preferences colorPalette stylePersonality materialPreferences spending_ranges stylePersona fitPreferences comfortLevel'.split())
LISTS = frozenset('stylePreferences occasions preferredColors preferredBrands seasonalPreferences seasonality'.split())
MEASUREMENTS = frozenset('height weight chest waist inseam'.split())


def _safe_value(value, depth=0):
    if depth > 8:
        return False
    if value is None or isinstance(value, bool):
        return True
    if isinstance(value, str):
        return len(value) <= 10000
    if isinstance(value, (float, int)):
        return math.isfinite(value)
    if isinstance(value, list):
        return len(value) <= 100 and all(_safe_value(v, depth + 1) for v in value)
    if isinstance(value, dict):
        return len(value) <= 100 and all(isinstance(k, str) and len(k) <= 100 and _safe_value(v, depth + 1) for k, v in value.items())
    return False


def profile_patch(data, user, now):
    if not isinstance(data, dict):
        raise HTTPException(422, 'Profile must be an object')
    unknown = set(data) - EDITABLE - LEGACY_INPUT
    if unknown:
        raise HTTPException(422, 'Unsupported profile fields: ' + ', '.join(sorted(unknown)))
    for key in ('id', 'userId', 'user_id'):
        if key in data and data[key] != user.id:
            raise HTTPException(403, 'Profile identity does not match authenticated user')
    if data.get('email') and data['email'] != user.email:
        raise HTTPException(422, 'Email changes must use account authentication')
    patch = {}
    for key in EDITABLE & data.keys():
        value = data[key]
        if not _safe_value(value):
            raise HTTPException(422, 'Invalid profile field: ' + key)
        if value is None and key in MAPS | LISTS:
            value = {} if key in MAPS else []
        if value is not None:
            valid = ((key not in STRINGS or isinstance(value, str))
                     and (key not in MAPS or isinstance(value, dict))
                     and (key not in LISTS or (isinstance(value, list) and all(isinstance(v, str) for v in value)))
                     and (key not in MEASUREMENTS or (isinstance(value, (str, int, float)) and not isinstance(value, bool)))
                     and (key not in ('onboardingCompleted', 'onboarding_completed') or isinstance(value, bool)))
            if key in ('preferences', 'colorPalette') and isinstance(value, dict):
                valid = valid and all(isinstance(v, list) and all(isinstance(x, str) for x in v) for v in value.values())
            if key in ('stylePersonality', 'comfortLevel') and isinstance(value, dict):
                valid = valid and all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1 for v in value.values())
            if key == 'fitPreferences' and isinstance(value, dict):
                valid = valid and all(isinstance(v, str) for v in value.values())
            if not valid:
                raise HTTPException(422, 'Invalid profile field: ' + key)
        patch['seasonalPreferences' if key == 'seasonality' else key] = value
    patch['email'] = user.email
    patch['updated_at'] = now
    return patch
