import json
import jsonschema
from pathlib import Path

def test_tasks_schema():
    """Test that tasks.json conforms to the schema."""
    # Load the schema
    schema_path = Path("data/task_schema.json")
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # Load the tasks
    tasks_path = Path("data/tasks.json")
    with open(tasks_path, 'r') as f:
        tasks = json.load(f)
    
    # Validate tasks against schema
    try:
        jsonschema.validate(instance=tasks, schema=schema)
        print("✅ Tasks data is valid according to the schema")
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ Schema validation error: {str(e)}")
        return False
    
    # Check that each task has the required fields
    required_fields = ["id", "uuid", "title", "description", "dependencies", 
                      "status", "priority", "created_date", "model", "source"]
    
    for i, task in enumerate(tasks):
        missing_fields = [field for field in required_fields if field not in task]
        if missing_fields:
            print(f"❌ Task {i+1} is missing required fields: {', '.join(missing_fields)}")
            return False
    
    print(f"✅ All {len(tasks)} tasks have the required fields")
    
    # Print a sample task for verification
    if tasks:
        print("\nSample task:")
        print(json.dumps(tasks[0], indent=2))
    
    return True

if __name__ == "__main__":
    test_tasks_schema()
