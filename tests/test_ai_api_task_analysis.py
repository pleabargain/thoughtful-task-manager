"""
Tests for the AI API task analysis functionality.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from src.api.ai_api import AIAPI
from src.models.task import Task

class TestAIAPITaskAnalysis:
    """Tests for the AI API task analysis functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ai_api = AIAPI()
        self.ai_api._initialized = True
        self.ai_api._model_name = "test_model"
        self.ai_api._client = MagicMock()
    
    def test_analyze_task_patterns_with_task_objects(self):
        """Test that analyze_task_patterns correctly handles Task objects."""
        # Create sample Task objects
        tasks = [
            Task(
                title="Test Task 1",
                description="Test Description 1",
                id="test-001",
                status="pending",
                priority=3
            ),
            Task(
                title="Test Task 2",
                description="Test Description 2",
                id="test-002",
                status="completed",
                priority=5
            )
        ]
        
        # Mock the _stream_chat_response method to return a valid JSON response
        self.ai_api._stream_chat_response = MagicMock(return_value=iter(['{"category1": "analysis1"}']))
        
        # Call analyze_task_patterns with Task objects
        result = list(self.ai_api.analyze_task_patterns(tasks))
        
        # Assert that the method completed without errors
        assert len(result) > 0
        assert 'status' in result[-1]
        assert result[-1]['status'] == 'complete'
    
    def test_analyze_task_patterns_with_dict_tasks(self):
        """Test that analyze_task_patterns correctly handles dictionary tasks."""
        # Create MULTIPLE sample task dictionaries to ensure all are processed
        task_dicts = [
            {
                'id': 'test-001',
                'title': 'Test Task 1',
                'description': 'Test Description 1',
                'status': 'pending',
                'priority': 3,
                'created_at': '2025-04-18T12:00:00'
            },
            {
                'id': 'test-002',
                'title': 'Test Task 2',
                'description': 'Test Description 2',
                'status': 'completed',
                'priority': 5,
                'created_at': '2025-04-17T10:00:00'
            },
            {
                'id': 'test-003',
                'title': 'Test Task 3',
                'description': 'Test Description 3',
                'status': 'in_progress',
                'priority': 4,
                'created_at': '2025-04-16T09:00:00'
            }
        ]
        
        # Capture what's actually sent to the LLM
        sent_to_llm = []
        
        def mock_stream_response(messages):
            # Capture the content sent to the LLM
            sent_to_llm.append(messages[1]['content'])
            return iter(['{"category1": "analysis1"}'])
        
        self.ai_api._stream_chat_response = mock_stream_response
        
        # Call analyze_task_patterns with dictionary tasks
        result = list(self.ai_api.analyze_task_patterns(task_dicts))
        
        # Assert that the method completed without errors
        assert len(result) > 0
        assert 'status' in result[-1]
        assert result[-1]['status'] == 'complete'
        
        # Verify ALL tasks were included in the message to the LLM
        assert len(sent_to_llm) > 0
        for task_dict in task_dicts:
            assert task_dict['id'] in sent_to_llm[0]
            assert task_dict['title'] in sent_to_llm[0]
        
        # Verify the task count is mentioned in the message
        assert f"analyzing ALL {len(task_dicts)} tasks" in sent_to_llm[0]
    
    def test_analyze_task_patterns_with_mixed_types(self):
        """Test that analyze_task_patterns correctly handles a mix of Task objects and dictionaries."""
        # Create a mix of Task objects and dictionaries
        tasks = [
            Task(
                title="Test Task 1",
                description="Test Description 1",
                id="test-001",
                status="pending",
                priority=3
            ),
            {
                'id': 'test-002',
                'title': 'Test Task 2',
                'description': 'Test Description 2',
                'status': 'completed',
                'priority': 5,
                'created_at': '2025-04-17T10:00:00'
            }
        ]
        
        # Capture what's actually sent to the LLM
        sent_to_llm = []
        
        def mock_stream_response(messages):
            # Capture the content sent to the LLM
            sent_to_llm.append(messages[1]['content'])
            return iter(['{"category1": "analysis1"}'])
        
        self.ai_api._stream_chat_response = mock_stream_response
        
        # Call analyze_task_patterns with mixed types
        result = list(self.ai_api.analyze_task_patterns(tasks))
        
        # Assert that the method completed without errors
        assert len(result) > 0
        assert 'status' in result[-1]
        assert result[-1]['status'] == 'complete'
        
        # Verify ALL tasks were included in the message to the LLM
        assert len(sent_to_llm) > 0
        assert "test-001" in sent_to_llm[0]
        assert "Test Task 1" in sent_to_llm[0]
        assert "test-002" in sent_to_llm[0]
        assert "Test Task 2" in sent_to_llm[0]
        
        # Verify the task count is mentioned in the message
        assert f"analyzing ALL {len(tasks)} tasks" in sent_to_llm[0]
