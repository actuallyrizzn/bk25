from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx

from .generators.powershell import PowerShellGenerator
from .generators.applescript import AppleScriptGenerator
from .generators.bash import BashGenerator
from .memory import ConversationMemory
from .persona_manager import PersonaManager
from .channel_manager import ChannelManager


class BK25Core:
    def __init__(self, ollama_url: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.1, max_tokens: int = 2048) -> None:
        self.config: Dict[str, Any] = {
            "ollama_url": ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434"),
            "model": model or os.getenv("BK25_MODEL", "llama3.1:8b"),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        self.generators: Dict[str, Any] = {
            "powershell": PowerShellGenerator(),
            "applescript": AppleScriptGenerator(),
            "bash": BashGenerator(),
        }

        self.memory = ConversationMemory()
        self.persona_manager = PersonaManager()
        self.channel_manager = ChannelManager()
        self._ollama_connected: bool = False
        self._mock_mode: bool = os.getenv("BK25_MOCK", "0") in ("1", "true", "True")

    async def initialize(self) -> None:
        await self.persona_manager.initialize()

    async def check_ollama_connection(self) -> bool:
        if self._mock_mode:
            self._ollama_connected = False
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.config['ollama_url']}/api/tags")
                self._ollama_connected = resp.is_success
                return self._ollama_connected
        except Exception:
            self._ollama_connected = False
            return False

    def is_ollama_connected(self) -> bool:
        return self._ollama_connected

    async def generate_completion(self, prompt: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        if self._mock_mode:
            # Deterministic mock response for tests/CI
            return f"[MOCK COMPLETION]\n{prompt[:200]}\n..."

        if not self._ollama_connected:
            await self.check_ollama_connection()
        if not self._ollama_connected:
            raise RuntimeError("Ollama is not connected. Start Ollama and ensure the model is available.")

        payload = {
            "model": self.config["model"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else self.config["temperature"],
                "num_predict": max_tokens if max_tokens is not None else self.config["max_tokens"],
            },
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.config['ollama_url']}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        await self.memory.add_message("user", message, context)

        detection = await self.detect_automation_intent(message)
        if detection[0]:
            platform = detection[1] or "powershell"
            automation = await self.generate_automation(message, platform, context)
            response = {
                "type": "automation",
                "message": f"I've generated a {platform} script for your automation:",
                "automation": automation,
                "conversational": True,
            }
        else:
            history = await self.memory.get_recent_messages(5)
            persona_prompt = self.persona_manager.build_persona_prompt(message, history)
            ai_text = await self.generate_completion(persona_prompt)
            response = {
                "type": "conversation",
                "message": ai_text,
                "conversational": True,
            }

        await self.memory.add_message("assistant", response["message"], {"type": response["type"]})
        return response

    async def detect_automation_intent(self, message: str) -> Tuple[bool, str]:
        explicit_keywords = [
            "create a script", "generate a script", "write a script",
            "create automation", "generate automation", "write automation",
            "create a powershell", "generate a powershell", "write a powershell",
            "create an applescript", "generate an applescript", "write an applescript",
            "create a bash", "generate a bash", "write a bash",
        ]
        platform_keywords = {
            "powershell": ["powershell", "windows", "ps1", ".ps1"],
            "applescript": ["applescript", "macos", "mac", "apple script", "automator"],
            "bash": ["bash script", "shell script", "linux script", "unix script", ".sh"],
        }
        lower = message.lower()
        is_automation = any(k in lower for k in explicit_keywords)
        platform = "powershell"
        for name, keys in platform_keywords.items():
            if any(k in lower for k in keys):
                platform = name
                break
        return is_automation, platform

    async def generate_automation(self, description: str, platform: str = "powershell", options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        options = options or {}
        generator = self.generators.get(platform)
        if generator is None:
            raise ValueError(f"Unsupported platform: {platform}")

        prompt = generator.build_generation_prompt(description, options)
        generated = await self.generate_completion(prompt, temperature=0.1, max_tokens=4096)
        parsed = generator.parse_generated_script(generated)
        automation = {
            "platform": platform,
            "description": description,
            "script": parsed["script"],
            "documentation": parsed.get("documentation"),
            "filename": parsed.get("filename"),
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "bk25Version": "1.0.0",
        }
        await self.memory.add_automation(automation)
        return automation

