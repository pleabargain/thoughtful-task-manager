"""
Base API class implementing MCP pattern.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseAPI(ABC):
    """Base class for all APIs implementing MCP pattern."""
    
    def __init__(self):
        self._model = None
        self._controller = None
        self._presenter = None
    
    @property
    def model(self) -> Any:
        """Get the model component."""
        return self._model
    
    @model.setter
    def model(self, value: Any) -> None:
        """Set the model component."""
        self._model = value
    
    @property
    def controller(self) -> Any:
        """Get the controller component."""
        return self._controller
    
    @controller.setter
    def controller(self, value: Any) -> None:
        """Set the controller component."""
        self._controller = value
    
    @property
    def presenter(self) -> Any:
        """Get the presenter component."""
        return self._presenter
    
    @presenter.setter
    def presenter(self, value: Any) -> None:
        """Set the presenter component."""
        self._presenter = value
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the API components."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the API configuration."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert API state to dictionary."""
        return {
            'model': self._model.__class__.__name__ if self._model else None,
            'controller': self._controller.__class__.__name__ if self._controller else None,
            'presenter': self._presenter.__class__.__name__ if self._presenter else None
        } 