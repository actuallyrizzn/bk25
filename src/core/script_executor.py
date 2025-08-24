import asyncio
import subprocess
import platform
import time
import signal
import psutil
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import os

from ..logging_config import get_logger

logger = get_logger("script_executor")

class ExecutionStatus(Enum):
    """Script execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class ExecutionPolicy(Enum):
    """Execution safety policies"""
    SAFE = "safe"           # Only safe commands, no system modifications
    RESTRICTED = "restricted"  # Limited system access, read-only operations
    STANDARD = "standard"    # Normal execution with safety checks
    ELEVATED = "elevated"    # Elevated privileges (admin/sudo)

@dataclass
class ExecutionRequest:
    """Script execution request"""
    script: str
    platform: str
    filename: Optional[str] = None
    working_directory: Optional[str] = None
    timeout: int = 300  # 5 minutes default
    policy: ExecutionPolicy = ExecutionPolicy.SAFE
    environment: Optional[Dict[str, str]] = None
    user_input: Optional[str] = None

@dataclass
class ExecutionResult:
    """Script execution result"""
    success: bool
    status: ExecutionStatus
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    execution_time: float = 0.0
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ExecutionMetrics:
    """Execution performance metrics"""
    start_time: float
    end_time: float
    total_time: float
    peak_memory: float
    average_cpu: float
    io_operations: int
    network_connections: int

class ScriptExecutor:
    """Safe script execution engine with monitoring"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger("script_executor")
        
        # Execution policies
        self.safe_commands = {
            'powershell': [
                'Get-Process', 'Get-Service', 'Get-ComputerInfo', 'Get-Date',
                'Get-Location', 'Get-ChildItem', 'Get-Content', 'Measure-Object',
                'Select-Object', 'Where-Object', 'Sort-Object', 'Format-Table'
            ],
            'applescript': [
                'tell application "System Events" to get name of every process',
                'tell application "Finder" to get name of every file',
                'current date', 'system info', 'get volume settings'
            ],
            'bash': [
                'ls', 'pwd', 'date', 'whoami', 'uname', 'ps', 'df', 'du',
                'cat', 'head', 'tail', 'grep', 'wc', 'sort', 'uniq'
            ]
        }
        
        # Dangerous commands to block
        self.blocked_commands = {
            'powershell': [
                'Remove-Item', 'Delete', 'Format-Volume', 'Clear-Content',
                'Stop-Process', 'Restart-Computer', 'Shutdown-Computer'
            ],
            'applescript': [
                'delete', 'move', 'duplicate', 'eject', 'restart', 'shut down'
            ],
            'bash': [
                'rm', 'rmdir', 'del', 'format', 'mkfs', 'dd', 'shutdown',
                'reboot', 'halt', 'poweroff'
            ]
        }
        
        # Platform-specific settings
        self.platform_config = {
            'windows': {
                'shell': 'powershell.exe',
                'args': ['-ExecutionPolicy', 'Bypass', '-Command'],
                'encoding': 'cp1252'
            },
            'darwin': {
                'shell': '/bin/bash',
                'args': ['-c'],
                'encoding': 'utf-8'
            },
            'linux': {
                'shell': '/bin/bash',
                'args': ['-c'],
                'encoding': 'utf-8'
            }
        }
        
        self.logger.info("[INIT] Script Executor initialized with safety policies")
    
    async def execute_script(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a script with full monitoring and safety checks"""
        try:
            self.logger.info(f"[EXEC] Executing {request.platform} script: {request.filename or 'inline'}")
            
            # Validate execution request
            validation = self._validate_execution_request(request)
            if not validation['valid']:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.FAILED,
                    error=f"Execution validation failed: {validation['reason']}"
                )
            
            # Create execution context
            context = await self._create_execution_context(request)
            
            # Execute with monitoring
            result = await self._execute_with_monitoring(request, context)
            
            # Log execution results
            self._log_execution_result(request, result)
            
            return result
            
        except Exception as error:
            self.logger.error(f"[ERROR] Script execution failed: {error}")
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                error=f"Execution error: {str(error)}"
            )
    
    def _validate_execution_request(self, request: ExecutionRequest) -> Dict[str, Any]:
        """Validate execution request against safety policies"""
        try:
            # Check platform support
            if request.platform not in self.safe_commands:
                return {
                    'valid': False,
                    'reason': f"Unsupported platform: {request.platform}"
                }
            
            # Check for blocked commands
            blocked = self._check_blocked_commands(request.script, request.platform)
            if blocked:
                return {
                    'valid': False,
                    'reason': f"Blocked commands detected: {', '.join(blocked)}"
                }
            
            # Check policy restrictions
            if request.policy == ExecutionPolicy.SAFE:
                safe_only = self._check_safe_commands_only(request.script, request.platform)
                if not safe_only:
                    return {
                        'valid': False,
                        'reason': "Safe policy requires only safe commands"
                    }
            
            # Check timeout limits
            if request.timeout > 3600:  # 1 hour max
                return {
                    'valid': False,
                    'reason': "Timeout exceeds maximum limit (1 hour)"
                }
            
            return {'valid': True}
            
        except Exception as error:
            return {
                'valid': False,
                'reason': f"Validation error: {str(error)}"
            }
    
    def _check_blocked_commands(self, script: str, platform: str) -> List[str]:
        """Check for blocked commands in the script"""
        blocked = []
        script_lower = script.lower()
        
        for command in self.blocked_commands.get(platform, []):
            if command.lower() in script_lower:
                blocked.append(command)
        
        return blocked
    
    def _check_safe_commands_only(self, script: str, platform: str) -> bool:
        """Check if script contains only safe commands"""
        script_lower = script.lower()
        
        # Check if any non-safe commands are present
        for command in self.safe_commands.get(platform, []):
            if command.lower() in script_lower:
                return True
        
        # If no safe commands found, it's not safe
        return False
    
    async def _create_execution_context(self, request: ExecutionRequest) -> Dict[str, Any]:
        """Create execution context with environment and working directory"""
        context = {
            'working_dir': request.working_directory or str(Path.cwd()),
            'environment': self._build_environment(request.environment),
            'platform': platform.system().lower(),
            'timestamp': time.time()
        }
        
        # Ensure working directory exists
        Path(context['working_dir']).mkdir(parents=True, exist_ok=True)
        
        return context
    
    def _build_environment(self, custom_env: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Build execution environment"""
        env = os.environ.copy()
        
        if custom_env:
            env.update(custom_env)
        
        # Add BK25-specific environment variables
        env['BK25_EXECUTION'] = 'true'
        env['BK25_TIMESTAMP'] = str(int(time.time()))
        
        return env
    
    async def _execute_with_monitoring(
        self, 
        request: ExecutionRequest, 
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute script with full monitoring"""
        start_time = time.time()
        process = None
        
        try:
            # Prepare execution command
            command = self._prepare_execution_command(request, context)
            
            # Start execution
            self.logger.info(f"[EXEC] Starting script execution: {command}")
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=context['working_dir'],
                env=context['environment']
            )
            
            # Monitor execution
            result = await self._monitor_execution(process, request, start_time)
            
            return result
            
        except asyncio.TimeoutError:
            if process:
                await self._terminate_process(process)
            
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.TIMEOUT,
                error=f"Execution timed out after {request.timeout} seconds",
                execution_time=time.time() - start_time
            )
            
        except Exception as error:
            if process:
                await self._terminate_process(process)
            
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILED,
                error=f"Execution failed: {str(error)}",
                execution_time=time.time() - start_time
            )
    
    def _prepare_execution_command(
        self, 
        request: ExecutionRequest, 
        context: Dict[str, Any]
    ) -> List[str]:
        """Prepare the execution command based on platform"""
        platform_config = self.platform_config.get(context['platform'])
        if not platform_config:
            raise ValueError(f"Unsupported platform: {context['platform']}")
        
        command = [platform_config['shell']]
        command.extend(platform_config['args'])
        
        if request.platform == 'powershell':
            # PowerShell specific handling
            command.append(request.script)
        else:
            # Bash/AppleScript
            command.append(request.script)
        
        return command
    
    async def _monitor_execution(
        self, 
        process: asyncio.subprocess.Process,
        request: ExecutionRequest,
        start_time: float
    ) -> ExecutionResult:
        """Monitor script execution with timeout and resource tracking"""
        try:
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=request.timeout
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Get exit code
            exit_code = process.returncode
            
            # Determine success
            success = exit_code == 0
            
            # Get output
            output = stdout.decode('utf-8', errors='ignore') if stdout else None
            error = stderr.decode('utf-8', errors='ignore') if stderr else None
            
            # Determine status
            if success:
                status = ExecutionStatus.COMPLETED
            else:
                status = ExecutionStatus.FAILED
            
            # Get resource metrics
            metrics = await self._get_execution_metrics(process.pid, start_time, end_time)
            
            return ExecutionResult(
                success=success,
                status=status,
                output=output,
                error=error,
                exit_code=exit_code,
                execution_time=execution_time,
                memory_usage=metrics.peak_memory if metrics else None,
                cpu_usage=metrics.average_cpu if metrics else None,
                metadata={
                    'pid': process.pid,
                    'platform': request.platform,
                    'policy': request.policy.value,
                    'metrics': metrics.__dict__ if metrics else None
                }
            )
            
        except asyncio.TimeoutError:
            raise
    
    async def _get_execution_metrics(
        self, 
        pid: int, 
        start_time: float, 
        end_time: float
    ) -> Optional[ExecutionMetrics]:
        """Get execution performance metrics"""
        try:
            process = psutil.Process(pid)
            
            # Get memory info
            memory_info = process.memory_info()
            peak_memory = memory_info.rss / 1024 / 1024  # MB
            
            # Get CPU usage
            cpu_percent = process.cpu_percent()
            
            # Get I/O info
            io_counters = process.io_counters()
            io_operations = io_counters.read_count + io_counters.write_count
            
            # Get network connections
            connections = process.connections()
            network_connections = len(connections)
            
            return ExecutionMetrics(
                start_time=start_time,
                end_time=end_time,
                total_time=end_time - start_time,
                peak_memory=peak_memory,
                average_cpu=cpu_percent,
                io_operations=io_operations,
                network_connections=network_connections
            )
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    async def _terminate_process(self, process: asyncio.subprocess.Process):
        """Safely terminate a running process"""
        try:
            if process.returncode is None:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
    
    def _log_execution_result(self, request: ExecutionRequest, result: ExecutionResult):
        """Log execution results"""
        if result.success:
            self.logger.info(
                f"[SUCCESS] Script execution completed successfully in {result.execution_time:.2f}s"
            )
        else:
            self.logger.error(
                f"[ERROR] Script execution failed: {result.error} (Status: {result.status.value})"
            )
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        # This would be implemented with a task registry
        # For now, return False as we don't have task tracking yet
        self.logger.warning("Execution cancellation not yet implemented")
        return False
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history (placeholder for future implementation)"""
        # This would return execution history from a database
        return []
    
    def get_system_resources(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available / 1024 / 1024 / 1024,  # GB
                'disk_percent': disk.percent,
                'disk_free': disk.free / 1024 / 1024 / 1024  # GB
            }
        except Exception as error:
            self.logger.error(f"Failed to get system resources: {error}")
            return {}
