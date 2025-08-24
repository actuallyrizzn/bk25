"""
Unit tests for the ChannelManager class.
"""

import pytest
from bk25.core.channel_manager import ChannelManager
from bk25.models.channel import Channel


class TestChannelManager:
    """Test cases for ChannelManager."""
    
    def test_initialization(self, channel_manager):
        """Test channel manager initialization."""
        assert len(channel_manager.channels) > 0
        assert channel_manager.current_channel == "web"
        assert "web" in channel_manager.channels
        assert "slack" in channel_manager.channels
        assert "discord" in channel_manager.channels
    
    def test_get_all_channels(self, channel_manager):
        """Test getting all channels."""
        channels = channel_manager.get_all_channels()
        assert isinstance(channels, list)
        assert len(channels) > 0
        assert all(isinstance(c, Channel) for c in channels)
        
        # Should be sorted by name
        names = [c.name for c in channels]
        assert names == sorted(names)
    
    def test_get_current_channel(self, channel_manager):
        """Test getting current channel."""
        current = channel_manager.get_current_channel()
        assert current is not None
        assert isinstance(current, Channel)
        assert current.id == "web"
    
    def test_switch_channel(self, channel_manager):
        """Test switching channels."""
        # Switch to existing channel
        result = channel_manager.switch_channel("slack")
        assert result is not None
        assert result.id == "slack"
        assert channel_manager.current_channel == "slack"
        
        # Switch to non-existent channel
        result = channel_manager.switch_channel("nonexistent")
        assert result is None
        assert channel_manager.current_channel == "slack"  # Should remain unchanged
    
    def test_get_channel(self, channel_manager):
        """Test getting channel by ID."""
        # Get existing channel
        slack_channel = channel_manager.get_channel("slack")
        assert slack_channel is not None
        assert slack_channel.id == "slack"
        assert slack_channel.name == "Slack"
        
        # Get non-existent channel
        result = channel_manager.get_channel("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_generate_channel_artifact(self, channel_manager):
        """Test generating channel artifacts."""
        # Switch to web channel
        channel_manager.switch_channel("web")
        
        # Generate HTML component
        artifact = await channel_manager.generate_channel_artifact(
            "html-component",
            "A simple button component",
            {"title": "Click Me"}
        )
        
        assert artifact["channel"] == "web"
        assert artifact["artifact_type"] == "html-component"
        assert artifact["description"] == "A simple button component"
        assert "artifact" in artifact
        assert "generated_at" in artifact
    
    @pytest.mark.asyncio
    async def test_generate_unsupported_artifact(self, channel_manager):
        """Test generating unsupported artifacts."""
        # Switch to web channel
        channel_manager.switch_channel("web")
        
        # Try to generate Slack-specific artifact on web channel
        with pytest.raises(ValueError, match="not supported by channel"):
            await channel_manager.generate_channel_artifact(
                "block-kit",  # Slack artifact
                "Test description"
            )
    
    @pytest.mark.asyncio
    async def test_slack_artifacts(self, channel_manager):
        """Test Slack-specific artifacts."""
        channel_manager.switch_channel("slack")
        
        # Test Block Kit generation
        artifact = await channel_manager.generate_channel_artifact(
            "block-kit",
            "A test block kit UI",
            {"title": "Test Block Kit"}
        )
        
        assert artifact["artifact"]["type"] == "slack-block-kit"
        assert "blocks" in artifact["artifact"]
        
        # Test Workflow generation
        workflow_artifact = await channel_manager.generate_channel_artifact(
            "workflow",
            "A test workflow",
            {"name": "Test Workflow"}
        )
        
        assert workflow_artifact["artifact"]["type"] == "slack-workflow"
        assert "workflow" in workflow_artifact["artifact"]
    
    @pytest.mark.asyncio
    async def test_teams_artifacts(self, channel_manager):
        """Test Teams-specific artifacts."""
        channel_manager.switch_channel("teams")
        
        # Test Adaptive Card generation
        artifact = await channel_manager.generate_channel_artifact(
            "adaptive-card",
            "A test adaptive card",
            {"title": "Test Card"}
        )
        
        assert artifact["artifact"]["type"] == "teams-adaptive-card"
        assert "card" in artifact["artifact"]
        assert artifact["artifact"]["card"]["type"] == "AdaptiveCard"
    
    @pytest.mark.asyncio
    async def test_discord_artifacts(self, channel_manager):
        """Test Discord-specific artifacts."""
        channel_manager.switch_channel("discord")
        
        # Test Embed generation
        artifact = await channel_manager.generate_channel_artifact(
            "embed",
            "A test embed",
            {"title": "Test Embed", "color": 0xFF0000}
        )
        
        assert artifact["artifact"]["type"] == "discord-embed"
        assert "embed" in artifact["artifact"]
        assert artifact["artifact"]["embed"]["color"] == 0xFF0000
    
    @pytest.mark.asyncio
    async def test_web_artifacts(self, channel_manager):
        """Test Web-specific artifacts."""
        channel_manager.switch_channel("web")
        
        # Test HTML component generation
        artifact = await channel_manager.generate_channel_artifact(
            "html-component",
            "A test component",
            {"title": "Test Component"}
        )
        
        assert artifact["artifact"]["type"] == "web-html-component"
        assert "html" in artifact["artifact"]
        assert "Test Component" in artifact["artifact"]["html"]
        
        # Test JavaScript widget generation
        js_artifact = await channel_manager.generate_channel_artifact(
            "javascript-widget",
            "A test widget",
            {"name": "TestWidget", "title": "Test Widget"}
        )
        
        assert js_artifact["artifact"]["type"] == "web-javascript-widget"
        assert "javascript" in js_artifact["artifact"]
        assert "TestWidget" in js_artifact["artifact"]["javascript"]
    
    @pytest.mark.asyncio
    async def test_whatsapp_artifacts(self, channel_manager):
        """Test WhatsApp-specific artifacts."""
        channel_manager.switch_channel("whatsapp")
        
        # Test message template generation
        artifact = await channel_manager.generate_channel_artifact(
            "message-template",
            "A test message template",
            {"name": "test_template", "title": "Test Template"}
        )
        
        assert artifact["artifact"]["type"] == "whatsapp-template"
        assert "template" in artifact["artifact"]
        assert artifact["artifact"]["template"]["name"] == "test_template"
    
    def test_get_available_artifacts(self, channel_manager):
        """Test getting available artifacts for current channel."""
        # Web channel artifacts
        channel_manager.switch_channel("web")
        artifacts = channel_manager.get_available_artifacts()
        assert "html-component" in artifacts
        assert "css-styling" in artifacts
        assert "javascript-widget" in artifacts
        
        # Slack channel artifacts
        channel_manager.switch_channel("slack")
        artifacts = channel_manager.get_available_artifacts()
        assert "block-kit" in artifacts
        assert "workflow" in artifacts
        assert "modal" in artifacts
    
    def test_get_channel_capabilities(self, channel_manager):
        """Test getting channel capabilities."""
        # Web channel capabilities
        channel_manager.switch_channel("web")
        capabilities = channel_manager.get_channel_capabilities()
        assert "responsive-design" in capabilities
        assert "interactive-components" in capabilities
        
        # Slack channel capabilities
        channel_manager.switch_channel("slack")
        capabilities = channel_manager.get_channel_capabilities()
        assert "block-kit-ui" in capabilities
        assert "workflows" in capabilities