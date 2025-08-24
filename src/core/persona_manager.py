"""
BK25 Persona Manager

Handles loading and switching between different AI personas.
Enables multi-modal experiences across web, Slack, voice, etc.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from ..logging_config import get_logger

logger = get_logger("persona_manager")

@dataclass
class PersonaPersonality:
    """Persona personality traits"""
    tone: str
    approach: str
    philosophy: str
    motto: str

@dataclass
class Persona:
    """Persona data structure"""
    id: str
    name: str
    description: str
    greeting: str
    capabilities: List[str]
    personality: PersonaPersonality
    system_prompt: str
    examples: List[str]
    channels: List[str]

class PersonaManager:
    """Manages AI personas for BK25"""
    
    def __init__(self, personas_path: Optional[str] = None):
        self.personas: Dict[str, Persona] = {}
        self.current_persona: Optional[Persona] = None
        self.personas_path = Path(personas_path) if personas_path else Path("./personas")
        self.logger = get_logger("persona_manager")
    
    async def initialize(self) -> None:
        """Initialize persona manager by loading all personas"""
        try:
            await self.load_all_personas()
            # Set default persona
            self.current_persona = (
                self.personas.get('vanilla') or 
                self.personas.get('default') or 
                next(iter(self.personas.values()), None)
            )
            
            self.logger.info(f"🎭 Persona Manager initialized with {len(self.personas)} personas")
            self.logger.info(f"📝 Current persona: {self.current_persona.name if self.current_persona else 'None'}")
            
        except Exception as error:
            self.logger.error(f"Persona Manager initialization error: {error}")
            # Create a fallback persona if loading fails
            self.create_fallback_persona()
    
    async def load_all_personas(self) -> None:
        """Load all persona files from the personas directory"""
        try:
            if not self.personas_path.exists():
                self.logger.warning(f"Personas directory not found: {self.personas_path}")
                return
            
            persona_files = list(self.personas_path.glob("*.json"))
            
            for file_path in persona_files:
                try:
                    persona_data = await self._load_persona_file(file_path)
                    if self.validate_persona(persona_data):
                        persona = self._create_persona_from_data(persona_data)
                        self.personas[persona.id] = persona
                        self.logger.info(f"✅ Loaded persona: {persona.name} ({persona.id})")
                    else:
                        self.logger.warning(f"⚠️ Invalid persona file: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Error loading persona {file_path.name}: {e}")
                    
        except Exception as error:
            self.logger.error(f"Error loading personas: {error}")
            raise
    
    async def _load_persona_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a single persona file"""
        async with asyncio.Lock():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def validate_persona(self, persona_data: Dict[str, Any]) -> bool:
        """Validate persona structure"""
        required_fields = ['id', 'name', 'description', 'greeting', 'systemPrompt']
        return all(field in persona_data for field in required_fields)
    
    def _create_persona_from_data(self, data: Dict[str, Any]) -> Persona:
        """Create a Persona object from JSON data"""
        # Handle the systemPrompt field (camelCase in JSON, snake_case in Python)
        system_prompt = data.get('systemPrompt', '')
        
        # Handle personality data
        personality_data = data.get('personality', {})
        personality = PersonaPersonality(
            tone=personality_data.get('tone', 'neutral'),
            approach=personality_data.get('approach', 'helpful'),
            philosophy=personality_data.get('philosophy', 'assistance'),
            motto=personality_data.get('motto', 'here to help')
        )
        
        return Persona(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            greeting=data['greeting'],
            capabilities=data.get('capabilities', []),
            personality=personality,
            system_prompt=system_prompt,
            examples=data.get('examples', []),
            channels=data.get('channels', ['web'])
        )
    
    def create_fallback_persona(self) -> None:
        """Create a fallback persona if loading fails"""
        fallback_persona = Persona(
            id='fallback',
            name='BK25 Assistant',
            description='Default assistant persona',
            greeting='👋 Hello! I\'m BK25, your helpful AI assistant.',
            capabilities=['General conversation', 'Automation scripting'],
            personality=PersonaPersonality(
                tone='friendly',
                approach='helpful',
                philosophy='assistance',
                motto='here to help'
            ),
            system_prompt='You are BK25, a helpful AI assistant that can generate automation scripts and provide conversational assistance.',
            examples=['Create a PowerShell script', 'Help with automation'],
            channels=['web']
        )
        
        self.personas['fallback'] = fallback_persona
        self.current_persona = fallback_persona
        self.logger.info('🔄 Using fallback persona')
    
    def get_all_personas(self) -> List[Persona]:
        """Get all available personas"""
        return list(self.personas.values())
    
    def get_personas_for_channel(self, channel: str) -> List[Persona]:
        """Get personas available for a specific channel"""
        return [
            persona for persona in self.personas.values()
            if not persona.channels or channel in persona.channels
        ]
    
    def get_current_persona(self) -> Optional[Persona]:
        """Get current persona"""
        return self.current_persona
    
    def switch_persona(self, persona_id: str) -> Optional[Persona]:
        """Switch to a different persona"""
        persona = self.personas.get(persona_id)
        if persona:
            self.current_persona = persona
            self.logger.info(f"🎭 Switched to persona: {persona.name} ({persona.id})")
            return persona
        else:
            self.logger.warning(f"⚠️ Persona not found: {persona_id}")
            return None
    
    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Get persona by ID"""
        return self.personas.get(persona_id)
    
    def build_persona_prompt(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Build conversation prompt using current persona"""
        persona = self.current_persona
        if not persona:
            return f"User: {message}\nAssistant:"
        
        prompt = persona.system_prompt + '\n\nConversation history:\n'
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                prompt += f"{msg.get('role', 'User')}: {msg.get('content', '')}\n"
        
        prompt += f"\nUser: {message}\nAssistant:"
        
        return prompt
    
    def get_greeting(self) -> str:
        """Get persona-specific greeting"""
        return self.current_persona.greeting if self.current_persona else 'Hello! How can I help you today?'
    
    def get_capabilities(self) -> List[str]:
        """Get persona-specific capabilities"""
        return self.current_persona.capabilities if self.current_persona else ['General assistance']
    
    def get_examples(self) -> List[str]:
        """Get persona-specific examples"""
        return self.current_persona.examples if self.current_persona else []
    
    def get_persona_metadata(self) -> Optional[Dict[str, Any]]:
        """Get persona metadata for UI"""
        if not self.current_persona:
            return None
        
        return {
            'id': self.current_persona.id,
            'name': self.current_persona.name,
            'description': self.current_persona.description,
            'greeting': self.current_persona.greeting,
            'capabilities': self.current_persona.capabilities,
            'examples': self.current_persona.examples,
            'personality': asdict(self.current_persona.personality)
        }
    
    async def reload_personas(self) -> None:
        """Reload personas from disk (useful for development)"""
        self.personas.clear()
        await self.load_all_personas()
        
        # Try to maintain current persona, fallback to default
        current_id = self.current_persona.id if self.current_persona else None
        if current_id and current_id in self.personas:
            self.current_persona = self.personas[current_id]
        else:
            self.current_persona = (
                self.personas.get('default') or 
                next(iter(self.personas.values()), None)
            )
        
        self.logger.info('🔄 Personas reloaded')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert current persona to dictionary for API responses"""
        if not self.current_persona:
            return {}
        
        return {
            'id': self.current_persona.id,
            'name': self.current_persona.name,
            'description': self.current_persona.description,
            'greeting': self.current_persona.greeting,
            'capabilities': self.current_persona.capabilities,
            'personality': asdict(self.current_persona.personality),
            'examples': self.current_persona.examples,
            'channels': self.current_persona.channels
        }
