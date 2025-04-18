"""
Tests for AI model verification.
"""
import unittest
from unittest.mock import patch, MagicMock
from src.api.ai_api import AIAPI

class TestAIModelVerification(unittest.TestCase):
    """Test cases for AI model verification."""

    def setUp(self):
        """Set up test environment."""
        self.api = AIAPI()

    @patch('ollama.Client')
    def test_model_verification_name_error(self, mock_client):
        """Test handling of model verification with missing 'name' key."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Mock the chat method to return a response without expected structure
        mock_instance.chat.return_value = {'unexpected': 'structure'}
        
        # Create test instance
        test_api = AIAPI()
        test_api._client = mock_instance
        
        # Test verification with improper response structure
        self.assertFalse(test_api._verify_model('test:latest'))
        
        # Test verify_model method which uses _verify_model
        test_api._model_name = 'test:latest'
        
        # Mock the list method to return a response with models
        mock_instance.list.return_value = {
            'models': [
                {'name': 'test:latest', 'size': 1000000}
            ]
        }
        
        self.assertFalse(test_api.verify_model())
        
    @patch('ollama.Client')
    def test_model_verification_non_dict_response(self, mock_client):
        """Test handling of model verification when response is not a dictionary."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Mock the chat method to return a non-dictionary response
        # This simulates the actual error observed in the application
        mock_instance.chat.return_value = None
        
        # Create test instance
        test_api = AIAPI()
        test_api._client = mock_instance
        
        # Test verification with non-dictionary response
        self.assertFalse(test_api._verify_model('test:latest'))
        
        # Also test with other non-dictionary types
        mock_instance.chat.return_value = "string response"
        self.assertFalse(test_api._verify_model('test:latest'))
        
        mock_instance.chat.return_value = 123
        self.assertFalse(test_api._verify_model('test:latest'))
        
        mock_instance.chat.return_value = []
        self.assertFalse(test_api._verify_model('test:latest'))
    
    @patch('ollama.Client')
    @patch('requests.post')
    def test_model_verification_chat_fallback_to_generate(self, mock_post, mock_client):
        """Test fallback to generate when chat fails."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Mock the chat method to raise an exception
        mock_instance.chat.side_effect = Exception("Chat method failed")
        
        # Mock the generate method to return a valid response
        mock_instance.generate.return_value = {
            'response': 'Test response'
        }
        
        # Create test instance
        test_api = AIAPI()
        test_api._client = mock_instance
        
        # Test verification with chat failure but successful generate
        self.assertTrue(test_api._verify_model('test:latest'))
        
        # Verify both methods were called
        mock_instance.chat.assert_called_once()
        mock_instance.generate.assert_called_once()
        # Direct API calls should not be made if generate succeeds
        mock_post.assert_not_called()

    @patch('ollama.Client')
    def test_model_verification_missing_models_key(self, mock_client):
        """Test handling of model verification with missing 'models' key."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Mock the list method to return a response without 'models' key
        mock_instance.list.return_value = {'unexpected': 'structure'}
        
        # Create test instance
        test_api = AIAPI()
        test_api._client = mock_instance
        test_api._model_name = 'test:latest'
        
        # Test verify_model method with missing 'models' key
        self.assertFalse(test_api.verify_model())

    @patch('ollama.Client')
    @patch('requests.post')
    def test_model_verification_direct_api_fallback(self, mock_post, mock_client):
        """Test fallback to direct API calls when client methods fail."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Mock the chat and generate methods to fail
        mock_instance.chat.side_effect = Exception("Chat method failed")
        mock_instance.generate.side_effect = Exception("Generate method failed")
        
        # Mock the direct API call to succeed
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Create test instance
        test_api = AIAPI()
        test_api._client = mock_instance
        
        # Test verification with direct API fallback
        self.assertTrue(test_api._verify_model('test:latest'))
        
        # Verify all methods were called
        mock_instance.chat.assert_called_once()
        mock_instance.generate.assert_called_once()
        self.assertEqual(mock_post.call_count, 1)  # Only the first direct API call should be made
    
    @patch('ollama.Client')
    @patch('requests.post')
    def test_model_verification_model_info_fallback(self, mock_post, mock_client):
        """Test fallback to model info check when other methods fail."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Mock the chat and generate methods to fail
        mock_instance.chat.side_effect = Exception("Chat method failed")
        mock_instance.generate.side_effect = Exception("Generate method failed")
        
        # Mock the first direct API call to fail
        first_response = MagicMock()
        first_response.status_code = 500
        
        # Mock the model info check to succeed
        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = {'modelfile': 'FROM mistral:latest'}
        
        # Set up the mock to return different responses for different calls
        mock_post.side_effect = [first_response, second_response]
        
        # Create test instance
        test_api = AIAPI()
        test_api._client = mock_instance
        
        # Test verification with model info fallback
        self.assertTrue(test_api._verify_model('test:latest'))
        
        # Verify all methods were called
        mock_instance.chat.assert_called_once()
        mock_instance.generate.assert_called_once()
        self.assertEqual(mock_post.call_count, 2)  # Both direct API calls should be made
    
    @patch('ollama.Client')
    @patch('requests.post')
    def test_model_verification_all_methods_fail(self, mock_post, mock_client):
        """Test when all verification methods fail."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Mock all methods to fail
        mock_instance.chat.side_effect = Exception("Chat method failed")
        mock_instance.generate.side_effect = Exception("Generate method failed")
        
        # Mock direct API calls to fail
        first_response = MagicMock()
        first_response.status_code = 500
        second_response = MagicMock()
        second_response.status_code = 500
        
        mock_post.side_effect = [first_response, second_response]
        
        # Create test instance
        test_api = AIAPI()
        test_api._client = mock_instance
        
        # Test verification with all methods failing
        self.assertFalse(test_api._verify_model('test:latest'))
        
        # Verify all methods were called
        mock_instance.chat.assert_called_once()
        mock_instance.generate.assert_called_once()
        self.assertEqual(mock_post.call_count, 2)  # Both direct API calls should be made

    @patch('ollama.Client')
    def test_model_verification_successful(self, mock_client):
        """Test successful model verification."""
        # Setup mock client
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Mock the chat method to return a valid response
        mock_instance.chat.return_value = {
            'message': {
                'content': 'Test response'
            }
        }
        
        # Mock the list method to return a response with models
        mock_instance.list.return_value = {
            'models': [
                {'name': 'test:latest', 'size': 1000000}
            ]
        }
        
        # Create test instance
        test_api = AIAPI()
        test_api._client = mock_instance
        test_api._model_name = 'test:latest'
        
        # Test verify_model method with valid response
        self.assertTrue(test_api.verify_model())

if __name__ == '__main__':
    unittest.main()
