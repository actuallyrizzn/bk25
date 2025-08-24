# BK25 Python Implementation Guide

## Quick Start

This guide provides step-by-step instructions for running and developing the Python port of BK25.

## Prerequisites

- Python 3.9+
- pip or poetry for package management
- Ollama running locally (for LLM functionality)

## Installation

### Option 1: Using pip
```bash
pip install -r requirements.txt
```

### Option 2: Using poetry (recommended)
```bash
poetry install
poetry shell
```

## Running the Application

### Development Mode
```bash
# Using uvicorn directly
uvicorn src.bk25.main:app --reload --host 0.0.0.0 --port 3000

# Or using the convenience script
python -m src.bk25.main
```

### Production Mode
```bash
uvicorn src.bk25.main:app --host 0.0.0.0 --port 3000
```

## Configuration

### Environment Variables
- `OLLAMA_URL`: Ollama API endpoint (default: http://localhost:11434)
- `BK25_MODEL`: LLM model to use (default: llama3.1:8b)
- `PORT`: Server port (default: 3000)
- `DEBUG`: Enable debug mode (default: False)

### Example .env file
```env
OLLAMA_URL=http://localhost:11434
BK25_MODEL=llama3.1:8b
PORT=3000
DEBUG=True
```

## API Endpoints

### Core Endpoints
- `GET /health` - Health check and system status
- `POST /api/chat` - Main conversation endpoint
- `GET /api/personas` - List available personas
- `POST /api/personas` - Create custom persona
- `GET /api/channels` - List available channels

### Request/Response Examples

#### Chat Endpoint
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate a PowerShell script to list all services",
    "persona": "technical-expert",
    "channel": "web",
    "platform": "powershell",
    "sessionId": "user123"
  }'
```

#### Health Check
```bash
curl http://localhost:3000/health
```

## Testing

### Running All Tests
```bash
# Using pytest
pytest

# With coverage
pytest --cov=src.bk25 --cov-report=html

# Using poetry
poetry run pytest
```

### Running Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end tests only
pytest tests/e2e/
```

### Test Configuration
Tests use pytest with the following plugins:
- `pytest-asyncio` for async test support
- `pytest-cov` for coverage reporting
- `pytest-mock` for mocking external dependencies

## Development Workflow

### Code Style
The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **mypy** for type checking

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/
```

### Pre-commit Hooks (Recommended)
```bash
pip install pre-commit
pre-commit install
```

## Project Structure Explained

```
src/bk25/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI application entry point
├── core/
│   ├── __init__.py
│   ├── bk25_core.py        # Main application logic
│   ├── persona_manager.py   # Persona system management
│   ├── channel_manager.py   # Channel simulation
│   └── memory.py           # Conversation memory
├── generators/
│   ├── __init__.py
│   ├── base.py             # Base generator class
│   ├── powershell.py       # PowerShell generation
│   ├── applescript.py      # AppleScript generation
│   └── bash.py             # Bash generation
├── api/
│   ├── __init__.py
│   └── routes.py           # FastAPI route definitions
└── models/
    ├── __init__.py
    ├── chat.py             # Chat request/response models
    ├── persona.py          # Persona data models
    └── channel.py          # Channel data models
```

## Key Components

### BK25Core (`core/bk25_core.py`)
Main application controller that orchestrates:
- Ollama API communication
- Persona management
- Channel simulation
- Memory persistence

### PersonaManager (`core/persona_manager.py`)
Handles:
- Loading persona definitions from JSON files
- Persona switching logic
- Custom persona creation and validation

### ChannelManager (`core/channel_manager.py`)
Manages:
- Channel-specific message formatting
- Artifact generation per channel
- Channel capability simulation

### Memory System (`core/memory.py`)
Provides:
- Conversation history storage (SQLite)
- Session management
- Context retrieval for LLM conversations

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama if not running
ollama serve
```

#### 2. Port Already in Use
```bash
# Check what's using port 3000
lsof -i :3000

# Use a different port
PORT=3001 uvicorn src.bk25.main:app --reload
```

#### 3. Import Errors
```bash
# Make sure you're in the correct directory
pwd  # Should show /path/to/bk25

# Install dependencies
pip install -r requirements.txt
```

#### 4. Database Issues
```bash
# Delete database to reset
rm -f conversations.db

# The app will recreate it on next run
```

### Debug Mode
Enable debug mode for detailed logging:
```bash
DEBUG=True uvicorn src.bk25.main:app --reload --log-level debug
```

## Contributing

### Adding New Generators
1. Create new generator in `src/bk25/generators/`
2. Inherit from `BaseGenerator`
3. Implement required methods
4. Add tests in `tests/unit/generators/`

### Adding New Personas
1. Create JSON file in `personas/` directory
2. Follow existing persona format
3. Add validation in `PersonaManager`
4. Test persona loading and behavior

### Adding New Channels
1. Add channel definition to `ChannelManager`
2. Implement channel-specific formatting
3. Add tests for new channel behavior
4. Update frontend channel selector

## Performance Optimization

### Database Optimization
- Use connection pooling for high-traffic scenarios
- Implement proper indexing for conversation queries
- Consider Redis for session caching

### API Optimization
- Enable FastAPI response caching
- Use async/await throughout
- Implement request rate limiting

### Memory Management
- Limit conversation history size
- Implement memory cleanup routines
- Use streaming responses for large outputs

## Deployment

### Docker Deployment
```bash
# Build image
docker build -t bk25-python .

# Run container
docker run -p 3000:3000 -e OLLAMA_URL=http://host.docker.internal:11434 bk25-python
```

### Production Considerations
- Use a production ASGI server (uvicorn with multiple workers)
- Set up proper logging and monitoring
- Configure reverse proxy (nginx/traefik)
- Set up SSL/TLS certificates
- Configure environment-specific settings

This guide should help developers quickly understand and work with the Python port of BK25.