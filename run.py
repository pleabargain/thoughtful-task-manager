#!/usr/bin/env python3
"""
Main entry point for the Thoughtful Task Manager.
"""

import os
import sys
import subprocess
import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.status import Status

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.api.task_api import TaskAPI
from src.api.ai_api import AIAPI

console = Console()

def check_ollama_service():
    """Check if Ollama service is running and accessible."""
    try:
        response = requests.get("http://localhost:11434/api/version")
        if response.status_code == 200:
            console.print("[green]✓ Ollama service is running[/green]")
            return True
    except requests.RequestException:
        console.print("[red]✗ Ollama service is not running[/red]")
        console.print("[yellow]Please start Ollama with: ollama serve[/yellow]")
        return False
    return False

def check_ollama_models():
    """Check if any Ollama models are installed."""
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            check=True
        )
        if len(result.stdout.strip().split('\n')) > 1:  # More than just the header
            console.print("[green]✓ Ollama models are available[/green]")
            return True
        else:
            console.print("[red]✗ No Ollama models found[/red]")
            console.print("[yellow]Please install a model with: ollama pull <model_name>[/yellow]")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        console.print(f"[red]✗ Error checking Ollama models: {str(e)}[/red]")
        return False

def main():
    """Main entry point for the application."""
    console.print("[bold cyan]Thoughtful Task Manager[/bold cyan]")
    console.print("[bold]Checking system requirements...[/bold]")
    
    # Check Ollama service
    if not check_ollama_service():
        console.print("\n[yellow]AI features will be disabled. You can still use basic task management.[/yellow]")
        ai_enabled = False
    else:
        # Check Ollama models
        ai_enabled = check_ollama_models()
        if not ai_enabled:
            console.print("\n[yellow]AI features will be disabled. You can still use basic task management.[/yellow]")
    
    # Initialize task manager
    from src.main import TaskManager
    task_manager = TaskManager()
    
    # Run the application
    task_manager.run()

if __name__ == "__main__":
    main() 