"""
Tests for simulating user input for complete task operations.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import os
import tempfile
from src.main import TaskManager

class TestUserInput(unittest.TestCase):
    """Test cases for simulating user input for task operations."""

    def setUp(self):
        """Set up test environment with a temporary task file."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.temp_dir.name, "test_tasks.json")
        self.task_manager = TaskManager(data_file=self.data_file)
        
        # Initialize the task manager
        self.task_manager.initialize()

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_complete_task_lifecycle(self):
        """Test the complete lifecycle of a task from creation to completion."""
        # Create a task directly
        task = self.task_manager.add_task({
            'title': 'Complete Project Documentation',
            'description': 'Write comprehensive documentation for the project',
            'priority': 5,
            'status': 'pending'
        })
        
        # Update the task status directly
        self.task_manager.update_task('Complete Project Documentation', {'status': 'in_progress'})
        self.task_manager.update_task('Complete Project Documentation', {'status': 'completed'})
        
        # Verify the task was saved to the file with the correct status
        with open(self.data_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(len(saved_data), 1)
        saved_task = saved_data[0]
        self.assertEqual(saved_task["title"], "Complete Project Documentation")
        self.assertEqual(saved_task["description"], "Write comprehensive documentation for the project")
        self.assertEqual(saved_task["priority"], 5)
        self.assertEqual(saved_task["status"], "completed")

    @patch('rich.prompt.Prompt.ask')
    def test_task_priority_validation(self, mock_ask):
        """Test that task priority is validated correctly."""
        # Mock user inputs with invalid then valid priority
        mock_ask.side_effect = [
            "2",  # Add task
            "Priority Test Task",  # Task title
            "Testing priority validation",  # Description
            "10",  # Invalid priority (out of range)
            "5",  # Valid priority (high)
            "8"   # Exit
        ]
        
        # Run the application with mocked input
        with patch('rich.console.Console.print') as mock_print:
            try:
                self.task_manager.run()
            except SystemExit:
                pass  # Expected when exiting
            except ValueError:
                self.fail("Priority validation failed")
        
        # Verify task was created with correct priority
        tasks = self.task_manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['priority'], 5)  # Should be 5 (high)

    @patch('rich.prompt.Prompt.ask')
    def test_delete_task(self, mock_ask):
        """Test deleting a task."""
        # First create a task
        test_task = {
            'id': 'test-001',
            'title': 'Test Task',
            'description': 'Task to be deleted',
            'status': 'pending',
            'priority': 3
        }
        self.task_manager.add_task(test_task)
        
        # Verify task was created
        tasks = self.task_manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        
        # Mock user inputs for deleting the task
        mock_ask.side_effect = [
            "4",  # Delete task
            "Test Task",  # Task to delete
            "8"   # Exit
        ]
        
        # Run the application with mocked input
        with patch('rich.console.Console.print') as mock_print:
            try:
                self.task_manager.run()
            except SystemExit:
                pass  # Expected when exiting
        
        # Verify task was deleted
        tasks = self.task_manager.list_tasks()
        self.assertEqual(len(tasks), 0)

if __name__ == '__main__':
    unittest.main()
