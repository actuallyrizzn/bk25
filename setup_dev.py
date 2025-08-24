#!/usr/bin/env python3
"""
BK25 Development Setup Script

This script sets up the development environment for BK25.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔧 Creating virtual environment...")
    try:
        subprocess.run(["python", "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine the correct pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def run_tests():
    """Run basic tests to verify setup"""
    print("🧪 Running basic tests...")
    
    # Determine the correct python command based on OS
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "venv/bin/python"
    
    if not run_command(f"{python_cmd} tests/test_basic.py", "Running basic tests"):
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 BK25 Development Environment Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("⚠️  Tests failed, but setup completed. Check the issues above.")
    
    print("\n🎉 Development environment setup completed!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    
    print("2. Start the development server:")
    print("   python run.py")
    print("   or")
    print("   uvicorn src.main:app --reload --port 8000")
    
    print("\n📚 API documentation will be available at: http://localhost:8000/docs")
    print("🌐 Web interface will be available at: http://localhost:8000")

if __name__ == "__main__":
    main()
