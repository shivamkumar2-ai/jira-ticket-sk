from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./learning_dashboard.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    jwt_secret: str = "dev-only-change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
    demo_user_email: str = "demo@example.com"
    demo_user_password: str = "demo1234"
    demo_user_name: str = "Demo User"
    google_api_key: str = ""
    google_embedding_model: str = "gemini-embedding-001"
    google_chat_model: str = "gemini-3.5-flash"
    google_chat_model_fallbacks: str = "gemini-3.1-flash-lite,gemini-3-flash"
    google_api_max_retries: int = 2
    rag_top_k: int = 5

    @property
    def google_chat_model_list(self) -> list[str]:
        models: list[str] = []
        for value in [self.google_chat_model, *self.google_chat_model_fallbacks.split(",")]:
            model = value.strip()
            if model and model not in models:
                models.append(model)
        return models

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
