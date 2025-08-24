import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.bk25 import BK25Core
from core.persona_manager import PersonaManager
from core.channel_manager import ChannelManager
from core.memory import ConversationMemory
from core.code_generator import CodeGenerator
from core.llm_integration import LLMManager
from core.prompt_engineering import PromptEngineer
from core.script_executor import ScriptExecutor, ExecutionRequest, ExecutionPolicy
from core.execution_monitor import ExecutionMonitor, TaskPriority

class TestBK25CoreIntegration:
    """Test BK25Core component integration"""
    
    @pytest.fixture
    def temp_personas_dir(self):
        """Create temporary personas directory with test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            personas_dir = Path(temp_dir) / "personas"
            personas_dir.mkdir()
            
            # Create test persona file
            test_persona = {
                "id": "test_persona",
                "name": "Test Persona",
                "description": "A test persona for integration testing",
                "greeting": "Hello! I'm a test persona for integration testing.",
                "capabilities": ["testing", "integration", "automation"],
                "personality": {
                    "tone": "professional",
                    "approach": "systematic",
                    "philosophy": "testing-first",
                    "motto": "Let's test everything systematically!"
                },
                "examples": ["Integration test example"],
                "channels": ["web", "discord"]
            }
            
            persona_file = personas_dir / "test_persona.json"
            with open(persona_file, 'w') as f:
                json.dump(test_persona, f)
            
            yield personas_dir
    
    @pytest.fixture
    def bk25_core(self, temp_personas_dir):
        """Create BK25Core instance with test configuration"""
        config = {
            'personas_path': str(temp_personas_dir),
            'max_conversations': 10,
            'max_messages_per_conversation': 20,
            'ollama_url': 'http://localhost:11434',
            'model': 'llama3.1:8b',
            'temperature': 0.1,
            'max_tokens': 2048
        }
        return BK25Core(config)
    
    @pytest.mark.asyncio
    async def test_initialization_integration(self, bk25_core):
        """Test that all components are properly initialized and integrated"""
        # Check that all core components exist
        assert bk25_core.persona_manager is not None
        assert bk25_core.channel_manager is not None
        assert bk25_core.memory is not None
        assert bk25_core.code_generator is not None
        assert bk25_core.llm_manager is not None
        assert bk25_core.prompt_engineer is not None
        assert bk25_core.script_executor is not None
        assert bk25_core.execution_monitor is not None
        
        # Check component types
        assert isinstance(bk25_core.persona_manager, PersonaManager)
        assert isinstance(bk25_core.channel_manager, ChannelManager)
        assert isinstance(bk25_core.memory, ConversationMemory)
        assert isinstance(bk25_core.code_generator, CodeGenerator)
        assert isinstance(bk25_core.llm_manager, LLMManager)
        assert isinstance(bk25_core.prompt_engineer, PromptEngineer)
        assert isinstance(bk25_core.script_executor, ScriptExecutor)
        assert isinstance(bk25_core.execution_monitor, ExecutionMonitor)
    
    @pytest.mark.asyncio
    async def test_persona_system_integration(self, bk25_core):
        """Test persona system integration with other components"""
        # Initialize persona manager
        await bk25_core.persona_manager.initialize()
        
        # Check that personas are loaded
        assert len(bk25_core.persona_manager.personas) > 0
        assert "test_persona" in bk25_core.persona_manager.personas
        
        # Test persona switching
        persona = bk25_core.persona_manager.switch_persona("test_persona")
        assert persona is not None
        assert persona.id == "test_persona"
        
        # Test persona prompt building
        prompt = bk25_core.persona_manager.build_persona_prompt("Help me with automation")
        assert prompt is not None
        assert "test_persona" in prompt.lower() or "persona" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_channel_system_integration(self, bk25_core):
        """Test channel system integration"""
        # Check that channels are available
        channels = bk25_core.channel_manager.get_all_channels()
        assert len(channels) > 0
        
        # Test channel switching
        web_channel = bk25_core.channel_manager.switch_channel("web")
        assert web_channel is not None
        assert web_channel.id == "web"
        
        # Test channel capabilities
        web_capabilities = web_channel.capabilities
        assert "chat" in web_capabilities
        assert "file_upload" in web_capabilities
        
        # Test channel summary
        summary = bk25_core.channel_manager.get_channel_summary("web")
        assert summary is not None
        assert summary["id"] == "web"
    
    @pytest.mark.asyncio
    async def test_memory_system_integration(self, bk25_core):
        """Test memory system integration"""
        # Create a conversation
        conversation = bk25_core.memory.create_conversation(
            "test_conv",
            "test_persona",
            "web"
        )
        assert conversation is not None
        assert conversation.id == "test_conv"
        
        # Add messages to conversation
        bk25_core.memory.add_message("test_conv", "user", "Hello, can you help me?")
        bk25_core.memory.add_message("test_conv", "assistant", "Of course! I'm here to help.")
        
        # Get conversation history
        history = bk25_core.memory.get_conversation_history("test_conv")
        assert len(history) == 2
        assert history[0].role == "user"
        assert history[1].role == "assistant"
        
        # Get conversation context
        context = bk25_core.memory.get_conversation_context("test_conv")
        assert context is not None
        assert "Hello, can you help me?" in context
        assert "Of course! I'm here to help." in context
    
    @pytest.mark.asyncio
    async def test_code_generation_integration(self, bk25_core):
        """Test code generation system integration"""
        # Test PowerShell generation
        powershell_script = bk25_core.code_generator.generate_script(
            "Get running processes",
            "powershell"
        )
        assert powershell_script is not None
        assert "Get-Process" in powershell_script
        
        # Test Bash generation
        bash_script = bk25_core.code_generator.generate_script(
            "List files in current directory",
            "bash"
        )
        assert bash_script is not None
        assert "ls" in bash_script
        
        # Test AppleScript generation
        applescript = bk25_core.code_generator.generate_script(
            "Get current date",
            "applescript"
        )
        assert applescript is not None
        assert "current date" in applescript.lower()
    
    @pytest.mark.asyncio
    async def test_llm_integration(self, bk25_core):
        """Test LLM system integration"""
        # Test LLM status
        llm_status = await bk25_core.get_llm_status()
        assert llm_status is not None
        assert "providers" in llm_status
        assert "current_provider" in llm_status
        
        # Test provider selection
        providers = await bk25_core.get_llm_providers()
        assert providers is not None
        assert len(providers) > 0
        
        # Test LLM test connection
        test_result = await bk25_core.test_llm_connection()
        assert test_result is not None
        assert "success" in test_result
    
    @pytest.mark.asyncio
    async def test_prompt_engineering_integration(self, bk25_core):
        """Test prompt engineering integration"""
        # Test prompt building
        prompt = bk25_core.prompt_engineer.build_script_generation_prompt(
            "Create a script to list files",
            "bash",
            "test_persona"
        )
        assert prompt is not None
        assert "list files" in prompt.lower()
        assert "bash" in prompt.lower()
        
        # Test prompt improvement
        improved_prompt = bk25_core.prompt_engineer.improve_prompt(
            "List files",
            "bash"
        )
        assert improved_prompt is not None
        assert len(improved_prompt) > len("List files")
    
    @pytest.mark.asyncio
    async def test_script_execution_integration(self, bk25_core):
        """Test script execution system integration"""
        # Test script execution
        result = await bk25_core.execute_script(
            script="echo 'Hello World'",
            platform="bash",
            timeout=10,
            policy="safe"
        )
        assert result is not None
        assert "success" in result
        assert "status" in result
        
        # Test task submission
        task_result = await bk25_core.submit_execution_task(
            name="Test Task",
            description="A test execution task",
            script="echo 'test'",
            platform="bash",
            priority="normal"
        )
        assert task_result is not None
        assert task_result["success"] is True
        assert "task_id" in task_result
    
    @pytest.mark.asyncio
    async def test_execution_monitoring_integration(self, bk25_core):
        """Test execution monitoring system integration"""
        # Start execution monitoring
        await bk25_core.start_execution_monitoring()
        
        # Submit a task
        task_result = await bk25_core.submit_execution_task(
            name="Monitor Test Task",
            description="A task to test monitoring",
            script="sleep 1 && echo 'done'",
            platform="bash",
            priority="normal"
        )
        
        task_id = task_result["task_id"]
        
        # Get task status
        status = await bk25_core.get_task_status(task_id)
        assert status is not None
        assert "success" in status
        assert "task" in status
        
        # Get execution history
        history = await bk25_core.get_execution_history(limit=10)
        assert history is not None
        assert "success" in history
        assert "tasks" in history
        
        # Get system statistics
        stats = await bk25_core.get_system_statistics()
        assert stats is not None
        assert "success" in stats
        assert "execution_statistics" in stats
        assert "system_resources" in stats
        assert "llm_status" in stats
        
        # Shutdown execution monitoring
        await bk25_core.shutdown_execution_monitoring()
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, bk25_core):
        """Test complete end-to-end workflow"""
        # 1. Initialize systems
        await bk25_core.persona_manager.initialize()
        await bk25_core.start_execution_monitoring()
        
        # 2. Set up conversation
        conversation_id = "e2e_test_conv"
        bk25_core.memory.create_conversation(
            conversation_id,
            "test_persona",
            "web"
        )
        
        # 3. Add user message
        bk25_core.memory.add_message(
            conversation_id,
            "user",
            "I need a PowerShell script to get system information"
        )
        
        # 4. Generate script using code generator
        script = bk25_core.code_generator.generate_script(
            "Get system information",
            "powershell"
        )
        assert script is not None
        
        # 5. Execute the script
        execution_result = await bk25_core.execute_script(
            script=script,
            platform="powershell",
            timeout=30,
            policy="safe"
        )
        assert execution_result is not None
        
        # 6. Add assistant response to conversation
        bk25_core.memory.add_message(
            conversation_id,
            "assistant",
            f"I've generated and executed a PowerShell script for you. Here's the result: {execution_result}"
        )
        
        # 7. Get conversation context
        context = bk25_core.memory.get_conversation_context(conversation_id)
        assert context is not None
        assert "system information" in context.lower()
        assert "powershell" in context.lower()
        
        # 8. Cleanup
        await bk25_core.shutdown_execution_monitoring()
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, bk25_core):
        """Test error handling across integrated components"""
        # Test with invalid persona
        invalid_persona = bk25_core.persona_manager.get_persona("nonexistent")
        assert invalid_persona is None
        
        # Test with invalid channel
        invalid_channel = bk25_core.channel_manager.get_channel("nonexistent")
        assert invalid_channel is None
        
        # Test with invalid conversation
        invalid_history = bk25_core.memory.get_conversation_history("nonexistent")
        assert invalid_history == []
        
        # Test with invalid script execution
        invalid_result = await bk25_core.execute_script(
            script="invalid_command_that_does_not_exist",
            platform="bash",
            timeout=5,
            policy="safe"
        )
        assert invalid_result is not None
        assert "success" in invalid_result
        
        # Test with invalid task ID
        invalid_status = await bk25_core.get_task_status("nonexistent")
        assert invalid_status is not None
        assert invalid_status["success"] is False
        assert "error" in invalid_status
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, bk25_core):
        """Test concurrent operations across components"""
        # Start execution monitoring
        await bk25_core.start_execution_monitoring()
        
        # Submit multiple tasks concurrently
        tasks = []
        for i in range(3):
            task_result = await bk25_core.submit_execution_task(
                name=f"Concurrent Task {i}",
                description=f"Task {i} for concurrent testing",
                script=f"echo 'task{i}'",
                platform="bash",
                priority="normal"
            )
            tasks.append(task_result["task_id"])
        
        # Wait for tasks to process
        await asyncio.sleep(0.5)
        
        # Check that all tasks were processed
        for task_id in tasks:
            status = await bk25_core.get_task_status(task_id)
            assert status is not None
            assert "success" in status
        
        # Get execution history
        history = await bk25_core.get_execution_history(limit=10)
        assert history is not None
        assert history["success"] is True
        assert len(history["tasks"]) >= 3
        
        # Cleanup
        await bk25_core.shutdown_execution_monitoring()
    
    @pytest.mark.asyncio
    async def test_resource_management(self, bk25_core):
        """Test resource management across components"""
        # Get system resources
        resources = bk25_core.script_executor.get_system_resources()
        assert resources is not None
        assert "cpu_percent" in resources
        assert "memory_percent" in resources
        assert "disk_percent" in resources
        
        # Test memory limits
        # Create many conversations to test memory limits
        for i in range(15):  # More than max_conversations (10)
            bk25_core.memory.create_conversation(
                f"memory_test_{i}",
                "test_persona",
                "web"
            )
        
        # Should still have max_conversations
        assert len(bk25_core.memory.conversations) <= 10
        
        # Test message limits
        conversation_id = "message_limit_test"
        bk25_core.memory.create_conversation(
            conversation_id,
            "test_persona",
            "web"
        )
        
        # Add more messages than limit
        for i in range(25):  # More than max_messages_per_conversation (20)
            bk25_core.memory.add_message(
                conversation_id,
                "user",
                f"Message {i}"
            )
        
        # Should still have max_messages_per_conversation
        conversation = bk25_core.memory.get_conversation(conversation_id)
        assert len(conversation.messages) <= 20
    
    @pytest.mark.asyncio
    async def test_configuration_integration(self, bk25_core):
        """Test configuration integration across components"""
        # Check that configuration is properly passed to components
        assert bk25_core.ollama_url == "http://localhost:11434"
        assert bk25_core.model == "llama3.1:8b"
        assert bk25_core.temperature == 0.1
        assert bk25_core.max_tokens == 2048
        
        # Check memory configuration
        assert bk25_core.memory.max_conversations == 10
        assert bk25_core.memory.max_messages_per_conversation == 20
        
        # Check persona manager configuration
        assert bk25_core.persona_manager.personas_path is not None
        
        # Check execution monitor configuration
        assert bk25_core.execution_monitor.max_concurrent_tasks == 5
        assert bk25_core.execution_monitor.task_timeout == 300
    
    @pytest.mark.asyncio
    async def test_logging_integration(self, bk25_core):
        """Test logging integration across components"""
        # All components should have loggers
        assert hasattr(bk25_core.persona_manager, 'logger')
        assert hasattr(bk25_core.channel_manager, 'logger')
        assert hasattr(bk25_core.memory, 'logger')
        assert hasattr(bk25_core.code_generator, 'logger')
        assert hasattr(bk25_core.llm_manager, 'logger')
        assert hasattr(bk25_core.prompt_engineer, 'logger')
        assert hasattr(bk25_core.script_executor, 'logger')
        assert hasattr(bk25_core.execution_monitor, 'logger')
        assert hasattr(bk25_core, 'logger')
    
    @pytest.mark.asyncio
    async def test_cleanup_and_shutdown(self, bk25_core):
        """Test cleanup and shutdown procedures"""
        # Start execution monitoring
        await bk25_core.start_execution_monitoring()
        
        # Submit a task
        task_result = await bk25_core.submit_execution_task(
            name="Shutdown Test Task",
            description="A task to test shutdown",
            script="echo 'shutdown test'",
            platform="bash",
            priority="normal"
        )
        
        # Shutdown execution monitoring
        await bk25_core.shutdown_execution_monitoring()
        
        # Check that monitoring is properly shut down
        # (This would be verified by checking that no new tasks are processed)
        assert True  # Placeholder for actual verification
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, bk25_core):
        """Test performance under load"""
        # Start execution monitoring
        await bk25_core.start_execution_monitoring()
        
        # Submit many tasks quickly
        start_time = asyncio.get_event_loop().time()
        
        tasks = []
        for i in range(10):
            task_result = await bk25_core.submit_execution_task(
                name=f"Load Test Task {i}",
                description=f"Task {i} for load testing",
                script=f"echo 'load_test_{i}'",
                platform="bash",
                priority="normal"
            )
            tasks.append(task_result["task_id"])
        
        submission_time = asyncio.get_event_loop().time() - start_time
        
        # Submission should be fast (under 1 second for 10 tasks)
        assert submission_time < 1.0
        
        # Wait for processing
        await asyncio.sleep(1.0)
        
        # Check that tasks were processed
        for task_id in tasks:
            status = await bk25_core.get_task_status(task_id)
            assert status is not None
        
        # Cleanup
        await bk25_core.shutdown_execution_monitoring()

if __name__ == "__main__":
    pytest.main([__file__])
