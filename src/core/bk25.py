"""
BK25 Core System

Main application controller that orchestrates all BK25 components:
- Persona management
- Channel simulation
- Conversation memory
- Code generation
- LLM integration
"""

import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.core.persona_manager import PersonaManager
from src.core.channel_manager import ChannelManager
from src.core.memory import ConversationMemory
from src.core.code_generator import CodeGenerator
from src.core.llm_integration import LLMManager
from src.core.prompt_engineering import PromptEngineer
from src.logging_config import get_logger

logger = get_logger("bk25_core")

class BK25Core:
    """Main BK25 application controller"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize core components
        self.persona_manager = PersonaManager(
            personas_path=self.config.get('personas_path', './personas')
        )
        self.channel_manager = ChannelManager()
        self.memory = ConversationMemory(
            max_conversations=self.config.get('max_conversations', 100),
            max_messages_per_conversation=self.config.get('max_messages_per_conversation', 50)
        )
        self.code_generator = CodeGenerator()
        
        # LLM system
        self.llm_manager = LLMManager(self.config)
        self.prompt_engineer = PromptEngineer()
        
        # LLM configuration
        self.ollama_url = self.config.get('ollama_url', 'http://localhost:11434')
        self.model = self.config.get('model', 'llama3.1:8b')
        self.temperature = self.config.get('temperature', 0.1)
        self.max_tokens = self.config.get('max_tokens', 2048)
        
        # Connection status
        self.ollama_connected = False
        
        self.logger = get_logger("bk25_core")
        self.logger.info("🚀 BK25 Core initialized")
    
    async def initialize(self) -> None:
        """Initialize all BK25 components"""
        try:
            self.logger.info("🔧 Initializing BK25 Core...")
            
            # Initialize persona manager
            await self.persona_manager.initialize()
            
            # Test Ollama connection
            await self.test_ollama_connection()
            
            self.logger.info("✅ BK25 Core initialization complete")
            
        except Exception as error:
            self.logger.error(f"❌ BK25 Core initialization failed: {error}")
            raise
    
    async def test_ollama_connection(self) -> bool:
        """Test connection to Ollama service"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    self.ollama_connected = True
                    self.logger.info(f"✅ Ollama connected at {self.ollama_url}")
                    return True
                else:
                    self.ollama_connected = False
                    self.logger.warning(f"⚠️ Ollama responded with status {response.status_code}")
                    return False
                    
        except Exception as error:
            self.ollama_connected = False
            self.logger.warning(f"⚠️ Ollama connection failed: {error}")
            return False
    
    def is_ollama_connected(self) -> bool:
        """Check if Ollama is connected"""
        return self.ollama_connected
    
    async def generate_completion(self, prompt: str, conversation_id: Optional[str] = None) -> str:
        """Generate LLM completion using current persona"""
        if not self.ollama_connected:
            return "⚠️ Ollama not connected. Please check your Ollama service."
        
        try:
            import httpx
            
            # Build persona-specific prompt
            persona_prompt = self.persona_manager.build_persona_prompt(prompt)
            
            # Add conversation context if available
            if conversation_id:
                context = self.memory.get_conversation_context(conversation_id)
                if context:
                    persona_prompt = f"{context}\n\n{persona_prompt}"
            
            # Prepare Ollama request
            request_data = {
                "model": self.model,
                "prompt": persona_prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    completion = result.get('response', 'No response generated')
                    
                    # Store in conversation memory if conversation_id provided
                    if conversation_id:
                        self.memory.add_message(conversation_id, "user", prompt)
                        self.memory.add_message(conversation_id, "assistant", completion)
                    
                    return completion
                else:
                    error_msg = f"Ollama API error: {response.status_code}"
                    self.logger.error(error_msg)
                    return error_msg
                    
        except Exception as error:
            error_msg = f"Error generating completion: {error}"
            self.logger.error(error_msg)
            return error_msg
    
    async def process_message(self, message: str, conversation_id: str, persona_id: Optional[str] = None, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a user message and generate response"""
        try:
            # Switch persona if specified
            if persona_id:
                self.persona_manager.switch_persona(persona_id)
            
            # Switch channel if specified
            if channel_id:
                self.channel_manager.switch_channel(channel_id)
            
            # Get or create conversation
            conversation = self.memory.get_conversation(conversation_id)
            if not conversation:
                current_persona = self.persona_manager.get_current_persona()
                current_channel = self.channel_manager.get_current_channel()
                conversation = self.memory.create_conversation(
                    conversation_id,
                    current_persona.id,
                    current_channel.id
                )
            
            # Generate response
            response = await self.generate_completion(message, conversation_id)
            
            # Get current persona and channel info
            current_persona = self.persona_manager.get_current_persona()
            current_channel = self.channel_manager.get_current_channel()
            
            return {
                'response': response,
                'persona': {
                    'id': current_persona.id,
                    'name': current_persona.name,
                    'greeting': current_persona.greeting
                },
                'channel': {
                    'id': current_channel.id,
                    'name': current_channel.name
                },
                'conversation_id': conversation_id,
                'timestamp': conversation.updated_at
            }
            
        except Exception as error:
            self.logger.error(f"Error processing message: {error}")
            return {
                'error': str(error),
                'response': 'Sorry, I encountered an error processing your message.'
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'ollama_connected': self.ollama_connected,
            'ollama_url': self.ollama_url,
            'model': self.model,
            'personas_loaded': len(self.persona_manager.get_all_personas()),
            'channels_available': len(self.channel_manager.get_all_channels()),
            'conversations_active': len(self.memory.conversations),
            'current_persona': self.persona_manager.get_current_persona().id if self.persona_manager.get_current_persona() else None,
            'current_channel': self.channel_manager.current_channel
        }
    
    def get_persona_info(self, persona_id: Optional[str] = None) -> Dict[str, Any]:
        """Get persona information"""
        if persona_id:
            persona = self.persona_manager.get_persona(persona_id)
            return persona.to_dict() if persona else {}
        else:
            return self.persona_manager.to_dict()
    
    def get_channel_info(self, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """Get channel information"""
        if channel_id:
            return self.channel_manager.get_channel_summary(channel_id)
        else:
            return self.channel_manager.get_channel_stats()
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        return self.memory.get_memory_stats()
    
    async def reload_personas(self) -> None:
        """Reload personas from disk"""
        await self.persona_manager.reload_personas()
        self.logger.info("🔄 Personas reloaded")
    
    def switch_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Switch to a different persona"""
        persona = self.persona_manager.switch_persona(persona_id)
        if persona:
            return persona.to_dict()
        return None
    
    def switch_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Switch to a different channel"""
        channel = self.channel_manager.switch_channel(channel_id)
        if channel:
            return self.channel_manager.get_channel_summary(channel_id)
        return None
    
    def get_conversation_history(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history"""
        messages = self.memory.get_conversation_history(conversation_id, limit)
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp,
                'metadata': msg.metadata
            }
            for msg in messages
        ]
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """Get all conversation summaries"""
        return self.memory.get_all_conversation_summaries()
    
    # Code Generation Methods
    async def generate_script(self, description: str, platform: str = 'auto', options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a script using the code generator"""
        try:
            from src.core.code_generator import GenerationRequest
            
            request = GenerationRequest(
                description=description,
                platform=platform,
                options=options
            )
            
            result = await self.code_generator.generate_script(
                request, 
                self.llm_manager, 
                self.prompt_engineer
            )
            
            return {
                'success': result.success,
                'script': result.script,
                'filename': result.filename,
                'documentation': result.documentation,
                'validation': {
                    'is_valid': result.validation.is_valid if result.validation else False,
                    'issues': result.validation.issues if result.validation else [],
                    'suggestions': result.validation.suggestions if result.validation else []
                } if result.validation else None,
                'error': result.error,
                'metadata': result.metadata
            }
            
        except Exception as error:
            self.logger.error(f"Script generation failed: {error}")
            return {
                'success': False,
                'error': f"Script generation error: {str(error)}"
            }
    
    def get_code_generation_info(self) -> Dict[str, Any]:
        """Get information about code generation capabilities"""
        return {
            'supported_platforms': self.code_generator.get_supported_platforms(),
            'statistics': self.code_generator.get_generation_statistics(),
            'automation_patterns': list(self.code_generator.automation_patterns.keys())
        }
    
    def get_platform_info(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific platform"""
        return self.code_generator.get_platform_info(platform)
    
    def get_automation_suggestions(self, description: str) -> List[Dict[str, Any]]:
        """Get automation suggestions based on description"""
        return self.code_generator.get_automation_suggestions(description)
    
    # LLM Management Methods
    async def get_llm_status(self) -> Dict[str, Any]:
        """Get LLM system status and provider information"""
        try:
            provider_status = await self.llm_manager.test_providers()
            available_providers = self.llm_manager.get_available_providers()
            
            return {
                'providers_configured': available_providers,
                'provider_status': provider_status,
                'total_providers': len(available_providers),
                'active_providers': sum(1 for status in provider_status.values() if status)
            }
        except Exception as error:
            self.logger.error(f"Error getting LLM status: {error}")
            return {
                'error': f"Failed to get LLM status: {str(error)}"
            }
    
    def get_llm_provider_info(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific LLM provider"""
        return self.llm_manager.get_provider_info(provider_name)
    
    async def test_llm_generation(self, prompt: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """Test LLM generation with a simple prompt"""
        try:
            from src.core.llm_integration import LLMRequest
            
            request = LLMRequest(
                prompt=prompt,
                model=self.model,
                temperature=0.1,
                max_tokens=100
            )
            
            response = await self.llm_manager.generate(request, preferred_provider=provider)
            
            return {
                'success': response.success,
                'content': response.content,
                'error': response.error,
                'provider': response.metadata.get('provider', 'unknown') if response.metadata else 'unknown',
                'usage': response.usage
            }
            
        except Exception as error:
            self.logger.error(f"LLM test generation failed: {error}")
            return {
                'success': False,
                'error': f"Test generation error: {str(error)}"
            }
    
    # Advanced Script Features
    async def improve_script(self, script: str, feedback: str, platform: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Improve an existing script based on feedback"""
        try:
            # Create prompt context
            from src.core.prompt_engineering import PromptContext
            
            context = PromptContext(
                persona_id=options.get('persona_id', 'default') if options else 'default',
                persona_name='Script Improvement Expert',
                persona_description='Specialized in iterative script improvement',
                persona_capabilities=['script_improvement', 'code_review'],
                channel_id=options.get('channel', 'web') if options else 'web',
                channel_name='Web Interface',
                conversation_history=[],
                user_preferences=options.get('preferences') if options else None
            )
            
            # Create improvement prompt
            prompt = self.prompt_engineer.create_iterative_improvement_prompt(
                original_script=script,
                feedback=feedback,
                platform=platform,
                context=context
            )
            
            # Generate improved script
            from src.core.llm_integration import LLMRequest
            
            llm_request = LLMRequest(
                prompt=f"{prompt.system_message}\n\n{prompt.user_prompt}\n\n{prompt.output_format}",
                model=self.model,
                temperature=0.1,
                max_tokens=options.get('max_tokens', 2048) if options else 2048
            )
            
            llm_response = await self.llm_manager.generate(llm_request)
            
            if not llm_response.success:
                return {
                    'success': False,
                    'error': f"LLM improvement failed: {llm_response.error}"
                }
            
            # Parse the improved script
            generator = self.code_generator.generators.get(platform)
            if not generator:
                return {
                    'success': False,
                    'error': f"Unsupported platform: {platform}"
                }
            
            parsed = generator.parse_generated_script(llm_response.content)
            
            return {
                'success': True,
                'improved_script': parsed['script'],
                'filename': parsed['filename'],
                'documentation': parsed['documentation'],
                'metadata': {
                    'improvement_method': 'llm',
                    'provider': llm_response.metadata.get('provider', 'unknown'),
                    'model': llm_response.metadata.get('model', 'unknown'),
                    'usage': llm_response.usage
                }
            }
            
        except Exception as error:
            self.logger.error(f"Script improvement failed: {error}")
            return {
                'success': False,
                'error': f"Script improvement error: {str(error)}"
            }
    
    async def validate_script(self, script: str, platform: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate and analyze a script for quality and improvements"""
        try:
            # Create prompt context
            from src.core.prompt_engineering import PromptContext
            
            context = PromptContext(
                persona_id=options.get('persona_id', 'default') if options else 'default',
                persona_name='Code Quality Expert',
                persona_description='Specialized in code review and validation',
                persona_capabilities=['code_review', 'quality_assessment'],
                channel_id=options.get('channel', 'web') if options else 'web',
                channel_name='Web Interface',
                conversation_history=[],
                user_preferences=options.get('preferences') if options else None
            )
            
            # Create validation prompt
            prompt = self.prompt_engineer.create_validation_prompt(
                script=script,
                platform=platform,
                context=context
            )
            
            # Generate validation analysis
            from src.core.llm_integration import LLMRequest
            
            llm_request = LLMRequest(
                prompt=f"{prompt.system_message}\n\n{prompt.user_prompt}",
                model=self.model,
                temperature=0.1,
                max_tokens=options.get('max_tokens', 1024) if options else 1024
            )
            
            llm_response = await self.llm_manager.generate(llm_request)
            
            if not llm_response.success:
                return {
                    'success': False,
                    'error': f"LLM validation failed: {llm_response.error}"
                }
            
            return {
                'success': True,
                'validation_analysis': llm_response.content,
                'metadata': {
                    'validation_method': 'llm',
                    'provider': llm_response.metadata.get('provider', 'unknown'),
                    'model': llm_response.metadata.get('model', 'unknown'),
                    'usage': llm_response.usage
                }
            }
            
        except Exception as error:
            self.logger.error(f"Script validation failed: {error}")
            return {
                'success': False,
                'error': f"Script validation error: {str(error)}"
            }
