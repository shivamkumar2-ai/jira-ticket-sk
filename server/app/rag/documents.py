from __future__ import annotations

import hashlib
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import ChatMessage, LearningProject


@dataclass(frozen=True)
class SourceDocument:
    source_type: str
    source_id: str
    content: str

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()


def _format_project(project: LearningProject) -> str:
    owner_name = project.owner.name if project.owner else "Unknown"
    tags = ", ".join(project.tags or [])
    return "\n".join(
        [
            f"Work item {project.id}: {project.title}",
            f"Owner: {owner_name}",
            f"Status: {project.status}",
            f"Priority: {project.priority}",
            f"Progress: {project.progress}%",
            f"Category: {project.category}",
            f"Description: {project.description}",
            f"Notes: {project.notes or 'None'}",
            f"Tags: {tags or 'None'}",
        ]
    )


def _format_chat_message(message: ChatMessage) -> str:
    author_name = message.author.name if message.author else "Unknown"
    return "\n".join(
        [
            f"Chat message {message.id}",
            f"Author: {author_name}",
            f"Sent at: {message.created_at.isoformat()}",
            f"Message: {message.content}",
        ]
    )


def collect_source_documents(db: Session) -> list[SourceDocument]:
    documents: list[SourceDocument] = []

    projects = list(
        db.scalars(
            select(LearningProject)
            .options(joinedload(LearningProject.owner))
            .order_by(LearningProject.updated_at.desc())
        ).unique().all()
    )
    for project in projects:
        documents.append(
            SourceDocument(
                source_type="project",
                source_id=project.id,
                content=_format_project(project),
            )
        )

    messages = list(
        db.scalars(
            select(ChatMessage)
            .options(joinedload(ChatMessage.author))
            .order_by(ChatMessage.created_at.asc())
        ).unique().all()
    )
    for message in messages:
        documents.append(
            SourceDocument(
                source_type="chat_message",
                source_id=message.id,
                content=_format_chat_message(message),
            )
        )

    return documents
