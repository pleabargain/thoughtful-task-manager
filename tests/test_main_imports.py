"""
Unit tests for verifying imports in the main module.
"""

import importlib
import inspect
import pytest
import sys
from pathlib import Path

def test_main_module_imports():
    """Test that all necessary imports are present in the main module."""
    # Import the main module
    import src.main
    
    # Reload the module to ensure we're testing the latest version
    importlib.reload(src.main)
    
    # Get the source code of the module
    source = inspect.getsource(src.main)
    
    # Check for essential imports
    essential_imports = [
        "import sys",
        "import os",
        "from pathlib import Path",
        "from rich.console import Console",
        "from rich.prompt import Prompt",
        "from rich.table import Table",
        "from .api import TaskAPI"
    ]
    
    for imp in essential_imports:
        assert imp in source, f"Missing import: {imp}"

def test_path_usage():
    """Test that Path is properly imported and used."""
    # Import the main module
    from src.main import TaskManager
    
    # Create a TaskManager instance
    manager = TaskManager(data_file="data/test_path.json")
    
    # Test that the current_file attribute is set correctly
    assert manager.current_file == "data/test_path.json"
    
    # Test that we can get the filename using Path
    filename = Path(manager.current_file).name
    assert filename == "test_path.json"
    
    # Test the list_task_files method (which uses Path)
    # This is a more complex test that requires mocking, so we'll just
    # verify that the method exists and doesn't raise an error when called
    assert hasattr(manager, "list_task_files")
    
    # Mock the task_api.list_task_files method to return a list of paths
    original_method = manager.task_api.list_task_files
    try:
        # Replace with a mock that returns a list with a single Path
        test_path = Path("data/test_path.json")
        manager.task_api.list_task_files = lambda x: [test_path]
        
        # Call the method and verify it doesn't raise an exception
        files = manager.list_task_files()
        assert files is not None
        assert len(files) == 1
        assert files[0] == test_path
    finally:
        # Restore the original method
        manager.task_api.list_task_files = original_method
