# Development Rules and Guidelines

## Code Organization
1. All new features must follow MCP (Model-Controller-Presenter) pattern
2. Keep files focused and single-responsibility
3. Maximum file length: 500 lines
4. Use type hints for all function parameters and returns

## Priority System Rules
1. Every task must have a priority (1-5)
2. Priority changes must be logged
3. Critical (level 5) tasks require a due date
4. Tasks can't be marked complete without all dependencies completed

## AI Integration Rules
1. AI features must be optional and gracefully degrade
2. All AI prompts must be templated and versioned
3. AI responses must be validated before use
4. Cache AI suggestions for similar contexts

## Testing Requirements
1. All new features require unit tests
2. Minimum 80% code coverage
3. Integration tests for AI features
4. Test both with and without Ollama available

## Documentation Standards
1. All public functions must have docstrings
2. Update README.md for user-facing changes
3. Update PROJECT_STATUS.md for development changes
4. Keep CHANGELOG.md updated with semantic versioning

## Git Workflow
1. Branch naming: 
   - feature/description
   - bugfix/description
   - hotfix/description
2. Commit messages must be descriptive and follow conventional commits
3. No direct commits to main branch
4. Pull requests require passing tests

## Data Management
1. All task data must be JSON serializable
2. Automatic backups before data modifications
3. Data validation before save
4. Support for data export/import

## Security Guidelines
1. No hardcoded credentials
2. Validate all user inputs
3. Secure storage of API keys
4. Regular dependency updates

## Performance Rules
1. Task operations must complete under 100ms
2. AI operations must timeout after 5s
3. Implement caching for frequent operations
4. Optimize file I/O operations

## Error Handling
1. All errors must be logged
2. User-friendly error messages
3. Graceful degradation of features
4. Automatic error reporting (optional)

## Accessibility
1. Color schemes must have sufficient contrast
2. Support for screen readers
3. Keyboard navigation support
4. Clear status messages

## Version Control
1. Semantic versioning (MAJOR.MINOR.PATCH)
2. Feature flags for major changes
3. Backward compatibility for data files
4. Migration scripts for breaking changes

These rules will be referenced and updated throughout the project development. All team members must follow these guidelines to maintain code quality and consistency. 