from __future__ import annotations

from sqlalchemy.orm import Session

from app.config import settings
from app.rag.exceptions import RagServiceError
from app.rag.google_client import generate_answer, is_google_ai_configured
from app.rag.indexer import count_embeddings, sync_embeddings
from app.rag.model_registry import list_model_catalog_payload, resolve_chat_models, resolve_embedding_model
from app.rag.retriever import RetrievedChunk, search_similar_chunks


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    if chunks:
        context = "\n\n---\n\n".join(
            f"[{index + 1}] ({chunk.source_type}:{chunk.source_id})\n{chunk.content}"
            for index, chunk in enumerate(chunks)
        )
    else:
        context = "No workspace records were indexed."

    return f"""You are VeloDesk AI, a helpful assistant for a work coordination workspace.
Answer using only the workspace context below. If the answer is not in the context, say you do not have enough workspace data and suggest what the user could add.

Workspace context:
{context}

User question:
{question}

Reply in clear, concise prose. Mention relevant work item IDs when helpful."""


def ask_workspace_question(db: Session, question: str, *, top_k: int | None = None) -> dict:
    limit = top_k or settings.rag_top_k
    if count_embeddings(db) == 0:
        sync_embeddings(db)

    chunks = search_similar_chunks(db, question, top_k=limit)
    answer = generate_answer(build_prompt(question, chunks))
    return {
        "answer": answer,
        "sources": [
            {
                "sourceType": chunk.source_type,
                "sourceId": chunk.source_id,
                "content": chunk.content,
                "score": round(chunk.score, 4),
            }
            for chunk in chunks
        ],
        "indexedCount": count_embeddings(db),
        "configured": is_google_ai_configured(),
    }


def get_rag_status(db: Session) -> dict:
    status = {
        "configured": is_google_ai_configured(),
        "indexedCount": count_embeddings(db),
        "embeddingModel": settings.google_embedding_model,
        "chatModel": settings.google_chat_model,
    }
    if is_google_ai_configured():
        try:
            status["embeddingModel"] = resolve_embedding_model()
            status["chatModel"] = resolve_chat_models()[0]
            status["selectedChatModels"] = resolve_chat_models()
        except RagServiceError:
            pass
    return status
