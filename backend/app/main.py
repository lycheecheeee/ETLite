"""
Net 仔 Podcast System - Main Application Entry Point
粵語 AI 理財播客後端服務
"""
import asyncio
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.core.config import settings
from app.api.routes import router as api_router
from app.services.websocket_manager import ConnectionManager
from app.services.podcast_generator import PodcastGenerator
from app.db.database import init_db

# Global connection manager for WebSocket
ws_manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}...")
    await init_db()
    print("✅ Database initialized")
    
    # Start background tasks
    background_task = asyncio.create_task(run_background_tasks())
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    background_task.cancel()
    try:
        await background_task
    except asyncio.CancelledError:
        pass

async def run_background_tasks():
    """Background task runner for podcast generation and notifications"""
    while True:
        try:
            await asyncio.sleep(60)  # Check every minute
            # Here you would check for scheduled podcast generations
            print("🎙️ Background task running...")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"❌ Background task error: {e}")

app = FastAPI(
    title=settings.APP_NAME,
    description="AI 粵語理財播客系統 - 結合人工智能、音頻內容與心理學設計的財經資訊平台",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Use origins from settings
allowed_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
# In development mode, allow all origins for convenience
if settings.DEBUG:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files for audio playback - use absolute path
AUDIO_DIR = Path(__file__).parent / "static" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# WebSocket endpoint for real-time updates
@app.websocket("/ws/podcast")
async def podcast_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time podcast updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages
            await handle_websocket_message(websocket, data)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

async def handle_websocket_message(websocket: WebSocket, data: str):
    """Handle incoming WebSocket messages"""
    import json
    message = json.loads(data)
    
    if message.get("type") == "subscribe":
        # Subscribe to specific podcast channel
        channel = message.get("channel")
        print(f"Client subscribed to {channel}")
    
    elif message.get("type") == "request_podcast":
        # Request new podcast generation
        user_id = message.get("user_id")
        profile = message.get("profile")
        # Trigger podcast generation
        generator = PodcastGenerator()
        await generator.generate_daily_podcast(user_id, profile)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Net 仔 Podcast API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS
    )
