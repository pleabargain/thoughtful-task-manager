"""
File handling utilities for the Thoughtful Task Manager.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import time

from ..models.task import Task

class FileHandler:
    """Handles file operations for tasks."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the file handler."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.tasks_file = self.data_dir / "tasks.json"
    
    def save_tasks(self, tasks: List[Task]) -> None:
        """Save tasks to file."""
        tasks_data = [task.to_dict() for task in tasks]
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks_data, f, indent=2)
    
    def load_tasks(self) -> List[Task]:
        """Load tasks from file."""
        if not self.tasks_file.exists():
            return []
        
        with open(self.tasks_file, 'r') as f:
            tasks_data = json.load(f)
        
        return [Task.from_dict(task_data) for task_data in tasks_data]
    
    def backup_tasks(self) -> None:
        """Create a backup of the tasks file."""
        if not self.tasks_file.exists():
            return
        
        backup_file = self.data_dir / f"tasks_backup_{int(time.time())}.json"
        import shutil
        shutil.copy2(self.tasks_file, backup_file) 