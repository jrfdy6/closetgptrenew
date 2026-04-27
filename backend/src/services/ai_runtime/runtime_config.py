from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _read_positive_float_env(name: str, default: float) -> float:
    raw = (os.getenv(name) or "").strip()
    if raw:
        try:
            value = float(raw)
            if value > 0:
                return value
        except ValueError:
            pass
    return default


DEFAULT_OPENAI_TIMEOUT_SECONDS = _read_positive_float_env("EASYOUTFIT_OPENAI_TIMEOUT_SECONDS", 45.0)
DEFAULT_OPENAI_VISION_MODEL = os.getenv("EASYOUTFIT_OPENAI_VISION_MODEL", "gpt-4o")
DEFAULT_OPENAI_EMBEDDING_MODEL = os.getenv("EASYOUTFIT_OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
DEFAULT_OPENAI_IMAGE_EDIT_MODEL = os.getenv("EASYOUTFIT_OPENAI_IMAGE_EDIT_MODEL", "gpt-image-1")
DEFAULT_OPENAI_IMAGE_EDIT_TIMEOUT_SECONDS = _read_positive_float_env(
    "EASYOUTFIT_OPENAI_IMAGE_EDIT_TIMEOUT_SECONDS",
    120.0,
)


def get_openai_api_key() -> str:
    return (os.getenv("OPENAI_API_KEY") or "").strip()


def is_openai_configured() -> bool:
    return bool(get_openai_api_key())


def get_openai_timeout_seconds(default: float = DEFAULT_OPENAI_TIMEOUT_SECONDS) -> float:
    return _read_positive_float_env("EASYOUTFIT_OPENAI_TIMEOUT_SECONDS", default)


def get_openai_vision_model(default: str = DEFAULT_OPENAI_VISION_MODEL) -> str:
    return (os.getenv("EASYOUTFIT_OPENAI_VISION_MODEL") or default).strip() or default


def get_openai_embedding_model(default: str = DEFAULT_OPENAI_EMBEDDING_MODEL) -> str:
    return (os.getenv("EASYOUTFIT_OPENAI_EMBEDDING_MODEL") or default).strip() or default


def get_openai_image_edit_model(default: str = DEFAULT_OPENAI_IMAGE_EDIT_MODEL) -> str:
    return (os.getenv("EASYOUTFIT_OPENAI_IMAGE_EDIT_MODEL") or default).strip() or default


def get_openai_image_edit_timeout_seconds(default: float = DEFAULT_OPENAI_IMAGE_EDIT_TIMEOUT_SECONDS) -> float:
    return _read_positive_float_env("EASYOUTFIT_OPENAI_IMAGE_EDIT_TIMEOUT_SECONDS", default)


def build_openai_client(*, api_key: str | None = None, timeout_seconds: float | None = None) -> OpenAI:
    resolved_api_key = (api_key or "").strip() or get_openai_api_key()
    if not resolved_api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    return OpenAI(api_key=resolved_api_key, timeout=timeout_seconds or get_openai_timeout_seconds())
