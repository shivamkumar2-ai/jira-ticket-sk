from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.rag.exceptions import RagConfigurationError, RagRateLimitError, RagServiceError
from app.rag.indexer import sync_embeddings
from app.rag.model_registry import list_model_catalog_payload
from app.rag.service import ask_workspace_question, get_rag_status
from app.schemas import (
    RagAskRequest,
    RagAskResponse,
    RagIndexResponse,
    RagModelsResponse,
    RagStatusResponse,
)

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/status", response_model=RagStatusResponse)
def rag_status(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> RagStatusResponse:
    return RagStatusResponse(**get_rag_status(db))


@router.get("/models", response_model=RagModelsResponse)
def rag_models(
    _: User = Depends(get_current_user),
) -> RagModelsResponse:
    try:
        return RagModelsResponse(**list_model_catalog_payload())
    except RagConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except RagServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/index", response_model=RagIndexResponse)
def rag_index(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> RagIndexResponse:
    try:
        result = sync_embeddings(db)
    except RagConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except RagRateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except RagServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return RagIndexResponse(**result)


@router.post("/ask", response_model=RagAskResponse)
def rag_ask(
    payload: RagAskRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> RagAskResponse:
    try:
        result = ask_workspace_question(db, payload.question)
    except RagConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except RagRateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except RagServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return RagAskResponse(**result)
