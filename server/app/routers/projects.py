from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.constants import SortOption
from app.crud import (
    compute_stats,
    create_project,
    delete_project,
    get_project,
    list_projects,
    replace_all_projects,
    update_project,
)
from app.database import get_db
from app.models import User
from app.schemas import (
    MessageResponse,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
    StatsResponse,
)
from app.seed import SEED_PROJECTS

router = APIRouter(prefix="/projects", tags=["projects"])


def resolve_user_ids(selected_users: list[str], current_user: User) -> list[str]:
    if not selected_users:
        return [current_user.id]
    return selected_users


@router.get("", response_model=ProjectListResponse)
def get_projects(
    search: str = Query(default="", max_length=200),
    status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    sort: SortOption = Query(default=SortOption.UPDATED_DESC),
    users: list[str] = Query(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectListResponse:
    user_ids = resolve_user_ids(users, current_user)
    items = list_projects(
        db,
        user_ids,
        search=search,
        status=status,
        category=category,
        priority=priority,
        sort=sort,
    )
    return ProjectListResponse(items=items, total=len(items))


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    users: list[str] = Query(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StatsResponse:
    user_ids = resolve_user_ids(users, current_user)
    return compute_stats(db, user_ids)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_by_id(
    project_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ProjectResponse:
    return get_project(db, project_id)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_learning_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    return create_project(db, current_user.id, payload)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_learning_project(
    project_id: str,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    return update_project(db, current_user.id, project_id, payload)


@router.delete("/{project_id}", response_model=MessageResponse)
def delete_learning_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    delete_project(db, current_user.id, project_id)
    return MessageResponse(message="Work item deleted.")


@router.post("/seed", response_model=ProjectListResponse)
def seed_learning_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectListResponse:
    items = replace_all_projects(db, current_user.id, SEED_PROJECTS)
    return ProjectListResponse(items=items, total=len(items))
