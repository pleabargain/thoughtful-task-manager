#!/usr/bin/env python3
"""
Main entry point for the Thoughtful Task Manager.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.status import Status

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
    
    def __init__(self, data_file=None):
        self.task_api = TaskAPI(data_file=data_file)
        self.ai_api = None
        self.ai_enabled = False
        self.default_data_dir = "data"
        self.current_file = data_file or "data/tasks.json"
    
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
        table.add_column("Due Date", justify="center")  # New column
        table.add_column("Source", justify="center")    # New column
        table.add_column("Dependencies", justify="center")

        # Create a dictionary of task IDs to titles for dependency lookup
        task_titles = {}
        for t in tasks:
            if isinstance(t, dict):
                task_titles[t['id']] = t['title']
            else:
                task_titles[t.id] = t.title

        for task in tasks:
            # Handle both Task objects and dictionaries
            if isinstance(task, dict):
                priority = task['priority']
                title = task['title']
                description = task['description']
                status = task['status']
                dependencies = task.get('dependencies', [])
                source = task.get('source', 'human')
                due_date = task.get('due_date', None)
            else:
                priority = task.priority
                title = task.title
                description = task.description
                status = task.status
                dependencies = task.dependencies if task.dependencies else []
                source = task.source
                due_date = task.due_date
                
            priority_style = {
                1: "green",
                2: "blue",
                3: "yellow",
                4: "red",
                5: "red bold"
            }.get(priority, "white")
            
            # Format due date
            due_date_display = ""
            if due_date:
                if isinstance(due_date, str):
                    try:
                        due_date = datetime.fromisoformat(due_date)
                        due_date_display = due_date.strftime("%Y-%m-%d")
                    except ValueError:
                        due_date_display = due_date
                else:
                    due_date_display = due_date.strftime("%Y-%m-%d")
            
            # Format source with color
            source_display = f"[green]{source}[/green]" if source == "human" else f"[blue]{source}[/blue]"
            
            # Format dependencies
            dep_display = ""
            if dependencies:
                dep_titles = []
                for dep_id in dependencies:
                    if dep_id in task_titles:
                        dep_titles.append(task_titles[dep_id])
                    else:
                        dep_titles.append(f"Unknown ({dep_id})")
                
                if len(dep_titles) <= 2:
                    dep_display = ", ".join(dep_titles)
                else:
                    dep_display = f"{len(dep_titles)} deps"
            
            table.add_row(
                title,
                description,
                f"[{priority_style}]{priority}[/{priority_style}]",
                status,
                due_date_display,
                source_display,
                dep_display
            )
        
        console.print(table)
    
    # Methods that delegate to task_api for testing
    def list_tasks(self):
        """Get all tasks."""
        return self.task_api.list_tasks()
    
    def add_task(self, task_data):
        """Add a new task."""
        if isinstance(task_data, dict):
            return self.task_api.create_task(
                title=task_data.get('title', ''),
                description=task_data.get('description', ''),
                priority=task_data.get('priority', 3),
                status=task_data.get('status', 'pending'),
                id=task_data.get('id')
            )
        return self.task_api.create_task(task_data)
    
    def update_task(self, task_id, update_data):
        """Update a task."""
        return self.task_api.update_task(task_id, **update_data)
    
    def delete_task(self, task_id):
        """Delete a task."""
        return self.task_api.delete_task(task_id)
    
    def get_task(self, task_id):
        """Get a task by ID."""
        return self.task_api.get_task(task_id)
    
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
    
    def handle_ai_suggestions(self):
        """Handle AI task suggestions with streaming output."""
        context = Prompt.ask("\nDescribe your current situation")
        
        with Status("[bold blue]Generating task suggestions...", spinner="dots") as status:
            try:
                current_suggestion = ""
                for result in self.ai_api.generate_task_suggestions(context):
                    if result['status'] == 'streaming':
                        current_suggestion += result['chunk']
                        status.update(f"[bold blue]Generating suggestions...\n\n{current_suggestion}")
                    elif result['status'] == 'complete':
                        console.print("\n[bold green]Generated Suggestions:[/bold green]")
                        for task in result['tasks']:
                            console.print(Panel(
                                f"[cyan]Title:[/cyan] {task['title']}\n"
                                f"[yellow]Priority:[/yellow] {task['priority']}\n"
                                f"[green]Est. Time:[/green] {task['estimated_time']}\n"
                                f"[white]{task['description']}[/white]"
                            ))
                    else:
                        console.print(f"\n[red]Error: {result.get('message', 'Unknown error')}[/red]")
            except Exception as e:
                console.print(f"\n[red]Failed to generate suggestions: {str(e)}[/red]")
    
    def handle_task_analysis(self):
        """Handle task pattern analysis with streaming output."""
        tasks = self.task_api.list_tasks()
        if not tasks:
            console.print("[yellow]No tasks available for analysis.[/yellow]")
            return
        
        # Create the output directory if it doesn't exist
        output_dir = "output"
        Path(output_dir).mkdir(exist_ok=True)
        
        # Get the base name of the current tasks file without extension
        base_name = os.path.basename(self.current_file)
        file_name = os.path.splitext(base_name)[0]
        
        # Create the output file name with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"analysis-{file_name}-{timestamp}.json"
        output_path = os.path.join(output_dir, output_file)
        
        with Status("[bold blue]Analyzing task patterns...", spinner="dots") as status:
            try:
                current_analysis = ""
                analysis_results = None
                
                for result in self.ai_api.analyze_task_patterns(tasks):
                    if result['status'] == 'streaming':
                        current_analysis += result['chunk']
                        status.update(f"[bold blue]Analyzing...\n\n{current_analysis}")
                    elif result['status'] == 'complete':
                        console.print("\n[bold green]Task Analysis:[/bold green]")
                        analysis_results = result['analysis']
                        
                        for category, details in analysis_results.items():
                            console.print(Panel(
                                Markdown(f"## {category}\n\n{details}"),
                                title=category
                            ))
                    else:
                        console.print(f"\n[red]Error: {result.get('message', 'Unknown error')}[/red]")
                
                # Save the analysis results to the output file if available
                if analysis_results:
                    # Calculate the total word count
                    word_count = 0
                    for category, details in analysis_results.items():
                        word_count += len(details.split())
                    
                    # Save the analysis results to the output file
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(analysis_results, f, indent=2)
                    
                    console.print(f"\n[green]Analysis saved to: {os.path.abspath(output_path)}[/green]")
                    console.print(f"[green]Word count: {word_count}[/green]")
            except Exception as e:
                console.print(f"\n[red]Failed to analyze tasks: {str(e)}[/red]")
    
    def list_task_files(self):
        """List all task files in the data directory."""
        files, count = self.task_api.list_task_files(self.default_data_dir)
        
        if count == 0:
            console.print("[yellow]No task files found in the data directory.[/yellow]")
            return None
        
        console.print(f"\n[bold]Available Task Files:[/bold] [cyan]({count} files found)[/cyan]")
        
        # Get task counts for each file for display
        file_info = []
        for file_path in files:
            task_count = self.task_api.get_task_count(str(file_path))
            file_info.append((file_path, task_count))
        
        # Display files with task counts
        for i, (file_path, task_count) in enumerate(file_info, 1):
            # Highlight the current file
            if str(file_path) == self.current_file or file_path.name == Path(self.current_file).name:
                console.print(f"{i}. [green]{file_path.name}[/green] [cyan]({task_count} tasks)[/cyan] (current)")
            else:
                console.print(f"{i}. {file_path.name} [cyan]({task_count} tasks)[/cyan]")
        
        return files
    
    def load_task_file(self):
        """Load tasks from a selected file."""
        files = self.list_task_files()
        
        if not files:
            return
        
        # Ask user to select a file
        choices = [str(i) for i in range(1, len(files) + 1)]
        choice = Prompt.ask("Select a file to load", choices=choices)
        
        selected_file = files[int(choice) - 1]
        
        # Show validation status
        with Status(f"[bold blue]Validating file {selected_file.name}...", spinner="dots") as status:
            # Validate and load the file
            success, message, task_count = self.task_api.change_tasks_file(str(selected_file))
        
        if success:
            self.current_file = str(selected_file)
            console.print(f"[green]{message}[/green]")
            if task_count == 0:
                console.print("[yellow]Warning: The file contains no tasks.[/yellow]")
            else:
                console.print(f"[green]Successfully loaded {task_count} tasks from {selected_file.name}[/green]")
        else:
            console.print(f"[red]Failed to load tasks: {message}[/red]")
    
    def exit_application(self):
        """Exit the application and clear the terminal."""
        console.print("[yellow]Goodbye![/yellow]")
        
        # Clear the terminal screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        sys.exit(0)
    
    def create_new_task_file(self):
        """Create a new empty task file."""
        import json
        
        # Ask for the new file name
        file_name = Prompt.ask("\nEnter new file name (without extension)")
        
        # Ensure it has .json extension
        if not file_name.endswith('.json'):
            file_name += '.json'
        
        # Create full path in the data directory
        file_path = Path(self.default_data_dir) / file_name
        
        # Check if file already exists
        if file_path.exists():
            overwrite = Prompt.ask(
                f"File {file_name} already exists. Overwrite?",
                choices=["y", "n"],
                default="n"
            )
            if overwrite.lower() != "y":
                console.print("[yellow]Operation cancelled.[/yellow]")
                return
        
        # Create an empty task list
        empty_tasks = []
        
        # Ensure data directory exists
        Path(self.default_data_dir).mkdir(exist_ok=True)
        
        # Write the empty task list to the file
        try:
            with open(file_path, 'w') as f:
                json.dump(empty_tasks, f, indent=2)
            
            console.print(f"[green]Created new task file: {file_name}[/green]")
            
            # Ask if user wants to switch to the new file
            switch = Prompt.ask(
                "Switch to the new file?",
                choices=["y", "n"],
                default="y"
            )
            
            if switch.lower() == "y":
                success, message, task_count = self.task_api.change_tasks_file(str(file_path))
                if success:
                    self.current_file = str(file_path)
                    console.print(f"[green]{message}[/green]")
                    console.print(f"[green]Switched to new empty task file: {file_name}[/green]")
                else:
                    console.print(f"[red]Failed to switch to new file: {message}[/red]")
        
        except Exception as e:
            console.print(f"[red]Error creating new task file: {str(e)}[/red]")
    
    def run(self):
        """Run the application."""
        try:
            self.initialize()
            
            while True:
                # Show the current file in the header with task count
                current_file_name = Path(self.current_file).name
                task_count = len(self.task_api.list_tasks())
                console.print(f"\n[bold cyan]Thoughtful Task Manager[/bold cyan] - [yellow]File: {current_file_name} ({task_count} tasks)[/yellow]")
                console.print("1. View Tasks")
                console.print("2. Add Task")
                console.print("3. Update Task")
                console.print("4. Delete Task")
                console.print("5. Show Priority Guide")
                console.print("6. Load Tasks from File")
                console.print("7. Create New Task File")
                if self.ai_enabled:
                    console.print("8. Get AI Suggestions")
                    console.print("9. Analyze Patterns")
                console.print("0. Exit")
                
                choices = ["1", "2", "3", "4", "5", "6", "7"]
                if self.ai_enabled:
                    choices.extend(["8", "9"])
                choices.append("0")
                
                choice = Prompt.ask("Select an option", choices=choices)
                
                if choice == "1":
                    tasks = self.task_api.list_tasks()
                    self.display_tasks(tasks)
                
                elif choice == "2":
                    self.show_priority_guide()
                    
                    # Title validation loop
                    while True:
                        title = Prompt.ask("\nTask title")
                        # Validate title
                        if title.isdigit():
                            console.print("[red]Error: Task title cannot be purely numeric[/red]")
                            continue
                        if len(title) < 5:
                            console.print("[red]Error: Task title must be at least 5 characters long[/red]")
                            continue
                        break
                    
                    description = Prompt.ask("Task description")
                    console.print("\nPriority Levels:")
                    for level, desc in PRIORITY_DESCRIPTIONS.items():
                        console.print(f"{level}: {desc}")
                    priority = int(Prompt.ask("\nPriority", choices=["1", "2", "3", "4", "5"]))
                    
                    # New code for dependencies
                    dependencies = []
                    add_dependencies = Prompt.ask(
                        "\nAdd dependencies?", 
                        choices=["y", "n"], 
                        default="n"
                    )
                    
                    if add_dependencies.lower() == "y":
                        # Get existing tasks
                        existing_tasks = self.task_api.list_tasks()
                        
                        if not existing_tasks:
                            console.print("[yellow]No existing tasks to add as dependencies.[/yellow]")
                        else:
                            # Display available tasks
                            console.print("\n[bold]Available Tasks:[/bold]")
                            for i, task in enumerate(existing_tasks, 1):
                                console.print(f"{i}. {task['title']} (ID: {task['id']})")
                            
                            # Let user select multiple tasks
                            console.print("\nEnter task numbers separated by commas (e.g., '1,3,4')")
                            console.print("Or press Enter to skip")
                            
                            selection = Prompt.ask("Select dependencies", default="")
                            
                            if selection.strip():
                                try:
                                    # Parse selection and get task IDs
                                    selected_indices = [int(idx.strip()) - 1 for idx in selection.split(",")]
                                    for idx in selected_indices:
                                        if 0 <= idx < len(existing_tasks):
                                            dependencies.append(existing_tasks[idx]['id'])
                                    
                                    if dependencies:
                                        console.print(f"[green]Added {len(dependencies)} dependencies[/green]")
                                except ValueError:
                                    console.print("[yellow]Invalid selection format. No dependencies added.[/yellow]")
                    
                    # Create task with dependencies
                    task = self.task_api.create_task(
                        title, 
                        description, 
                        priority=priority,
                        dependencies=dependencies
                    )
                    
                    # Check if the title was modified to make it unique
                    if task['title'] != title:
                        console.print(f"[yellow]Note: Title was modified to avoid duplication.[/yellow]")
                    
                    console.print(f"[green]Created task: {task['title']}[/green]")
                
                elif choice == "3":
                    title = Prompt.ask("Task title to update")
                    task = self.task_api.get_task(title)
                    if task:
                        update_type = Prompt.ask(
                            "What to update",
                            choices=["title", "status", "priority", "description", "dependencies"]
                        )
                        
                        if update_type == "status":
                            new_value = Prompt.ask("New status", choices=["pending", "in_progress", "completed"])
                            updated_task = self.task_api.update_task(title, **{update_type: new_value})
                        
                        elif update_type == "priority":
                            self.show_priority_guide()
                            new_value = int(Prompt.ask("\nNew priority", choices=["1", "2", "3", "4", "5"]))
                            updated_task = self.task_api.update_task(title, **{update_type: new_value})
                        
                        elif update_type == "title":
                            # Title validation loop
                            while True:
                                new_value = Prompt.ask("New title")
                                # Validate title
                                if new_value.isdigit():
                                    console.print("[red]Error: Task title cannot be purely numeric[/red]")
                                    continue
                                if len(new_value) < 5:
                                    console.print("[red]Error: Task title must be at least 5 characters long[/red]")
                                    continue
                                break
                            
                            updated_task = self.task_api.update_task(title, **{update_type: new_value})
                            
                            # Check if the title was modified to make it unique
                            if updated_task and updated_task['title'] != new_value:
                                console.print(f"[yellow]Note: Title was modified to avoid duplication.[/yellow]")
                        
                        elif update_type == "description":
                            new_value = Prompt.ask("New description")
                            updated_task = self.task_api.update_task(title, **{update_type: new_value})
                        
                        elif update_type == "dependencies":
                            # Get existing tasks
                            existing_tasks = self.task_api.list_tasks()
                            
                            if not existing_tasks:
                                console.print("[yellow]No existing tasks to add as dependencies.[/yellow]")
                                continue
                            
                            # Show current dependencies
                            current_deps = task.get('dependencies', [])
                            if current_deps:
                                console.print("\n[bold]Current Dependencies:[/bold]")
                                for dep_id in current_deps:
                                    dep_task = self.task_api.get_task(dep_id)
                                    if dep_task:
                                        console.print(f"• {dep_task['title']} (ID: {dep_id})")
                                    else:
                                        console.print(f"• Unknown task (ID: {dep_id})")
                            else:
                                console.print("\n[yellow]No current dependencies.[/yellow]")
                            
                            # Ask if user wants to replace or add dependencies
                            dep_action = Prompt.ask(
                                "\nHow do you want to update dependencies?",
                                choices=["replace", "add", "remove", "cancel"],
                                default="add"
                            )
                            
                            if dep_action == "cancel":
                                console.print("[yellow]Dependency update cancelled.[/yellow]")
                                continue
                            
                            # Display available tasks
                            console.print("\n[bold]Available Tasks:[/bold]")
                            for i, t in enumerate(existing_tasks, 1):
                                # Don't show the current task as a dependency option
                                if t['id'] != task['id']:
                                    in_deps = t['id'] in current_deps
                                    status = "[green](current dependency)[/green]" if in_deps else ""
                                    console.print(f"{i}. {t['title']} (ID: {t['id']}) {status}")
                            
                            if dep_action == "replace" or dep_action == "add":
                                # Let user select multiple tasks
                                console.print("\nEnter task numbers separated by commas (e.g., '1,3,4')")
                                console.print("Or press Enter to skip")
                                
                                selection = Prompt.ask("Select dependencies", default="")
                                
                                if selection.strip():
                                    try:
                                        # Parse selection and get task IDs
                                        selected_indices = [int(idx.strip()) - 1 for idx in selection.split(",")]
                                        selected_deps = []
                                        
                                        for idx in selected_indices:
                                            if 0 <= idx < len(existing_tasks) and existing_tasks[idx]['id'] != task['id']:
                                                selected_deps.append(existing_tasks[idx]['id'])
                                        
                                        if dep_action == "replace":
                                            # Replace all dependencies
                                            new_deps = selected_deps
                                        else:  # add
                                            # Add to existing dependencies
                                            new_deps = list(set(current_deps + selected_deps))
                                        
                                        # Update the task
                                        updated_task = self.task_api.update_task(title, dependencies=new_deps)
                                        console.print(f"[green]Updated dependencies for task: {updated_task['title']}[/green]")
                                    except ValueError:
                                        console.print("[yellow]Invalid selection format. No changes made.[/yellow]")
                                        continue
                                else:
                                    if dep_action == "replace":
                                        # Clear all dependencies
                                        updated_task = self.task_api.update_task(title, dependencies=[])
                                        console.print(f"[green]Cleared all dependencies for task: {updated_task['title']}[/green]")
                                    else:
                                        console.print("[yellow]No dependencies added.[/yellow]")
                                        continue
                            
                            elif dep_action == "remove":
                                if not current_deps:
                                    console.print("[yellow]No dependencies to remove.[/yellow]")
                                    continue
                                
                                # Let user select dependencies to remove
                                console.print("\nEnter task numbers to remove, separated by commas")
                                console.print("Or press Enter to skip")
                                
                                selection = Prompt.ask("Select dependencies to remove", default="")
                                
                                if selection.strip():
                                    try:
                                        # Parse selection and get task IDs
                                        selected_indices = [int(idx.strip()) - 1 for idx in selection.split(",")]
                                        to_remove = []
                                        
                                        for idx in selected_indices:
                                            if 0 <= idx < len(existing_tasks):
                                                to_remove.append(existing_tasks[idx]['id'])
                                        
                                        # Remove selected dependencies
                                        new_deps = [dep for dep in current_deps if dep not in to_remove]
                                        
                                        # Update the task
                                        updated_task = self.task_api.update_task(title, dependencies=new_deps)
                                        console.print(f"[green]Removed selected dependencies from task: {updated_task['title']}[/green]")
                                    except ValueError:
                                        console.print("[yellow]Invalid selection format. No changes made.[/yellow]")
                                        continue
                                else:
                                    console.print("[yellow]No dependencies removed.[/yellow]")
                                    continue
                        
                        console.print(f"[green]Updated task: {updated_task['title']}[/green]")
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
                
                elif choice == "6":
                    self.load_task_file()
                
                elif choice == "7":
                    self.create_new_task_file()
                
                elif choice == "8" and self.ai_enabled:
                    self.handle_ai_suggestions()
                
                elif choice == "9" and self.ai_enabled:
                    self.handle_task_analysis()
                
                elif choice == "0" or choice.lower() == "exit":
                    self.exit_application()
        
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
