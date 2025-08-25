#!/usr/bin/env python3
"""
Simple test runner for BK25
"""

import sys
import subprocess
import os

def main():
    """Run tests with appropriate arguments"""
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("pytest not found. Installing development dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "archive/testing/requirements-dev.txt"])
        import pytest
    
    # Default to running all tests
    if len(sys.argv) == 1:
        print("Running all tests...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
    else:
        # Pass through any arguments to pytest
        subprocess.run([sys.executable, "-m", "pytest"] + sys.argv[1:])

if __name__ == "__main__":
    main()
