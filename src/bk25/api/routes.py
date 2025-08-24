"""
BK25 API Routes

FastAPI route definitions for the BK25 application.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ..models.chat import ChatRequest, ChatResponse, HealthResponse, ErrorResponse
from ..models.persona import PersonaMetadata, CreatePersonaRequest
from ..models.channel import Channel


def create_router(bk25_core) -> APIRouter:
    """Create API router with BK25 core instance"""
    router = APIRouter()
    
    @router.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            tagline="Agents for whomst? For humans who need automation that works.",
            ollama="connected" if bk25_core.is_ollama_connected() else "disconnected"
        )
    
    @router.post("/api/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        """Main conversation endpoint"""
        try:
            # Switch persona if specified
            if request.persona:
                bk25_core.persona_manager.switch_persona(request.persona)
            
            # Switch channel if specified
            if request.channel:
                bk25_core.channel_manager.switch_channel(request.channel)
            
            # Process the message
            response = await bk25_core.process_message(request.message, request.context)
            
            # Add persona and channel info
            response["persona_info"] = bk25_core.persona_manager.get_persona_metadata()
            response["channel_info"] = {
                "id": bk25_core.channel_manager.current_channel,
                "name": bk25_core.channel_manager.get_current_channel().name if bk25_core.channel_manager.get_current_channel() else None,
                "artifacts": bk25_core.channel_manager.get_available_artifacts(),
                "capabilities": bk25_core.channel_manager.get_channel_capabilities()
            }
            
            return ChatResponse(**response)
            
        except Exception as error:
            print(f"Chat error: {error}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Internal server error",
                    "message": "BK25 encountered an issue processing your request"
                }
            )
    
    @router.post("/api/generate")
    async def generate_automation(
        description: str,
        platform: str = "powershell",
        options: Dict[str, Any] = None
    ):
        """Generate automation script endpoint"""
        try:
            if not description:
                raise HTTPException(status_code=400, detail="Description is required")
            
            automation = await bk25_core.generate_automation(description, platform, options or {})
            return automation
            
        except Exception as error:
            print(f"Generation error: {error}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Generation failed",
                    "message": "Could not generate automation script"
                }
            )
    
    # Persona management endpoints
    @router.get("/api/personas")
    async def get_personas(channel: str = Query("web")):
        """Get available personas for a channel"""
        try:
            personas = bk25_core.persona_manager.get_personas_for_channel(channel)
            return [persona.model_dump() for persona in personas]
        except Exception as error:
            print(f"Personas error: {error}")
            raise HTTPException(status_code=500, detail="Failed to get personas")
    
    @router.get("/api/personas/current", response_model=PersonaMetadata)
    async def get_current_persona():
        """Get current persona metadata"""
        try:
            metadata = bk25_core.persona_manager.get_persona_metadata()
            if metadata:
                return metadata
            else:
                raise HTTPException(status_code=404, detail="No current persona")
        except Exception as error:
            print(f"Current persona error: {error}")
            raise HTTPException(status_code=500, detail="Failed to get current persona")
    
    @router.post("/api/personas/switch")
    async def switch_persona(request: dict):
        """Switch to a different persona"""
        persona_id = request.get("persona_id")
        try:
            if not persona_id:
                raise HTTPException(status_code=400, detail="Persona ID is required")
            
            persona = bk25_core.persona_manager.switch_persona(persona_id)
            if persona:
                return {
                    "success": True,
                    "persona": bk25_core.persona_manager.get_persona_metadata().model_dump() if bk25_core.persona_manager.get_persona_metadata() else None
                }
            else:
                raise HTTPException(status_code=404, detail="Persona not found")
        except HTTPException:
            raise
        except Exception as error:
            print(f"Switch persona error: {error}")
            raise HTTPException(status_code=500, detail="Failed to switch persona")
    
    @router.post("/api/personas/create")
    async def create_persona(request: CreatePersonaRequest):
        """Create a custom persona"""
        try:
            # Create persona ID from name
            persona_id = request.name.lower().replace(" ", "_").replace("-", "_")
            persona_id = "".join(c for c in persona_id if c.isalnum() or c == "_")
            
            persona_data = {
                "id": persona_id,
                "name": request.name,
                "description": request.description or f"Custom persona: {request.name}",
                "greeting": f"Hello! I'm {request.name}. How can I help you today?",
                "systemPrompt": request.system_prompt,
                "capabilities": request.capabilities or ["Custom assistance based on provided instructions"],
                "examples": request.examples or ["Ask me anything within my custom instructions"],
                "channels": request.channels or ["web"],
                "personality": request.personality or {
                    "tone": "helpful and adaptive",
                    "approach": "follows custom instructions",
                    "philosophy": "user-defined behavior",
                    "motto": "customized for your needs"
                }
            }
            
            persona = bk25_core.persona_manager.create_custom_persona(persona_data)
            return {
                "success": True,
                "persona": persona.model_dump()
            }
            
        except Exception as error:
            print(f"Create persona error: {error}")
            raise HTTPException(status_code=500, detail="Failed to create persona")
    
    # Channel management endpoints
    @router.get("/api/channels")
    async def get_channels():
        """Get all available channels"""
        try:
            channels = bk25_core.channel_manager.get_all_channels()
            return [channel.model_dump() for channel in channels]
        except Exception as error:
            print(f"Channels error: {error}")
            raise HTTPException(status_code=500, detail="Failed to get channels")
    
    @router.get("/api/channels/current")
    async def get_current_channel():
        """Get current channel information"""
        try:
            current_channel = bk25_core.channel_manager.get_current_channel()
            if current_channel:
                return current_channel.model_dump()
            else:
                raise HTTPException(status_code=404, detail="No current channel")
        except Exception as error:
            print(f"Current channel error: {error}")
            raise HTTPException(status_code=500, detail="Failed to get current channel")
    
    @router.post("/api/channels/switch")
    async def switch_channel(request: dict):
        """Switch to a different channel"""
        channel_id = request.get("channel_id")
        try:
            if not channel_id:
                raise HTTPException(status_code=400, detail="Channel ID is required")
            
            channel = bk25_core.channel_manager.switch_channel(channel_id)
            if channel:
                return {
                    "success": True,
                    "channel": channel.model_dump(),
                    "artifacts": bk25_core.channel_manager.get_available_artifacts(),
                    "capabilities": bk25_core.channel_manager.get_channel_capabilities()
                }
            else:
                raise HTTPException(status_code=404, detail="Channel not found")
        except HTTPException:
            raise
        except Exception as error:
            print(f"Switch channel error: {error}")
            raise HTTPException(status_code=500, detail="Failed to switch channel")
    
    @router.post("/api/channels/generate-artifact")
    async def generate_channel_artifact(
        artifact_type: str,
        description: str,
        options: Dict[str, Any] = None
    ):
        """Generate channel-specific artifact"""
        try:
            if not artifact_type or not description:
                raise HTTPException(
                    status_code=400,
                    detail="Artifact type and description are required"
                )
            
            artifact = await bk25_core.channel_manager.generate_channel_artifact(
                artifact_type, description, options or {}
            )
            return artifact
            
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error))
        except Exception as error:
            print(f"Generate artifact error: {error}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Failed to generate artifact",
                    "message": str(error)
                }
            )
    
    @router.get("/api/stats")
    async def get_stats():
        """Get system statistics"""
        try:
            stats = await bk25_core.get_stats()
            return stats
        except Exception as error:
            print(f"Stats error: {error}")
            raise HTTPException(status_code=500, detail="Failed to get stats")
    
    return router