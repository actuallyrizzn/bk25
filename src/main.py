#!/usr/bin/env python3
"""
BK25: Generate enterprise automation without enterprise complexity

A love letter to the conversational AI community
From Peter Swimm (original Botkit PM) and the Toilville team

"Agents for whomst?" - For humans who need automation that works.
"""

import os
import uvicorn
import time
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

# FastAPI app will be initialized after the lifespan function

# Settings management endpoints will be defined after the app is created



# Global BK25 instance
bk25: Optional[BK25Core] = None

# Modern lifespan event handler (replaces deprecated on_event)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for BK25 startup and shutdown"""
    global bk25
    
    # Startup
    try:
        print("[STARTUP] BK25 Python Edition starting up...")
        
        # Debug: Print current LLM configuration
        print(f"[DEBUG] Current LLM provider: {config.llm.provider}")
        print(f"[DEBUG] OpenAI API key set: {'YES' if config.llm.openai_api_key else 'NO'}")
        print(f"[DEBUG] OpenAI API key length: {len(config.llm.openai_api_key) if config.llm.openai_api_key else 0}")
        print(f"[DEBUG] Ollama URL: {config.llm.ollama_url}")
        
        # Initialize BK25 core with full LLM configuration
        bk25_config = {
            "port": int(os.getenv("PORT", "8000")),
            "personas_path": str(config.paths.personas_path),
            # LLM configuration from config module
            "provider": config.llm.provider,
            "ollama_url": config.llm.ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434"),
            "ollama_model": config.llm.ollama_model or os.getenv("BK25_MODEL", "llama3.1:8b"),
            "openai_api_key": config.llm.openai_api_key,
            "openai_model": config.llm.openai_model,
            "openai_base_url": config.llm.openai_base_url,
            "anthropic_api_key": config.llm.anthropic_api_key,
            "anthropic_model": config.llm.anthropic_model,
            "anthropic_base_url": config.llm.anthropic_base_url,
            "google_api_key": config.llm.google_api_key,
            "google_model": config.llm.google_model,
            "custom_api_url": config.llm.custom_api_url,
            "custom_api_key": config.llm.custom_api_key,
            "custom_model": config.llm.custom_model,
            "temperature": config.llm.temperature,
            "max_tokens": config.llm.max_tokens,
            "timeout": config.llm.timeout
        }
        
        print(f"[DEBUG] BK25 config keys: {list(bk25_config.keys())}")
        print(f"[DEBUG] LLM provider in config: {bk25_config.get('provider')}")
        print(f"[DEBUG] OpenAI API key in config: {'SET' if bk25_config.get('openai_api_key') else 'NOT SET'}")
        
        bk25 = BK25Core(bk25_config)
        
        await bk25.initialize()
        
        # Start execution monitoring system
        await bk25.start_execution_monitoring()
        
        print("[STATUS] Migration Status: Phase 5 - Script Execution & Monitoring")
        print(f"[PERSONAS] Personas loaded: {len(bk25.persona_manager.get_all_personas())}")
        print(f"[CHANNELS] Channels available: {len(bk25.channel_manager.get_all_channels())}")
        print(f"[GENERATORS] Code generators: {len(bk25.code_generator.get_supported_platforms())} platforms")
        print(f"[LLM] LLM providers: {len(bk25.llm_manager.get_available_providers())} configured")
        print(f"[EXEC] Script execution: available with monitoring")
        
    except Exception as error:
        print(f"[ERROR] Failed to initialize BK25: {error}")
        raise
    
    yield
    
    # Shutdown
    try:
        if bk25:
            print("[SHUTDOWN] Shutting down BK25...")
            await bk25.shutdown_execution_monitoring()
            print("[SHUTDOWN] BK25 shutdown complete")
    except Exception as error:
        print(f"[ERROR] Error during shutdown: {error}")

# Update FastAPI app to use lifespan
app = FastAPI(
    title="BK25 - Multi-Persona Channel Simulator",
    description="Generate enterprise automation without enterprise complexity",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.server.cors_origins or ["*"],  # Use config or default to all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (web interface)
web_path = Path(__file__).parent.parent / "web"
print(f"[DEBUG] Web path: {web_path}")
print(f"[DEBUG] Web path exists: {web_path.exists()}")

if web_path.exists():
    print(f"[DEBUG] Mounting web interface at /web")
    app.mount("/web", StaticFiles(directory=str(web_path), html=True), name="web")
    
    # Serve the main web interface at root
    @app.get("/")
    async def root():
        """Serve the main BK25 web interface"""
        from fastapi.responses import FileResponse
        print(f"[DEBUG] Serving root route, file: {web_path / 'index.html'}")
        return FileResponse(str(web_path / "index.html"))
    
    # Alternative: redirect to web interface
    @app.get("/app")
    async def app_redirect():
        """Redirect to the main application"""
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/web/")
    
    # Simple info route
    @app.get("/info")
    async def info():
        """Get basic app information"""
        return {
            "app": "BK25 - Multi-Persona Channel Simulator",
            "version": "1.0.0",
            "status": "running",
            "web_interface": "/web/",
            "health": "/health"
        }

# Settings management endpoints
@app.get("/api/settings")
async def get_settings():
    """Get current LLM settings"""
    try:
        # Get settings from the configuration system
        return config.get_llm_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting settings: {str(e)}")

@app.post("/api/settings")
async def save_settings(settings: dict):
    """Save LLM settings"""
    try:
        # Validate required fields based on provider
        provider = settings.get("provider")
        if not provider:
            raise HTTPException(status_code=400, detail="Provider is required")
        
        if provider == "ollama":
            if not settings.get("ollama", {}).get("url"):
                raise HTTPException(status_code=400, detail="Ollama URL is required")
            if not settings.get("ollama", {}).get("model"):
                raise HTTPException(status_code=400, detail="Ollama model is required")
        elif provider in ["openai", "anthropic", "google"]:
            provider_names = {"openai": "OpenAI", "anthropic": "Anthropic", "google": "Google"}
            provider_name = provider_names.get(provider, provider.title())
            if not settings.get(provider, {}).get("apiKey"):
                raise HTTPException(status_code=400, detail=f"{provider_name} API key is required")
            if not settings.get(provider, {}).get("model"):
                raise HTTPException(status_code=400, detail=f"{provider_name} model is required")
        elif provider == "custom":
            if not settings.get("custom", {}).get("url"):
                raise HTTPException(status_code=400, detail="Custom API URL is required")
            if not settings.get("custom", {}).get("apiKey"):
                raise HTTPException(status_code=400, detail="Custom API key is required")
        
        # Save settings to the configuration system
        config.update_llm_settings(settings)
        print(f"[INFO] Settings updated: {provider} provider configured")
        
        return {"message": "Settings saved successfully", "provider": provider}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving settings: {str(e)}")

@app.post("/api/settings/test")
async def test_connection(settings: dict):
    """Test LLM connection with current settings"""
    try:
        provider = settings.get("provider")
        if not provider:
            raise HTTPException(status_code=400, detail="Provider is required")
        
        start_time = time.time()
        
        if provider == "ollama":
            # Test Ollama connection
            ollama_settings = settings.get("ollama", {})
            url = ollama_settings.get("url", "http://localhost:11434")
            model = ollama_settings.get("model", "llama3.1:8b")
            
            import httpx
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{url}/api/tags", timeout=10)
                    if response.status_code == 200:
                        models = response.json()
                        # Check if the specified model is available
                        available_models = [model['name'] for model in models.get('models', [])]
                        if model in available_models:
                            response_time = int((time.time() - start_time) * 1000)
                            return {
                                "success": True,
                                "model": model,
                                "responseTime": response_time,
                                "availableModels": available_models,
                                "message": f"Successfully connected to Ollama at {url}"
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"Model '{model}' not found. Available models: {', '.join(available_models)}",
                                "message": f"Model '{model}' not found in available models"
                            }
                    else:
                        return {"success": False, "error": f"Ollama server returned status {response.status_code}", "message": "Ollama server error"}
                except httpx.ConnectError:
                    return {"success": False, "error": "Cannot connect to Ollama server. Is it running?", "message": "Connection failed"}
                except httpx.TimeoutException:
                    return {"success": False, "error": "Connection timeout. Check if Ollama is running and accessible.", "message": "Connection timeout"}
                except Exception as e:
                    return {"success": False, "error": f"Connection error: {str(e)}", "message": "Unexpected error"}
        
        elif provider in ["openai", "anthropic", "google"]:
            # For now, just validate the API key format
            provider_settings = settings.get(provider, {})
            api_key = provider_settings.get("apiKey", "")
            provider_names = {"openai": "OpenAI", "anthropic": "Anthropic", "google": "Google"}
            provider_name = provider_names.get(provider, provider.title())
            
            if not api_key or len(api_key) < 10:
                return {"success": False, "error": f"Invalid {provider_name} API key format", "message": f"API key validation failed for {provider_name}"}
            
            # In a real implementation, you'd make a test API call
            response_time = int((time.time() - start_time) * 1000)
            return {
                "success": True,
                "model": provider_settings.get("model", "unknown"),
                "responseTime": response_time,
                "message": f"{provider_name} API key format validated. Test API call not implemented yet."
            }
        
        elif provider == "custom":
            # Validate custom API URL format
            custom_settings = settings.get("custom", {})
            url = custom_settings.get("url", "")
            if not url or not url.startswith(("http://", "https://")):
                return {"success": False, "error": "Invalid custom API URL format", "message": "URL validation failed"}
            
            response_time = int((time.time() - start_time) * 1000)
            return {
                "success": True,
                "model": custom_settings.get("model", "custom"),
                "responseTime": response_time,
                "message": "Custom API URL format validated. Test API call not implemented yet."
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing connection: {str(e)}")

# Debug route to test routing
@app.get("/debug")
async def debug():
    """Debug route to test routing"""
    return {
        "message": "Debug route working",
        "web_path": str(web_path),
        "web_exists": web_path.exists(),
        "files": [f.name for f in web_path.iterdir()] if web_path.exists() else []
    }

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
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error loading personas: {str(error)}")

@app.get("/api/personas/current")
async def get_current_persona():
    """Get current active persona"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        current_persona = bk25.persona_manager.get_current_persona()
        if not current_persona:
            raise HTTPException(status_code=404, detail="No current persona set")
        
        return {
            "id": current_persona.id,
            "name": current_persona.name,
            "description": current_persona.description,
            "personality": {
                "tone": current_persona.personality.tone,
                "approach": current_persona.personality.approach,
                "philosophy": current_persona.personality.philosophy,
                "motto": current_persona.personality.motto
            },
            "capabilities": current_persona.capabilities,
            "examples": current_persona.examples,
            "channels": current_persona.channels
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting current persona: {str(error)}")

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

@app.post("/api/personas/create")
async def create_persona(request: Request):
    """Create a new custom persona"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        body = await request.json()
        
        # Validate required fields
        required_fields = ["name", "description", "personality"]
        for field in required_fields:
            if field not in body:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create persona data structure
        persona_data = {
            "id": body.get("id", f"custom-{body['name'].lower().replace(' ', '-')}"),
            "name": body["name"],
            "description": body["description"],
            "personality": body["personality"],
            "capabilities": body.get("capabilities", {}),
            "examples": body.get("examples", []),
            "channels": body.get("channels", ["web"]),
            "greeting": body.get("greeting", f"Hello! I'm {body['name']}. How can I help you today?")
        }
        
        # Add to persona manager
        new_persona = bk25.persona_manager.add_custom_persona(persona_data)
        if not new_persona:
            raise HTTPException(status_code=500, detail="Failed to create persona")
        
        return {
            "message": f"Persona {persona_data['name']} created successfully",
            "persona": {
                "id": new_persona.id,
                "name": new_persona.name,
                "description": new_persona.description,
                "personality": {
                    "tone": new_persona.personality.tone,
                    "approach": new_persona.personality.approach,
                    "philosophy": new_persona.personality.philosophy,
                    "motto": new_persona.personality.motto
                },
                "capabilities": new_persona.capabilities,
                "examples": new_persona.examples,
                "channels": new_persona.channels
            }
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error creating persona: {str(error)}")

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
                            "supported": cap.supported if hasattr(cap, 'supported') else cap.get('supported', False),
                            "description": cap.description if hasattr(cap, 'description') else cap.get('description', '')
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
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error loading channels: {str(error)}")

@app.get("/api/channels/current")
async def get_current_channel():
    """Get current active channel"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        current_channel = bk25.channel_manager.get_current_channel()
        if not current_channel:
            raise HTTPException(status_code=404, detail="No current channel set")
        
        return {
            "id": current_channel.id,
            "name": current_channel.name,
            "description": current_channel.description,
            "capabilities": {
                name: {
                    "supported": cap.supported,
                    "description": cap.description
                }
                for name, cap in current_channel.capabilities.items()
            },
            "artifact_types": current_channel.artifact_types,
            "metadata": current_channel.metadata
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting current channel: {str(error)}")

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
                "supported": cap.supported if hasattr(cap, 'supported') else cap.get('supported', False),
                "description": cap.description if hasattr(cap, 'description') else cap.get('description', '')
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
    """Chat processing endpoint with code extraction"""
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
        
        # Extract code blocks from the response if present
        response_text = result.get("response", "")
        extracted_code = None
        
        if response_text and "```" in response_text:
            # SIMPLE STRING REPLACEMENT - find the code block and replace it
            start = response_text.find("```")
            end = response_text.find("```", start + 3)
            
            if start != -1 and end != -1:
                # Extract the code content
                code_section = response_text[start:end + 3]
                
                # Get language from first line after ```
                lines = code_section.split('\n')
                language = "script"
                if len(lines) > 1:
                    first_line = lines[1].strip()
                    if first_line and first_line.isalpha():
                        language = first_line
                
                # Extract just the code (remove the ``` markers and language line)
                code_content = code_section[3:]  # Remove first ```
                if code_content.startswith('\n'):
                    code_content = code_content[1:]
                if '\n' in code_content:
                    code_content = code_content.split('\n', 1)[1]  # Skip language line
                code_content = code_content[:-3]  # Remove last ```
                
                extracted_code = {
                    "language": language,
                    "code": code_content.strip(),
                    "filename": f"Generated {language.capitalize()} Script"
                }
                
                # REPLACE THE CODE BLOCK WITH THE WIDGET
                widget = f'<div class="mt-2 p-2 bg-info bg-opacity-10 rounded border border-info"><div class="d-flex align-items-center text-info"><i class="bi bi-code-slash me-2"></i><span class="small">→ <strong>{language.upper()}</strong> script generated! Check the output panel to the right.</span></div></div>'
                
                response_text = response_text[:start] + widget + response_text[end + 3:]
                
                print(f"[DEBUG] Replaced code block with widget: {language}")
        
        # Return the modified response
        enhanced_result = {
            **result,
            "response": response_text,  # This now has the widget instead of code
            "extracted_code": extracted_code
        }
        
        print(f"[DEBUG] Chat response: has_code={extracted_code is not None}")
        if extracted_code:
            print(f"[DEBUG] Code block: {extracted_code['language']} ({len(extracted_code['code'])} chars)")
        
        return enhanced_result
        
    except HTTPException:
        raise
    except Exception as error:
        print(f"[ERROR] Chat endpoint error: {error}")
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
    except HTTPException:
        raise
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
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error loading conversation: {str(error)}")

@app.get("/api/system/status")
async def get_system_status():
    """Get overall system status"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        return bk25.get_system_status()
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(error)}")

@app.get("/api/system/memory")
async def get_memory_info():
    """Get memory information"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        return bk25.get_memory_info()
    except HTTPException:
        raise
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
        
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(error)}")

@app.get("/api/generate/platforms")
async def get_supported_platforms():
    """Get supported code generation platforms"""
    if not bk25:
        raise HTTPException(status_code=503, detail="BK25 not initialized")
    
    try:
        return bk25.get_code_generation_info()
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
        
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
        
    except HTTPException:
        raise
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
        
    except HTTPException:
        raise
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
        
    except HTTPException:
        raise
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
        
    except HTTPException:
        raise
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
        
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
        
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error getting running tasks: {str(error)}")

# Custom 404 handler removed - let FastAPI handle 404 errors naturally

# Custom 500 handler removed - let FastAPI handle 500 errors naturally

# Catch-all route for debugging (only for non-API routes to avoid intercepting API tests)
@app.get("/{path:path}")
async def catch_all(path: str):
    """Catch-all route for debugging"""
    # Don't intercept API routes - let FastAPI handle 404s naturally
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    return {
        "message": f"Route not found: /{path}",
        "available_routes": [
            "/",
            "/web/",
            "/app",
            "/info",
            "/debug",
            "/health",
            "/docs"
        ]
    }

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="BK25 Python Edition")
    parser.add_argument("--host", help="Host to bind to (overrides config)")
    parser.add_argument("--port", type=int, help="Port to bind to (overrides config)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (overrides config)")
    args = parser.parse_args()
    
    # Get configuration from config system, with command line overrides
    host = args.host or config.server.host
    port = args.port or config.server.port
    reload = args.reload if args.reload is not None else config.server.reload
    
    print(f"[SERVER] Starting BK25 on {host}:{port}")
    print(f"[RELOAD] Reload mode: {reload}")
    print(f"[CONFIG] Using configuration from: {config.paths.config_path}")
    print(f"[DOCS] API docs available at: http://{host}:{port}/docs")
    
    # Start the server
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
