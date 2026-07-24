from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.database import engine


def _table_exists(connection, table_name: str) -> bool:
    row = connection.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name},
    ).fetchone()
    return row is not None


def _column_exists(connection, table_name: str, column_name: str) -> bool:
    rows = connection.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    return any(row[1] == column_name for row in rows)


def run_migrations(db_engine: Engine = engine) -> None:
    with db_engine.begin() as connection:
        if not _table_exists(connection, "users"):
            connection.execute(
                text(
                    """
                    CREATE TABLE users (
                        id VARCHAR(64) PRIMARY KEY,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        name VARCHAR(120) NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP NOT NULL
                    )
                    """
                )
            )
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)"))

        if _table_exists(connection, "learning_projects") and not _column_exists(
            connection,
            "learning_projects",
            "user_id",
        ):
            connection.execute(text("ALTER TABLE learning_projects ADD COLUMN user_id VARCHAR(64)"))
