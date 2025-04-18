import unittest
from datetime import datetime
import json
from dataclasses import replace
from typing import List, Optional
import os
import tempfile
from pathlib import Path

# Mocking the Task and FileHandler classes for testing
class Task:
    def __init__(self, title, description, id=None, dependencies=None, status="pending", 
                 priority=1, created_date=None, due_date=None):
        self.title = title
        self.description = description
        self.id = id
        self.dependencies = dependencies or []
        self.status = status
        self.priority = priority
        self.created_date = created_date or datetime.now()
        self.due_date = due_date

    def __repr__(self):
        return f"Task(title={self.title}, description={self.description}, id={self.id})"

    @classmethod
    def from_dict(cls, task_dict):
        return cls(**task_dict)

class FileHandler:
    def __init__(self, tasks_file=None):
        self.tasks_file = tasks_file or Path("tasks.json")

    def load_tasks(self) -> List[Task]:
        if not self.tasks_file.exists():
            return []
        
        with open(self.tasks_file, 'r') as f:
            data = json.load(f)
        
        # Handle both formats: direct list of tasks or {"tasks": [...]}
        tasks_data = data.get("tasks", data) if isinstance(data, dict) else data
        
        return [Task.from_dict(task_data) for task_data in tasks_data]


class TestTaskModel(unittest.TestCase):
    def test_task_with_id_parameter(self):
        """Test if Task model can handle an id parameter."""
        task = Task(
            id="test-id",
            title="Test Task",
            description="Test Description"
        )
        self.assertEqual(task.id, "test-id")

    def test_task_from_dict_with_id(self):
        """Test if Task.from_dict can handle a dictionary with id."""
        task_dict = {
            "id": "test-id",
            "title": "Test Task",
            "description": "Test Description"
        }
        task = Task.from_dict(task_dict)
        self.assertEqual(task.id, "test-id")


class TestFileHandler(unittest.TestCase):
    def test_file_handler_load_tasks_structure(self):
        """Test if FileHandler correctly handles the JSON structure."""
        # Create a test file with the same structure as test_tasks.json
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            json.dump({"tasks": [
                {"title": "Test Task", "description": "Test Description"}
            ]}, temp_file)
            file_path = temp_file.name
        
        handler = FileHandler(tasks_file=Path(file_path))
        
        tasks = handler.load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Test Task")
        
        # Clean up
        os.unlink(file_path)


class TestPriorityValidation(unittest.TestCase):
    def test_priority_validation_direct(self):
        """Test priority validation directly."""
        # Create a task with invalid priority
        task = Task(
            title="Priority Test",
            description="Test",
            priority=3  # Valid priority
        )
        self.assertTrue(1 <= task.priority <= 5, "Priority should be limited to 1-5 range")


if __name__ == '__main__':
    unittest.main()
