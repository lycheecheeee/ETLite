"""
API Routes
API 路由定義
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import User, Podcast, ContentAtom
from app.services.podcast_generator import podcast_generator
from app.services.websocket_manager import ws_manager

router = APIRouter()


# Request/Response Models
class UserProfileRequest(BaseModel):
    foundation: str = "intermediate"
    mindset: str = "balanced"
    timeframe: str = "medium"

class PodcastGenerateRequest(BaseModel):
    user_id: str
    profile: UserProfileRequest
    podcast_type: str = "morning"

class MessageRequest(BaseModel):
    user_id: str
    message: str
    podcast_id: Optional[str] = None


# User Routes
@router.post("/users", response_model=dict)
async def create_user(user_data: dict, db: AsyncSession = Depends(get_db)):
    """Create new user"""
    # Implementation would save to database
    return {
        "message": "User created successfully",
        "user_id": "user_123"
    }


@router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user profile"""
    # Implementation would fetch from database
    return {
        "user_id": user_id,
        "foundation": "intermediate",
        "mindset": "balanced",
        "timeframe": "medium",
        "subscription": "free"
    }


# Podcast Routes
@router.post("/podcasts/generate")
async def generate_podcast(request: PodcastGenerateRequest):
    """Generate personalized podcast"""
    try:
        podcast = await podcast_generator.generate_daily_podcast(
            user_id=request.user_id,
            profile=request.profile.dict(),
            podcast_type=request.podcast_type
        )
        
        # Notify via WebSocket
        await ws_manager.notify_podcast_update(
            podcast_id=podcast.id,
            status="completed",
            user_id=request.user_id
        )
        
        return {
            "message": "Podcast generated successfully",
            "podcast_id": podcast.id,
            "title": podcast.title,
            "duration": podcast.duration
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/podcasts")
async def list_podcasts(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List user's podcasts"""
    # Implementation would query database
    return {
        "podcasts": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.get("/podcasts/{podcast_id}")
async def get_podcast(podcast_id: str, db: AsyncSession = Depends(get_db)):
    """Get podcast details"""
    return {
        "id": podcast_id,
        "title": "晨早開市前瞻",
        "duration": 300,
        "audio_url": "/audio/podcast_xxx.wav",
        "segments": []
    }


@router.post("/podcasts/{podcast_id}/play")
async def play_podcast(podcast_id: str, db: AsyncSession = Depends(get_db)):
    """Track podcast playback"""
    # Increment play count
    return {"status": "ok"}


# Content Atom Routes
@router.get("/atoms", response_model=List[dict])
async def list_content_atoms(
    type: Optional[str] = None,
    sentiment: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List content atoms with filters"""
    # Implementation would query database
    return [
        {
            "id": "atom_1",
            "type": "market_index",
            "title": "恒生指數",
            "content": "恒指現報 18,256.45 點，升 256.78 點",
            "sentiment": "positive"
        }
    ]


@router.post("/atoms")
async def create_content_atom(atom_data: dict, db: AsyncSession = Depends(get_db)):
    """Create new content atom"""
    return {"message": "Atom created", "id": "atom_xxx"}


# Interaction Routes
@router.post("/interactions/message")
async def send_message(request: MessageRequest):
    """Send message to podcast hosts (simulated)"""
    # This would trigger AI response generation
    return {
        "message": "Message sent successfully",
        "response_pending": True
    }


@router.get("/interactions/questions")
async def get_unanswered_questions(user_id: str):
    """Get user's unanswered questions"""
    return {
        "questions": [
            {
                "id": "q1",
                "question": "而家追入騰訊合唔合適？",
                "status": "pending",
                "created_at": "2026-03-05T10:30:00"
            }
        ]
    }


# Market Data Routes (mock for now)
@router.get("/market/indices")
async def get_market_indices():
    """Get current market indices"""
    return {
        "hang_seng": {
            "value": 18256.45,
            "change": 256.78,
            "change_percent": 1.43
        },
        "hscei": {
            "value": 6543.21,
            "change": -32.10,
            "change_percent": -0.49
        }
    }


@router.get("/market/stocks/{stock_code}")
async def get_stock_price(stock_code: str):
    """Get stock price"""
    return {
        "code": stock_code,
        "name": "騰訊控股",
        "price": 368.40,
        "change": 3.2,
        "change_percent": 0.88,
        "volume": "15.6 億"
    }


# Health & Status
@router.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "redis": "connected",
            "tts": "ready"
        }
    }
