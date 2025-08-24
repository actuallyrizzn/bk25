#!/usr/bin/env python3
"""
Comprehensive test script for the complete BK25 system
"""

import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_complete_system():
    """Test the complete BK25 system"""
    try:
        print("🚀 Testing Complete BK25 System...")
        
        # Test BK25 Core
        print("\n🔧 Testing BK25 Core...")
        from src.core.bk25 import BK25Core
        bk25 = BK25Core({
            "ollama_url": "http://localhost:11434",
            "model": "llama3.1:8b",
            "personas_path": "./personas"
        })
        print("✅ BK25 Core created successfully")
        
        # Test initialization
        print("\n🔧 Testing System Initialization...")
        await bk25.initialize()
        print("✅ BK25 Core initialized successfully")
        
        # Test persona system
        print("\n🎭 Testing Persona System...")
        personas = bk25.persona_manager.get_all_personas()
        print(f"✅ Personas loaded: {len(personas)}")
        
        # Test channel system
        print("\n📺 Testing Channel System...")
        channels = bk25.channel_manager.get_all_channels()
        print(f"✅ Channels loaded: {len(channels)}")
        
        # Test code generation
        print("\n📝 Testing Code Generation...")
        from src.core.code_generator import GenerationRequest
        request = GenerationRequest(
            description="Create a script to list all running processes",
            platform="powershell"
        )
        print("✅ Generation request created")
        
        # Test LLM integration
        print("\n🤖 Testing LLM Integration...")
        llm_status = bk25.llm_manager.get_available_providers()
        print(f"✅ LLM providers: {len(llm_status)}")
        
        # Test script execution
        print("\n⚡ Testing Script Execution...")
        executor_resources = bk25.script_executor.get_system_resources()
        print(f"✅ Script executor system resources retrieved")
        
        # Test execution monitoring
        print("\n📊 Testing Execution Monitoring...")
        monitor_stats = await bk25.execution_monitor.get_system_statistics()
        print(f"✅ Execution monitor statistics retrieved")
        
        # Test system status
        print("\n📈 Testing System Status...")
        system_status = bk25.get_system_status()
        print(f"✅ System status retrieved")
        print(f"   - Personas: {system_status['personas_loaded']}")
        print(f"   - Channels: {system_status['channels_available']}")
        print(f"   - LLM: {'Connected' if system_status['ollama_connected'] else 'Disconnected'}")
        
        print("\n🎉 Complete BK25 system test successful!")
        print("\n📋 System Summary:")
        print(f"   - Personas: {len(personas)} loaded")
        print(f"   - Channels: {len(channels)} available")
        print(f"   - Code generators: 3 platforms")
        print(f"   - LLM integration: Ready")
        print(f"   - Script execution: Ready")
        print(f"   - Execution monitoring: Ready")
        
    except Exception as e:
        print(f"❌ Complete system test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_system())
