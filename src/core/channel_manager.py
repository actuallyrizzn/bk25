"""
BK25 Channel Manager

Manages different communication channels and their capabilities.
Handles channel-specific formatting and artifact generation.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..logging_config import get_logger

logger = get_logger("channel_manager")

class ChannelType(Enum):
    """Supported channel types"""
    WEB = "web"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    TWITCH = "twitch"
    WHATSAPP = "whatsapp"
    APPLE_BUSINESS_CHAT = "apple-business-chat"

@dataclass
class ChannelCapability:
    """Channel capability definition"""
    name: str
    description: str
    supported: bool
    implementation: Optional[str] = None

@dataclass
class Channel:
    """Channel definition with capabilities"""
    id: str
    name: str
    description: str
    capabilities: Dict[str, ChannelCapability]
    supported_personas: List[str]
    artifact_types: List[str]
    metadata: Dict[str, Any]

class ChannelManager:
    """Manages communication channels for BK25"""
    
    def __init__(self):
        self.channels: Dict[str, Channel] = {}
        self.current_channel: str = "web"
        self.logger = get_logger("channel_manager")
        self.initialize_channels()
    
    def initialize_channels(self) -> None:
        """Initialize supported channels with their capabilities"""
        channels = [
            Channel(
                id="web",
                name="Web Interface",
                description="Standard web-based chat interface with HTML/CSS/JS support",
                capabilities={
                    "rich_text": ChannelCapability("Rich Text", "HTML formatting support", True),
                    "file_upload": ChannelCapability("File Upload", "File attachment support", True),
                    "real_time": ChannelCapability("Real-time Updates", "WebSocket support", True),
                    "custom_ui": ChannelCapability("Custom UI", "Custom HTML components", True)
                },
                supported_personas=["*"],  # All personas
                artifact_types=["html", "css", "javascript", "json"],
                metadata={"color": "#007bff", "icon": "🌐"}
            ),
            Channel(
                id="slack",
                name="Slack",
                description="Slack workspace integration with Block Kit support",
                capabilities={
                    "blocks": ChannelCapability("Block Kit", "Slack Block Kit UI", True),
                    "threads": ChannelCapability("Threads", "Threaded conversations", True),
                    "reactions": ChannelCapability("Reactions", "Emoji reactions", True),
                    "slash_commands": ChannelCapability("Slash Commands", "Slack slash commands", True)
                },
                supported_personas=["*"],
                artifact_types=["blocks", "attachments", "modals"],
                metadata={"color": "#4A154B", "icon": "chat"}
            ),
            Channel(
                id="teams",
                name="Microsoft Teams",
                description="Teams integration with Adaptive Cards and bot framework",
                capabilities={
                    "adaptive_cards": ChannelCapability("Adaptive Cards", "Teams Adaptive Cards", True),
                    "task_modules": ChannelCapability("Task Modules", "Teams task modules", True),
                    "bot_framework": ChannelCapability("Bot Framework", "Microsoft Bot Framework", True),
                    "tabs": ChannelCapability("Tabs", "Teams tabs integration", True)
                },
                supported_personas=["*"],
                artifact_types=["adaptive_cards", "task_modules", "bot_activities"],
                metadata={"color": "#6264A7", "icon": "office"}
            ),
            Channel(
                id="discord",
                name="Discord",
                description="Discord bot integration with embeds and slash commands",
                capabilities={
                    "embeds": ChannelCapability("Embeds", "Discord rich embeds", True),
                    "slash_commands": ChannelCapability("Slash Commands", "Discord slash commands", True),
                    "reactions": ChannelCapability("Reactions", "Emoji reactions", True),
                    "voice": ChannelCapability("Voice", "Voice channel support", False)
                },
                supported_personas=["*"],
                artifact_types=["embeds", "slash_commands", "components"],
                metadata={"color": "#5865F2", "icon": "game"}
            ),
            Channel(
                id="twitch",
                name="Twitch",
                description="Twitch chat integration with streamer tools",
                capabilities={
                    "chat_commands": ChannelCapability("Chat Commands", "Twitch chat commands", True),
                    "extensions": ChannelCapability("Extensions", "Twitch extensions", False),
                    "moderation": ChannelCapability("Moderation", "Chat moderation tools", False),
                    "alerts": ChannelCapability("Alerts", "Stream alerts", False)
                },
                supported_personas=["*"],
                artifact_types=["chat_commands", "extensions"],
                metadata={"color": "#9146FF", "icon": "stream"}
            ),
            Channel(
                id="whatsapp",
                name="WhatsApp",
                description="WhatsApp Business API integration",
                capabilities={
                    "media": ChannelCapability("Media", "Image/video support", True),
                    "templates": ChannelCapability("Templates", "Message templates", True),
                    "quick_replies": ChannelCapability("Quick Replies", "Quick reply buttons", True),
                    "location": ChannelCapability("Location", "Location sharing", False)
                },
                supported_personas=["*"],
                artifact_types=["templates", "media", "interactive"],
                metadata={"color": "#25D366", "icon": "mobile"}
            ),
            Channel(
                id="apple-business-chat",
                name="Apple Business Chat",
                description="Apple Business Chat integration for iOS users",
                capabilities={
                    "rich_links": ChannelCapability("Rich Links", "Rich link previews", True),
                    "payments": ChannelCapability("Payments", "Apple Pay integration", False),
                    "scheduling": ChannelCapability("Scheduling", "Calendar scheduling", False),
                    "file_sharing": ChannelCapability("File Sharing", "File sharing support", True)
                },
                supported_personas=["*"],
                artifact_types=["rich_links", "interactive_messages", "payments"],
                metadata={"color": "#000000", "icon": "apple"}
            )
        ]
        
        for channel in channels:
            self.channels[channel.id] = channel
        
        self.logger.info(f"[CHANNEL] Channel Manager initialized with {len(self.channels)} channels")
    
    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get a channel by ID"""
        return self.channels.get(channel_id)
    
    def get_all_channels(self) -> List[Channel]:
        """Get all available channels"""
        return list(self.channels.values())
    
    def get_current_channel(self) -> Channel:
        """Get the current active channel"""
        return self.channels.get(self.current_channel, self.channels["web"])
    
    def switch_channel(self, channel_id: str) -> Optional[Channel]:
        """Switch to a different channel"""
        if channel_id in self.channels:
            self.current_channel = channel_id
            channel = self.channels[channel_id]
            self.logger.info(f"[CHANNEL] Switched to channel: {channel.name} ({channel.id})")
            return channel
        else:
            self.logger.warning(f"[WARNING] Channel not found: {channel_id}")
            return None
    
    def get_channel_capabilities(self, channel_id: str) -> Dict[str, ChannelCapability]:
        """Get capabilities for a specific channel"""
        channel = self.get_channel(channel_id)
        return channel.capabilities if channel else {}
    
    def is_capability_supported(self, channel_id: str, capability_name: str) -> bool:
        """Check if a capability is supported by a channel"""
        capabilities = self.get_channel_capabilities(channel_id)
        capability = capabilities.get(capability_name)
        return capability.supported if capability else False
    
    def get_supported_artifact_types(self, channel_id: str) -> List[str]:
        """Get supported artifact types for a channel"""
        channel = self.get_channel(channel_id)
        return channel.artifact_types if channel else []
    
    def get_channel_metadata(self, channel_id: str) -> Dict[str, Any]:
        """Get metadata for a channel"""
        channel = self.get_channel(channel_id)
        return channel.metadata if channel else {}
    
    def get_channels_for_persona(self, persona_id: str) -> List[Channel]:
        """Get channels that support a specific persona"""
        return [
            channel for channel in self.channels.values()
            if "*" in channel.supported_personas or persona_id in channel.supported_personas
        ]
    
    def validate_channel_artifact(self, channel_id: str, artifact_type: str) -> bool:
        """Validate if an artifact type is supported by a channel"""
        supported_types = self.get_supported_artifact_types(channel_id)
        return artifact_type in supported_types
    
    def get_channel_summary(self, channel_id: str) -> Dict[str, Any]:
        """Get a summary of a channel"""
        channel = self.get_channel(channel_id)
        if not channel:
            return {}
        
        return {
            'id': channel.id,
            'name': channel.name,
            'description': channel.description,
            'capabilities': {
                name: {
                    'supported': cap.supported,
                    'description': cap.description
                }
                for name, cap in channel.capabilities.items()
            },
            'artifact_types': channel.artifact_types,
            'metadata': channel.metadata
        }
    
    def get_all_channel_summaries(self) -> List[Dict[str, Any]]:
        """Get summaries of all channels"""
        return [
            self.get_channel_summary(channel_id)
            for channel_id in self.channels.keys()
        ]
    
    def get_channel_stats(self) -> Dict[str, Any]:
        """Get channel statistics"""
        total_capabilities = sum(
            len(channel.capabilities) for channel in self.channels.values()
        )
        supported_capabilities = sum(
            sum(1 for cap in channel.capabilities.values() if cap.supported)
            for channel in self.channels.values()
        )
        
        return {
            'total_channels': len(self.channels),
            'total_capabilities': total_capabilities,
            'supported_capabilities': supported_capabilities,
            'current_channel': self.current_channel,
            'channels': list(self.channels.keys())
        }
