import os
import json
import pytest
from datetime import datetime
from src.main import TaskManager

@pytest.fixture
def test_data_file(tmp_path):
    """Create a temporary test data file."""
    return str(tmp_path / "test_tasks.json")

@pytest.fixture
def task_manager(test_data_file):
    """Create a TaskManager instance with the test data file."""
    return TaskManager(data_file=test_data_file)

@pytest.fixture
def sample_tasks():
    """Load sample tasks from the test_tasks.json file."""
    with open("data/test_tasks.json", 'r') as f:
        return json.load(f)['tasks']

def test_load_tasks(task_manager, test_data_file, sample_tasks):
    """Test loading tasks from a file."""
    # Write sample tasks to the test file
    with open(test_data_file, 'w') as f:
        json.dump({'tasks': sample_tasks}, f)
    
    # Create a new manager instance to load the tasks
    manager = TaskManager(data_file=test_data_file)
    loaded_tasks = manager.list_tasks()
    
    assert len(loaded_tasks) == len(sample_tasks)
    assert loaded_tasks[0]['id'] == sample_tasks[0]['id']
    assert loaded_tasks[0]['title'] == sample_tasks[0]['title']

def test_add_task(task_manager):
    """Test adding a new task."""
    new_task = {
        'id': 'task-004',
        'title': 'New Test Task',
        'status': 'pending',
        'priority': 'medium',
        'due_date': '2024-04-30'
    }
    
    added_task = task_manager.add_task(new_task)
    assert added_task['id'] == new_task['id']
    assert added_task['title'] == new_task['title']
    assert 'created_at' in added_task
    assert 'updated_at' in added_task

def test_update_task(task_manager, sample_tasks):
    """Test updating an existing task."""
    # First add a task
    task_manager.add_task(sample_tasks[0])
    
    # Update the task
    update_data = {
        'status': 'completed',
        'priority': 'high'
    }
    
    updated_task = task_manager.update_task(sample_tasks[0]['id'], update_data)
    assert updated_task['status'] == 'completed'
    assert updated_task['priority'] == 'high'
    assert 'updated_at' in updated_task

def test_delete_task(task_manager, sample_tasks):
    """Test deleting a task."""
    # First add a task
    task_manager.add_task(sample_tasks[0])
    
    # Delete the task
    success = task_manager.delete_task(sample_tasks[0]['id'])
    assert success is True
    
    # Verify the task is gone
    assert task_manager.get_task(sample_tasks[0]['id']) is None

def test_get_task(task_manager, sample_tasks):
    """Test getting a specific task."""
    # First add a task
    task_manager.add_task(sample_tasks[0])
    
    # Get the task
    task = task_manager.get_task(sample_tasks[0]['id'])
    assert task is not None
    assert task['id'] == sample_tasks[0]['id']
    assert task['title'] == sample_tasks[0]['title']
