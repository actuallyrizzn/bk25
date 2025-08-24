"""
BK25 Main Application

FastAPI application entry point for the Python port of BK25.
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bk25.core.bk25_core import BK25Core
from bk25.api.routes import create_router


# Initialize BK25 core
bk25_config = {
    "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
    "model": os.getenv("BK25_MODEL", "llama3.1:8b"),
    "port": int(os.getenv("PORT", "3000"))
}

bk25_core = BK25Core(bk25_config)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🤖 BK25: Generate enterprise automation without enterprise complexity")
    print('"Agents for whomst?" - For humans who need automation that works.')
    print("\nInitializing BK25...")
    
    try:
        await bk25_core.initialize()
        print("✅ BK25 initialized successfully")
        
        # Check Ollama connection
        connected = await bk25_core.check_ollama_connection()
        if connected:
            print("✅ Ollama connected successfully")
            print(f"📝 Using model: {bk25_core.config['model']}")
        else:
            print("❌ Ollama not connected")
            print("💡 Start Ollama with: ollama serve")
            print("💡 Pull model with: ollama pull llama3.1:8b")
            
    except Exception as e:
        print(f"❌ Failed to initialize BK25: {e}")
        sys.exit(1)
    
    yield
    
    # Shutdown
    print("\n👋 BK25 shutting down gracefully...")
    await bk25_core.close()

# Create FastAPI app
app = FastAPI(
    title="BK25",
    description="Generate enterprise automation without enterprise complexity",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create and include router
router = create_router(bk25_core)
app.include_router(router)

# Serve static files (web interface)
web_dir = Path(__file__).parent.parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")
    
    @app.get("/")
    async def read_root():
        """Redirect root to the web interface"""
        return RedirectResponse(url="/static/index.html")





def main():
    """Main entry point for running the application"""
    port = bk25_config["port"]
    
    print(f"""
🤖 BK25: Generate enterprise automation without enterprise complexity

Starting server on http://localhost:{port}
Web interface: http://localhost:{port}
API docs: http://localhost:{port}/docs
API endpoint: http://localhost:{port}/api/chat

"Agents for whomst?" - For humans who need automation that works.
""")
    
    uvicorn.run(
        "bk25.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to True for development
        log_level="info"
    )


if __name__ == "__main__":
    main()