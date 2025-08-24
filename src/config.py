"""
BK25 Configuration Module

Centralized configuration management for the BK25 system.
"""

import os
from typing import Optional
from pathlib import Path

class BK25Config:
    """Configuration class for BK25 system settings"""
    
    def __init__(self):
        # Server configuration
        self.host: str = os.getenv("BK25_HOST", "0.0.0.0")
        self.port: int = int(os.getenv("BK25_PORT", "8000"))
        self.reload: bool = os.getenv("BK25_RELOAD", "false").lower() == "true"
        
        # LLM configuration
        self.ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model: str = os.getenv("BK25_MODEL", "llama3.1:8b")
        self.temperature: float = float(os.getenv("BK25_TEMPERATURE", "0.1"))
        self.max_tokens: int = int(os.getenv("BK25_MAX_TOKENS", "2048"))
        
        # Paths
        self.base_path: Path = Path(__file__).parent.parent
        self.personas_path: Path = self.base_path / "personas"
        self.web_path: Path = self.base_path / "web"
        self.data_path: Path = self.base_path / "data"
        
        # Feature flags
        self.enable_analytics: bool = os.getenv("BK25_ENABLE_ANALYTICS", "false").lower() == "true"
        self.enable_auth: bool = os.getenv("BK25_ENABLE_AUTH", "false").lower() == "true"
        
        # Environment
        self.environment: str = os.getenv("BK25_ENV", "development")
        self.debug: bool = self.environment == "development"
        
        # Create necessary directories
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure necessary directories exist"""
        self.data_path.mkdir(exist_ok=True)
        (self.data_path / "logs").mkdir(exist_ok=True)
        (self.data_path / "conversations").mkdir(exist_ok=True)
    
    def get_ollama_config(self) -> dict:
        """Get Ollama configuration"""
        return {
            "url": self.ollama_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    def get_server_config(self) -> dict:
        """Get server configuration"""
        return {
            "host": self.host,
            "port": self.port,
            "reload": self.reload,
            "debug": self.debug
        }
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == "development"

# Global configuration instance
config = BK25Config()
