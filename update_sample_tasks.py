import json
import uuid

# Read the current sample tasks
with open('data/sample_tasks.json', 'r') as f:
    tasks = json.load(f)

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

# Write the updated tasks back to the file
with open('data/sample_tasks.json', 'w') as f:
    json.dump(tasks, f, indent=2)

print(f"Updated {len(tasks)} tasks in data/sample_tasks.json")
