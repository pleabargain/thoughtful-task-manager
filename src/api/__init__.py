"""
API package for Thoughtful Task Manager.
Provides RESTful API endpoints and MCP pattern implementation.
"""

from .base import BaseAPI
from src.api.task_api import TaskAPI
from src.api.ai_api import AIAPI

__all__ = ['BaseAPI', 'TaskAPI', 'AIAPI'] 