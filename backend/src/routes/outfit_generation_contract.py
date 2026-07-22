"""Pure request/response contracts for the active outfit generation route."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, Dict, List, Optional, Tuple


class RequiredBaseItemNotFound(ValueError):
    """Raised when a requested wardrobe item is not present in the request."""


def _to_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "model_dump"):
        return dict(value.model_dump())
    if hasattr(value, "dict"):
        return dict(value.dict())
    return {
        key: getattr(value, key)
        for key in ("id", "name", "type", "subType", "color", "imageUrl")
        if hasattr(value, key)
    }


def _read(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(key, default)
    return getattr(value, key, default)


def item_identifier(item: Any) -> str:
    """Return a normalized item ID for dictionaries and Pydantic objects."""
    raw_id = _read(item, "id", "")
    return str(raw_id).strip() if raw_id is not None else ""


def resolve_required_base_item(
    wardrobe: Optional[Sequence[Any]], base_item_id: Optional[str]
) -> Optional[Any]:
    requested_id = str(base_item_id).strip() if base_item_id is not None else ""
    if not requested_id:
        return None

    for item in wardrobe or []:
        if item_identifier(item) == requested_id:
            return item

    raise RequiredBaseItemNotFound(
        f"Requested base item '{requested_id}' is not present in the submitted wardrobe"
    )


def _core_category(item: Any) -> str:
    raw_type = str(_read(item, "type", "") or "").lower().replace("clothingtype.", "")
    raw_subtype = str(_read(item, "subType", "") or "").lower()
    descriptor = f"{raw_type} {raw_subtype}".strip()
    if not descriptor:
        descriptor = str(_read(item, "name", "") or "").lower()

    category_keywords = (
        ("shoes", ("shoe", "sneaker", "boot", "sandal", "heel", "loafer", "oxford")),
        ("bottoms", ("pant", "jean", "trouser", "skirt", "short", "legging")),
        ("outerwear", ("jacket", "blazer", "coat", "cardigan", "vest")),
        ("one_piece", ("dress", "jumpsuit", "romper")),
        ("tops", ("shirt", "blouse", "sweater", "hoodie", "tank", "tee", "top", "polo")),
        ("accessories", ("belt", "hat", "scarf", "tie", "bag", "watch", "jewelry")),
    )
    for category, keywords in category_keywords:
        if any(keyword in descriptor for keyword in keywords):
            return category
    return "other"


def enforce_required_base_item(
    items: Optional[Sequence[Any]],
    wardrobe: Optional[Sequence[Any]],
    base_item_id: Optional[str],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Guarantee that the requested item appears exactly once in the outfit.

    When the generator omitted the item, replace an item from the same core category
    to preserve outfit size. If no comparable category exists, prepend the item.
    """
    requested_id = str(base_item_id).strip() if base_item_id is not None else ""
    normalized_items = [_to_dict(item) for item in (items or [])]
    contract = {
        "base_item_requested": bool(requested_id),
        "base_item_id": requested_id or None,
        "base_item_included": False,
        "base_item_repaired": False,
        "base_item_repair_action": "not_requested",
    }
    if not requested_id:
        return normalized_items, contract

    base_item = resolve_required_base_item(wardrobe, requested_id)
    matching_indexes = [
        index for index, item in enumerate(normalized_items) if item_identifier(item) == requested_id
    ]
    if matching_indexes:
        first_index = matching_indexes[0]
        deduplicated = [
            item
            for index, item in enumerate(normalized_items)
            if item_identifier(item) != requested_id or index == first_index
        ]
        duplicate_removed = len(matching_indexes) > 1
        contract.update(
            {
                "base_item_included": True,
                "base_item_repaired": duplicate_removed,
                "base_item_repair_action": "deduplicated" if duplicate_removed else "already_present",
            }
        )
        return deduplicated, contract

    base_item_dict = _to_dict(base_item)
    base_category = _core_category(base_item_dict)
    replacement_index = next(
        (
            index
            for index, item in enumerate(normalized_items)
            if base_category != "other" and _core_category(item) == base_category
        ),
        None,
    )

    if replacement_index is None:
        repaired_items = [base_item_dict, *normalized_items]
        action = "prepended"
    else:
        repaired_items = list(normalized_items)
        repaired_items[replacement_index] = base_item_dict
        action = "replaced_same_category"

    contract.update(
        {
            "base_item_included": True,
            "base_item_repaired": True,
            "base_item_repair_action": action,
        }
    )
    return repaired_items, contract


def _string_list(value: Any) -> List[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        values = list(value)
    else:
        values = []

    result: List[str] = []
    for item in values:
        if isinstance(item, str):
            cleaned = item.strip()
            if cleaned and cleaned not in result:
                result.append(cleaned)
    return result


def normalize_body_type(value: Any) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")
    aliases = {
        "round": "apple",
        "apple": "apple",
        "round_apple": "apple",
        "apple_round": "apple",
        "triangle": "pear",
        "pear_triangle": "pear",
        "triangle_pear": "pear",
        "straight": "rectangle",
        "straight_rectangle": "rectangle",
        "rectangle_straight": "rectangle",
        "inverted_triangle": "inverted_triangle",
    }
    normalized = aliases.get(token, token)
    return normalized if normalized in {
        "hourglass",
        "pear",
        "apple",
        "rectangle",
        "inverted_triangle",
        "oval",
        "average",
    } else "average"


def normalize_skin_tone(value: Any) -> str:
    """Normalize depth without inferring warm/cool undertone from the quiz slider."""
    raw_value = str(value or "").strip()
    slider_match = re.fullmatch(r"skin_tone_(\d{1,3})", raw_value.lower())
    numeric_match = re.fullmatch(r"(\d{1,3})", raw_value)
    if slider_match or numeric_match:
        depth = int((slider_match or numeric_match).group(1))
        if 0 <= depth <= 100:
            if depth <= 33:
                return "light"
            if depth <= 66:
                return "medium"
            return "deep"

    lowered = raw_value.lower()
    if any(label in lowered for label in ("fair", "light")):
        return "light"
    if any(label in lowered for label in ("deep", "dark")):
        return "deep"
    if any(label in lowered for label in ("warm", "cool", "neutral")):
        return next(label for label in ("warm", "cool", "neutral") if label in lowered)
    return "medium"


def normalize_generation_user_profile(
    profile: Optional[Mapping[str, Any]], user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Hydrate and normalize quiz signals for the robust scoring service."""
    source = dict(profile or {})
    measurements = source.get("measurements")
    measurements = dict(measurements) if isinstance(measurements, Mapping) else {}
    preferences = source.get("preferences")
    preferences = dict(preferences) if isinstance(preferences, Mapping) else {}

    body_type = source.get("bodyType") or source.get("body_type") or measurements.get("bodyType")
    skin_tone = source.get("skinTone") or source.get("skin_tone") or measurements.get("skinTone")
    height = source.get("height") or measurements.get("height") or ""
    weight = source.get("weight") or measurements.get("weight") or ""

    style_profile = source.get("stylePreferences")
    style_profile = dict(style_profile) if isinstance(style_profile, Mapping) else {}
    styles = (
        _string_list(style_profile.get("preferredStyles"))
        or _string_list(source.get("style_preferences"))
        or _string_list(source.get("stylePreferences"))
        or _string_list(preferences.get("style"))
    )
    colors = (
        _string_list(style_profile.get("favoriteColors"))
        or _string_list(source.get("color_preferences"))
        or _string_list(source.get("colorPreferences"))
        or _string_list(preferences.get("colors"))
    )
    brands = _string_list(style_profile.get("preferredBrands"))

    normalized_body_type = normalize_body_type(body_type)
    normalized_skin_tone = normalize_skin_tone(skin_tone)
    normalized = {
        **source,
        "id": user_id or source.get("id") or "",
        "bodyType": normalized_body_type,
        "skinTone": normalized_skin_tone,
        "height": height,
        "weight": weight,
        "style_preferences": styles,
        "color_preferences": colors,
        "stylePreferences": {
            **style_profile,
            "preferredStyles": styles,
            "favoriteColors": colors,
            "preferredBrands": brands,
        },
        "measurements": {
            **measurements,
            "bodyType": normalized_body_type,
            "skinTone": normalized_skin_tone,
            "height": height,
            "weight": weight,
        },
    }
    return normalized
