"""
Phase 2 Tests: Persona System & Memory

These tests verify that the persona system, channel management, and conversation memory
are working correctly.
"""

import pytest
import sys
import asyncio
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_persona_manager_creation():
    """Test that PersonaManager can be created"""
    try:
        from core.persona_manager import PersonaManager
        pm = PersonaManager()
        assert pm is not None
        assert hasattr(pm, 'personas')
        assert hasattr(pm, 'current_persona')
        print("✅ PersonaManager creation test passed")
        return True
    except Exception as e:
        pytest.fail(f"PersonaManager creation failed: {e}")

def test_channel_manager_creation():
    """Test that ChannelManager can be created"""
    try:
        from core.channel_manager import ChannelManager
        cm = ChannelManager()
        assert cm is not None
        assert hasattr(cm, 'channels')
        assert hasattr(cm, 'current_channel')
        print("✅ ChannelManager creation test passed")
        return True
    except Exception as e:
        pytest.fail(f"ChannelManager creation failed: {e}")

def test_memory_creation():
    """Test that ConversationMemory can be created"""
    try:
        from core.memory import ConversationMemory
        memory = ConversationMemory()
        assert memory is not None
        assert hasattr(memory, 'conversations')
        print("✅ ConversationMemory creation test passed")
        return True
    except Exception as e:
        pytest.fail(f"ConversationMemory creation failed: {e}")

def test_bk25_core_creation():
    """Test that BK25Core can be created"""
    try:
        from core.bk25 import BK25Core
        core = BK25Core()
        assert core is not None
        assert hasattr(core, 'persona_manager')
        assert hasattr(core, 'channel_manager')
        assert hasattr(core, 'memory')
        print("✅ BK25Core creation test passed")
        return True
    except Exception as e:
        pytest.fail(f"BK25Core creation failed: {e}")

def test_persona_loading():
    """Test that personas can be loaded from JSON files"""
    try:
        from core.persona_manager import PersonaManager
        pm = PersonaManager()
        
        # Check if personas directory exists
        personas_path = Path("personas")
        assert personas_path.exists(), "Personas directory not found"
        
        # Check if persona files exist
        persona_files = list(personas_path.glob("*.json"))
        assert len(persona_files) > 0, "No persona files found"
        
        print(f"✅ Found {len(persona_files)} persona files")
        return True
    except Exception as e:
        pytest.fail(f"Persona loading test failed: {e}")

def test_channel_initialization():
    """Test that channels are properly initialized"""
    try:
        from core.channel_manager import ChannelManager
        cm = ChannelManager()
        
        # Check that channels were initialized
        assert len(cm.channels) > 0, "No channels initialized"
        
        # Check for expected channels
        expected_channels = ['web', 'slack', 'teams', 'discord', 'twitch', 'whatsapp', 'apple-business-chat']
        for channel_id in expected_channels:
            assert channel_id in cm.channels, f"Channel {channel_id} not found"
        
        print(f"✅ {len(cm.channels)} channels initialized correctly")
        return True
    except Exception as e:
        pytest.fail(f"Channel initialization test failed: {e}")

def test_persona_validation():
    """Test persona validation logic"""
    try:
        from core.persona_manager import PersonaManager
        pm = PersonaManager()
        
        # Test valid persona data
        valid_persona = {
            'id': 'test',
            'name': 'Test Persona',
            'description': 'A test persona',
            'greeting': 'Hello!',
            'systemPrompt': 'You are a test persona'
        }
        
        assert pm.validate_persona(valid_persona), "Valid persona should pass validation"
        
        # Test invalid persona data
        invalid_persona = {
            'id': 'test',
            'name': 'Test Persona'
            # Missing required fields
        }
        
        assert not pm.validate_persona(invalid_persona), "Invalid persona should fail validation"
        
        print("✅ Persona validation test passed")
        return True
    except Exception as e:
        pytest.fail(f"Persona validation test failed: {e}")

def test_channel_capabilities():
    """Test channel capability system"""
    try:
        from core.channel_manager import ChannelManager
        cm = ChannelManager()
        
        # Test web channel capabilities
        web_channel = cm.get_channel('web')
        assert web_channel is not None, "Web channel not found"
        
        # Check for expected capabilities
        assert 'rich_text' in web_channel.capabilities, "Web channel missing rich_text capability"
        assert 'custom_ui' in web_channel.capabilities, "Web channel missing custom_ui capability"
        
        # Test capability checking
        assert cm.is_capability_supported('web', 'rich_text'), "Web channel should support rich_text"
        assert not cm.is_capability_supported('web', 'nonexistent'), "Web channel should not support nonexistent capability"
        
        print("✅ Channel capabilities test passed")
        return True
    except Exception as e:
        pytest.fail(f"Channel capabilities test failed: {e}")

def test_memory_operations():
    """Test conversation memory operations"""
    try:
        from core.memory import ConversationMemory
        memory = ConversationMemory()
        
        # Test conversation creation
        conv = memory.create_conversation('test_conv', 'vanilla', 'web')
        assert conv is not None, "Conversation creation failed"
        assert conv.id == 'test_conv', "Conversation ID mismatch"
        
        # Test message addition
        success = memory.add_message('test_conv', 'user', 'Hello!')
        assert success, "Message addition failed"
        
        # Test conversation retrieval
        retrieved_conv = memory.get_conversation('test_conv')
        assert retrieved_conv is not None, "Conversation retrieval failed"
        assert len(retrieved_conv.messages) == 1, "Message count mismatch"
        
        # Test conversation history
        history = memory.get_conversation_history('test_conv')
        assert len(history) == 1, "History count mismatch"
        assert history[0].content == 'Hello!', "Message content mismatch"
        
        print("✅ Memory operations test passed")
        return True
    except Exception as e:
        pytest.fail(f"Memory operations test failed: {e}")

async def test_bk25_initialization():
    """Test BK25 core initialization"""
    try:
        from core.bk25 import BK25Core
        core = BK25Core()
        
        # Test initialization
        await core.initialize()
        
        # Check that components are initialized
        assert len(core.persona_manager.get_all_personas()) > 0, "No personas loaded"
        assert len(core.channel_manager.get_all_channels()) > 0, "No channels loaded"
        
        print("✅ BK25 initialization test passed")
        return True
    except Exception as e:
        pytest.fail(f"BK25 initialization test failed: {e}")

def main():
    """Run all Phase 2 tests"""
    print("🧪 Running Phase 2 Tests: Persona System & Memory")
    print("=" * 60)
    
    tests = [
        ("PersonaManager Creation", test_persona_manager_creation),
        ("ChannelManager Creation", test_channel_manager_creation),
        ("ConversationMemory Creation", test_memory_creation),
        ("BK25Core Creation", test_bk25_core_creation),
        ("Persona Loading", test_persona_loading),
        ("Channel Initialization", test_channel_initialization),
        ("Persona Validation", test_persona_validation),
        ("Channel Capabilities", test_channel_capabilities),
        ("Memory Operations", test_memory_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    # Run async test
    print(f"\n🔍 Running: BK25 Initialization")
    try:
        asyncio.run(test_bk25_initialization())
        passed += 1
    except Exception as e:
        print(f"❌ BK25 Initialization failed: {e}")
    
    total += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Phase 2 tests passed! The persona system is working correctly.")
        return True
    else:
        print(f"\n❌ {total - passed} tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
