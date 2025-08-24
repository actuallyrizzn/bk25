import pytest
import asyncio
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.persona_manager import PersonaManager, Persona, PersonaPersonality

class TestPersonaPersonality:
    """Test PersonaPersonality dataclass"""
    
    def test_persona_personality_creation(self):
        """Test creating a PersonaPersonality instance"""
        personality = PersonaPersonality(
            tone="professional",
            approach="systematic",
            philosophy="efficiency-first",
            motto="Work smarter, not harder"
        )
        
        assert personality.tone == "professional"
        assert personality.approach == "systematic"
        assert personality.philosophy == "efficiency-first"
        assert personality.motto == "Work smarter, not harder"
    
    def test_persona_personality_defaults(self):
        """Test PersonaPersonality with default values"""
        personality = PersonaPersonality()
        
        assert personality.tone == "friendly"
        assert personality.approach == "helpful"
        assert personality.philosophy == "user-centric"
        assert personality.motto == "Let's solve this together!"

class TestPersona:
    """Test Persona dataclass"""
    
    def test_persona_creation(self):
        """Test creating a Persona instance"""
        personality = PersonaPersonality(
            tone="professional",
            approach="systematic"
        )
        
        persona = Persona(
            id="test_persona",
            name="Test Persona",
            description="A test persona for testing",
            greeting="Hello, I'm a test persona!",
            capabilities=["testing", "validation"],
            personality=personality,
            examples=["Example 1", "Example 2"],
            channels=["web", "discord"]
        )
        
        assert persona.id == "test_persona"
        assert persona.name == "Test Persona"
        assert persona.description == "A test persona for testing"
        assert persona.greeting == "Hello, I'm a test persona!"
        assert persona.capabilities == ["testing", "validation"]
        assert persona.personality == personality
        assert persona.examples == ["Example 1", "Example 2"]
        assert persona.channels == ["web", "discord"]
    
    def test_persona_defaults(self):
        """Test Persona with default values"""
        persona = Persona(
            id="minimal",
            name="Minimal Persona"
        )
        
        assert persona.id == "minimal"
        assert persona.name == "Minimal Persona"
        assert persona.description == ""
        assert persona.greeting == ""
        assert persona.capabilities == []
        assert persona.examples == []
        assert persona.channels == []
        assert isinstance(persona.personality, PersonaPersonality)
    
    def test_persona_to_dict(self):
        """Test Persona.to_dict() method"""
        personality = PersonaPersonality(tone="friendly")
        persona = Persona(
            id="test",
            name="Test",
            personality=personality
        )
        
        result = persona.to_dict()
        
        assert result["id"] == "test"
        assert result["name"] == "Test"
        assert result["personality"]["tone"] == "friendly"
        assert "capabilities" in result
        assert "examples" in result
        assert "channels" in result

class TestPersonaManager:
    """Test PersonaManager class"""
    
    @pytest.fixture
    def temp_personas_dir(self):
        """Create temporary personas directory with test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            personas_dir = Path(temp_dir) / "personas"
            personas_dir.mkdir()
            
            # Create test persona files
            test_personas = {
                "vanilla.json": {
                    "id": "vanilla",
                    "name": "Vanilla Chatbot",
                    "description": "Default onboarding-focused persona",
                    "greeting": "Hello! I'm here to help you with automation.",
                    "capabilities": ["onboarding", "automation"],
                    "personality": {
                        "tone": "friendly",
                        "approach": "helpful",
                        "philosophy": "user-centric",
                        "motto": "Let's get started!"
                    },
                    "examples": ["Example 1", "Example 2"],
                    "channels": ["web", "discord"]
                },
                "expert.json": {
                    "id": "expert",
                    "name": "Technical Expert",
                    "description": "Deep technical knowledge and solutions",
                    "greeting": "I'm your technical expert. What can I help you with?",
                    "capabilities": ["technical_support", "problem_solving"],
                    "personality": {
                        "tone": "professional",
                        "approach": "systematic",
                        "philosophy": "efficiency-first",
                        "motto": "Let's solve this systematically!"
                    },
                    "examples": ["Technical Example"],
                    "channels": ["web", "teams"]
                }
            }
            
            for filename, content in test_personas.items():
                file_path = personas_dir / filename
                with open(file_path, 'w') as f:
                    json.dump(content, f)
            
            yield personas_dir
    
    @pytest.fixture
    def persona_manager(self, temp_personas_dir):
        """Create PersonaManager instance with test data"""
        return PersonaManager(personas_path=str(temp_personas_dir))
    
    @pytest.mark.asyncio
    async def test_initialization(self, persona_manager):
        """Test PersonaManager initialization"""
        assert persona_manager.personas_path is not None
        assert persona_manager.personas == {}
        assert persona_manager.current_persona is None
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, persona_manager):
        """Test successful initialization"""
        await persona_manager.initialize()
        
        assert len(persona_manager.personas) == 2
        assert "vanilla" in persona_manager.personas
        assert "expert" in persona_manager.personas
        assert persona_manager.current_persona is not None
    
    @pytest.mark.asyncio
    async def test_initialize_with_invalid_file(self, temp_personas_dir):
        """Test initialization with invalid JSON file"""
        # Create invalid JSON file
        invalid_file = temp_personas_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
        
        persona_manager = PersonaManager(personas_path=str(temp_personas_dir))
        await persona_manager.initialize()
        
        # Should skip invalid file and load valid ones
        assert len(persona_manager.personas) == 2
        assert "invalid" not in persona_manager.personas
    
    @pytest.mark.asyncio
    async def test_initialize_with_missing_directory(self):
        """Test initialization with non-existent directory"""
        persona_manager = PersonaManager(personas_path="/non/existent/path")
        
        # Should not raise error, just have empty personas
        await persona_manager.initialize()
        assert len(persona_manager.personas) == 0
    
    @pytest.mark.asyncio
    async def test_get_persona_existing(self, persona_manager):
        """Test getting existing persona"""
        await persona_manager.initialize()
        
        persona = persona_manager.get_persona("vanilla")
        assert persona is not None
        assert persona.id == "vanilla"
        assert persona.name == "Vanilla Chatbot"
    
    @pytest.mark.asyncio
    async def test_get_persona_nonexistent(self, persona_manager):
        """Test getting non-existent persona"""
        await persona_manager.initialize()
        
        persona = persona_manager.get_persona("nonexistent")
        assert persona is None
    
    @pytest.mark.asyncio
    async def test_get_all_personas(self, persona_manager):
        """Test getting all personas"""
        await persona_manager.initialize()
        
        all_personas = persona_manager.get_all_personas()
        assert len(all_personas) == 2
        assert all(persona.id in ["vanilla", "expert"] for persona in all_personas)
    
    @pytest.mark.asyncio
    async def test_get_personas_for_channel(self, persona_manager):
        """Test getting personas for specific channel"""
        await persona_manager.initialize()
        
        web_personas = persona_manager.get_personas_for_channel("web")
        assert len(web_personas) == 2  # Both support web
        
        teams_personas = persona_manager.get_personas_for_channel("teams")
        assert len(teams_personas) == 1  # Only expert supports teams
        assert teams_personas[0].id == "expert"
    
    @pytest.mark.asyncio
    async def test_get_personas_for_nonexistent_channel(self, persona_manager):
        """Test getting personas for non-existent channel"""
        await persona_manager.initialize()
        
        personas = persona_manager.get_personas_for_channel("nonexistent")
        assert len(personas) == 0
    
    @pytest.mark.asyncio
    async def test_switch_persona_success(self, persona_manager):
        """Test successful persona switching"""
        await persona_manager.initialize()
        
        # Switch to expert persona
        result = persona_manager.switch_persona("expert")
        assert result is not None
        assert result.id == "expert"
        assert persona_manager.current_persona.id == "expert"
    
    @pytest.mark.asyncio
    async def test_switch_persona_nonexistent(self, persona_manager):
        """Test switching to non-existent persona"""
        await persona_manager.initialize()
        
        result = persona_manager.switch_persona("nonexistent")
        assert result is None
        # Current persona should remain unchanged
        assert persona_manager.current_persona is not None
    
    @pytest.mark.asyncio
    async def test_get_current_persona(self, persona_manager):
        """Test getting current persona"""
        await persona_manager.initialize()
        
        # Should have default persona
        current = persona_manager.get_current_persona()
        assert current is not None
        assert current.id in ["vanilla", "expert"]
    
    @pytest.mark.asyncio
    async def test_get_current_persona_none(self):
        """Test getting current persona when none set"""
        persona_manager = PersonaManager(personas_path="/empty/path")
        await persona_manager.initialize()
        
        current = persona_manager.get_current_persona()
        assert current is None
    
    @pytest.mark.asyncio
    async def test_build_persona_prompt(self, persona_manager):
        """Test building persona-specific prompt"""
        await persona_manager.initialize()
        
        prompt = "Help me with automation"
        result = persona_manager.build_persona_prompt(prompt)
        
        assert result is not None
        assert prompt in result
        assert "persona" in result.lower() or "assistant" in result.lower()
    
    @pytest.mark.asyncio
    async def test_build_persona_prompt_no_current(self):
        """Test building prompt when no current persona"""
        persona_manager = PersonaManager(personas_path="/empty/path")
        await persona_manager.initialize()
        
        prompt = "Help me with automation"
        result = persona_manager.build_persona_prompt(prompt)
        
        # Should return original prompt when no persona
        assert result == prompt
    
    @pytest.mark.asyncio
    async def test_reload_personas(self, persona_manager, temp_personas_dir):
        """Test reloading personas from disk"""
        await persona_manager.initialize()
        initial_count = len(persona_manager.personas)
        
        # Add new persona file
        new_persona = {
            "id": "new",
            "name": "New Persona",
            "description": "A new test persona",
            "greeting": "Hello, I'm new!",
            "capabilities": ["testing"],
            "personality": {
                "tone": "friendly",
                "approach": "helpful",
                "philosophy": "user-centric",
                "motto": "Let's test!"
            },
            "examples": [],
            "channels": ["web"]
        }
        
        new_file = temp_personas_dir / "new.json"
        with open(new_file, 'w') as f:
            json.dump(new_persona, f)
        
        # Reload personas
        await persona_manager.reload_personas()
        
        assert len(persona_manager.personas) == initial_count + 1
        assert "new" in persona_manager.personas
    
    @pytest.mark.asyncio
    async def test_to_dict(self, persona_manager):
        """Test PersonaManager.to_dict() method"""
        await persona_manager.initialize()
        
        result = persona_manager.to_dict()
        
        assert "personas" in result
        assert "current_persona" in result
        assert "total_count" in result
        assert result["total_count"] == 2
    
    @pytest.mark.asyncio
    async def test_validate_persona_data_valid(self):
        """Test validation of valid persona data"""
        valid_data = {
            "id": "test",
            "name": "Test",
            "description": "Test description",
            "greeting": "Hello!",
            "capabilities": ["test"],
            "personality": {
                "tone": "friendly",
                "approach": "helpful",
                "philosophy": "user-centric",
                "motto": "Let's test!"
            },
            "examples": [],
            "channels": ["web"]
        }
        
        # Should not raise any exceptions
        PersonaManager._validate_persona_data(valid_data)
    
    @pytest.mark.asyncio
    async def test_validate_persona_data_missing_required(self):
        """Test validation with missing required fields"""
        invalid_data = {
            "name": "Test"  # Missing id
        }
        
        with pytest.raises(ValueError, match="Missing required field: id"):
            PersonaManager._validate_persona_data(invalid_data)
    
    @pytest.mark.asyncio
    async def test_validate_persona_data_invalid_personality(self):
        """Test validation with invalid personality data"""
        invalid_data = {
            "id": "test",
            "name": "Test",
            "personality": "invalid"  # Should be dict
        }
        
        with pytest.raises(ValueError, match="Personality must be a dictionary"):
            PersonaManager._validate_persona_data(invalid_data)
    
    @pytest.mark.asyncio
    async def test_validate_persona_data_invalid_capabilities(self):
        """Test validation with invalid capabilities"""
        invalid_data = {
            "id": "test",
            "name": "Test",
            "capabilities": "invalid"  # Should be list
        }
        
        with pytest.raises(ValueError, match="Capabilities must be a list"):
            PersonaManager._validate_persona_data(invalid_data)
    
    @pytest.mark.asyncio
    async def test_validate_persona_data_invalid_channels(self):
        """Test validation with invalid channels"""
        invalid_data = {
            "id": "test",
            "name": "Test",
            "channels": "invalid"  # Should be list
        }
        
        with pytest.raises(ValueError, match="Channels must be a list"):
            PersonaManager._validate_persona_data(invalid_data)
    
    @pytest.mark.asyncio
    async def test_error_handling_corrupted_file(self, temp_personas_dir):
        """Test handling of corrupted persona files"""
        # Create corrupted JSON file
        corrupted_file = temp_personas_dir / "corrupted.json"
        with open(corrupted_file, 'w') as f:
            f.write('{"id": "corrupted", "name": "Corrupted", "invalid": json}')
        
        persona_manager = PersonaManager(personas_path=str(temp_personas_dir))
        
        # Should not crash, just skip corrupted file
        await persona_manager.initialize()
        assert "corrupted" not in persona_manager.personas
    
    @pytest.mark.asyncio
    async def test_error_handling_malformed_json(self, temp_personas_dir):
        """Test handling of malformed JSON"""
        # Create malformed JSON file
        malformed_file = temp_personas_dir / "malformed.json"
        with open(malformed_file, 'w') as f:
            f.write('{"id": "malformed", "name": "Malformed", "unclosed": "quote}')
        
        persona_manager = PersonaManager(personas_path=str(temp_personas_dir))
        
        # Should not crash, just skip malformed file
        await persona_manager.initialize()
        assert "malformed" not in persona_manager.personas

if __name__ == "__main__":
    pytest.main([__file__])
