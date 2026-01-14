"""Tests for the persistence layer."""

import pytest
import tempfile
import os
from datetime import datetime

from src.persistence import TaskStorage, TaskRecord
from src.persistence.storage import ExecutionStepRecord


@pytest.fixture
def temp_storage():
    """Create a temporary storage for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    storage = TaskStorage(db_path)
    yield storage

    # Cleanup
    os.unlink(db_path)


def create_sample_task(input_text: str = "test input", thread_id: str = "test-thread"):
    """Create a sample task record for testing."""
    return TaskRecord(
        id=None,
        input_text=input_text,
        output_text="test output",
        tools_used=["TextProcessorTool"],
        execution_steps=[
            ExecutionStepRecord(
                step_number=1,
                description="Test step",
                timestamp=datetime.now().isoformat(),
            )
        ],
        created_at=datetime.now().isoformat(),
        thread_id=thread_id,
    )


class TestTaskStorage:
    """Tests for TaskStorage."""

    def test_save_and_get_task(self, temp_storage):
        """Test saving and retrieving a task."""
        record = create_sample_task()
        task_id = temp_storage.save_task(record)

        assert task_id is not None
        assert task_id > 0

        retrieved = temp_storage.get_task(task_id)
        assert retrieved is not None
        assert retrieved.input_text == "test input"
        assert retrieved.output_text == "test output"
        assert "TextProcessorTool" in retrieved.tools_used

    def test_get_all_tasks(self, temp_storage):
        """Test getting all tasks."""
        # Save multiple tasks
        for i in range(5):
            record = create_sample_task(input_text=f"task {i}")
            temp_storage.save_task(record)

        tasks = temp_storage.get_all_tasks()
        assert len(tasks) == 5

    def test_get_tasks_with_pagination(self, temp_storage):
        """Test pagination for getting tasks."""
        for i in range(10):
            record = create_sample_task(input_text=f"task {i}")
            temp_storage.save_task(record)

        # Get first 5
        tasks = temp_storage.get_all_tasks(limit=5, offset=0)
        assert len(tasks) == 5

        # Get next 5
        tasks = temp_storage.get_all_tasks(limit=5, offset=5)
        assert len(tasks) == 5

    def test_get_tasks_by_thread(self, temp_storage):
        """Test filtering tasks by thread."""
        # Create tasks for different threads
        for i in range(3):
            record = create_sample_task(thread_id="thread-1")
            temp_storage.save_task(record)

        for i in range(2):
            record = create_sample_task(thread_id="thread-2")
            temp_storage.save_task(record)

        thread1_tasks = temp_storage.get_tasks_by_thread("thread-1")
        thread2_tasks = temp_storage.get_tasks_by_thread("thread-2")

        assert len(thread1_tasks) == 3
        assert len(thread2_tasks) == 2

    def test_delete_task(self, temp_storage):
        """Test deleting a task."""
        record = create_sample_task()
        task_id = temp_storage.save_task(record)

        # Verify task exists
        assert temp_storage.get_task(task_id) is not None

        # Delete task
        result = temp_storage.delete_task(task_id)
        assert result is True

        # Verify task is deleted
        assert temp_storage.get_task(task_id) is None

    def test_delete_nonexistent_task(self, temp_storage):
        """Test deleting a task that doesn't exist."""
        result = temp_storage.delete_task(9999)
        assert result is False

    def test_clear_all(self, temp_storage):
        """Test clearing all tasks."""
        for i in range(5):
            record = create_sample_task()
            temp_storage.save_task(record)

        assert len(temp_storage.get_all_tasks()) == 5

        temp_storage.clear_all()

        assert len(temp_storage.get_all_tasks()) == 0

    def test_task_to_dict(self, temp_storage):
        """Test TaskRecord.to_dict() method."""
        record = create_sample_task()
        task_id = temp_storage.save_task(record)
        retrieved = temp_storage.get_task(task_id)

        task_dict = retrieved.to_dict()

        assert "id" in task_dict
        assert "input_text" in task_dict
        assert "output_text" in task_dict
        assert "tools_used" in task_dict
        assert "execution_steps" in task_dict
        assert isinstance(task_dict["execution_steps"], list)
