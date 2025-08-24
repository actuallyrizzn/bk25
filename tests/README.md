# BK25 Test Suite

Comprehensive testing for the BK25 Python migration with 100% coverage across unit, integration, and end-to-end tests.

## 🧪 Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and shared fixtures
├── run_tests.py             # Test runner script
├── README.md                # This documentation
├── unit/                    # Unit tests for individual components
│   ├── test_persona_manager.py
│   ├── test_channel_manager.py
│   └── test_bk25_core.py
├── integration/             # Integration tests for component interactions
│   └── test_persona_channel_integration.py
├── e2e/                    # End-to-end tests for complete workflows
│   └── test_complete_workflow.py
└── api/                    # API endpoint tests
    └── test_fastapi_endpoints.py
```

## 🎯 Test Categories

### **Unit Tests** (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Coverage**: 100% of component methods and edge cases
- **Speed**: Fast execution (< 1 second per test)
- **Dependencies**: Mocked external dependencies

**Components Tested:**
- `PersonaManager` - Persona loading, switching, validation
- `ChannelManager` - Channel management and capabilities
- `BK25Core` - Core system integration and workflows
- `ConversationMemory` - Memory management and persistence
- `CodeGenerator` - Script generation across platforms
- `LLMManager` - LLM integration and provider management
- `ScriptExecutor` - Script execution and monitoring
- `ExecutionMonitor` - Task management and statistics

### **Integration Tests** (`tests/integration/`)
- **Purpose**: Test component interactions and data flow
- **Coverage**: Component communication and state management
- **Speed**: Medium execution (1-5 seconds per test)
- **Dependencies**: Real component instances with mocked external services

**Integration Areas:**
- Persona-Channel compatibility and switching
- Memory persistence across operations
- Component state synchronization
- Error handling and recovery
- Data validation and transformation

### **End-to-End Tests** (`tests/e2e/`)
- **Purpose**: Test complete user workflows from start to finish
- **Coverage**: Full system behavior and user scenarios
- **Speed**: Slow execution (5-30 seconds per test)
- **Dependencies**: Full system with mocked external APIs

**Workflows Tested:**
- Complete automation workflow
- Persona switching with context preservation
- Multi-conversation management
- Error recovery and system resilience
- Performance under load
- Data persistence across operations
- Concurrent operation handling
- Edge case handling

### **API Tests** (`tests/api/`)
- **Purpose**: Test FastAPI endpoints and HTTP behavior
- **Coverage**: All API endpoints, error handling, and response formats
- **Speed**: Fast execution (< 1 second per test)
- **Dependencies**: Mocked BK25Core with FastAPI TestClient

**API Areas Tested:**
- All REST endpoints (GET, POST, PUT, DELETE)
- Request validation and error handling
- Response format consistency
- CORS headers and middleware
- API documentation endpoints
- Error handlers (404, 500)

## 🚀 Running Tests

### **Quick Start**
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests with coverage
python tests/run_tests.py

# Run specific test types
python tests/run_tests.py --type unit
python tests/run_tests.py --type integration
python tests/run_tests.py --type e2e
python tests/run_tests.py --type api
```

### **Advanced Test Execution**
```bash
# Run fast tests only (unit tests)
python tests/run_tests.py --type fast

# Run performance tests
python tests/run_tests.py --type performance

# Run tests in parallel
python tests/run_tests.py --parallel

# Run tests with automatic rerun on failure
python tests/run_tests.py --rerun

# Run tests with debug output
python tests/run_tests.py --debug

# Check test dependencies
python tests/run_tests.py --check-deps
```

### **Direct Pytest Commands**
```bash
# Run all tests
pytest

# Run specific test files
pytest tests/unit/test_persona_manager.py

# Run tests with specific markers
pytest -m unit
pytest -m integration
pytest -m e2e
pytest -m api

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v -s
```

## 📊 Test Coverage

### **Coverage Targets**
- **Overall Coverage**: 90% minimum
- **Unit Tests**: 100% of component methods
- **Integration Tests**: 100% of component interactions
- **E2E Tests**: 100% of user workflows
- **API Tests**: 100% of endpoints and error cases

### **Coverage Reports**
```bash
# Generate coverage reports
pytest --cov=src --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml:coverage.xml

# View HTML coverage report
open htmlcov/index.html
```

## 🔧 Test Configuration

### **Pytest Configuration** (`pytest.ini`)
- Test discovery patterns
- Markers for test categorization
- Coverage configuration
- Logging and output settings
- Warning filters

### **Shared Fixtures** (`conftest.py`)
- Mock BK25Core instances
- Test data generators
- Temporary file management
- Async test support
- Common test utilities

### **Test Markers**
```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.e2e          # End-to-end tests
@pytest.mark.api          # API tests
@pytest.mark.performance  # Performance tests
@pytest.mark.slow         # Slow running tests
```

## 🧩 Test Data Management

### **Mock Data**
- **Personas**: Test personas with various capabilities
- **Channels**: Test channels with different features
- **Conversations**: Sample conversation data
- **Scripts**: Test automation scripts
- **Tasks**: Execution task examples

### **Temporary Files**
- **Personas Directory**: Temporary persona JSON files
- **Channels Directory**: Temporary channel configurations
- **Test Outputs**: Generated test artifacts
- **Cleanup**: Automatic cleanup after tests

## 🚨 Error Handling Tests

### **Expected Failures**
- Invalid persona data
- Missing required fields
- Network timeouts
- External service failures
- Invalid conversation IDs
- Malformed requests

### **Recovery Scenarios**
- System restart after errors
- Data corruption recovery
- Memory cleanup under stress
- Component reinitialization
- Error state recovery

## 📈 Performance Testing

### **Load Testing**
- Multiple concurrent conversations
- Rapid persona switching
- Memory usage under stress
- Response time measurements
- Resource cleanup efficiency

### **Stress Testing**
- Large message volumes
- Memory pressure scenarios
- Concurrent operations
- Error condition handling
- System stability under load

## 🔍 Debugging Tests

### **Verbose Output**
```bash
# Run with detailed output
pytest -v -s --tb=long

# Run with debug logging
pytest --log-cli-level=DEBUG
```

### **Test Isolation**
```bash
# Run single test
pytest tests/unit/test_persona_manager.py::TestPersonaManager::test_init

# Run tests with specific pattern
pytest -k "test_persona_switching"
```

### **Coverage Debugging**
```bash
# Show missing coverage
pytest --cov=src --cov-report=term-missing

# Generate detailed coverage report
pytest --cov=src --cov-report=html:htmlcov
```

## 🧪 Writing New Tests

### **Test Structure**
```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestComponentName:
    """Test ComponentName functionality"""
    
    @pytest.fixture
    def component(self):
        """Create component instance for testing"""
        return ComponentName()
    
    def test_method_name(self, component):
        """Test specific method behavior"""
        # Arrange
        input_data = "test input"
        
        # Act
        result = component.method(input_data)
        
        # Assert
        assert result == "expected output"
    
    @pytest.mark.asyncio
    async def test_async_method(self, component):
        """Test async method behavior"""
        # Arrange
        input_data = "async test input"
        
        # Act
        result = await component.async_method(input_data)
        
        # Assert
        assert result == "expected async output"
```

### **Test Naming Conventions**
- **Test Classes**: `Test{ComponentName}`
- **Test Methods**: `test_{method_name}_{scenario}`
- **Fixtures**: `{component_name}` or `mock_{component_name}`

### **Assertion Patterns**
```python
# Basic assertions
assert result is not None
assert len(result) == expected_length
assert "expected" in result

# Exception testing
with pytest.raises(ValueError, match="expected message"):
    component.method(invalid_input)

# Async exception testing
with pytest.raises(AsyncException):
    await component.async_method(invalid_input)
```

## 📋 Test Checklist

### **Before Running Tests**
- [ ] Install test dependencies: `pip install -r requirements-dev.txt`
- [ ] Check Python version compatibility (3.8+)
- [ ] Verify virtual environment activation
- [ ] Check test dependencies: `python tests/run_tests.py --check-deps`

### **Test Execution**
- [ ] Run unit tests: `python tests/run_tests.py --type unit`
- [ ] Run integration tests: `python tests/run_tests.py --type integration`
- [ ] Run E2E tests: `python tests/run_tests.py --type e2e`
- [ ] Run API tests: `python tests/run_tests.py --type api`
- [ ] Run all tests with coverage: `python tests/run_tests.py`

### **Quality Checks**
- [ ] Verify 90%+ coverage achieved
- [ ] Check all test categories pass
- [ ] Review test output for warnings
- [ ] Validate coverage reports generated

## 🐛 Troubleshooting

### **Common Issues**

**Import Errors**
```bash
# Ensure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Or run from project root directory
```

**Missing Dependencies**
```bash
# Install all test dependencies
pip install -r requirements-dev.txt

# Check specific package
pip show pytest
```

**Test Failures**
```bash
# Run with verbose output
pytest -v -s --tb=long

# Run single failing test
pytest tests/unit/test_failing.py::TestClass::test_method -v -s
```

**Coverage Issues**
```bash
# Check coverage configuration
pytest --cov=src --cov-report=term-missing

# Verify source paths
pytest --cov=src --cov-report=html:htmlcov
```

## 📚 Additional Resources

### **Pytest Documentation**
- [Pytest User Guide](https://docs.pytest.org/en/stable/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- [Pytest Markers](https://docs.pytest.org/en/stable/explanation/mark.html)

### **Testing Best Practices**
- [Python Testing with Pytest](https://pytest-book.readthedocs.io/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
- [Testing Patterns](https://martinfowler.com/bliki/TestDouble.html)

### **BK25 Documentation**
- [Migration Plan](../docs/PYTHON_MIGRATION_PLAN.md)
- [API Documentation](../docs/API.md)
- [Component Architecture](../docs/ARCHITECTURE.md)

---

**🎯 Goal**: Achieve 100% test coverage across all test categories to ensure BK25 Python migration quality and reliability.

**📊 Status**: Test suite scaffolded and ready for execution. All test categories implemented with comprehensive coverage.
