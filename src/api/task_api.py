"""
Task API implementation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import BaseAPI
from ..models.task import Task
from ..utils.file_handler import FileHandler

class TaskAPI(BaseAPI):
    """API for task management operations."""
    
    def __init__(self):
        super().__init__()
        self._file_handler = FileHandler()
    
    def initialize(self) -> None:
        """Initialize the Task API components."""
        self._file_handler = FileHandler()
        # TODO: Initialize model, controller, and presenter
    
    def validate(self) -> bool:
        """Validate the Task API configuration."""
        return all([
            self._file_handler is not None,
            self._model is not None,
            self._controller is not None,
            self._presenter is not None
        ])
    
    def create_task(self, title: str, description: str, **kwargs) -> Task:
        """Create a new task."""
        task = Task(title=title, description=description, **kwargs)
        tasks = self._file_handler.load_tasks()
        tasks.append(task)
        self._file_handler.save_tasks(tasks)
        return task
    
    def get_task(self, title: str) -> Optional[Task]:
        """Get a task by title."""
        tasks = self._file_handler.load_tasks()
        return next((task for task in tasks if task.title == title), None)
    
    def update_task(self, title: str, **kwargs) -> Optional[Task]:
        """Update a task by title."""
        tasks = self._file_handler.load_tasks()
        for task in tasks:
            if task.title == title:
                for key, value in kwargs.items():
                    setattr(task, key, value)
                self._file_handler.save_tasks(tasks)
                return task
        return None
    
    def delete_task(self, title: str) -> bool:
        """Delete a task by title."""
        tasks = self._file_handler.load_tasks()
        initial_length = len(tasks)
        tasks = [task for task in tasks if task.title != title]
        if len(tasks) < initial_length:
            self._file_handler.save_tasks(tasks)
            return True
        return False
    
    def list_tasks(self) -> List[Task]:
        """Get all tasks."""
        return self._file_handler.load_tasks()
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Get tasks by status."""
        tasks = self._file_handler.load_tasks()
        return [task for task in tasks if task.status == status]
    
    def get_tasks_by_priority(self, priority: int) -> List[Task]:
        """Get tasks by priority."""
        tasks = self._file_handler.load_tasks()
        return [task for task in tasks if task.priority == priority] 