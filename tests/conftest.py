"""
Pytest configuration and shared fixtures for BK25 tests
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, AsyncMock

# Add project root to Python path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.bk25 import BK25Core
from src.core.persona_manager import PersonaManager
from src.core.channel_manager import ChannelManager
from src.core.memory import ConversationMemory
from src.core.code_generator import CodeGenerator
from src.core.llm_integration import LLMManager
from src.core.prompt_engineering import PromptEngineer
from src.core.script_executor import ScriptExecutor
from src.core.execution_monitor import ExecutionMonitor
from src.config import config


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        "ollama_url": "http://localhost:11434",
        "model": "llama3.1:8b",
        "personas_path": "./personas",
        "max_conversations": 50,
        "max_messages_per_conversation": 25,
        "execution_timeout": 300,
        "log_level": "DEBUG"
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "success": True,
        "content": "This is a test response from the LLM",
        "error": None,
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "metadata": {
            "provider": "ollama",
            "model": "llama3.1:8b"
        }
    }


@pytest.fixture
def mock_persona_data():
    """Mock persona data for testing"""
    return {
        "id": "test-persona",
        "name": "Test Persona",
        "description": "A test persona for unit testing",
        "greeting": "Hello! I'm a test persona.",
        "capabilities": ["testing", "debugging"],
        "personality": {
            "tone": "professional",
            "approach": "systematic",
            "philosophy": "testing",
            "motto": "Test everything"
        },
        "examples": ["Test example 1", "Test example 2"],
        "channels": ["web", "cli"],
        "system_prompt": "You are a test persona focused on testing and debugging."
    }


@pytest.fixture
def mock_channel_data():
    """Mock channel data for testing"""
    return {
        "id": "test-channel",
        "name": "Test Channel",
        "description": "A test channel for unit testing",
        "capabilities": {
            "text": {"supported": True, "description": "Text messaging"},
            "files": {"supported": False, "description": "File sharing"}
        },
        "artifact_types": ["text", "json"],
        "metadata": {"test": True}
    }


@pytest.fixture
def mock_conversation_data():
    """Mock conversation data for testing"""
    return {
        "id": "test-conversation",
        "persona_id": "test-persona",
        "channel_id": "test-channel",
        "messages": [
            {"role": "user", "content": "Hello", "timestamp": "2025-01-27T10:00:00Z"},
            {"role": "assistant", "content": "Hi there!", "timestamp": "2025-01-27T10:00:01Z"}
        ]
    }


@pytest.fixture
def mock_script_data():
    """Mock script data for testing"""
    return {
        "description": "Test script for unit testing",
        "platform": "powershell",
        "script": "Write-Host 'Hello from test script'",
        "filename": "test_script.ps1",
        "documentation": "This is a test script"
    }


@pytest.fixture
def mock_execution_request():
    """Mock execution request for testing"""
    return {
        "script": "echo 'Hello World'",
        "platform": "bash",
        "filename": "test.sh",
        "working_directory": "/tmp",
        "timeout": 60,
        "policy": "safe",
        "environment": {"TEST": "true"}
    }


@pytest.fixture
def mock_task_data():
    """Mock task data for testing"""
    return {
        "id": "test-task-123",
        "name": "Test Task",
        "description": "A test execution task",
        "script": "echo 'Hello World'",
        "platform": "bash",
        "priority": "normal",
        "tags": ["test", "unit"],
        "metadata": {"test": True}
    }


@pytest.fixture
async def mock_bk25_core(mock_config):
    """Create a mock BK25 core instance for testing"""
    core = BK25Core(mock_config)
    
    # Mock external dependencies
    core.ollama_connected = False
    core.llm_manager.test_providers = AsyncMock(return_value={"ollama": False})
    core.llm_manager.get_available_providers = Mock(return_value=["ollama"])
    
    # Mock persona manager
    core.persona_manager.get_all_personas = Mock(return_value=[])
    core.persona_manager.get_current_persona = Mock(return_value=None)
    
    # Mock channel manager
    core.channel_manager.get_all_channels = Mock(return_value=[])
    core.channel_manager.get_current_channel = Mock(return_value=None)
    
    # Mock code generator
    core.code_generator.get_supported_platforms = Mock(return_value=["powershell", "bash", "applescript"])
    
    # Mock execution monitor
    core.execution_monitor.start_monitoring = AsyncMock()
    core.execution_monitor.get_system_statistics = AsyncMock(return_value={})
    
    yield core


@pytest.fixture
def mock_persona_manager(mock_config):
    """Create a mock persona manager for testing"""
    pm = PersonaManager(mock_config.get("personas_path"))
    pm.get_all_personas = Mock(return_value=[])
    pm.get_current_persona = Mock(return_value=None)
    pm.get_personas_for_channel = Mock(return_value=[])
    pm.switch_persona = Mock(return_value=None)
    pm.add_custom_persona = Mock(return_value=None)
    return pm


@pytest.fixture
def mock_channel_manager():
    """Create a mock channel manager for testing"""
    cm = ChannelManager()
    cm.get_all_channels = Mock(return_value=[])
    cm.get_current_channel = Mock(return_value=None)
    cm.get_channel = Mock(return_value=None)
    cm.switch_channel = Mock(return_value=None)
    return cm


@pytest.fixture
def mock_memory(mock_config):
    """Create a mock conversation memory for testing"""
    memory = ConversationMemory(
        max_conversations=mock_config.get("max_conversations"),
        max_messages_per_conversation=mock_config.get("max_messages_per_conversation")
    )
    memory.get_conversation = Mock(return_value=None)
    memory.get_conversation_context = Mock(return_value="")
    memory.get_all_conversations = Mock(return_value=[])
    memory.get_all_conversation_summaries = Mock(return_value=[])
    return memory


@pytest.fixture
def mock_code_generator():
    """Create a mock code generator for testing"""
    cg = CodeGenerator()
    cg.get_supported_platforms = Mock(return_value=["powershell", "bash", "applescript"])
    cg.get_generation_statistics = Mock(return_value={})
    cg.get_platform_info = Mock(return_value={})
    cg.get_automation_suggestions = Mock(return_value=[])
    return cg


@pytest.fixture
def mock_llm_manager(mock_config):
    """Create a mock LLM manager for testing"""
    lm = LLMManager(mock_config)
    lm.test_providers = AsyncMock(return_value={"ollama": False})
    lm.get_available_providers = Mock(return_value=["ollama"])
    lm.get_provider_info = Mock(return_value={})
    lm.generate = AsyncMock(return_value=Mock(success=True, content="Test response"))
    return lm


@pytest.fixture
def mock_prompt_engineer():
    """Create a mock prompt engineer for testing"""
    pe = PromptEngineer()
    pe.create_persona_prompt = Mock(return_value="Test prompt")
    pe.create_validation_prompt = Mock(return_value=Mock(system_message="Test", user_prompt="Test", output_format="Test"))
    pe.create_iterative_improvement_prompt = Mock(return_value=Mock(system_message="Test", user_prompt="Test", output_format="Test"))
    return pe


@pytest.fixture
def mock_script_executor(mock_config):
    """Create a mock script executor for testing"""
    se = ScriptExecutor(mock_config)
    se.execute_script = AsyncMock(return_value=Mock(
        success=True,
        status=Mock(value="completed"),
        output="Test output",
        error=None,
        exit_code=0,
        execution_time=1.0,
        memory_usage=1024,
        cpu_usage=1.0
    ))
    se.get_system_resources = Mock(return_value={
        "cpu_count": 4,
        "memory_total": 8192,
        "memory_available": 4096
    })
    return se


@pytest.fixture
def mock_execution_monitor(mock_config):
    """Create a mock execution monitor for testing"""
    em = ExecutionMonitor(mock_config)
    em.start_monitoring = AsyncMock()
    em.shutdown = AsyncMock()
    em.submit_task = AsyncMock(return_value="test-task-123")
    em.get_task_status = AsyncMock(return_value=Mock(
        id="test-task-123",
        name="Test Task",
        description="Test description",
        status=Mock(value="completed"),
        priority=Mock(value="normal"),
        created_at=None,
        started_at=None,
        completed_at=None,
        execution_time=1.0,
        exit_code=0,
        output="Test output",
        error=None,
        tags=["test"],
        metadata={"test": True}
    ))
    em.get_execution_history = AsyncMock(return_value=[])
    em.get_system_statistics = AsyncMock(return_value={})
    em.get_running_tasks = AsyncMock(return_value=[])
    em.cancel_task = AsyncMock(return_value=True)
    return em


@pytest.fixture
def test_data_dir(temp_dir):
    """Create test data directory with sample files"""
    # Create personas directory
    personas_dir = temp_dir / "personas"
    personas_dir.mkdir()
    
    # Create sample persona file
    persona_file = personas_dir / "test-persona.json"
    persona_file.write_text('''{
        "id": "test-persona",
        "name": "Test Persona",
        "description": "A test persona for unit testing",
        "greeting": "Hello! I'm a test persona.",
        "capabilities": ["testing", "debugging"],
        "personality": {
            "tone": "professional",
            "approach": "systematic",
            "philosophy": "testing",
            "motto": "Test everything"
        },
        "examples": ["Test example 1", "Test example 2"],
        "channels": ["web", "cli"],
        "system_prompt": "You are a test persona focused on testing and debugging."
    }''')
    
    # Create channels directory
    channels_dir = temp_dir / "channels"
    channels_dir.mkdir()
    
    # Create sample channel file
    channel_file = channels_dir / "test-channel.json"
    channel_file.write_text('''{
        "id": "test-channel",
        "name": "Test Channel",
        "description": "A test channel for unit testing",
        "capabilities": {
            "text": {"supported": true, "description": "Text messaging"},
            "files": {"supported": false, "description": "File sharing"}
        },
        "artifact_types": ["text", "json"],
        "metadata": {"test": true}
    }''')
    
    yield temp_dir


@pytest.fixture
def mock_fastapi_app():
    """Mock FastAPI app for testing"""
    from fastapi import FastAPI
    app = FastAPI(title="Test BK25 API")
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    @app.get("/api/personas")
    async def get_personas():
        return {"personas": [], "total_count": 0}
    
    return app


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing HTTP requests"""
    client = Mock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.__aenter__ = Mock(return_value=client)
    client.__aexit__ = AsyncMock()
    return client


# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests for complete workflows"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and stress tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "api: API endpoint tests"
    )
    config.addinivalue_line(
        "markers", "web: Web interface tests"
    )
