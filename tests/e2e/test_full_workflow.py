"""
End-to-end tests for complete BK25 workflows.
"""

import pytest
import asyncio
from pathlib import Path
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bk25.core.bk25_core import BK25Core
from bk25.core.memory import ConversationMemory
from bk25.core.persona_manager import PersonaManager
from bk25.core.channel_manager import ChannelManager


class TestFullWorkflow:
    """End-to-end tests for complete BK25 workflows."""
    
    @pytest.fixture
    async def full_bk25_system(self):
        """Create a fully initialized BK25 system for testing."""
        # Create temporary database
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_bk25.db"
        
        config = {
            "ollama_url": "http://localhost:11434",
            "model": "test-model",
            "temperature": 0.1,
            "max_tokens": 100
        }
        
        core = BK25Core(config)
        core.memory.db_path = str(db_path)
        core.ollama_connected = False  # Mock Ollama for tests
        
        await core.memory.initialize_database()
        await core.persona_manager.initialize()
        
        yield core
        
        await core.close()
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_conversation_workflow(self, full_bk25_system):
        """Test complete conversation workflow."""
        bk25 = full_bk25_system
        
        # Mock LLM response since we don't have Ollama
        async def mock_generate_completion(prompt, options=None):
            if "automation" in prompt.lower():
                return "I'll help you create an automation script."
            return "Hello! I'm here to help you with automation tasks."
        
        bk25.generate_completion = mock_generate_completion
        
        # Test conversation
        response = await bk25.process_message("Hello, can you help me?")
        
        assert response["type"] == "conversation"
        assert "help" in response["message"].lower()
        assert response["conversational"] is True
        
        # Check that message was stored
        messages = await bk25.memory.get_recent_messages(5)
        assert len(messages) >= 2  # User message + assistant response
        assert messages[-2]["role"] == "user"
        assert messages[-1]["role"] == "assistant"
    
    @pytest.mark.asyncio
    async def test_automation_detection_workflow(self, full_bk25_system):
        """Test automation detection and generation workflow."""
        bk25 = full_bk25_system
        
        # Mock automation generation
        async def mock_generate_completion(prompt, options=None):
            if "powershell" in prompt.lower():
                return '''
```powershell
# Generated PowerShell script
Write-Host "Hello, World!" -ForegroundColor Green
```
                '''.strip()
            return "I can help you create automation scripts."
        
        bk25.generate_completion = mock_generate_completion
        
        # Test automation request
        response = await bk25.process_message("Create a PowerShell script to say hello")
        
        assert response["type"] == "automation"
        assert "automation" in response
        
        automation = response["automation"]
        assert automation["platform"] == "powershell"
        assert "Write-Host" in automation["script"]
        assert automation["filename"].endswith(".ps1")
        
        # Check that automation was stored
        automations = await bk25.memory.find_similar_automations("hello")
        assert len(automations) == 1
        assert automations[0]["platform"] == "powershell"
    
    @pytest.mark.asyncio
    async def test_persona_switching_workflow(self, full_bk25_system):
        """Test persona switching workflow."""
        bk25 = full_bk25_system
        
        # Create test persona
        test_persona_data = {
            "id": "test-expert",
            "name": "Test Expert",
            "description": "Expert in testing",
            "greeting": "Hello! I'm a testing expert.",
            "systemPrompt": "You are an expert in software testing.",
            "capabilities": ["Testing", "Quality Assurance"],
            "examples": ["Write unit tests", "Design test cases"]
        }
        
        test_persona = bk25.persona_manager.create_custom_persona(test_persona_data)
        assert test_persona.id == "test-expert"
        
        # Switch to test persona
        switched = bk25.persona_manager.switch_persona("test-expert")
        assert switched is not None
        assert switched.name == "Test Expert"
        
        # Verify current persona
        current = bk25.persona_manager.get_current_persona()
        assert current.id == "test-expert"
        
        # Test persona-specific functionality
        greeting = bk25.persona_manager.get_greeting()
        assert "testing expert" in greeting.lower()
        
        capabilities = bk25.persona_manager.get_capabilities()
        assert "Testing" in capabilities
    
    @pytest.mark.asyncio
    async def test_channel_switching_workflow(self, full_bk25_system):
        """Test channel switching workflow."""
        bk25 = full_bk25_system
        
        # Test switching to Slack
        slack_channel = bk25.channel_manager.switch_channel("slack")
        assert slack_channel is not None
        assert slack_channel.id == "slack"
        
        # Generate Slack artifact
        artifact = await bk25.channel_manager.generate_channel_artifact(
            "block-kit",
            "A welcome message for new team members",
            {"title": "Welcome to the Team"}
        )
        
        assert artifact["channel"] == "slack"
        assert artifact["artifact_type"] == "block-kit"
        assert artifact["artifact"]["type"] == "slack-block-kit"
        
        # Test switching to Discord
        discord_channel = bk25.channel_manager.switch_channel("discord")
        assert discord_channel.id == "discord"
        
        # Generate Discord artifact
        embed_artifact = await bk25.channel_manager.generate_channel_artifact(
            "embed",
            "Server announcement",
            {"title": "Server Update", "color": 0x00FF00}
        )
        
        assert embed_artifact["channel"] == "discord"
        assert embed_artifact["artifact"]["embed"]["color"] == 0x00FF00
    
    @pytest.mark.asyncio
    async def test_multi_platform_generation_workflow(self, full_bk25_system):
        """Test generating automation for multiple platforms."""
        bk25 = full_bk25_system
        
        # Mock different platform generations
        async def mock_generate_completion(prompt, options=None):
            if "powershell" in prompt.lower():
                return '''
```powershell
Get-Process | Where-Object {$_.ProcessName -eq "notepad"}
```
                '''.strip()
            elif "applescript" in prompt.lower():
                return '''
```applescript
tell application "TextEdit" to activate
```
                '''.strip()
            elif "bash" in prompt.lower():
                return '''
```bash
#!/bin/bash
ps aux | grep notepad
```
                '''.strip()
            return "Generated script"
        
        bk25.generate_completion = mock_generate_completion
        
        # Test PowerShell generation
        ps_automation = await bk25.generate_automation(
            "Find running notepad processes",
            "powershell"
        )
        assert ps_automation["platform"] == "powershell"
        assert "Get-Process" in ps_automation["script"]
        
        # Test AppleScript generation
        as_automation = await bk25.generate_automation(
            "Open TextEdit application",
            "applescript"
        )
        assert as_automation["platform"] == "applescript"
        assert "TextEdit" in as_automation["script"]
        
        # Test Bash generation
        bash_automation = await bk25.generate_automation(
            "Search for notepad process",
            "bash"
        )
        assert bash_automation["platform"] == "bash"
        assert "#!/bin/bash" in bash_automation["script"]
        
        # Verify all automations were stored
        stats = await bk25.get_stats()
        assert stats["total_automations"] == 3
        assert stats["platform_distribution"]["powershell"] == 1
        assert stats["platform_distribution"]["applescript"] == 1
        assert stats["platform_distribution"]["bash"] == 1
    
    @pytest.mark.asyncio
    async def test_conversation_memory_workflow(self, full_bk25_system):
        """Test conversation memory and context workflow."""
        bk25 = full_bk25_system
        
        # Mock LLM to echo context
        async def mock_generate_completion(prompt, options=None):
            return f"I understand your request. Based on our conversation: {len(prompt)} characters in prompt."
        
        bk25.generate_completion = mock_generate_completion
        
        # Have a multi-turn conversation
        response1 = await bk25.process_message("Hello, I need help with automation")
        response2 = await bk25.process_message("Specifically PowerShell scripts")
        response3 = await bk25.process_message("Can you create one for file operations?")
        
        # Check that all messages were stored
        messages = await bk25.memory.get_recent_messages(10)
        assert len(messages) >= 6  # 3 user + 3 assistant messages
        
        # Verify conversation flow
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        assert "automation" in user_messages[0]["content"].lower()
        assert "powershell" in user_messages[1]["content"].lower()
        assert "file operations" in user_messages[2]["content"].lower()
        
        # Test context building
        recent_messages = await bk25.memory.get_recent_messages(4)
        prompt = bk25.persona_manager.build_persona_prompt("New message", recent_messages)
        
        # Should contain recent conversation context
        assert "automation" in prompt
        assert "PowerShell" in prompt or "powershell" in prompt
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, full_bk25_system):
        """Test error handling throughout the system."""
        bk25 = full_bk25_system
        
        # Test invalid persona switching
        result = bk25.persona_manager.switch_persona("nonexistent")
        assert result is None
        
        # Test invalid channel switching
        result = bk25.channel_manager.switch_channel("nonexistent")
        assert result is None
        
        # Test unsupported platform generation
        with pytest.raises(ValueError):
            await bk25.generate_automation("test", "unsupported_platform")
        
        # Test unsupported artifact generation
        bk25.channel_manager.switch_channel("web")
        with pytest.raises(ValueError):
            await bk25.channel_manager.generate_channel_artifact("block-kit", "test")
        
        # Test processing with Ollama connection error
        bk25.ollama_connected = False
        response = await bk25.process_message("Hello")
        assert response["type"] == "error"
        assert "error" in response