import os
os.environ["BK25_MOCK"] = "1"

from fastapi.testclient import TestClient
from bk25.server import create_app


def test_end_to_end_flow():
    client = TestClient(create_app())
    # Health
    assert client.get("/health").status_code == 200
    # Personas
    personas = client.get("/api/personas").json()
    # Switch channel
    assert client.post("/api/channels/switch", json={"channelId": "web"}).status_code == 200
    # Chat
    assert client.post("/api/chat", json={"message": "hello there"}).status_code == 200
    # Generate automation
    resp = client.post(
        "/api/generate", json={"description": "create a bash script to say hi", "platform": "bash"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["platform"] == "bash"
