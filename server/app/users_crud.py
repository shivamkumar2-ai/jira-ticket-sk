from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import LearningProject, User
from app.schemas import UserResponse


def list_users(db: Session) -> list[UserResponse]:
    users = list(db.scalars(select(User).order_by(User.name.asc())).all())
    return [UserResponse.model_validate(user) for user in users]


def get_projects_query(user_ids: list[str]):
    return (
        select(LearningProject)
        .options(joinedload(LearningProject.owner))
        .where(LearningProject.user_id.in_(user_ids))
    )
