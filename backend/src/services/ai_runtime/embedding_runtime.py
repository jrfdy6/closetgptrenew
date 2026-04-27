from __future__ import annotations

import logging

from .runtime_config import build_openai_client, get_openai_embedding_model, is_openai_configured

logger = logging.getLogger(__name__)


async def generate_text_embedding(
    text: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
    max_input_chars: int | None = None,
) -> list[float] | None:
    if not api_key and not is_openai_configured():
        return None

    normalized_text = text[:max_input_chars] if max_input_chars else text
    if not normalized_text.strip():
        return None

    try:
        client = build_openai_client(api_key=api_key)
        response = client.embeddings.create(
            model=model or get_openai_embedding_model(),
            input=normalized_text,
        )
        return list(response.data[0].embedding)
    except Exception as exc:
        logger.error(f"Error generating text embedding: {exc}")
        return None
