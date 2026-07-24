from __future__ import annotations

import time
from dataclasses import dataclass

from app.config import settings
from app.rag.exceptions import RagConfigurationError, RagServiceError


def is_google_ai_configured() -> bool:
    return bool(settings.google_api_key.strip())

GENERATE_ACTION = "generateContent"
EMBED_ACTION = "embedContent"

CHAT_MODEL_BLOCKLIST = (
    "embedding",
    "image",
    "tts",
    "live",
    "imagen",
    "veo",
    "robotics",
    "computer-use",
    "deep-research",
    "antigravity",
    "lyria",
    "omni",
    "aqa",
    "nano-banana",
)

_CACHE_TTL_SECONDS = 300
_catalog_cache: dict | None = None
_catalog_cached_at = 0.0


@dataclass(frozen=True)
class GoogleModelInfo:
    name: str
    display_name: str
    description: str
    supported_actions: tuple[str, ...]


def normalize_model_name(name: str | None) -> str:
    if not name:
        return ""
    if name.startswith("models/"):
        return name.removeprefix("models/")
    if "/models/" in name:
        return name.rsplit("/models/", 1)[-1]
    return name


def clear_model_catalog_cache() -> None:
    global _catalog_cache, _catalog_cached_at
    _catalog_cache = None
    _catalog_cached_at = 0.0


def _supports_action(model, action: str) -> bool:
    return action in (model.supported_actions or [])


def _is_chat_candidate(model_id: str) -> bool:
    lowered = model_id.lower()
    return not any(token in lowered for token in CHAT_MODEL_BLOCKLIST)


def _rank_chat_model(model_id: str) -> tuple[int, str]:
    lowered = model_id.lower()
    if not _is_chat_candidate(model_id):
        return (100, lowered)

    priority = 50
    if "gemini" in lowered:
        priority -= 10
    if "flash-lite" in lowered:
        priority -= 4
    elif "flash" in lowered:
        priority -= 8
    if "pro" in lowered:
        priority += 3
    if "preview" in lowered or "exp" in lowered:
        priority += 2
    if "3.5" in lowered:
        priority -= 6
    if "3.1" in lowered:
        priority -= 3
    if "2.5" in lowered:
        priority += 4
    if "2.0" in lowered:
        priority += 6
    return (priority, lowered)


def _rank_embedding_model(model_id: str) -> tuple[int, str]:
    lowered = model_id.lower()
    priority = 50
    if "gemini-embedding" in lowered:
        priority -= 10
    if "embedding" in lowered:
        priority -= 5
    if "2" in lowered:
        priority -= 2
    if "preview" in lowered or "exp" in lowered:
        priority += 3
    return (priority, lowered)


def _fetch_catalog_from_api() -> dict[str, list[GoogleModelInfo]]:
    from app.rag.google_client import get_genai_client

    client = get_genai_client()
    chat_models: list[GoogleModelInfo] = []
    embedding_models: list[GoogleModelInfo] = []

    try:
        pager = client.models.list()
        for model in pager:
            model_id = normalize_model_name(model.name)
            if not model_id:
                continue

            info = GoogleModelInfo(
                name=model_id,
                display_name=model.display_name or model_id,
                description=model.description or "",
                supported_actions=tuple(model.supported_actions or ()),
            )

            if _supports_action(model, GENERATE_ACTION) and _is_chat_candidate(model_id):
                chat_models.append(info)
            if _supports_action(model, EMBED_ACTION):
                embedding_models.append(info)
    except Exception as exc:  # noqa: BLE001
        raise RagServiceError(f"Unable to list Google AI models: {exc}") from exc

    chat_models.sort(key=lambda item: _rank_chat_model(item.name))
    embedding_models.sort(key=lambda item: _rank_embedding_model(item.name))

    return {
        "chat": chat_models,
        "embedding": embedding_models,
    }


def get_model_catalog(*, force_refresh: bool = False) -> dict[str, list[GoogleModelInfo]]:
    global _catalog_cache, _catalog_cached_at

    if not is_google_ai_configured():
        raise RagConfigurationError(
            "Set GOOGLE_API_KEY in server/.env to enable VeloDesk AI."
        )

    now = time.time()
    if (
        not force_refresh
        and _catalog_cache is not None
        and now - _catalog_cached_at < _CACHE_TTL_SECONDS
    ):
        return _catalog_cache

    _catalog_cache = _fetch_catalog_from_api()
    _catalog_cached_at = now
    return _catalog_cache


def _dedupe_preserve_order(models: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for model in models:
        if model and model not in seen:
            seen.add(model)
            ordered.append(model)
    return ordered


def resolve_chat_models() -> list[str]:
    if not is_google_ai_configured():
        return settings.google_chat_model_list

    catalog = get_model_catalog()
    available = [model.name for model in catalog["chat"]]
    if not available:
        return settings.google_chat_model_list

    preferred = [
        model
        for model in settings.google_chat_model_list
        if model in available
    ]
    auto_ranked = [model for model in available if model not in preferred]
    resolved = _dedupe_preserve_order([*preferred, *auto_ranked])
    return resolved or settings.google_chat_model_list


def resolve_embedding_model() -> str:
    configured = settings.google_embedding_model.strip()
    if not is_google_ai_configured():
        return configured

    catalog = get_model_catalog()
    available = [model.name for model in catalog["embedding"]]
    if configured in available:
        return configured
    if available:
        return available[0]
    return configured


def list_model_catalog_payload() -> dict:
    catalog = get_model_catalog()
    chat_models = resolve_chat_models()
    embedding_model = resolve_embedding_model()
    return {
        "chatModels": [
            {
                "name": model.name,
                "displayName": model.display_name,
                "description": model.description,
                "supportedActions": list(model.supported_actions),
            }
            for model in catalog["chat"]
        ],
        "embeddingModels": [
            {
                "name": model.name,
                "displayName": model.display_name,
                "description": model.description,
                "supportedActions": list(model.supported_actions),
            }
            for model in catalog["embedding"]
        ],
        "selectedChatModels": chat_models,
        "selectedEmbeddingModel": embedding_model,
    }
