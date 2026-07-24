from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.chat_crud import create_message, list_messages
from app.database import get_db
from app.models import User
from app.schemas import ChatMessageCreate, ChatMessageListResponse, ChatMessageResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/messages", response_model=ChatMessageListResponse)
def get_messages(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ChatMessageListResponse:
    items = list_messages(db)
    return ChatMessageListResponse(items=items, total=len(items))


@router.post("/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def post_message(
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatMessageResponse:
    return create_message(db, current_user, payload)
