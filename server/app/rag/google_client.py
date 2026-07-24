from __future__ import annotations

import re
import time
from functools import lru_cache

from google import genai
from google.genai import types

from app.config import settings
from app.rag.exceptions import RagConfigurationError, RagRateLimitError, RagServiceError
from app.rag.model_registry import is_google_ai_configured, resolve_chat_models, resolve_embedding_model


@lru_cache(maxsize=1)
def get_genai_client() -> genai.Client:
    if not is_google_ai_configured():
        raise RagConfigurationError(
            "Set GOOGLE_API_KEY in server/.env to enable VeloDesk AI."
        )
    return genai.Client(api_key=settings.google_api_key.strip())


def _is_rate_limit_error(exc: Exception) -> bool:
    message = str(exc).upper()
    return "429" in message or "RESOURCE_EXHAUSTED" in message


def _parse_retry_seconds(exc: Exception) -> float:
    text = str(exc)
    for pattern in (
        r"retry in ([\d.]+)s",
        r"'retryDelay': '(\d+)s'",
        r"retryDelay['\"]:\s*['\"](\d+)s",
    ):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return 35.0


def _is_model_unavailable_error(exc: Exception) -> bool:
    message = str(exc).upper()
    return "404" in message and ("NOT_FOUND" in message or "NO LONGER AVAILABLE" in message)


def _friendly_rate_limit_message() -> str:
    models = ", ".join(resolve_chat_models())
    return (
        "Google AI free-tier quota was exceeded. Wait about a minute and try again. "
        f"Tried models: {models}. You can also set GOOGLE_CHAT_MODEL=gemini-3.1-flash-lite "
        "in server/.env for higher free-tier limits."
    )


def _friendly_model_unavailable_message() -> str:
    models = ", ".join(resolve_chat_models())
    return (
        "No configured Google AI chat model is available for your API key. "
        f"Tried models: {models}. Set GOOGLE_CHAT_MODEL=gemini-3.5-flash in server/.env."
    )


def _should_try_next_model(exc: Exception) -> bool:
    return _is_rate_limit_error(exc) or _is_model_unavailable_error(exc)


def _call_with_rate_limit_retry(action, *, action_name: str):
    last_error: Exception | None = None
    attempts = max(1, settings.google_api_max_retries)

    for attempt in range(attempts):
        try:
            return action()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if not _is_rate_limit_error(exc) or attempt >= attempts - 1:
                break
            time.sleep(min(_parse_retry_seconds(exc), 60))

    if last_error and _is_rate_limit_error(last_error):
        raise RagRateLimitError(_friendly_rate_limit_message()) from last_error

    raise RagServiceError(f"{action_name} failed: {last_error}") from last_error


def embed_texts(texts: list[str], *, task_type: str) -> list[list[float]]:
    if not texts:
        return []

    client = get_genai_client()
    model = resolve_embedding_model()

    def request():
        return client.models.embed_content(
            model=model,
            contents=texts,
            config=types.EmbedContentConfig(task_type=task_type),
        )

    try:
        response = _call_with_rate_limit_retry(
            request,
            action_name=f"Embedding request for model '{model}'",
        )
    except RagRateLimitError:
        raise
    except RagServiceError as exc:
        raise RagServiceError(
            f"Embedding request failed for model '{model}': {exc}"
        ) from exc

    embeddings = response.embeddings or []
    if len(embeddings) != len(texts):
        raise RagServiceError("Embedding response size did not match input.")

    return [list(item.values) for item in embeddings]


def embed_query(text: str) -> list[float]:
    return embed_texts([text], task_type="RETRIEVAL_QUERY")[0]


def embed_documents(texts: list[str]) -> list[list[float]]:
    return embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")


def generate_answer(prompt: str) -> str:
    client = get_genai_client()
    last_error: Exception | None = None

    for model in resolve_chat_models():
        def request(current_model: str = model):
            return client.models.generate_content(
                model=current_model,
                contents=prompt,
            )

        try:
            response = _call_with_rate_limit_retry(
                request,
                action_name=f"Generation request for model '{model}'",
            )
        except RagRateLimitError as exc:
            last_error = exc
            continue
        except RagServiceError as exc:
            last_error = exc
            if _should_try_next_model(exc):
                continue
            raise RagServiceError(f"Generation request failed for model '{model}': {exc}") from exc
        else:
            text = (response.text or "").strip()
            if not text:
                raise RagServiceError("Google AI returned an empty response.")
            return text

    if isinstance(last_error, RagRateLimitError):
        raise last_error
    if last_error and _is_rate_limit_error(last_error):
        raise RagRateLimitError(_friendly_rate_limit_message()) from last_error
    if last_error and _is_model_unavailable_error(last_error):
        raise RagServiceError(_friendly_model_unavailable_message()) from last_error
    raise RagServiceError(f"Generation request failed: {last_error}") from last_error
