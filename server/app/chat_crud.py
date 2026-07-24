from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import ChatMessage, User
from app.schemas import ChatMessageCreate, ChatMessageResponse, new_chat_message_id


def _to_response(message: ChatMessage) -> ChatMessageResponse:
    author_name = message.author.name if message.author else "Unknown"
    return ChatMessageResponse(
        id=message.id,
        user_id=message.user_id,
        user_name=author_name,
        content=message.content,
        created_at=message.created_at,
    )


def list_messages(db: Session, *, limit: int = 100) -> list[ChatMessageResponse]:
    messages = list(
        db.scalars(
            select(ChatMessage)
            .options(joinedload(ChatMessage.author))
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        ).unique().all()
    )
    return [_to_response(message) for message in messages]


def create_message(db: Session, user: User, payload: ChatMessageCreate) -> ChatMessageResponse:
    message = ChatMessage(
        id=new_chat_message_id(),
        user_id=user.id,
        content=payload.content,
        created_at=datetime.now(UTC),
    )
    db.add(message)
    db.commit()
    created_id = message.id
    message = db.scalar(
        select(ChatMessage)
        .options(joinedload(ChatMessage.author))
        .where(ChatMessage.id == created_id)
    )
    return _to_response(message)
