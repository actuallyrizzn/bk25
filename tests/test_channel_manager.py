import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

# Add src to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.channel_manager import ChannelManager, Channel, ChannelType, ChannelCapability

class TestChannelType:
    """Test ChannelType enum"""
    
    def test_channel_type_values(self):
        """Test ChannelType enum values"""
        assert ChannelType.WEB == "web"
        assert ChannelType.APPLE_BUSINESS_CHAT == "apple_business_chat"
        assert ChannelType.DISCORD == "discord"
        assert ChannelType.MICROSOFT_TEAMS == "microsoft_teams"
        assert ChannelType.SLACK == "slack"
        assert ChannelType.TWITCH == "twitch"
        assert ChannelType.WHATSAPP == "whatsapp"

class TestChannelCapability:
    """Test ChannelCapability dataclass"""
    
    def test_channel_capability_creation(self):
        """Test creating a ChannelCapability instance"""
        capability = ChannelCapability(
            name="file_upload",
            description="Upload files to the channel",
            supported=True,
            max_file_size=10,
            allowed_types=["image", "document"]
        )
        
        assert capability.name == "file_upload"
        assert capability.description == "Upload files to the channel"
        assert capability.supported is True
        assert capability.max_file_size == 10
        assert capability.allowed_types == ["image", "document"]
    
    def test_channel_capability_defaults(self):
        """Test ChannelCapability with default values"""
        capability = ChannelCapability(
            name="basic_chat",
            description="Basic chat functionality"
        )
        
        assert capability.name == "basic_chat"
        assert capability.description == "Basic chat functionality"
        assert capability.supported is True
        assert capability.max_file_size is None
        assert capability.allowed_types is None

class TestChannel:
    """Test Channel dataclass"""
    
    def test_channel_creation(self):
        """Test creating a Channel instance"""
        capabilities = {
            "chat": ChannelCapability(
                name="chat",
                description="Text chat support",
                supported=True
            ),
            "file_upload": ChannelCapability(
                name="file_upload",
                description="File upload support",
                supported=False
            )
        }
        
        channel = Channel(
            id="web",
            name="Web Interface",
            description="Standard web-based interface",
            capabilities=capabilities,
            artifact_types=["html", "css", "javascript"],
            metadata={"theme": "light", "responsive": True}
        )
        
        assert channel.id == "web"
        assert channel.name == "Web Interface"
        assert channel.description == "Standard web-based interface"
        assert len(channel.capabilities) == 2
        assert "chat" in channel.capabilities
        assert "file_upload" in channel.capabilities
        assert channel.artifact_types == ["html", "css", "javascript"]
        assert channel.metadata["theme"] == "light"
        assert channel.metadata["responsive"] is True
    
    def test_channel_defaults(self):
        """Test Channel with default values"""
        channel = Channel(
            id="minimal",
            name="Minimal Channel"
        )
        
        assert channel.id == "minimal"
        assert channel.name == "Minimal Channel"
        assert channel.description == ""
        assert channel.capabilities == {}
        assert channel.artifact_types == []
        assert channel.metadata == {}
    
    def test_channel_to_dict(self):
        """Test Channel.to_dict() method"""
        capabilities = {
            "chat": ChannelCapability(
                name="chat",
                description="Chat support",
                supported=True
            )
        }
        
        channel = Channel(
            id="test",
            name="Test Channel",
            capabilities=capabilities
        )
        
        result = channel.to_dict()
        
        assert result["id"] == "test"
        assert result["name"] == "Test Channel"
        assert "capabilities" in result
        assert "artifact_types" in result
        assert "metadata" in result

class TestChannelManager:
    """Test ChannelManager class"""
    
    @pytest.fixture
    def channel_manager(self):
        """Create ChannelManager instance"""
        return ChannelManager()
    
    def test_initialization(self, channel_manager):
        """Test ChannelManager initialization"""
        assert channel_manager.channels is not None
        assert len(channel_manager.channels) > 0
        assert channel_manager.current_channel is not None
    
    def test_get_channel_existing(self, channel_manager):
        """Test getting existing channel"""
        channel = channel_manager.get_channel("web")
        assert channel is not None
        assert channel.id == "web"
        assert channel.name == "Web Interface"
    
    def test_get_channel_nonexistent(self, channel_manager):
        """Test getting non-existent channel"""
        channel = channel_manager.get_channel("nonexistent")
        assert channel is None
    
    def test_get_all_channels(self, channel_manager):
        """Test getting all channels"""
        all_channels = channel_manager.get_all_channels()
        assert len(all_channels) > 0
        
        # Check that all expected channels are present
        expected_channels = ["web", "discord", "slack", "teams", "whatsapp", "twitch", "apple_business_chat"]
        for expected in expected_channels:
            assert any(ch.id == expected for ch in all_channels)
    
    def test_switch_channel_success(self, channel_manager):
        """Test successful channel switching"""
        initial_channel = channel_manager.current_channel
        
        # Switch to discord channel
        result = channel_manager.switch_channel("discord")
        assert result is not None
        assert result.id == "discord"
        assert channel_manager.current_channel.id == "discord"
        assert channel_manager.current_channel != initial_channel
    
    def test_switch_channel_nonexistent(self, channel_manager):
        """Test switching to non-existent channel"""
        initial_channel = channel_manager.current_channel
        
        result = channel_manager.switch_channel("nonexistent")
        assert result is None
        # Current channel should remain unchanged
        assert channel_manager.current_channel == initial_channel
    
    def test_get_current_channel(self, channel_manager):
        """Test getting current channel"""
        current = channel_manager.get_current_channel()
        assert current is not None
        assert current.id in [ch.id for ch in channel_manager.get_all_channels()]
    
    def test_get_channel_summary_existing(self, channel_manager):
        """Test getting channel summary for existing channel"""
        summary = channel_manager.get_channel_summary("web")
        assert summary is not None
        assert "id" in summary
        assert "name" in summary
        assert "description" in summary
        assert "capabilities" in summary
        assert summary["id"] == "web"
    
    def test_get_channel_summary_nonexistent(self, channel_manager):
        """Test getting channel summary for non-existent channel"""
        summary = channel_manager.get_channel_summary("nonexistent")
        assert summary is None
    
    def test_get_channel_stats(self, channel_manager):
        """Test getting channel statistics"""
        stats = channel_manager.get_channel_stats()
        assert "total_channels" in stats
        assert "current_channel" in stats
        assert "capability_summary" in stats
        assert stats["total_channels"] > 0
        assert stats["current_channel"] is not None
    
    def test_web_channel_capabilities(self, channel_manager):
        """Test web channel specific capabilities"""
        web_channel = channel_manager.get_channel("web")
        assert web_channel is not None
        
        # Check web-specific capabilities
        assert "chat" in web_channel.capabilities
        assert "file_upload" in web_channel.capabilities
        assert "rich_content" in web_channel.capabilities
        
        # Check web-specific artifact types
        assert "html" in web_channel.artifact_types
        assert "css" in web_channel.artifact_types
        assert "javascript" in web_channel.artifact_types
    
    def test_discord_channel_capabilities(self, channel_manager):
        """Test Discord channel specific capabilities"""
        discord_channel = channel_manager.get_channel("discord")
        assert discord_channel is not None
        
        # Check Discord-specific capabilities
        assert "chat" in discord_channel.capabilities
        assert "embeds" in discord_channel.capabilities
        assert "slash_commands" in discord_channel.capabilities
        
        # Check Discord-specific artifact types
        assert "embed" in discord_channel.artifact_types
        assert "slash_command" in discord_channel.artifact_types
    
    def test_slack_channel_capabilities(self, channel_manager):
        """Test Slack channel specific capabilities"""
        slack_channel = channel_manager.get_channel("slack")
        assert slack_channel is not None
        
        # Check Slack-specific capabilities
        assert "chat" in slack_channel.capabilities
        assert "block_kit" in slack_channel.capabilities
        assert "workflows" in slack_channel.capabilities
        
        # Check Slack-specific artifact types
        assert "block_kit" in slack_channel.artifact_types
        assert "workflow" in slack_channel.artifact_types
    
    def test_teams_channel_capabilities(self, channel_manager):
        """Test Microsoft Teams channel specific capabilities"""
        teams_channel = channel_manager.get_channel("teams")
        assert teams_channel is not None
        
        # Check Teams-specific capabilities
        assert "chat" in teams_channel.capabilities
        assert "adaptive_cards" in teams_channel.capabilities
        assert "task_modules" in teams_channel.capabilities
        
        # Check Teams-specific artifact types
        assert "adaptive_card" in teams_channel.artifact_types
        assert "task_module" in teams_channel.artifact_types
    
    def test_whatsapp_channel_capabilities(self, channel_manager):
        """Test WhatsApp channel specific capabilities"""
        whatsapp_channel = channel_manager.get_channel("whatsapp")
        assert whatsapp_channel is not None
        
        # Check WhatsApp-specific capabilities
        assert "chat" in whatsapp_channel.capabilities
        assert "media_sharing" in whatsapp_channel.capabilities
        assert "quick_replies" in whatsapp_channel.capabilities
        
        # Check WhatsApp-specific artifact types
        assert "message_template" in whatsapp_channel.artifact_types
        assert "quick_reply" in whatsapp_channel.artifact_types
    
    def test_twitch_channel_capabilities(self, channel_manager):
        """Test Twitch channel specific capabilities"""
        twitch_channel = channel_manager.get_channel("twitch")
        assert twitch_channel is not None
        
        # Check Twitch-specific capabilities
        assert "chat" in twitch_channel.capabilities
        assert "extensions" in twitch_channel.capabilities
        assert "stream_integration" in twitch_channel.capabilities
        
        # Check Twitch-specific artifact types
        assert "chat_command" in twitch_channel.artifact_types
        assert "extension" in twitch_channel.artifact_types
    
    def test_apple_business_chat_capabilities(self, channel_manager):
        """Test Apple Business Chat channel specific capabilities"""
        apple_channel = channel_manager.get_channel("apple_business_chat")
        assert apple_channel is not None
        
        # Check Apple Business Chat-specific capabilities
        assert "chat" in apple_channel.capabilities
        assert "rich_interactive_messages" in apple_channel.capabilities
        assert "payments" in apple_channel.capabilities
        
        # Check Apple Business Chat-specific artifact types
        assert "rich_message" in apple_channel.artifact_types
        assert "payment_request" in apple_channel.artifact_types
    
    def test_channel_capability_validation(self, channel_manager):
        """Test channel capability validation"""
        web_channel = channel_manager.get_channel("web")
        
        # Test supported capability
        chat_capability = web_channel.capabilities.get("chat")
        assert chat_capability is not None
        assert chat_capability.supported is True
        
        # Test unsupported capability (if any)
        for capability in web_channel.capabilities.values():
            assert isinstance(capability.supported, bool)
            assert isinstance(capability.name, str)
            assert isinstance(capability.description, str)
    
    def test_channel_metadata(self, channel_manager):
        """Test channel metadata"""
        web_channel = channel_manager.get_channel("web")
        assert web_channel.metadata is not None
        
        # Check that metadata is a dictionary
        assert isinstance(web_channel.metadata, dict)
    
    def test_channel_artifact_types(self, channel_manager):
        """Test channel artifact types"""
        web_channel = channel_manager.get_channel("web")
        assert web_channel.artifact_types is not None
        
        # Check that artifact types is a list
        assert isinstance(web_channel.artifact_types, list)
        
        # Check that all artifact types are strings
        for artifact_type in web_channel.artifact_types:
            assert isinstance(artifact_type, str)
    
    def test_channel_switching_preserves_state(self, channel_manager):
        """Test that channel switching preserves channel state"""
        # Get initial state
        initial_web = channel_manager.get_channel("web")
        initial_discord = channel_manager.get_channel("discord")
        
        # Switch channels multiple times
        channel_manager.switch_channel("discord")
        channel_manager.switch_channel("web")
        channel_manager.switch_channel("discord")
        
        # Get final state
        final_web = channel_manager.get_channel("web")
        final_discord = channel_manager.get_channel("discord")
        
        # State should be preserved
        assert initial_web.id == final_web.id
        assert initial_web.name == final_web.name
        assert initial_discord.id == final_discord.id
        assert initial_discord.name == final_discord.name
    
    def test_channel_manager_singleton_behavior(self):
        """Test that ChannelManager behaves like a singleton for channel data"""
        manager1 = ChannelManager()
        manager2 = ChannelManager()
        
        # Both should have the same channel data
        assert len(manager1.get_all_channels()) == len(manager2.get_all_channels())
        
        # Channel IDs should be the same
        manager1_ids = [ch.id for ch in manager1.get_all_channels()]
        manager2_ids = [ch.id for ch in manager2.get_all_channels()]
        assert set(manager1_ids) == set(manager2_ids)
    
    def test_channel_capability_methods(self):
        """Test ChannelCapability methods and properties"""
        capability = ChannelCapability(
            name="test_capability",
            description="Test description",
            supported=True,
            max_file_size=100,
            allowed_types=["text", "image"]
        )
        
        # Test string representation
        str_repr = str(capability)
        assert "test_capability" in str_repr
        assert "Test description" in str_repr
        
        # Test dictionary conversion
        dict_repr = capability.__dict__
        assert "name" in dict_repr
        assert "description" in dict_repr
        assert "supported" in dict_repr
    
    def test_channel_methods(self):
        """Test Channel methods and properties"""
        capabilities = {
            "test": ChannelCapability(
                name="test",
                description="Test capability",
                supported=True
            )
        }
        
        channel = Channel(
            id="test_channel",
            name="Test Channel",
            capabilities=capabilities
        )
        
        # Test string representation
        str_repr = str(channel)
        assert "test_channel" in str_repr
        assert "Test Channel" in str_repr
        
        # Test dictionary conversion
        dict_repr = channel.to_dict()
        assert "id" in dict_repr
        assert "name" in dict_repr
        assert "capabilities" in dict_repr

if __name__ == "__main__":
    pytest.main([__file__])
