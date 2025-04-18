# Thoughtful Task Manager

A Python-based task management system that uses local AI (Ollama) to generate and manage tasks intelligently.

## Features
- Local text file-based task storage
- Priority-based task management (5 levels)
- Rich CLI interface with color coding
- Task dependency management
- Progress tracking and updates
- AI-powered task suggestions (optional)
- Daily to-do list generation

## Priority System
Tasks are managed using a 5-level priority system:
1. 🟢 **Low** - Can be done when convenient
2. 🔵 **Medium-Low** - Should be done soon
3. 🟡 **Medium** - Important but not urgent
4. 🟠 **Medium-High** - Important and time-sensitive
5. 🔴 **High** - Critical and urgent

## Requirements
- Python 3.8+
- Ollama with Gemma3 model (optional for AI features)
- Git

## Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python run.py
   ```

## Usage
The application provides a rich CLI interface with the following options:
1. View Tasks - Display all tasks in a formatted table
2. Add Task - Create a new task with title, description, and priority
3. Update Task - Modify task status, priority, or description
4. Delete Task - Remove a task
5. Show Priority Guide - Display priority level descriptions
6. Get AI Suggestions (requires Ollama)
7. Analyze Patterns (requires Ollama)
8. Exit

### Task Management
- Tasks are displayed in a color-coded table based on priority
- Each task includes:
  - Title
  - Description
  - Priority level (1-5)
  - Current status (pending/in_progress/completed)

### AI Features (Optional)
If Ollama is installed and configured:
- Get AI-generated task suggestions based on your current context
- Analyze task patterns and completion trends
- Optimize task scheduling

## Project Structure
```
thoughtful_task_manager/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── task_api.py
│   │   └── ai_api.py
│   ├── models/
│   │   └── task.py
│   ├── utils/
│   │   └── file_handler.py
│   └── main.py
├── tests/
├── data/
├── requirements.txt
└── README.md
```

## Development Status
See [PROJECT_STATUS.md](PROJECT_STATUS.md) for current development status and roadmap.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details. 