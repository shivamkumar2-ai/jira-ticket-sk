from unittest.mock import patch

from app.rag.exceptions import RagRateLimitError
from app.rag.google_client import _is_rate_limit_error, _parse_retry_seconds, generate_answer
from fastapi.testclient import TestClient

from tests.conftest import auth_headers, client


def test_rag_status_without_google_key(client: TestClient, monkeypatch):
    monkeypatch.setattr("app.rag.service.is_google_ai_configured", lambda: False)
    headers = auth_headers(client, "ragstatus@example.com", "password123")
    response = client.get("/api/rag/status", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["configured"] is False
    assert payload["indexedCount"] == 0


def test_rag_ask_requires_google_key(client: TestClient, monkeypatch):
    monkeypatch.setattr("app.rag.google_client.is_google_ai_configured", lambda: False)
    headers = auth_headers(client, "ragask@example.com", "password123")
    response = client.post(
        "/api/rag/ask",
        headers=headers,
        json={"question": "What work items are in progress?"},
    )
    assert response.status_code == 503


def test_parse_retry_seconds_from_google_error():
    error = Exception(
        "429 RESOURCE_EXHAUSTED ... Please retry in 33.673069316s."
    )
    assert _is_rate_limit_error(error) is True
    assert _parse_retry_seconds(error) == 33.673069316


@patch("app.rag.google_client._call_with_rate_limit_retry")
@patch("app.rag.google_client.resolve_chat_models", return_value=["gemini-3.5-flash"])
@patch("app.rag.service.sync_embeddings")
@patch("app.rag.service.search_similar_chunks")
@patch("app.rag.service.generate_answer")
@patch("app.rag.service.is_google_ai_configured", return_value=True)
@patch("app.rag.service.count_embeddings")
def test_rag_ask_with_mocked_pipeline(
    mock_count,
    _mock_configured,
    mock_generate,
    mock_search,
    mock_sync,
    _mock_resolve_models,
    _mock_retry,
    client: TestClient,
):
    mock_count.side_effect = [0, 1]
    mock_sync.return_value = {"indexed": 1, "created": 1, "updated": 0, "removed": 0, "sources": 1}
    mock_search.return_value = [
        type(
            "Chunk",
            (),
            {
                "source_type": "project",
                "source_id": "vd-1",
                "content": "Work item vd-1: Fix login bug",
                "score": 0.91,
            },
        )()
    ]
    mock_generate.return_value = "VD-1 is in progress."

    headers = auth_headers(client, "ragmock@example.com", "password123")
    response = client.post(
        "/api/rag/ask",
        headers=headers,
        json={"question": "What is in progress?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "VD-1 is in progress."
    assert payload["sources"][0]["sourceId"] == "vd-1"
    assert payload["indexedCount"] == 1


def test_generate_answer_raises_rate_limit_error_when_all_models_exhausted(monkeypatch):
    monkeypatch.setattr(
        "app.rag.google_client.resolve_chat_models",
        lambda: ["gemini-3.5-flash"],
    )
    monkeypatch.setattr("app.rag.google_client.settings.google_api_max_retries", 1)
    monkeypatch.setattr("app.rag.google_client.time.sleep", lambda _seconds: None)
    with patch("app.rag.google_client.get_genai_client") as mock_client:
        mock_client.return_value.models.generate_content.side_effect = Exception(
            "429 RESOURCE_EXHAUSTED for gemini-3.5-flash"
        )
        try:
            generate_answer("hello")
        except RagRateLimitError as exc:
            assert "quota was exceeded" in str(exc).lower()
        else:
            raise AssertionError("Expected RagRateLimitError")


def test_generate_answer_falls_back_when_model_not_found(monkeypatch):
    monkeypatch.setattr(
        "app.rag.google_client.resolve_chat_models",
        lambda: ["gemini-2.5-flash", "gemini-3.5-flash"],
    )

    with patch("app.rag.google_client.get_genai_client") as mock_client:
        def generate_content(*, model, contents):
            if model == "gemini-2.5-flash":
                raise Exception(
                    "404 NOT_FOUND. This model is no longer available to new users."
                )
            return type("Response", (), {"text": "Answer from fallback model."})()

        mock_client.return_value.models.generate_content.side_effect = generate_content
        assert generate_answer("hello") == "Answer from fallback model."
