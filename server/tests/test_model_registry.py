from unittest.mock import MagicMock

from app.rag.model_registry import (
    clear_model_catalog_cache,
    normalize_model_name,
    resolve_chat_models,
    resolve_embedding_model,
)


def _model(name: str, actions: list[str]):
    model = MagicMock()
    model.name = f"models/{name}"
    model.display_name = name
    model.description = ""
    model.supported_actions = actions
    return model


def test_normalize_model_name():
    assert normalize_model_name("models/gemini-3.5-flash") == "gemini-3.5-flash"
    assert normalize_model_name("publishers/google/models/gemini-3.5-flash") == "gemini-3.5-flash"


def test_resolve_models_from_google_list(monkeypatch):
    clear_model_catalog_cache()
    monkeypatch.setattr("app.rag.model_registry.is_google_ai_configured", lambda: True)
    monkeypatch.setattr("app.rag.model_registry.settings.google_chat_model", "gemini-2.5-flash")
    monkeypatch.setattr("app.rag.model_registry.settings.google_chat_model_fallbacks", "")
    monkeypatch.setattr(
        "app.rag.model_registry.settings.google_embedding_model",
        "gemini-embedding-001",
    )

    pager = [
        _model("gemini-3.5-flash", ["generateContent"]),
        _model("gemini-3.1-flash-lite", ["generateContent"]),
        _model("gemini-embedding-001", ["embedContent"]),
        _model("imagen-4.0-generate-001", ["generateContent"]),
    ]

    mock_client = MagicMock()
    mock_client.models.list.return_value = pager
    monkeypatch.setattr("app.rag.google_client.get_genai_client", lambda: mock_client)

    chat_models = resolve_chat_models()
    assert chat_models[0] == "gemini-3.5-flash"
    assert "gemini-3.1-flash-lite" in chat_models
    assert "gemini-2.5-flash" not in chat_models
    assert "imagen-4.0-generate-001" not in chat_models
    assert resolve_embedding_model() == "gemini-embedding-001"
