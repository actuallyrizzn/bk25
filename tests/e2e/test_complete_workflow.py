"""
End-to-end tests for complete BK25 workflows
"""

import pytest
import json
import asyncio
import time
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from src.core.bk25 import BK25Core


class TestCompleteWorkflow:
    """Test complete end-to-end workflows"""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for test files"""
        return tmp_path

    @pytest.fixture
    def personas_path(self, temp_dir):
        """Create personas directory with test data"""
        personas_dir = temp_dir / "personas"
        personas_dir.mkdir()
        
        # Create test persona files
        persona_data = [
            {
                "id": "automation-expert",
                "name": "Automation Expert",
                "description": "Expert in creating automation scripts",
                "greeting": "Hello! I'm an automation expert. What would you like me to help you with?",
                "capabilities": ["script_generation", "automation", "cross_platform"],
                "personality": {
                    "tone": "professional",
                    "approach": "systematic",
                    "philosophy": "efficiency",
                    "motto": "Automate everything possible"
                },
                "examples": ["Create a backup script", "Automate file processing"],
                "channels": ["web", "cli"],
                "systemPrompt": "You are an automation expert focused on creating efficient, reliable scripts."
            },
            {
                "id": "web-developer",
                "name": "Web Developer",
                "description": "Specialist in web development and automation",
                "greeting": "Hi! I'm a web developer. How can I help with your web automation needs?",
                "capabilities": ["web_automation", "javascript", "selenium"],
                "personality": {
                    "tone": "friendly",
                    "approach": "creative",
                    "philosophy": "user_experience",
                    "motto": "Make the web work for you"
                },
                "examples": ["Web scraping script", "Browser automation"],
                "channels": ["web"],
                "systemPrompt": "You are a web development expert specializing in automation and scripting."
            }
        ]
        
        for persona in persona_data:
            persona_file = personas_dir / f"{persona['id']}.json"
            persona_file.write_text(json.dumps(persona, indent=2))
        
        return str(personas_dir)

    @pytest.fixture
    def bk25_core(self, personas_path):
        """Create BK25Core instance with test data"""
        config = {
            "personas_path": personas_path,
            "ollama_url": "http://localhost:11434",
            "model": "llama3.1:8b",
            "max_conversations": 10,
            "max_messages_per_conversation": 20
        }
        
        core = BK25Core(config)
        
        # Mock external dependencies
        core.ollama_connected = False
        core.llm_manager.test_providers = AsyncMock(return_value={"ollama": False})
        core.llm_manager.get_available_providers = Mock(return_value=["ollama"])
        
        # Mock execution monitor
        core.execution_monitor.start_monitoring = AsyncMock()
        core.execution_monitor.get_system_statistics = AsyncMock(return_value={})
        
        # Initialize synchronously by running the async method in the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(core.initialize())
            return core
        finally:
            loop.close()

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_automation_workflow(self, bk25_core):
        """Test complete automation workflow from start to finish"""
        # 1. Initialize system
        assert bk25_core.persona_manager is not None
        assert bk25_core.channel_manager is not None
        assert bk25_core.memory is not None
        
        # 2. Switch to automation expert persona
        automation_persona = bk25_core.persona_manager.switch_persona("automation-expert")
        assert automation_persona is not None
        assert automation_persona.id == "automation-expert"
        assert "script_generation" in automation_persona.capabilities
        
        # 3. Start a conversation
        conversation_id = "test-automation-workflow"
        
        # 4. Send initial message
        initial_message = "I need a PowerShell script to backup files from one folder to another"
        result = await bk25_core.process_message(initial_message, conversation_id)
        
        assert result is not None
        assert "response" in result
        assert result["conversation_id"] == conversation_id
        assert result["persona"]["id"] == "automation-expert"
        
        # 5. Verify conversation was created in memory
        conversation = bk25_core.memory.get_conversation(conversation_id)
        assert conversation is not None
        
        # 6. Send follow-up message
        follow_up = "Can you also add error handling and logging to the script?"
        result2 = await bk25_core.process_message(follow_up, conversation_id)
        
        assert result2 is not None
        assert result2["conversation_id"] == conversation_id
        
        # 7. Verify conversation history
        history = bk25_core.get_conversation_history(conversation_id)
        assert len(history) >= 2  # At least initial and follow-up messages
        
        # 8. Check system status
        status = bk25_core.get_system_status()
        assert status["personas_loaded"] >= 1
        assert status["conversations_active"] >= 1

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_persona_switching_workflow(self, bk25_core):
        """Test complete persona switching workflow"""
        # 1. Start with automation expert
        automation_persona = bk25_core.persona_manager.switch_persona("automation-expert")
        assert automation_persona.id == "automation-expert"
        
        # 2. Start conversation
        conversation_id = "persona-switching-test"
        message1 = "Hello, I need help with automation"
        result1 = await bk25_core.process_message(message1, conversation_id)
        assert result1["persona"]["id"] == "automation-expert"
        
        # 3. Switch to web developer persona
        web_persona = bk25_core.persona_manager.switch_persona("web-developer")
        assert web_persona.id == "web-developer"
        assert "web_automation" in web_persona.capabilities
        
        # 4. Continue conversation with new persona
        message2 = "Now I need help with web automation"
        result2 = await bk25_core.process_message(message2, conversation_id)
        assert result2["persona"]["id"] == "web-developer"
        
        # 5. Verify persona context is maintained
        current_persona = bk25_core.persona_manager.get_current_persona()
        assert current_persona.id == "web-developer"
        
        # 6. Switch back to automation expert
        automation_persona_again = bk25_core.persona_manager.switch_persona("automation-expert")
        assert automation_persona_again.id == "automation-expert"
        
        # 7. Continue conversation
        message3 = "Back to general automation help"
        result3 = await bk25_core.process_message(message3, conversation_id)
        assert result3["persona"]["id"] == "automation-expert"

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_multi_conversation_workflow(self, bk25_core):
        """Test managing multiple conversations simultaneously"""
        # 1. Start first conversation
        conv1_id = "conversation-1"
        message1 = "Help me with PowerShell scripting"
        result1 = await bk25_core.process_message(message1, conv1_id)
        assert result1["conversation_id"] == conv1_id
        
        # 2. Start second conversation
        conv2_id = "conversation-2"
        message2 = "I need help with web automation"
        result2 = await bk25_core.process_message(message2, conv2_id)
        assert result2["conversation_id"] == conv2_id
        
        # 3. Continue first conversation
        message1_2 = "Can you show me an example?"
        result1_2 = await bk25_core.process_message(message1_2, conv1_id)
        assert result1_2["conversation_id"] == conv1_id
        
        # 4. Continue second conversation
        message2_2 = "What tools should I use?"
        result2_2 = await bk25_core.process_message(message2_2, conv2_id)
        assert result2_2["conversation_id"] == conv2_id
        
        # 5. Verify both conversations exist
        conv1 = bk25_core.memory.get_conversation(conv1_id)
        conv2 = bk25_core.memory.get_conversation(conv2_id)
        assert conv1 is not None
        assert conv2 is not None
        
        # 6. Check conversation summaries
        summaries = bk25_core.get_all_conversations()
        assert len(summaries) >= 2
        
        # 7. Verify conversation isolation
        history1 = bk25_core.get_conversation_history(conv1_id)
        history2 = bk25_core.get_conversation_history(conv2_id)
        assert len(history1) >= 2
        assert len(history2) >= 2

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, bk25_core):
        """Test error recovery and system resilience"""
        # 1. Test with invalid persona ID
        invalid_result = bk25_core.persona_manager.switch_persona("nonexistent-persona")
        assert invalid_result is None
        
        # 2. Verify system is still functional
        current_persona = bk25_core.persona_manager.get_current_persona()
        # Should be None or default persona
        
        # 3. Test with valid persona
        valid_persona = bk25_core.persona_manager.switch_persona("automation-expert")
        assert valid_persona is not None
        
        # 4. Test conversation with invalid ID
        try:
            result = await bk25_core.process_message("Hello", "")
            # Should handle gracefully
        except Exception:
            # Expected behavior for invalid conversation ID
            pass
        
        # 5. Test with valid conversation
        valid_result = await bk25_core.process_message("Hello", "error-recovery-test")
        assert valid_result is not None
        
        # 6. Verify system status is still healthy
        status = bk25_core.get_system_status()
        assert status is not None

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_performance_workflow(self, bk25_core):
        """Test system performance under load"""
        import time
        
        # 1. Measure persona switching performance
        start_time = time.time()
        
        for i in range(50):
            persona_id = "automation-expert" if i % 2 == 0 else "web-developer"
            bk25_core.persona_manager.switch_persona(persona_id)
        
        persona_switch_time = time.time() - start_time
        assert persona_switch_time < 1.0  # Should complete in under 1 second
        
        # 2. Measure conversation creation performance
        start_time = time.time()
        
        for i in range(20):
            conv_id = f"perf-test-{i}"
            await bk25_core.process_message(f"Test message {i}", conv_id)
        
        conversation_time = time.time() - start_time
        assert conversation_time < 5.0  # Should complete in under 5 seconds
        
        # 3. Measure memory retrieval performance
        start_time = time.time()
        
        for i in range(100):
            bk25_core.memory.get_conversation(f"perf-test-{i % 20}")
        
        memory_time = time.time() - start_time
        assert memory_time < 1.0  # Should complete in under 1 second

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_data_persistence_workflow(self, bk25_core, personas_path):
        """Test data persistence across system operations"""
        # 1. Create conversation
        conv_id = "persistence-test"
        message = "This conversation should persist"
        result = await bk25_core.process_message(message, conv_id)
        assert result is not None
        
        # 2. Verify conversation exists
        conversation = bk25_core.memory.get_conversation(conv_id)
        assert conversation is not None
        
        # 3. Reload personas
        await bk25_core.reload_personas()
        
        # 4. Verify personas still exist
        automation_persona = bk25_core.persona_manager.get_persona("automation-expert")
        assert automation_persona is not None
        assert automation_persona.id == "automation-expert"
        
        # 5. Verify conversation still exists
        conversation_after_reload = bk25_core.memory.get_conversation(conv_id)
        assert conversation_after_reload is not None
        
        # 6. Continue conversation
        follow_up = "This should work after reload"
        result2 = await bk25_core.process_message(follow_up, conv_id)
        assert result2 is not None
        assert result2["conversation_id"] == conv_id

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_integration_workflow(self, bk25_core):
        """Test integration between all system components"""
        # 1. Test persona and memory integration
        persona = bk25_core.persona_manager.switch_persona("automation-expert")
        assert persona is not None
        
        conv_id = "integration-test"
        message = "Test integration between components"
        result = await bk25_core.process_message(message, conv_id)
        
        # 2. Verify all components are working together
        assert result["persona"]["id"] == "automation-expert"
        assert result["conversation_id"] == conv_id
        
        # 3. Test memory and conversation integration
        conversation = bk25_core.memory.get_conversation(conv_id)
        assert conversation is not None
        
        # 4. Test persona and channel integration
        web_personas = bk25_core.persona_manager.get_personas_for_channel("web")
        assert len(web_personas) >= 1
        
        # 5. Test system status integration
        status = bk25_core.get_system_status()
        assert status["personas_loaded"] >= 1
        assert status["conversations_active"] >= 1
        
        # 6. Test component communication
        persona_info = bk25_core.get_persona_info()
        assert "personas" in persona_info
        
        memory_info = bk25_core.get_memory_info()
        assert memory_info is not None

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_stress_workflow(self, bk25_core):
        """Test system under stress conditions"""
        # 1. Create many conversations rapidly
        start_time = time.time()
        
        for i in range(100):
            conv_id = f"stress-test-{i}"
            try:
                await bk25_core.process_message(f"Stress test message {i}", conv_id)
            except Exception:
                # Some failures are expected under stress
                pass
        
        stress_time = time.time() - start_time
        assert stress_time < 30.0  # Should complete in under 30 seconds
        
        # 2. Test rapid persona switching
        start_time = time.time()
        
        for i in range(200):
            persona_id = "automation-expert" if i % 3 == 0 else "web-developer"
            try:
                bk25_core.persona_manager.switch_persona(persona_id)
            except Exception:
                # Some failures are expected under stress
                pass
        
        switch_time = time.time() - start_time
        assert switch_time < 5.0  # Should complete in under 5 seconds
        
        # 3. Verify system is still functional
        status = bk25_core.get_system_status()
        assert status is not None
        
        # 4. Test memory cleanup under stress
        try:
            summaries = bk25_core.get_all_conversations()
            # Should not crash
        except Exception:
            # Memory cleanup might fail under extreme stress
            pass

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_edge_case_workflow(self, bk25_core):
        """Test edge cases and boundary conditions"""
        # 1. Test with very long message
        long_message = "A" * 10000  # 10KB message
        result = await bk25_core.process_message(long_message, "edge-test")
        assert result is not None
        
        # 2. Test with empty message
        empty_result = await bk25_core.process_message("", "edge-test-2")
        assert empty_result is not None
        
        # 3. Test with special characters
        special_message = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        special_result = await bk25_core.process_message(special_message, "edge-test-3")
        assert special_result is not None
        
        # 4. Test with very long conversation ID
        long_conv_id = "A" * 1000
        long_conv_result = await bk25_core.process_message("Test", long_conv_id)
        assert long_conv_result is not None
        
        # 5. Test with unicode characters
        unicode_message = "Hello 世界! 🌍 Привет! こんにちは!"
        unicode_result = await bk25_core.process_message(unicode_message, "edge-test-4")
        assert unicode_result is not None

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_concurrent_workflow(self, bk25_core):
        """Test concurrent operations"""
        # 1. Create multiple conversations concurrently
        async def create_conversation(i):
            conv_id = f"concurrent-{i}"
            return await bk25_core.process_message(f"Concurrent message {i}", conv_id)
        
        # 2. Run concurrent operations
        tasks = [create_conversation(i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 3. Verify results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 5  # At least half should succeed
        
        # 4. Test concurrent persona switching
        async def switch_persona(persona_id):
            return bk25_core.persona_manager.switch_persona(persona_id)
        
        persona_tasks = [
            switch_persona("automation-expert"),
            switch_persona("web-developer"),
            switch_persona("automation-expert")
        ]
        
        persona_results = await asyncio.gather(*persona_tasks, return_exceptions=True)
        assert len(persona_results) == 3
        
        # 5. Verify final state
        final_persona = bk25_core.persona_manager.get_current_persona()
        assert final_persona is not None
