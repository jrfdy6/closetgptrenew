"""Conservative, lossless interpretation of the existing questionnaire values.

These signals are optional ranking hints, not measurements of garment fit. Raw
answers stay on the profile; unknown values never become an invented user fact.
"""
from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any, Optional


def _record(value: Any) -> dict:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return vars(value) if hasattr(value, "__dict__") else {}


def _first(*values: Any) -> Any:
    return next((value for value in values if value is not None and value != ""), None)


def normalize_body_type(value: Any) -> Optional[str]:
    token = re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")
    token = {
        "round": "apple", "round_apple": "apple", "apple_round": "apple",
        "triangle": "pear", "pear_triangle": "pear", "triangle_pear": "pear",
        "straight": "rectangle", "straight_rectangle": "rectangle",
        "rectangle_straight": "rectangle",
    }.get(token, token)
    return token if token in {
        "hourglass", "pear", "apple", "rectangle", "inverted_triangle", "oval",
        "average", "athletic", "plus_size", "petite", "tall", "slim", "muscular",
    } else None


def skin_tone_signals(value: Any) -> dict:
    raw = str(value if value is not None else "").strip().lower()
    match = re.fullmatch(r"(?:skin_tone_)?(100|[1-9]?\d)", raw)
    index = int(match.group(1)) if match else None
    words = set(re.findall(r"[a-z]+", raw))
    depth = None
    if index is not None:
        depth = "light" if index <= 33 else "medium" if index <= 66 else "deep"
    elif words & {"light", "fair", "deep", "dark", "medium"}:
        depth = "light" if words & {"light", "fair"} else "deep" if words & {"deep", "dark"} else "medium"
    # The slider represents depth. It says nothing about warm/cool undertone.
    undertones = words & {"warm", "cool", "neutral"}
    undertone = next(iter(undertones)) if len(undertones) == 1 else None
    return {"skin_depth_index": index, "skin_depth": depth, "skin_undertone": undertone}


def normalize_skin_tone(value: Any) -> Optional[str]:
    signals = skin_tone_signals(value)
    return signals["skin_undertone"] or signals["skin_depth"]


def height_signals(value: Any) -> dict:
    raw = str(value or "").strip().lower().replace("’", "'").replace("′", "'").replace("″", '"')
    raw = raw.replace("–", "-").replace("—", "-")
    point = r"(?P<feet>[3-8])\s*(?:'|ft|feet)\s*(?P<inches>\d{1,2})\s*(?:\"|in|inches)?"

    def parse_point(text: str) -> Optional[float]:
        match = re.fullmatch(point, text.strip())
        if match and int(match.group("inches")) < 12:
            return float(int(match.group("feet")) * 12 + int(match.group("inches")))
        cm = re.fullmatch(r"(\d{2,3}(?:\.\d+)?)\s*cm", text.strip())
        return float(cm.group(1)) / 2.54 if cm and 100 <= float(cm.group(1)) <= 260 else None

    lower = upper = None
    recognized = False
    if raw.startswith("under "):
        upper = parse_point(raw[6:])
        recognized = upper is not None
    elif raw.startswith("over "):
        lower = parse_point(raw[5:])
        recognized = lower is not None
    elif "-" in raw:
        parts = raw.split("-")
        if len(parts) == 2:
            lower, upper = (parse_point(part) for part in parts)
            recognized = lower is not None and upper is not None and lower <= upper
    else:
        lower = upper = parse_point(raw)
        recognized = lower is not None

    category = None
    if recognized:
        # Apply a coarse rule only when the whole disclosed range fits it.
        if upper is not None and (upper < 64 or raw.startswith("under ") and upper == 64):
            category = "short"
        elif lower is not None and (lower > 69 or raw.startswith("over ") and lower == 69):
            category = "tall"
        elif lower is not None and upper is not None and lower >= 64 and upper <= 69:
            category = "average"
        else:
            category = "mixed"
    return {
        "height_range_inches": {"lower": lower, "upper": upper} if recognized else None,
        "height_category": category,
    }


def normalize_profile_signals(profile: Any) -> dict:
    """Derive signals afresh so stale client-provided normalized fields cannot win."""
    source = _record(profile)
    measurements = _record(source.get("measurements"))
    body = _first(source.get("bodyType"), source.get("body_type"), measurements.get("bodyType"))
    skin = _first(source.get("skinTone"), source.get("skin_tone"), measurements.get("skinTone"))
    height = _first(source.get("height"), measurements.get("height"), measurements.get("heightFeetInches"))
    age = source.get("age")
    age = age if isinstance(age, (int, float)) and not isinstance(age, bool) and 0 < age <= 120 and math.isfinite(age) else None
    body_type = normalize_body_type(body)
    return {
        "body_type": body_type,
        **skin_tone_signals(skin),
        **height_signals(height),
        "plus_size": body_type == "plus_size" or measurements.get("plusSize") is True,
        "age": age,
    }
