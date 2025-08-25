#!/usr/bin/env python3
"""
Unit tests for BK25 Configuration System
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from src.config import (
    LLMConfig, ServerConfig, PathConfig, DatabaseConfig, LoggingConfig,
    BK25Config, get_config, reload_config
)


class TestLLMConfig:
    """Test LLMConfig dataclass"""
    
    def test_default_values(self):
        """Test default values are set correctly"""
        config = LLMConfig()
        
        assert config.provider == "ollama"
        assert config.ollama_url == "http://localhost:11434"
        assert config.ollama_model == "llama3.1:8b"
        assert config.openai_api_key == ""
        assert config.openai_model == "gpt-4o"
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
        assert config.timeout == 60
    
    def test_custom_values(self):
        """Test custom values can be set"""
        config = LLMConfig(
            provider="openai",
            openai_api_key="test-key",
            temperature=0.5,
            max_tokens=1000
        )
        
        assert config.provider == "openai"
        assert config.openai_api_key == "test-key"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000


class TestServerConfig:
    """Test ServerConfig dataclass"""
    
    def test_default_values(self):
        """Test default values are set correctly"""
        config = ServerConfig()
        
        assert config.host == "0.0.0.0"
        assert config.port == 3003
        assert config.reload is True
        assert config.secret_key == "your-secret-key-here-change-this-in-production"
        assert config.cors_origins is None
    
    def test_custom_values(self):
        """Test custom values can be set"""
        config = ServerConfig(
            host="127.0.0.1",
            port=8080,
            reload=False,
            cors_origins=["http://localhost:3000"]
        )
        
        assert config.host == "127.0.0.1"
        assert config.port == 8080
        assert config.reload is False
        assert config.cors_origins == ["http://localhost:3000"]


class TestPathConfig:
    """Test PathConfig dataclass"""
    
    def test_default_values(self):
        """Test default values are set correctly"""
        config = PathConfig()
        
        assert config.base_dir == Path(".")
        assert config.data_dir == Path("./data")
        assert config.personas_path == Path("./data/personas")
        assert config.channels_path == Path("./data/channels")
        assert config.logs_path == Path("./logs")
        assert config.config_path == Path("./config")


class TestDatabaseConfig:
    """Test DatabaseConfig dataclass"""
    
    def test_default_values(self):
        """Test default values are set correctly"""
        config = DatabaseConfig()
        
        assert config.url == "sqlite:///./data/bk25.db"
        assert config.echo is False
    
    def test_custom_values(self):
        """Test custom values can be set"""
        config = DatabaseConfig(
            url="postgresql://user:pass@localhost/db",
            echo=True
        )
        
        assert config.url == "postgresql://user:pass@localhost/db"
        assert config.echo is True


class TestLoggingConfig:
    """Test LoggingConfig dataclass"""
    
    def test_default_values(self):
        """Test default values are set correctly"""
        config = LoggingConfig()
        
        assert config.level == "INFO"
        assert config.file == "./logs/bk25.log"
        assert "asctime" in config.format
        assert "name" in config.format
        assert "levelname" in config.format
        assert "message" in config.format


class TestBK25Config:
    """Test BK25Config class"""
    
    def test_init_defaults(self):
        """Test initialization with defaults"""
        config = BK25Config()
        
        assert isinstance(config.llm, LLMConfig)
        assert isinstance(config.server, ServerConfig)
        assert isinstance(config.paths, PathConfig)
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.logging, LoggingConfig)
    
    @patch('src.config.os.getenv')
    def test_load_environment_vars(self, mock_getenv):
        """Test loading configuration from environment variables"""
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'env-key',
            'OPENAI_MODEL': 'gpt-4',
            'BK25_PORT': '8080',
            'LLM_TEMPERATURE': '0.3',
            'LLM_MAX_TOKENS': '1500',
            'BK25_RELOAD': 'false'
        }.get(key, default)
        
        config = BK25Config()
        
        assert config.llm.provider == 'openai'
        assert config.llm.openai_api_key == 'env-key'
        assert config.llm.openai_model == 'gpt-4'
        assert config.server.port == 8080
        assert config.llm.temperature == 0.3
        assert config.llm.max_tokens == 1500
        assert config.server.reload is False
    
    @patch('src.config.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.config.json.load')
    def test_load_config_file(self, mock_json_load, mock_file, mock_exists):
        """Test loading configuration from JSON file"""
        mock_exists.return_value = True
        mock_json_load.return_value = {
            'llm': {
                'provider': 'anthropic',
                'anthropic_model': 'claude-3-opus'
            },
            'server': {
                'port': 9000
            }
        }
        
        config = BK25Config("test_config.json")
        
        assert config.llm.provider == 'anthropic'
        assert config.llm.anthropic_model == 'claude-3-opus'
        assert config.server.port == 9000
    
    @patch('src.config.Path.mkdir')
    def test_create_directories(self, mock_mkdir):
        """Test directory creation"""
        # Create config without calling _create_directories in constructor
        config = BK25Config.__new__(BK25Config)
        config.llm = LLMConfig()
        config.server = ServerConfig()
        config.paths = PathConfig()
        config.database = DatabaseConfig()
        config.logging = LoggingConfig()
        
        # Call _create_directories manually
        config._create_directories()
        
        # Should call mkdir for each directory
        assert mock_mkdir.call_count == 5
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.config.json.dump')
    def test_save_config(self, mock_json_dump, mock_file):
        """Test saving configuration to file"""
        config = BK25Config()
        config.save_config("test_save.json")
        
        mock_json_dump.assert_called_once()
        # Check that the config data structure is correct
        call_args = mock_json_dump.call_args[0]
        assert 'llm' in call_args[0]
        assert 'server' in call_args[0]
        assert 'database' in call_args[0]
        assert 'logging' in call_args[0]
    
    def test_get_llm_settings(self):
        """Test getting LLM settings as dictionary"""
        config = BK25Config()
        config.llm.provider = "openai"
        config.llm.openai_api_key = "test-key"
        config.llm.openai_model = "gpt-4"
        config.llm.temperature = 0.8
        
        settings = config.get_llm_settings()
        
        assert settings['provider'] == 'openai'
        assert settings['openai']['apiKey'] == 'test-key'
        assert settings['openai']['model'] == 'gpt-4'
        assert settings['temperature'] == 0.8
        assert 'ollama' in settings
        assert 'anthropic' in settings
        assert 'google' in settings
        assert 'custom' in settings
    
    def test_update_llm_settings(self):
        """Test updating LLM settings from API"""
        config = BK25Config()
        
        new_settings = {
            'provider': 'anthropic',
            'anthropic': {
                'apiKey': 'new-key',
                'model': 'claude-3-sonnet'
            },
            'temperature': 0.5,
            'maxTokens': 3000
        }
        
        config.update_llm_settings(new_settings)
        
        assert config.llm.provider == 'anthropic'
        assert config.llm.anthropic_api_key == 'new-key'
        assert config.llm.anthropic_model == 'claude-3-sonnet'
        assert config.llm.temperature == 0.5
        assert config.llm.max_tokens == 3000
    
    @patch('src.config.BK25Config.save_config')
    def test_update_llm_settings_saves_config(self, mock_save):
        """Test that updating settings calls save_config"""
        config = BK25Config()
        
        config.update_llm_settings({'provider': 'openai'})
        
        mock_save.assert_called_once()


class TestConfigFunctions:
    """Test convenience functions"""
    
    def test_get_config(self):
        """Test get_config function returns global instance"""
        from src.config import config as global_config
        config = get_config()
        
        assert config is global_config
    
    @patch('src.config.BK25Config')
    def test_reload_config(self, mock_config_class):
        """Test reload_config function creates new instance"""
        mock_instance = mock_config_class.return_value
        
        result = reload_config()
        
        mock_config_class.assert_called_once()
        assert result is mock_instance


class TestConfigIntegration:
    """Test configuration system integration"""
    
    @patch('src.config.os.getenv')
    def test_environment_override_file(self, mock_getenv):
        """Test that environment variables override file config"""
        mock_getenv.side_effect = lambda key, default=None: {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'env-override'
        }.get(key, default)
        
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                'llm': {
                    'provider': 'ollama',
                    'openai_api_key': 'file-value'
                }
            }, f)
            config_file = f.name
        
        try:
            config = BK25Config(config_file)
            
            # Environment should override file
            assert config.llm.provider == 'openai'
            assert config.llm.openai_api_key == 'env-override'
        finally:
            os.unlink(config_file)
    
    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from environment"""
        with patch.dict(os.environ, {
            'CORS_ORIGINS': '["http://localhost:3000", "https://example.com"]'
        }):
            config = BK25Config()
            assert config.server.cors_origins == ["http://localhost:3000", "https://example.com"]
        
        with patch.dict(os.environ, {
            'CORS_ORIGINS': 'http://localhost:3000'
        }):
            config = BK25Config()
            assert config.server.cors_origins == ["http://localhost:3000"]
    
    def test_numeric_environment_vars(self):
        """Test numeric environment variables are parsed correctly"""
        with patch.dict(os.environ, {
            'BK25_PORT': '5000',
            'LLM_TEMPERATURE': '0.2',
            'LLM_MAX_TOKENS': '5000',
            'LLM_TIMEOUT': '120'
        }):
            config = BK25Config()
            
            assert config.server.port == 5000
            assert config.llm.temperature == 0.2
            assert config.llm.max_tokens == 5000
            assert config.llm.timeout == 120
    
    def test_boolean_environment_vars(self):
        """Test boolean environment variables are parsed correctly"""
        with patch.dict(os.environ, {
            'BK25_RELOAD': 'false',
            'DATABASE_ECHO': 'true'
        }):
            config = BK25Config()
            
            assert config.server.reload is False
            assert config.database.echo is True
