"""
BK25 Persona Manager

Handles loading and switching between different AI personas
Enables multi-modal experiences across web, Slack, voice, etc.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..models.persona import Persona, PersonaMetadata


class PersonaManager:
    """Manages AI personas for different conversation contexts"""
    
    def __init__(self, personas_path: str = "./personas"):
        self.personas: Dict[str, Persona] = {}
        self.current_persona: Optional[Persona] = None
        self.personas_path = Path(personas_path)
    
    async def initialize(self) -> None:
        """Initialize persona manager by loading all personas"""
        try:
            await self.load_all_personas()
            # Set default persona
            self.current_persona = (
                self.personas.get("vanilla") or 
                self.personas.get("default") or 
                next(iter(self.personas.values()), None)
            )
            print(f"🎭 Persona Manager initialized with {len(self.personas)} personas")
            print(f"📝 Current persona: {self.current_persona.name if self.current_persona else 'None'}")
        except Exception as error:
            print(f"Persona Manager initialization error: {error}")
            # Create a fallback persona if loading fails
            self.create_fallback_persona()
    
    async def load_all_personas(self) -> None:
        """Load all persona files from the personas directory"""
        try:
            if not self.personas_path.exists():
                print(f"⚠️ Personas directory not found: {self.personas_path}")
                return
            
            persona_files = list(self.personas_path.glob("*.json"))
            
            for file_path in persona_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        persona_data = json.load(f)
                    
                    # Validate and create persona
                    if self.validate_persona_data(persona_data):
                        persona = Persona(**persona_data)
                        self.personas[persona.id] = persona
                        print(f"✅ Loaded persona: {persona.name} ({persona.id})")
                    else:
                        print(f"⚠️ Invalid persona file: {file_path.name}")
                except Exception as e:
                    print(f"⚠️ Error loading persona {file_path.name}: {e}")
                    
        except Exception as error:
            print(f"Error loading personas: {error}")
            raise
    
    def validate_persona_data(self, persona_data: Dict[str, Any]) -> bool:
        """Validate persona structure"""
        required_fields = ["id", "name", "description", "greeting", "systemPrompt"]
        return all(field in persona_data for field in required_fields)
    
    def create_fallback_persona(self) -> None:
        """Create a fallback persona if loading fails"""
        fallback_data = {
            "id": "fallback",
            "name": "BK25 Assistant",
            "description": "Default assistant persona",
            "greeting": "👋 Hello! I'm BK25, your helpful AI assistant.",
            "capabilities": ["General conversation", "Automation scripting"],
            "systemPrompt": "You are BK25, a helpful AI assistant that can generate automation scripts and provide conversational assistance.",
            "examples": ["Create a PowerShell script", "Help with automation"],
            "channels": None  # No channel restriction - available everywhere
        }
        
        fallback_persona = Persona(**fallback_data)
        self.personas["fallback"] = fallback_persona
        self.current_persona = fallback_persona
        print("🔄 Using fallback persona")
    
    def get_all_personas(self) -> List[Persona]:
        """Get all available personas"""
        return list(self.personas.values())
    
    def get_personas_for_channel(self, channel: str) -> List[Persona]:
        """Get personas available for a specific channel"""
        return [
            persona for persona in self.personas.values()
            if persona.channels is None or channel in persona.channels
        ]
    
    def get_current_persona(self) -> Optional[Persona]:
        """Get current persona"""
        return self.current_persona
    
    def switch_persona(self, persona_id: str) -> Optional[Persona]:
        """Switch to a different persona"""
        persona = self.personas.get(persona_id)
        if persona:
            self.current_persona = persona
            print(f"🎭 Switched to persona: {persona.name} ({persona.id})")
            return persona
        else:
            print(f"⚠️ Persona not found: {persona_id}")
            return None
    
    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Get persona by ID"""
        return self.personas.get(persona_id)
    
    def build_persona_prompt(
        self, 
        message: str, 
        conversation_history: List[Dict[str, Any]] = None
    ) -> str:
        """Build conversation prompt using current persona"""
        persona = self.current_persona
        if not persona:
            return f"User: {message}\nAssistant:"
        
        conversation_history = conversation_history or []
        
        prompt = persona.system_prompt + "\n\nConversation history:\n"
        
        # Add conversation history
        for msg in conversation_history:
            prompt += f"{msg['role']}: {msg['content']}\n"
        
        prompt += f"\nUser: {message}\nAssistant:"
        
        return prompt
    
    def get_greeting(self) -> str:
        """Get persona-specific greeting"""
        return self.current_persona.greeting if self.current_persona else "Hello! How can I help you today?"
    
    def get_capabilities(self) -> List[str]:
        """Get persona-specific capabilities"""
        return self.current_persona.capabilities if self.current_persona else ["General assistance"]
    
    def get_examples(self) -> List[str]:
        """Get persona-specific examples"""
        return self.current_persona.examples if self.current_persona else []
    
    def get_persona_metadata(self) -> Optional[PersonaMetadata]:
        """Get persona metadata for UI"""
        if not self.current_persona:
            return None
        
        return PersonaMetadata(
            id=self.current_persona.id,
            name=self.current_persona.name,
            description=self.current_persona.description,
            greeting=self.current_persona.greeting,
            capabilities=self.current_persona.capabilities,
            examples=self.current_persona.examples,
            personality=self.current_persona.personality
        )
    
    async def reload_personas(self) -> None:
        """Reload personas from disk (useful for development)"""
        current_id = self.current_persona.id if self.current_persona else None
        
        self.personas.clear()
        await self.load_all_personas()
        
        # Try to maintain current persona, fallback to default
        if current_id and current_id in self.personas:
            self.current_persona = self.personas[current_id]
        else:
            self.current_persona = (
                self.personas.get("default") or 
                next(iter(self.personas.values()), None)
            )
        
        print("🔄 Personas reloaded")
    
    def create_custom_persona(self, persona_data: Dict[str, Any]) -> Persona:
        """Create a custom persona at runtime"""
        # Generate ID if not provided
        if "id" not in persona_data:
            persona_data["id"] = f"custom_{len([p for p in self.personas.values() if p.id.startswith('custom_')])}"
        
        # Validate required fields
        if not self.validate_persona_data(persona_data):
            raise ValueError("Invalid persona data - missing required fields")
        
        persona = Persona(**persona_data)
        self.personas[persona.id] = persona
        
        return persona