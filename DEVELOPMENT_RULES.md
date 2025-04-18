# Development Rules

## General Guidelines

1. **Code Quality**: Maintain high standards for code quality, including clear and concise code, thorough documentation, and adherence to coding conventions.
2. **Code Review**: Code changes should be reviewed by peers to ensure they meet quality standards.
3. **Testing**: Comprehensive testing is essential. Write unit tests for all new functionality and critical changes.
4. **Documentation**: Keep comprehensive documentation up to date, including code comments, README files, and any relevant documentation.

## Testing Requirements

1. **Unit Tests**: Write unit tests for all new functionality. Unit tests should be comprehensive, covering both typical use cases and edge cases.
2. **Integration Tests**: Ensure that all components work together correctly through integration tests.
3. **UI Tests**: For applications with a user interface, include tests for the UI components.
4. **Running Tests**: Always use `pytest -v` to run all tests in the project. This ensures comprehensive test coverage and helps identify any regressions early.
5. **Error Isolation**: If an error occurs in the execution of the code, a unit test must be written to help isolate that error. These tests should:
   - Target the specific functionality that's failing
   - Provide clear error messages that identify the root cause
   - Be included in the same commit as the fix
   - Serve as regression tests to prevent the issue from recurring

## Commit Messages

1. **Descriptive Messages**: Write clear, descriptive commit messages that explain the changes being made.
2. **Link to Issues**: If applicable, link commits to relevant issues or pull requests.

## Code Structure

1. **Modular Design**: Structure code into logical modules, each with a clear purpose.
2. **File Organization**: Follow a consistent file organization that makes it easy to locate files.
3. **Documentation**: Document the purpose of each module and file.
4. **Object Identification**: Use UUID for reliable object identification across systems. Every object that needs to be uniquely identified should have a UUID field.
5. **Schema Definition**: Define data structures using JSON schema to ensure consistency and validation.

## Code Style

1. **Consistency**: Follow a consistent style guide for code formatting.
2. **Readability**: Write code that is easy to read and understand.
3. **Naming Conventions**: Use clear and descriptive names for variables, functions, and classes.

## Code Maintainability

1. **Refactoring**: Regularly refactor code to improve maintainability.
2. **Performance**: Write code that is efficient and performs well.
3. **Error Handling**: Implement robust error handling mechanisms.
4. **Type Checking**: Implement explicit type checking for methods that can receive different types of inputs.
5. **Interface Consistency**: Ensure consistent interfaces between components, especially when data is passed between them.

## Data Safety

1. **File Operations**: Never delete or overwrite files without explicitly informing the user and obtaining confirmation.
2. **Backups**: Create backups before performing operations that could result in data loss.
3. **Validation**: Always validate file contents before processing to prevent corruption or data loss.
4. **Error Recovery**: Implement mechanisms to recover from errors during file operations.
5. **Schema Validation**: Validate data against JSON schema before saving to ensure data integrity.

## Data Validation

1. **Schema Definition**: All data structures must have a corresponding JSON schema that defines their structure, required fields, and constraints.
2. **Validation Process**: Data must be validated against its schema when loading and saving.
3. **Schema Updates**: When updating a schema:
   - Ensure backward compatibility or provide migration tools
   - Update all related code that interacts with the schema
   - Document changes in the schema version history
4. **Error Handling**: Validation errors must be handled gracefully:
   - Provide clear error messages that identify the specific validation issue
   - Log validation failures for debugging
   - Prevent invalid data from being saved
5. **Default Values**: Provide sensible default values for optional fields to ensure valid data even when fields are missing.
6. **UUID Generation**: Generate UUIDs for new objects using the uuid module, ensuring uniqueness across systems.
7. **Metadata Tracking**: Include metadata fields (e.g., model, source) to track the origin and history of data objects.

## Data Processing

1. **Complete Data Processing**: When processing collections of data, the entire collection must be preserved unless explicitly required to filter or truncate.
2. **Type Handling**: Methods that process data must handle different input types gracefully:
   - Check the type of input data before processing (e.g., `isinstance(data, dict)`)
   - Handle both object instances and dictionaries when appropriate
   - Document expected input types in method docstrings
3. **Data Integrity**: Ensure that data processing does not inadvertently lose or modify information:
   - Preserve all fields when converting between formats
   - Maintain relationships between data elements
   - Verify data integrity after processing
4. **Collection Processing**: When processing collections (lists, arrays):
   - Verify that all items in the collection are processed
   - Handle empty collections gracefully
   - Preserve the order of items when order matters
5. **LLM Input Verification**: When sending data to LLMs or external services:
   - Verify that the complete dataset is included
   - Include metadata about the dataset (e.g., count of items)
   - Log what is being sent for debugging purposes

## API Design

1. **Consistent Interfaces**: APIs should maintain consistent interfaces:
   - Methods with similar purposes should accept and return similar types
   - Return types should be consistent across related methods
   - Parameter names should be consistent across related methods
2. **Flexible Input Handling**: APIs should be designed to handle various input formats:
   - Accept both object instances and dictionaries when appropriate
   - Document all accepted input formats
   - Provide examples of different input formats in documentation
3. **Robust Error Handling**: APIs should handle errors gracefully:
   - Catch and handle type errors explicitly
   - Provide clear error messages that identify the issue
   - Fail gracefully with meaningful error messages
4. **Type Annotations**: Use type annotations to document expected types:
   - Use Union types for methods that accept multiple types (e.g., `Union[Task, Dict[str, Any]]`)
   - Document type expectations in docstrings
   - Consider using TypedDict for dictionary structures
5. **Testing Different Input Types**: Write tests that verify API behavior with different input types:
   - Test with object instances
   - Test with dictionaries
   - Test with mixed collections
   - Test with edge cases (empty collections, invalid types)
