from __future__ import annotations

import os
from typing import Any

UPLOAD_IMAGE_ANALYSIS_JOB_KIND = "upload_image_analysis"
DEFAULT_CODEX_ADMIN_EMAILS = {"jfeezie@gmail.com"}
DEFAULT_FAST_PATH_TIMEOUT_MS = 2500
DEFAULT_FAST_PATH_POLL_MS = 250


def _truthy_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def codex_upload_analysis_enabled() -> bool:
    return _truthy_env("EASYOUTFIT_CODEX_UPLOAD_ANALYSIS_ENABLED", default=False)


def codex_fast_path_timeout_ms() -> int:
    raw = os.getenv("EASYOUTFIT_CODEX_UPLOAD_FAST_PATH_TIMEOUT_MS")
    if not raw:
        return DEFAULT_FAST_PATH_TIMEOUT_MS
    try:
        return max(0, int(raw))
    except ValueError:
        return DEFAULT_FAST_PATH_TIMEOUT_MS


def codex_fast_path_poll_ms() -> int:
    raw = os.getenv("EASYOUTFIT_CODEX_UPLOAD_FAST_PATH_POLL_MS")
    if not raw:
        return DEFAULT_FAST_PATH_POLL_MS
    try:
        return max(50, int(raw))
    except ValueError:
        return DEFAULT_FAST_PATH_POLL_MS


def _normalized_email_set(raw: str | None) -> set[str]:
    emails = {email.strip().lower() for email in (raw or "").split(",") if email.strip()}
    return emails


def _normalized_user_id_set(raw: str | None) -> set[str]:
    return {user_id.strip() for user_id in (raw or "").split(",") if user_id.strip()}


def codex_admin_emails() -> set[str]:
    configured = _normalized_email_set(os.getenv("EASYOUTFIT_CODEX_ADMIN_EMAILS"))
    return configured or set(DEFAULT_CODEX_ADMIN_EMAILS)


def codex_admin_user_ids() -> set[str]:
    return _normalized_user_id_set(os.getenv("EASYOUTFIT_CODEX_COHORT_USER_IDS"))


def is_codex_image_analysis_user(*, user_id: str | None, email: str | None) -> bool:
    if not codex_upload_analysis_enabled():
        return False
    normalized_email = (email or "").strip().lower()
    normalized_user_id = (user_id or "").strip()
    return normalized_email in codex_admin_emails() or normalized_user_id in codex_admin_user_ids()


def build_upload_image_analysis_output_schema() -> dict[str, Any]:
    visual_enum = {
        "type": "string",
    }
    color_entry = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "hex": {"type": "string"},
        },
        "required": ["name", "hex"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "subType": {"type": "string"},
            "brand": {"type": "string"},
            "style": {"type": "array", "items": {"type": "string"}},
            "season": {"type": "array", "items": {"type": "string"}},
            "occasion": {"type": "array", "items": {"type": "string"}},
            "mood": {"type": "array", "items": {"type": "string"}},
            "dominantColors": {"type": "array", "items": color_entry},
            "matchingColors": {"type": "array", "items": color_entry},
            "metadata": {
                "type": "object",
                "properties": {
                    "naturalDescription": {"type": "string"},
                    "visualAttributes": {
                        "type": "object",
                        "properties": {
                            "material": visual_enum,
                            "pattern": visual_enum,
                            "fit": visual_enum,
                            "sleeveLength": visual_enum,
                            "formalLevel": visual_enum,
                            "genderTarget": visual_enum,
                            "wearLayer": visual_enum,
                            "neckline": visual_enum,
                            "transparency": visual_enum,
                            "collarType": visual_enum,
                            "embellishments": visual_enum,
                            "printSpecificity": visual_enum,
                            "rise": visual_enum,
                            "legOpening": visual_enum,
                            "heelHeight": visual_enum,
                            "waistbandType": visual_enum,
                            "statementLevel": {"type": "integer"},
                        },
                        "required": [
                            "material",
                            "pattern",
                            "fit",
                            "sleeveLength",
                            "formalLevel",
                            "genderTarget",
                            "wearLayer",
                            "neckline",
                            "transparency",
                            "collarType",
                            "embellishments",
                            "printSpecificity",
                            "rise",
                            "legOpening",
                            "heelHeight",
                            "waistbandType",
                            "statementLevel",
                        ],
                        "additionalProperties": False,
                    },
                },
                "required": ["naturalDescription", "visualAttributes"],
                "additionalProperties": False,
            },
        },
        "required": [
            "name",
            "type",
            "subType",
            "brand",
            "style",
            "season",
            "occasion",
            "mood",
            "dominantColors",
            "matchingColors",
            "metadata",
        ],
        "additionalProperties": False,
    }


def build_codex_upload_prompt(*, image_path: str, source_name: str | None, source_url: str | None) -> str:
    source_name_line = f"Source filename: {source_name}\n" if source_name else ""
    source_url_line = f"Source URL: {source_url}\n" if source_url else ""
    return (
        "You are analyzing a single clothing item image for EasyOutfit.\n"
        "Inspect the local image file and return JSON that matches the provided schema exactly.\n"
        "Be conservative and precise. Do not invent garments, colors, or brands that are not visible.\n"
        "The item should be named in a concise user-facing way, such as 'Black cropped blazer' or 'Blue straight-leg jeans'.\n"
        "Use normalized lowercase values for arrays like style, season, occasion, and mood.\n"
        "Prefer short, practical values for visual attributes.\n"
        "If a field is unclear, use 'unknown' or an empty string rather than guessing.\n\n"
        f"{source_name_line}"
        f"{source_url_line}"
        f"Local image path: {image_path}\n"
    )


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        cleaned = item.strip().lower()
        if cleaned:
            normalized.append(cleaned)
    return normalized


def _string_value(value: Any, default: str = "") -> str:
    if not isinstance(value, str):
        return default
    cleaned = value.strip()
    return cleaned or default


def _color_entries(value: Any, fallback_name: str = "unknown") -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    if isinstance(value, list):
        for item in value:
            if not isinstance(item, dict):
                continue
            name = _string_value(item.get("name"), "unknown")
            hex_value = _string_value(item.get("hex"), "#000000")
            entries.append({"name": name, "hex": hex_value})
    if entries:
        return entries
    return [{"name": fallback_name, "hex": "#000000"}]


def build_pending_codex_analysis(*, file_name: str | None = None) -> dict[str, Any]:
    item_name = _string_value(file_name.rsplit(".", 1)[0] if file_name and "." in file_name else file_name, "Processing item")
    return {
        "name": item_name,
        "type": "unknown",
        "subType": "",
        "clothing_type": "unknown",
        "color": "unknown",
        "primary_color": "unknown",
        "dominantColors": [{"name": "unknown", "hex": "#000000"}],
        "matchingColors": [],
        "style": [],
        "season": [],
        "occasion": [],
        "brand": "",
        "material": "unknown",
        "fit": "unknown",
        "sleeveLength": "unknown",
        "pattern": "unknown",
        "gender": "unisex",
        "formalLevel": "casual",
        "mood": [],
        "metadata": {
            "naturalDescription": "Codex is analyzing this item.",
            "visualAttributes": {
                "material": "unknown",
                "pattern": "unknown",
                "fit": "unknown",
                "sleeveLength": "unknown",
                "formalLevel": "casual",
                "genderTarget": "unisex",
                "wearLayer": "Mid",
                "neckline": "",
                "transparency": "opaque",
                "collarType": "",
                "embellishments": "none",
                "printSpecificity": "none",
                "rise": "",
                "legOpening": "",
                "heelHeight": "",
                "waistbandType": "",
                "statementLevel": 0,
            },
        },
    }


def normalize_codex_upload_analysis_result(raw: dict[str, Any], *, file_name: str | None = None) -> dict[str, Any]:
    metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
    visual = metadata.get("visualAttributes") if isinstance(metadata.get("visualAttributes"), dict) else {}
    dominant_colors = _color_entries(raw.get("dominantColors"))
    primary_color = dominant_colors[0]["name"] if dominant_colors else "unknown"
    pending = build_pending_codex_analysis(file_name=file_name)
    pending_visual = pending["metadata"]["visualAttributes"]
    return {
        "name": _string_value(raw.get("name"), pending["name"]),
        "type": _string_value(raw.get("type"), "unknown"),
        "subType": _string_value(raw.get("subType"), ""),
        "clothing_type": _string_value(raw.get("type"), "unknown"),
        "color": primary_color,
        "primary_color": primary_color,
        "dominantColors": dominant_colors,
        "matchingColors": _color_entries(raw.get("matchingColors"), fallback_name=primary_color) if raw.get("matchingColors") else [],
        "style": _string_list(raw.get("style")),
        "season": _string_list(raw.get("season")),
        "occasion": _string_list(raw.get("occasion")),
        "brand": _string_value(raw.get("brand"), ""),
        "material": _string_value(visual.get("material"), "unknown"),
        "fit": _string_value(visual.get("fit"), "unknown"),
        "sleeveLength": _string_value(visual.get("sleeveLength"), "unknown"),
        "pattern": _string_value(visual.get("pattern"), "unknown"),
        "gender": _string_value(visual.get("genderTarget"), "unisex"),
        "formalLevel": _string_value(visual.get("formalLevel"), "casual"),
        "mood": _string_list(raw.get("mood")),
        "metadata": {
            "naturalDescription": _string_value(metadata.get("naturalDescription"), ""),
            "visualAttributes": {
                "material": _string_value(visual.get("material"), pending_visual["material"]),
                "pattern": _string_value(visual.get("pattern"), pending_visual["pattern"]),
                "fit": _string_value(visual.get("fit"), pending_visual["fit"]),
                "sleeveLength": _string_value(visual.get("sleeveLength"), pending_visual["sleeveLength"]),
                "formalLevel": _string_value(visual.get("formalLevel"), pending_visual["formalLevel"]),
                "genderTarget": _string_value(visual.get("genderTarget"), pending_visual["genderTarget"]),
                "wearLayer": _string_value(visual.get("wearLayer"), pending_visual["wearLayer"]),
                "neckline": _string_value(visual.get("neckline"), pending_visual["neckline"]),
                "transparency": _string_value(visual.get("transparency"), pending_visual["transparency"]),
                "collarType": _string_value(visual.get("collarType"), pending_visual["collarType"]),
                "embellishments": _string_value(visual.get("embellishments"), pending_visual["embellishments"]),
                "printSpecificity": _string_value(visual.get("printSpecificity"), pending_visual["printSpecificity"]),
                "rise": _string_value(visual.get("rise"), pending_visual["rise"]),
                "legOpening": _string_value(visual.get("legOpening"), pending_visual["legOpening"]),
                "heelHeight": _string_value(visual.get("heelHeight"), pending_visual["heelHeight"]),
                "waistbandType": _string_value(visual.get("waistbandType"), pending_visual["waistbandType"]),
                "statementLevel": int(visual.get("statementLevel") or 0),
            },
        },
    }
