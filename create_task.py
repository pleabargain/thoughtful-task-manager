update rules to include JSON schemaimport json
import uuid
import argparse
from datetime import datetime

def create_task(title, description, priority=3, status="pending", due_date=None, model="unknown", source="human"):
    """Create a new task with the required fields."""
    task = {
        "id": f"task-{uuid.uuid4().hex[:6]}",
        "uuid": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "dependencies": [],
        "status": status,
        "priority": int(priority),
        "created_date": datetime.now().isoformat(),
        "due_date": due_date,
        "model": model,
        "source": source
    }
    
    return task

def add_task_to_file(task, file_path="data/tasks.json"):
    """Add a task to the specified file."""
    try:
        # Read existing tasks
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                
                # Handle both formats: direct list of tasks or {"tasks": [...]}
                if isinstance(data, dict) and "tasks" in data:
                    tasks = data["tasks"]
                    data["tasks"].append(task)
                else:
                    tasks = data
                    data.append(task)
            except json.JSONDecodeError:
                # If the file is empty or invalid, create a new task list
                tasks = [task]
                data = tasks
    except FileNotFoundError:
        # If the file doesn't exist, create a new task list
        tasks = [task]
        data = tasks
    
    # Write the updated tasks back to the file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return len(tasks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new task")
    parser.add_argument("title", help="Task title")
    parser.add_argument("description", help="Task description")
    parser.add_argument("--priority", type=int, default=3, help="Task priority (1-5)")
    parser.add_argument("--status", default="pending", help="Task status")
    parser.add_argument("--due-date", help="Task due date (ISO format)")
    parser.add_argument("--model", default="unknown", help="Model used to create the task")
    parser.add_argument("--source", default="human", help="Source of the task")
    parser.add_argument("--file", default="data/tasks.json", help="File to add the task to")
    
    args = parser.parse_args()
    
    task = create_task(
        args.title,
        args.description,
        args.priority,
        args.status,
        args.due_date,
        args.model,
        args.source
    )
    
    count = add_task_to_file(task, args.file)
    
    print(f"Task '{args.title}' added to {args.file}")
    print(f"Total tasks: {count}")
