import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_headers, client, login_user, register_user


def test_login_invalid_password(client: TestClient):
    register_user(client, "badlogin@example.com", "password123")
    response = login_user(client, "badlogin@example.com", "wrong-password")
    assert response.status_code == 401


def test_me_endpoint(client: TestClient):
    headers = auth_headers(client, "me@example.com", "password123")
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
