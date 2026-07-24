from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentEmbedding
from app.rag.documents import SourceDocument, collect_source_documents
from app.rag.google_client import embed_documents
from app.schemas import new_embedding_id


def count_embeddings(db: Session) -> int:
    return len(db.scalars(select(DocumentEmbedding.id)).all())


def sync_embeddings(db: Session) -> dict[str, int]:
    documents = collect_source_documents(db)
    removed = _remove_stale_embeddings(db, documents)
    created, updated = _upsert_documents(db, documents)
    return {
        "indexed": count_embeddings(db),
        "created": created,
        "updated": updated,
        "removed": removed,
        "sources": len(documents),
    }


def _upsert_documents(db: Session, documents: list[SourceDocument]) -> tuple[int, int]:
    if not documents:
        return 0, 0

    existing = {
        (row.source_type, row.source_id): row
        for row in db.scalars(select(DocumentEmbedding)).all()
    }

    to_embed: list[SourceDocument] = []
    for document in documents:
        current = existing.get((document.source_type, document.source_id))
        if current and current.content_hash == document.content_hash:
            continue
        to_embed.append(document)

    if not to_embed:
        return 0, 0

    vectors = embed_documents([document.content for document in to_embed])
    created = 0
    updated = 0
    now = datetime.now(UTC)

    for document, vector in zip(to_embed, vectors, strict=True):
        key = (document.source_type, document.source_id)
        current = existing.get(key)
        if current:
            current.content = document.content
            current.content_hash = document.content_hash
            current.embedding = vector
            current.updated_at = now
            updated += 1
        else:
            db.add(
                DocumentEmbedding(
                    id=new_embedding_id(),
                    source_type=document.source_type,
                    source_id=document.source_id,
                    content=document.content,
                    content_hash=document.content_hash,
                    embedding=vector,
                    updated_at=now,
                )
            )
            created += 1

    db.commit()
    return created, updated


def _remove_stale_embeddings(db: Session, documents: list[SourceDocument]) -> int:
    valid_keys = {(document.source_type, document.source_id) for document in documents}
    stale = [
        row
        for row in db.scalars(select(DocumentEmbedding)).all()
        if (row.source_type, row.source_id) not in valid_keys
    ]
    for row in stale:
        db.delete(row)
    if stale:
        db.commit()
    return len(stale)
