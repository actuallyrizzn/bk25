import os
os.environ["BK25_MOCK"] = "1"

from fastapi.testclient import TestClient
from bk25.server import create_app


def get_client():
    app = create_app()
    return TestClient(app)


def test_health_and_personas():
    client = get_client()
    r = client.get("/health")
    assert r.status_code == 200
    r = client.get("/api/personas")
    assert r.status_code == 200


def test_chat_and_generate():
    client = get_client()
    r = client.post("/api/chat", json={"message": "hello"})
    assert r.status_code == 200
    r = client.post("/api/generate", json={"description": "create a script to echo hi", "platform": "bash"})
    assert r.status_code == 200
    data = r.json()
    assert data["platform"] == "bash"


def test_channels_switch_and_artifact():
    client = get_client()
    r = client.post("/api/channels/switch", json={"channelId": "slack"})
    assert r.status_code == 200
    r = client.post(
        "/api/channels/generate-artifact",
        json={"artifactType": "block-kit", "description": "demo"},
    )
    assert r.status_code == 200
