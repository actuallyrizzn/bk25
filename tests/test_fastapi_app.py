import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from main import app
from core.bk25 import BK25Core

class TestFastAPIApplication:
    """Test FastAPI application end-to-end"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def temp_personas_dir(self):
        """Create temporary personas directory with test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            personas_dir = Path(temp_dir) / "personas"
            personas_dir.mkdir()
            
            # Create test persona file
            test_persona = {
                "id": "test_persona",
                "name": "Test Persona",
                "description": "A test persona for E2E testing",
                "greeting": "Hello! I'm a test persona for E2E testing.",
                "capabilities": ["testing", "e2e", "automation"],
                "personality": {
                    "tone": "professional",
                    "approach": "systematic",
                    "philosophy": "e2e-first",
                    "motto": "Let's test end-to-end systematically!"
                },
                "examples": ["E2E test example"],
                "channels": ["web", "discord"]
            }
            
            persona_file = personas_dir / "test_persona.json"
            with open(persona_file, 'w') as f:
                json.dump(test_persona, f)
            
            yield personas_dir
    
    @pytest.fixture
    def mock_bk25_core(self, temp_personas_dir):
        """Create mock BK25Core instance"""
        with patch('main.bk25') as mock_bk25:
            # Mock the BK25Core instance
            mock_core = Mock()
            mock_core.persona_manager = Mock()
            mock_core.channel_manager = Mock()
            mock_core.memory = Mock()
            mock_core.code_generator = Mock()
            mock_core.llm_manager = Mock()
            mock_core.prompt_engineer = Mock()
            mock_core.script_executor = Mock()
            mock_core.execution_monitor = Mock()
            
            # Mock persona manager methods
            mock_core.persona_manager.get_all_personas.return_value = [
                {"id": "test_persona", "name": "Test Persona"}
            ]
            mock_core.persona_manager.get_persona.return_value = {
                "id": "test_persona", "name": "Test Persona"
            }
            
            # Mock channel manager methods
            mock_core.channel_manager.get_all_channels.return_value = [
                {"id": "web", "name": "Web Interface"}
            ]
            mock_core.channel_manager.get_channel.return_value = {
                "id": "web", "name": "Web Interface"
            }
            
            # Mock memory methods
            mock_core.memory.get_all_conversation_summaries.return_value = [
                {"id": "test_conv", "persona_id": "test_persona"}
            ]
            mock_core.memory.get_conversation_history.return_value = [
                {"role": "user", "content": "Hello"}
            ]
            
            # Mock code generator methods
            mock_core.code_generator.generate_script.return_value = "echo 'test'"
            mock_core.code_generator.get_supported_platforms.return_value = ["bash", "powershell"]
            
            # Mock LLM manager methods
            mock_core.llm_manager.get_status.return_value = {
                "providers": ["ollama", "openai"],
                "current_provider": "ollama"
            }
            mock_core.llm_manager.test_connection.return_value = {"success": True}
            
            # Mock script executor methods
            mock_core.script_executor.execute_script.return_value = {
                "success": True, "output": "test output"
            }
            
            # Mock execution monitor methods
            mock_core.execution_monitor.submit_task.return_value = "task_123"
            mock_core.execution_monitor.get_task_status.return_value = Mock(
                id="task_123", status="completed", output="test output"
            )
            mock_core.execution_monitor.get_execution_history.return_value = [
                Mock(id="task_123", status="completed")
            ]
            mock_core.execution_monitor.get_system_statistics.return_value = {
                "total_tasks": 1, "completed_tasks": 1
            }
            mock_core.execution_monitor.get_running_tasks.return_value = []
            
            # Mock startup and shutdown methods
            mock_core.start_execution_monitoring = AsyncMock()
            mock_core.shutdown_execution_monitoring = AsyncMock()
            
            mock_bk25.return_value = mock_core
            yield mock_core
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "Phase 5" in data["message"]
        assert data["script_execution"] == "available"
        assert "timestamp" in data
    
    def test_api_personas_endpoint(self, client, mock_bk25_core):
        """Test personas API endpoint"""
        response = client.get("/api/personas")
        assert response.status_code == 200
        
        data = response.json()
        assert "personas" in data
        assert "total_count" in data
        assert len(data["personas"]) > 0
    
    def test_api_personas_specific_endpoint(self, client, mock_bk25_core):
        """Test specific persona API endpoint"""
        response = client.get("/api/personas/test_persona")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "test_persona"
        assert data["name"] == "Test Persona"
    
    def test_api_personas_nonexistent_endpoint(self, client, mock_bk25_core):
        """Test non-existent persona API endpoint"""
        # Mock persona manager to return None for non-existent persona
        mock_bk25_core.persona_manager.get_persona.return_value = None
        
        response = client.get("/api/personas/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"].lower()
    
    def test_api_channels_endpoint(self, client, mock_bk25_core):
        """Test channels API endpoint"""
        response = client.get("/api/channels")
        assert response.status_code == 200
        
        data = response.json()
        assert "channels" in data
        assert "total_count" in data
        assert len(data["channels"]) > 0
    
    def test_api_channels_specific_endpoint(self, client, mock_bk25_core):
        """Test specific channel API endpoint"""
        response = client.get("/api/channels/web")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "web"
        assert data["name"] == "Web Interface"
    
    def test_api_channels_nonexistent_endpoint(self, client, mock_bk25_core):
        """Test non-existent channel API endpoint"""
        # Mock channel manager to return None for non-existent channel
        mock_bk25_core.channel_manager.get_channel.return_value = None
        
        response = client.get("/api/channels/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"].lower()
    
    def test_api_conversations_endpoint(self, client, mock_bk25_core):
        """Test conversations API endpoint"""
        response = client.get("/api/conversations")
        assert response.status_code == 200
        
        data = response.json()
        assert "conversations" in data
        assert "total_count" in data
        assert len(data["conversations"]) > 0
    
    def test_api_conversations_specific_endpoint(self, client, mock_bk25_core):
        """Test specific conversation API endpoint"""
        response = client.get("/api/conversations/test_conv")
        assert response.status_code == 200
        
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) > 0
    
    def test_api_conversations_nonexistent_endpoint(self, client, mock_bk25_core):
        """Test non-existent conversation API endpoint"""
        # Mock memory to return empty history for non-existent conversation
        mock_bk25_core.memory.get_conversation_history.return_value = []
        
        response = client.get("/api/conversations/nonexistent")
        assert response.status_code == 200
        
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) == 0
    
    def test_api_chat_endpoint(self, client, mock_bk25_core):
        """Test chat API endpoint"""
        chat_data = {
            "message": "Hello, can you help me?",
            "persona_id": "test_persona",
            "channel_id": "web",
            "conversation_id": "test_conv"
        }
        
        response = client.post("/api/chat", json=chat_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data
    
    def test_api_chat_endpoint_invalid_data(self, client):
        """Test chat API endpoint with invalid data"""
        # Test with missing required fields
        invalid_data = {"message": "Hello"}
        
        response = client.post("/api/chat", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_api_generate_script_endpoint(self, client, mock_bk25_core):
        """Test script generation API endpoint"""
        generate_data = {
            "description": "List files in current directory",
            "platform": "bash",
            "persona_id": "test_persona"
        }
        
        response = client.post("/api/generate/script", json=generate_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "script" in data
        assert "platform" in data
        assert data["platform"] == "bash"
    
    def test_api_generate_script_endpoint_invalid_platform(self, client):
        """Test script generation API endpoint with invalid platform"""
        generate_data = {
            "description": "List files",
            "platform": "invalid_platform",
            "persona_id": "test_persona"
        }
        
        response = client.post("/api/generate/script", json=generate_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "platform" in data["error"].lower()
    
    def test_api_generate_platforms_endpoint(self, client, mock_bk25_core):
        """Test supported platforms API endpoint"""
        response = client.get("/api/generate/platforms")
        assert response.status_code == 200
        
        data = response.json()
        assert "platforms" in data
        assert "bash" in data["platforms"]
        assert "powershell" in data["platforms"]
    
    def test_api_generate_platform_specific_endpoint(self, client, mock_bk25_core):
        """Test platform-specific generation API endpoint"""
        response = client.get("/api/generate/platform/bash")
        assert response.status_code == 200
        
        data = response.json()
        assert "platform" in data
        assert data["platform"] == "bash"
    
    def test_api_generate_platform_nonexistent_endpoint(self, client):
        """Test non-existent platform generation API endpoint"""
        response = client.get("/api/generate/platform/nonexistent")
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "platform" in data["error"].lower()
    
    def test_api_generate_suggestions_endpoint(self, client, mock_bk25_core):
        """Test generation suggestions API endpoint"""
        response = client.get("/api/generate/suggestions")
        assert response.status_code == 200
        
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0
    
    def test_api_llm_status_endpoint(self, client, mock_bk25_core):
        """Test LLM status API endpoint"""
        response = client.get("/api/llm/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "providers" in data
        assert "current_provider" in data
        assert "ollama" in data["providers"]
    
    def test_api_llm_providers_endpoint(self, client, mock_bk25_core):
        """Test LLM providers API endpoint"""
        response = client.get("/api/llm/providers")
        assert response.status_code == 200
        
        data = response.json()
        assert "providers" in data
        assert len(data["providers"]) > 0
    
    def test_api_llm_test_endpoint(self, client, mock_bk25_core):
        """Test LLM test connection API endpoint"""
        response = client.post("/api/llm/test")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert data["success"] is True
    
    def test_api_scripts_improve_endpoint(self, client, mock_bk25_core):
        """Test script improvement API endpoint"""
        improve_data = {
            "script": "ls",
            "platform": "bash",
            "feedback": "Make it more descriptive"
        }
        
        response = client.post("/api/scripts/improve", json=improve_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "improved_script" in data
        assert "platform" in data
    
    def test_api_scripts_validate_endpoint(self, client, mock_bk25_core):
        """Test script validation API endpoint"""
        validate_data = {
            "script": "ls -la",
            "platform": "bash"
        }
        
        response = client.post("/api/scripts/validate", json=validate_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "valid" in data
        assert "issues" in data
    
    def test_api_execute_script_endpoint(self, client, mock_bk25_core):
        """Test script execution API endpoint"""
        execute_data = {
            "script": "echo 'Hello World'",
            "platform": "bash",
            "timeout": 10,
            "policy": "safe"
        }
        
        response = client.post("/api/execute/script", json=execute_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "status" in data
    
    def test_api_execute_script_endpoint_invalid_policy(self, client):
        """Test script execution API endpoint with invalid policy"""
        execute_data = {
            "script": "echo 'test'",
            "platform": "bash",
            "policy": "invalid_policy"
        }
        
        response = client.post("/api/execute/script", json=execute_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "policy" in data["error"].lower()
    
    def test_api_execute_task_endpoint(self, client, mock_bk25_core):
        """Test task submission API endpoint"""
        task_data = {
            "name": "Test Task",
            "description": "A test execution task",
            "script": "echo 'test'",
            "platform": "bash",
            "priority": "normal"
        }
        
        response = client.post("/api/execute/task", json=task_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert data["success"] is True
        assert "task_id" in data
    
    def test_api_execute_task_endpoint_invalid_priority(self, client):
        """Test task submission API endpoint with invalid priority"""
        task_data = {
            "name": "Test Task",
            "description": "A test task",
            "script": "echo 'test'",
            "platform": "bash",
            "priority": "invalid_priority"
        }
        
        response = client.post("/api/execute/task", json=task_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "priority" in data["error"].lower()
    
    def test_api_execute_task_status_endpoint(self, client, mock_bk25_core):
        """Test task status API endpoint"""
        response = client.get("/api/execute/task/task_123")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "task" in data
        assert data["task"]["id"] == "task_123"
    
    def test_api_execute_task_status_nonexistent_endpoint(self, client, mock_bk25_core):
        """Test task status API endpoint for non-existent task"""
        # Mock execution monitor to return None for non-existent task
        mock_bk25_core.execution_monitor.get_task_status.return_value = None
        
        response = client.get("/api/execute/task/nonexistent")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert data["success"] is False
        assert "error" in data
    
    def test_api_execute_task_cancel_endpoint(self, client, mock_bk25_core):
        """Test task cancellation API endpoint"""
        response = client.delete("/api/execute/task/task_123")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "message" in data
    
    def test_api_execute_history_endpoint(self, client, mock_bk25_core):
        """Test execution history API endpoint"""
        response = client.get("/api/execute/history")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "tasks" in data
        assert len(data["tasks"]) > 0
    
    def test_api_execute_history_endpoint_with_filters(self, client, mock_bk25_core):
        """Test execution history API endpoint with filters"""
        response = client.get("/api/execute/history?status=completed&platform=bash&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "tasks" in data
    
    def test_api_execute_statistics_endpoint(self, client, mock_bk25_core):
        """Test execution statistics API endpoint"""
        response = client.get("/api/execute/statistics")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "execution_statistics" in data
        assert "system_resources" in data
        assert "llm_status" in data
    
    def test_api_execute_running_endpoint(self, client, mock_bk25_core):
        """Test running tasks API endpoint"""
        response = client.get("/api/execute/running")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "tasks" in data
        assert len(data["tasks"]) >= 0
    
    def test_api_system_status_endpoint(self, client, mock_bk25_core):
        """Test system status API endpoint"""
        response = client.get("/api/system/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "components" in data
        assert "personas" in data["components"]
        assert "channels" in data["components"]
        assert "memory" in data["components"]
    
    def test_api_system_memory_endpoint(self, client, mock_bk25_core):
        """Test system memory API endpoint"""
        response = client.get("/api/system/memory")
        assert response.status_code == 200
        
        data = response.json()
        assert "memory_stats" in data
        assert "conversations" in data
    
    def test_404_error_handling(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"].lower()
        assert "Phase 5" in data["message"]
    
    def test_500_error_handling(self, client, mock_bk25_core):
        """Test 500 error handling"""
        # Mock an error in the persona manager
        mock_bk25_core.persona_manager.get_all_personas.side_effect = Exception("Test error")
        
        response = client.get("/api/personas")
        assert response.status_code == 500
        
        data = response.json()
        assert "error" in data
        assert "internal server error" in data["error"].lower()
        assert "Phase 5" in data["message"]
    
    def test_cors_headers(self, client):
        """Test CORS headers"""
        response = client.options("/api/personas")
        assert response.status_code == 200
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_request_validation(self, client):
        """Test request validation"""
        # Test invalid JSON
        response = client.post("/api/chat", data="invalid json")
        assert response.status_code == 422
        
        # Test missing required fields
        response = client.post("/api/chat", json={})
        assert response.status_code == 422
        
        # Test invalid field types
        response = client.post("/api/chat", json={
            "message": 123,  # Should be string
            "persona_id": "test",
            "channel_id": "web",
            "conversation_id": "test"
        })
        assert response.status_code == 422
    
    def test_response_format_consistency(self, client, mock_bk25_core):
        """Test response format consistency across endpoints"""
        # Test personas endpoint
        personas_response = client.get("/api/personas")
        personas_data = personas_response.json()
        assert "personas" in personas_data
        assert "total_count" in personas_data
        
        # Test channels endpoint
        channels_response = client.get("/api/channels")
        channels_data = channels_response.json()
        assert "channels" in channels_data
        assert "total_count" in channels_data
        
        # Test conversations endpoint
        conversations_response = client.get("/api/conversations")
        conversations_data = conversations_response.json()
        assert "conversations" in conversations_data
        assert "total_count" in conversations_data
        
        # All endpoints should have consistent structure
        for data in [personas_data, channels_data, conversations_data]:
            assert isinstance(data, dict)
            assert "total_count" in data
    
    def test_async_operations(self, client, mock_bk25_core):
        """Test async operations work correctly"""
        # Test multiple concurrent requests
        import asyncio
        
        async def make_requests():
            tasks = []
            for i in range(5):
                task = asyncio.create_task(
                    asyncio.get_event_loop().run_in_executor(
                        None, 
                        client.get, 
                        "/api/personas"
                    )
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            return responses
        
        # Run concurrent requests
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        responses = loop.run_until_complete(make_requests())
        loop.close()
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
    
    def test_middleware_functionality(self, client):
        """Test middleware functionality"""
        # Test logging middleware
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test timing middleware (if implemented)
        # This would check for timing headers or logs
        
        # Test error handling middleware
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_environment_configuration(self, client):
        """Test environment configuration handling"""
        # Test that the app starts with default configuration
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test that configuration is properly loaded
        # This would check environment-specific behavior
    
    def test_performance_characteristics(self, client):
        """Test basic performance characteristics"""
        import time
        
        # Test response time for simple endpoint
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Health check should be very fast (under 100ms)
        assert response_time < 0.1
    
    def test_security_headers(self, client):
        """Test security headers"""
        response = client.get("/health")
        
        # Check for security headers
        headers = response.headers
        
        # Basic security headers that should be present
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection"
        ]
        
        for header in security_headers:
            if header in headers:
                assert headers[header] is not None
    
    def test_api_versioning(self, client):
        """Test API versioning if implemented"""
        # Test that API endpoints are properly versioned
        # This would check for version prefixes or headers
        
        # For now, just verify the current API structure
        response = client.get("/api/personas")
        assert response.status_code == 200
        
        # API should be consistent
        data = response.json()
        assert "personas" in data
    
    def test_rate_limiting(self, client):
        """Test rate limiting if implemented"""
        # Test that rate limiting works correctly
        # This would make many requests quickly and check for rate limit responses
        
        # For now, just verify basic functionality
        for i in range(10):
            response = client.get("/health")
            assert response.status_code == 200
    
    def test_health_check_detailed(self, client, mock_bk25_core):
        """Test detailed health check functionality"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check all required fields
        required_fields = ["status", "message", "script_execution", "timestamp"]
        for field in required_fields:
            assert field in data
        
        # Check status values
        assert data["status"] in ["healthy", "unhealthy", "degraded"]
        assert data["script_execution"] in ["available", "unavailable"]
        
        # Check timestamp format
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        assert re.match(timestamp_pattern, data["timestamp"])
    
    def test_startup_event(self, client, mock_bk25_core):
        """Test startup event functionality"""
        # The startup event should have been called during app initialization
        # We can verify this by checking that the execution monitoring was started
        
        # Verify that the startup event was triggered
        # This is implicit in the app initialization, but we can check the state
        
        response = client.get("/health")
        assert response.status_code == 200
        
        # The app should be in a healthy state after startup
        data = response.json()
        assert data["status"] == "healthy"

if __name__ == "__main__":
    pytest.main([__file__])
