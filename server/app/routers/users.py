from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import UserListResponse
from app.users_crud import list_users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserListResponse)
def get_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> UserListResponse:
    items = list_users(db)
    return UserListResponse(items=items, total=len(items))
