from fastapi.testclient import TestClient

from tests.conftest import auth_headers, client


def test_chat_messages_round_trip(client: TestClient):
    headers_a = auth_headers(client, "chatuser1@example.com", "password123")
    headers_b = auth_headers(client, "chatuser2@example.com", "password123")

    empty = client.get("/api/chat/messages", headers=headers_a)
    assert empty.status_code == 200
    assert empty.json()["total"] == 0

    created = client.post(
        "/api/chat/messages",
        headers=headers_a,
        json={"content": "Hello team"},
    )
    assert created.status_code == 201
    payload = created.json()
    assert payload["content"] == "Hello team"
    assert payload["userName"]
    assert payload["userId"]

    listed = client.get("/api/chat/messages", headers=headers_b)
    assert listed.status_code == 200
    items = listed.json()["items"]
    assert len(items) == 1
    assert items[0]["content"] == "Hello team"

    invalid = client.post(
        "/api/chat/messages",
        headers=headers_b,
        json={"content": "   "},
    )
    assert invalid.status_code == 422
