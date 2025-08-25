#!/usr/bin/env python3
"""
Integration tests for BK25 Configuration System
Tests the interaction between configuration, API endpoints, and web interface
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from fastapi.testclient import TestClient
from src.main import app
from src.config import BK25Config, config


class TestConfigurationIntegration:
    """Test configuration system integration"""
    
    def test_config_initialization(self):
        """Test that configuration is properly initialized on app startup"""
        # Create a fresh config instance to avoid interference from other tests
        with patch.dict(os.environ, {}, clear=True):
            test_config = BK25Config()
            
            # Check that config is properly initialized
            assert test_config is not None
            assert hasattr(test_config, 'llm')
            assert hasattr(test_config, 'server')
            assert hasattr(test_config, 'paths')
            
            # Check default values
            assert test_config.llm.provider == "ollama"
            assert test_config.server.port == 3003
            assert test_config.server.reload is True
    
    def test_config_directory_creation(self):
        """Test that configuration creates necessary directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a config in a temporary directory
            config_path = Path(temp_dir) / "test_config"
            config_path.mkdir()
            
            # Initialize config with temp directory
            test_config = BK25Config()
            test_config.paths.base_dir = Path(temp_dir)
            test_config.paths.data_dir = Path(temp_dir) / "data"
            test_config.paths.personas_path = Path(temp_dir) / "data" / "personas"
            test_config.paths.channels_path = Path(temp_dir) / "data" / "channels"
            test_config.paths.logs_path = Path(temp_dir) / "logs"
            test_config.paths.config_path = Path(temp_dir) / "config"
            
            # Create directories
            test_config._create_directories()
            
            # Check directories were created
            assert (Path(temp_dir) / "data").exists()
            assert (Path(temp_dir) / "data" / "personas").exists()
            assert (Path(temp_dir) / "data" / "channels").exists()
            assert (Path(temp_dir) / "logs").exists()
            assert (Path(temp_dir) / "config").exists()
    
    def test_config_file_loading(self):
        """Test configuration loading from JSON file"""
        config_data = {
            'llm': {
                'provider': 'openai',
                'openai_api_key': 'file-key',
                'openai_model': 'gpt-4'
            },
            'server': {
                'port': 9000,
                'host': '127.0.0.1'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            test_config = BK25Config(config_file)
            
            # Check that file config was loaded
            assert test_config.llm.provider == 'openai'
            assert test_config.llm.openai_api_key == 'file-key'
            assert test_config.llm.openai_model == 'gpt-4'
            assert test_config.server.port == 9000
            assert test_config.server.host == '127.0.0.1'
        finally:
            os.unlink(config_file)
    
    def test_environment_override_file(self):
        """Test that environment variables override file configuration"""
        config_data = {
            'llm': {
                'provider': 'ollama',
                'ollama_model': 'file-model'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            with patch.dict(os.environ, {
                'LLM_PROVIDER': 'openai',
                'OLLAMA_MODEL': 'env-model'
            }):
                test_config = BK25Config(config_file)
                
                # Environment should override file
                assert test_config.llm.provider == 'openai'
                # Environment should also override ollama_model since OLLAMA_MODEL was set
                assert test_config.llm.ollama_model == 'env-model'
        finally:
            os.unlink(config_file)
    
    def test_config_save_and_reload(self):
        """Test configuration saving and reloading"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            
            # Create initial config
            test_config = BK25Config()
            test_config.llm.provider = "anthropic"
            test_config.llm.anthropic_api_key = "save-test-key"
            
            # Save config
            test_config.save_config(str(config_file))
            
            # Verify file was created
            assert config_file.exists()
            
            # Load config from file
            loaded_config = BK25Config(str(config_file))
            
            # Verify settings were saved
            assert loaded_config.llm.provider == "anthropic"
            assert loaded_config.llm.anthropic_api_key == "save-test-key"
    
    def test_llm_settings_api_format(self):
        """Test that LLM settings API returns correct format"""
        test_config = BK25Config()
        test_config.llm.provider = "openai"
        test_config.llm.openai_api_key = "api-test-key"
        test_config.llm.openai_model = "gpt-4"
        test_config.llm.temperature = 0.6
        
        settings = test_config.get_llm_settings()
        
        # Check structure
        assert "provider" in settings
        assert "openai" in settings
        assert "temperature" in settings
        assert "maxTokens" in settings
        assert "timeout" in settings
        
        # Check values
        assert settings["provider"] == "openai"
        assert settings["openai"]["apiKey"] == "api-test-key"
        assert settings["openai"]["model"] == "gpt-4"
        assert settings["temperature"] == 0.6
        
        # Check all providers are present
        assert "ollama" in settings
        assert "anthropic" in settings
        assert "google" in settings
        assert "custom" in settings
    
    def test_llm_settings_update(self):
        """Test updating LLM settings from API format"""
        test_config = BK25Config()
        
        # Initial state
        assert test_config.llm.provider == "ollama"
        assert test_config.llm.openai_api_key == ""
        
        # Update settings
        new_settings = {
            'provider': 'google',
            'google': {
                'apiKey': 'google-test-key',
                'model': 'gemini-1.5-pro'
            },
            'temperature': 0.4,
            'maxTokens': 4000
        }
        
        test_config.update_llm_settings(new_settings)
        
        # Verify updates
        assert test_config.llm.provider == 'google'
        assert test_config.llm.google_api_key == 'google-test-key'
        assert test_config.llm.google_model == 'gemini-1.5-pro'
        assert test_config.llm.temperature == 0.4
        assert test_config.llm.max_tokens == 4000
        
        # Verify other providers weren't affected
        assert test_config.llm.openai_api_key == ""
        assert test_config.llm.ollama_url == "http://localhost:11434"
    
    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from environment"""
        # Test JSON array format
        with patch.dict(os.environ, {
            'CORS_ORIGINS': '["http://localhost:3000", "https://example.com"]'
        }):
            test_config = BK25Config()
            assert test_config.server.cors_origins == ["http://localhost:3000", "https://example.com"]
        
        # Test single string format
        with patch.dict(os.environ, {
            'CORS_ORIGINS': 'http://localhost:3000'
        }):
            test_config = BK25Config()
            assert test_config.server.cors_origins == ["http://localhost:3000"]
        
        # Test invalid JSON (should fall back to single string)
        with patch.dict(os.environ, {
            'CORS_ORIGINS': 'invalid-json'
        }):
            test_config = BK25Config()
            assert test_config.server.cors_origins == ["invalid-json"]
    
    def test_numeric_environment_parsing(self):
        """Test numeric environment variables are parsed correctly"""
        with patch.dict(os.environ, {
            'BK25_PORT': '5000',
            'LLM_TEMPERATURE': '0.2',
            'LLM_MAX_TOKENS': '5000',
            'LLM_TIMEOUT': '120'
        }):
            test_config = BK25Config()
            
            assert test_config.server.port == 5000
            assert test_config.llm.temperature == 0.2
            assert test_config.llm.max_tokens == 5000
            assert test_config.llm.timeout == 120
    
    def test_boolean_environment_parsing(self):
        """Test boolean environment variables are parsed correctly"""
        with patch.dict(os.environ, {
            'BK25_RELOAD': 'false',
            'DATABASE_ECHO': 'true'
        }):
            test_config = BK25Config()
            
            assert test_config.server.reload is False
            assert test_config.database.echo is True
        
        # Test default values when not set
        with patch.dict(os.environ, {}, clear=True):
            test_config = BK25Config()
            
            assert test_config.server.reload is True
            assert test_config.database.echo is False


class TestConfigurationWebInterface:
    """Test configuration integration with web interface"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_web_interface_config_access(self, client):
        """Test that web interface can access configuration"""
        # Test root route serves web interface
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Test app redirect
        response = client.get("/app")
        assert response.status_code == 200
        
        # Test info endpoint
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
    
    def test_settings_modal_integration(self, client):
        """Test that settings modal is properly integrated in web interface"""
        response = client.get("/")
        assert response.status_code == 200
        
        html_content = response.text
        
        # Check that settings button is present
        assert "settings-btn" in html_content
        
        # Check that settings modal is present
        assert "settings-modal" in html_content
        
        # Check that all provider options are present
        assert "ollama" in html_content
        assert "openai" in html_content
        assert "anthropic" in html_content
        assert "google" in html_content
        assert "custom" in html_content
        
        # Check that advanced settings are present
        assert "temperature" in html_content
        assert "maxTokens" in html_content
        assert "timeout" in html_content
    
    def test_configuration_persistence_across_sessions(self, client):
        """Test that configuration persists across different test sessions"""
        # Set configuration in first session
        settings = {
            "provider": "openai",
            "openai": {
                "apiKey": "persist-session-key",
                "model": "gpt-4"
            }
        }
        
        response = client.post("/api/settings", json=settings)
        assert response.status_code == 200
        
        # Verify settings were saved
        response = client.get("/api/settings")
        assert response.status_code == 200
        
        data = response.json()
        assert data["provider"] == "openai"
        assert data["openai"]["apiKey"] == "persist-session-key"
        
        # Create new client (simulating new session)
        new_client = TestClient(app)
        
        # Verify settings are still available
        response = new_client.get("/api/settings")
        assert response.status_code == 200
        
        data = response.json()
        assert data["provider"] == "openai"
        assert data["openai"]["apiKey"] == "persist-session-key"


class TestConfigurationErrorHandling:
    """Test configuration system error handling"""
    
    def test_invalid_config_file(self):
        """Test handling of invalid configuration file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_file = f.name
        
        try:
            # Should not raise exception, just log warning
            test_config = BK25Config(config_file)
            
            # Should fall back to defaults
            assert test_config.llm.provider == "ollama"
            assert test_config.server.port == 3003
        finally:
            os.unlink(config_file)
    
    def test_missing_config_file(self):
        """Test handling of missing configuration file"""
        # Should not raise exception
        test_config = BK25Config("nonexistent_file.json")
        
        # Should use defaults
        assert test_config.llm.provider == "ollama"
        assert test_config.server.port == 3003
    
    def test_invalid_environment_values(self):
        """Test handling of invalid environment variable values"""
        with patch.dict(os.environ, {
            'BK25_PORT': 'invalid-port',
            'LLM_TEMPERATURE': 'invalid-temp',
            'LLM_MAX_TOKENS': 'invalid-tokens'
        }):
            # Should not raise exception, should use defaults
            test_config = BK25Config()
            
            assert test_config.server.port == 3003
            assert test_config.llm.temperature == 0.7
            assert test_config.llm.max_tokens == 2000
    
    def test_config_file_permission_errors(self):
        """Test handling of file permission errors"""
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            # Should not raise exception, just log warning
            test_config = BK25Config("test_config.json")
            
            # Should use defaults
            assert test_config.llm.provider == "ollama"
            assert test_config.server.port == 3003
    
    def test_directory_creation_errors(self):
        """Test handling of directory creation errors"""
        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            # Should not raise exception, just log warning
            test_config = BK25Config()
            
            # Should continue with defaults
            assert test_config.llm.provider == "ollama"
            assert test_config.server.port == 3003
