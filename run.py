#!/usr/bin/env python3
"""
BK25 Startup Script

Simple script to start the BK25 Python application.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main startup function"""
    print("🚀 Starting BK25 Python Edition...")
    print("📝 Migration Status: Phase 1 - Foundation & Core Infrastructure")
    print("🔧 Setting up environment...")
    
    try:
        # Import and run the main application
        from src.main import app
        import uvicorn
        
        # Get configuration
        from src.config import config
        
        print(f"🌐 Server will start on {config.host}:{config.port}")
        print(f"📚 API documentation will be available at: http://{config.host}:{config.port}/docs")
        print(f"🔄 Reload mode: {'enabled' if config.reload else 'disabled'}")
        print(f"🏗️ Environment: {config.environment}")
        
        # Start the server
        uvicorn.run(
            "src.main:app",
            host=config.host,
            port=config.port,
            reload=config.reload,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed the required dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("💡 Check the logs for more details")
        sys.exit(1)

if __name__ == "__main__":
    main()
