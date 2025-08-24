from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .core import BK25Core


class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] | None = None


class GenerateRequest(BaseModel):
    description: str
    platform: str | None = "powershell"
    options: Dict[str, Any] | None = None


class PersonaSwitchRequest(BaseModel):
    personaId: str


class PersonaCreateRequest(BaseModel):
    name: str
    description: str | None = None
    systemPrompt: str
    channels: list[str] | None = None


class ChannelSwitchRequest(BaseModel):
    channelId: str


class GenerateArtifactRequest(BaseModel):
    artifactType: str
    description: str
    options: Dict[str, Any] | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="BK25", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    core = BK25Core()

    @app.on_event("startup")
    async def _startup() -> None:
        await core.initialize()
        await core.check_ollama_connection()

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        return {
            "status": "healthy",
            "version": "1.0.0",
            "tagline": "Agents for whomst? For humans who need automation that works.",
            "ollama": "connected" if core.is_ollama_connected() else "disconnected",
        }

    @app.post("/api/chat")
    async def api_chat(req: ChatRequest) -> Dict[str, Any]:
        if not req.message:
            raise HTTPException(status_code=400, detail="Message is required")
        return await core.process_message(req.message, req.context or {})

    @app.post("/api/generate")
    async def api_generate(req: GenerateRequest) -> Dict[str, Any]:
        if not req.description:
            raise HTTPException(status_code=400, detail="Description is required")
        return await core.generate_automation(req.description, req.platform or "powershell", req.options or {})

    @app.get("/api/personas")
    async def api_personas(channel: str = Query(default="web")) -> Any:
        return core.persona_manager.get_personas_for_channel(channel)

    @app.get("/api/personas/current")
    async def api_personas_current() -> Any:
        return core.persona_manager.get_persona_metadata()

    @app.post("/api/personas/switch")
    async def api_personas_switch(req: PersonaSwitchRequest) -> Any:
        if not req.personaId:
            raise HTTPException(status_code=400, detail="Persona ID is required")
        persona = core.persona_manager.switch_persona(req.personaId)
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona not found")
        return {"success": True, "persona": core.persona_manager.get_persona_metadata()}

    @app.post("/api/personas/create")
    async def api_personas_create(req: PersonaCreateRequest) -> Any:
        if not req.name or not req.systemPrompt:
            raise HTTPException(status_code=400, detail="Name and system prompt are required")
        persona_id = (
            req.name.lower().replace(" ", "-")
            .replace("_", "-")
            .encode("ascii", "ignore")
            .decode()
        )
        persona_id = "".join(ch for ch in persona_id if ch.isalnum() or ch == "-")
        persona_id = "-".join(filter(None, persona_id.split("-")))

        new_persona = {
            "id": persona_id,
            "name": req.name,
            "description": req.description or f"Custom persona: {req.name}",
            "greeting": f"Hello! I'm {req.name}. How can I help you today?",
            "capabilities": ["Custom assistance based on provided instructions"],
            "personality": {
                "tone": "helpful and adaptive",
                "approach": "follows custom instructions",
                "philosophy": "user-defined behavior",
                "motto": "customized for your needs",
            },
            "systemPrompt": req.systemPrompt,
            "examples": ["Ask me anything within my custom instructions"],
            "channels": req.channels or ["web"],
            "custom": True,
        }
        core.persona_manager.personas[persona_id] = new_persona
        return {"success": True, "persona": new_persona}

    @app.get("/api/channels")
    async def api_channels() -> Any:
        return core.channel_manager.get_all_channels()

    @app.get("/api/channels/current")
    async def api_channels_current() -> Any:
        return core.channel_manager.get_current_channel()

    @app.post("/api/channels/switch")
    async def api_channels_switch(req: ChannelSwitchRequest) -> Any:
        if not req.channelId:
            raise HTTPException(status_code=400, detail="Channel ID is required")
        channel = core.channel_manager.switch_channel(req.channelId)
        if channel is None:
            raise HTTPException(status_code=404, detail="Channel not found")
        return {
            "success": True,
            "channel": channel,
            "artifacts": core.channel_manager.get_available_artifacts(),
            "capabilities": core.channel_manager.get_channel_capabilities(),
        }

    @app.post("/api/channels/generate-artifact")
    async def api_channels_generate_artifact(req: GenerateArtifactRequest) -> Any:
        if not req.artifactType or not req.description:
            raise HTTPException(status_code=400, detail="Artifact type and description are required")
        artifact = await core.channel_manager.generate_channel_artifact(req.artifactType, req.description, req.options or {})
        return artifact

    # Serve static UI from old/web if exists
    static_path = Path("./old/web")
    if static_path.exists():
        app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")

    return app


def main() -> None:
    port = int(os.getenv("PORT", "3000"))
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

