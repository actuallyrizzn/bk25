#!/usr/bin/env python3
"""
BK25 Configuration Management
Loads configuration from environment variables and config files
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class LLMConfig:
    """LLM Provider Configuration"""
    provider: str = "ollama"
    
    # Ollama settings
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    
    # OpenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = "https://api.openai.com/v1"
    
    # Anthropic settings
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet"
    anthropic_base_url: str = "https://api.anthropic.com"
    
    # Google settings
    google_api_key: str = ""
    google_model: str = "gemini-1.5-pro"
    
    # Custom API settings
    custom_api_url: str = ""
    custom_api_key: str = ""
    custom_model: str = ""
    
    # LLM parameters
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60

@dataclass
class ServerConfig:
    """Server Configuration"""
    host: str = "0.0.0.0"
    port: int = 3003
    reload: bool = True
    secret_key: str = "your-secret-key-here-change-this-in-production"
    cors_origins: list = None

@dataclass
class PathConfig:
    """File Path Configuration"""
    base_dir: Path = Path(".")
    data_dir: Path = Path("./data")
    personas_path: Path = Path("./data/personas")
    channels_path: Path = Path("./data/channels")
    logs_path: Path = Path("./logs")
    config_path: Path = Path("./config")

@dataclass
class DatabaseConfig:
    """Database Configuration"""
    url: str = "sqlite:///./data/bk25.db"
    echo: bool = False

@dataclass
class LoggingConfig:
    """Logging Configuration"""
    level: str = "INFO"
    file: str = "./logs/bk25.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class BK25Config:
    """Main configuration class for BK25"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.llm = LLMConfig()
        self.server = ServerConfig()
        self.paths = PathConfig()
        self.database = DatabaseConfig()
        self.logging = LoggingConfig()
        
        # Load configuration
        if config_file:
            self._load_config_file(config_file)
        self._load_environment_vars()  # Environment variables override file config
        self._create_directories()
    
    def _load_environment_vars(self):
        """Load configuration from environment variables"""
        
        # LLM Configuration
        self.llm.provider = os.getenv("LLM_PROVIDER", self.llm.provider)
        self.llm.ollama_url = os.getenv("OLLAMA_URL", self.llm.ollama_url)
        self.llm.ollama_model = os.getenv("OLLAMA_MODEL", self.llm.ollama_model)
        self.llm.openai_api_key = os.getenv("OPENAI_API_KEY", self.llm.openai_api_key)
        self.llm.openai_model = os.getenv("OPENAI_MODEL", self.llm.openai_model)
        self.llm.openai_base_url = os.getenv("OPENAI_BASE_URL", self.llm.openai_base_url)
        self.llm.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", self.llm.anthropic_api_key)
        self.llm.anthropic_model = os.getenv("ANTHROPIC_MODEL", self.llm.anthropic_model)
        self.llm.anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL", self.llm.anthropic_base_url)
        self.llm.google_api_key = os.getenv("GOOGLE_API_KEY", self.llm.google_api_key)
        self.llm.google_model = os.getenv("GOOGLE_MODEL", self.llm.google_model)
        self.llm.custom_api_url = os.getenv("CUSTOM_API_URL", self.llm.custom_api_url)
        self.llm.custom_api_key = os.getenv("CUSTOM_API_KEY", self.llm.custom_api_key)
        self.llm.custom_model = os.getenv("CUSTOM_MODEL", self.llm.custom_model)
        
        # LLM Parameters
        if os.getenv("LLM_TEMPERATURE"):
            try:
                self.llm.temperature = float(os.getenv("LLM_TEMPERATURE"))
            except ValueError:
                print(f"[CONFIG] Warning: Invalid LLM_TEMPERATURE value, using default: {self.llm.temperature}")
        if os.getenv("LLM_MAX_TOKENS"):
            try:
                self.llm.max_tokens = int(os.getenv("LLM_MAX_TOKENS"))
            except ValueError:
                print(f"[CONFIG] Warning: Invalid LLM_MAX_TOKENS value, using default: {self.llm.max_tokens}")
        if os.getenv("LLM_TIMEOUT"):
            try:
                self.llm.timeout = int(os.getenv("LLM_TIMEOUT"))
            except ValueError:
                print(f"[CONFIG] Warning: Invalid LLM_TIMEOUT value, using default: {self.llm.timeout}")
        
        # Server Configuration
        self.server.host = os.getenv("BK25_HOST", self.server.host)
        if os.getenv("BK25_PORT"):
            try:
                self.server.port = int(os.getenv("BK25_PORT"))
            except ValueError:
                print(f"[CONFIG] Warning: Invalid BK25_PORT value, using default: {self.server.port}")
        self.server.reload = os.getenv("BK25_RELOAD", "true").lower() == "true"
        self.server.secret_key = os.getenv("SECRET_KEY", self.server.secret_key)
        
        # CORS Origins
        cors_origins = os.getenv("CORS_ORIGINS")
        if cors_origins:
            try:
                self.server.cors_origins = json.loads(cors_origins)
            except json.JSONDecodeError:
                self.server.cors_origins = [cors_origins]
        
        # Path Configuration
        if os.getenv("BK25_BASE_DIR"):
            self.paths.base_dir = Path(os.getenv("BK25_BASE_DIR"))
        if os.getenv("DATA_PATH"):
            self.paths.data_dir = Path(os.getenv("DATA_PATH"))
        if os.getenv("PERSONAS_PATH"):
            self.paths.personas_path = Path(os.getenv("PERSONAS_PATH"))
        if os.getenv("CHANNELS_PATH"):
            self.paths.channels_path = Path(os.getenv("CHANNELS_PATH"))
        if os.getenv("LOGS_PATH"):
            self.paths.logs_path = Path(os.getenv("LOGS_PATH"))
        if os.getenv("CONFIG_PATH"):
            self.paths.config_path = Path(os.getenv("CONFIG_PATH"))
        
        # Database Configuration
        self.database.url = os.getenv("DATABASE_URL", self.database.url)
        self.database.echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        
        # Logging Configuration
        self.logging.level = os.getenv("LOG_LEVEL", self.logging.level)
        self.logging.file = os.getenv("LOG_FILE", self.logging.file)
        self.logging.format = os.getenv("LOG_FORMAT", self.logging.format)
    
    def _load_config_file(self, config_file: str):
        """Load configuration from a JSON file"""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update LLM config
                if 'llm' in config_data:
                    for key, value in config_data['llm'].items():
                        if hasattr(self.llm, key):
                            setattr(self.llm, key, value)
                
                # Update server config
                if 'server' in config_data:
                    for key, value in config_data['server'].items():
                        if hasattr(self.server, key):
                            setattr(self.server, key, value)
                
                # Update other configs as needed
                if 'database' in config_data:
                    for key, value in config_data['database'].items():
                        if hasattr(self.database, key):
                            setattr(self.database, key, value)
                
                print(f"[CONFIG] Loaded configuration from {config_file}")
        except Exception as e:
            print(f"[CONFIG] Warning: Could not load config file {config_file}: {e}")
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.paths.data_dir,
            self.paths.personas_path,
            self.paths.channels_path,
            self.paths.logs_path,
            self.paths.config_path
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"[CONFIG] Warning: Could not create directory {directory}: {e}")
                # Continue with other directories
    
    def save_config(self, config_file: str = None):
        """Save current configuration to a file"""
        if not config_file:
            config_file = self.paths.config_path / "bk25_config.json"
        
        config_data = {
            'llm': asdict(self.llm),
            'server': asdict(self.server),
            'database': asdict(self.database),
            'logging': asdict(self.logging)
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            print(f"[CONFIG] Configuration saved to {config_file}")
        except Exception as e:
            print(f"[CONFIG] Error saving configuration: {e}")
    
    def get_llm_settings(self) -> Dict[str, Any]:
        """Get LLM settings as a dictionary for the API"""
        return {
            "provider": self.llm.provider,
            "ollama": {
                "url": self.llm.ollama_url,
                "model": self.llm.ollama_model
            },
            "openai": {
                "apiKey": self.llm.openai_api_key,
                "model": self.llm.openai_model,
                "baseUrl": self.llm.openai_base_url
            },
            "anthropic": {
                "apiKey": self.llm.anthropic_api_key,
                "model": self.llm.anthropic_model,
                "baseUrl": self.llm.anthropic_base_url
            },
            "google": {
                "apiKey": self.llm.google_api_key,
                "model": self.llm.google_model
            },
            "custom": {
                "url": self.llm.custom_api_url,
                "apiKey": self.llm.custom_api_key,
                "model": self.llm.custom_model
            },
            "temperature": self.llm.temperature,
            "maxTokens": self.llm.max_tokens,
            "timeout": self.llm.timeout
        }
    
    def update_llm_settings(self, settings: Dict[str, Any]):
        """Update LLM settings from API"""
        if 'provider' in settings:
            self.llm.provider = settings['provider']
        
        if 'ollama' in settings:
            ollama = settings['ollama']
            if 'url' in ollama:
                self.llm.ollama_url = ollama['url']
            if 'model' in ollama:
                self.llm.ollama_model = ollama['model']
        
        if 'openai' in settings:
            openai = settings['openai']
            if 'apiKey' in openai:
                self.llm.openai_api_key = openai['apiKey']
            if 'model' in openai:
                self.llm.openai_model = openai['model']
            if 'baseUrl' in openai:
                self.llm.openai_base_url = openai['baseUrl']
        
        if 'anthropic' in settings:
            anthropic = settings['anthropic']
            if 'apiKey' in anthropic:
                self.llm.anthropic_api_key = anthropic['apiKey']
            if 'model' in anthropic:
                self.llm.anthropic_model = anthropic['model']
            if 'baseUrl' in anthropic:
                self.llm.anthropic_base_url = anthropic['baseUrl']
        
        if 'google' in settings:
            google = settings['google']
            if 'apiKey' in google:
                self.llm.google_api_key = google['apiKey']
            if 'model' in google:
                self.llm.google_model = google['model']
        
        if 'custom' in settings:
            custom = settings['custom']
            if 'url' in custom:
                self.llm.custom_api_url = custom['url']
            if 'apiKey' in custom:
                self.llm.custom_api_key = custom['apiKey']
            if 'model' in custom:
                self.llm.custom_model = custom['model']
        
        if 'temperature' in settings:
            self.llm.temperature = float(settings['temperature'])
        if 'maxTokens' in settings:
            self.llm.max_tokens = int(settings['maxTokens'])
        if 'timeout' in settings:
            self.llm.timeout = int(settings['timeout'])
        
        # Save configuration
        self.save_config()

# Global configuration instance
config = BK25Config()

# Convenience functions
def get_config() -> BK25Config:
    """Get the global configuration instance"""
    return config

def reload_config():
    """Reload configuration from environment and files"""
    global config
    config = BK25Config()
    return config
