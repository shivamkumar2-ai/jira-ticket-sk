from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth import create_user, get_user_by_email
from app.config import settings
from app.crud import ProjectNotFoundError, replace_all_projects, user_has_projects
from app.database import SessionLocal, init_db
from app.migrate import run_migrations
from app.routers import auth, chat, health, projects, rag, users
from app.schemas import ErrorResponse
from app.seed import SEED_PROJECTS


def bootstrap_demo_user(db: Session) -> None:
    user = get_user_by_email(db, settings.demo_user_email)
    if not user:
        user = create_user(
            db,
            settings.demo_user_email,
            settings.demo_user_password,
            settings.demo_user_name,
        )

    if not user_has_projects(db, user.id):
        replace_all_projects(db, user.id, SEED_PROJECTS)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    run_migrations()
    with SessionLocal() as db:
        bootstrap_demo_user(db)
    yield


app = FastAPI(
    title="VeloDesk API",
    description="Backend API for the VeloDesk work coordination platform.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(rag.router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    errors: dict[str, list[str]] = {}
    for error in exc.errors():
        field = error["loc"][-1]
        if isinstance(field, str):
            errors.setdefault(field, []).append(error["msg"])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(detail=errors).model_dump(),
    )


@app.exception_handler(ProjectNotFoundError)
async def project_not_found_handler(_: Request, exc: ProjectNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(detail=str(exc)).model_dump(),
    )
