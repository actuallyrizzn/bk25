#!/usr/bin/env python3
"""
Test script for complete code generation system
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_code_generation():
    """Test complete code generation system"""
    try:
        print("🔍 Testing Code Generation System...")
        
        # Test main code generator
        from src.core.code_generator import CodeGenerator, GenerationRequest
        cg = CodeGenerator()
        print(f"✅ Code Generator initialized with {len(cg.generators)} platforms")
        
        # List supported platforms
        print(f"📋 Supported platforms: {list(cg.generators.keys())}")
        
        # Test platform detection
        print(f"🔍 Platform hints: {list(cg.platform_hints.keys())}")
        
        # Test automation patterns
        print(f"🔄 Automation patterns: {list(cg.automation_patterns.keys())}")
        
        # Test generation request creation
        request = GenerationRequest(
            description="Create a script to list all running processes",
            platform="powershell",
            options={"verbose": True}
        )
        print(f"✅ Generation request created: {request.platform}")
        
        # Test individual generators
        print("\n🔧 Testing Individual Generators...")
        
        # PowerShell
        ps_gen = cg.generators['powershell']
        ps_prompt = ps_gen.build_generation_prompt("List processes")
        print(f"✅ PowerShell prompt: {len(ps_prompt)} characters")
        
        # AppleScript
        as_gen = cg.generators['applescript']
        as_prompt = as_gen.build_generation_prompt("Open Safari")
        print(f"✅ AppleScript prompt: {len(as_prompt)} characters")
        
        # Bash
        bash_gen = cg.generators['bash']
        bash_prompt = bash_gen.build_generation_prompt("Backup files")
        print(f"✅ Bash prompt: {len(bash_prompt)} characters")
        
        print("\n🎉 Code generation system working successfully!")
        
    except Exception as e:
        print(f"❌ Code generation test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_code_generation()
