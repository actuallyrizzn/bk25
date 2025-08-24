#!/usr/bin/env python3
"""
BK25: Generate enterprise automation without enterprise complexity

A love letter to the conversational AI community
From Peter Swimm (original Botkit PM) and the Toilville team

"Agents for whomst?" - For humans who need automation that works.
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path

# Import BK25 core components (will be implemented in Phase 1)
# from src.core.bk25 import BK25Core
# from src.core.persona_manager import PersonaManager
# from src.core.channel_manager import ChannelManager

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

# Global BK25 instance (will be initialized in Phase 1)
# bk25 = None

@app.on_event("startup")
async def startup_event():
    """Initialize BK25 on startup"""
    # TODO: Initialize BK25 core components
    # global bk25
    # bk25 = BK25Core({
    #     "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
    #     "model": os.getenv("BK25_MODEL", "llama3.1:8b"),
    #     "port": int(os.getenv("PORT", "8000"))
    # })
    # await bk25.initialize()
    print("🚀 BK25 Python Edition starting up...")
    print("📝 Migration in progress - Phase 1: Foundation & Core Infrastructure")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "tagline": "Agents for whomst? For humans who need automation that works.",
        "migration_status": "Phase 1 - Foundation & Core Infrastructure",
        "ollama": "not_implemented_yet"  # Will be implemented in Phase 1
    }

@app.get("/api/personas")
async def get_personas(channel: str = "web"):
    """Get available personas for a channel"""
    # TODO: Implement persona loading in Phase 1
    return {
        "message": "Persona system not yet implemented",
        "status": "migration_in_progress",
        "phase": "Phase 1 - Foundation & Core Infrastructure"
    }

@app.get("/api/channels")
async def get_channels():
    """Get available channels"""
    # TODO: Implement channel system in Phase 1
    return {
        "message": "Channel system not yet implemented",
        "status": "migration_in_progress",
        "phase": "Phase 1 - Foundation & Core Infrastructure"
    }

@app.post("/api/chat")
async def chat_endpoint():
    """Chat processing endpoint"""
    # TODO: Implement chat processing in Phase 5
    return {
        "message": "Chat processing not yet implemented",
        "status": "migration_in_progress",
        "phase": "Phase 5 - LLM Integration & Chat Processing"
    }

@app.post("/api/generate")
async def generate_automation():
    """Automation generation endpoint"""
    # TODO: Implement automation generation in Phase 4
    return {
        "message": "Automation generation not yet implemented",
        "status": "migration_in_progress",
        "phase": "Phase 4 - Code Generation System"
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors gracefully"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested resource was not found",
            "migration_status": "Phase 1 - Foundation & Core Infrastructure"
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
            "migration_status": "Phase 1 - Foundation & Core Infrastructure"
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
