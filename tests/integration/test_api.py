"""
Integration tests for the BK25 API endpoints.
"""

import pytest
import httpx
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bk25.main import app


class TestAPI:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "tagline" in data
        assert "ollama" in data
    
    def test_chat_endpoint_basic(self, client):
        """Test basic chat functionality."""
        request_data = {
            "message": "Hello, how are you?",
            "persona": "fallback",
            "channel": "web",
            "platform": "powershell"
        }
        
        response = client.post("/api/chat", json=request_data)
        
        # Should work even without Ollama (will be mocked or return error)
        assert response.status_code in [200, 500]  # 500 if Ollama not available
        
        if response.status_code == 200:
            data = response.json()
            assert "type" in data
            assert "message" in data
            assert "conversational" in data
    
    def test_chat_endpoint_validation(self, client):
        """Test chat endpoint validation."""
        # Missing message
        response = client.post("/api/chat", json={})
        assert response.status_code == 422  # Validation error
        
        # Invalid message type
        response = client.post("/api/chat", json={"message": 123})
        assert response.status_code == 422
    
    def test_personas_endpoints(self, client):
        """Test persona management endpoints."""
        # Get all personas
        response = client.get("/api/personas")
        assert response.status_code == 200
        
        personas = response.json()
        assert isinstance(personas, list)
        assert len(personas) > 0
        
        # Get current persona
        response = client.get("/api/personas/current")
        assert response.status_code == 200
        
        current = response.json()
        assert "id" in current
        assert "name" in current
    
    def test_switch_persona(self, client):
        """Test persona switching."""
        # Switch to fallback persona
        response = client.post("/api/personas/switch", params={"persona_id": "fallback"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "persona" in data
        
        # Try to switch to non-existent persona
        response = client.post("/api/personas/switch", params={"persona_id": "nonexistent"})
        assert response.status_code == 404
    
    def test_create_persona(self, client):
        """Test custom persona creation."""
        persona_data = {
            "name": "Test Persona",
            "description": "A test persona",
            "system_prompt": "You are a helpful test assistant.",
            "capabilities": ["Testing"],
            "examples": ["Run tests"]
        }
        
        response = client.post("/api/personas/create", json=persona_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "persona" in data
        assert data["persona"]["name"] == "Test Persona"
    
    def test_channels_endpoints(self, client):
        """Test channel management endpoints."""
        # Get all channels
        response = client.get("/api/channels")
        assert response.status_code == 200
        
        channels = response.json()
        assert isinstance(channels, list)
        assert len(channels) > 0
        
        # Check for expected channels
        channel_ids = [c["id"] for c in channels]
        assert "web" in channel_ids
        assert "slack" in channel_ids
        assert "discord" in channel_ids
        
        # Get current channel
        response = client.get("/api/channels/current")
        assert response.status_code == 200
        
        current = response.json()
        assert "id" in current
        assert "name" in current
    
    def test_switch_channel(self, client):
        """Test channel switching."""
        # Switch to slack channel
        response = client.post("/api/channels/switch", params={"channel_id": "slack"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "channel" in data
        assert data["channel"]["id"] == "slack"
        
        # Try to switch to non-existent channel
        response = client.post("/api/channels/switch", params={"channel_id": "nonexistent"})
        assert response.status_code == 404
    
    def test_generate_artifact(self, client):
        """Test channel artifact generation."""
        # First switch to web channel
        client.post("/api/channels/switch", params={"channel_id": "web"})
        
        # Generate HTML component
        response = client.post("/api/channels/generate-artifact", params={
            "artifact_type": "html-component",
            "description": "A test button component"
        })
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["channel"] == "web"
        assert data["artifact_type"] == "html-component"
        assert "artifact" in data
        assert "generated_at" in data
    
    def test_generate_artifact_validation(self, client):
        """Test artifact generation validation."""
        # Missing parameters
        response = client.post("/api/channels/generate-artifact", params={})
        assert response.status_code == 422  # Validation error
        
        # Switch to web channel and try unsupported artifact
        client.post("/api/channels/switch", params={"channel_id": "web"})
        
        response = client.post("/api/channels/generate-artifact", params={
            "artifact_type": "block-kit",  # Slack artifact, not web
            "description": "Test"
        })
        assert response.status_code == 400  # Bad request
    
    def test_stats_endpoint(self, client):
        """Test system statistics endpoint."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "ollama_connected" in data
        assert "model" in data
        assert "personas_loaded" in data
        assert "current_persona" in data
        assert "current_channel" in data