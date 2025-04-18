"""
AI API implementation for Ollama integration.
"""

import os
import time
import subprocess
import requests
from typing import List, Dict, Any, Optional, Tuple, Generator, Iterator
import json
import ollama
from src.api.base import BaseAPI
from src.models.task import Task
from src.config.llm_config import LLMConfig

class OllamaConnectionError(Exception):
    """Exception raised for Ollama connection issues."""
    pass

class OllamaModelError(Exception):
    """Exception raised for model-related issues."""
    pass

class AIAPI(BaseAPI):
    """API for AI-powered task operations."""
    
    OLLAMA_API_URL = "http://localhost:11434"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __init__(self):
        super().__init__()
        self._config = LLMConfig()
        self._model_name = None
        self._client = None
        self._initialized = False
        self._conversation_history = []
    
    def initialize(self) -> None:
        """Initialize the AI API components with retry mechanism."""
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Test Ollama connection first
            if not self.test_connection():
                raise OllamaConnectionError(
                    f"Could not connect to Ollama service at {self.OLLAMA_API_URL} "
                    "after multiple attempts. Please ensure Ollama is running."
                )
            
            self._client = ollama.Client(host=self.OLLAMA_API_URL)
            
            # Get and validate models
            models = self.get_available_models()
            if not models:
                raise OllamaModelError("No models found. Please install at least one model using 'ollama pull <model_name>'")
            
            # Display models
            self._display_models(models)
            
            # Handle model selection
            saved_model = self._config.get_model_name()
            if saved_model and any(m['name'] == saved_model for m in models):
                print(f"\nUsing previously selected model: {saved_model}")
                model_name = saved_model
            else:
                print("\nSelect a model by entering its number:")
                choice = input(f"Enter a number (1-{len(models)}): ").strip()
                try:
                    num = int(choice)
                    if 1 <= num <= len(models):
                        model_name = models[num-1]['name']
                        self._config.set_model_name(model_name)
                    else:
                        print("\nInvalid selection. Using first available model.")
                        model_name = models[0]['name']
                        self._config.set_model_name(model_name)
                except ValueError:
                    print("\nInvalid input. Using first available model.")
                    model_name = models[0]['name']
                    self._config.set_model_name(model_name)
            
            # Verify selected model
            if not self._verify_model(model_name):
                raise OllamaModelError(f"Selected model '{model_name}' is not properly initialized")
            
            self._model_name = model_name
            self._initialized = True
            print(f"\nSuccessfully initialized with model: {self._model_name}\n")
            
        except Exception as e:
            self._initialized = False
            self._model_name = None
            print(f"\nAI initialization failed: {str(e)}")
            print("AI features will be disabled. You can still use other features.\n")
            raise
    
    def test_connection(self, max_retries: int = MAX_RETRIES) -> bool:
        """Test connection to Ollama service with retry mechanism."""
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"Retrying connection (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(self.RETRY_DELAY)
                
                response = requests.get(f"{self.OLLAMA_API_URL}/api/version")
                if response.status_code == 200:
                    return True
                
            except requests.RequestException as e:
                print(f"Connection attempt {attempt + 1} failed: {str(e)}")
        
        return False
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with error handling."""
        models = []
        errors = []
        
        # Try command line first
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                check=True
            )
            return self._parse_model_list(result.stdout)
        except subprocess.CalledProcessError as e:
            errors.append(f"Command line error: {str(e)}")
        except FileNotFoundError:
            errors.append("Ollama command not found")
        
        # Try API as fallback
        try:
            if self._client:
                result = self._client.list()
                if result and 'models' in result:
                    return [
                        {
                            'name': m.get('name', 'Unknown'),
                            'size': self._format_size(m.get('size', 0)),
                            'modified': m.get('modified', 'Unknown')
                        }
                        for m in result['models']
                    ]
        except Exception as e:
            errors.append(f"API error: {str(e)}")
        
        if not models:
            error_msg = "\n".join(errors)
            raise OllamaModelError(f"Failed to get model list:\n{error_msg}")
        
        return models
    
    def _parse_model_list(self, output: str) -> List[Dict[str, Any]]:
        """Parse model list from command output."""
        models = []
        lines = output.strip().split('\n')
        
        if len(lines) <= 1:  # No models or just header
            return models
        
        for line in lines[1:]:  # Skip header
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 4:
                # Handle size that might be split into value and unit
                size_value = parts[2]
                size_unit = parts[3] if len(parts) > 3 else ''
                size = f"{size_value}{size_unit}" if size_unit else size_value
                
                # Get modified date, skipping ID and size parts
                modified = ' '.join(parts[4:]) if len(parts) > 4 else 'Unknown'
                
                models.append({
                    'name': parts[0],
                    'size': size,
                    'modified': modified
                })
        
        return models
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"
    
    def _display_models(self, models: List[Dict[str, Any]]) -> None:
        """Display available models with numbers."""
        print("\nAvailable Models:")
        print("-" * 80)
        print(f"{'#':<4}{'Name':<40}{'Size':<12}{'Modified':<24}")
        print("-" * 80)
        
        for i, model in enumerate(models, 1):
            name = model['name']
            size = model['size']
            modified = model['modified']
            print(f"{i:<4}{name:<40}{size:<12}{modified:<24}")
        print("-" * 80)
    
    def _verify_model(self, model_name: str) -> bool:
        """Verify if the model is properly initialized with multiple fallback methods."""
        print(f"\nVerifying model '{model_name}'...")
        
        # Method 1: Try direct API call first (most reliable)
        try:
            print(f"Attempting to verify model using direct API call...")
            import requests
            url = f"{self.OLLAMA_API_URL}/api/generate"
            payload = {
                "model": model_name,
                "prompt": "Test.",
                "stream": False
            }
            response = requests.post(url, json=payload, timeout=10)  # Add timeout
            
            if response.status_code == 200:
                print("Model verified successfully using direct API call")
                return True
            else:
                print(f"Direct API verification failed: status code {response.status_code}")
        except Exception as e:
            print(f"Direct API verification failed: {str(e)}")
        
        # Method 2: Try a simple model info check
        try:
            print(f"Attempting to verify model using model info check...")
            url = f"{self.OLLAMA_API_URL}/api/show"
            payload = {"name": model_name}
            response = requests.post(url, json=payload, timeout=10)  # Add timeout
            
            if response.status_code == 200:
                data = response.json()
                if 'modelfile' in data:
                    print("Model verified successfully using model info check")
                    return True
                else:
                    print(f"Model info check failed: invalid response structure")
            else:
                print(f"Model info check failed: status code {response.status_code}")
        except Exception as e:
            print(f"Model info check failed: {str(e)}")
        
        # Method 3: Try using the Python client's chat method
        try:
            print(f"Attempting to verify model using chat method...")
            response = self._client.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': 'Test.'}],
                stream=False
            )
            
            if isinstance(response, dict) and 'message' in response:
                if isinstance(response['message'], dict) and 'content' in response['message']:
                    print("Model verified successfully using chat method")
                    return True
                else:
                    print(f"Chat method verification failed: invalid message structure")
            else:
                print(f"Chat method verification failed: invalid response structure")
        except Exception as e:
            print(f"Chat method verification failed: {str(e)}")
        
        # Method 4: Try using the Python client's generate method
        try:
            print(f"Attempting to verify model using generate method...")
            response = self._client.generate(
                model=model_name,
                prompt="Test.",
                stream=False
            )
            
            if isinstance(response, dict) and 'response' in response:
                print("Model verified successfully using generate method")
                return True
            else:
                print(f"Generate method verification failed: invalid response structure")
        except Exception as e:
            print(f"Generate method verification failed: {str(e)}")
        
        print(f"All verification methods failed for model '{model_name}'")
        return False
    
    def validate(self) -> bool:
        """Validate the AI API configuration."""
        return all([
            self._client is not None,
            self._model_name is not None,
            self._initialized
        ])
    
    def verify_model(self) -> bool:
        """Verify if the specified model is available and working."""
        if not self._model_name:
            return False
            
        try:
            # Try direct API first (most reliable method)
            try:
                print(f"\nVerifying model '{self._model_name}'...")
                # Try direct API call to check model
                url = f"{self.OLLAMA_API_URL}/api/show"
                payload = {"name": self._model_name}
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'modelfile' in data:
                        print(f"Model '{self._model_name}' verified via direct API")
                        # If model exists, verify it works
                        return self._verify_model(self._model_name)
                    else:
                        print(f"Model info check failed: invalid response structure")
                else:
                    print(f"Model info check failed: status code {response.status_code}")
            except Exception as e:
                print(f"Error checking model via direct API: {str(e)}")
            
            # Fallback to client list check
            try:
                models = self._client.list()
                
                # Safely check if model exists in the list
                model_exists = False
                if isinstance(models, dict) and 'models' in models:
                    model_exists = any(
                        isinstance(model, dict) and 'name' in model and model['name'] == self._model_name 
                        for model in models.get('models', [])
                    )
                
                if model_exists:
                    print(f"Model '{self._model_name}' found in list")
                    return self._verify_model(self._model_name)
                else:
                    print(f"Model '{self._model_name}' not found in client list")
            except Exception as e:
                print(f"Error checking model list via client: {str(e)}")
            
            # Fallback to command line
            try:
                result = subprocess.run(
                    ['ollama', 'list'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                models = self._parse_model_list(result.stdout)
                model_exists = any(model['name'] == self._model_name for model in models)
                
                if model_exists:
                    print(f"Model '{self._model_name}' found via command line")
                    return self._verify_model(self._model_name)
                else:
                    print(f"Model '{self._model_name}' not found via command line")
            except Exception as e:
                print(f"Error checking model via command line: {str(e)}")
            
            # If we still couldn't verify the model exists, but we have a saved model name,
            # let's trust it and try to verify it works
            if self._config.get_model_name() == self._model_name:
                print(f"Using saved model '{self._model_name}' despite not finding it in list")
                return self._verify_model(self._model_name)
            
            print(f"Model verification failed: model '{self._model_name}' not found")
            return False
        except Exception as e:
            print(f"Model verification failed: {str(e)}")
            return False
    
    def _stream_chat_response(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Stream chat response from the model."""
        try:
            for chunk in self._client.chat(
                model=self._model_name,
                messages=messages,
                stream=True
            ):
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
        except Exception as e:
            yield f"\nError: {str(e)}"

    def generate_task_suggestions(self, context: str) -> Iterator[Dict[str, Any]]:
        """Generate task suggestions using AI with streaming response."""
        if not self.validate():
            raise OllamaConnectionError("AI API not properly initialized")

        prompt = {
            'role': 'system',
            'content': '''You are a task management assistant. Based on the context, suggest 3-5 tasks.
            Format each task as a JSON object with:
            - title: string (short, clear title)
            - description: string (detailed description)
            - priority: number (1-5, where 5 is highest)
            - estimated_time: string (e.g., "2 hours")
            Return only the JSON array of tasks, no other text.'''
        }

        user_message = {
            'role': 'user',
            'content': f"Context: {context}"
        }

        response_text = ""
        for chunk in self._stream_chat_response([prompt, user_message]):
            response_text += chunk
            yield {'status': 'streaming', 'chunk': chunk}

        try:
            tasks = json.loads(response_text)
            if isinstance(tasks, list):
                yield {'status': 'complete', 'tasks': tasks}
            else:
                yield {'status': 'error', 'message': 'Invalid response format'}
        except json.JSONDecodeError:
            yield {'status': 'error', 'message': 'Failed to parse response as JSON'}

    def optimize_task_schedule(self, tasks: List[Task]) -> Iterator[Dict[str, Any]]:
        """Optimize task schedule using AI with streaming response."""
        if not self.validate():
            raise OllamaConnectionError("AI API not properly initialized")

        tasks_json = [task.to_dict() for task in tasks]
        prompt = {
            'role': 'system',
            'content': '''You are a task scheduling assistant. Optimize the task schedule considering:
            - Task priorities
            - Dependencies
            - Estimated completion times
            Return the optimized schedule as a JSON array of task IDs with explanations.'''
        }

        user_message = {
            'role': 'user',
            'content': f"Tasks to optimize: {json.dumps(tasks_json, indent=2)}"
        }

        response_text = ""
        for chunk in self._stream_chat_response([prompt, user_message]):
            response_text += chunk
            yield {'status': 'streaming', 'chunk': chunk}

        try:
            schedule = json.loads(response_text)
            yield {'status': 'complete', 'schedule': schedule}
        except json.JSONDecodeError:
            yield {'status': 'error', 'message': 'Failed to parse response as JSON'}

    def analyze_task_patterns(self, tasks: List[Any]) -> Iterator[Dict[str, Any]]:
        """Analyze task completion patterns using AI with streaming response."""
        if not self.validate():
            raise OllamaConnectionError("AI API not properly initialized")

        # Handle both Task objects and dictionaries while preserving ALL tasks
        tasks_json = []
        for task in tasks:
            if isinstance(task, dict):
                # If it's already a dictionary, use it as is (preserving all fields)
                tasks_json.append(task)
            else:
                # If it's a Task object, call to_dict() on it
                tasks_json.append(task.to_dict())
        prompt = {
            'role': 'system',
            'content': '''You are a task analysis assistant. Analyze the COMPLETE task history and identify:
            - Most productive times
            - Common dependencies
            - Task completion trends
            - Areas for improvement
            - Patterns across ALL tasks
            Return the analysis as a JSON object with these categories.'''
        }

        user_message = {
            'role': 'user',
            'content': f"Complete task history to analyze (analyzing ALL {len(tasks_json)} tasks): {json.dumps(tasks_json, indent=2)}"
        }

        response_text = ""
        for chunk in self._stream_chat_response([prompt, user_message]):
            response_text += chunk
            yield {'status': 'streaming', 'chunk': chunk}

        try:
            analysis = json.loads(response_text)
            yield {'status': 'complete', 'analysis': analysis}
        except json.JSONDecodeError:
            yield {'status': 'error', 'message': 'Failed to parse response as JSON'}
