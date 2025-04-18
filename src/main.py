#!/usr/bin/env python3
"""
Main entry point for the Thoughtful Task Manager.
"""

import sys
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    """Main entry point for the application."""
    console.print("[bold green]Welcome to Thoughtful Task Manager![/bold green]")
    
    # TODO: Implement main application logic
    console.print("Initializing...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]An error occurred: {str(e)}[/red]")
        sys.exit(1) 