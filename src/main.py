#!/usr/bin/env python3
"""
BK25: Generate enterprise automation without enterprise complexity

A love letter to the conversational AI community
From Peter Swimm (original Botkit PM) and the Toilville team

"Agents for whomst?" - For humans who need automation that works.
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Optional, Dict, Any

# Import BK25 core components
from src.core.bk25 import BK25Core
from src.core.persona_manager import PersonaManager
from src.core.channel_manager import ChannelManager
from src.config import config

# Initialize FastAPI app
app = FastAPI(
    title="BK25 - Multi-Persona Channel Simulator",
    description="Generate enterprise automation without enterprise complexity",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (web interface)
web_path = Path(__file__).parent.parent / "web"
if web_path.exists():
    app.mount("/", StaticFiles(directory=str(web_path), html=True), name="web")

# Global BK25 instance
bk25: Optional[BK25Core] = None

@app.on_event("startup")
async def startup_event():
    """Initialize BK25 on startup"""
    global bk25
    
    try:
        # Initialize BK25 core
        bk25 = BK25Core({
            "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
            "model": os.getenv("BK25_MODEL", "llama3.1:8b"),
            "port": int(os.getenv("PORT", "8000")),
            "personas_path": str(config.personas_path)
        })
        
        await bk25.initialize()
        
        print("🚀 BK25 Python Edition starting up...")
        print("📝 Migration Status: Phase 2 - Persona System & Memory")
        print(f"🎭 Personas loaded: {len(bk25.persona_manager.get_all_personas())}")
        print(f"📺 Channels available: {len(bk25.channel_manager.get_all_channels())}")
        
    except Exception as error:
        print(f"❌ Failed to initialize BK25: {error}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    status = bk25.get_system_status()
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "tagline": "Agents for whomst? For humans who need automation that works.",
        "migration_status": "Phase 2 - Persona System & Memory",
        "ollama": "connected" if status["ollama_connected"] else "disconnected",
        "personas_loaded": status["personas_loaded"],
        "channels_available": status["channels_available"],
        "conversations_active": status["conversations_active"]
    }

@app.get("/api/personas")
async def get_personas(channel: str = "web"):
    """Get available personas for a channel"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        personas = bk25.persona_manager.get_personas_for_channel(channel)
        return {
            "personas": [
                {
                    "id": persona.id,
                    "name": persona.name,
                    "description": persona.description,
                    "greeting": persona.greeting,
                    "capabilities": persona.capabilities,
                    "personality": {
                        "tone": persona.personality.tone,
                        "approach": persona.personality.approach,
                        "philosophy": persona.personality.philosophy,
                        "motto": persona.personality.motto
                    },
                    "examples": persona.examples,
                    "channels": persona.channels
                }
                for persona in personas
            ],
            "current_persona": bk25.persona_manager.get_current_persona().id if bk25.persona_manager.get_current_persona() else None,
            "total_count": len(personas)
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error loading personas: {str(error)}")

@app.get("/api/personas/{persona_id}")
async def get_persona(persona_id: str):
    """Get specific persona by ID"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    persona = bk25.persona_manager.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    
    return {
        "id": persona.id,
        "name": persona.name,
        "description": persona.description,
        "greeting": persona.greeting,
        "capabilities": persona.capabilities,
        "personality": {
            "tone": persona.personality.tone,
            "approach": persona.personality.approach,
            "philosophy": persona.personality.philosophy,
            "motto": persona.personality.motto
        },
        "examples": persona.examples,
        "channels": persona.channels
    }

@app.post("/api/personas/{persona_id}/switch")
async def switch_persona(persona_id: str):
    """Switch to a different persona"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    persona = bk25.switch_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    
    return {
        "message": f"Switched to persona: {persona['name']}",
        "persona": persona
    }

@app.get("/api/channels")
async def get_channels():
    """Get available channels"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        channels = bk25.channel_manager.get_all_channels()
        return {
            "channels": [
                {
                    "id": channel.id,
                    "name": channel.name,
                    "description": channel.description,
                    "capabilities": {
                        name: {
                            "supported": cap.supported,
                            "description": cap.description
                        }
                        for name, cap in channel.capabilities.items()
                    },
                    "artifact_types": channel.artifact_types,
                    "metadata": channel.metadata
                }
                for channel in channels
            ],
            "current_channel": bk25.channel_manager.current_channel,
            "total_count": len(channels)
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error loading channels: {str(error)}")

@app.get("/api/channels/{channel_id}")
async def get_channel(channel_id: str):
    """Get specific channel by ID"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    channel = bk25.channel_manager.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
    
    return {
        "id": channel.id,
        "name": channel.name,
        "description": channel.description,
        "capabilities": {
            name: {
                "supported": cap.supported,
                "description": cap.description
            }
            for name, cap in channel.capabilities.items()
        },
        "artifact_types": channel.artifact_types,
        "metadata": channel.metadata
    }

@app.post("/api/channels/{channel_id}/switch")
async def switch_channel(channel_id: str):
    """Switch to a different channel"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    channel = bk25.switch_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
    
    return {
        "message": f"Switched to channel: {channel['name']}",
        "channel": channel
    }

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """Chat processing endpoint"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        body = await request.json()
        message = body.get("message", "")
        conversation_id = body.get("conversation_id", "default")
        persona_id = body.get("persona_id")
        channel_id = body.get("channel_id")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Process the message
        result = await bk25.process_message(message, conversation_id, persona_id, channel_id)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(error)}")

@app.post("/api/generate")
async def generate_automation(request: Request):
    """Automation generation endpoint"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        body = await request.json()
        prompt = body.get("prompt", "")
        conversation_id = body.get("conversation_id", "default")
        persona_id = body.get("persona_id")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Generate automation using the specified persona
        if persona_id:
            bk25.switch_persona(persona_id)
        
        # Generate completion
        response = await bk25.generate_completion(prompt, conversation_id)
        
        return {
            "generated_code": response,
            "persona": bk25.persona_manager.get_current_persona().id if bk25.persona_manager.get_current_persona() else None,
            "conversation_id": conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error generating automation: {str(error)}")

@app.get("/api/conversations")
async def get_conversations():
    """Get all conversation summaries"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        conversations = bk25.get_all_conversations()
        return {
            "conversations": conversations,
            "total_count": len(conversations)
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error loading conversations: {str(error)}")

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, limit: Optional[int] = None):
    """Get conversation history"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        history = bk25.get_conversation_history(conversation_id, limit)
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "total_messages": len(history)
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error loading conversation: {str(error)}")

@app.get("/api/system/status")
async def get_system_status():
    """Get overall system status"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        return bk25.get_system_status()
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(error)}")

@app.get("/api/system/memory")
async def get_memory_info():
    """Get memory information"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        return bk25.get_memory_info()
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting memory info: {str(error)}")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors gracefully"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested resource was not found",
            "migration_status": "Phase 2 - Persona System & Memory"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors gracefully"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "BK25 encountered an issue processing your request",
            "migration_status": "Phase 2 - Persona System & Memory"
        }
    )

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("BK25_HOST", "0.0.0.0")
    port = int(os.getenv("BK25_PORT", "8000"))
    reload = os.getenv("BK25_RELOAD", "false").lower() == "true"
    
    print(f"🌐 Starting BK25 on {host}:{port}")
    print(f"🔄 Reload mode: {reload}")
    print(f"📚 API docs available at: http://{host}:{port}/docs")
    
    # Start the server
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
