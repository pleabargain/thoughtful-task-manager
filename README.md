# Thoughtful Task Manager

A Python-based task management system that uses local AI (Ollama) to generate and manage tasks.

## Features (Planned)
- Local text file-based task storage
- AI-powered task suggestions using Ollama
- Daily to-do list generation
- Task dependency management
- Progress tracking and updates

## Requirements
- Python 3.8+
- Ollama with Gemma3 model
- Git

## Setup
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Verify Ollama installation and Gemma3 model

## Project Structure
```
thoughtful_task_manager/
├── src/
│   ├── __init__.py
│   ├── models/
│   ├── utils/
│   └── main.py
├── tests/
├── data/
├── requirements.txt
└── README.md
```

## Progress
- [x] Project structure created
- [ ] Basic file operations
- [ ] Task management system
- [ ] AI integration
- [ ] User interface 