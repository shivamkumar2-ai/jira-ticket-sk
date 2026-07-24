from datetime import UTC, datetime

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session, joinedload

from app.constants import PRIORITY_WEIGHT, ProjectStatus, SortOption
from app.models import LearningProject, User
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate, StatsResponse
from app.ticket_ids import next_ticket_id
from app.users_crud import get_projects_query


class ProjectNotFoundError(Exception):
    def __init__(self, project_id: str) -> None:
        self.project_id = project_id
        super().__init__(f"Project '{project_id}' was not found.")


def _to_response(project: LearningProject) -> ProjectResponse:
    owner_name = project.owner.name if project.owner else "Unknown"
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        category=project.category,
        status=project.status,
        priority=project.priority,
        progress=project.progress,
        tags=project.tags or [],
        resource_url=project.resource_url,
        notes=project.notes,
        owner_id=project.user_id,
        owner_name=owner_name,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def list_projects(
    db: Session,
    user_ids: list[str],
    *,
    search: str = "",
    status: str | None = None,
    category: str | None = None,
    priority: str | None = None,
    sort: SortOption = SortOption.UPDATED_DESC,
) -> list[ProjectResponse]:
    if not user_ids:
        return []

    projects = list(db.scalars(get_projects_query(user_ids)).unique().all())

    query_text = search.strip().lower()
    filtered: list[LearningProject] = []

    for project in projects:
        if status and project.status != status:
            continue
        if category and project.category != category:
            continue
        if priority and project.priority != priority:
            continue

        if query_text:
            haystack = " ".join(
                [
                    project.title,
                    project.description,
                    project.notes,
                    " ".join(project.tags or []),
                ]
            ).lower()
            if query_text not in haystack:
                continue

        filtered.append(project)

    reverse = sort == SortOption.UPDATED_DESC
    filtered.sort(key=lambda project: _sort_key(project, sort), reverse=reverse)
    return [_to_response(project) for project in filtered]


def _sort_key(project: LearningProject, sort: SortOption):
    if sort == SortOption.UPDATED_ASC:
        return project.updated_at
    if sort == SortOption.TITLE_ASC:
        return project.title.lower()
    if sort == SortOption.PROGRESS_DESC:
        return (-project.progress, project.updated_at.timestamp())
    if sort == SortOption.PRIORITY_DESC:
        return (-PRIORITY_WEIGHT.get(project.priority, 0), project.updated_at.timestamp())
    return project.updated_at


def get_project(db: Session, project_id: str) -> ProjectResponse:
    project = db.scalar(
        select(LearningProject)
        .options(joinedload(LearningProject.owner))
        .where(LearningProject.id == project_id)
    )
    if not project:
        raise ProjectNotFoundError(project_id)
    return _to_response(project)


def create_project(db: Session, user_id: str, payload: ProjectCreate) -> ProjectResponse:
    now = datetime.now(UTC)
    project = LearningProject(
        id=next_ticket_id(db),
        user_id=user_id,
        title=payload.title,
        description=payload.description,
        category=payload.category.value,
        status=payload.status.value,
        priority=payload.priority.value,
        progress=payload.progress,
        tags=payload.tags,
        resource_url=payload.resource_url,
        notes=payload.notes,
        created_at=now,
        updated_at=now,
    )
    db.add(project)
    db.commit()
    created_id = project.id
    project = db.scalar(
        select(LearningProject)
        .options(joinedload(LearningProject.owner))
        .where(LearningProject.id == created_id)
    )
    return _to_response(project)


def update_project(
    db: Session,
    user_id: str,
    project_id: str,
    payload: ProjectUpdate,
) -> ProjectResponse:
    project = db.get(LearningProject, project_id)
    if not project or project.user_id != user_id:
        raise ProjectNotFoundError(project_id)

    project.title = payload.title
    project.description = payload.description
    project.category = payload.category.value
    project.status = payload.status.value
    project.priority = payload.priority.value
    project.progress = payload.progress
    project.tags = payload.tags
    project.resource_url = payload.resource_url
    project.notes = payload.notes
    project.updated_at = datetime.now(UTC)

    db.commit()
    updated_id = project.id
    project = db.scalar(
        select(LearningProject)
        .options(joinedload(LearningProject.owner))
        .where(LearningProject.id == updated_id)
    )
    return _to_response(project)


def delete_project(db: Session, user_id: str, project_id: str) -> None:
    project = db.get(LearningProject, project_id)
    if not project or project.user_id != user_id:
        raise ProjectNotFoundError(project_id)
    db.delete(project)
    db.commit()


def compute_stats(db: Session, user_ids: list[str]) -> StatsResponse:
    if not user_ids:
        return StatsResponse(total=0, completed=0, in_progress=0, not_started=0, avg_progress=0)

    projects = list(db.scalars(get_projects_query(user_ids)).unique().all())
    total = len(projects)
    completed = sum(1 for project in projects if project.status == ProjectStatus.COMPLETED)
    in_progress = sum(1 for project in projects if project.status == ProjectStatus.IN_PROGRESS)
    not_started = sum(1 for project in projects if project.status == ProjectStatus.NOT_STARTED)
    avg_progress = round(sum(project.progress for project in projects) / total) if total else 0

    return StatsResponse(
        total=total,
        completed=completed,
        in_progress=in_progress,
        not_started=not_started,
        avg_progress=avg_progress,
    )


def replace_all_projects(
    db: Session,
    user_id: str,
    projects: list[dict],
) -> list[ProjectResponse]:
    incoming_ids = [item["id"] for item in projects]

    # Remove this user's projects and any rows that reuse the incoming seed ids
    # (e.g. orphaned rows from a prior demo user or pre-auth migration).
    delete_filters = [LearningProject.user_id == user_id]
    if incoming_ids:
        delete_filters.append(LearningProject.id.in_(incoming_ids))

    db.execute(delete(LearningProject).where(or_(*delete_filters)))
    db.commit()

    for item in projects:
        project = LearningProject(
            id=item["id"],
            user_id=user_id,
            title=item["title"],
            description=item["description"],
            category=item["category"],
            status=item["status"],
            priority=item["priority"],
            progress=item["progress"],
            tags=item.get("tags", []),
            resource_url=item.get("resource_url", item.get("resourceUrl", "")),
            notes=item.get("notes", ""),
            created_at=item["created_at"],
            updated_at=item["updated_at"],
        )
        db.add(project)

    db.commit()
    return list_projects(db, [user_id])


def user_has_projects(db: Session, user_id: str) -> bool:
    return db.scalar(
        select(LearningProject.id).where(LearningProject.user_id == user_id).limit(1)
    ) is not None
