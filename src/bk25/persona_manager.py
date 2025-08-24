from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class PersonaManager:
    def __init__(self, personas_path: str = "./old/personas") -> None:
        self.personas_path = Path(personas_path)
        self.personas: Dict[str, Dict[str, Any]] = {}
        self.current_persona: Optional[Dict[str, Any]] = None

    async def initialize(self) -> None:
        await self.load_all_personas()
        self.current_persona = (
            self.personas.get("vanilla")
            or self.personas.get("default")
            or (next(iter(self.personas.values())) if self.personas else None)
        )

    async def load_all_personas(self) -> None:
        self.personas.clear()
        if not self.personas_path.exists():
            self.personas_path.mkdir(parents=True, exist_ok=True)
        for file in sorted(self.personas_path.glob("*.json")):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                if self.validate_persona(data):
                    self.personas[data["id"]] = data
            except Exception:
                # Skip invalid persona files
                continue

    def validate_persona(self, persona: Dict[str, Any]) -> bool:
        required = ["id", "name", "description", "greeting", "systemPrompt"]
        return all(k in persona and persona[k] for k in required)

    def get_all_personas(self) -> List[Dict[str, Any]]:
        return list(self.personas.values())

    def get_personas_for_channel(self, channel: str) -> List[Dict[str, Any]]:
        return [p for p in self.personas.values() if ("channels" not in p) or (channel in p.get("channels", []))]

    def get_current_persona(self) -> Optional[Dict[str, Any]]:
        return self.current_persona

    def switch_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        persona = self.personas.get(persona_id)
        if persona is not None:
            self.current_persona = persona
            return persona
        return None

    def get_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        return self.personas.get(persona_id)

    def build_persona_prompt(self, message: str, conversation_history: List[Dict[str, Any]]) -> str:
        persona = self.current_persona
        if not persona:
            return f"User: {message}\nAssistant:"
        prompt = str(persona.get("systemPrompt", "")) + "\n\nConversation history:\n"
        for msg in conversation_history:
            prompt += f"{msg['role']}: {msg['content']}\n"
        prompt += f"\nUser: {message}\nAssistant:"
        return prompt

    def get_persona_metadata(self) -> Optional[Dict[str, Any]]:
        if not self.current_persona:
            return None
        p = self.current_persona
        return {
            "id": p.get("id"),
            "name": p.get("name"),
            "description": p.get("description"),
            "greeting": p.get("greeting"),
            "capabilities": p.get("capabilities"),
            "examples": p.get("examples"),
            "personality": p.get("personality"),
        }

