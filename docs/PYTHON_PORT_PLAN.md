# BK25 Python Port Plan

## Overview
This document outlines the comprehensive plan for porting BK25 from Node.js to Python, maintaining all functionality while leveraging Python's ecosystem advantages.

## Original System Analysis

### Current Node.js Architecture
```
bk25/
├── src/
│   ├── core/
│   │   ├── bk25.js              # Main application controller
│   │   ├── persona-manager.js   # Persona system management
│   │   ├── channel-manager.js   # Channel simulation system
│   │   └── memory.js           # Conversation memory system
│   ├── generators/
│   │   ├── powershell.js       # PowerShell script generation
│   │   ├── applescript.js      # AppleScript generation
│   │   └── bash.js             # Bash script generation
│   └── index.js                # Server entry point
├── personas/                   # Persona definition files (JSON)
├── web/                       # Frontend web interface
└── docker/                    # Containerization configs
```

### Key Technologies Used
- **Runtime**: Node.js with ES modules
- **Web Framework**: Express.js
- **Database**: SQLite3
- **HTTP Client**: node-fetch
- **LLM Integration**: Ollama API
- **Frontend**: Vanilla HTML/CSS/JavaScript

## Python Port Architecture

### Target Python Structure
```
bk25/
├── src/
│   ├── bk25/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── bk25_core.py     # Main application controller
│   │   │   ├── persona_manager.py # Persona system management
│   │   │   ├── channel_manager.py # Channel simulation system
│   │   │   └── memory.py        # Conversation memory system
│   │   ├── generators/
│   │   │   ├── __init__.py
│   │   │   ├── powershell.py    # PowerShell script generation
│   │   │   ├── applescript.py   # AppleScript generation
│   │   │   └── bash.py          # Bash script generation
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py        # FastAPI routes
│   │   └── main.py              # Server entry point
├── personas/                    # Persona definition files (JSON)
├── web/                        # Frontend web interface (static)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── requirements.txt
├── pyproject.toml
└── README.md
```

### Technology Stack Mapping

| Node.js Component | Python Equivalent | Rationale |
|-------------------|-------------------|-----------|
| Express.js | FastAPI | Modern, fast, auto-docs, type hints |
| SQLite3 | SQLite3 (sqlite3 module) | Direct equivalent |
| node-fetch | httpx/aiohttp | Async HTTP client |
| ES Modules | Python packages | Native module system |
| JSON files | JSON files | Same format, Python json module |

## Phase-by-Phase Port Plan

### Phase 1: Project Setup and Dependencies
1. **Create Python package structure**
   - Set up proper `__init__.py` files
   - Create `pyproject.toml` for modern Python packaging
   - Create `requirements.txt` for dependencies

2. **Dependencies mapping**:
   ```
   express -> fastapi + uvicorn
   cors -> fastapi-cors (built-in)
   sqlite3 -> sqlite3 (built-in)
   node-fetch -> httpx
   ```

### Phase 2: Core System Port
1. **Memory System** (`memory.py`)
   - Port conversation memory management
   - SQLite database operations
   - Session management

2. **Persona Manager** (`persona_manager.py`)
   - JSON persona loading
   - Persona switching logic
   - Custom persona creation

3. **Channel Manager** (`channel_manager.py`)
   - Channel simulation system
   - Message formatting per channel
   - Artifact generation

4. **Main BK25 Core** (`bk25_core.py`)
   - Ollama API integration
   - Core conversation logic
   - System orchestration

### Phase 3: Code Generators Port
1. **PowerShell Generator** (`powershell.py`)
   - Template-based script generation
   - Windows automation patterns

2. **AppleScript Generator** (`applescript.py`)
   - macOS automation scripts
   - Application integration

3. **Bash Generator** (`bash.py`)
   - Linux/Unix shell scripts
   - System automation

### Phase 4: Web Framework Implementation
1. **FastAPI Server** (`main.py`)
   - API endpoint definitions
   - Static file serving
   - CORS configuration

2. **Routes Implementation** (`api/routes.py`)
   - Chat API endpoint
   - Health check
   - Persona management endpoints
   - Channel switching endpoints

### Phase 5: Testing Suite Implementation
1. **Unit Tests**
   - Test each module in isolation
   - Mock external dependencies (Ollama API)
   - Test persona loading and switching
   - Test code generation logic

2. **Integration Tests**
   - Test API endpoints
   - Test database operations
   - Test full conversation flows

3. **End-to-End Tests**
   - Test complete user workflows
   - Test web interface integration
   - Test code generation pipeline

## Key Considerations

### 1. Async/Await Patterns
- **Node.js**: Uses promises and async/await
- **Python**: Use `asyncio` and `async`/`await` for FastAPI compatibility

### 2. Error Handling
- **Node.js**: Try/catch with promises
- **Python**: Try/except with proper exception types

### 3. Environment Configuration
- **Node.js**: `process.env`
- **Python**: `os.environ` or `pydantic` settings

### 4. File System Operations
- **Node.js**: `fs` module and `path`
- **Python**: `pathlib` and `os` modules

### 5. JSON Handling
- **Node.js**: Native JSON support
- **Python**: `json` module (very similar)

## Implementation Strategy

### 1. Direct Port Approach
- Maintain exact same functionality
- Keep same API endpoints
- Preserve persona system exactly
- Maintain web interface compatibility

### 2. Python Best Practices
- Use type hints throughout
- Follow PEP 8 style guidelines
- Use proper exception handling
- Implement proper logging

### 3. Testing Strategy
- Test-driven development for new code
- Comprehensive test coverage (>90%)
- Mock external dependencies
- Integration tests for API endpoints

## Success Criteria

1. **Functional Parity**: All original features work identically
2. **API Compatibility**: Same REST API endpoints and responses
3. **Performance**: Equal or better response times
4. **Test Coverage**: >90% test coverage with all tests passing
5. **Documentation**: Complete documentation for new Python implementation

## Timeline Estimate

1. **Phase 1** (Setup): 30 minutes
2. **Phase 2** (Core): 2 hours
3. **Phase 3** (Generators): 1 hour
4. **Phase 4** (Web Framework): 1 hour
5. **Phase 5** (Testing): 2 hours
6. **Bug fixes and iteration**: 1 hour

**Total Estimated Time**: ~7-8 hours

## Dependencies Required

```toml
[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.104.1"
uvicorn = "^0.24.0"
httpx = "^0.25.0"
pydantic = "^2.5.0"
python-multipart = "^0.0.6"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
black = "^23.11.0"
isort = "^5.12.0"
mypy = "^1.7.1"
```

This plan ensures a systematic, thorough port while maintaining all functionality and adding robust testing.