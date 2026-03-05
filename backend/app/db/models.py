"""
Database Models
數據庫模型 - PostgreSQL
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model - 用戶資料"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    
    # User profile (3D model)
    foundation_level = Column(String(20), default="intermediate")  # beginner/intermediate/advanced
    mindset_type = Column(String(20), default="balanced")  # conservative/balanced/aggressive
    timeframe_preference = Column(String(20), default="medium")  # long/medium/short
    
    # Subscription
    subscription_tier = Column(String(20), default="free")  # free/member/premium
    subscription_expires = Column(DateTime)
    
    # Preferences
    favorite_hosts = Column(JSON, default=list)  # ["zicheng", "mina"]
    notification_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    podcasts = relationship("Podcast", back_populates="user", cascade="all, delete-orphan")


class Podcast(Base):
    """Podcast model - 播客節目"""
    __tablename__ = "podcasts"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(500), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # morning/market_close/before_sleep/breaking
    
    # Audio
    audio_path = Column(String(1000))
    duration = Column(Float)  # in seconds
    
    # Status
    status = Column(String(20), default="pending")  # pending/generating/completed/failed
    play_count = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="podcasts")
    segments = relationship("PodcastSegment", back_populates="podcast", cascade="all, delete-orphan")


class PodcastSegment(Base):
    """Podcast Segment model - 節目分段"""
    __tablename__ = "podcast_segments"
    
    id = Column(String, primary_key=True)
    podcast_id = Column(String, ForeignKey("podcasts.id"), nullable=False)
    
    index = Column(Integer, nullable=False)  # Order in podcast
    host = Column(String(50))  # zicheng/mina
    type = Column(String(50))  # intro/market_overview/stock_focus/etc.
    
    text = Column(Text)  # Script text
    audio_path = Column(String(1000))
    duration = Column(Float)
    
    emotion = Column(String(50), default="neutral")
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    podcast = relationship("Podcast", back_populates="segments")


class ContentAtom(Base):
    """Content Atom model - 內容原子"""
    __tablename__ = "content_atoms"
    
    id = Column(String, primary_key=True)
    
    type = Column(String(50), nullable=False)  # market_index/stock/macro/etc.
    title = Column(String(500), nullable=False)
    content = Column(Text)
    
    data = Column(JSON)  # Structured data
    sentiment = Column(String(20))  # positive/negative/neutral
    
    source = Column(String(200))
    published_at = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Indexes for fast querying
    # __table_args__ = (
    #     Index('idx_type_sentiment', 'type', 'sentiment'),
    #     Index('idx_published_at', 'published_at'),
    # )


class UserInteraction(Base):
    """User Interaction model - 用戶互動記錄"""
    __tablename__ = "user_interactions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    
    interaction_type = Column(String(50))  # play/pause/skip/message/call_in
    content_id = Column(String)  # podcast_id or segment_id
    timestamp = Column(DateTime, server_default=func.now())
    
    metadata = Column(JSON)


# Initialize function
async def init_db():
    """Initialize database tables"""
    from app.db.database import engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created")
