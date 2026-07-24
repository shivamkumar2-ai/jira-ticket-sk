from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.crud import create_project
from app.database import Base
from app.models import LearningProject, User
from app.schemas import ProjectCreate
from app.constants import ProjectCategory, ProjectPriority, ProjectStatus
from app.ticket_ids import format_ticket_id, next_ticket_id, parse_ticket_number


def _build_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _sample_payload() -> ProjectCreate:
    return ProjectCreate(
        title="New ticket",
        description="Ticket description for numbering test.",
        category=ProjectCategory.TASK,
        status=ProjectStatus.NOT_STARTED,
        priority=ProjectPriority.MEDIUM,
        progress=0,
        tags=[],
        resource_url="",
        notes="",
    )


def test_parse_ticket_number():
    assert parse_ticket_number("VELODESK-24") == 24
    assert parse_ticket_number("velodesk-7") == 7
    assert parse_ticket_number("seed-1") is None


def test_next_ticket_id_increments_from_existing_rows():
    Session = _build_db()
    now = datetime.now(UTC)

    with Session() as db:
        db.add(
            User(
                id="user-1",
                email="ticket@example.com",
                name="Ticket User",
                password_hash="hash",
                created_at=now,
            )
        )
        db.add(
            LearningProject(
                id=format_ticket_id(45),
                user_id="user-1",
                title="Existing",
                description="Existing ticket",
                category="task",
                status="not_started",
                priority="low",
                progress=0,
                tags=[],
                resource_url="",
                notes="",
                created_at=now,
                updated_at=now,
            )
        )
        db.commit()

        assert next_ticket_id(db) == "VELODESK-46"


def test_create_project_assigns_velodesk_ticket_id():
    Session = _build_db()
    now = datetime.now(UTC)

    with Session() as db:
        db.add(
            User(
                id="user-2",
                email="create@example.com",
                name="Creator",
                password_hash="hash",
                created_at=now,
            )
        )
        db.commit()

        created = create_project(db, "user-2", _sample_payload())
        assert created.id == "VELODESK-1"

        second = create_project(db, "user-2", _sample_payload())
        assert second.id == "VELODESK-2"
