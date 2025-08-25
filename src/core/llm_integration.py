"""
BK25 LLM Integration

Handles integration with various LLM providers for intelligent script generation.
Supports Ollama (local), OpenAI, and other providers.
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path

from ..logging_config import get_logger

logger = get_logger("llm_integration")

@dataclass
class LLMRequest:
    """LLM generation request"""
    prompt: str
    model: str
    temperature: float = 0.1
    max_tokens: int = 2048
    system_message: Optional[str] = None
    context: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

@dataclass
class LLMResponse:
    """LLM generation response"""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(f"llm_provider_{self.__class__.__name__.lower()}")
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate content using the LLM provider"""
        raise NotImplementedError("Subclasses must implement generate method")
    
    def is_available(self) -> bool:
        """Check if the provider is available"""
        raise NotImplementedError("Subclasses must implement is_available method")

class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('ollama_url', 'http://localhost:11434')
        self.default_model = config.get('model', 'llama3.1:8b')
        self.timeout = config.get('timeout', 30.0)
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate content using Ollama"""
        try:
            import httpx
            
            # Build the full prompt
            full_prompt = self._build_prompt(request)
            
            # Prepare Ollama request
            ollama_request = {
                "model": request.model or self.default_model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            }
            
            # Add any additional options
            if request.options:
                ollama_request["options"].update(request.options)
            
            self.logger.info(f"Generating with Ollama model: {ollama_request['model']}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=ollama_request,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('response', '')
                    
                    # Extract usage information if available
                    usage = {}
                    if 'eval_count' in result:
                        usage['tokens_generated'] = result['eval_count']
                    if 'prompt_eval_count' in result:
                        usage['tokens_prompt'] = result['prompt_eval_count']
                    
                    return LLMResponse(
                        success=True,
                        content=content,
                        usage=usage,
                        metadata={
                            'provider': 'ollama',
                            'model': ollama_request['model'],
                            'response_time': result.get('total_duration', 0)
                        }
                    )
                else:
                    error_msg = f"Ollama API error: {response.status_code}"
                    self.logger.error(f"{error_msg} - {response.text}")
                    return LLMResponse(
                        success=False,
                        error=error_msg
                    )
                    
        except Exception as error:
            self.logger.error(f"Ollama generation failed: {error}")
            return LLMResponse(
                success=False,
                error=f"Ollama generation error: {str(error)}"
            )
    
    def _build_prompt(self, request: LLMRequest) -> str:
        """Build the full prompt for Ollama"""
        parts = []
        
        # Add system message if provided
        if request.system_message:
            parts.append(f"System: {request.system_message}")
        
        # Add context if provided
        if request.context:
            parts.append(f"Context: {request.context}")
        
        # Add main prompt
        parts.append(f"User: {request.prompt}")
        
        # Add response instruction
        parts.append("Assistant: ")
        
        return "\n\n".join(parts)
    
    async def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
                
        except Exception:
            return False

class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('openai_api_key')
        self.base_url = config.get('openai_base_url', 'https://api.openai.com/v1')
        self.default_model = config.get('model', 'gpt-3.5-turbo')
        self.timeout = config.get('timeout', 30.0)
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate content using OpenAI"""
        if not self.api_key:
            return LLMResponse(
                success=False,
                error="OpenAI API key not configured"
            )
        
        try:
            import httpx
            
            # Build messages for chat completion
            messages = []
            
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            
            if request.context:
                messages.append({"role": "user", "content": f"Context: {request.context}"})
            
            messages.append({"role": "user", "content": request.prompt})
            
            # Prepare OpenAI request
            openai_request = {
                "model": request.model or self.default_model,
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
            
            # Add any additional options
            if request.options:
                openai_request.update(request.options)
            
            self.logger.info(f"Generating with OpenAI model: {openai_request['model']}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=openai_request,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Extract usage information
                    usage = result.get('usage', {})
                    
                    return LLMResponse(
                        success=True,
                        content=content,
                        usage=usage,
                        metadata={
                            'provider': 'openai',
                            'model': openai_request['model'],
                            'finish_reason': result['choices'][0].get('finish_reason')
                        }
                    )
                else:
                    error_msg = f"OpenAI API error: {response.status_code}"
                    self.logger.error(f"{error_msg} - {response.text}")
                    return LLMResponse(
                        success=False,
                        error=error_msg
                    )
                    
        except Exception as error:
            self.logger.error(f"OpenAI generation failed: {error}")
            return LLMResponse(
                success=False,
                error=f"OpenAI generation error: {str(error)}"
            )
    
    async def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return bool(self.api_key)

class LLMManager:
    """Manages multiple LLM providers and selects the best one"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger("llm_manager")
        
        # Debug: Print what we received
        self.logger.info(f"LLM Manager received config keys: {list(config.keys())}")
        self.logger.info(f"LLM Manager config provider: {config.get('provider')}")
        self.logger.info(f"LLM Manager ollama_url: {config.get('ollama_url')}")
        self.logger.info(f"LLM Manager openai_api_key: {'SET' if config.get('openai_api_key') else 'NOT SET'}")
        
        # Initialize providers
        self.providers = {}
        
        # Add Ollama provider
        if config.get('ollama_url'):
            self.logger.info(f"Adding Ollama provider with URL: {config.get('ollama_url')}")
            self.providers['ollama'] = OllamaProvider(config)
        
        # Add OpenAI provider
        openai_key = config.get('openai_api_key')
        self.logger.info(f"OpenAI key check: '{openai_key}' (type: {type(openai_key)}, length: {len(openai_key) if openai_key else 0})")
        self.logger.info(f"OpenAI key truthy check: {bool(openai_key)}")
        
        if openai_key:
            self.logger.info(f"Adding OpenAI provider with model: {config.get('openai_model', 'gpt-4o')}")
            self.providers['openai'] = OpenAIProvider(config)
        else:
            self.logger.warning("OpenAI provider not added - API key is empty/falsy")
        
        self.logger.info(f"LLM Manager initialized with {len(self.providers)} providers: {list(self.providers.keys())}")
    
    async def generate(self, request: LLMRequest, preferred_provider: Optional[str] = None) -> LLMResponse:
        """Generate content using the best available provider"""
        try:
            # Check if preferred provider is available
            if preferred_provider and preferred_provider in self.providers:
                provider = self.providers[preferred_provider]
                if await provider.is_available():
                    self.logger.info(f"Using preferred provider: {preferred_provider}")
                    return await provider.generate(request)
            
            # Find the best available provider
            available_providers = []
            for name, provider in self.providers.items():
                if await provider.is_available():
                    available_providers.append((name, provider))
            
            if not available_providers:
                return LLMResponse(
                    success=False,
                    error="No LLM providers available"
                )
            
            # Select the first available provider (could implement priority logic here)
            selected_name, selected_provider = available_providers[0]
            self.logger.info(f"Using provider: {selected_name}")
            
            return await selected_provider.generate(request)
            
        except Exception as error:
            self.logger.error(f"LLM generation failed: {error}")
            return LLMResponse(
                success=False,
                error=f"LLM generation error: {str(error)}"
            )
    
    def get_available_providers(self) -> List[str]:
        """Get list of configured providers"""
        return list(self.providers.keys())
    
    async def test_providers(self) -> Dict[str, bool]:
        """Test all providers and return availability status"""
        results = {}
        
        for name, provider in self.providers.items():
            try:
                results[name] = await provider.is_available()
            except Exception as error:
                self.logger.error(f"Error testing provider {name}: {error}")
                results[name] = False
        
        return results
    
    def get_provider_info(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific provider"""
        provider = self.providers.get(provider_name)
        if not provider:
            return None
        
        info = {
            'name': provider_name,
            'class': provider.__class__.__name__,
            'config_keys': list(provider.config.keys())
        }
        
        # Add provider-specific information
        if isinstance(provider, OllamaProvider):
            info['base_url'] = provider.base_url
            info['default_model'] = provider.default_model
        elif isinstance(provider, OpenAIProvider):
            info['base_url'] = provider.base_url
            info['default_model'] = provider.default_model
            info['has_api_key'] = bool(provider.api_key)
        
        return info
