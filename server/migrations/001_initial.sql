-- Initial schema for AI Learning Dashboard
-- Applied automatically via SQLAlchemy metadata; kept for review and manual setup.

CREATE TABLE IF NOT EXISTS learning_projects (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    priority VARCHAR(16) NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    tags JSON NOT NULL,
    resource_url VARCHAR(2048) NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_learning_projects_category ON learning_projects (category);
CREATE INDEX IF NOT EXISTS ix_learning_projects_status ON learning_projects (status);
CREATE INDEX IF NOT EXISTS ix_learning_projects_priority ON learning_projects (priority);
