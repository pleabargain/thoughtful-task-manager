"""
Task API implementation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .base import BaseAPI
from ..models.task import Task
from ..utils.file_handler import FileHandler

class TaskAPI(BaseAPI):
    """API for task management operations."""
    
    def __init__(self, data_file=None):
        super().__init__()
        self._file_handler = FileHandler()
        if data_file:
            self._file_handler.tasks_file = Path(data_file)
        self._original_tasks_file = self._file_handler.tasks_file
    
    def initialize(self) -> None:
        """Initialize the Task API components."""
        # Keep the existing file handler if it has a custom tasks_file
        custom_tasks_file = getattr(self._file_handler, 'tasks_file', None)
        self._file_handler = FileHandler()
        if custom_tasks_file:
            self._file_handler.tasks_file = custom_tasks_file
        # TODO: Initialize model, controller, and presenter
    
    def validate(self) -> bool:
        """Validate the Task API configuration."""
        return all([
            self._file_handler is not None,
            self._model is not None,
            self._controller is not None,
            self._presenter is not None
        ])
    
    def create_task(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """Create a new task."""
        try:
            # Validate title
            if title.isdigit():
                raise ValueError("Task title cannot be purely numeric")
            if len(title) < 5:
                raise ValueError("Task title must be at least 5 characters long")
                
            # Check if a task with the same title already exists
            tasks = self._file_handler.load_tasks()
            title_exists = any(task.title == title for task in tasks)
            
            if title_exists:
                # Make the title unique by appending a suffix
                base_title = title
                suffix = 1
                while any(task.title == f"{base_title} ({suffix})" for task in tasks):
                    suffix += 1
                title = f"{base_title} ({suffix})"
            
            task = Task(title=title, description=description, **kwargs)
            tasks.append(task)
            self._file_handler.save_tasks(tasks)
            
            # Convert to dict and add created_at/updated_at for compatibility with tests
            task_dict = task.to_dict()
            task_dict['created_at'] = task_dict.pop('created_date')
            task_dict['updated_at'] = task_dict['created_at']
            return task_dict
        except ValueError as e:
            # Handle validation errors
            from rich.console import Console
            console = Console()
            console.print(f"[red]Error: {str(e)}[/red]")
            return None
    
    def get_task(self, task_id_or_title: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID or title."""
        tasks = self._file_handler.load_tasks()
        
        # First try to find by ID
        task = next((task for task in tasks if task.id == task_id_or_title), None)
        
        # If not found by ID, try to find by title
        if task is None:
            task = next((task for task in tasks if task.title == task_id_or_title), None)
        
        if task:
            # Convert to dict and add created_at/updated_at for compatibility with tests
            task_dict = task.to_dict()
            task_dict['created_at'] = task_dict.pop('created_date')
            task_dict['updated_at'] = task_dict['created_at']
            return task_dict
        return None
    
    def update_task(self, task_id_or_title: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a task by ID or title."""
        try:
            # Validate title if it's being updated
            if 'title' in kwargs:
                new_title = kwargs['title']
                if new_title.isdigit():
                    raise ValueError("Task title cannot be purely numeric")
                if len(new_title) < 5:
                    raise ValueError("Task title must be at least 5 characters long")
            
            tasks = self._file_handler.load_tasks()
            
            # First try to find by ID
            task_index = next((i for i, task in enumerate(tasks) if task.id == task_id_or_title), None)
            
            # If not found by ID, try to find by title
            if task_index is None:
                task_index = next((i for i, task in enumerate(tasks) if task.title == task_id_or_title), None)
            
            if task_index is not None:
                task = tasks[task_index]
                
                # Check if we're updating the title and if the new title would be a duplicate
                if 'title' in kwargs:
                    new_title = kwargs['title']
                    # Check if another task (not this one) already has this title
                    title_exists = any(t.title == new_title and t != task for t in tasks)
                    
                    if title_exists:
                        # Make the title unique by appending a suffix
                        base_title = new_title
                        suffix = 1
                        while any(t.title == f"{base_title} ({suffix})" and t != task for t in tasks):
                            suffix += 1
                        kwargs['title'] = f"{base_title} ({suffix})"
                
                # Update the task
                for key, value in kwargs.items():
                    setattr(task, key, value)
                
                self._file_handler.save_tasks(tasks)
                
                # Convert to dict and add created_at/updated_at for compatibility with tests
                task_dict = task.to_dict()
                task_dict['created_at'] = task_dict.pop('created_date')
                task_dict['updated_at'] = task_dict['created_at']
                return task_dict
            return None
        except ValueError as e:
            # Handle validation errors
            from rich.console import Console
            console = Console()
            console.print(f"[red]Error: {str(e)}[/red]")
            return None
    
    def delete_task(self, task_id_or_title: str) -> bool:
        """Delete a task by ID or title."""
        tasks = self._file_handler.load_tasks()
        initial_length = len(tasks)
        
        # Try to delete by ID first
        filtered_tasks = [task for task in tasks if task.id != task_id_or_title]
        
        # If no tasks were deleted by ID, try to delete by title
        if len(filtered_tasks) == initial_length:
            filtered_tasks = [task for task in tasks if task.title != task_id_or_title]
        
        if len(filtered_tasks) < initial_length:
            self._file_handler.save_tasks(filtered_tasks)
            return True
        return False
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks."""
        tasks = self._file_handler.load_tasks()
        
        # Convert to dicts and add created_at/updated_at for compatibility with tests
        task_dicts = []
        for task in tasks:
            task_dict = task.to_dict()
            task_dict['created_at'] = task_dict.pop('created_date')
            task_dict['updated_at'] = task_dict['created_at']
            task_dicts.append(task_dict)
        
        return task_dicts
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Get tasks by status."""
        tasks = self._file_handler.load_tasks()
        return [task for task in tasks if task.status == status]
    
    def get_tasks_by_priority(self, priority: int) -> List[Task]:
        """Get tasks by priority."""
        tasks = self._file_handler.load_tasks()
        return [task for task in tasks if task.priority == priority]
    
    def change_tasks_file(self, file_path: str) -> tuple[bool, str, int]:
        """
        Change the current tasks file.
        
        Args:
            file_path: Path to the new tasks file.
            
        Returns:
            A tuple of (success, message, task_count) where:
            - success: True if the file was changed successfully, False otherwise
            - message: A message explaining the result
            - task_count: Number of tasks in the file if successful, 0 otherwise
        """
        # Validate the file first
        is_valid, message, task_count = self._file_handler.validate_task_file(file_path)
        
        if not is_valid:
            return False, message, 0
        
        # Change the tasks file
        self._file_handler.tasks_file = Path(file_path)
        return True, f"Successfully changed to task file: {file_path}", task_count
    
    def reset_to_default_file(self) -> None:
        """Reset to the default tasks file."""
        self._file_handler.tasks_file = self._original_tasks_file
    
    def list_task_files(self, directory: Optional[str] = None) -> tuple[List[Path], int]:
        """
        List all task files in the specified directory.
        
        Args:
            directory: Directory to search for task files. Defaults to data directory.
            
        Returns:
            A tuple containing:
            - List of Path objects representing potential task files
            - Count of JSON files found
        """
        return self._file_handler.list_task_files(directory)
    
    def get_task_count(self, file_path: str) -> int:
        """
        Get the number of tasks in a file.
        
        Args:
            file_path: Path to the file to count tasks in.
            
        Returns:
            Number of tasks in the file, or 0 if the file is invalid.
        """
        return self._file_handler.get_task_count(file_path)
    
    def get_current_file_info(self) -> tuple[str, int]:
        """
        Get information about the current tasks file.
        
        Returns:
            A tuple containing:
            - The name of the current tasks file
            - The number of tasks in the file
        """
        current_file = str(self._file_handler.tasks_file)
        task_count = len(self.list_tasks())
        return current_file, task_count
