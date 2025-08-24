#!/usr/bin/env python3
"""
Test script for persona system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_personas():
    """Test persona loading and management"""
    try:
        from src.core.persona_manager import PersonaManager
        
        print("🎭 Testing Persona Manager...")
        
        # Initialize persona manager
        pm = PersonaManager()
        await pm.initialize()
        
        # Check personas loaded
        personas = pm.get_all_personas()
        print(f"✅ Personas loaded: {len(personas)}")
        
        # List all personas
        for persona in personas:
            print(f"  - {persona.name} ({persona.id})")
        
        # Check current persona
        current = pm.get_current_persona()
        if current:
            print(f"✅ Current persona: {current.name} ({current.id})")
            print(f"  Description: {current.description}")
            print(f"  Greeting: {current.greeting}")
        else:
            print("⚠️ No current persona set")
        
        # Test persona switching
        if len(personas) > 1:
            first_persona = personas[0]
            pm.switch_persona(first_persona.id)
            print(f"✅ Switched to: {pm.get_current_persona().name}")
        
        print("\n🎉 Persona system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Persona test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_personas())
