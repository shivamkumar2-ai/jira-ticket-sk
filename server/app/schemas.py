from datetime import datetime
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import ProjectCategory, ProjectPriority, ProjectStatus


def _normalize_tags(value: list[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [tag.strip() for tag in value.split(",") if tag.strip()]
    return [tag.strip() for tag in value if tag.strip()]


class ProjectBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)
    category: ProjectCategory
    status: ProjectStatus
    priority: ProjectPriority
    progress: int = Field(ge=0, le=100)
    tags: list[str] = Field(default_factory=list, max_length=8)
    resource_url: str = Field(default="", alias="resourceUrl", max_length=2048)
    notes: str = Field(default="", max_length=1000)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("title", "description", "notes", "resource_url", mode="before")
    @classmethod
    def strip_strings(cls, value: str | None) -> str:
        return (value or "").strip()

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, value: list[str] | str | None) -> list[str]:
        return _normalize_tags(value)

    @field_validator("tags")
    @classmethod
    def validate_tag_lengths(cls, value: list[str]) -> list[str]:
        for tag in value:
            if len(tag) > 24:
                raise ValueError("Each tag must be 24 characters or fewer.")
        return value

    @field_validator("resource_url")
    @classmethod
    def validate_resource_url(cls, value: str) -> str:
        if value and not value.lower().startswith(("http://", "https://")):
            raise ValueError("Resource URL must start with http:// or https://.")
        return value


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: str
    owner_id: str = Field(alias="ownerId")
    owner_name: str = Field(alias="ownerName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int


class StatsResponse(BaseModel):
    total: int
    completed: int
    in_progress: int = Field(alias="inProgress")
    not_started: int = Field(alias="notStarted")
    avg_progress: int = Field(alias="avgProgress")

    model_config = ConfigDict(populate_by_name=True)


class MessageResponse(BaseModel):
    message: str


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=120)

    @field_validator("email", "name", mode="before")
    @classmethod
    def strip_values(cls, value: str) -> str:
        return value.strip()


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def strip_email(cls, value: str) -> str:
        return value.strip()


class UserResponse(BaseModel):
    id: str
    email: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int


class AuthResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    user: UserResponse

    model_config = ConfigDict(populate_by_name=True)


class ErrorResponse(BaseModel):
    detail: str | dict[str, list[str]]


def new_chat_message_id() -> str:
    return str(uuid4())


def new_embedding_id() -> str:
    return str(uuid4())


class RagAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

    @field_validator("question", mode="before")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return (value or "").strip()


class RagSourceResponse(BaseModel):
    source_type: str = Field(alias="sourceType")
    source_id: str = Field(alias="sourceId")
    content: str
    score: float

    model_config = ConfigDict(populate_by_name=True)


class RagAskResponse(BaseModel):
    answer: str
    sources: list[RagSourceResponse]
    indexed_count: int = Field(alias="indexedCount")
    configured: bool

    model_config = ConfigDict(populate_by_name=True)


class RagIndexResponse(BaseModel):
    indexed: int
    created: int
    updated: int
    removed: int
    sources: int


class RagModelInfo(BaseModel):
    name: str
    display_name: str = Field(alias="displayName")
    description: str = ""
    supported_actions: list[str] = Field(default_factory=list, alias="supportedActions")

    model_config = ConfigDict(populate_by_name=True)


class RagModelsResponse(BaseModel):
    chat_models: list[RagModelInfo] = Field(alias="chatModels")
    embedding_models: list[RagModelInfo] = Field(alias="embeddingModels")
    selected_chat_models: list[str] = Field(alias="selectedChatModels")
    selected_embedding_model: str = Field(alias="selectedEmbeddingModel")

    model_config = ConfigDict(populate_by_name=True)


class RagStatusResponse(BaseModel):
    configured: bool
    indexed_count: int = Field(alias="indexedCount")
    embedding_model: str = Field(alias="embeddingModel")
    chat_model: str = Field(alias="chatModel")
    selected_chat_models: list[str] = Field(default_factory=list, alias="selectedChatModels")

    model_config = ConfigDict(populate_by_name=True)


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content", mode="before")
    @classmethod
    def strip_content(cls, value: str) -> str:
        return (value or "").strip()


class ChatMessageResponse(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    user_name: str = Field(alias="userName")
    content: str
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ChatMessageListResponse(BaseModel):
    items: list[ChatMessageResponse]
    total: int
