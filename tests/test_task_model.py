"""
Unit tests for the Task model.
"""

import pytest
from datetime import datetime
from src.models.task import Task

def test_task_with_id():
    """Test creating a Task with an ID."""
    task = Task(
        title="Test Task",
        description="Test Description",
        id="task-001"
    )
    assert task.id == "task-001"
    assert task.title == "Test Task"
    assert task.description == "Test Description"

def test_task_to_dict_with_id():
    """Test that to_dict includes the ID field."""
    task = Task(
        title="Test Task",
        description="Test Description",
        id="task-001"
    )
    task_dict = task.to_dict()
    assert task_dict["id"] == "task-001"
    assert task_dict["title"] == "Test Task"
    assert task_dict["description"] == "Test Description"

def test_task_from_dict_with_id():
    """Test creating a Task from a dictionary with an ID."""
    task_dict = {
        "id": "task-001",
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending",
        "priority": 3
    }
    task = Task.from_dict(task_dict)
    assert task.id == "task-001"
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.status == "pending"
    assert task.priority == 3

def test_priority_validation_string():
    """Test that priority is validated when passed as a string."""
    task = Task(
        title="Test Task",
        description="Test Description",
        priority="4"
    )
    assert task.priority == 4

def test_priority_validation_out_of_range_high():
    """Test that priority is clamped when out of range (high)."""
    task = Task(
        title="Test Task",
        description="Test Description",
        priority=10
    )
    assert task.priority == 5  # Should be clamped to max value (5)

def test_priority_validation_out_of_range_low():
    """Test that priority is clamped when out of range (low)."""
    task = Task(
        title="Test Task",
        description="Test Description",
        priority=0
    )
    assert task.priority == 1  # Should be clamped to min value (1)

def test_priority_validation_non_integer():
    """Test that priority is set correctly for string values."""
    task = Task(
        title="Test Task",
        description="Test Description",
        priority="high"  # Non-integer string
    )
    assert task.priority == 5  # 'high' should map to 5

def test_title_validation_numeric():
    """Test that numeric titles are rejected."""
    with pytest.raises(ValueError, match="Task title cannot be purely numeric"):
        Task(
            title="12345",
            description="Test Description"
        )

def test_title_validation_length():
    """Test that short titles are rejected."""
    with pytest.raises(ValueError, match="Task title must be at least 5 characters long"):
        Task(
            title="Test",
            description="Test Description"
        )
