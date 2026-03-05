"""
Application Configuration
配置管理
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Net 仔 Podcast System"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-in-production"
    
    # Database
    DATABASE_URL: str = "postgresql://netzai:password@localhost:5432/netzai_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Azure TTS
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "southeastasia"
    AZURE_SPEECH_VOICE: str = "zh-HK-HiuMaanNeural"
    
    # Cantonese AI TTS (Alternative/Primary)
    CANTONESE_AI_API_URL: str = "https://cantonese.ai/api/tts"
    CANTONESE_AI_API_KEY: str = ""
    CANTONESE_AI_VOICE_ID: str = "087b8717-9ff7-49fe-9ab5-9c30b15769ee"  # Mina voice
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # Storage (MinIO/S3)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "podcast-audio"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()
