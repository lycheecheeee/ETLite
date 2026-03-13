"""
Podcast Generator Service
播客生成服務 - AI 驅動的內容生成與音頻製作
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from app.services.tts_service import tts_service
from app.services.cantonese_tts_service import cantonese_tts
from app.services.audio_processor import AudioProcessor
from app.db.models import Podcast, PodcastSegment
from app.core.config import settings

logger = logging.getLogger(__name__)

class PodcastGenerator:
    """AI-powered podcast generation service"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        # Use Cantonese AI TTS as primary service (higher quality for Cantonese)
        self.tts_service = cantonese_tts if settings.CANTONESE_AI_API_KEY else tts_service
        logger.info("✅ PodcastGenerator initialized")
    
    async def generate_daily_podcast(
        self,
        user_id: str,
        profile: Dict[str, str],
        podcast_type: str = "morning"
    ) -> Podcast:
        """
        Generate personalized daily podcast based on user profile
        
        Args:
            user_id: User identifier
            profile: User profile (foundation, mindset, timeframe)
            podcast_type: morning/market_close/before_sleep
            
        Returns:
            Generated Podcast object
        """
        logger.info(f"🎙️ Generating {podcast_type} podcast for user {user_id}")
        
        # Step 1: Generate content script based on profile
        script = await self._generate_script(profile, podcast_type)
        
        # Step 2: Create podcast record
        podcast_id = str(uuid.uuid4())
        podcast = Podcast(
            id=podcast_id,
            user_id=user_id,
            title=script["title"],
            description=script["description"],
            type=podcast_type,
            duration=0,  # Will be updated after audio generation
            status="generating"
        )
        
        # Step 3: Generate audio segments
        segments = []
        for idx, segment_data in enumerate(script["segments"]):
            segment = await self._generate_segment(
                podcast_id=podcast_id,
                index=idx,
                segment_data=segment_data,
                profile=profile
            )
            segments.append(segment)
        
        # Step 4: Merge all segments
        final_audio_path = await self.audio_processor.merge_segments(
            segments=[s.audio_path for s in segments],
            output_filename=f"podcast_{podcast_id}.wav"
        )
        
        # Step 5: Update podcast with final info
        podcast.audio_path = final_audio_path
        podcast.duration = await self.audio_processor.get_duration(final_audio_path)
        podcast.status = "completed"
        podcast.segments = segments
        
        # Step 6: Save to database and cache
        await self._save_podcast(podcast)
        
        logger.info(f"✅ Podcast generated: {podcast.title}")
        return podcast
    
    async def _generate_script(
        self,
        profile: Dict[str, str],
        podcast_type: str
    ) -> Dict[str, Any]:
        """Generate podcast script based on user profile"""
        
        # This would integrate with LLM (OpenAI/LangChain)
        # For now, use template-based approach
        
        foundation = profile.get("foundation", "intermediate")
        mindset = profile.get("mindset", "balanced")
        timeframe = profile.get("timeframe", "medium")
        
        # Customize content based on profile
        if foundation == "beginner":
            tone = "friendly_educational"
            terminology_level = "simple"
        elif foundation == "advanced":
            tone = "professional_fast"
            terminology_level = "advanced"
        else:
            tone = "balanced"
            terminology_level = "moderate"
        
        # Generate script structure
        script = {
            "title": f"晨早開市前瞻 - {datetime.now().strftime('%Y-%m-%d')}",
            "description": "為你準備今日嘅市場分析同投資策略",
            "segments": [
                {
                    "type": "intro",
                    "host": "zicheng",
                    "text": "早晨！我係子程，歡迎收聽 Net 仔財經早新聞。今日恒指高開 256 點，科技股領漲...",
                    "emotion": "cheerful",
                    "duration_estimate": 15
                },
                {
                    "type": "market_overview",
                    "host": "mina",
                    "text": "多謝子程。我係敏娜。隔夜美股三大指數齊升，道指升 0.8%，納指升 1.2%...",
                    "emotion": "professional",
                    "duration_estimate": 20
                },
                {
                    "type": "stock_focus",
                    "host": "zicheng",
                    "text": "個股方面，騰訊尋晚公佈業績，全年盈利增長 25%，超出行家預期...",
                    "emotion": "excited",
                    "duration_estimate": 25
                },
                {
                    "type": "interaction",
                    "host": "mina",
                    "text": "收到 WhatsApp 消息，陳先生問：而家追入騰訊合唔合適？...",
                    "emotion": "friendly",
                    "duration_estimate": 15
                },
                {
                    "type": "expert_advice",
                    "host": "zicheng",
                    "text": "陳先生好問題。技術指標顯示短期超買，建議分段建倉...",
                    "emotion": "professional",
                    "duration_estimate": 20
                },
                {
                    "type": "closing",
                    "host": "mina",
                    "text": "好啦，今日早節節目去到呢度。下午 5 點我哋再見！",
                    "emotion": "cheerful",
                    "duration_estimate": 10
                }
            ]
        }
        
        return script
    
    async def _generate_segment(
        self,
        podcast_id: str,
        index: int,
        segment_data: Dict[str, Any],
        profile: Dict[str, str]
    ) -> PodcastSegment:
        """Generate single podcast segment"""
        
        host = segment_data["host"]
        text = segment_data["text"]
        emotion = segment_data.get("emotion", "neutral")
        
        # Map emotion to speed/pitch for Cantonese AI
        emotion_params = {
            "cheerful": {"speed": 1.1, "pitch": 5},
            "professional": {"speed": 1.0, "pitch": 0},
            "excited": {"speed": 1.3, "pitch": 10},
            "friendly": {"speed": 1.0, "pitch": 5},
            "neutral": {"speed": 1.0, "pitch": 0}
        }
        
        params = emotion_params.get(emotion, {"speed": 1.0, "pitch": 0})
        
        # Generate TTS audio using Cantonese AI service
        filename = f"podcast_{podcast_id}_{index:03d}_{host}.wav"
        audio_result = await self.tts_service.synthesize_speech(
            text=text,
            output_filename=filename,
            speed=params["speed"],
            pitch=params["pitch"],
            return_timestamp=False  # 不需要時間戳，只要音頻
        )
        
        # 獲取音頻路徑（支持新舊返回格式）
        audio_path = audio_result if isinstance(audio_result, str) else audio_result.get("audio_path", "")
        
        # Get actual duration
        duration = await self.audio_processor.get_duration(audio_path)
        
        # Create segment record
        segment = PodcastSegment(
            id=str(uuid.uuid4()),
            podcast_id=podcast_id,
            index=index,
            host=host,
            type=segment_data["type"],
            text=text,
            audio_path=audio_path,
            duration=duration
        )
        
        return segment
    
    async def _save_podcast(self, podcast: Podcast):
        """Save podcast to database and cache"""
        # Implementation would use SQLAlchemy/Redis
        logger.info(f"💾 Saving podcast to database: {podcast.id}")
        pass


# Global podcast generator instance
podcast_generator = PodcastGenerator()
