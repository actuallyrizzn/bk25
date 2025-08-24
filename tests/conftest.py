"""
Test configuration and fixtures for BK25.
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bk25.core.bk25_core import BK25Core
from bk25.core.memory import ConversationMemory
from bk25.core.persona_manager import PersonaManager
from bk25.core.channel_manager import ChannelManager


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_bk25.db"
    
    yield str(db_path)
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
async def memory(temp_db):
    """Create a ConversationMemory instance for testing."""
    memory = ConversationMemory(temp_db)
    await memory.initialize_database()
    yield memory
    await memory.close()


@pytest.fixture
def persona_manager():
    """Create a PersonaManager instance for testing."""
    manager = PersonaManager()
    # Create a fallback persona for testing
    manager.create_fallback_persona()
    return manager


@pytest.fixture
def channel_manager():
    """Create a ChannelManager instance for testing."""
    return ChannelManager()


@pytest.fixture
async def bk25_core(temp_db):
    """Create a BK25Core instance for testing."""
    config = {
        "ollama_url": "http://localhost:11434",
        "model": "test-model",
        "temperature": 0.1,
        "max_tokens": 100
    }
    
    core = BK25Core(config)
    # Override the database path for testing
    core.memory.db_path = temp_db
    
    # Don't initialize Ollama connection for tests
    core.ollama_connected = False
    
    await core.memory.initialize_database()
    await core.persona_manager.initialize()
    
    yield core
    
    await core.close()


@pytest.fixture
def sample_persona_data():
    """Sample persona data for testing."""
    return {
        "id": "test-persona",
        "name": "Test Persona",
        "description": "A test persona for unit testing",
        "greeting": "Hello! I'm a test persona.",
        "systemPrompt": "You are a helpful test assistant.",
        "capabilities": ["Testing", "Validation"],
        "examples": ["Run tests", "Validate functionality"],
        "channels": ["web", "test"]
    }


@pytest.fixture
def sample_automation():
    """Sample automation data for testing."""
    return {
        "platform": "powershell",
        "description": "Test automation script",
        "script": "Write-Host 'Hello, World!'",
        "documentation": "A simple test script",
        "filename": "test_script.ps1"
    }