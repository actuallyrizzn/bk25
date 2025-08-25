# BK25 Configuration Guide

This guide explains how to configure BK25 using environment variables, configuration files, or the web interface.

## Configuration Methods

BK25 supports three configuration methods (in order of priority):

1. **Environment Variables** (highest priority)
2. **Configuration Files** (JSON format)
3. **Web Interface Settings** (saved to config file)

## Quick Start

### 1. Copy the Example Configuration

```bash
cp config/bk25_config.json.example config/bk25_config.json
```

### 2. Edit the Configuration File

Modify `config/bk25_config.json` with your preferred settings.

### 3. Restart BK25

The server will automatically load the new configuration.

## Environment Variables

You can set these environment variables to override configuration file settings:

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BK25_HOST` | `0.0.0.0` | Host to bind the server to |
| `BK25_PORT` | `3003` | Port to bind the server to |
| `BK25_RELOAD` | `true` | Enable auto-reload for development |
| `SECRET_KEY` | `your-secret-key-here` | Secret key for security features |

### LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | LLM provider: `ollama`, `openai`, `anthropic`, `google`, `custom` |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1:8b` | Ollama model name |
| `OPENAI_API_KEY` | `` | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI model name |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI API base URL |
| `ANTHROPIC_API_KEY` | `` | Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet` | Anthropic model name |
| `ANTHROPIC_BASE_URL` | `https://api.anthropic.com` | Anthropic API base URL |
| `GOOGLE_API_KEY` | `` | Google API key |
| `GOOGLE_MODEL` | `gemini-1.5-pro` | Google model name |
| `CUSTOM_API_URL` | `` | Custom API endpoint URL |
| `CUSTOM_API_KEY` | `` | Custom API authentication key |
| `CUSTOM_MODEL` | `` | Custom API model parameter |
| `LLM_TEMPERATURE` | `0.7` | LLM creativity (0.0 = focused, 2.0 = creative) |
| `LLM_MAX_TOKENS` | `2000` | Maximum response length |
| `LLM_TIMEOUT` | `60` | Request timeout in seconds |

### Path Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BK25_BASE_DIR` | `.` | Base directory for BK25 |
| `DATA_PATH` | `./data` | Data storage directory |
| `PERSONAS_PATH` | `./data/personas` | Persona definitions directory |
| `CHANNELS_PATH` | `./data/channels` | Channel definitions directory |
| `LOGS_PATH` | `./logs` | Log files directory |
| `CONFIG_PATH` | `./config` | Configuration files directory |

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/bk25.db` | Database connection string |
| `DATABASE_ECHO` | `false` | Enable SQL query logging |

### Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | `./logs/bk25.log` | Log file path |
| `LOG_FORMAT` | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log message format |

### CORS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `["http://localhost:3000", "http://localhost:3003"]` | Allowed CORS origins (JSON array) |

## Configuration File Format

The configuration file uses JSON format with the following structure:

```json
{
  "llm": {
    "provider": "ollama",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama3.1:8b",
    "openai_api_key": "",
    "openai_model": "gpt-4o",
    "anthropic_api_key": "",
    "anthropic_model": "claude-3-5-sonnet",
    "google_api_key": "",
    "google_model": "gemini-1.5-pro",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 60
  },
  "server": {
    "host": "0.0.0.0",
    "port": 3003,
    "reload": true,
    "secret_key": "your-secret-key-here",
    "cors_origins": ["http://localhost:3000"]
  },
  "database": {
    "url": "sqlite:///./data/bk25.db",
    "echo": false
  },
  "logging": {
    "level": "INFO",
    "file": "./logs/bk25.log"
  }
}
```

## LLM Provider Examples

### Ollama (Local)

```json
{
  "llm": {
    "provider": "ollama",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama3.1:8b",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

### OpenAI

```json
{
  "llm": {
    "provider": "openai",
    "openai_api_key": "sk-your-api-key-here",
    "openai_model": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 4000
  }
}
```

### Anthropic (Claude)

```json
{
  "llm": {
    "provider": "anthropic",
    "anthropic_api_key": "sk-ant-your-api-key-here",
    "anthropic_model": "claude-3-5-sonnet",
    "temperature": 0.7,
    "max_tokens": 4000
  }
}
```

### Google (Gemini)

```json
{
  "llm": {
    "provider": "google",
    "google_api_key": "AIza-your-api-key-here",
    "google_model": "gemini-1.5-pro",
    "temperature": 0.7,
    "max_tokens": 4000
  }
}
```

### Custom API

```json
{
  "llm": {
    "provider": "custom",
    "custom_api_url": "https://api.example.com/v1",
    "custom_api_key": "your-api-key",
    "custom_model": "your-model-name",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

## Web Interface Configuration

You can also configure BK25 through the web interface:

1. Click the ⚙️ **Settings** button in the top-right corner
2. Select your preferred LLM provider
3. Enter your API keys and model settings
4. Click **Test Connection** to verify settings
5. Click **Save Settings** to persist the configuration

Settings changed through the web interface are automatically saved to the configuration file.

## Configuration File Locations

BK25 looks for configuration files in these locations (in order of priority):

1. `./config/bk25_config.json` (current directory)
2. `~/.bk25/config.json` (user home directory)
3. `/etc/bk25/config.json` (system-wide)

## Environment File Support

You can create a `.env` file in your project directory with environment variables:

```bash
# .env file
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
BK25_PORT=3003
```

**Note**: BK25 doesn't automatically load `.env` files. You need to use a tool like `python-dotenv` or source the file manually.

## Security Considerations

### API Keys

- **Never commit API keys to version control**
- Use environment variables or secure configuration files
- Consider using a secrets management service in production

### Server Configuration

- Change the default `SECRET_KEY` in production
- Restrict `CORS_ORIGINS` to trusted domains
- Use HTTPS in production environments

### File Permissions

- Ensure configuration files have appropriate permissions
- Don't make configuration files world-readable

## Troubleshooting

### Configuration Not Loading

1. Check file permissions
2. Verify JSON syntax
3. Check environment variable names
4. Restart the BK25 server

### Settings Not Persisting

1. Ensure the config directory is writable
2. Check for configuration file conflicts
3. Verify the configuration file path

### Environment Variables Not Working

1. Restart the terminal/process
2. Check variable names (case-sensitive)
3. Verify variable values
4. Check for typos

## Advanced Configuration

### Multiple Configuration Files

You can load multiple configuration files by specifying them in order:

```python
from src.config import BK25Config

# Load multiple config files
config = BK25Config("config/base.json")
config._load_config_file("config/override.json")
```

### Dynamic Configuration

You can update configuration at runtime:

```python
from src.config import get_config

config = get_config()
config.llm.provider = "openai"
config.llm.openai_api_key = "new-key"
config.save_config()
```

### Configuration Validation

The configuration system automatically validates:

- Required fields for each LLM provider
- Numeric ranges for parameters
- URL formats for API endpoints
- File path existence and permissions

## Support

For configuration issues:

1. Check the logs in `./logs/bk25.log`
2. Verify your configuration file syntax
3. Test with minimal configuration
4. Check the web interface for error messages
