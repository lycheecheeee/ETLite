"""
Application Configuration
配置管理 - 支持 BigModel GLM + Cantonese AI TTS
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os
import secrets
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings"""

    # ===========================================
    # Application Settings
    # ===========================================
    APP_NAME: str = "Net 仔 Podcast System"
    DEBUG: bool = True
    # Generate a random secret if not set (for development only)
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_hex(32))

    # ===========================================
    # Database Configuration
    # ===========================================
    DATABASE_URL: str = ""

    # ===========================================
    # Redis Configuration
    # ===========================================
    REDIS_URL: str = "redis://localhost:6379/0"

    # ===========================================
    # BigModel GLM Configuration (Primary LLM)
    # 智譜AI - https://open.bigmodel.cn
    # ===========================================
    BIGMODEL_API_KEY: str = ""
    BIGMODEL_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/"
    BIGMODEL_MODEL: str = "glm-4-flash"  # 快速版，質素可用 glm-4-air
    BIGMODEL_MODEL_QUALITY: str = "glm-4-air"  # 高質素版

    # ===========================================
    # OpenAI Configuration (Backup LLM)
    # ===========================================
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # ===========================================
    # LLM Provider Selection
    # ===========================================
    LLM_PROVIDER: str = "bigmodel"  # "bigmodel" or "openai"

    # ===========================================
    # Azure TTS Configuration (Backup)
    # ===========================================
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "southeastasia"
    AZURE_SPEECH_VOICE: str = "zh-HK-HiuMaanNeural"

    # ===========================================
    # Cantonese AI TTS Configuration (Primary)
    # https://cantonese.ai
    # API Docs: https://docs.cantonese.ai/text-to-speech
    # ===========================================
    CANTONESE_AI_API_URL: str = "https://cantonese.ai/api/tts"
    CANTONESE_AI_API_KEY: str = ""
    # Default voice ID - browse more at https://cantonese.ai/voices
    CANTONESE_AI_VOICE_ID: str = "2725cf0f-efe2-4132-9e06-62ad84b2973d"
    CANTONESE_AI_TTS_CONCURRENCY: int = 8  # Pro = 10 req/min, 設 8 留 buffer
    CANTONESE_AI_CHUNK_SIZE: int = 500  # API 最多支援 5000 字

    # ===========================================
    # TTS Provider Selection
    # ===========================================
    TTS_PROVIDER: str = "cantonese_ai"  # "cantonese_ai" or "azure"

    # ===========================================
    # Storage (MinIO/S3)
    # ===========================================
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "podcast-audio"
    MINIO_SECURE: bool = False

    # ===========================================
    # Celery Configuration
    # ===========================================
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ===========================================
    # Server Configuration
    # ===========================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # ===========================================
    # CORS Configuration
    # ===========================================
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    # ===========================================
    # Logging Configuration
    # ===========================================
    LOG_LEVEL: str = "INFO"

    # ===========================================
    # ETNet RSS Feeds
    # ===========================================
    ETNET_FEEDS: dict = {
        "精選新聞": "https://www.etnet.com.hk/www/tc/news/rss.php?section=featured",
        "即時新聞": "https://www.etnet.com.hk/www/tc/news/rss.php?section=realtime",
        "焦點專題": "https://www.etnet.com.hk/www/tc/news/rss.php?section=focus",
        "股市傳聞": "https://www.etnet.com.hk/www/tc/news/rss.php?section=rumour",
        "股票評論": "https://www.etnet.com.hk/www/tc/news/rss.php?section=commentary",
        "科技": "https://www.etnet.com.hk/www/tc/news/rss.php?section=technology",
    }

    # ===========================================
    # Output Directory
    # ===========================================
    OUTPUT_DIR: str = "output"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_config()

    def _validate_config(self):
        """Validate critical configuration at startup"""
        warnings = []
        errors = []

        # Validate LLM configuration
        if self.LLM_PROVIDER == "bigmodel":
            if not self.BIGMODEL_API_KEY:
                errors.append("BIGMODEL_API_KEY is required when LLM_PROVIDER='bigmodel'")
        elif self.LLM_PROVIDER == "openai":
            if not self.OPENAI_API_KEY:
                errors.append("OPENAI_API_KEY is required when LLM_PROVIDER='openai'")

        # Validate TTS configuration
        if self.TTS_PROVIDER == "cantonese_ai":
            if not self.CANTONESE_AI_API_KEY:
                errors.append("CANTONESE_AI_API_KEY is required when TTS_PROVIDER='cantonese_ai'")
            if not self.CANTONESE_AI_VOICE_ID:
                warnings.append("CANTONESE_AI_VOICE_ID is not set, TTS may fail")
        elif self.TTS_PROVIDER == "azure":
            if not self.AZURE_SPEECH_KEY:
                errors.append("AZURE_SPEECH_KEY is required when TTS_PROVIDER='azure'")

        # Validate SECRET_KEY in production
        if not self.DEBUG and len(self.SECRET_KEY) < 32:
            warnings.append("SECRET_KEY should be at least 32 characters in production")

        # Log warnings
        for warning in warnings:
            logger.warning(f"⚠️ Config Warning: {warning}")

        # Log errors but don't raise in DEBUG mode
        for error in errors:
            if self.DEBUG:
                logger.warning(f"🔴 Config Error (DEBUG mode, continuing): {error}")
            else:
                raise ValueError(f"Configuration Error: {error}")

    def get_llm_config(self) -> dict:
        """Get LLM configuration based on provider"""
        if self.LLM_PROVIDER == "bigmodel":
            return {
                "api_key": self.BIGMODEL_API_KEY,
                "base_url": self.BIGMODEL_BASE_URL,
                "model": self.BIGMODEL_MODEL,
                "model_quality": self.BIGMODEL_MODEL_QUALITY,
            }
        else:  # openai
            return {
                "api_key": self.OPENAI_API_KEY,
                "base_url": self.OPENAI_BASE_URL,
                "model": self.OPENAI_MODEL,
            }

    def get_tts_config(self) -> dict:
        """Get TTS configuration based on provider"""
        if self.TTS_PROVIDER == "cantonese_ai":
            return {
                "api_url": self.CANTONESE_AI_API_URL,
                "api_key": self.CANTONESE_AI_API_KEY,
                "voice_id": self.CANTONESE_AI_VOICE_ID,
                "concurrency": self.CANTONESE_AI_TTS_CONCURRENCY,
                "chunk_size": self.CANTONESE_AI_CHUNK_SIZE,
            }
        else:  # azure
            return {
                "speech_key": self.AZURE_SPEECH_KEY,
                "region": self.AZURE_SPEECH_REGION,
                "voice": self.AZURE_SPEECH_VOICE,
            }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
