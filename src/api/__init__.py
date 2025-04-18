"""
API package for Thoughtful Task Manager.
Provides RESTful API endpoints and MCP pattern implementation.
"""

from .base import BaseAPI
from .task_api import TaskAPI
from .ai_api import AIAPI

__all__ = ['BaseAPI', 'TaskAPI', 'AIAPI'] 