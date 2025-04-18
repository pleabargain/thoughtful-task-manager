#!/usr/bin/env python3
"""
Script to analyze patterns in task data and save results to JSON.
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

from src.api.ai_api import AIAPI
from src.api.task_api import TaskAPI

def count_words(text):
    """Count the number of words in a text."""
    if not text:
        return 0
    return len(text.split())

def analyze_patterns(json_file, output_dir="output"):
    """
    Analyze patterns in the specified JSON file and save results to output directory.
    
    Args:
        json_file: Path to the JSON file to analyze
        output_dir: Directory to save the analysis results
    
    Returns:
        Tuple of (success, message, output_path)
    """
    # Ensure the JSON file exists
    if not os.path.exists(json_file):
        return False, f"Error: File {json_file} not found", None
    
    # Create the output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)
    
    # Get the base name of the JSON file without extension
    base_name = os.path.basename(json_file)
    file_name = os.path.splitext(base_name)[0]
    
    # Create the output file name with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"analysis-{file_name}-{timestamp}.json"
    output_path = os.path.join(output_dir, output_file)
    
    try:
        # Initialize the AI API
        ai_api = AIAPI()
        ai_api.initialize()
        
        if not ai_api.verify_model():
            return False, "Error: AI model verification failed", None
        
        # Initialize the Task API with the specified JSON file
        task_api = TaskAPI(data_file=json_file)
        tasks = task_api.list_tasks()
        
        if not tasks:
            return False, f"Error: No tasks found in {json_file}", None
        
        print(f"Analyzing {len(tasks)} tasks from {json_file}...")
        
        # Collect the analysis results
        analysis_results = {}
        word_count = 0
        
        # Process the analysis results
        analysis_results = None
        current_chunk = ""
        
        for result in ai_api.analyze_task_patterns(tasks):
            print(f"Analysis result status: {result['status']}")
            if result['status'] == 'complete':
                analysis_results = result['analysis']
                break
            elif result['status'] == 'streaming':
                current_chunk += result.get('chunk', '')
            elif result['status'] == 'error':
                print(f"Error during analysis: {result.get('message', 'Unknown error')}")
                # Don't return immediately, try to create a fallback analysis
        
        # If we didn't get a valid analysis but have streaming content, try to create a fallback
        if not analysis_results and current_chunk:
            print("Attempting to create fallback analysis from streaming content...")
            try:
                # Try to extract JSON from the content (it might be wrapped in markdown code blocks)
                import re
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', current_chunk)
                if json_match:
                    json_content = json_match.group(1)
                    analysis_results = json.loads(json_content)
                    print("Successfully extracted JSON from markdown code blocks")
                else:
                    # Try to find anything that looks like JSON
                    json_start = current_chunk.find('{')
                    json_end = current_chunk.rfind('}')
                    if json_start >= 0 and json_end > json_start:
                        json_content = current_chunk[json_start:json_end+1]
                        analysis_results = json.loads(json_content)
                        print("Successfully extracted JSON from content")
            except json.JSONDecodeError:
                print("Failed to extract valid JSON from content")
        
        # If we still don't have a valid analysis, create a simple one from the content
        if not analysis_results:
            print("Creating simple analysis from content...")
            # Create a simple analysis with the content we have
            analysis_results = {
                "Priority Distribution": "Could not analyze priority distribution due to parsing error.",
                "Status Patterns": "Could not analyze status patterns due to parsing error.",
                "Time Management": "Could not analyze time management due to parsing error.",
                "Task Relationships": "Could not analyze task relationships due to parsing error.",
                "Content Analysis": "Could not analyze content due to parsing error.",
                "Raw Content": current_chunk[:1000] + "..." if len(current_chunk) > 1000 else current_chunk
            }
        
        # Calculate the total word count
        for category, details in analysis_results.items():
            word_count += count_words(details)
        
        # Save the analysis results to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2)
        
        return True, f"Analysis completed successfully with {word_count} words", output_path
    
    except Exception as e:
        return False, f"Error during analysis: {str(e)}", None

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Analyze patterns in task data and save results to JSON")
    parser.add_argument("json_file", help="Path to the JSON file to analyze")
    parser.add_argument("--output-dir", default="output", help="Directory to save the analysis results")
    
    args = parser.parse_args()
    
    success, message, output_path = analyze_patterns(args.json_file, args.output_dir)
    
    if success:
        print(f"[SUCCESS] {message}")
        print(f"Analysis saved to: {os.path.abspath(output_path)}")
    else:
        print(f"[ERROR] {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
