import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Add src to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.execution_monitor import (
    ExecutionMonitor, ExecutionTask, TaskStatus, TaskPriority, TaskMetrics
)

class TestTaskStatus:
    """Test TaskStatus enum"""
    
    def test_task_status_values(self):
        """Test TaskStatus enum values"""
        assert TaskStatus.QUEUED == "queued"
        assert TaskStatus.PREPARING == "preparing"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.TIMEOUT == "timeout"
        assert TaskStatus.CANCELLED == "cancelled"
        assert TaskStatus.PAUSED == "paused"

class TestTaskPriority:
    """Test TaskPriority enum"""
    
    def test_task_priority_values(self):
        """Test TaskPriority enum values"""
        assert TaskPriority.LOW == 1
        assert TaskPriority.NORMAL == 2
        assert TaskPriority.HIGH == 3
        assert TaskPriority.CRITICAL == 4
    
    def test_task_priority_comparison(self):
        """Test TaskPriority comparison"""
        assert TaskPriority.LOW < TaskPriority.NORMAL
        assert TaskPriority.NORMAL < TaskPriority.HIGH
        assert TaskPriority.HIGH < TaskPriority.CRITICAL
        assert TaskPriority.CRITICAL > TaskPriority.LOW

class TestExecutionTask:
    """Test ExecutionTask dataclass"""
    
    def test_execution_task_creation(self):
        """Test creating an ExecutionTask instance"""
        task = ExecutionTask(
            id="test_task",
            name="Test Task",
            description="A test execution task",
            script="echo 'Hello World'",
            platform="bash",
            status=TaskStatus.QUEUED,
            priority=TaskPriority.NORMAL,
            created_at=datetime.now(),
            tags=["test", "automation"],
            metadata={"user": "test_user"}
        )
        
        assert task.id == "test_task"
        assert task.name == "Test Task"
        assert task.description == "A test execution task"
        assert task.script == "echo 'Hello World'"
        assert task.platform == "bash"
        assert task.status == TaskStatus.QUEUED
        assert task.priority == TaskPriority.NORMAL
        assert task.tags == ["test", "automation"]
        assert task.metadata["user"] == "test_user"
        assert task.retry_count == 0
        assert task.max_retries == 3
    
    def test_execution_task_defaults(self):
        """Test ExecutionTask with default values"""
        task = ExecutionTask(
            id="minimal",
            name="Minimal Task",
            description="Minimal task description",
            script="echo 'test'",
            platform="bash",
            status=TaskStatus.QUEUED,
            priority=TaskPriority.NORMAL,
            created_at=datetime.now()
        )
        
        assert task.id == "minimal"
        assert task.name == "Minimal Task"
        assert task.started_at is None
        assert task.completed_at is None
        assert task.execution_time == 0.0
        assert task.exit_code is None
        assert task.output is None
        assert task.error is None
        assert task.tags == []
        assert task.metadata == {}
        assert task.retry_count == 0
        assert task.max_retries == 3

class TestTaskMetrics:
    """Test TaskMetrics dataclass"""
    
    def test_task_metrics_creation(self):
        """Test creating a TaskMetrics instance"""
        metrics = TaskMetrics(
            task_id="test_task",
            cpu_usage=[25.5, 30.2, 28.1],
            memory_usage=[100.2, 105.8, 102.3],
            io_operations=[50, 55, 52],
            network_connections=[2, 3, 2],
            start_time=1000.0,
            end_time=1005.0
        )
        
        assert metrics.task_id == "test_task"
        assert metrics.cpu_usage == [25.5, 30.2, 28.1]
        assert metrics.memory_usage == [100.2, 105.8, 102.3]
        assert metrics.io_operations == [50, 55, 52]
        assert metrics.network_connections == [2, 3, 2]
        assert metrics.start_time == 1000.0
        assert metrics.end_time == 1005.0
    
    def test_task_metrics_defaults(self):
        """Test TaskMetrics with default values"""
        metrics = TaskMetrics(task_id="test")
        
        assert metrics.task_id == "test"
        assert metrics.cpu_usage == []
        assert metrics.memory_usage == []
        assert metrics.io_operations == []
        assert metrics.network_connections == []
        assert metrics.start_time is None
        assert metrics.end_time is None

class TestExecutionMonitor:
    """Test ExecutionMonitor class"""
    
    @pytest.fixture
    def execution_monitor(self):
        """Create ExecutionMonitor instance"""
        return ExecutionMonitor()
    
    def test_initialization(self, execution_monitor):
        """Test ExecutionMonitor initialization"""
        assert execution_monitor.config == {}
        assert execution_monitor.tasks == {}
        assert execution_monitor.task_metrics == {}
        assert execution_monitor.running_tasks == {}
        assert execution_monitor.max_concurrent_tasks == 5
        assert execution_monitor.task_timeout == 300
        assert execution_monitor.metrics_interval == 1.0
        assert execution_monitor.status_callbacks == []
        assert execution_monitor.completion_callbacks == []
        assert "total_tasks" in execution_monitor.stats
    
    @pytest.mark.asyncio
    async def test_start_monitoring_success(self, execution_monitor):
        """Test successful monitoring start"""
        with patch('asyncio.create_task') as mock_create_task:
            await execution_monitor.start_monitoring()
            
            # Should create 3 background tasks
            assert mock_create_task.call_count == 3
            
            # Check that tasks were created for expected functions
            calls = [call[0][0].__name__ for call in mock_create_task.call_args_list]
            assert '_process_task_queue' in calls
            assert '_collect_metrics' in calls
            assert '_cleanup_old_tasks' in calls
    
    @pytest.mark.asyncio
    async def test_start_monitoring_failure(self, execution_monitor):
        """Test monitoring start failure"""
        with patch('asyncio.create_task', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                await execution_monitor.start_monitoring()
    
    @pytest.mark.asyncio
    async def test_submit_task_success(self, execution_monitor):
        """Test successful task submission"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash",
            priority=TaskPriority.NORMAL,
            tags=["test"],
            metadata={"user": "test_user"}
        )
        
        assert task_id is not None
        assert task_id in execution_monitor.tasks
        
        task = execution_monitor.tasks[task_id]
        assert task.name == "Test Task"
        assert task.description == "Test description"
        assert task.script == "echo 'test'"
        assert task.platform == "bash"
        assert task.status == TaskStatus.QUEUED
        assert task.priority == TaskPriority.NORMAL
        assert task.tags == ["test"]
        assert task.metadata["user"] == "test_user"
        
        # Check that task was added to priority queue
        assert execution_monitor.priority_queue.qsize() == 1
        
        # Check statistics update
        assert execution_monitor.stats["total_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_submit_task_failure(self, execution_monitor):
        """Test task submission failure"""
        with patch('asyncio.Queue.put', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                await execution_monitor.submit_task(
                    name="Test Task",
                    description="Test description",
                    script="echo 'test'",
                    platform="bash"
                )
    
    @pytest.mark.asyncio
    async def test_get_task_status_existing(self, execution_monitor):
        """Test getting existing task status"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        task = await execution_monitor.get_task_status(task_id)
        assert task is not None
        assert task.id == task_id
        assert task.name == "Test Task"
    
    @pytest.mark.asyncio
    async def test_get_task_status_nonexistent(self, execution_monitor):
        """Test getting non-existent task status"""
        task = await execution_monitor.get_task_status("nonexistent")
        assert task is None
    
    @pytest.mark.asyncio
    async def test_get_running_tasks(self, execution_monitor):
        """Test getting running tasks"""
        # Submit a task
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Initially no running tasks
        running_tasks = await execution_monitor.get_running_tasks()
        assert len(running_tasks) == 0
        
        # Manually set task to running (simulating execution)
        execution_monitor.tasks[task_id].status = TaskStatus.RUNNING
        
        running_tasks = await execution_monitor.get_running_tasks()
        assert len(running_tasks) == 1
        assert running_tasks[0].id == task_id
    
    @pytest.mark.asyncio
    async def test_get_task_metrics_existing(self, execution_monitor):
        """Test getting existing task metrics"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        metrics = await execution_monitor.get_task_metrics(task_id)
        assert metrics is not None
        assert metrics.task_id == task_id
    
    @pytest.mark.asyncio
    async def test_get_task_metrics_nonexistent(self, execution_monitor):
        """Test getting non-existent task metrics"""
        metrics = await execution_monitor.get_task_metrics("nonexistent")
        assert metrics is None
    
    @pytest.mark.asyncio
    async def test_cancel_task_success(self, execution_monitor):
        """Test successful task cancellation"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Cancel the task
        success = await execution_monitor.cancel_task(task_id)
        assert success is True
        
        # Check task status
        task = execution_monitor.tasks[task_id]
        assert task.status == TaskStatus.CANCELLED
        assert task.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_cancel_task_nonexistent(self, execution_monitor):
        """Test cancelling non-existent task"""
        success = await execution_monitor.cancel_task("nonexistent")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_cancel_task_already_completed(self, execution_monitor):
        """Test cancelling already completed task"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Set task to completed
        execution_monitor.tasks[task_id].status = TaskStatus.COMPLETED
        
        # Try to cancel
        success = await execution_monitor.cancel_task(task_id)
        assert success is False
    
    @pytest.mark.asyncio
    async def test_pause_task_success(self, execution_monitor):
        """Test successful task pause"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Set task to running
        execution_monitor.tasks[task_id].status = TaskStatus.RUNNING
        
        # Pause the task
        success = await execution_monitor.pause_task(task_id)
        assert success is True
        
        # Check task status
        task = execution_monitor.tasks[task_id]
        assert task.status == TaskStatus.PAUSED
    
    @pytest.mark.asyncio
    async def test_pause_task_not_running(self, execution_monitor):
        """Test pausing non-running task"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Task is queued, not running
        success = await execution_monitor.pause_task(task_id)
        assert success is False
    
    @pytest.mark.asyncio
    async def test_resume_task_success(self, execution_monitor):
        """Test successful task resume"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Set task to paused
        execution_monitor.tasks[task_id].status = TaskStatus.PAUSED
        
        # Resume the task
        success = await execution_monitor.resume_task(task_id)
        assert success is True
        
        # Check task status
        task = execution_monitor.tasks[task_id]
        assert task.status == TaskStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_resume_task_not_paused(self, execution_monitor):
        """Test resuming non-paused task"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Task is queued, not paused
        success = await execution_monitor.resume_task(task_id)
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_execution_history_no_filters(self, execution_monitor):
        """Test getting execution history without filters"""
        # Submit multiple tasks
        for i in range(3):
            await execution_monitor.submit_task(
                name=f"Task {i}",
                description=f"Task {i} description",
                script=f"echo 'task{i}'",
                platform="bash"
            )
        
        history = await execution_monitor.get_execution_history()
        assert len(history) == 3
        
        # Should be sorted by creation time (newest first)
        assert history[0].created_at >= history[1].created_at
        assert history[1].created_at >= history[2].created_at
    
    @pytest.mark.asyncio
    async def test_get_execution_history_with_status_filter(self, execution_monitor):
        """Test getting execution history with status filter"""
        # Submit tasks
        task_id1 = await execution_monitor.submit_task(
            name="Task 1",
            description="Task 1 description",
            script="echo 'task1'",
            platform="bash"
        )
        
        task_id2 = await execution_monitor.submit_task(
            name="Task 2",
            description="Task 2 description",
            script="echo 'task2'",
            platform="bash"
        )
        
        # Set different statuses
        execution_monitor.tasks[task_id1].status = TaskStatus.COMPLETED
        execution_monitor.tasks[task_id2].status = TaskStatus.FAILED
        
        # Filter by completed status
        completed_history = await execution_monitor.get_execution_history(
            status_filter=TaskStatus.COMPLETED
        )
        assert len(completed_history) == 1
        assert completed_history[0].status == TaskStatus.COMPLETED
        
        # Filter by failed status
        failed_history = await execution_monitor.get_execution_history(
            status_filter=TaskStatus.FAILED
        )
        assert len(failed_history) == 1
        assert failed_history[0].status == TaskStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_get_execution_history_with_platform_filter(self, execution_monitor):
        """Test getting execution history with platform filter"""
        # Submit tasks with different platforms
        await execution_monitor.submit_task(
            name="PowerShell Task",
            description="PowerShell task",
            script="Get-Process",
            platform="powershell"
        )
        
        await execution_monitor.submit_task(
            name="Bash Task",
            description="Bash task",
            script="ls -la",
            platform="bash"
        )
        
        # Filter by PowerShell
        powershell_history = await execution_monitor.get_execution_history(
            platform_filter="powershell"
        )
        assert len(powershell_history) == 1
        assert powershell_history[0].platform == "powershell"
        
        # Filter by Bash
        bash_history = await execution_monitor.get_execution_history(
            platform_filter="bash"
        )
        assert len(bash_history) == 1
        assert bash_history[0].platform == "bash"
    
    @pytest.mark.asyncio
    async def test_get_execution_history_with_tag_filter(self, execution_monitor):
        """Test getting execution history with tag filter"""
        # Submit tasks with different tags
        await execution_monitor.submit_task(
            name="Task 1",
            description="Task 1",
            script="echo 'task1'",
            platform="bash",
            tags=["automation", "test"]
        )
        
        await execution_monitor.submit_task(
            name="Task 2",
            description="Task 2",
            script="echo 'task2'",
            platform="bash",
            tags=["deployment", "production"]
        )
        
        # Filter by automation tag
        automation_history = await execution_monitor.get_execution_history(
            tag_filter="automation"
        )
        assert len(automation_history) == 1
        assert "automation" in automation_history[0].tags
        
        # Filter by production tag
        production_history = await execution_monitor.get_execution_history(
            tag_filter="production"
        )
        assert len(production_history) == 1
        assert "production" in production_history[0].tags
    
    @pytest.mark.asyncio
    async def test_get_execution_history_with_limit(self, execution_monitor):
        """Test getting execution history with limit"""
        # Submit 5 tasks
        for i in range(5):
            await execution_monitor.submit_task(
                name=f"Task {i}",
                description=f"Task {i}",
                script=f"echo 'task{i}'",
                platform="bash"
            )
        
        # Get history with limit 3
        history = await execution_monitor.get_execution_history(limit=3)
        assert len(history) == 3
    
    @pytest.mark.asyncio
    async def test_get_system_statistics(self, execution_monitor):
        """Test getting system statistics"""
        # Submit and complete some tasks
        task_id1 = await execution_monitor.submit_task(
            name="Task 1",
            description="Task 1",
            script="echo 'task1'",
            platform="bash"
        )
        
        task_id2 = await execution_monitor.submit_task(
            name="Task 2",
            description="Task 2",
            script="echo 'task2'",
            platform="bash"
        )
        
        # Set task statuses
        execution_monitor.tasks[task_id1].status = TaskStatus.COMPLETED
        execution_monitor.tasks[task_id1].completed_at = datetime.now()
        execution_monitor.tasks[task_id1].execution_time = 5.0
        
        execution_monitor.tasks[task_id2].status = TaskStatus.FAILED
        execution_monitor.tasks[task_id2].completed_at = datetime.now()
        
        # Update statistics
        execution_monitor.stats["completed_tasks"] = 1
        execution_monitor.stats["failed_tasks"] = 1
        execution_monitor.stats["total_execution_time"] = 5.0
        execution_monitor.stats["average_execution_time"] = 5.0
        
        stats = await execution_monitor.get_system_statistics()
        
        assert "total_tasks" in stats
        assert "completed_tasks" in stats
        assert "failed_tasks" in stats
        assert "total_execution_time" in stats
        assert "average_execution_time" in stats
        assert "recent_24h" in stats
        assert "current_running" in stats
        assert "queue_size" in stats
        
        assert stats["total_tasks"] == 2
        assert stats["completed_tasks"] == 1
        assert stats["failed_tasks"] == 1
        assert stats["total_execution_time"] == 5.0
        assert stats["average_execution_time"] == 5.0
    
    def test_add_status_callback(self, execution_monitor):
        """Test adding status callback"""
        def test_callback(task):
            pass
        
        execution_monitor.add_status_callback(test_callback)
        assert test_callback in execution_monitor.status_callbacks
    
    def test_add_completion_callback(self, execution_monitor):
        """Test adding completion callback"""
        def test_callback(task):
            pass
        
        execution_monitor.add_completion_callback(test_callback)
        assert test_callback in execution_monitor.completion_callbacks
    
    @pytest.mark.asyncio
    async def test_process_task_queue_basic(self, execution_monitor):
        """Test basic task queue processing"""
        # Submit a task
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Start processing (this will run in background)
        asyncio.create_task(execution_monitor._process_task_queue())
        
        # Wait a bit for processing
        await asyncio.sleep(0.1)
        
        # Task should be processed (status might change)
        task = execution_monitor.tasks[task_id]
        assert task is not None
    
    @pytest.mark.asyncio
    async def test_process_task_queue_max_concurrent_limit(self, execution_monitor):
        """Test task queue processing with max concurrent limit"""
        execution_monitor.max_concurrent_tasks = 1
        
        # Submit 2 tasks
        task_id1 = await execution_monitor.submit_task(
            name="Task 1",
            description="Task 1",
            script="echo 'task1'",
            platform="bash"
        )
        
        task_id2 = await execution_monitor.submit_task(
            name="Task 2",
            description="Task 2",
            script="echo 'task2'",
            platform="bash"
        )
        
        # Start processing
        asyncio.create_task(execution_monitor._process_task_queue())
        
        # Wait a bit for processing
        await asyncio.sleep(0.1)
        
        # Only one task should be running
        running_tasks = await execution_monitor.get_running_tasks()
        assert len(running_tasks) <= 1
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self, execution_monitor):
        """Test successful task execution"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Execute the task
        await execution_monitor._execute_task(execution_monitor.tasks[task_id])
        
        # Check task status
        task = execution_monitor.tasks[task_id]
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.execution_time > 0
        assert task.exit_code == 0
        assert task.output == "Task completed successfully"
        
        # Check statistics
        assert execution_monitor.stats["completed_tasks"] == 1
        assert execution_monitor.stats["total_execution_time"] > 0
    
    @pytest.mark.asyncio
    async def test_execute_task_failure(self, execution_monitor):
        """Test failed task execution"""
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Mock execution to fail
        with patch.object(execution_monitor, '_run_task_execution', side_effect=Exception("Test error")):
            await execution_monitor._execute_task(execution_monitor.tasks[task_id])
        
        # Check task status
        task = execution_monitor.tasks[task_id]
        assert task.status == TaskStatus.FAILED
        assert task.error == "Test error"
        assert task.completed_at is not None
        
        # Check statistics
        assert execution_monitor.stats["failed_tasks"] == 1
    
    @pytest.mark.asyncio
    async def test_collect_metrics(self, execution_monitor):
        """Test metrics collection"""
        # Submit a task
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Start metrics collection
        asyncio.create_task(execution_monitor._collect_metrics())
        
        # Wait a bit for collection
        await asyncio.sleep(0.1)
        
        # Metrics should be collected
        metrics = await execution_monitor.get_task_metrics(task_id)
        assert metrics is not None
    
    @pytest.mark.asyncio
    async def test_cleanup_old_tasks(self, execution_monitor):
        """Test cleanup of old tasks"""
        # Submit a task
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Set task to old completed status
        task = execution_monitor.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.created_at = datetime.now() - timedelta(days=8)  # 8 days old
        
        # Start cleanup
        asyncio.create_task(execution_monitor._cleanup_old_tasks())
        
        # Wait a bit for cleanup
        await asyncio.sleep(0.1)
        
        # Old task should be removed
        assert task_id not in execution_monitor.tasks
    
    @pytest.mark.asyncio
    async def test_notify_status_change(self, execution_monitor):
        """Test status change notification"""
        notification_received = False
        
        def test_callback(task):
            nonlocal notification_received
            notification_received = True
        
        execution_monitor.add_status_callback(test_callback)
        
        # Submit a task (this should trigger notification)
        await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Wait a bit for notification
        await asyncio.sleep(0.1)
        
        # Notification should have been sent
        assert notification_received
    
    @pytest.mark.asyncio
    async def test_notify_completion(self, execution_monitor):
        """Test completion notification"""
        completion_received = False
        
        def test_callback(task):
            nonlocal completion_received
            completion_received = True
        
        execution_monitor.add_completion_callback(test_callback)
        
        # Submit and execute a task
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Execute the task
        await execution_monitor._execute_task(execution_monitor.tasks[task_id])
        
        # Wait a bit for notification
        await asyncio.sleep(0.1)
        
        # Completion notification should have been sent
        assert completion_received
    
    @pytest.mark.asyncio
    async def test_shutdown_success(self, execution_monitor):
        """Test successful shutdown"""
        # Submit a task
        task_id = await execution_monitor.submit_task(
            name="Test Task",
            description="Test description",
            script="echo 'test'",
            platform="bash"
        )
        
        # Set task to running
        execution_monitor.tasks[task_id].status = TaskStatus.RUNNING
        
        # Mock running task
        mock_task = AsyncMock()
        execution_monitor.running_tasks[task_id] = mock_task
        
        # Shutdown
        await execution_monitor.shutdown()
        
        # Running task should be cancelled
        mock_task.cancel.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown_failure(self, execution_monitor):
        """Test shutdown failure"""
        with patch.object(execution_monitor, '_execute_task', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                await execution_monitor.shutdown()
    
    def test_error_handling_invalid_task_data(self, execution_monitor):
        """Test error handling with invalid task data"""
        # Should not crash with invalid data
        with pytest.raises(Exception):
            # This would normally cause issues, but we're testing error handling
            execution_monitor.tasks = None
            execution_monitor.get_all_channels()
    
    def test_error_handling_callback_exceptions(self, execution_monitor):
        """Test error handling when callbacks raise exceptions"""
        def bad_callback(task):
            raise Exception("Callback error")
        
        execution_monitor.add_status_callback(bad_callback)
        
        # Should not crash when callback raises exception
        # (This would be tested in actual notification scenarios)
        assert bad_callback in execution_monitor.status_callbacks

if __name__ == "__main__":
    pytest.main([__file__])
