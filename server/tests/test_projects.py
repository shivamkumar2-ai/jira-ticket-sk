import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_headers, register_user, login_user
from app.seed import SEED_PROJECTS


def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_and_login(client: TestClient):
    register_response = register_user(client, "new@example.com", "password123")
    assert register_response.status_code == 201
    body = register_response.json()
    assert body["accessToken"]
    assert body["user"]["email"] == "new@example.com"

    login_response = login_user(client, "new@example.com", "password123")
    assert login_response.status_code == 200


def test_projects_require_auth(client: TestClient):
    response = client.get("/api/projects")
    assert response.status_code == 401


def test_seed_and_list_projects(client: TestClient):
    headers = auth_headers(client, "seed@example.com", "password123")
    seed_response = client.post("/api/projects/seed", headers=headers)
    assert seed_response.status_code == 200
    payload = seed_response.json()
    assert payload["total"] == len(SEED_PROJECTS)

    list_response = client.get("/api/projects", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == len(SEED_PROJECTS)


def test_seed_is_idempotent(client: TestClient):
    headers = auth_headers(client, "reseed@example.com", "password123")

    first = client.post("/api/projects/seed", headers=headers)
    second = client.post("/api/projects/seed", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["total"] == len(SEED_PROJECTS)
    assert second.json()["total"] == len(SEED_PROJECTS)

    list_response = client.get("/api/projects", headers=headers)
    assert list_response.json()["total"] == len(SEED_PROJECTS)


def test_create_project_validation_error(client: TestClient):
    headers = auth_headers(client, "validation@example.com", "password123")
    response = client.post(
        "/api/projects",
        headers=headers,
        json={
            "title": "",
            "description": "",
            "category": "task",
            "status": "in_progress",
            "priority": "medium",
            "progress": 10,
            "tags": [],
            "resourceUrl": "",
            "notes": "",
        },
    )
    assert response.status_code == 422


def test_create_update_delete_project(client: TestClient):
    headers = auth_headers(client, "crud@example.com", "password123")
    client.post("/api/projects/seed", headers=headers)

    create_response = client.post(
        "/api/projects",
        headers=headers,
        json={
            "title": "Test work item",
            "description": "A test description for API coverage.",
            "category": "bug",
            "status": "not_started",
            "priority": "high",
            "progress": 5,
            "tags": ["test"],
            "resourceUrl": "https://example.com",
            "notes": "notes",
        },
    )
    assert create_response.status_code == 201
    project = create_response.json()
    project_id = project["id"]
    assert project_id.startswith("VELODESK-")

    update_response = client.put(
        f"/api/projects/{project_id}",
        headers=headers,
        json={
            **project,
            "progress": 80,
            "status": "in_progress",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["progress"] == 80

    delete_response = client.delete(f"/api/projects/{project_id}", headers=headers)
    assert delete_response.status_code == 200

    missing_response = client.get(f"/api/projects/{project_id}", headers=headers)
    assert missing_response.status_code == 404


def test_search_and_stats(client: TestClient):
    headers = auth_headers(client, "search@example.com", "password123")
    client.post("/api/projects/seed", headers=headers)

    search_response = client.get("/api/projects", headers=headers, params={"search": "filter"})
    assert search_response.status_code == 200
    titles = [item["title"] for item in search_response.json()["items"]]
    assert any("filter" in title.lower() for title in titles)

    stats_response = client.get("/api/projects/stats", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total"] == len(SEED_PROJECTS)
    assert "avgProgress" in stats
