import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_user(client: TestClient, email: str = "user@example.com", password: str = "password123"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": "Test User"},
    )


def login_user(client: TestClient, email: str = "user@example.com", password: str = "password123"):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def auth_headers(client: TestClient, email: str = "user@example.com", password: str = "password123"):
    response = register_user(client, email, password)
    if response.status_code == 409:
        response = login_user(client, email, password)
    assert response.status_code in (200, 201)
    token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}
