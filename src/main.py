#!/usr/bin/env python3
"""
Main entry point for the Thoughtful Task Manager.
"""

import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from .api import TaskAPI, AIAPI

console = Console()

PRIORITY_DESCRIPTIONS = {
    1: "[green]Low[/green] - Can be done when convenient",
    2: "[blue]Medium-Low[/blue] - Should be done soon",
    3: "[yellow]Medium[/yellow] - Important but not urgent",
    4: "[orange]Medium-High[/orange] - Important and time-sensitive",
    5: "[red]High[/red] - Critical and urgent"
}

class TaskManager:
    """Main application class."""
    
    def __init__(self):
        self.task_api = TaskAPI()
        self.ai_api = None
        self.ai_enabled = False
    
    def show_priority_guide(self):
        """Display the priority level guide."""
        console.print("\n[bold]Priority Levels Guide:[/bold]")
        for level, description in PRIORITY_DESCRIPTIONS.items():
            console.print(f"{level}: {description}")
    
    def display_tasks(self, tasks):
        """Display tasks in a formatted table."""
        if not tasks:
            console.print("[yellow]No tasks found.[/yellow]")
            return

        table = Table(show_header=True)
        table.add_column("Title", style="cyan")
        table.add_column("Description")
        table.add_column("Priority", justify="center")
        table.add_column("Status", justify="center")

        for task in tasks:
            priority_style = {
                1: "green",
                2: "blue",
                3: "yellow",
                4: "red",
                5: "red bold"
            }.get(task.priority, "white")
            
            table.add_row(
                task.title,
                task.description,
                f"[{priority_style}]{task.priority}[/{priority_style}]",
                task.status
            )
        
        console.print(table)
    
    def initialize(self):
        """Initialize the application."""
        console.print("[bold green]Initializing Thoughtful Task Manager...[/bold green]")
        
        # Initialize Task API
        self.task_api.initialize()
        
        # Try to initialize AI API
        try:
            self.ai_api = AIAPI()
            self.ai_api.initialize()
            if self.ai_api.verify_model():
                self.ai_enabled = True
                console.print("[green]AI features enabled successfully![/green]")
            else:
                console.print("[yellow]AI model not found. AI features will be disabled.[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Failed to initialize AI features: {str(e)}[/yellow]")
            console.print("[yellow]AI features will be disabled.[/yellow]")
    
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
                console.print("5. Show Priority Guide")
                if self.ai_enabled:
                    console.print("6. Get AI Suggestions")
                    console.print("7. Analyze Patterns")
                console.print("8. Exit")
                
                choices = ["1", "2", "3", "4", "5", "8"]
                if self.ai_enabled:
                    choices.extend(["6", "7"])
                
                choice = Prompt.ask("Select an option", choices=choices)
                
                if choice == "1":
                    tasks = self.task_api.list_tasks()
                    self.display_tasks(tasks)
                
                elif choice == "2":
                    self.show_priority_guide()
                    title = Prompt.ask("\nTask title")
                    description = Prompt.ask("Task description")
                    console.print("\nPriority Levels:")
                    for level, desc in PRIORITY_DESCRIPTIONS.items():
                        console.print(f"{level}: {desc}")
                    priority = int(Prompt.ask("\nPriority", choices=["1", "2", "3", "4", "5"]))
                    task = self.task_api.create_task(title, description, priority=priority)
                    console.print(f"[green]Created task: {task.title}[/green]")
                
                elif choice == "3":
                    title = Prompt.ask("Task title to update")
                    task = self.task_api.get_task(title)
                    if task:
                        update_type = Prompt.ask(
                            "What to update",
                            choices=["status", "priority", "description"]
                        )
                        if update_type == "status":
                            new_value = Prompt.ask("New status", choices=["pending", "in_progress", "completed"])
                        elif update_type == "priority":
                            self.show_priority_guide()
                            new_value = int(Prompt.ask("\nNew priority", choices=["1", "2", "3", "4", "5"]))
                        else:
                            new_value = Prompt.ask("New description")
                        
                        self.task_api.update_task(title, **{update_type: new_value})
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
                    self.show_priority_guide()
                
                elif choice == "6" and self.ai_enabled:
                    context = Prompt.ask("Describe your current situation")
                    suggestions = self.ai_api.generate_task_suggestions(context)
                    console.print("\n[bold]Suggested Tasks:[/bold]")
                    for suggestion in suggestions:
                        console.print(f"- {suggestion['title']}: {suggestion['description']}")
                
                elif choice == "7" and self.ai_enabled:
                    tasks = self.task_api.list_tasks()
                    patterns = self.ai_api.analyze_task_patterns(tasks)
                    console.print("\n[bold]Task Analysis:[/bold]")
                    for key, value in patterns.items():
                        console.print(f"{key}: {value}")
                
                elif choice == "8":
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