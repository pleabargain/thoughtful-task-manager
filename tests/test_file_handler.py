"""
Unit tests for the FileHandler.
"""

import json
import pytest
from pathlib import Path
from src.utils.file_handler import FileHandler
from src.models.task import Task

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory."""
    return tmp_path

@pytest.fixture
def file_handler(temp_data_dir):
    """Create a FileHandler with a temporary data directory."""
    return FileHandler(data_dir=str(temp_data_dir))

def test_load_tasks_empty_file(file_handler):
    """Test loading tasks from an empty file."""
    # Ensure the file doesn't exist
    assert not file_handler.tasks_file.exists()
    
    # Load tasks should return an empty list
    tasks = file_handler.load_tasks()
    assert isinstance(tasks, list)
    assert len(tasks) == 0

def test_load_tasks_direct_list(file_handler, temp_data_dir):
    """Test loading tasks from a file with a direct list of tasks."""
    # Create a test file with a direct list of tasks
    tasks_data = [
        {
            "id": "task-001",
            "title": "Test Task 1",
            "description": "Test Description 1",
            "status": "pending",
            "priority": 3
        },
        {
            "id": "task-002",
            "title": "Test Task 2",
            "description": "Test Description 2",
            "status": "in_progress",
            "priority": 4
        }
    ]
    
    with open(file_handler.tasks_file, 'w') as f:
        json.dump(tasks_data, f)
    
    # Load tasks
    tasks = file_handler.load_tasks()
    
    # Verify tasks were loaded correctly
    assert isinstance(tasks, list)
    assert len(tasks) == 2
    assert tasks[0].id == "task-001"
    assert tasks[0].title == "Test Task 1"
    assert tasks[1].id == "task-002"
    assert tasks[1].title == "Test Task 2"

def test_load_tasks_with_tasks_key(file_handler):
    """Test loading tasks from a file with a 'tasks' key."""
    # Create a test file with a 'tasks' key
    tasks_data = {
        "tasks": [
            {
                "id": "task-001",
                "title": "Test Task 1",
                "description": "Test Description 1",
                "status": "pending",
                "priority": 3
            },
            {
                "id": "task-002",
                "title": "Test Task 2",
                "description": "Test Description 2",
                "status": "in_progress",
                "priority": 4
            }
        ]
    }
    
    with open(file_handler.tasks_file, 'w') as f:
        json.dump(tasks_data, f)
    
    # Load tasks
    tasks = file_handler.load_tasks()
    
    # Verify tasks were loaded correctly
    assert isinstance(tasks, list)
    assert len(tasks) == 2
    assert tasks[0].id == "task-001"
    assert tasks[0].title == "Test Task 1"
    assert tasks[1].id == "task-002"
    assert tasks[1].title == "Test Task 2"

def test_save_and_load_tasks(file_handler):
    """Test saving and loading tasks."""
    # Create some tasks
    tasks = [
        Task(
            id="task-001",
            title="Test Task 1",
            description="Test Description 1",
            status="pending",
            priority=3
        ),
        Task(
            id="task-002",
            title="Test Task 2",
            description="Test Description 2",
            status="in_progress",
            priority=4
        )
    ]
    
    # Save tasks
    file_handler.save_tasks(tasks)
    
    # Verify file was created
    assert file_handler.tasks_file.exists()
    
    # Load tasks
    loaded_tasks = file_handler.load_tasks()
    
    # Verify tasks were loaded correctly
    assert isinstance(loaded_tasks, list)
    assert len(loaded_tasks) == 2
    assert loaded_tasks[0].id == "task-001"
    assert loaded_tasks[0].title == "Test Task 1"
    assert loaded_tasks[1].id == "task-002"
    assert loaded_tasks[1].title == "Test Task 2"
