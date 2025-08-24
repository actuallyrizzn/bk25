"""
BK25 Core: The heart of automation generation

This is where the magic happens - converting natural language
into working PowerShell, AppleScript, and Bash automation.

Philosophy: Simple, focused, and actually works.
"""

import httpx
from datetime import datetime
from typing import Dict, List, Optional, Any

from .memory import ConversationMemory
from .persona_manager import PersonaManager
from .channel_manager import ChannelManager
from ..generators.powershell import PowerShellGenerator
from ..generators.applescript import AppleScriptGenerator
from ..generators.bash import BashGenerator


class BK25Core:
    """Main BK25 application controller"""
    
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {}
        
        self.config = {
            "ollama_url": config.get("ollama_url", "http://localhost:11434"),
            "model": config.get("model", "llama3.1:8b"),
            "temperature": config.get("temperature", 0.1),  # Low temperature for consistent code generation
            "max_tokens": config.get("max_tokens", 2048),
            **config
        }
        
        # Initialize generators
        self.generators = {
            "powershell": PowerShellGenerator(),
            "applescript": AppleScriptGenerator(),
            "bash": BashGenerator()
        }
        
        # Initialize conversation memory
        self.memory = ConversationMemory()
        
        # Initialize persona manager
        self.persona_manager = PersonaManager()
        
        # Initialize channel manager
        self.channel_manager = ChannelManager()
        
        # Connection status
        self.ollama_connected = False
        
        # HTTP client for API calls
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def initialize(self) -> None:
        """Initialize BK25 (call this after construction)"""
        await self.memory.initialize_database()
        await self.persona_manager.initialize()
        await self.check_ollama_connection()
    
    async def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = await self.http_client.get(f"{self.config['ollama_url']}/api/tags")
            self.ollama_connected = response.status_code == 200
            return self.ollama_connected
        except Exception:
            self.ollama_connected = False
            return False
    
    def is_ollama_connected(self) -> bool:
        """Get connection status"""
        return self.ollama_connected
    
    async def generate_completion(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """Generate completion using Ollama"""
        if not self.ollama_connected:
            await self.check_ollama_connection()
        
        if not self.ollama_connected:
            raise RuntimeError("Ollama is not connected. Please start Ollama and ensure the model is available.")
        
        options = options or {}
        
        try:
            request_data = {
                "model": self.config["model"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": options.get("temperature", self.config["temperature"]),
                    "num_predict": options.get("max_tokens", self.config["max_tokens"])
                }
            }
            
            response = await self.http_client.post(
                f"{self.config['ollama_url']}/api/generate",
                json=request_data
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Ollama API error: {response.status_code} {response.text}")
            
            data = response.json()
            return data.get("response", "")
            
        except Exception as error:
            print(f"Ollama generation error: {error}")
            raise
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a conversational message"""
        try:
            context = context or {}
            
            # Store message in memory
            await self.memory.add_message("user", message, context)
            
            # Determine if this is an automation request
            automation_intent = await self.detect_automation_intent(message)
            
            if automation_intent["is_automation"]:
                # Generate automation script
                automation = await self.generate_automation(
                    message,
                    automation_intent.get("platform", "powershell"),
                    context
                )
                
                response = {
                    "type": "automation",
                    "message": f"I've generated a {automation_intent.get('platform', 'PowerShell')} script for your automation:",
                    "automation": automation,
                    "conversational": True
                }
            else:
                # Regular conversation using current persona
                conversation_history = await self.memory.get_recent_messages(5)
                conversation_prompt = self.persona_manager.build_persona_prompt(message, conversation_history)
                
                ai_response = await self.generate_completion(conversation_prompt)
                
                response = {
                    "type": "conversation",
                    "message": ai_response,
                    "conversational": True
                }
            
            # Store response in memory
            await self.memory.add_message("assistant", response["message"], {"type": response["type"]})
            
            return response
            
        except Exception as error:
            print(f"Message processing error: {error}")
            return {
                "type": "error",
                "message": "I encountered an issue processing your request. Please try again.",
                "error": str(error)
            }
    
    async def detect_automation_intent(self, message: str) -> Dict[str, Any]:
        """Detect if a message is requesting automation"""
        explicit_automation_keywords = [
            "create a script", "generate a script", "write a script",
            "create automation", "generate automation", "write automation",
            "create a powershell", "generate a powershell", "write a powershell",
            "create an applescript", "generate an applescript", "write an applescript",
            "create a bash", "generate a bash", "write a bash"
        ]
        
        platform_keywords = {
            "powershell": ["powershell", "windows", "ps1", ".ps1"],
            "applescript": ["applescript", "macos", "mac", "apple script", "automator"],
            "bash": ["bash script", "shell script", "linux script", "unix script", ".sh"]
        }
        
        lower_message = message.lower()
        
        # Only trigger automation for explicit script requests
        is_automation = any(keyword in lower_message for keyword in explicit_automation_keywords)
        
        # Detect platform
        platform = "powershell"  # default
        for platform_name, keywords in platform_keywords.items():
            if any(keyword in lower_message for keyword in keywords):
                platform = platform_name
                break
        
        return {"is_automation": is_automation, "platform": platform}
    
    async def generate_automation(
        self, 
        description: str, 
        platform: str = "powershell", 
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate automation script"""
        generator = self.generators.get(platform)
        if not generator:
            raise ValueError(f"Unsupported platform: {platform}")
        
        options = options or {}
        
        # Build prompt for script generation
        prompt = generator.build_generation_prompt(description, options)
        
        # Generate script using LLM
        generated_script = await self.generate_completion(prompt, {
            "temperature": 0.1,  # Very low temperature for consistent code
            "max_tokens": 4096   # More tokens for longer scripts
        })
        
        # Parse and validate the generated script
        parsed_script = generator.parse_generated_script(generated_script)
        
        # Add metadata
        automation = {
            "platform": platform,
            "description": description,
            "script": parsed_script["script"],
            "documentation": parsed_script.get("documentation", ""),
            "filename": parsed_script.get("filename", ""),
            "generated_at": datetime.now().isoformat(),
            "bk25_version": "1.0.0"
        }
        
        # Store in memory for future reference
        await self.memory.add_automation(automation)
        
        return automation
    
    def build_conversation_prompt(self, message: str, conversation_history: List[Dict[str, Any]] = None) -> str:
        """Build conversation prompt with context"""
        conversation_history = conversation_history or []
        
        system_prompt = """You are BK25, an AI assistant that specializes in generating enterprise automation scripts and helping with conversational AI tasks.

Your personality:
- Helpful and professional, but not overly formal
- Focused on practical solutions that actually work
- Skeptical of overly complex enterprise solutions
- Believes in "agents for whomst?" - technology should serve humans

Your capabilities:
- Generate PowerShell, AppleScript, and Bash automation scripts
- Help with RPA (Robotic Process Automation) tasks
- Provide conversational AI assistance
- Explain technical concepts clearly

Guidelines:
- Be concise and practical
- If someone asks for automation, offer to generate a script
- Always explain what your generated scripts do
- Prefer simple solutions over complex ones
- Remember that your goal is to help humans automate repetitive tasks"""
        
        prompt = system_prompt + "\n\nConversation history:\n"
        
        # Add conversation history
        for msg in conversation_history:
            prompt += f"{msg['role']}: {msg['content']}\n"
        
        prompt += f"\nUser: {message}\nAssistant:"
        
        return prompt
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        memory_stats = await self.memory.get_stats()
        return {
            "ollama_connected": self.ollama_connected,
            "ollama_url": self.config["ollama_url"],
            "model": self.config["model"],
            "personas_loaded": len(self.persona_manager.personas),
            "current_persona": self.persona_manager.current_persona.name if self.persona_manager.current_persona else None,
            "current_channel": self.channel_manager.current_channel,
            "channels_available": len(self.channel_manager.channels),
            "generators_available": list(self.generators.keys()),
            **memory_stats
        }
    
    async def close(self) -> None:
        """Close connections and cleanup"""
        await self.memory.close()
        await self.http_client.aclose()