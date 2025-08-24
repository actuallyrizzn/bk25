import pytest
import asyncio
import platform
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.script_executor import (
    ScriptExecutor, ExecutionRequest, ExecutionResult, 
    ExecutionStatus, ExecutionPolicy, ExecutionMetrics
)

class TestExecutionStatus:
    """Test ExecutionStatus enum"""
    
    def test_execution_status_values(self):
        """Test ExecutionStatus enum values"""
        assert ExecutionStatus.PENDING == "pending"
        assert ExecutionStatus.RUNNING == "running"
        assert ExecutionStatus.COMPLETED == "completed"
        assert ExecutionStatus.FAILED == "failed"
        assert ExecutionStatus.TIMEOUT == "timeout"
        assert ExecutionStatus.CANCELLED == "cancelled"

class TestExecutionPolicy:
    """Test ExecutionPolicy enum"""
    
    def test_execution_policy_values(self):
        """Test ExecutionPolicy enum values"""
        assert ExecutionPolicy.SAFE == "safe"
        assert ExecutionPolicy.RESTRICTED == "restricted"
        assert ExecutionPolicy.STANDARD == "standard"
        assert ExecutionPolicy.ELEVATED == "elevated"

class TestExecutionRequest:
    """Test ExecutionRequest dataclass"""
    
    def test_execution_request_creation(self):
        """Test creating an ExecutionRequest instance"""
        request = ExecutionRequest(
            script="Get-Process",
            platform="powershell",
            filename="test.ps1",
            working_directory="/tmp",
            timeout=60,
            policy=ExecutionPolicy.SAFE,
            environment={"TEST_VAR": "test_value"},
            user_input="test input"
        )
        
        assert request.script == "Get-Process"
        assert request.platform == "powershell"
        assert request.filename == "test.ps1"
        assert request.working_directory == "/tmp"
        assert request.timeout == 60
        assert request.policy == ExecutionPolicy.SAFE
        assert request.environment["TEST_VAR"] == "test_value"
        assert request.user_input == "test input"
    
    def test_execution_request_defaults(self):
        """Test ExecutionRequest with default values"""
        request = ExecutionRequest(
            script="ls",
            platform="bash"
        )
        
        assert request.script == "ls"
        assert request.platform == "bash"
        assert request.filename is None
        assert request.working_directory is None
        assert request.timeout == 300
        assert request.policy == ExecutionPolicy.SAFE
        assert request.environment is None
        assert request.user_input is None

class TestExecutionResult:
    """Test ExecutionResult dataclass"""
    
    def test_execution_result_creation(self):
        """Test creating an ExecutionResult instance"""
        result = ExecutionResult(
            success=True,
            status=ExecutionStatus.COMPLETED,
            output="Process list retrieved",
            error=None,
            exit_code=0,
            execution_time=1.5,
            memory_usage=50.2,
            cpu_usage=25.0,
            metadata={"pid": 12345, "platform": "powershell"}
        )
        
        assert result.success is True
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output == "Process list retrieved"
        assert result.error is None
        assert result.exit_code == 0
        assert result.execution_time == 1.5
        assert result.memory_usage == 50.2
        assert result.cpu_usage == 25.0
        assert result.metadata["pid"] == 12345
    
    def test_execution_result_defaults(self):
        """Test ExecutionResult with default values"""
        result = ExecutionResult(
            success=False,
            status=ExecutionStatus.FAILED
        )
        
        assert result.success is False
        assert result.status == ExecutionStatus.FAILED
        assert result.output is None
        assert result.error is None
        assert result.exit_code is None
        assert result.execution_time == 0.0
        assert result.memory_usage is None
        assert result.cpu_usage is None
        assert result.metadata is None

class TestExecutionMetrics:
    """Test ExecutionMetrics dataclass"""
    
    def test_execution_metrics_creation(self):
        """Test creating an ExecutionMetrics instance"""
        metrics = ExecutionMetrics(
            start_time=1000.0,
            end_time=1005.0,
            total_time=5.0,
            peak_memory=100.5,
            average_cpu=30.2,
            io_operations=150,
            network_connections=2
        )
        
        assert metrics.start_time == 1000.0
        assert metrics.end_time == 1005.0
        assert metrics.total_time == 5.0
        assert metrics.peak_memory == 100.5
        assert metrics.average_cpu == 30.2
        assert metrics.io_operations == 150
        assert metrics.network_connections == 2

class TestScriptExecutor:
    """Test ScriptExecutor class"""
    
    @pytest.fixture
    def script_executor(self):
        """Create ScriptExecutor instance"""
        return ScriptExecutor()
    
    def test_initialization(self, script_executor):
        """Test ScriptExecutor initialization"""
        assert script_executor.config == {}
        assert script_executor.safe_commands is not None
        assert script_executor.blocked_commands is not None
        assert script_executor.platform_config is not None
        
        # Check platform-specific config
        if platform.system().lower() == "windows":
            assert "windows" in script_executor.platform_config
        elif platform.system().lower() == "darwin":
            assert "darwin" in script_executor.platform_config
        elif platform.system().lower() == "linux":
            assert "linux" in script_executor.platform_config
    
    def test_safe_commands_structure(self, script_executor):
        """Test safe commands structure"""
        assert "powershell" in script_executor.safe_commands
        assert "applescript" in script_executor.safe_commands
        assert "bash" in script_executor.safe_commands
        
        # Check that safe commands are lists
        for platform, commands in script_executor.safe_commands.items():
            assert isinstance(commands, list)
            assert len(commands) > 0
    
    def test_blocked_commands_structure(self, script_executor):
        """Test blocked commands structure"""
        assert "powershell" in script_executor.blocked_commands
        assert "applescript" in script_executor.blocked_commands
        assert "bash" in script_executor.blocked_commands
        
        # Check that blocked commands are lists
        for platform, commands in script_executor.blocked_commands.items():
            assert isinstance(commands, list)
            assert len(commands) > 0
    
    def test_platform_config_structure(self, script_executor):
        """Test platform configuration structure"""
        for platform_name, config in script_executor.platform_config.items():
            assert "shell" in config
            assert "args" in config
            assert "encoding" in config
            assert isinstance(config["shell"], str)
            assert isinstance(config["args"], list)
            assert isinstance(config["encoding"], str)
    
    @pytest.mark.asyncio
    async def test_execute_script_success(self, script_executor):
        """Test successful script execution"""
        request = ExecutionRequest(
            script="echo 'Hello World'",
            platform="bash",
            timeout=10
        )
        
        # Mock subprocess execution
        with patch('asyncio.create_subprocess_exec') as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"Hello World\n", b"")
            mock_process.returncode = 0
            mock_process.pid = 12345
            
            mock_create_subprocess.return_value = mock_process
            
            result = await script_executor.execute_script(request)
            
            assert result.success is True
            assert result.status == ExecutionStatus.COMPLETED
            assert result.output == "Hello World\n"
            assert result.error is None
            assert result.exit_code == 0
            assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_execute_script_failure(self, script_executor):
        """Test failed script execution"""
        request = ExecutionRequest(
            script="invalid_command",
            platform="bash",
            timeout=10
        )
        
        # Mock subprocess execution
        with patch('asyncio.create_subprocess_exec') as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"command not found")
            mock_process.returncode = 127
            mock_process.pid = 12345
            
            mock_create_subprocess.return_value = mock_process
            
            result = await script_executor.execute_script(request)
            
            assert result.success is False
            assert result.status == ExecutionStatus.FAILED
            assert result.output is None
            assert result.error == "command not found"
            assert result.exit_code == 127
            assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_execute_script_timeout(self, script_executor):
        """Test script execution timeout"""
        request = ExecutionRequest(
            script="sleep 30",
            platform="bash",
            timeout=1
        )
        
        # Mock subprocess execution with timeout
        with patch('asyncio.create_subprocess_exec') as mock_create_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.side_effect = asyncio.TimeoutError()
            mock_process.pid = 12345
            
            mock_create_subprocess.return_value = mock_process
            
            result = await script_executor.execute_script(request)
            
            assert result.success is False
            assert result.status == ExecutionStatus.TIMEOUT
            assert "timeout" in result.error.lower()
            assert result.execution_time > 0
    
    def test_validate_execution_request_valid(self, script_executor):
        """Test validation of valid execution request"""
        request = ExecutionRequest(
            script="Get-Process",
            platform="powershell",
            timeout=300
        )
        
        validation = script_executor._validate_execution_request(request)
        assert validation["valid"] is True
    
    def test_validate_execution_request_unsupported_platform(self, script_executor):
        """Test validation with unsupported platform"""
        request = ExecutionRequest(
            script="test",
            platform="unsupported",
            timeout=300
        )
        
        validation = script_executor._validate_execution_request(request)
        assert validation["valid"] is False
        assert "unsupported platform" in validation["reason"]
    
    def test_validate_execution_request_blocked_commands(self, script_executor):
        """Test validation with blocked commands"""
        request = ExecutionRequest(
            script="Remove-Item -Recurse -Force C:\\",
            platform="powershell",
            timeout=300
        )
        
        validation = script_executor._validate_execution_request(request)
        assert validation["valid"] is False
        assert "blocked commands" in validation["reason"]
    
    def test_validate_execution_request_safe_policy_violation(self, script_executor):
        """Test validation with safe policy violation"""
        request = ExecutionRequest(
            script="some_unknown_command",
            platform="bash",
            timeout=300,
            policy=ExecutionPolicy.SAFE
        )
        
        validation = script_executor._validate_execution_request(request)
        assert validation["valid"] is False
        assert "safe policy" in validation["reason"]
    
    def test_validate_execution_request_timeout_exceeded(self, script_executor):
        """Test validation with timeout exceeding limit"""
        request = ExecutionRequest(
            script="Get-Process",
            platform="powershell",
            timeout=7200  # 2 hours
        )
        
        validation = script_executor._validate_execution_request(request)
        assert validation["valid"] is False
        assert "timeout exceeds maximum" in validation["reason"]
    
    def test_check_blocked_commands_powershell(self, script_executor):
        """Test blocked command detection for PowerShell"""
        script = "Remove-Item C:\\temp, Stop-Process -Name notepad"
        blocked = script_executor._check_blocked_commands(script, "powershell")
        
        assert "Remove-Item" in blocked
        assert "Stop-Process" in blocked
        assert len(blocked) == 2
    
    def test_check_blocked_commands_bash(self, script_executor):
        """Test blocked command detection for Bash"""
        script = "rm -rf /tmp, shutdown -h now"
        blocked = script_executor._check_blocked_commands(script, "bash")
        
        assert "rm" in blocked
        assert "shutdown" in blocked
        assert len(blocked) == 2
    
    def test_check_blocked_commands_applescript(self, script_executor):
        """Test blocked command detection for AppleScript"""
        script = "delete file \"test.txt\", restart computer"
        blocked = script_executor._check_blocked_commands(script, "applescript")
        
        assert "delete" in blocked
        assert "restart" in blocked
        assert len(blocked) == 2
    
    def test_check_safe_commands_only_valid(self, script_executor):
        """Test safe command validation with valid commands"""
        script = "Get-Process, Get-Service, Get-Date"
        is_safe = script_executor._check_safe_commands_only(script, "powershell")
        assert is_safe is True
    
    def test_check_safe_commands_only_invalid(self, script_executor):
        """Test safe command validation with invalid commands"""
        script = "some_unknown_command, another_unknown"
        is_safe = script_executor._check_safe_commands_only(script, "bash")
        assert is_safe is False
    
    @pytest.mark.asyncio
    async def test_create_execution_context(self, script_executor):
        """Test execution context creation"""
        request = ExecutionRequest(
            script="test",
            platform="bash",
            working_directory="/custom/path",
            environment={"CUSTOM_VAR": "custom_value"}
        )
        
        context = await script_executor._create_execution_context(request)
        
        assert context["working_dir"] == "/custom/path"
        assert context["environment"]["CUSTOM_VAR"] == "custom_value"
        assert context["platform"] == platform.system().lower()
        assert "timestamp" in context
    
    def test_build_environment(self, script_executor):
        """Test environment building"""
        custom_env = {"CUSTOM_VAR": "custom_value"}
        env = script_executor._build_environment(custom_env)
        
        # Should include system environment
        assert "PATH" in env or "PATH" in os.environ
        
        # Should include custom environment
        assert env["CUSTOM_VAR"] == "custom_value"
        
        # Should include BK25-specific variables
        assert "BK25_EXECUTION" in env
        assert "BK25_TIMESTAMP" in env
    
    def test_prepare_execution_command_windows(self, script_executor):
        """Test command preparation for Windows"""
        with patch('platform.system', return_value='Windows'):
            request = ExecutionRequest(
                script="Get-Process",
                platform="powershell"
            )
            context = {"platform": "windows"}
            
            command = script_executor._prepare_execution_command(request, context)
            
            assert command[0] == "powershell.exe"
            assert "-ExecutionPolicy" in command
            assert "-Command" in command
            assert "Get-Process" in command
    
    def test_prepare_execution_command_unix(self, script_executor):
        """Test command preparation for Unix-like systems"""
        with patch('platform.system', return_value='Linux'):
            request = ExecutionRequest(
                script="ls -la",
                platform="bash"
            )
            context = {"platform": "linux"}
            
            command = script_executor._prepare_execution_command(request, context)
            
            assert command[0] == "/bin/bash"
            assert "-c" in command
            assert "ls -la" in command
    
    def test_prepare_execution_command_unsupported_platform(self, script_executor):
        """Test command preparation with unsupported platform"""
        request = ExecutionRequest(
            script="test",
            platform="bash"
        )
        context = {"platform": "unsupported"}
        
        with pytest.raises(ValueError, match="Unsupported platform"):
            script_executor._prepare_execution_command(request, context)
    
    @pytest.mark.asyncio
    async def test_get_execution_metrics_success(self, script_executor):
        """Test successful execution metrics collection"""
        with patch('psutil.Process') as mock_process:
            mock_process_instance = Mock()
            mock_process_instance.memory_info.return_value = Mock(rss=1024 * 1024 * 100)  # 100MB
            mock_process_instance.cpu_percent.return_value = 25.5
            mock_process_instance.io_counters.return_value = Mock(read_count=50, write_count=30)
            mock_process_instance.connections.return_value = [Mock(), Mock()]  # 2 connections
            
            mock_process.return_value = mock_process_instance
            
            metrics = await script_executor._get_execution_metrics(12345, 1000.0, 1005.0)
            
            assert metrics is not None
            assert metrics.peak_memory == 100.0  # MB
            assert metrics.average_cpu == 25.5
            assert metrics.io_operations == 80
            assert metrics.network_connections == 2
            assert metrics.total_time == 5.0
    
    @pytest.mark.asyncio
    async def test_get_execution_metrics_no_process(self, script_executor):
        """Test execution metrics when process doesn't exist"""
        with patch('psutil.Process', side_effect=psutil.NoSuchProcess(12345)):
            metrics = await script_executor._get_execution_metrics(12345, 1000.0, 1005.0)
            assert metrics is None
    
    @pytest.mark.asyncio
    async def test_get_execution_metrics_access_denied(self, script_executor):
        """Test execution metrics when access is denied"""
        with patch('psutil.Process', side_effect=psutil.AccessDenied()):
            metrics = await script_executor._get_execution_metrics(12345, 1000.0, 1005.0)
            assert metrics is None
    
    @pytest.mark.asyncio
    async def test_terminate_process_success(self, script_executor):
        """Test successful process termination"""
        mock_process = AsyncMock()
        mock_process.returncode = None  # Process is running
        
        await script_executor._terminate_process(mock_process)
        
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_terminate_process_timeout(self, script_executor):
        """Test process termination with timeout"""
        mock_process = AsyncMock()
        mock_process.returncode = None  # Process is running
        mock_process.wait.side_effect = asyncio.TimeoutError()
        
        await script_executor._terminate_process(mock_process)
        
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()
        mock_process.wait.assert_called()
    
    def test_log_execution_result_success(self, script_executor):
        """Test logging successful execution result"""
        request = ExecutionRequest(script="test", platform="bash")
        result = ExecutionResult(
            success=True,
            status=ExecutionStatus.COMPLETED,
            execution_time=1.5
        )
        
        # Should not raise any exceptions
        script_executor._log_execution_result(request, result)
    
    def test_log_execution_result_failure(self, script_executor):
        """Test logging failed execution result"""
        request = ExecutionRequest(script="test", platform="bash")
        result = ExecutionResult(
            success=False,
            status=ExecutionStatus.FAILED,
            error="Test error",
            execution_time=0.5
        )
        
        # Should not raise any exceptions
        script_executor._log_execution_result(request, result)
    
    def test_get_system_resources_success(self, script_executor):
        """Test successful system resource retrieval"""
        with patch('psutil.cpu_percent', return_value=45.2), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value = Mock(percent=75.5, available=1024**3 * 8)  # 8GB
            mock_disk.return_value = Mock(percent=60.0, free=1024**3 * 100)  # 100GB
            
            resources = script_executor.get_system_resources()
            
            assert "cpu_percent" in resources
            assert "memory_percent" in resources
            assert "memory_available" in resources
            assert "disk_percent" in resources
            assert "disk_free" in resources
            
            assert resources["cpu_percent"] == 45.2
            assert resources["memory_percent"] == 75.5
            assert resources["memory_available"] == 8.0  # GB
            assert resources["disk_percent"] == 60.0
            assert resources["disk_free"] == 100.0  # GB
    
    def test_get_system_resources_failure(self, script_executor):
        """Test system resource retrieval failure"""
        with patch('psutil.cpu_percent', side_effect=Exception("Test error")):
            resources = script_executor.get_system_resources()
            assert resources == {}
    
    @pytest.mark.asyncio
    async def test_cancel_execution_not_implemented(self, script_executor):
        """Test execution cancellation (not yet implemented)"""
        result = await script_executor.cancel_execution("test_id")
        assert result is False
    
    def test_get_execution_history_not_implemented(self, script_executor):
        """Test execution history retrieval (not yet implemented)"""
        history = script_executor.get_execution_history()
        assert history == []
    
    def test_platform_specific_configuration(self, script_executor):
        """Test platform-specific configuration"""
        if platform.system().lower() == "windows":
            config = script_executor.platform_config["windows"]
            assert config["shell"] == "powershell.exe"
            assert "-ExecutionPolicy" in config["args"]
            assert config["encoding"] == "cp1252"
        elif platform.system().lower() == "darwin":
            config = script_executor.platform_config["darwin"]
            assert config["shell"] == "/bin/bash"
            assert config["args"] == ["-c"]
            assert config["encoding"] == "utf-8"
        elif platform.system().lower() == "linux":
            config = script_executor.platform_config["linux"]
            assert config["shell"] == "/bin/bash"
            assert config["args"] == ["-c"]
            assert config["encoding"] == "utf-8"
    
    def test_safe_commands_platform_specific(self, script_executor):
        """Test that safe commands are platform-specific"""
        # PowerShell safe commands
        assert "Get-Process" in script_executor.safe_commands["powershell"]
        assert "Get-Service" in script_executor.safe_commands["powershell"]
        
        # Bash safe commands
        assert "ls" in script_executor.safe_commands["bash"]
        assert "pwd" in script_executor.safe_commands["bash"]
        
        # AppleScript safe commands
        assert "current date" in script_executor.safe_commands["applescript"]
        assert "system info" in script_executor.safe_commands["applescript"]
    
    def test_blocked_commands_platform_specific(self, script_executor):
        """Test that blocked commands are platform-specific"""
        # PowerShell blocked commands
        assert "Remove-Item" in script_executor.blocked_commands["powershell"]
        assert "Restart-Computer" in script_executor.blocked_commands["powershell"]
        
        # Bash blocked commands
        assert "rm" in script_executor.blocked_commands["bash"]
        assert "shutdown" in script_executor.blocked_commands["bash"]
        
        # AppleScript blocked commands
        assert "delete" in script_executor.blocked_commands["applescript"]
        assert "restart" in script_executor.blocked_commands["applescript"]

if __name__ == "__main__":
    pytest.main([__file__])
