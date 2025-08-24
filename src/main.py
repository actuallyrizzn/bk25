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
from typing import Optional, Dict, Any, List

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
        
        # Start execution monitoring system
        await bk25.start_execution_monitoring()
        
        print("🚀 BK25 Python Edition starting up...")
        print("📝 Migration Status: Phase 5 - Script Execution & Monitoring")
        print(f"🎭 Personas loaded: {len(bk25.persona_manager.get_all_personas())}")
        print(f"📺 Channels available: {len(bk25.channel_manager.get_all_channels())}")
        print(f"⚙️ Code generators: {len(bk25.code_generator.get_supported_platforms())} platforms")
        print(f"🤖 LLM providers: {len(bk25.llm_manager.get_available_providers())} configured")
        print(f"🚀 Script execution: available with monitoring")
        
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
            "migration_status": "Phase 5 - Script Execution & Monitoring",
            "ollama": "connected" if status["ollama_connected"] else "disconnected",
            "personas_loaded": status["personas_loaded"],
            "channels_available": status["channels_available"],
            "conversations_active": status["conversations_active"],
            "code_generation": "available",
            "llm_integration": "available",
            "script_execution": "available"
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

# Code Generation Endpoints
@app.post("/api/generate/script")
async def generate_script(request: Request):
    """Generate a script based on description and platform"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        body = await request.json()
        description = body.get('description')
        platform = body.get('platform', 'auto')
        options = body.get('options')
        
        if not description:
            raise HTTPException(status_code=400, detail="Description is required")
        
        result = await bk25.generate_script(description, platform, options)
        return result
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(error)}")

@app.get("/api/generate/platforms")
async def get_supported_platforms():
    """Get supported code generation platforms"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        return bk25.get_code_generation_info()
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting platform info: {str(error)}")

@app.get("/api/generate/platform/{platform}")
async def get_platform_info(platform: str):
    """Get detailed information about a specific platform"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        info = bk25.get_platform_info(platform)
        if not info:
            raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
        
        return info
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting platform info: {str(error)}")

@app.post("/api/generate/suggestions")
async def get_automation_suggestions(request: Request):
    """Get automation suggestions based on description"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        body = await request.json()
        description = body.get('description')
        if not description:
            raise HTTPException(status_code=400, detail="Description is required")
        
        suggestions = bk25.get_automation_suggestions(description)
        return {"suggestions": suggestions}
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(error)}")

# Advanced LLM Features Endpoints
@app.get("/api/llm/status")
async def get_llm_status():
    """Get LLM system status and provider information"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        status = await bk25.get_llm_status()
        return status
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting LLM status: {str(error)}")

@app.get("/api/llm/providers/{provider_name}")
async def get_llm_provider_info(provider_name: str):
    """Get detailed information about a specific LLM provider"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        info = bk25.get_llm_provider_info(provider_name)
        if not info:
            raise HTTPException(status_code=404, detail=f"Provider {provider_name} not found")
        
        return info
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting provider info: {str(error)}")

@app.post("/api/llm/test")
async def test_llm_generation(request: Request):
    """Test LLM generation with a simple prompt"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        body = await request.json()
        prompt = body.get('prompt')
        provider = body.get('provider')
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        result = await bk25.test_llm_generation(prompt, provider)
        return result
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error testing LLM: {str(error)}")

@app.post("/api/scripts/improve")
async def improve_script(request: Request):
    """Improve an existing script based on feedback"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        body = await request.json()
        script = body.get('script')
        feedback = body.get('feedback')
        platform = body.get('platform')
        options = body.get('options')
        
        if not script or not feedback or not platform:
            raise HTTPException(status_code=400, detail="Script, feedback, and platform are required")
        
        result = await bk25.improve_script(script, feedback, platform, options)
        return result
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error improving script: {str(error)}")

@app.post("/api/scripts/validate")
async def validate_script(request: Request):
    """Validate and analyze a script for quality and improvements"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        body = await request.json()
        script = body.get('script')
        platform = body.get('platform')
        options = body.get('options')
        
        if not script or not platform:
            raise HTTPException(status_code=400, detail="Script and platform are required")
        
        result = await bk25.validate_script(script, platform, options)
        return result
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error validating script: {str(error)}")

# Script Execution Endpoints
@app.post("/api/execute/script")
async def execute_script(request: Request):
    """Execute a script directly"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        body = await request.json()
        script = body.get('script')
        platform = body.get('platform')
        filename = body.get('filename')
        working_directory = body.get('working_directory')
        timeout = body.get('timeout', 300)
        policy = body.get('policy', 'safe')
        environment = body.get('environment')
        
        if not script or not platform:
            raise HTTPException(status_code=400, detail="Script and platform are required")
        
        result = await bk25.execute_script(
            script=script,
            platform=platform,
            filename=filename,
            working_directory=working_directory,
            timeout=timeout,
            policy=policy,
            environment=environment
        )
        return result
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error executing script: {str(error)}")

@app.post("/api/execute/task")
async def submit_execution_task(request: Request):
    """Submit a script execution task"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        body = await request.json()
        name = body.get('name')
        description = body.get('description')
        script = body.get('script')
        platform = body.get('platform')
        priority = body.get('priority', 'normal')
        tags = body.get('tags')
        metadata = body.get('metadata')
        
        if not name or not description or not script or not platform:
            raise HTTPException(status_code=400, detail="Name, description, script, and platform are required")
        
        result = await bk25.submit_execution_task(
            name=name,
            description=description,
            script=script,
            platform=platform,
            priority=priority,
            tags=tags,
            metadata=metadata
        )
        return result
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error submitting task: {str(error)}")

@app.get("/api/execute/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of an execution task"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        result = await bk25.get_task_status(task_id)
        return result
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting task status: {str(error)}")

@app.delete("/api/execute/task/{task_id}")
async def cancel_execution_task(task_id: str):
    """Cancel an execution task"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        result = await bk25.cancel_execution_task(task_id)
        return result
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(error)}")

@app.get("/api/execute/history")
async def get_execution_history(
    limit: int = 100,
    status: Optional[str] = None,
    platform: Optional[str] = None,
    tag: Optional[str] = None
):
    """Get execution history with optional filters"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        result = await bk25.get_execution_history(
            limit=limit,
            status_filter=status,
            platform_filter=platform,
            tag_filter=tag
        )
        return result
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting execution history: {str(error)}")

@app.get("/api/execute/statistics")
async def get_execution_statistics():
    """Get system execution statistics"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        result = await bk25.get_system_statistics()
        return result
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(error)}")

@app.get("/api/execute/running")
async def get_running_tasks():
    """Get all currently running tasks"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        tasks = await bk25.execution_monitor.get_running_tasks()
        
        # Convert to serializable format
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'status': task.status.value,
                'priority': task.priority.value,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'execution_time': task.execution_time,
                'tags': task.tags,
                'metadata': task.metadata
            })
        
        return {
            'success': True,
            'running_tasks': task_list,
            'total_count': len(task_list)
        }
        
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting running tasks: {str(error)}")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors gracefully"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested resource was not found",
            "migration_status": "Phase 5 - Script Execution & Monitoring"
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
            "migration_status": "Phase 5 - Script Execution & Monitoring"
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
