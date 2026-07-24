# AI Learning Dashboard (Frontend)

Frontend-heavy competency exercise: an **AI Learning Dashboard / Project Tracker** built with React and Vite, connected to the Python FastAPI backend.

## Project choice

- **Track:** Frontend-heavy — AI Learning Dashboard / Project Tracker
- **Persistence:** Python API + SQLite (`server/`)

## Features (Core)

| Area | Implementation |
|------|----------------|
| Dashboard | Summary stats: total, in progress, completed, not started, average progress |
| CRUD | Create, edit, delete learning items |
| Search & filter | Search across title, description, tags, notes; filter by status, category, priority; sort options |
| Validation | Required fields, length limits, progress range, URL format, tag limits |
| Error handling | API errors, load retry, form errors, error boundary, toast notifications |
| Seed data | Loaded from backend on first API startup; reset via UI |
| Tests | Vitest unit tests for validation, filters, and key UI components |

## Tech stack

- React 19
- Vite 8
- Vitest + Testing Library
- CSS (no UI framework — keeps dependencies minimal)

## Getting started

### Prerequisites

- Node.js 18+
- npm
- Python backend running on port 8000 (see `server/README.md`)

### Authentication

- Sign in / Sign up screen on first visit
- JWT stored in `localStorage`
- Demo account: `demo@example.com` / `demo1234`

### Install and run

**Terminal 1 — backend:**
```bash
cd server
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend:**
```bash
cd client
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api` to `http://127.0.0.1:8000`.

Optional: copy `.env.example` to `.env` and set `VITE_API_BASE_URL` if needed.

### Scripts

```bash
npm run dev        # Start dev server
npm run build      # Production build
npm run preview    # Preview production build
npm run test       # Run tests once
npm run test:watch # Run tests in watch mode
npm run lint       # Lint with oxlint
```

## Data model

Each learning item includes:

- `title`, `description`
- `category` (prompt engineering, agents, RAG, etc.)
- `status` (not started, in progress, completed)
- `priority` (low, medium, high)
- `progress` (0–100)
- `tags`, `resourceUrl`, `notes`
- `createdAt`, `updatedAt`

Storage is handled by the backend API. The client calls:

- `GET /api/projects` — list with search/filter/sort
- `GET /api/projects/stats` — dashboard stats
- `POST /api/projects` — create
- `PUT /api/projects/{id}` — update
- `DELETE /api/projects/{id}` — delete
- `POST /api/projects/seed` — reset sample data

## Project structure

```
client/
├── src/
│   ├── components/     # UI components
│   ├── constants/      # Enums and labels
│   ├── data/           # Seed data
│   ├── api/            # API client (fetch wrapper + projects)
│   ├── hooks/          # useProjects state/logic
│   ├── utils/          # storage, validation, filters
│   └── test/           # Test setup
├── docs/
│   ├── AI_WORKFLOW.md
│   ├── REFLECTION.md
│   └── PR_DESCRIPTION.md
└── README.md
```

## AI-assisted workflow

See [docs/AI_WORKFLOW.md](./docs/AI_WORKFLOW.md) for how Cursor was used to plan, generate, refine, test, and document this project.

## Reflection

See [docs/REFLECTION.md](./docs/REFLECTION.md).

## Notes for reviewers

- Frontend talks to the Python API in `server/` via Vite dev proxy.
- Start both servers for full-stack local testing.
- Authentication is intentionally omitted.
