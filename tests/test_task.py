"""
Tests for the Task model.
"""

import pytest
from datetime import datetime
from src.models.task import Task

def test_task_creation():
    """Test basic task creation."""
    task = Task(
        title="Test Task",
        description="Test Description"
    )
    
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.status == "pending"
    assert task.priority == 1
    assert isinstance(task.created_date, datetime)
    assert task.dependencies == []

def test_task_to_dict():
    """Test task conversion to dictionary."""
    task = Task(
        title="Test Task",
        description="Test Description",
        dependencies=["task1", "task2"],
        status="in_progress",
        priority=2
    )
    
    task_dict = task.to_dict()
    
    assert task_dict["title"] == "Test Task"
    assert task_dict["description"] == "Test Description"
    assert task_dict["dependencies"] == ["task1", "task2"]
    assert task_dict["status"] == "in_progress"
    assert task_dict["priority"] == 2

def test_task_from_dict():
    """Test task creation from dictionary."""
    task_dict = {
        "title": "Test Task",
        "description": "Test Description",
        "dependencies": ["task1"],
        "status": "completed",
        "priority": 3,
        "created_date": datetime.now().isoformat()
    }
    
    task = Task.from_dict(task_dict)
    
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.dependencies == ["task1"]
    assert task.status == "completed"
    assert task.priority == 3 