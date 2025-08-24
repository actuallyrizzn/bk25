import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from ..logging_config import get_logger

logger = get_logger("execution_monitor")

class TaskStatus(Enum):
    """Task execution status"""
    QUEUED = "queued"
    PREPARING = "preparing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ExecutionTask:
    """Represents an execution task"""
    id: str
    name: str
    description: str
    script: str
    platform: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: float = 0.0
    exit_code: Optional[int] = None
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class TaskMetrics:
    """Task execution metrics"""
    task_id: str
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    io_operations: List[int] = field(default_factory=list)
    network_connections: List[int] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class ExecutionMonitor:
    """Monitors and manages script execution tasks"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger("execution_monitor")
        
        # Task storage
        self.tasks: Dict[str, ExecutionTask] = {}
        self.task_metrics: Dict[str, TaskMetrics] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Task queue
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.priority_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
        # Monitoring settings
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 5)
        self.task_timeout = self.config.get('task_timeout', 300)  # 5 minutes
        self.metrics_interval = self.config.get('metrics_interval', 1.0)  # 1 second
        
        # Callbacks
        self.status_callbacks: List[Callable[[ExecutionTask], None]] = []
        self.completion_callbacks: List[Callable[[ExecutionTask], None]] = []
        
        # Statistics
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }
        
        self.logger.info("🚀 Execution Monitor initialized")
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        try:
            self.logger.info("🔄 Starting execution monitoring system")
            
            # Start task processor
            asyncio.create_task(self._process_task_queue())
            
            # Start metrics collector
            asyncio.create_task(self._collect_metrics())
            
            # Start cleanup task
            asyncio.create_task(self._cleanup_old_tasks())
            
            self.logger.info("✅ Execution monitoring system started")
            
        except Exception as error:
            self.logger.error(f"❌ Failed to start monitoring: {error}")
            raise
    
    async def submit_task(
        self,
        name: str,
        description: str,
        script: str,
        platform: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Submit a new execution task"""
        try:
            task_id = str(uuid.uuid4())
            
            task = ExecutionTask(
                id=task_id,
                name=name,
                description=description,
                script=script,
                platform=platform,
                status=TaskStatus.QUEUED,
                priority=priority,
                created_at=datetime.now(),
                tags=tags or [],
                metadata=metadata or {}
            )
            
            # Store task
            self.tasks[task_id] = task
            self.task_metrics[task_id] = TaskMetrics(task_id=task_id)
            
            # Add to priority queue
            await self.priority_queue.put((priority.value, task_id))
            
            # Update statistics
            self.stats['total_tasks'] += 1
            
            self.logger.info(f"📝 Task submitted: {name} (ID: {task_id})")
            
            # Notify status change
            await self._notify_status_change(task)
            
            return task_id
            
        except Exception as error:
            self.logger.error(f"❌ Failed to submit task: {error}")
            raise
    
    async def get_task_status(self, task_id: str) -> Optional[ExecutionTask]:
        """Get the current status of a task"""
        return self.tasks.get(task_id)
    
    async def get_running_tasks(self) -> List[ExecutionTask]:
        """Get all currently running tasks"""
        return [
            task for task in self.tasks.values()
            if task.status == TaskStatus.RUNNING
        ]
    
    async def get_task_metrics(self, task_id: str) -> Optional[TaskMetrics]:
        """Get metrics for a specific task"""
        return self.task_metrics.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running or queued task"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                return False
            
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return False
            
            # Cancel running task
            if task_id in self.running_tasks:
                running_task = self.running_tasks[task_id]
                running_task.cancel()
                del self.running_tasks[task_id]
            
            # Update task status
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            
            self.logger.info(f"🚫 Task cancelled: {task.name} (ID: {task_id})")
            
            # Notify status change
            await self._notify_status_change(task)
            
            return True
            
        except Exception as error:
            self.logger.error(f"❌ Failed to cancel task {task_id}: {error}")
            return False
    
    async def pause_task(self, task_id: str) -> bool:
        """Pause a running task"""
        try:
            task = self.tasks.get(task_id)
            if not task or task.status != TaskStatus.RUNNING:
                return False
            
            # Pause the task (implementation depends on the executor)
            task.status = TaskStatus.PAUSED
            
            self.logger.info(f"⏸️ Task paused: {task.name} (ID: {task_id})")
            
            # Notify status change
            await self._notify_status_change(task)
            
            return True
            
        except Exception as error:
            self.logger.error(f"❌ Failed to pause task {task_id}: {error}")
            return False
    
    async def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        try:
            task = self.tasks.get(task_id)
            if not task or task.status != TaskStatus.PAUSED:
                return False
            
            # Resume the task
            task.status = TaskStatus.RUNNING
            
            self.logger.info(f"▶️ Task resumed: {task.name} (ID: {task_id})")
            
            # Notify status change
            await self._notify_status_change(task)
            
            return True
            
        except Exception as error:
            self.logger.error(f"❌ Failed to resume task {task_id}: {error}")
            return False
    
    async def get_execution_history(
        self,
        limit: int = 100,
        status_filter: Optional[TaskStatus] = None,
        platform_filter: Optional[str] = None,
        tag_filter: Optional[str] = None
    ) -> List[ExecutionTask]:
        """Get execution history with optional filters"""
        try:
            tasks = list(self.tasks.values())
            
            # Apply filters
            if status_filter:
                tasks = [t for t in tasks if t.status == status_filter]
            
            if platform_filter:
                tasks = [t for t in tasks if t.platform == platform_filter]
            
            if tag_filter:
                tasks = [t for t in tasks if tag_filter in t.tags]
            
            # Sort by creation time (newest first)
            tasks.sort(key=lambda t: t.created_at, reverse=True)
            
            return tasks[:limit]
            
        except Exception as error:
            self.logger.error(f"❌ Failed to get execution history: {error}")
            return []
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get system execution statistics"""
        try:
            current_time = datetime.now()
            
            # Calculate recent statistics (last 24 hours)
            recent_tasks = [
                task for task in self.tasks.values()
                if task.created_at > current_time - timedelta(hours=24)
            ]
            
            recent_completed = [
                task for task in recent_tasks
                if task.status == TaskStatus.COMPLETED
            ]
            
            recent_failed = [
                task for task in recent_tasks
                if task.status == TaskStatus.FAILED
            ]
            
            # Calculate success rate
            total_recent = len(recent_tasks)
            success_rate = (len(recent_completed) / total_recent * 100) if total_recent > 0 else 0
            
            return {
                'total_tasks': self.stats['total_tasks'],
                'completed_tasks': self.stats['completed_tasks'],
                'failed_tasks': self.stats['failed_tasks'],
                'total_execution_time': self.stats['total_execution_time'],
                'average_execution_time': self.stats['average_execution_time'],
                'recent_24h': {
                    'total_tasks': total_recent,
                    'completed_tasks': len(recent_completed),
                    'failed_tasks': len(recent_failed),
                    'success_rate': round(success_rate, 2)
                },
                'current_running': len(self.running_tasks),
                'queue_size': self.priority_queue.qsize()
            }
            
        except Exception as error:
            self.logger.error(f"❌ Failed to get system statistics: {error}")
            return {}
    
    def add_status_callback(self, callback: Callable[[ExecutionTask], None]):
        """Add a callback for task status changes"""
        self.status_callbacks.append(callback)
    
    def add_completion_callback(self, callback: Callable[[ExecutionTask], None]):
        """Add a callback for task completion"""
        self.completion_callbacks.append(callback)
    
    async def _process_task_queue(self):
        """Process the task queue"""
        while True:
            try:
                # Wait for a task
                priority, task_id = await self.priority_queue.get()
                
                # Check if we can run more tasks
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    # Put task back in queue
                    await self.priority_queue.put((priority, task_id))
                    await asyncio.sleep(1)
                    continue
                
                # Get the task
                task = self.tasks.get(task_id)
                if not task:
                    continue
                
                # Update status
                task.status = TaskStatus.PREPARING
                await self._notify_status_change(task)
                
                # Start execution
                await self._execute_task(task)
                
            except asyncio.CancelledError:
                break
            except Exception as error:
                self.logger.error(f"❌ Task queue processing error: {error}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, task: ExecutionTask):
        """Execute a single task"""
        try:
            # Update status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            await self._notify_status_change(task)
            
            # Create execution task
            execution_task = asyncio.create_task(
                self._run_task_execution(task),
                name=f"task_{task.id}"
            )
            
            # Store running task
            self.running_tasks[task.id] = execution_task
            
            # Wait for completion
            await execution_task
            
        except Exception as error:
            self.logger.error(f"❌ Task execution failed: {task.id}: {error}")
            task.status = TaskStatus.FAILED
            task.error = str(error)
            task.completed_at = datetime.now()
            
            # Update statistics
            self.stats['failed_tasks'] += 1
            
            # Notify status change
            await self._notify_status_change(task)
            
        finally:
            # Clean up running task
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    async def _run_task_execution(self, task: ExecutionTask):
        """Run the actual task execution"""
        try:
            # This would integrate with the ScriptExecutor
            # For now, simulate execution
            await asyncio.sleep(2)  # Simulate work
            
            # Simulate success
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.execution_time = (task.completed_at - task.started_at).total_seconds()
            task.exit_code = 0
            task.output = "Task completed successfully"
            
            # Update statistics
            self.stats['completed_tasks'] += 1
            self.stats['total_execution_time'] += task.execution_time
            self.stats['average_execution_time'] = (
                self.stats['total_execution_time'] / self.stats['completed_tasks']
            )
            
            # Notify completion
            await self._notify_completion(task)
            
        except Exception as error:
            task.status = TaskStatus.FAILED
            task.error = str(error)
            task.completed_at = datetime.now()
            
            # Update statistics
            self.stats['failed_tasks'] += 1
            
            # Notify status change
            await self._notify_status_change(task)
    
    async def _collect_metrics(self):
        """Collect metrics for running tasks"""
        while True:
            try:
                await asyncio.sleep(self.metrics_interval)
                
                for task_id, task in self.running_tasks.items():
                    if task_id in self.task_metrics:
                        metrics = self.task_metrics[task_id]
                        
                        # Collect current metrics (simplified)
                        if metrics.start_time is None:
                            metrics.start_time = time.time()
                        
                        # This would collect real metrics from the running process
                        # For now, just update the timestamp
                        metrics.end_time = time.time()
                
            except asyncio.CancelledError:
                break
            except Exception as error:
                self.logger.error(f"❌ Metrics collection error: {error}")
                await asyncio.sleep(1)
    
    async def _cleanup_old_tasks(self):
        """Clean up old completed tasks"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(days=7)  # Keep 7 days
                
                tasks_to_remove = []
                for task_id, task in self.tasks.items():
                    if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                        task.created_at < cutoff_time):
                        tasks_to_remove.append(task_id)
                
                for task_id in tasks_to_remove:
                    del self.tasks[task_id]
                    if task_id in self.task_metrics:
                        del self.task_metrics[task_id]
                
                if tasks_to_remove:
                    self.logger.info(f"🧹 Cleaned up {len(tasks_to_remove)} old tasks")
                
            except asyncio.CancelledError:
                break
            except Exception as error:
                self.logger.error(f"❌ Cleanup error: {error}")
                await asyncio.sleep(1)
    
    async def _notify_status_change(self, task: ExecutionTask):
        """Notify status change callbacks"""
        for callback in self.status_callbacks:
            try:
                callback(task)
            except Exception as error:
                self.logger.error(f"❌ Status callback error: {error}")
    
    async def _notify_completion(self, task: ExecutionTask):
        """Notify completion callbacks"""
        for callback in self.completion_callbacks:
            try:
                callback(task)
            except Exception as error:
                self.logger.error(f"❌ Completion callback error: {error}")
    
    async def shutdown(self):
        """Shutdown the monitoring system"""
        try:
            self.logger.info("🔄 Shutting down execution monitoring system")
            
            # Cancel all running tasks
            for task_id, task in self.running_tasks.items():
                task.cancel()
            
            # Wait for tasks to complete
            if self.running_tasks:
                await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
            
            self.logger.info("✅ Execution monitoring system shutdown complete")
            
        except Exception as error:
            self.logger.error(f"❌ Shutdown error: {error}")
            raise
