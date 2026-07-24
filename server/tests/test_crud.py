from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.crud import replace_all_projects, user_has_projects
from app.database import Base
from app.models import LearningProject
from app.seed import SEED_PROJECTS


def test_replace_all_projects_removes_orphan_seed_ids():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with Session() as db:
        orphan = LearningProject(
            id="VELODESK-24",
            user_id="old-user-id",
            title="Old seed row",
            description="Orphan from a previous user",
            category="bug",
            status="not_started",
            priority="low",
            progress=0,
            tags=[],
            resource_url="",
            notes="",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(orphan)
        db.commit()

        replace_all_projects(db, "new-user-id", SEED_PROJECTS)

        assert not user_has_projects(db, "old-user-id")
        assert user_has_projects(db, "new-user-id")
        titles = [
            project.title
            for project in db.scalars(
                select(LearningProject).where(LearningProject.user_id == "new-user-id")
            ).all()
        ]
        assert any("VD-24" in title for title in titles)
        assert "Old seed row" not in titles
