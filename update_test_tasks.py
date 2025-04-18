import json
import uuid

# Read the current test tasks
with open('data/test_tasks.json', 'r') as f:
    data = json.load(f)

# Get the tasks list
tasks = data.get("tasks", [])

# Update each task with the new fields
for task in tasks:
    # Add UUID if not present
    if 'uuid' not in task:
        task['uuid'] = str(uuid.uuid4())
    
    # Add model information if not present
    if 'model' not in task:
        task['model'] = "unknown"
    
    # Add source information if not present
    if 'source' not in task:
        task['source'] = "human"
    
    # Add dependencies if not present
    if 'dependencies' not in task:
        task['dependencies'] = []
    
    # Rename created_at to created_date if needed
    if 'created_at' in task and 'created_date' not in task:
        task['created_date'] = task.pop('created_at')
    
    # Remove updated_at as it's not in our schema
    if 'updated_at' in task:
        task.pop('updated_at')

# Write the updated tasks back to the file
with open('data/test_tasks.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Updated {len(tasks)} tasks in data/test_tasks.json")
