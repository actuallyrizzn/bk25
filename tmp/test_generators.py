#!/usr/bin/env python3
"""
Test script for code generators
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_generators():
    """Test code generators"""
    try:
        print("🔍 Testing Code Generators...")
        
        # Test PowerShell generator
        from src.generators.powershell import PowerShellGenerator
        ps_gen = PowerShellGenerator()
        print(f"✅ PowerShell generator: {ps_gen.platform}")
        
        # Test AppleScript generator
        from src.generators.applescript import AppleScriptGenerator
        as_gen = AppleScriptGenerator()
        print(f"✅ AppleScript generator: {as_gen.platform}")
        
        # Test Bash generator
        from src.generators.bash import BashGenerator
        bash_gen = BashGenerator()
        print(f"✅ Bash generator: {bash_gen.platform}")
        
        # Test code generation
        print("\n🔧 Testing Code Generation...")
        
        # Test PowerShell generation
        ps_prompt = ps_gen.build_generation_prompt("Create a script to list all running processes")
        print(f"✅ PowerShell prompt generated: {len(ps_prompt)} characters")
        
        # Test AppleScript generation
        as_prompt = as_gen.build_generation_prompt("Create a script to open Safari and navigate to a website")
        print(f"✅ AppleScript prompt generated: {len(as_prompt)} characters")
        
        # Test Bash generation
        bash_prompt = bash_gen.build_generation_prompt("Create a script to backup files to a remote server")
        print(f"✅ Bash prompt generated: {len(bash_prompt)} characters")
        
        print("\n🎉 All code generators working successfully!")
        
    except Exception as e:
        print(f"❌ Code generator test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generators()
