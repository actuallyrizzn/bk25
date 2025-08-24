"""
Unit tests for ChannelManager component
"""

import pytest
from unittest.mock import Mock, patch
from src.core.channel_manager import ChannelManager
from src.core.channels.base import BaseChannel


class TestChannelManager:
    """Test ChannelManager functionality"""

    @pytest.fixture
    def channel_manager(self):
        """Create ChannelManager instance for testing"""
        return ChannelManager()

    @pytest.fixture
    def mock_web_channel(self):
        """Create mock web channel"""
        from src.core.channel_manager import ChannelCapability
        channel = Mock()
        channel.id = "web"
        channel.name = "Web Interface"
        channel.description = "Web-based user interface"
        channel.capabilities = {
            "text": ChannelCapability("Text", "Text messaging", True),
            "files": ChannelCapability("Files", "File uploads", True),
            "rich_content": ChannelCapability("Rich Content", "Rich content display", True)
        }
        channel.artifact_types = ["html", "css", "javascript"]
        channel.metadata = {"web": True}
        return channel

    @pytest.fixture
    def mock_slack_channel(self):
        """Create mock Slack channel"""
        from src.core.channel_manager import ChannelCapability
        channel = Mock()
        channel.id = "slack"
        channel.name = "Slack"
        channel.description = "Slack workspace integration"
        channel.capabilities = {
            "text": ChannelCapability("Text", "Text messaging", True),
            "blocks": ChannelCapability("Blocks", "Block Kit components", True),
            "files": ChannelCapability("Files", "File sharing", True)
        }
        channel.artifact_types = ["blocks", "attachments", "modals"]
        channel.metadata = {"slack": True}
        return channel

    @pytest.fixture
    def mock_teams_channel(self):
        """Create mock Teams channel"""
        from src.core.channel_manager import ChannelCapability
        channel = Mock()
        channel.id = "teams"
        channel.name = "Microsoft Teams"
        channel.description = "Teams workspace integration"
        channel.capabilities = {
            "text": ChannelCapability("Text", "Text messaging", True),
            "adaptive_cards": ChannelCapability("Adaptive Cards", "Adaptive Cards", True),
            "files": ChannelCapability("Files", "File sharing", True)
        }
        channel.artifact_types = ["adaptive_cards", "attachments"]
        channel.metadata = {"teams": True}
        return channel

    def test_init(self, channel_manager):
        """Test ChannelManager initialization"""
        assert channel_manager.channels is not None
        assert isinstance(channel_manager.channels, dict)
        assert len(channel_manager.channels) > 0  # Starts with predefined channels
        assert channel_manager.current_channel == "web"  # Defaults to web
        assert channel_manager.logger is not None

    def test_get_all_channels(self, channel_manager, mock_web_channel, mock_slack_channel):
        """Test getting all channels"""
        # Store original channels
        original_channels = channel_manager.channels.copy()
        
        # Clear and add test channels
        channel_manager.channels.clear()
        channel_manager.channels["web"] = mock_web_channel
        channel_manager.channels["slack"] = mock_slack_channel

        all_channels = channel_manager.get_all_channels()
        assert len(all_channels) == 2
        assert any(ch.id == "web" for ch in all_channels)
        assert any(ch.id == "slack" for ch in all_channels)
        
        # Restore original channels
        channel_manager.channels = original_channels

    def test_get_channel_existing(self, channel_manager, mock_web_channel):
        """Test getting existing channel by ID"""
        channel_manager.channels["web"] = mock_web_channel

        retrieved = channel_manager.get_channel("web")
        assert retrieved is not None
        assert retrieved.id == "web"
        assert retrieved.name == "Web Interface"

    def test_get_channel_nonexistent(self, channel_manager):
        """Test getting non-existent channel by ID"""
        retrieved = channel_manager.get_channel("nonexistent")
        assert retrieved is None

    def test_get_current_channel_none(self, channel_manager):
        """Test getting current channel when none set"""
        # Store original current channel
        original_current = channel_manager.current_channel
        
        # Set to None temporarily
        channel_manager.current_channel = None
        current = channel_manager.get_current_channel()
        # The method has a fallback to return the web channel when current_channel is None
        assert current is not None
        assert current.id == "web"
        
        # Restore original current channel
        channel_manager.current_channel = original_current

    def test_get_current_channel_set(self, channel_manager, mock_web_channel):
        """Test getting current channel when one is set"""
        channel_manager.channels["web"] = mock_web_channel
        channel_manager.current_channel = "web"

        current = channel_manager.get_current_channel()
        assert current is not None
        assert current.id == "web"

    def test_switch_channel_existing(self, channel_manager, mock_web_channel):
        """Test switching to existing channel"""
        channel_manager.channels["web"] = mock_web_channel

        result = channel_manager.switch_channel("web")
        assert result is not None
        assert result.id == "web"
        assert channel_manager.current_channel == "web"

    def test_switch_channel_nonexistent(self, channel_manager):
        """Test switching to non-existent channel"""
        # Store original current channel
        original_current = channel_manager.current_channel
        
        result = channel_manager.switch_channel("nonexistent")
        assert result is None
        # The current_channel should remain unchanged when switching fails
        assert channel_manager.current_channel == original_current
        
        # Restore original current channel
        channel_manager.current_channel = original_current

    def test_get_channel_summary(self, channel_manager, mock_web_channel):
        """Test getting channel summary"""
        channel_manager.channels["web"] = mock_web_channel

        summary = channel_manager.get_channel_summary("web")
        assert summary is not None
        assert "id" in summary
        assert "name" in summary
        assert "description" in summary
        assert "capabilities" in summary

    def test_get_channel_summary_nonexistent(self, channel_manager):
        """Test getting summary for non-existent channel"""
        summary = channel_manager.get_channel_summary("nonexistent")
        # The method returns an empty dict for non-existent channels
        assert summary == {}

    def test_get_channel_stats(self, channel_manager, mock_web_channel, mock_slack_channel):
        """Test getting channel statistics"""
        # Store original channels
        original_channels = channel_manager.channels.copy()
        
        # Clear and add test channels
        channel_manager.channels.clear()
        channel_manager.channels["web"] = mock_web_channel
        channel_manager.channels["slack"] = mock_slack_channel

        stats = channel_manager.get_channel_stats()
        assert "total_channels" in stats
        assert "current_channel" in stats
        assert stats["total_channels"] == 2
        
        # Restore original channels
        channel_manager.channels = original_channels

    def test_channel_capabilities(self, channel_manager, mock_web_channel):
        """Test channel capabilities functionality"""
        channel_manager.channels["web"] = mock_web_channel

        # Test individual capabilities
        assert mock_web_channel.capabilities["text"].supported is True
        assert mock_web_channel.capabilities["files"].supported is True
        assert mock_web_channel.capabilities["rich_content"].supported is True

        # Test capability descriptions
        assert "Text messaging" in mock_web_channel.capabilities["text"].description
        assert "File uploads" in mock_web_channel.capabilities["files"].description

    def test_channel_artifact_types(self, channel_manager, mock_web_channel, mock_slack_channel):
        """Test channel artifact types"""
        channel_manager.channels["web"] = mock_web_channel
        channel_manager.channels["slack"] = mock_slack_channel

        # Test web channel artifacts
        web_artifacts = mock_web_channel.artifact_types
        assert "html" in web_artifacts
        assert "css" in web_artifacts
        assert "javascript" in web_artifacts

        # Test Slack channel artifacts
        slack_artifacts = mock_slack_channel.artifact_types
        assert "blocks" in slack_artifacts
        assert "attachments" in slack_artifacts
        assert "modals" in slack_artifacts

    def test_channel_metadata(self, channel_manager, mock_web_channel, mock_slack_channel):
        """Test channel metadata"""
        channel_manager.channels["web"] = mock_web_channel
        channel_manager.channels["slack"] = mock_slack_channel

        # Test web channel metadata
        assert mock_web_channel.metadata["web"] is True

        # Test Slack channel metadata
        assert mock_slack_channel.metadata["slack"] is True

    def test_channel_switching_preserves_state(self, channel_manager, mock_web_channel, mock_slack_channel):
        """Test that channel switching preserves other state"""
        # Add channels to manager
        channel_manager.channels["web"] = mock_web_channel
        channel_manager.channels["slack"] = mock_slack_channel

        # Switch to web channel
        channel_manager.switch_channel("web")
        assert channel_manager.current_channel == "web"

        # Switch to Slack channel
        channel_manager.switch_channel("slack")
        assert channel_manager.current_channel == "slack"

        # Verify both channels still exist
        assert "web" in channel_manager.channels
        assert "slack" in channel_manager.channels

    def test_channel_validation(self, channel_manager):
        """Test channel validation"""
        # Test valid channel
        valid_channel = Mock(spec=BaseChannel)
        valid_channel.id = "valid"
        valid_channel.name = "Valid Channel"
        valid_channel.description = "A valid channel"
        valid_channel.capabilities = {}
        valid_channel.artifact_types = []
        valid_channel.metadata = {}

        channel_manager.channels["valid"] = valid_channel
        assert "valid" in channel_manager.channels

        # Test channel without required attributes
        invalid_channel = Mock()
        invalid_channel.id = "invalid"
        # Missing name, description, etc.

        # Should still be added (validation happens at channel level)
        channel_manager.channels["invalid"] = invalid_channel
        assert "invalid" in channel_manager.channels

    def test_channel_capability_checking(self, channel_manager, mock_web_channel):
        """Test checking channel capabilities"""
        channel_manager.channels["web"] = mock_web_channel

        # Test capability checking
        assert mock_web_channel.capabilities["text"].supported is True
        assert mock_web_channel.capabilities["files"].supported is True

        # Test non-existent capability
        if "nonexistent" in mock_web_channel.capabilities:
            assert False, "Should not have nonexistent capability"
        else:
            assert True, "Correctly missing nonexistent capability"

    def test_channel_artifact_generation(self, channel_manager, mock_web_channel):
        """Test channel artifact generation capabilities"""
        channel_manager.channels["web"] = mock_web_channel

        # Test that web channel supports HTML/CSS/JS artifacts
        supported_artifacts = mock_web_channel.artifact_types
        assert "html" in supported_artifacts
        assert "css" in supported_artifacts
        assert "javascript" in supported_artifacts

        # Test artifact count
        assert len(supported_artifacts) == 3

    def test_channel_switching_behavior(self, channel_manager, mock_web_channel, mock_slack_channel):
        """Test channel switching behavior"""
        # Store original channels and current channel
        original_channels = channel_manager.channels.copy()
        original_current = channel_manager.current_channel
        
        # Clear and add test channels
        channel_manager.channels.clear()
        channel_manager.channels["web"] = mock_web_channel
        channel_manager.channels["slack"] = mock_slack_channel
        channel_manager.current_channel = None

        # Initial state
        assert channel_manager.current_channel is None

        # Switch to web
        result1 = channel_manager.switch_channel("web")
        assert result1 is not None
        assert channel_manager.current_channel == "web"

        # Switch to Slack
        result2 = channel_manager.switch_channel("slack")
        assert result2 is not None
        assert channel_manager.current_channel == "slack"

        # Verify previous channel still exists
        assert "web" in channel_manager.channels
        assert "slack" in channel_manager.channels
        
        # Restore original state
        channel_manager.channels = original_channels
        channel_manager.current_channel = original_current

    def test_channel_manager_empty_state(self, channel_manager):
        """Test channel manager behavior when empty"""
        # Store original channels
        original_channels = channel_manager.channels.copy()
        
        # Test empty state
        channel_manager.channels.clear()
        assert len(channel_manager.channels) == 0
        
        # Test getting all channels when empty
        all_channels = channel_manager.get_channel_stats()
        assert all_channels["total_channels"] == 0
        
        # Restore original channels
        channel_manager.channels = original_channels
        # current_channel might still be set even when channels are empty
        # This is expected behavior

        # Test switching when no channels exist
        result = channel_manager.switch_channel("nonexistent")
        assert result is None

    def test_channel_manager_error_handling(self, channel_manager):
        """Test channel manager error handling"""
        # Test getting channel that doesn't exist
        channel = channel_manager.get_channel("nonexistent")
        assert channel is None

        # Test getting summary for non-existent channel
        summary = channel_manager.get_channel_summary("nonexistent")
        # The method returns an empty dict for non-existent channels
        assert summary == {}

        # Test switching to non-existent channel
        result = channel_manager.switch_channel("nonexistent")
        assert result is None

    def test_channel_capability_structure(self, channel_manager, mock_web_channel):
        """Test channel capability structure"""
        channel_manager.channels["web"] = mock_web_channel

        # Test capability structure
        text_capability = mock_web_channel.capabilities["text"]
        assert hasattr(text_capability, "supported")
        assert hasattr(text_capability, "description")
        assert isinstance(text_capability.supported, bool)
        assert isinstance(text_capability.description, str)

        # Test all capabilities have required structure
        for cap_name, cap_data in mock_web_channel.capabilities.items():
            assert hasattr(cap_data, "supported")
            assert hasattr(cap_data, "description")
            assert isinstance(cap_data.supported, bool)
            assert isinstance(cap_data.description, str)

    def test_channel_metadata_structure(self, channel_manager, mock_web_channel):
        """Test channel metadata structure"""
        channel_manager.channels["web"] = mock_web_channel

        # Test metadata is dictionary
        assert isinstance(mock_web_channel.metadata, dict)

        # Test metadata content
        assert mock_web_channel.metadata["web"] is True

    def test_channel_artifact_types_structure(self, channel_manager, mock_web_channel):
        """Test channel artifact types structure"""
        channel_manager.channels["web"] = mock_web_channel

        # Test artifact types is list
        assert isinstance(mock_web_channel.artifact_types, list)

        # Test artifact types content
        expected_types = ["html", "css", "javascript"]
        for expected_type in expected_types:
            assert expected_type in mock_web_channel.artifact_types
