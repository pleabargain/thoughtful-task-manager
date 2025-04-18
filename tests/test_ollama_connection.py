"""
Tests for Ollama API connection and model management.
"""
import unittest
import subprocess
from unittest.mock import patch, MagicMock
import requests
from src.api.ai_api import AIAPI, OllamaModelError

class TestOllamaConnection(unittest.TestCase):
    """Test cases for Ollama connection and model management."""

    def setUp(self):
        """Set up test environment."""
        self.api = AIAPI()

    def test_ollama_service_running(self):
        """Test if Ollama service is running and accessible."""
        try:
            response = requests.get("http://localhost:11434/api/version")
            self.assertEqual(response.status_code, 200)
            print("✓ Ollama service is running")
        except requests.RequestException:
            self.fail("Ollama service is not running on http://localhost:11434")

    def test_model_list_command(self):
        """Test if ollama list command works."""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                 capture_output=True, 
                                 text=True, 
                                 check=True)
            self.assertIn("NAME", result.stdout)
            print("✓ Ollama list command works")
        except subprocess.CalledProcessError:
            self.fail("ollama list command failed")
        except FileNotFoundError:
            self.fail("ollama command not found")

    @patch('builtins.input', return_value='1')
    @patch('src.api.ai_api.AIAPI.test_connection')
    @patch('src.api.ai_api.AIAPI.get_available_models')
    @patch('src.api.ai_api.AIAPI._verify_model')
    @patch('ollama.Client')
    def test_client_initialization(self, mock_client, mock_verify, mock_models, mock_connection, mock_input):
        """Test Ollama client initialization with mocked client."""
        # Setup mocks
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_connection.return_value = True
        mock_verify.return_value = True
        mock_models.return_value = [
            {'name': 'test:latest', 'size': '1.0GB', 'modified': 'now'}
        ]
        
        # Test successful initialization
        self.api._config.get_model_name = MagicMock(return_value=None)  # Force model selection
        self.api.initialize()
        
        # Verify all mocks were called correctly
        mock_client.assert_called_once_with(host="http://localhost:11434")
        mock_verify.assert_called_once()
        mock_models.assert_called_once()
        mock_input.assert_called_once_with("Enter a number (1-1): ")
        
        # Verify model was selected and saved
        self.assertEqual(self.api._model_name, 'test:latest')
        self.assertTrue(self.api._initialized)

    @patch('requests.get')
    def test_connection_retry(self, mock_get):
        """Test connection retry mechanism."""
        # Simulate connection failures then success
        mock_get.side_effect = [
            requests.exceptions.ConnectionError(),
            requests.exceptions.ConnectionError(),
            MagicMock(status_code=200)
        ]
        
        connected = self.api.test_connection(max_retries=3)
        self.assertTrue(connected)
        self.assertEqual(mock_get.call_count, 3)

    def test_model_name_parsing(self):
        """Test model name parsing from ollama list output."""
        sample_output = '''
NAME                    ID              SIZE   MODIFIED
llama3.2:latest        a80c4f17acd5    2.0    GB     38 hours ago
gemma3:latest          a2af6cc3eb7f    3.3    GB     2 weeks ago
'''
        models = self.api._parse_model_list(sample_output)
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]['name'], 'llama3.2:latest')
        self.assertEqual(models[0]['size'], '2.0GB')
        self.assertEqual(models[1]['size'], '3.3GB')
        self.assertEqual(models[1]['modified'], '2 weeks ago')

    def test_model_verification_failure(self):
        """Test handling of model verification failure."""
        # Create a test instance with a mock client
        test_api = AIAPI()
        test_api._client = MagicMock()
        test_api._client.generate.side_effect = Exception("Model error")
        
        # Test that verification fails and raises error
        self.assertFalse(test_api._verify_model('test:latest'))
    
    @patch('requests.post')
    def test_direct_api_verification(self, mock_post):
        """Test that direct API verification works correctly."""
        # Setup mock response for direct API call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Create test instance
        test_api = AIAPI()
        
        # Test verification with direct API
        self.assertTrue(test_api._verify_model('test:latest'))
        
        # Verify direct API was called with correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['model'], 'test:latest')
        self.assertEqual(kwargs['json']['prompt'], 'Test.')
        self.assertEqual(kwargs['json']['stream'], False)
        self.assertEqual(kwargs['timeout'], 10)
    
    @patch('requests.post')
    @patch('ollama.Client')
    def test_verify_model_prioritizes_direct_api(self, mock_client, mock_post):
        """Test that verify_model prioritizes direct API calls."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Setup mock response for direct API call
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = {'modelfile': 'FROM mistral:latest'}
        
        second_response = MagicMock()
        second_response.status_code = 200
        
        # Set up the mock to return different responses for different calls
        mock_post.side_effect = [first_response, second_response]
        
        # Create test instance
        test_api = AIAPI()
        test_api._client = mock_instance
        test_api._model_name = 'test:latest'
        
        # Test verify_model method
        self.assertTrue(test_api.verify_model())
        
        # Verify direct API was called first and client methods were not called
        self.assertEqual(mock_post.call_count, 2)  # First for model check, second for verification
        mock_instance.list.assert_not_called()  # Client list should not be called
        mock_instance.chat.assert_not_called()  # Client chat should not be called
        mock_instance.generate.assert_not_called()  # Client generate should not be called

if __name__ == '__main__':
    unittest.main()
