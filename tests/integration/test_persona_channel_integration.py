"""
Integration tests for persona and channel interactions
"""

import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from src.core.persona_manager import PersonaManager
from src.core.channel_manager import ChannelManager
from src.core.bk25 import BK25Core


class TestPersonaChannelIntegration:
    """Test integration between persona and channel systems"""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for test files"""
        return tmp_path

    @pytest.fixture
    def personas_path(self, temp_dir):
        """Create personas directory with test data"""
        personas_dir = temp_dir / "personas"
        personas_dir.mkdir()
        
        # Create test persona files
        persona_data = [
            {
                "id": "web-persona",
                "name": "Web Persona",
                "description": "Persona for web interface",
                "greeting": "Hello from web!",
                "capabilities": ["web_automation", "ui_testing"],
                "personality": {
                    "tone": "friendly",
                    "approach": "helpful",
                    "philosophy": "web_first",
                    "motto": "Web automation made easy"
                },
                "examples": ["Create a web form", "Test a website"],
                "channels": ["web"],
                "systemPrompt": "You are a web automation expert."
            },
            {
                "id": "slack-persona",
                "name": "Slack Persona",
                "description": "Persona for Slack integration",
                "greeting": "Hello from Slack!",
                "capabilities": ["slack_automation", "team_collaboration"],
                "personality": {
                    "tone": "professional",
                    "approach": "collaborative",
                    "philosophy": "team_work",
                    "motto": "Better together"
                },
                "examples": ["Send Slack message", "Create channel"],
                "channels": ["slack"],
                "systemPrompt": "You are a Slack automation expert."
            },
            {
                "id": "multi-channel-persona",
                "name": "Multi-Channel Persona",
                "description": "Persona for multiple channels",
                "greeting": "Hello from multiple channels!",
                "capabilities": ["cross_platform", "integration"],
                "personality": {
                    "tone": "versatile",
                    "approach": "adaptive",
                    "philosophy": "platform_agnostic",
                    "motto": "Works everywhere"
                },
                "examples": ["Cross-platform script", "Multi-channel message"],
                "channels": ["web", "slack", "teams"],
                "systemPrompt": "You are a cross-platform automation expert."
            }
        ]
        
        for persona in persona_data:
            persona_file = personas_dir / f"{persona['id']}.json"
            persona_file.write_text(json.dumps(persona, indent=2))
        
        return str(personas_dir)

    @pytest.fixture
    def persona_manager(self, personas_path):
        """Create PersonaManager instance"""
        pm = PersonaManager(personas_path)
        # Initialize synchronously by running the async method in the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(pm.initialize())
            return pm
        finally:
            loop.close()

    @pytest.fixture
    def channel_manager(self):
        """Create ChannelManager instance"""
        return ChannelManager()

    @pytest.fixture
    def bk25_core(self, personas_path):
        """Create BK25Core instance with test data"""
        config = {
            "personas_path": personas_path,
            "ollama_url": "http://localhost:11434",
            "model": "llama3.1:8b"
        }
        
        core = BK25Core(config)
        
        # Mock external dependencies
        core.ollama_connected = False
        core.llm_manager.test_providers = AsyncMock(return_value={"ollama": False})
        core.llm_manager.get_available_providers = Mock(return_value=["ollama"])
        
        # Mock execution monitor
        core.execution_monitor.start_monitoring = AsyncMock()
        core.execution_monitor.get_system_statistics = AsyncMock(return_value={})
        
        # Initialize synchronously by running the async method in the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(core.initialize())
            return core
        finally:
            loop.close()

    @pytest.mark.asyncio
    async def test_persona_channel_compatibility(self, persona_manager, channel_manager):
        """Test that personas and channels are compatible"""
        # Get all personas
        all_personas = persona_manager.get_all_personas()
        assert len(all_personas) == 3
        
        # Test web persona with web channel
        web_personas = persona_manager.get_personas_for_channel("web")
        assert len(web_personas) == 2  # web-persona and multi-channel-persona
        assert any(p.id == "web-persona" for p in web_personas)
        assert any(p.id == "multi-channel-persona" for p in web_personas)
        
        # Test Slack persona with Slack channel
        slack_personas = persona_manager.get_personas_for_channel("slack")
        assert len(slack_personas) == 2  # slack-persona and multi-channel-persona
        assert any(p.id == "slack-persona" for p in slack_personas)
        assert any(p.id == "multi-channel-persona" for p in slack_personas)
        
        # Test Teams persona with Teams channel
        teams_personas = persona_manager.get_personas_for_channel("teams")
        assert len(teams_personas) == 1  # Only multi-channel-persona
        assert any(p.id == "multi-channel-persona" for p in teams_personas)

    @pytest.mark.asyncio
    async def test_persona_switching_preserves_channel_context(self, persona_manager, channel_manager):
        """Test that persona switching preserves channel context"""
        # Switch to web persona
        web_persona = persona_manager.switch_persona("web-persona")
        assert web_persona is not None
        assert web_persona.id == "web-persona"
        
        # Verify web persona supports web channel
        assert "web" in web_persona.channels
        
        # Switch to Slack persona
        slack_persona = persona_manager.switch_persona("slack-persona")
        assert slack_persona is not None
        assert slack_persona.id == "slack-persona"
        
        # Verify Slack persona supports Slack channel
        assert "slack" in slack_persona.channels
        
        # Switch back to web persona
        web_persona_again = persona_manager.switch_persona("web-persona")
        assert web_persona_again is not None
        assert web_persona_again.id == "web-persona"

    @pytest.mark.asyncio
    async def test_channel_specific_persona_capabilities(self, persona_manager):
        """Test that personas have channel-specific capabilities"""
        # Get web persona
        web_persona = persona_manager.get_persona("web-persona")
        assert web_persona is not None
        
        # Check web-specific capabilities
        assert "web_automation" in web_persona.capabilities
        assert "ui_testing" in web_persona.capabilities
        
        # Get Slack persona
        slack_persona = persona_manager.get_persona("slack-persona")
        assert slack_persona is not None
        
        # Check Slack-specific capabilities
        assert "slack_automation" in slack_persona.capabilities
        assert "team_collaboration" in slack_persona.capabilities
        
        # Get multi-channel persona
        multi_persona = persona_manager.get_persona("multi-channel-persona")
        assert multi_persona is not None
        
        # Check cross-platform capabilities
        assert "cross_platform" in multi_persona.capabilities
        assert "integration" in multi_persona.capabilities

    @pytest.mark.asyncio
    async def test_persona_channel_switching_workflow(self, bk25_core):
        """Test complete workflow of persona and channel switching"""
        # Initial state - should have a default persona set
        initial_persona = bk25_core.persona_manager.get_current_persona()
        assert initial_persona is not None
        initial_persona_id = initial_persona.id
        
        # Switch to web persona
        web_persona = bk25_core.persona_manager.switch_persona("web-persona")
        assert web_persona is not None
        assert web_persona.id == "web-persona"
        
        # Verify persona is set as current
        current_persona = bk25_core.persona_manager.get_current_persona()
        assert current_persona.id == "web-persona"
        
        # Switch to Slack persona
        slack_persona = bk25_core.persona_manager.switch_persona("slack-persona")
        assert slack_persona is not None
        assert slack_persona.id == "slack-persona"
        
        # Verify persona switched
        current_persona = bk25_core.persona_manager.get_current_persona()
        assert current_persona.id == "slack-persona"
        
        # Switch back to initial persona
        initial_persona_again = bk25_core.persona_manager.switch_persona(initial_persona_id)
        assert initial_persona_again is not None
        assert initial_persona_again.id == initial_persona_id

    @pytest.mark.asyncio
    async def test_persona_channel_validation(self, persona_manager):
        """Test validation of persona-channel combinations"""
        # Test valid combinations
        web_persona = persona_manager.get_persona("web-persona")
        assert "web" in web_persona.channels
        
        slack_persona = persona_manager.get_persona("slack-persona")
        assert "slack" in slack_persona.channels
        
        multi_persona = persona_manager.get_persona("multi-channel-persona")
        assert "web" in multi_persona.channels
        assert "slack" in multi_persona.channels
        assert "teams" in multi_persona.channels
        
        # Test invalid combinations
        assert "teams" not in web_persona.channels
        assert "web" not in slack_persona.channels

    @pytest.mark.asyncio
    async def test_persona_channel_examples(self, persona_manager):
        """Test that personas have channel-appropriate examples"""
        # Web persona examples
        web_persona = persona_manager.get_persona("web-persona")
        web_examples = web_persona.examples
        assert any("web" in example.lower() or "form" in example.lower() for example in web_examples)
        
        # Slack persona examples
        slack_persona = persona_manager.get_persona("slack-persona")
        slack_examples = slack_persona.examples
        assert any("slack" in example.lower() or "message" in example.lower() for example in slack_examples)
        
        # Multi-channel persona examples
        multi_persona = persona_manager.get_persona("multi-channel-persona")
        multi_examples = multi_persona.examples
        assert any("cross" in example.lower() or "multi" in example.lower() for example in multi_examples)

    @pytest.mark.asyncio
    async def test_persona_channel_personality_alignment(self, persona_manager):
        """Test that persona personalities align with channel purposes"""
        # Web persona - should be user-friendly
        web_persona = persona_manager.get_persona("web-persona")
        assert web_persona.personality.tone == "friendly"
        assert web_persona.personality.approach == "helpful"
        assert "web_first" in web_persona.personality.philosophy
        
        # Slack persona - should be professional and collaborative
        slack_persona = persona_manager.get_persona("slack-persona")
        assert slack_persona.personality.tone == "professional"
        assert "collaborative" in slack_persona.personality.approach
        assert "team_work" in slack_persona.personality.philosophy
        
        # Multi-channel persona - should be versatile
        multi_persona = persona_manager.get_persona("multi-channel-persona")
        assert "versatile" in multi_persona.personality.tone
        assert "adaptive" in multi_persona.personality.approach
        assert "platform_agnostic" in multi_persona.personality.philosophy

    @pytest.mark.asyncio
    async def test_persona_channel_system_prompts(self, persona_manager):
        """Test that system prompts are channel-appropriate"""
        # Web persona system prompt
        web_persona = persona_manager.get_persona("web-persona")
        assert "web automation expert" in web_persona.system_prompt.lower()
        
        # Slack persona system prompt
        slack_persona = persona_manager.get_persona("slack-persona")
        assert "slack automation expert" in slack_persona.system_prompt.lower()
        
        # Multi-channel persona system prompt
        multi_persona = persona_manager.get_persona("multi-channel-persona")
        assert "cross-platform automation expert" in multi_persona.system_prompt.lower()

    @pytest.mark.asyncio
    async def test_persona_channel_greeting_consistency(self, persona_manager):
        """Test that greetings are consistent with channel context"""
        # Web persona greeting
        web_persona = persona_manager.get_persona("web-persona")
        assert "web" in web_persona.greeting.lower()
        
        # Slack persona greeting
        slack_persona = persona_manager.get_persona("slack-persona")
        assert "slack" in slack_persona.greeting.lower()
        
        # Multi-channel persona greeting
        multi_persona = persona_manager.get_persona("multi-channel-persona")
        assert "multiple channels" in multi_persona.greeting.lower()

    @pytest.mark.asyncio
    async def test_persona_channel_switching_performance(self, persona_manager):
        """Test performance of persona-channel switching"""
        import time
        
        # Measure switching time
        start_time = time.time()
        
        for _ in range(100):
            persona_manager.switch_persona("web-persona")
            persona_manager.switch_persona("slack-persona")
            persona_manager.switch_persona("multi-channel-persona")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 300 switches in reasonable time (less than 1 second)
        assert total_time < 1.0
        assert persona_manager.get_current_persona().id == "multi-channel-persona"

    @pytest.mark.asyncio
    async def test_persona_channel_error_handling(self, persona_manager):
        """Test error handling in persona-channel operations"""
        # Test switching to non-existent persona
        result = persona_manager.switch_persona("nonexistent-persona")
        assert result is None
        
        # Test getting personas for non-existent channel
        non_existent_channel_personas = persona_manager.get_personas_for_channel("nonexistent")
        assert len(non_existent_channel_personas) == 0
        
        # Test getting non-existent persona
        non_existent_persona = persona_manager.get_persona("nonexistent-persona")
        assert non_existent_persona is None

    @pytest.mark.asyncio
    async def test_persona_channel_data_persistence(self, persona_manager, personas_path):
        """Test that persona-channel data persists across reloads"""
        # Get initial personas
        initial_personas = persona_manager.get_all_personas()
        assert len(initial_personas) == 3
        
        # Reload personas
        await persona_manager.reload_personas()
        
        # Verify data persisted
        reloaded_personas = persona_manager.get_all_personas()
        assert len(reloaded_personas) == 3
        
        # Verify specific persona data
        web_persona = persona_manager.get_persona("web-persona")
        assert web_persona is not None
        assert web_persona.name == "Web Persona"
        assert "web" in web_persona.channels

    @pytest.mark.asyncio
    async def test_persona_channel_cross_reference(self, persona_manager):
        """Test cross-referencing between personas and channels"""
        # Get all personas
        all_personas = persona_manager.get_all_personas()
        
        # Build channel-to-persona mapping
        channel_personas = {}
        for persona in all_personas:
            for channel in persona.channels:
                if channel not in channel_personas:
                    channel_personas[channel] = []
                channel_personas[channel].append(persona.id)
        
        # Verify mappings
        assert "web" in channel_personas
        assert "slack" in channel_personas
        assert "teams" in channel_personas
        
        # Verify web channel has 2 personas
        assert len(channel_personas["web"]) == 2
        assert "web-persona" in channel_personas["web"]
        assert "multi-channel-persona" in channel_personas["web"]
        
        # Verify Slack channel has 2 personas
        assert len(channel_personas["slack"]) == 2
        assert "slack-persona" in channel_personas["slack"]
        assert "multi-channel-persona" in channel_personas["slack"]
        
        # Verify Teams channel has 1 persona
        assert len(channel_personas["teams"]) == 1
        assert "multi-channel-persona" in channel_personas["teams"]
