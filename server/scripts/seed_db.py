"""Load seed learning projects into the database."""

from app.crud import replace_all_projects
from app.database import SessionLocal, init_db
from app.seed import SEED_PROJECTS


def main() -> None:
    init_db()
    with SessionLocal() as db:
        projects = replace_all_projects(db, SEED_PROJECTS)
    print(f"Seeded {len(projects)} learning projects.")


if __name__ == "__main__":
    main()
