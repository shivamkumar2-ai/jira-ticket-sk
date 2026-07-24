import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_headers, client, register_user


def test_list_users(client: TestClient):
    headers = auth_headers(client, "listusers1@example.com", "password123")
    register_user(client, "listusers2@example.com", "password123")

    response = client.get("/api/users", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 2
    assert all("name" in user and "email" in user for user in payload["items"])


def test_filter_projects_by_user(client: TestClient):
    headers_a = auth_headers(client, "usera@example.com", "password123")
    headers_b = auth_headers(client, "userb@example.com", "password123")

    me_a = client.get("/api/auth/me", headers=headers_a).json()
    me_b = client.get("/api/auth/me", headers=headers_b).json()

    client.post(
        "/api/projects",
        headers=headers_a,
        json={
            "title": "User A item",
            "description": "Owned by user A only.",
            "category": "task",
            "status": "in_progress",
            "priority": "medium",
            "progress": 10,
            "tags": [],
            "resourceUrl": "",
            "notes": "",
        },
    )

    only_b = client.get("/api/projects", headers=headers_b, params={"users": [me_b["id"]]})
    assert only_b.status_code == 200
    assert all(item["ownerId"] == me_b["id"] for item in only_b.json()["items"])

    both = client.get(
        "/api/projects",
        headers=headers_a,
        params=[("users", me_a["id"]), ("users", me_b["id"])],
    )
    assert both.status_code == 200
    owner_ids = {item["ownerId"] for item in both.json()["items"]}
    assert me_a["id"] in owner_ids
    assert "ownerName" in both.json()["items"][0]
