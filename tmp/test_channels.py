#!/usr/bin/env python3
"""
Test script for channel system
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_channels():
    """Test channel loading and management"""
    try:
        print("🔍 Importing ChannelManager...")
        from src.core.channel_manager import ChannelManager
        print("✅ ChannelManager imported successfully")
        
        print("📺 Testing Channel Manager...")
        
        # Initialize channel manager
        print("🔧 Creating ChannelManager instance...")
        cm = ChannelManager()
        print("✅ ChannelManager instance created")
        
        # Check channels loaded
        print("🔍 Getting all channels...")
        channels = cm.get_all_channels()
        print(f"✅ Channels loaded: {len(channels)}")
        
        # List all channels
        for i, channel in enumerate(channels):
            print(f"  {i+1}. {channel.name} ({channel.id})")
            print(f"     Description: {channel.description}")
            print(f"     Capabilities: {len(channel.capabilities)}")
            print(f"     Artifact types: {channel.artifact_types}")
            print()
        
        # Check current channel
        print("🔍 Getting current channel...")
        current = cm.get_current_channel()
        print(f"✅ Current channel: {current.name} ({current.id})")
        
        # Test channel switching
        if len(channels) > 1:
            print("🔄 Testing channel switching...")
            first_channel = channels[0]
            cm.switch_channel(first_channel.id)
            print(f"✅ Switched to: {cm.get_current_channel().name}")
        
        print("\n🎉 Channel system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Channel test failed: {e}")
        import traceback
        traceback.print_exc()

def test_channel_modules():
    """Test individual channel modules"""
    try:
        print("\n🔍 Testing Channel Modules...")
        
        # Test Slack channel
        from src.core.channels.slack import SlackChannel
        slack = SlackChannel()
        print(f"✅ Slack channel: {slack.name} ({slack.id})")
        
        # Test Teams channel
        from src.core.channels.teams import TeamsChannel
        teams = TeamsChannel()
        print(f"✅ Teams channel: {teams.name} ({teams.id})")
        
        # Test Discord channel
        from src.core.channels.discord import DiscordChannel
        discord = DiscordChannel()
        print(f"✅ Discord channel: {discord.name} ({discord.id})")
        
        # Test Web channel
        from src.core.channels.web import WebChannel
        web = WebChannel()
        print(f"✅ Web channel: {web.name} ({web.id})")
        
        print("🎉 All channel modules imported successfully!")
        
    except Exception as e:
        print(f"❌ Channel module test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_channels()
    test_channel_modules()
