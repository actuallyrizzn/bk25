"""
Unit tests for BK25Core component
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.core.bk25 import BK25Core


class TestBK25Core:
    """Test BK25Core functionality"""

    @pytest.fixture
    def mock_config(self):
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
    def bk25_core(self, mock_config):
        """Create BK25Core instance for testing"""
        core = BK25Core(mock_config)
        
        # Mock external dependencies
        core.ollama_connected = False
        core.llm_manager.test_providers = AsyncMock(return_value={"ollama": False})
        core.llm_manager.get_available_providers = Mock(return_value=["ollama"])
        
        # Mock persona manager methods
        core.persona_manager.get_all_personas = Mock(return_value=[])
        core.persona_manager.get_current_persona = Mock(return_value=None)
        core.persona_manager.get_persona = Mock(return_value=None)
        core.persona_manager.switch_persona = Mock(return_value=None)
        core.persona_manager.reload_personas = AsyncMock()
        core.persona_manager.build_persona_prompt = Mock(return_value="Enhanced prompt")
        core.persona_manager.to_dict = Mock(return_value={"personas": [], "current": None})
        
        # Mock channel manager methods
        core.channel_manager.get_all_channels = Mock(return_value=[])
        core.channel_manager.get_current_channel = Mock(return_value=None)
        core.channel_manager.get_channel_summary = Mock(return_value={})
        core.channel_manager.switch_channel = Mock(return_value=None)
        core.channel_manager.get_channel_stats = Mock(return_value={"total": 3, "current": "web"})
        
        # Mock code generator methods
        core.code_generator.get_supported_platforms = Mock(return_value=["powershell", "bash", "applescript"])
        
        # Mock execution monitor methods
        core.execution_monitor.start_monitoring = AsyncMock()
        core.execution_monitor.get_system_statistics = AsyncMock(return_value={})
        core.execution_monitor.shutdown = AsyncMock()
        
        # Mock memory methods
        core.memory.get_memory_stats = Mock(return_value={"conversations": 0, "messages": 0})
        core.memory.get_conversation_history = Mock(return_value=[])
        core.memory.get_all_conversation_summaries = Mock(return_value=[])
        core.memory.get_conversation = Mock(return_value=None)
        core.memory.get_conversation_context = Mock(return_value="Context")
        core.memory.create_conversation = Mock(return_value=Mock(updated_at="2025-01-27T10:00:00Z"))
        
        return core

    def test_init(self, mock_config):
        """Test BK25Core initialization"""
        core = BK25Core(mock_config)
        
        assert core.config == mock_config
        assert core.ollama_url == "http://localhost:11434"
        assert core.model == "llama3.1:8b"
        assert core.temperature == 0.1
        assert core.max_tokens == 2048
        assert core.ollama_connected is False
        assert core.logger is not None

    def test_init_default_config(self):
        """Test BK25Core initialization with default config"""
        core = BK25Core()
        
        assert core.config == {}
        assert core.ollama_url == "http://localhost:11434"
        assert core.model == "llama3.1:8b"
        assert core.temperature == 0.1
        assert core.max_tokens == 2048

    @pytest.mark.asyncio
    async def test_initialize_success(self, bk25_core):
        """Test successful initialization"""
        # Mock persona manager initialization
        bk25_core.persona_manager.initialize = AsyncMock()
        
        # Mock Ollama connection test
        bk25_core.test_ollama_connection = AsyncMock(return_value=False)
        
        await bk25_core.initialize()
        
        # Verify components were initialized
        bk25_core.persona_manager.initialize.assert_called_once()
        bk25_core.test_ollama_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_failure(self, mock_config):
        """Test initialization failure"""
        core = BK25Core(mock_config)
        
        # Mock persona manager to raise exception
        core.persona_manager.initialize = AsyncMock(side_effect=Exception("Initialization failed"))
        
        with pytest.raises(Exception, match="Initialization failed"):
            await core.initialize()

    @pytest.mark.asyncio
    async def test_test_ollama_connection_success(self, bk25_core):
        """Test successful Ollama connection"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"models": []}
            
            mock_client_instance = Mock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            # Properly mock the async context manager
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await bk25_core.test_ollama_connection()
            
            assert result is True
            assert bk25_core.ollama_connected is True

    @pytest.mark.asyncio
    async def test_test_ollama_connection_failure(self, bk25_core):
        """Test failed Ollama connection"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.get.side_effect = Exception("Connection failed")
            # Properly mock the async context manager
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await bk25_core.test_ollama_connection()
            
            assert result is False
            assert bk25_core.ollama_connected is False

    @pytest.mark.asyncio
    async def test_test_ollama_connection_timeout(self, bk25_core):
        """Test Ollama connection timeout"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.get.side_effect = Exception("Timeout")
            # Properly mock the async context manager
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await bk25_core.test_ollama_connection()
            
            assert result is False
            assert bk25_core.ollama_connected is False

    def test_is_ollama_connected(self, bk25_core):
        """Test Ollama connection status check"""
        # Test disconnected
        bk25_core.ollama_connected = False
        assert bk25_core.is_ollama_connected() is False
        
        # Test connected
        bk25_core.ollama_connected = True
        assert bk25_core.is_ollama_connected() is True

    @pytest.mark.asyncio
    async def test_generate_completion_no_ollama(self, bk25_core):
        """Test completion generation without Ollama connection"""
        bk25_core.ollama_connected = False
        
        result = await bk25_core.generate_completion("Test prompt")
        
        assert "Ollama not connected" in result

    @pytest.mark.asyncio
    async def test_generate_completion_with_ollama(self, bk25_core):
        """Test completion generation with Ollama connection"""
        bk25_core.ollama_connected = True
        
        # Mock persona manager
        mock_persona = Mock()
        mock_persona.name = "Test Persona"
        bk25_core.persona_manager.get_current_persona.return_value = mock_persona
        bk25_core.persona_manager.build_persona_prompt.return_value = "Enhanced prompt"
        
        # Mock memory
        bk25_core.memory.get_conversation_context.return_value = "Context"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"response": "Generated response"}
            
            mock_client_instance = Mock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            # Properly mock the async context manager
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await bk25_core.generate_completion("Test prompt", "conv123")
            
            assert result == "Generated response"

    @pytest.mark.asyncio
    async def test_generate_completion_ollama_error(self, bk25_core):
        """Test completion generation with Ollama error"""
        bk25_core.ollama_connected = True
        
        # Mock persona manager
        mock_persona = Mock()
        bk25_core.persona_manager.get_current_persona.return_value = mock_persona
        bk25_core.persona_manager.build_persona_prompt.return_value = "Enhanced prompt"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            
            mock_client_instance = Mock()
            mock_client_instance.post = AsyncMock(return_value=mock_response)
            # Properly mock the async context manager
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await bk25_core.generate_completion("Test prompt")
            
            assert "Ollama API error: 500" in result

    @pytest.mark.asyncio
    async def test_process_message_success(self, bk25_core):
        """Test successful message processing"""
        # Mock persona manager
        mock_persona = Mock()
        mock_persona.id = "test-persona"
        mock_persona.name = "Test Persona"
        mock_persona.greeting = "Hello!"
        bk25_core.persona_manager.get_current_persona.return_value = mock_persona
        
        # Mock channel manager
        mock_channel = Mock()
        mock_channel.id = "test-channel"
        mock_channel.name = "Test Channel"
        bk25_core.channel_manager.get_current_channel.return_value = mock_channel
        
        # Mock memory
        bk25_core.memory.get_conversation.return_value = None
        bk25_core.memory.create_conversation.return_value = Mock(updated_at="2025-01-27T10:00:00Z")
        
        # Mock completion generation
        bk25_core.generate_completion = AsyncMock(return_value="Generated response")
        
        result = await bk25_core.process_message("Hello", "conv123")
        
        assert result["response"] == "Generated response"
        assert result["persona"]["id"] == "test-persona"
        assert result["channel"]["id"] == "test-channel"
        assert result["conversation_id"] == "conv123"

    @pytest.mark.asyncio
    async def test_process_message_with_persona_switch(self, bk25_core):
        """Test message processing with persona switching"""
        # Mock persona switching
        mock_persona = Mock()
        mock_persona.id = "new-persona"
        mock_persona.name = "New Persona"
        mock_persona.greeting = "Hello from new persona!"
        bk25_core.persona_manager.switch_persona.return_value = mock_persona
        bk25_core.persona_manager.get_current_persona.return_value = mock_persona
        
        # Mock channel manager
        mock_channel = Mock()
        mock_channel.id = "test-channel"
        mock_channel.name = "Test Channel"
        bk25_core.channel_manager.get_current_channel.return_value = mock_channel
        
        # Mock memory
        bk25_core.memory.get_conversation.return_value = None
        bk25_core.memory.create_conversation.return_value = Mock(updated_at="2025-01-27T10:00:00Z")
        
        # Mock completion generation
        bk25_core.generate_completion = AsyncMock(return_value="Generated response")
        
        result = await bk25_core.process_message("Hello", "conv123", persona_id="new-persona")
        
        # Verify persona was switched
        bk25_core.persona_manager.switch_persona.assert_called_once_with("new-persona")
        assert result["persona"]["id"] == "new-persona"

    @pytest.mark.asyncio
    async def test_process_message_with_channel_switch(self, bk25_core):
        """Test message processing with channel switching"""
        # Mock persona manager
        mock_persona = Mock()
        mock_persona.id = "test-persona"
        mock_persona.name = "Test Persona"
        mock_persona.greeting = "Hello!"
        bk25_core.persona_manager.get_current_persona.return_value = mock_persona
        
        # Mock channel switching
        mock_channel = Mock()
        mock_channel.id = "new-channel"
        mock_channel.name = "New Channel"
        bk25_core.channel_manager.switch_channel.return_value = mock_channel
        bk25_core.channel_manager.get_current_channel.return_value = mock_channel
        
        # Mock memory
        bk25_core.memory.get_conversation.return_value = None
        bk25_core.memory.create_conversation.return_value = Mock(updated_at="2025-01-27T10:00:00Z")
        
        # Mock completion generation
        bk25_core.generate_completion = AsyncMock(return_value="Generated response")
        
        result = await bk25_core.process_message("Hello", "conv123", channel_id="new-channel")
        
        # Verify channel was switched
        bk25_core.channel_manager.switch_channel.assert_called_once_with("new-channel")
        assert result["channel"]["id"] == "new-channel"

    @pytest.mark.asyncio
    async def test_process_message_error(self, bk25_core):
        """Test message processing error handling"""
        # Mock persona manager to raise exception
        bk25_core.persona_manager.get_current_persona.side_effect = Exception("Persona error")
        
        result = await bk25_core.process_message("Hello", "conv123")
        
        assert "error" in result
        assert "Persona error" in result["error"]
        assert "Sorry, I encountered an error" in result["response"]

    def test_get_system_status(self, bk25_core):
        """Test system status retrieval"""
        # Mock component methods
        bk25_core.persona_manager.get_all_personas.return_value = [Mock(), Mock()]  # 2 personas
        bk25_core.channel_manager.get_all_channels.return_value = [Mock(), Mock(), Mock()]  # 3 channels
        bk25_core.memory.conversations = {"conv1": Mock(), "conv2": Mock()}  # 2 conversations
        
        status = bk25_core.get_system_status()
        
        assert status["ollama_connected"] is False
        assert status["ollama_url"] == "http://localhost:11434"
        assert status["model"] == "llama3.1:8b"
        assert status["personas_loaded"] == 2
        assert status["channels_available"] == 3
        assert status["conversations_active"] == 2

    def test_get_persona_info(self, bk25_core):
        """Test persona information retrieval"""
        # Mock persona manager
        mock_persona = Mock()
        mock_persona.to_dict.return_value = {"id": "test", "name": "Test"}
        bk25_core.persona_manager.get_persona.return_value = mock_persona
        
        # Test getting specific persona
        result = bk25_core.get_persona_info("test-persona")
        assert result == {"id": "test", "name": "Test"}
        
        # Test getting all personas
        bk25_core.persona_manager.to_dict.return_value = {"personas": [], "current": None}
        result = bk25_core.get_persona_info()
        assert "personas" in result

    def test_get_channel_info(self, bk25_core):
        """Test channel information retrieval"""
        # Mock channel manager
        bk25_core.channel_manager.get_channel_summary.return_value = {"id": "test", "name": "Test"}
        bk25_core.channel_manager.get_channel_stats.return_value = {"total": 3, "current": "web"}
        
        # Test getting specific channel
        result = bk25_core.get_channel_info("test-channel")
        assert result == {"id": "test", "name": "Test"}
        
        # Test getting all channels
        result = bk25_core.get_channel_info()
        assert "total" in result

    def test_get_memory_info(self, bk25_core):
        """Test memory information retrieval"""
        # Mock memory
        bk25_core.memory.get_memory_stats.return_value = {"conversations": 5, "messages": 25}
        
        result = bk25_core.get_memory_info()
        
        assert result["conversations"] == 5
        assert result["messages"] == 25

    @pytest.mark.asyncio
    async def test_reload_personas(self, bk25_core):
        """Test persona reloading"""
        bk25_core.persona_manager.reload_personas = AsyncMock()
        
        await bk25_core.reload_personas()
        
        bk25_core.persona_manager.reload_personas.assert_called_once()

    def test_switch_persona(self, bk25_core):
        """Test persona switching"""
        # Mock persona manager
        mock_persona = Mock()
        mock_persona.to_dict.return_value = {"id": "new", "name": "New Persona"}
        bk25_core.persona_manager.switch_persona.return_value = mock_persona
        
        result = bk25_core.switch_persona("new-persona")
        
        assert result == {"id": "new", "name": "New Persona"}
        bk25_core.persona_manager.switch_persona.assert_called_once_with("new-persona")

    def test_switch_channel(self, bk25_core):
        """Test channel switching"""
        # Mock channel manager
        bk25_core.channel_manager.switch_channel.return_value = Mock()
        bk25_core.channel_manager.get_channel_summary.return_value = {"id": "new", "name": "New Channel"}
        
        result = bk25_core.switch_channel("new-channel")
        
        assert result == {"id": "new", "name": "New Channel"}
        bk25_core.channel_manager.switch_channel.assert_called_once_with("new-channel")

    def test_get_conversation_history(self, bk25_core):
        """Test conversation history retrieval"""
        # Mock memory
        mock_messages = [
            Mock(role="user", content="Hello", timestamp="2025-01-27T10:00:00Z", metadata={}),
            Mock(role="assistant", content="Hi!", timestamp="2025-01-27T10:00:01Z", metadata={})
        ]
        bk25_core.memory.get_conversation_history.return_value = mock_messages
        
        result = bk25_core.get_conversation_history("conv123", limit=10)
        
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello"
        assert result[1]["role"] == "assistant"
        assert result[1]["content"] == "Hi!"

    def test_get_all_conversations(self, bk25_core):
        """Test all conversations retrieval"""
        # Mock memory
        bk25_core.memory.get_all_conversation_summaries.return_value = [
            {"id": "conv1", "summary": "First conversation"},
            {"id": "conv2", "summary": "Second conversation"}
        ]
        
        result = bk25_core.get_all_conversations()
        
        assert len(result) == 2
        assert result[0]["id"] == "conv1"
        assert result[1]["id"] == "conv2"

    @pytest.mark.asyncio
    async def test_start_execution_monitoring(self, bk25_core):
        """Test execution monitoring start"""
        await bk25_core.start_execution_monitoring()
        
        bk25_core.execution_monitor.start_monitoring.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_execution_monitoring_error(self, bk25_core):
        """Test execution monitoring start error"""
        bk25_core.execution_monitor.start_monitoring.side_effect = Exception("Start failed")
        
        with pytest.raises(Exception, match="Start failed"):
            await bk25_core.start_execution_monitoring()

    @pytest.mark.asyncio
    async def test_shutdown_execution_monitoring(self, bk25_core):
        """Test execution monitoring shutdown"""
        await bk25_core.shutdown_execution_monitoring()
        
        bk25_core.execution_monitor.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_execution_monitoring_error(self, bk25_core):
        """Test execution monitoring shutdown error"""
        bk25_core.execution_monitor.shutdown.side_effect = Exception("Shutdown failed")
        
        with pytest.raises(Exception, match="Shutdown failed"):
            await bk25_core.shutdown_execution_monitoring()

    def test_config_validation(self, mock_config):
        """Test configuration validation"""
        core = BK25Core(mock_config)
        
        # Test that config values are properly set
        assert core.ollama_url == mock_config["ollama_url"]
        assert core.model == mock_config["model"]
        assert core.temperature == 0.1  # Default value
        assert core.max_tokens == 2048  # Default value

    def test_component_initialization(self, mock_config):
        """Test that all components are properly initialized"""
        core = BK25Core(mock_config)
        
        # Test that all required components exist
        assert core.persona_manager is not None
        assert core.channel_manager is not None
        assert core.memory is not None
        assert core.code_generator is not None
        assert core.llm_manager is not None
        assert core.prompt_engineer is not None
        assert core.script_executor is not None
        assert core.execution_monitor is not None

    def test_logging_setup(self, mock_config):
        """Test that logging is properly set up"""
        core = BK25Core(mock_config)
        
        assert core.logger is not None
        # Test that logger has expected methods
        assert hasattr(core.logger, 'info')
        assert hasattr(core.logger, 'error')
        assert hasattr(core.logger, 'warning')
        assert hasattr(core.logger, 'debug')
