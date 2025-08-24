"""
Basic tests for BK25 Python setup

These tests verify that the basic Python infrastructure is working.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test that basic modules can be imported"""
    try:
        from config import BK25Config, config
        from logging_config import setup_logging, get_logger
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import basic modules: {e}")

def test_config_creation():
    """Test that configuration can be created"""
    try:
        from config import BK25Config
        config = BK25Config()
        assert config.port == 8000
        assert config.host == "0.0.0.0"
        assert config.ollama_url == "http://localhost:11434"
    except Exception as e:
        pytest.fail(f"Failed to create configuration: {e}")

def test_logging_setup():
    """Test that logging can be set up"""
    try:
        from logging_config import setup_logging
        logger = setup_logging(log_level="INFO")
        assert logger is not None
        assert logger.level == 20  # INFO level
    except Exception as e:
        pytest.fail(f"Failed to set up logging: {e}")

def test_paths_exist():
    """Test that necessary directories exist"""
    base_path = Path(__file__).parent.parent
    assert base_path.exists()
    assert (base_path / "src").exists()
    assert (base_path / "docs").exists()
    assert (base_path / "old").exists()

if __name__ == "__main__":
    # Run basic tests
    print("Running basic BK25 Python setup tests...")
    
    try:
        test_imports()
        print("✅ Import tests passed")
        
        test_config_creation()
        print("✅ Configuration tests passed")
        
        test_logging_setup()
        print("✅ Logging tests passed")
        
        test_paths_exist()
        print("✅ Path tests passed")
        
        print("\n🎉 All basic tests passed! BK25 Python setup is working.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
