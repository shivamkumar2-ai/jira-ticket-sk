# AI Learning Dashboard API (Python Backend)

FastAPI backend for the **AI Learning Dashboard / Project Tracker** frontend. Provides REST APIs with SQLite persistence, validation, search/filter, seed data, and tests.

## Tech stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2
- SQLite
- Pydantic v2
- Pytest + httpx TestClient

## Setup

### 1. Create virtual environment

```bash
cd server
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment variables

```bash
copy .env.example .env
```

Optional settings in `.env`:
- `DATABASE_URL` — default `sqlite:///./learning_dashboard.db`
- `CORS_ORIGINS` — default allows Vite dev server
- `API_HOST`, `API_PORT`

### 4. Initialize database (optional)

Tables are created automatically on startup. You can also run:

```bash
python -m scripts.init_db
python -m scripts.seed_db
```

Migration SQL for reference: `migrations/001_initial.sql`

## Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API base: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

On first startup, seed data is loaded automatically if the database is empty.

## Authentication

JWT bearer authentication protects all `/api/projects` routes.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Sign in |
| GET | `/api/auth/me` | Current user (requires token) |

**Demo account (seeded on startup):**
- Email: `demo@example.com`
- Password: `demo1234`

Set `JWT_SECRET` in `.env` for production.

## API endpoints

All project routes require `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/projects` | List projects (search/filter/sort) |
| GET | `/api/projects/stats` | Dashboard summary stats |
| GET | `/api/projects/{id}` | Get one project |
| POST | `/api/projects` | Create project |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |
| POST | `/api/projects/seed` | Reset to sample seed data |

### Query parameters (`GET /api/projects`)

| Param | Description |
|-------|-------------|
| `search` | Search title, description, tags, notes |
| `status` | `not_started`, `in_progress`, `completed` |
| `category` | e.g. `rag`, `agents`, `prompt_engineering` |
| `priority` | `low`, `medium`, `high` |
| `sort` | `updated_desc`, `updated_asc`, `title_asc`, `progress_desc`, `priority_desc` |

### Request/response shape

JSON uses camelCase aliases to match the React frontend:

```json
{
  "id": "seed-1",
  "title": "Prompt engineering fundamentals",
  "description": "...",
  "category": "prompt_engineering",
  "status": "in_progress",
  "priority": "high",
  "progress": 45,
  "tags": ["prompts", "basics"],
  "resourceUrl": "https://example.com",
  "notes": "",
  "createdAt": "2026-07-01T09:00:00.000Z",
  "updatedAt": "2026-07-10T14:30:00.000Z"
}
```

## Tests

```bash
pytest
```

## Project structure

```
server/
├── app/
│   ├── main.py          # FastAPI app, CORS, error handlers
│   ├── config.py        # Settings
│   ├── database.py      # SQLAlchemy engine/session
│   ├── models.py        # LearningProject model
│   ├── schemas.py       # Pydantic request/response models
│   ├── crud.py          # DB operations, search/filter
│   ├── seed.py          # Seed data
│   ├── constants.py     # Enums
│   └── routers/
│       ├── health.py
│       └── projects.py
├── migrations/
│   └── 001_initial.sql
├── scripts/
│   ├── init_db.py
│   └── seed_db.py
├── tests/
│   ├── test_projects.py
│   └── test_schemas.py
├── requirements.txt
└── README.md
```

## Connect frontend

Point the React client to `http://localhost:8000/api` (CORS is enabled for `http://localhost:5173`). The frontend currently uses `localStorage`; you can swap `useProjects` to call these APIs next.

## Error handling

- `422` — validation errors (field-level detail)
- `404` — project not found
- `500` — unexpected server errors
