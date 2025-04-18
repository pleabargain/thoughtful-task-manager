#!/usr/bin/env python3

import os
import subprocess
import requests
from typing import List, Dict, Any
import ollama

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_available_models() -> List[Dict[str, Any]]:
    """Get list of available Ollama models."""
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            check=True
        )
        return parse_model_list(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error getting models: {str(e)}")
        return []

def parse_model_list(output: str) -> List[Dict[str, Any]]:
    """Parse the output of ollama list command."""
    models = []
    lines = output.strip().split('\n')
    
    if len(lines) <= 1:  # No models or just header
        return models
    
    for line in lines[1:]:  # Skip header
        if not line.strip():
            continue
        
        parts = line.split()
        if len(parts) >= 4:
            name = parts[0]
            size = f"{parts[2]}{parts[3]}" if len(parts) > 3 else parts[2]
            modified = ' '.join(parts[4:]) if len(parts) > 4 else 'Unknown'
            
            models.append({
                'name': name,
                'size': size,
                'modified': modified
            })
    
    return models

def display_models(models: List[Dict[str, Any]]) -> None:
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

def select_model(models: List[Dict[str, Any]]) -> str:
    """Prompt user to select a model."""
    while True:
        try:
            choice = input(f"\nSelect a model by entering its number (1-{len(models)}): ").strip()
            num = int(choice)
            if 1 <= num <= len(models):
                return models[num-1]['name']
        except ValueError:
            pass
        print(f"Please enter a number between 1 and {len(models)}")

def main():
    """Main function to run the Ollama chat interface."""
    clear_screen()
    print("Checking Ollama connection...")
    
    # Check if Ollama service is running
    try:
        response = requests.get("http://localhost:11434/api/version")
        if response.status_code != 200:
            print("Error: Ollama service is not responding correctly")
            return
    except requests.RequestException:
        print("Error: Ollama service is not running. Please start Ollama first.")
        return
    
    # Get and display available models
    models = get_available_models()
    if not models:
        print("No models found. Please install at least one model using 'ollama pull <model_name>'")
        return
    
    display_models(models)
    model_name = select_model(models)
    
    print(f"\nInitializing chat with model: {model_name}")
    print("\nEnter your message (or 'quit' to exit)")
    
    # Initialize Ollama client
    client = ollama.Client(host="http://localhost:11434")
    
    # Main chat loop
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ('quit', 'exit'):
                print("\nGoodbye!")
                break
            
            if not user_input:
                continue
            
            # Stream the response
            print("\nAssistant: ", end='', flush=True)
            for chunk in client.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': user_input}],
                stream=True
            ):
                print(chunk['message']['content'], end='', flush=True)
            print()  # New line after response
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            continue

if __name__ == '__main__':
    main() 