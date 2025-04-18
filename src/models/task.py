"""
Task model for the Thoughtful Task Manager.
"""

from dataclasses import dataclass, fields
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

@dataclass
class Task:
    """Represents a single task in the system."""
    title: str
    description: str
    id: Optional[str] = None
    uuid: Optional[str] = None
    dependencies: List[str] = None
    status: str = "pending"
    priority: int = 1
    created_date: datetime = None
    due_date: Optional[datetime] = None
    model: str = "unknown"
    source: str = "human"
    
    # Priority mapping for string priorities
    PRIORITY_MAP = {
        'low': 1,
        'medium-low': 2,
        'medium': 3,
        'medium-high': 4,
        'high': 5
    }
    
    def __post_init__(self):
        """Initialize default values and validate after dataclass initialization."""
        if self.dependencies is None:
            self.dependencies = []
        if self.created_date is None:
            self.created_date = datetime.now()
        if self.uuid is None:
            self.uuid = str(uuid.uuid4())
        
        # Title validation
        if self.title:
            # Check if title is purely numeric
            if self.title.isdigit():
                raise ValueError("Task title cannot be purely numeric")
            
            # Check minimum length
            if len(self.title) < 5:
                raise ValueError("Task title must be at least 5 characters long")
        
        # Validate priority
        if isinstance(self.priority, str):
            # Try to convert string priority to int
            if self.priority.lower() in self.PRIORITY_MAP:
                self.priority = self.PRIORITY_MAP[self.priority.lower()]
            else:
                try:
                    self.priority = int(self.priority)
                except ValueError:
                    self.priority = 3  # Default to medium priority
        
        # Clamp priority to valid range (1-5)
        if not isinstance(self.priority, int) or self.priority < 1 or self.priority > 5:
            self.priority = max(1, min(5, self.priority if isinstance(self.priority, int) else 3))
    
    def to_dict(self) -> dict:
        """Convert task to dictionary format."""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "title": self.title,
            "description": self.description,
            "dependencies": self.dependencies,
            "status": self.status,
            "priority": self.priority,
            "created_date": self.created_date.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "model": self.model,
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create a Task instance from dictionary data."""
        # Create a copy to avoid modifying the original
        task_data = data.copy()
        
        # Ensure required fields exist
        if "title" not in task_data:
            task_data["title"] = f"Task {task_data.get('id', 'Unknown')}"
        
        if "description" not in task_data:
            task_data["description"] = "No description provided"
        
        # Map field names
        if "created_at" in task_data:
            task_data["created_date"] = task_data.pop("created_at")
        if "updated_at" in task_data:
            task_data.pop("updated_at")  # Remove as we don't have this field
        
        # Handle non-standard fields by removing them
        standard_fields = {"id", "uuid", "title", "description", "dependencies", "status", 
                          "priority", "created_date", "due_date", "model", "source"}
        
        # Store any extra fields in a safe way
        extra_fields = {k: v for k, v in task_data.items() 
                       if k not in standard_fields and k not in ["tags", "notes"]}
        
        # Remove non-standard fields
        for field in list(task_data.keys()):
            if field not in standard_fields:
                task_data.pop(field)
        
        # Convert date strings to datetime objects
        if "created_date" in task_data and isinstance(task_data["created_date"], str):
            try:
                task_data["created_date"] = datetime.fromisoformat(task_data["created_date"])
            except ValueError:
                # Handle different date formats
                task_data["created_date"] = datetime.now()
        
        if "due_date" in task_data and task_data["due_date"] and isinstance(task_data["due_date"], str):
            try:
                task_data["due_date"] = datetime.fromisoformat(task_data["due_date"])
            except ValueError:
                # If we can't parse the date, set it to None
                task_data["due_date"] = None
        
        # Ensure we have valid fields for Task initialization
        valid_fields = [f.name for f in fields(cls)]
        task_data = {k: v for k, v in task_data.items() if k in valid_fields}
        
        return cls(**task_data)
