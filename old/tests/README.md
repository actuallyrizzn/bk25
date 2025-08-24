# Tests

This directory contains test files for BK25 components.

## Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for system interactions
├── fixtures/       # Test data and mock files
└── helpers/        # Test utilities and helper functions
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Run specific test file
npm test -- --grep "persona-manager"
```

## Test Categories

### Unit Tests
- **Core Components**: `src/core/` module testing
- **Generators**: Platform-specific code generation testing
- **Persona System**: Persona loading and management testing
- **Channel System**: Channel simulation and artifact generation

### Integration Tests
- **API Endpoints**: REST API functionality testing
- **Persona Switching**: End-to-end persona management
- **Code Generation**: Complete automation script generation flows
- **Channel Simulation**: Multi-channel conversation testing

## Writing Tests

Tests should follow these conventions:
- Use descriptive test names
- Include setup and teardown as needed
- Mock external dependencies
- Test both success and error cases
- Maintain good test coverage

## Test Data

The `fixtures/` directory contains:
- Sample persona configurations
- Mock conversation histories
- Example automation scripts
- Channel-specific test artifacts
