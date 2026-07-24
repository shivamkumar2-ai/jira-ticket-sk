-- Auth migration: users table and per-user projects

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- For existing databases created before auth:
-- ALTER TABLE learning_projects ADD COLUMN user_id VARCHAR(64);
