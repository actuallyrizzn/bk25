"""
BK25 Channel Modules

This package contains channel-specific modules for artifact generation and simulation.
Each channel provides platform-specific formatting and capabilities.
"""

__version__ = "1.0.0"
__author__ = "Toilville (Peter Swimm)"
__description__ = "Multi-channel simulation and artifact generation"

from .base import BaseChannel
from .web import WebChannel
from .slack import SlackChannel
from .teams import TeamsChannel
from .discord import DiscordChannel
from .twitch import TwitchChannel
from .whatsapp import WhatsAppChannel
from .apple_business_chat import AppleBusinessChatChannel

__all__ = [
    'BaseChannel',
    'WebChannel',
    'SlackChannel',
    'TeamsChannel',
    'DiscordChannel',
    'TwitchChannel',
    'WhatsAppChannel',
    'AppleBusinessChatChannel'
]
