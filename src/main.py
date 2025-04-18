#!/usr/bin/env python3
"""
Main entry point for the Thoughtful Task Manager.
"""

import sys
from rich.console import Console
from rich.prompt import Prompt

from .api import TaskAPI, AIAPI

console = Console()

class TaskManager:
    """Main application class."""
    
    def __init__(self):
        self.task_api = TaskAPI()
        self.ai_api = AIAPI()
    
    def initialize(self):
        """Initialize the application."""
        console.print("[bold green]Initializing Thoughtful Task Manager...[/bold green]")
        
        # Initialize APIs
        self.task_api.initialize()
        self.ai_api.initialize()
        
        # Verify AI model
        if not self.ai_api.verify_model():
            console.print("[red]Error: Required AI model not found. Please ensure Ollama is running with the Gemma3 model.[/red]")
            sys.exit(1)
    
    def run(self):
        """Run the application."""
        try:
            self.initialize()
            
            while True:
                console.print("\n[bold cyan]Thoughtful Task Manager[/bold cyan]")
                console.print("1. View Tasks")
                console.print("2. Add Task")
                console.print("3. Update Task")
                console.print("4. Delete Task")
                console.print("5. Get AI Suggestions")
                console.print("6. Analyze Patterns")
                console.print("7. Exit")
                
                choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7"])
                
                if choice == "1":
                    tasks = self.task_api.list_tasks()
                    for task in tasks:
                        console.print(f"[bold]{task.title}[/bold]: {task.description}")
                
                elif choice == "2":
                    title = Prompt.ask("Task title")
                    description = Prompt.ask("Task description")
                    task = self.task_api.create_task(title, description)
                    console.print(f"[green]Created task: {task.title}[/green]")
                
                elif choice == "3":
                    title = Prompt.ask("Task title to update")
                    task = self.task_api.get_task(title)
                    if task:
                        new_status = Prompt.ask("New status", choices=["pending", "in_progress", "completed"])
                        self.task_api.update_task(title, status=new_status)
                        console.print(f"[green]Updated task: {title}[/green]")
                    else:
                        console.print(f"[red]Task not found: {title}[/red]")
                
                elif choice == "4":
                    title = Prompt.ask("Task title to delete")
                    if self.task_api.delete_task(title):
                        console.print(f"[green]Deleted task: {title}[/green]")
                    else:
                        console.print(f"[red]Task not found: {title}[/red]")
                
                elif choice == "5":
                    context = Prompt.ask("Describe your current situation")
                    suggestions = self.ai_api.generate_task_suggestions(context)
                    console.print("\n[bold]Suggested Tasks:[/bold]")
                    for suggestion in suggestions:
                        console.print(f"- {suggestion['title']}: {suggestion['description']}")
                
                elif choice == "6":
                    tasks = self.task_api.list_tasks()
                    patterns = self.ai_api.analyze_task_patterns(tasks)
                    console.print("\n[bold]Task Analysis:[/bold]")
                    for key, value in patterns.items():
                        console.print(f"{key}: {value}")
                
                elif choice == "7":
                    console.print("[yellow]Goodbye![/yellow]")
                    break
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[red]An error occurred: {str(e)}[/red]")
            sys.exit(1)

def main():
    """Main entry point for the application."""
    task_manager = TaskManager()
    task_manager.run()

if __name__ == "__main__":
    main() 