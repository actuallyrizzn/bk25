"""
Unit tests for PersonaManager component
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.core.persona_manager import PersonaManager
from src.core.persona_manager import Persona, PersonaPersonality


class TestPersonaManager:
    """Test PersonaManager functionality"""

    @pytest.fixture
    def persona_manager(self, temp_dir):
        """Create PersonaManager instance for testing"""
        personas_path = temp_dir / "personas"
        personas_path.mkdir()
        return PersonaManager(str(personas_path))

    @pytest.fixture
    def sample_persona_data(self):
        """Sample persona data for testing"""
        return {
            "id": "test-persona",
            "name": "Test Persona",
            "description": "A test persona for unit testing",
            "greeting": "Hello! I'm a test persona.",
            "capabilities": ["testing", "debugging"],
            "personality": {
                "tone": "professional",
                "approach": "systematic",
                "philosophy": "testing",
                "motto": "Test everything"
            },
            "examples": ["Test example 1", "Test example 2"],
            "channels": ["web", "cli"],
            "systemPrompt": "You are a test persona focused on testing and debugging."
        }

    @pytest.fixture
    def sample_persona_data_for_direct_creation(self):
        """Sample persona data for direct Persona creation (uses snake_case)"""
        from src.core.persona_manager import PersonaPersonality
        return {
            "id": "test-persona",
            "name": "Test Persona",
            "description": "A test persona for unit testing",
            "greeting": "Hello! I'm a test persona.",
            "capabilities": ["testing", "debugging"],
            "personality": PersonaPersonality(
                tone="professional",
                approach="systematic",
                philosophy="testing",
                motto="Test everything"
            ),
            "examples": ["Test example 1", "Test example 2"],
            "channels": ["web", "cli"],
            "system_prompt": "You are a test persona focused on testing and debugging."
        }

    @pytest.fixture
    def sample_persona_file(self, sample_persona_data):
        """Sample persona file content"""
        return json.dumps(sample_persona_data, indent=2)

    def test_init(self, persona_manager):
        """Test PersonaManager initialization"""
        assert persona_manager.personas_path is not None
        assert isinstance(persona_manager.personas, dict)
        assert persona_manager.current_persona is None
        assert persona_manager.logger is not None

    @pytest.mark.asyncio
    async def test_initialize_empty_directory(self, persona_manager):
        """Test initialization with empty personas directory"""
        await persona_manager.initialize()
        assert len(persona_manager.personas) == 0
        assert persona_manager.current_persona is None

    @pytest.mark.asyncio
    async def test_initialize_with_personas(self, persona_manager, sample_persona_data, sample_persona_file):
        """Test initialization with existing persona files"""
        # Create persona file
        persona_file = Path(persona_manager.personas_path) / f"{sample_persona_data['id']}.json"
        persona_file.write_text(sample_persona_file)

        await persona_manager.initialize()
        
        assert len(persona_manager.personas) == 1
        assert sample_persona_data['id'] in persona_manager.personas
        assert persona_manager.personas[sample_persona_data['id']].name == sample_persona_data['name']

    @pytest.mark.asyncio
    async def test_initialize_invalid_json(self, persona_manager, temp_dir):
        """Test initialization with invalid JSON files"""
        # Create invalid JSON file
        invalid_file = Path(persona_manager.personas_path) / "invalid.json"
        invalid_file.write_text("{ invalid json }")

        # Should not raise exception, just log error
        await persona_manager.initialize()
        assert len(persona_manager.personas) == 0

    @pytest.mark.asyncio
    async def test_initialize_missing_required_fields(self, persona_manager, temp_dir):
        """Test initialization with persona missing required fields"""
        # Create persona file missing required fields
        incomplete_data = {
            "id": "incomplete",
            "name": "Incomplete Persona"
            # Missing description and other required fields
        }
        incomplete_file = Path(persona_manager.personas_path) / "incomplete.json"
        incomplete_file.write_text(json.dumps(incomplete_data))

        await persona_manager.initialize()
        assert len(persona_manager.personas) == 0

    def test_get_all_personas(self, persona_manager, sample_persona_data_for_direct_creation):
        """Test getting all personas"""
        # Add persona directly to manager
        persona = Persona(**sample_persona_data_for_direct_creation)
        persona_manager.personas[sample_persona_data_for_direct_creation['id']] = persona

        all_personas = persona_manager.get_all_personas()
        assert len(all_personas) == 1
        assert all_personas[0].id == sample_persona_data_for_direct_creation['id']

    def test_get_persona_existing(self, persona_manager, sample_persona_data_for_direct_creation):
        """Test getting existing persona by ID"""
        persona = Persona(**sample_persona_data_for_direct_creation)
        persona_manager.personas[sample_persona_data_for_direct_creation['id']] = persona

        retrieved = persona_manager.get_persona(sample_persona_data_for_direct_creation['id'])
        assert retrieved is not None
        assert retrieved.id == sample_persona_data_for_direct_creation['id']
        assert retrieved.name == sample_persona_data_for_direct_creation['name']

    def test_get_persona_nonexistent(self, persona_manager):
        """Test getting non-existent persona by ID"""
        retrieved = persona_manager.get_persona("nonexistent")
        assert retrieved is None

    def test_get_personas_for_channel(self, persona_manager, sample_persona_data_for_direct_creation):
        """Test getting personas for specific channel"""
        # Add persona that supports 'web' channel
        persona = Persona(**sample_persona_data_for_direct_creation)
        persona_manager.personas[sample_persona_data_for_direct_creation['id']] = persona

        web_personas = persona_manager.get_personas_for_channel("web")
        assert len(web_personas) == 1
        assert web_personas[0].id == sample_persona_data_for_direct_creation['id']

        # Test channel not supported
        cli_personas = persona_manager.get_personas_for_channel("cli")
        assert len(cli_personas) == 1  # Should still return since persona supports 'cli'

        # Test unsupported channel
        unsupported_personas = persona_manager.get_personas_for_channel("unsupported")
        assert len(unsupported_personas) == 0

    def test_get_current_persona_none(self, persona_manager):
        """Test getting current persona when none set"""
        current = persona_manager.get_current_persona()
        assert current is None

    def test_get_current_persona_set(self, persona_manager, sample_persona_data_for_direct_creation):
        """Test getting current persona when one is set"""
        persona = Persona(**sample_persona_data_for_direct_creation)
        persona_manager.personas[sample_persona_data_for_direct_creation['id']] = persona
        persona_manager.current_persona = persona

        current = persona_manager.get_current_persona()
        assert current is not None
        assert current.id == sample_persona_data_for_direct_creation['id']

    def test_switch_persona_existing(self, persona_manager, sample_persona_data_for_direct_creation):
        """Test switching to existing persona"""
        persona = Persona(**sample_persona_data_for_direct_creation)
        persona_manager.personas[sample_persona_data_for_direct_creation['id']] = persona

        result = persona_manager.switch_persona(sample_persona_data_for_direct_creation['id'])
        assert result is not None
        assert result.id == sample_persona_data_for_direct_creation['id']
        assert persona_manager.current_persona.id == sample_persona_data_for_direct_creation['id']

    def test_switch_persona_nonexistent(self, persona_manager):
        """Test switching to non-existent persona"""
        result = persona_manager.switch_persona("nonexistent")
        assert result is None
        assert persona_manager.current_persona is None

    def test_add_custom_persona_valid(self, persona_manager, sample_persona_data):
        """Test adding valid custom persona"""
        result = persona_manager.add_custom_persona(sample_persona_data)
        assert result is not None
        assert result.id == sample_persona_data['id']
        assert result.name == sample_persona_data['name']
        assert sample_persona_data['id'] in persona_manager.personas

    def test_add_custom_persona_missing_fields(self, persona_manager):
        """Test adding custom persona with missing required fields"""
        incomplete_data = {
            "id": "incomplete",
            "name": "Incomplete"
            # Missing description
        }
        result = persona_manager.add_custom_persona(incomplete_data)
        assert result is None
        assert "incomplete" not in persona_manager.personas

    def test_add_custom_persona_duplicate_id(self, persona_manager, sample_persona_data):
        """Test adding custom persona with duplicate ID"""
        # Add first persona
        persona_manager.add_custom_persona(sample_persona_data)
        
        # Try to add second with same ID
        duplicate_data = sample_persona_data.copy()
        duplicate_data['name'] = "Different Name"
        
        result = persona_manager.add_custom_persona(duplicate_data)
        assert result is None
        assert len(persona_manager.personas) == 1

    def test_build_persona_prompt_no_current(self, persona_manager):
        """Test building prompt when no current persona"""
        prompt = persona_manager.build_persona_prompt("Test message")
        assert "Test message" in prompt
        assert "User: Test message" in prompt

    def test_build_persona_prompt_with_current(self, persona_manager, sample_persona_data_for_direct_creation):
        """Test building prompt with current persona"""
        persona = Persona(**sample_persona_data_for_direct_creation)
        persona_manager.personas[sample_persona_data_for_direct_creation['id']] = persona
        persona_manager.current_persona = persona

        prompt = persona_manager.build_persona_prompt("Test message")
        assert sample_persona_data_for_direct_creation['system_prompt'] in prompt
        assert "Test message" in prompt

    @pytest.mark.asyncio
    async def test_reload_personas(self, persona_manager, sample_persona_data, sample_persona_file):
        """Test reloading personas from disk"""
        # Initial state
        await persona_manager.initialize()
        assert len(persona_manager.personas) == 0

        # Add persona file
        persona_file = Path(persona_manager.personas_path) / f"{sample_persona_data['id']}.json"
        persona_file.write_text(sample_persona_file)

        # Reload
        await persona_manager.reload_personas()
        assert len(persona_manager.personas) == 1
        assert sample_persona_data['id'] in persona_manager.personas

    def test_to_dict(self, persona_manager, sample_persona_data_for_direct_creation):
        """Test converting persona manager to dictionary"""
        persona = Persona(**sample_persona_data_for_direct_creation)
        persona_manager.personas[sample_persona_data_for_direct_creation['id']] = persona
        persona_manager.current_persona = persona

        result = persona_manager.to_dict()
        assert "id" in result
        assert "name" in result
        assert result["id"] == sample_persona_data_for_direct_creation['id']

    def test_persona_validation(self, persona_manager):
        """Test persona data validation"""
        # Test valid persona
        valid_data = {
            "id": "valid",
            "name": "Valid Persona",
            "description": "A valid persona",
            "personality": {
                "tone": "friendly",
                "approach": "helpful",
                "philosophy": "assistance",
                "motto": "I help"
            }
        }
        result = persona_manager.add_custom_persona(valid_data)
        assert result is not None

        # Test invalid personality
        invalid_personality = valid_data.copy()
        invalid_personality["personality"] = {
            "tone": "invalid_tone",  # Invalid tone
            "approach": "helpful",
            "philosophy": "assistance",
            "motto": "I help"
        }
        result = persona_manager.add_custom_persona(invalid_personality)
        assert result is None

    def test_persona_capabilities(self, persona_manager, sample_persona_data):
        """Test persona capabilities functionality"""
        persona = persona_manager.add_custom_persona(sample_persona_data)
        assert persona is not None
        
        # Test capabilities
        assert "testing" in persona.capabilities
        assert "debugging" in persona.capabilities
        assert len(persona.capabilities) == 2

    def test_persona_channels(self, persona_manager, sample_persona_data):
        """Test persona channel support"""
        persona = persona_manager.add_custom_persona(sample_persona_data)
        assert persona is not None
        
        # Test channel support
        assert "web" in persona.channels
        assert "cli" in persona.channels
        assert len(persona.channels) == 2

    def test_persona_examples(self, persona_manager, sample_persona_data):
        """Test persona examples"""
        persona = persona_manager.add_custom_persona(sample_persona_data)
        assert persona is not None
        
        # Test examples
        assert "Test example 1" in persona.examples
        assert "Test example 2" in persona.examples
        assert len(persona.examples) == 2

    def test_persona_greeting(self, persona_manager, sample_persona_data):
        """Test persona greeting"""
        persona = persona_manager.add_custom_persona(sample_persona_data)
        assert persona is not None
        
        assert persona.greeting == "Hello! I'm a test persona."

    def test_persona_system_prompt(self, persona_manager, sample_persona_data):
        """Test persona system prompt"""
        persona = persona_manager.add_custom_persona(sample_persona_data)
        assert persona is not None
        
        assert "You are Test Persona, A test persona for unit testing" in persona.system_prompt

    @pytest.mark.asyncio
    async def test_error_handling_during_initialization(self, persona_manager, temp_dir):
        """Test error handling during initialization"""
        # Create a file that's not JSON
        non_json_file = Path(persona_manager.personas_path) / "not_json.txt"
        non_json_file.write_text("This is not JSON")

        # Should not crash, just log error
        await persona_manager.initialize()
        assert len(persona_manager.personas) == 0

    def test_persona_switching_preserves_state(self, persona_manager, sample_persona_data):
        """Test that persona switching preserves other state"""
        # Add two personas
        persona1_data = sample_persona_data.copy()
        persona1_data['id'] = 'persona1'
        persona1_data['name'] = 'Persona 1'
        
        persona2_data = sample_persona_data.copy()
        persona2_data['id'] = 'persona2'
        persona2_data['name'] = 'Persona 2'
        
        persona1 = persona_manager.add_custom_persona(persona1_data)
        persona2 = persona_manager.add_custom_persona(persona2_data)
        
        # Switch to first persona
        persona_manager.switch_persona('persona1')
        assert persona_manager.current_persona.id == 'persona1'
        
        # Switch to second persona
        persona_manager.switch_persona('persona2')
        assert persona_manager.current_persona.id == 'persona2'
        
        # Verify both personas still exist
        assert 'persona1' in persona_manager.personas
        assert 'persona2' in persona_manager.personas
