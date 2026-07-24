# VeloDesk

Full-stack work coordination platform for managing work items, team collaboration, and AI-assisted workspace search.

## Project structure

```
jira-ticket-sk/
├── client/          # React + Vite frontend
├── server/          # FastAPI + SQLite backend
└── README.md
```

| Folder | Stack | Purpose |
|--------|-------|---------|
| [`client/`](client/) | React 19, Vite 8, Vitest | Dashboard UI, auth, filters, chat sidebar |
| [`server/`](server/) | FastAPI, SQLAlchemy, SQLite | REST API, JWT auth, RAG, embeddings |

## Features

- **Work items** — Create, edit, delete with auto IDs (`VELODESK-{NUMBER}`)
- **Dashboard** — Stats for total, in progress, completed, and average progress
- **Search & filters** — Status, category, priority, sort, and **user checkboxes**
- **Auth** — Register, login, JWT sessions; demo account on first startup
- **Team chat** — Shared workspace messages in a toggleable right sidebar
- **VeloDesk AI (RAG)** — Ask questions about work items and chat history using Google Gemini
- **Tests** — Vitest (frontend) and Pytest (backend)

## Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- **npm**
- **Google AI API key** (optional, for AI chat in the sidebar)

## Quick start

### 1. Backend

```bash
cd server
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

**macOS/Linux:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `server/.env` and set at least:

```env
JWT_SECRET=your-secret-here
GOOGLE_API_KEY=your-google-ai-key   # optional, for AI tab
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/api/health  

### 2. Frontend

```bash
cd client
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api` to the backend.

### Demo login

| Field | Value |
|-------|-------|
| Email | `demo@example.com` |
| Password | `demo1234` |

## Environment variables

### Server (`server/.env`)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | SQLite path (default: `./learning_dashboard.db`) |
| `CORS_ORIGINS` | Allowed frontend origins |
| `JWT_SECRET` | Secret for signing JWT tokens |
| `GOOGLE_API_KEY` | Google AI Studio key for RAG |
| `GOOGLE_CHAT_MODEL` | Preferred chat model (auto-fallback if unavailable) |
| `GOOGLE_EMBEDDING_MODEL` | Embedding model (default: `gemini-embedding-001`) |

See [`server/.env.example`](server/.env.example) for all options.

### Client (`client/.env`)

Optional. Copy `client/.env.example` if you need a custom API base URL (`VITE_API_BASE_URL`).

## API overview

| Area | Endpoints |
|------|-----------|
| Auth | `POST /api/auth/register`, `login`, `GET /api/auth/me` |
| Work items | `GET/POST /api/projects`, `PUT/DELETE /api/projects/{id}` |
| Stats | `GET /api/projects/stats` |
| Users | `GET /api/users` |
| Chat | `GET/POST /api/chat/messages` |
| RAG | `GET /api/rag/status`, `GET /api/rag/models`, `POST /api/rag/ask`, `POST /api/rag/index` |

All routes except `/api/health` and auth register/login require `Authorization: Bearer <token>`.

## Scripts

### Frontend (`client/`)

```bash
npm run dev        # Dev server
npm run build      # Production build
npm run test       # Run tests
npm run lint       # Lint
```

### Backend (`server/`)

```bash
pytest             # Run tests
uvicorn app.main:app --reload --port 8000
```

## What is not committed

Each folder has its own `.gitignore`:

| Ignored | Folder |
|---------|--------|
| `node_modules/`, `dist/`, `.env` | `client/` |
| `.venv/`, `.env`, `*.db`, `__pycache__/` | `server/` |

After cloning, run `npm install` in `client/` and `pip install -r requirements.txt` in `server/`.

## Further reading

- [client/README.md](client/README.md) — Frontend details
- [server/README.md](server/README.md) — Backend API details

## License

Private project — add a license if you plan to open-source it.
