"""
File handling utilities for the Thoughtful Task Manager.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time
import jsonschema

from ..models.task import Task

class FileHandler:
    """Handles file operations for tasks."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the file handler."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.tasks_file = self.data_dir / "tasks.json"
        self.schema_file = self.data_dir / "task_schema.json"
    
    def save_tasks(self, tasks: List[Task]) -> None:
        """Save tasks to file."""
        tasks_data = [task.to_dict() for task in tasks]
        
        # Validate against schema if available
        if self.schema_file.exists():
            self.validate_against_schema(tasks_data)
            
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks_data, f, indent=2)
    
    def load_tasks(self) -> List[Task]:
        """Load tasks from file."""
        if not self.tasks_file.exists():
            return []
        
        with open(self.tasks_file, 'r') as f:
            data = json.load(f)
        
        # Handle both formats: direct list of tasks or {"tasks": [...]}
        tasks_data = data.get("tasks", data) if isinstance(data, dict) else data
        
        # Validate against schema if available
        if self.schema_file.exists():
            self.validate_against_schema(tasks_data)
            
        return [Task.from_dict(task_data) for task_data in tasks_data]
    
    def validate_against_schema(self, tasks_data: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validate tasks data against the JSON schema.
        
        Args:
            tasks_data: List of task dictionaries to validate
            
        Returns:
            A tuple of (is_valid, message) where:
            - is_valid: True if the data is valid according to the schema, False otherwise
            - message: A message explaining the validation result
        """
        if not self.schema_file.exists():
            return True, "No schema file found for validation"
        
        try:
            with open(self.schema_file, 'r') as f:
                schema = json.load(f)
            
            jsonschema.validate(instance=tasks_data, schema=schema)
            return True, "Tasks data is valid according to the schema"
        except jsonschema.exceptions.ValidationError as e:
            return False, f"Schema validation error: {str(e)}"
        except Exception as e:
            return False, f"Error during schema validation: {str(e)}"
    
    def backup_tasks(self) -> None:
        """Create a backup of the tasks file."""
        if not self.tasks_file.exists():
            return
        
        backup_file = self.data_dir / f"tasks_backup_{int(time.time())}.json"
        import shutil
        shutil.copy2(self.tasks_file, backup_file)
    
    def list_task_files(self, directory: Optional[str] = None) -> tuple[List[Path], int]:
        """
        List all JSON files in the specified directory that could contain tasks.
        
        Args:
            directory: Directory to search for task files. Defaults to self.data_dir.
            
        Returns:
            A tuple containing:
            - List of Path objects representing potential task files
            - Count of JSON files found
        """
        search_dir = Path(directory) if directory else self.data_dir
        
        # Ensure the directory exists
        if not search_dir.exists():
            search_dir.mkdir(parents=True, exist_ok=True)
            return [], 0
        
        # Find all JSON files in the directory
        json_files = sorted([f for f in search_dir.glob("*.json")])
        return json_files, len(json_files)
    
    def validate_task_file(self, file_path: str) -> tuple[bool, str, int]:
        """
        Validate if a file contains valid task data.
        
        Args:
            file_path: Path to the file to validate.
            
        Returns:
            A tuple of (is_valid, message, task_count) where:
            - is_valid: True if the file contains valid task data, False otherwise
            - message: A message explaining the validation result
            - task_count: Number of tasks in the file if valid, 0 otherwise
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return False, f"File does not exist: {file_path}", 0
        
        try:
            # Try to load the file as JSON
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Check if it's a list or a dict with a 'tasks' key
            tasks_data = data.get("tasks", data) if isinstance(data, dict) else data
            
            # Verify it's a list
            if not isinstance(tasks_data, list):
                return False, f"File does not contain a list of tasks: {file_path}", 0
            
            # If the list is empty, it's still valid but has 0 tasks
            if not tasks_data:
                return True, f"File contains an empty task list: {file_path}", 0
            
            # Count the number of valid tasks
            valid_task_count = 0
            for task in tasks_data:
                # Check if it has the minimum required fields
                if isinstance(task, dict) and ('title' in task or 'id' in task):
                    valid_task_count += 1
            
            # If no valid tasks were found, return an error
            if valid_task_count == 0:
                return False, f"No valid tasks found in file: {file_path}", 0
            
            # If some tasks are valid but not all, provide a warning
            if valid_task_count < len(tasks_data):
                return True, f"File contains {valid_task_count} valid tasks (out of {len(tasks_data)}): {file_path}", valid_task_count
            
            # All tasks are valid
            return True, f"File contains {valid_task_count} valid tasks: {file_path}", valid_task_count
            
        except json.JSONDecodeError:
            return False, f"File contains invalid JSON: {file_path}", 0
        except (IOError, KeyError, TypeError) as e:
            return False, f"Error validating file: {file_path} - {str(e)}", 0
    
    def get_task_count(self, file_path: str) -> int:
        """
        Get the number of tasks in a file.
        
        Args:
            file_path: Path to the file to count tasks in.
            
        Returns:
            Number of tasks in the file, or 0 if the file is invalid.
        """
        is_valid, _, task_count = self.validate_task_file(file_path)
        return task_count if is_valid else 0
