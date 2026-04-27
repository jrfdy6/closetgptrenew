from __future__ import annotations

from .runtime_config import get_openai_image_edit_model, get_openai_image_edit_timeout_seconds


def get_image_edit_runtime_config() -> dict[str, str | float]:
    """
    Centralize image-edit runtime defaults before the worker is fully migrated.
    """
    return {
        "api_url": "https://api.openai.com/v1/images/edits",
        "model": get_openai_image_edit_model(),
        "timeout_seconds": get_openai_image_edit_timeout_seconds(),
    }
