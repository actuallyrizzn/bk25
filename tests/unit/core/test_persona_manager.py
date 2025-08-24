"""
Unit tests for the PersonaManager class.
"""

import pytest
from bk25.core.persona_manager import PersonaManager
from bk25.models.persona import Persona


class TestPersonaManager:
    """Test cases for PersonaManager."""
    
    def test_initialization(self, persona_manager):
        """Test persona manager initialization."""
        assert len(persona_manager.personas) >= 1  # At least fallback persona
        assert persona_manager.current_persona is not None
        assert persona_manager.current_persona.id == "fallback"
    
    def test_validate_persona_data(self, persona_manager):
        """Test persona data validation."""
        valid_data = {
            "id": "test",
            "name": "Test",
            "description": "Test persona",
            "greeting": "Hello!",
            "systemPrompt": "You are a test."
        }
        assert persona_manager.validate_persona_data(valid_data) is True
        
        # Missing required field
        invalid_data = valid_data.copy()
        del invalid_data["systemPrompt"]
        assert persona_manager.validate_persona_data(invalid_data) is False
    
    def test_create_fallback_persona(self):
        """Test fallback persona creation."""
        manager = PersonaManager()
        manager.create_fallback_persona()
        
        assert "fallback" in manager.personas
        fallback = manager.personas["fallback"]
        assert fallback.name == "BK25 Assistant"
        assert fallback.id == "fallback"
    
    def test_get_all_personas(self, persona_manager):
        """Test getting all personas."""
        personas = persona_manager.get_all_personas()
        assert isinstance(personas, list)
        assert len(personas) >= 1
        assert all(isinstance(p, Persona) for p in personas)
    
    def test_get_personas_for_channel(self, persona_manager, sample_persona_data):
        """Test getting personas for specific channel."""
        # Add test persona
        persona = Persona(**sample_persona_data)
        persona_manager.personas[persona.id] = persona
        
        # Test with supported channel
        web_personas = persona_manager.get_personas_for_channel("web")
        assert len(web_personas) >= 2  # fallback + test persona
        
        # Test with unsupported channel
        discord_personas = persona_manager.get_personas_for_channel("discord")
        assert len(discord_personas) >= 1  # fallback (no channel restriction)
    
    def test_switch_persona(self, persona_manager, sample_persona_data):
        """Test switching personas."""
        # Add test persona
        persona = Persona(**sample_persona_data)
        persona_manager.personas[persona.id] = persona
        
        # Switch to test persona
        result = persona_manager.switch_persona("test-persona")
        assert result is not None
        assert result.id == "test-persona"
        assert persona_manager.current_persona.id == "test-persona"
        
        # Try to switch to non-existent persona
        result = persona_manager.switch_persona("nonexistent")
        assert result is None
        assert persona_manager.current_persona.id == "test-persona"  # Should remain unchanged
    
    def test_get_persona(self, persona_manager, sample_persona_data):
        """Test getting persona by ID."""
        # Add test persona
        persona = Persona(**sample_persona_data)
        persona_manager.personas[persona.id] = persona
        
        # Get existing persona
        result = persona_manager.get_persona("test-persona")
        assert result is not None
        assert result.id == "test-persona"
        
        # Get non-existent persona
        result = persona_manager.get_persona("nonexistent")
        assert result is None
    
    def test_build_persona_prompt(self, persona_manager):
        """Test building conversation prompts."""
        # Simple prompt
        prompt = persona_manager.build_persona_prompt("Hello")
        assert "Hello" in prompt
        assert "User:" in prompt
        assert "Assistant:" in prompt
        
        # With conversation history
        history = [
            {"role": "user", "content": "Hi there"},
            {"role": "assistant", "content": "Hello! How can I help?"}
        ]
        prompt_with_history = persona_manager.build_persona_prompt("What's the weather?", history)
        assert "Hi there" in prompt_with_history
        assert "What's the weather?" in prompt_with_history
    
    def test_get_greeting(self, persona_manager, sample_persona_data):
        """Test getting persona greeting."""
        # Default fallback greeting
        greeting = persona_manager.get_greeting()
        assert isinstance(greeting, str)
        assert len(greeting) > 0
        
        # Custom persona greeting
        persona = Persona(**sample_persona_data)
        persona_manager.personas[persona.id] = persona
        persona_manager.switch_persona("test-persona")
        
        custom_greeting = persona_manager.get_greeting()
        assert custom_greeting == "Hello! I'm a test persona."
    
    def test_get_capabilities(self, persona_manager, sample_persona_data):
        """Test getting persona capabilities."""
        capabilities = persona_manager.get_capabilities()
        assert isinstance(capabilities, list)
        
        # Add persona with custom capabilities
        persona = Persona(**sample_persona_data)
        persona_manager.personas[persona.id] = persona
        persona_manager.switch_persona("test-persona")
        
        custom_capabilities = persona_manager.get_capabilities()
        assert "Testing" in custom_capabilities
        assert "Validation" in custom_capabilities
    
    def test_get_examples(self, persona_manager, sample_persona_data):
        """Test getting persona examples."""
        examples = persona_manager.get_examples()
        assert isinstance(examples, list)
        
        # Add persona with custom examples
        persona = Persona(**sample_persona_data)
        persona_manager.personas[persona.id] = persona
        persona_manager.switch_persona("test-persona")
        
        custom_examples = persona_manager.get_examples()
        assert "Run tests" in custom_examples
        assert "Validate functionality" in custom_examples
    
    def test_get_persona_metadata(self, persona_manager, sample_persona_data):
        """Test getting persona metadata."""
        metadata = persona_manager.get_persona_metadata()
        assert metadata is not None
        assert hasattr(metadata, "id")
        assert hasattr(metadata, "name")
        
        # Switch to custom persona
        persona = Persona(**sample_persona_data)
        persona_manager.personas[persona.id] = persona
        persona_manager.switch_persona("test-persona")
        
        custom_metadata = persona_manager.get_persona_metadata()
        assert custom_metadata.id == "test-persona"
        assert custom_metadata.name == "Test Persona"
    
    def test_create_custom_persona(self, persona_manager):
        """Test creating custom personas."""
        persona_data = {
            "name": "Custom Test",
            "description": "A custom test persona",
            "greeting": "Hello from custom!",
            "systemPrompt": "You are a custom persona.",
            "capabilities": ["Custom tasks"],
            "examples": ["Do custom things"]
        }
        
        persona = persona_manager.create_custom_persona(persona_data)
        assert persona.name == "Custom Test"
        assert persona.id in persona_manager.personas
        
        # Test auto-generated ID
        persona_data_no_id = persona_data.copy()
        persona_2 = persona_manager.create_custom_persona(persona_data_no_id)
        assert persona_2.id.startswith("custom_")
        
        # Test validation failure
        invalid_data = {"name": "Invalid"}  # Missing required fields
        with pytest.raises(ValueError):
            persona_manager.create_custom_persona(invalid_data)