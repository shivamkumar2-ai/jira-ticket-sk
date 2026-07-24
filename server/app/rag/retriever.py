from __future__ import annotations

import math
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentEmbedding
from app.rag.google_client import embed_query


@dataclass(frozen=True)
class RetrievedChunk:
    source_type: str
    source_id: str
    content: str
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def search_similar_chunks(db: Session, query: str, *, top_k: int) -> list[RetrievedChunk]:
    query_vector = embed_query(query)
    rows = list(db.scalars(select(DocumentEmbedding)).all())
    scored = [
        RetrievedChunk(
            source_type=row.source_type,
            source_id=row.source_id,
            content=row.content,
            score=cosine_similarity(query_vector, row.embedding),
        )
        for row in rows
    ]
    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:top_k]
