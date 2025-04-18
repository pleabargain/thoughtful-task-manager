# Thoughtful Task Manager

A smart task management system with AI-powered features using Ollama.

## Features
- Task management with priority levels
- AI-powered task suggestions
- Smart scheduling optimization
- Task pattern analysis
- Color-coded interface
- Progress tracking
- JSON schema validation
- UUID-based task identification
- Model and source tracking for tasks
- Create and manage multiple task files
- Task dependency management

## Requirements
- Python 3.8 or higher
- Ollama installed and running
- 8GB RAM minimum
- Available port 11434

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/thoughtful-task-manager.git
cd thoughtful-task-manager
```

2. Install production dependencies:
```bash
pip install -r requirements.txt
```

3. Install test dependencies (for development):
```bash
pip install -r requirements-test.txt
```

4. Install and start Ollama:
- Download from https://ollama.ai
- Start the Ollama service
- Pull at least one model: `ollama pull llama3.2:latest`

## Development Setup

1. Set up test environment:
```bash
# Create test package
touch tests/__init__.py

# Configure pytest
cp conftest.py.example conftest.py
```

2. Run tests:
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_ollama_connection.py -v

# Run with coverage
python -m pytest --cov=src tests/
```

## Project Structure
```
thoughtful-task-manager/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── ai_api.py
│   │   ├── task_api.py
│   │   └── base.py
│   ├── models/
│   │   └── task.py
│   ├── utils/
│   │   └── file_handler.py
│   └── config/
│       └── llm_config.py
├── data/
│   ├── tasks.json
│   ├── task_schema.json
│   └── sample_tasks.json
├── tests/
│   ├── __init__.py
│   ├── test_ollama_connection.py
│   ├── test_task_model.py
│   └── test_file_handler.py
├── conftest.py
├── requirements.txt
├── requirements-test.txt
├── README.md
├── DEVELOPMENT_RULES.md
└── PROJECT_STATUS.md
```

## Testing Guidelines
1. Always run tests before committing:
```bash
python -m pytest
```

2. Check test coverage:
```bash
python -m pytest --cov=src tests/
```

3. Test external service integration:
```bash
python -m pytest tests/test_ollama_connection.py -v
```

## Current Test Coverage

The project currently has improved test coverage, with key components having excellent coverage:

| Component | Coverage |
|-----------|----------|
| Task model | 96% |
| FileHandler | 81% |
| TaskAPI | 91% |
| AI API | 29% |
| Main application | 0% |

### Recent Improvements

1. **Task Model and API**: Fixed issues with task ID handling, priority validation, and JSON structure handling
2. **AI Model Verification**: Implemented robust error handling and fallback mechanisms for AI model verification
3. **Task Display Fix**: Fixed bug in TaskManager's display_tasks method to properly handle dictionary tasks, preventing "'dict' object has no attribute 'priority'" errors
4. **Duplicate Title Prevention**: Implemented automatic title uniqueness to prevent duplicate task titles, with user notifications when titles are modified
5. **JSON Schema Implementation**: Added JSON schema validation for tasks with UUID, model, and source tracking
6. **UI Improvements**: Added ability to create new task files directly from the UI and fixed menu option ordering for better usability
7. **Task Dependency Management**: Added comprehensive dependency management with the ability to create, view, and update task dependencies
8. **Title Validation**: Added validation to ensure task titles are not purely numeric and are at least 5 characters long
9. **Enhanced Task Display**: Added source and due date information to the task list view for better task tracking

## Data Schema

The application uses a JSON schema for task validation:

### Task Schema

Tasks are validated against a JSON schema that defines:

- Required fields: id, uuid, title, description, dependencies, status, priority, created_date, model, source
- Field types and constraints (e.g., priority must be 1-5)
- Format validation (e.g., dates must be in ISO format)

### UUID-based Identification

Each task has a UUID (Universally Unique Identifier) that:

- Provides a globally unique identifier for each task
- Is automatically generated when a task is created
- Ensures reliable task identification even across different systems

### Model and Source Tracking

Tasks include metadata about their origin:

- `model`: Tracks which AI model was used to create or modify the task
- `source`: Indicates whether the task was created by a human or an AI model

This enables better tracking of task provenance and helps analyze the effectiveness of AI-generated tasks.

To view detailed coverage information, run:
```bash
python -m pytest --cov=src --cov-report=html tests/
```
Then open `htmlcov/index.html` in your browser.

## Common Issues and Solutions

### Test Import Issues
- Ensure `__init__.py` exists in test directory
- Check `conftest.py` configuration
- Verify Python path in test environment

### Ollama Connection Issues
- Verify Ollama service is running
- Check port 11434 is available
- Ensure model is downloaded
- Check network connectivity

### Test Failures
- Mock external services
- Handle user input in tests
- Use proper test isolation
- Check test dependencies

## Contributing
1. Read `DEVELOPMENT_RULES.md`
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

## License
MIT License

## Contact
Your Name - your.email@example.com
