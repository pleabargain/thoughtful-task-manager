"""
Task model for the Thoughtful Task Manager.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Task:
    """Represents a single task in the system."""
    title: str
    description: str
    dependencies: List[str] = None
    status: str = "pending"
    priority: int = 1
    created_date: datetime = None
    due_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass initialization."""
        if self.dependencies is None:
            self.dependencies = []
        if self.created_date is None:
            self.created_date = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert task to dictionary format."""
        return {
            "title": self.title,
            "description": self.description,
            "dependencies": self.dependencies,
            "status": self.status,
            "priority": self.priority,
            "created_date": self.created_date.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create a Task instance from dictionary data."""
        if "created_date" in data:
            data["created_date"] = datetime.fromisoformat(data["created_date"])
        if "due_date" in data and data["due_date"]:
            data["due_date"] = datetime.fromisoformat(data["due_date"])
        return cls(**data) 