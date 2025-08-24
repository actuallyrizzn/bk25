#!/usr/bin/env python3
"""
Test script for channel modules
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_channel_modules():
    """Test individual channel modules"""
    try:
        print("🔍 Testing Channel Modules...")
        
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
    test_channel_modules()
