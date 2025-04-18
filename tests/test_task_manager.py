"""
Tests for the TaskManager class.
"""
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
from src.main import TaskManager

class TestTaskManager(unittest.TestCase):
    """Test cases for the TaskManager class."""

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

    def test_add_task_dict_attribute_error(self):
        """Test that an error is raised when trying to access title attribute on a dict."""
        # Mock the create_task method to return a dictionary
        with patch.object(self.task_manager.task_api, 'create_task') as mock_create_task:
            # Set up the mock to return a dictionary
            mock_create_task.return_value = {
                'id': 'test-001',
                'title': 'Test Task',
                'description': 'Test Description',
                'status': 'pending',
                'priority': 3,
                'created_at': '2025-04-18T12:00:00',
                'updated_at': '2025-04-18T12:00:00'
            }
            
            # Test that accessing task.title raises an AttributeError
            with self.assertRaises(AttributeError) as context:
                # This simulates what happens in the run method
                task = self.task_manager.add_task({
                    'title': 'Test Task',
                    'description': 'Test Description'
                })
                # This will raise AttributeError: 'dict' object has no attribute 'title'
                print(f"Created task: {task.title}")
            
            # Verify the specific error message
            self.assertIn("'dict' object has no attribute 'title'", str(context.exception))
    
    def test_display_tasks_with_dict_tasks(self):
        """Test that display_tasks correctly handles dictionary tasks."""
        # Create sample task dictionaries
        task_dicts = [
            {
                'id': 'test-001',
                'title': 'Test Task 1',
                'description': 'Test Description 1',
                'status': 'pending',
                'priority': 3,
                'created_at': '2025-04-18T12:00:00',
                'updated_at': '2025-04-18T12:00:00'
            },
            {
                'id': 'test-002',
                'title': 'Test Task 2',
                'description': 'Test Description 2',
                'status': 'completed',
                'priority': 5,
                'created_at': '2025-04-18T12:00:00',
                'updated_at': '2025-04-18T12:00:00'
            }
        ]
        
        # Mock the list_tasks method to return the sample dictionaries
        with patch.object(self.task_manager.task_api, 'list_tasks', return_value=task_dicts):
            # Mock the console.print method
            with patch('src.main.console.print') as mock_print:
                # Call display_tasks - this should now work without raising an AttributeError
                self.task_manager.display_tasks(task_dicts)
                
                # Assert that console.print was called (table was displayed)
                mock_print.assert_called()
    
    def test_duplicate_title_prevention(self):
        """Test that duplicate task titles are automatically made unique."""
        # Create a task with a specific title
        first_title = "Test Task"
        first_task = self.task_manager.add_task({
            'title': first_title,
            'description': 'First task description'
        })
        
        # Create another task with the same title
        second_task = self.task_manager.add_task({
            'title': first_title,
            'description': 'Second task description'
        })
        
        # Verify that the second task's title was modified to be unique
        self.assertNotEqual(first_task['title'], second_task['title'])
        self.assertEqual(second_task['title'], f"{first_title} (1)")
        
        # Create a third task with the same title
        third_task = self.task_manager.add_task({
            'title': first_title,
            'description': 'Third task description'
        })
        
        # Verify that the third task's title was modified to be unique
        self.assertNotEqual(first_task['title'], third_task['title'])
        self.assertNotEqual(second_task['title'], third_task['title'])
        self.assertEqual(third_task['title'], f"{first_title} (2)")
    
    def test_update_task_title_uniqueness(self):
        """Test that updating a task's title to a duplicate title makes it unique."""
        # Create two tasks with different titles
        first_task = self.task_manager.add_task({
            'title': "First Task",
            'description': 'First task description'
        })
        
        second_task = self.task_manager.add_task({
            'title': "Second Task",
            'description': 'Second task description'
        })
        
        # Update the second task's title to match the first task's title
        updated_task = self.task_manager.update_task(second_task['title'], {'title': first_task['title']})
        
        # Verify that the updated title was modified to be unique
        self.assertNotEqual(updated_task['title'], first_task['title'])
        self.assertEqual(updated_task['title'], f"{first_task['title']} (1)")
        
        # Create a third task
        third_task = self.task_manager.add_task({
            'title': "Third Task",
            'description': 'Third task description'
        })
        
        # Update the third task's title to match the first task's title
        updated_third_task = self.task_manager.update_task(third_task['title'], {'title': first_task['title']})
        
        # Verify that the updated title was modified to be unique
        self.assertNotEqual(updated_third_task['title'], first_task['title'])
        self.assertNotEqual(updated_third_task['title'], updated_task['title'])
        self.assertEqual(updated_third_task['title'], f"{first_task['title']} (2)")
    
    def test_create_new_task_file(self):
        """Test that create_new_task_file creates a new file correctly."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set the default_data_dir to the temporary directory
            self.task_manager.default_data_dir = temp_dir
            
            # Mock the Prompt.ask method to return a file name
            with patch('src.main.Prompt.ask', side_effect=["test_new_file", "y"]) as mock_ask:
                # Mock the console.print method
                with patch('src.main.console.print') as mock_print:
                    # Mock the change_tasks_file method to return success
                    with patch.object(self.task_manager.task_api, 'change_tasks_file', 
                                     return_value=(True, "File loaded successfully", 0)) as mock_change:
                        # Call the method
                        self.task_manager.create_new_task_file()
                        
                        # Verify that the file was created
                        file_path = os.path.join(temp_dir, "test_new_file.json")
                        self.assertTrue(os.path.exists(file_path))
                        
                        # Verify that the file contains an empty array
                        with open(file_path, 'r') as f:
                            content = f.read()
                            self.assertEqual(content, "[]")
                        
                        # Verify that the user was asked to switch to the new file
                        mock_ask.assert_any_call("Switch to the new file?", choices=["y", "n"], default="y")
                        
                        # Verify that change_tasks_file was called with the correct path
                        mock_change.assert_called_once_with(file_path)
                        
                        # Verify that success messages were printed
                        mock_print.assert_any_call(f"[green]Created new task file: test_new_file.json[/green]")
    
    def test_create_new_task_file_existing(self):
        """Test that create_new_task_file handles existing files correctly."""
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set the default_data_dir to the temporary directory
            self.task_manager.default_data_dir = temp_dir
            
            # Create an existing file
            file_path = os.path.join(temp_dir, "existing_file.json")
            with open(file_path, 'w') as f:
                f.write('["existing content"]')
            
            # Mock the Prompt.ask method to return a file name and choose not to overwrite
            with patch('src.main.Prompt.ask', side_effect=["existing_file", "n"]) as mock_ask:
                # Mock the console.print method
                with patch('src.main.console.print') as mock_print:
                    # Call the method
                    self.task_manager.create_new_task_file()
                    
                    # Verify that the user was asked about overwriting
                    mock_ask.assert_any_call(
                        "File existing_file.json already exists. Overwrite?",
                        choices=["y", "n"],
                        default="n"
                    )
                    
                    # Verify that the operation was cancelled
                    mock_print.assert_any_call("[yellow]Operation cancelled.[/yellow]")
                    
                    # Verify that the file content was not changed
                    with open(file_path, 'r') as f:
                        content = f.read()
                        self.assertEqual(content, '["existing content"]')
    
    def test_display_tasks_with_source_and_due_date(self):
        """Test that display_tasks correctly shows source and due date."""
        # Create sample task dictionaries with source and due date
        from datetime import datetime
        
        task_dicts = [
            {
                'id': 'test-001',
                'title': 'Test Task 1',
                'description': 'Test Description 1',
                'status': 'pending',
                'priority': 3,
                'created_at': '2025-04-18T12:00:00',
                'updated_at': '2025-04-18T12:00:00',
                'source': 'human',
                'due_date': '2025-05-01T12:00:00',
                'dependencies': []
            },
            {
                'id': 'test-002',
                'title': 'Test Task 2',
                'description': 'Test Description 2',
                'status': 'completed',
                'priority': 5,
                'created_at': '2025-04-18T12:00:00',
                'updated_at': '2025-04-18T12:00:00',
                'source': 'AI Model',
                'due_date': None,
                'dependencies': []
            }
        ]
        
        # Mock the list_tasks method to return the sample dictionaries
        with patch.object(self.task_manager.task_api, 'list_tasks', return_value=task_dicts):
            # Mock the console.print method
            with patch('src.main.console.print') as mock_print:
                # Call display_tasks
                self.task_manager.display_tasks(task_dicts)
                
                # Assert that console.print was called (table was displayed)
                mock_print.assert_called()
                
                # We can't easily check the exact table content, but we can verify
                # that the method completed without errors

if __name__ == '__main__':
    unittest.main()
