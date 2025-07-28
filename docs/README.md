# Documentation

This directory contains comprehensive documentation for BK25.

## Structure

```
docs/
├── api/            # API reference documentation
├── guides/         # User guides and tutorials
├── architecture/   # System architecture documentation
├── personas/       # Persona creation and management guides
├── channels/       # Channel-specific documentation
├── deployment/     # Deployment and configuration guides
└── examples/       # Code examples and use cases
```

## Documentation Categories

### API Reference (`api/`)
- REST API endpoints
- Request/response schemas
- Authentication methods
- Error handling

### User Guides (`guides/`)
- Getting started tutorial
- Persona creation guide
- Channel configuration
- Code generation workflows

### Architecture (`architecture/`)
- System design overview
- Component relationships
- Data flow diagrams
- Extension points

### Personas (`personas/`)
- Built-in persona documentation
- Custom persona creation
- Persona configuration reference
- Best practices

### Channels (`channels/`)
- Channel-specific features
- Artifact generation guides
- Integration examples
- Platform limitations

### Deployment (`deployment/`)
- Installation instructions
- Configuration options
- Docker deployment
- Production considerations

### Examples (`examples/`)
- Sample conversations
- Generated automation scripts
- Integration examples
- Use case scenarios

## Contributing to Documentation

When adding documentation:
- Use clear, concise language
- Include code examples where relevant
- Keep documentation up-to-date with code changes
- Follow the established structure and formatting
- Test all code examples before committing

## Building Documentation

```bash
# Generate API documentation
npm run docs:api

# Build user guides
npm run docs:build

# Serve documentation locally
npm run docs:serve
