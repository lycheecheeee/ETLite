"""
Azure TTS Service
語音合成服務 - 使用 Azure Cognitive Services
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Dict
import uuid

import azure.cognitiveservices.speech as speechsdk
from app.core.config import settings

logger = logging.getLogger(__name__)


class TTSService:
    """Azure TTS service for Cantonese speech synthesis with async support"""
    
    def __init__(self):
        # 驗證 API Key
        if not settings.AZURE_SPEECH_KEY:
            logger.warning("⚠️ Azure Speech Key not configured. TTS will return mock audio.")
            self.speech_config = None
            return
        
        self.speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY,
            region=settings.AZURE_SPEECH_REGION
        )
        self.speech_config.speech_synthesis_voice_name = settings.AZURE_SPEECH_VOICE
        
        # 創建輸出目錄
        self.output_dir = Path(settings.OUTPUT_DIR) / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Azure TTS initialized with voice: {self.speech_config.speech_synthesis_voice_name}")
    
    async def synthesize_speech(
        self,
        text: str,
        output_filename: Optional[str] = None,
        ssml: Optional[str] = None,
        speed: float = 1.0,
        pitch: int = 0
    ) -> str:
        """
        Synthesize speech from text with optional emotional expression
        
        Args:
            text: Text to convert to speech
            output_filename: Optional custom filename
            ssml: Optional SSML markup for advanced control
            speed: Speech speed (0.5-2.0)
            pitch: Pitch adjustment (-100 to 100)
            
        Returns:
            Path to generated audio file
        """
        if not self.speech_config:
            logger.warning("TTS service not initialized. Returning mock audio path.")
            return ""
        
        if not output_filename:
            output_filename = f"{uuid.uuid4().hex[:8]}.wav"
        
        output_path = self.output_dir / output_filename
        
        # 配置音頻輸出
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
        
        # 使用線程池執行，避免阻塞
        loop = asyncio.get_event_loop()
        
        try:
            if ssml:
                # 使用 SSML
                result = await loop.run_in_executor(
                    None,
                    lambda: speechsdk.SpeechSynthesizer(
                        speech_config=self.speech_config,
                        audio_config=audio_config
                    ).speak_ssml_async(ssml).get()
                )
            else:
                # 純文本
                result = await loop.run_in_executor(
                    None,
                    lambda: speechsdk.SpeechSynthesizer(
                        speech_config=self.speech_config,
                        audio_config=audio_config
                    ).speak_text_async(text).get()
                )
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"✅ Speech synthesized: {output_path}")
                return str(output_path)
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                logger.error(f"❌ Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.error_details:
                    logger.error(f"Error: {cancellation_details.error_details}")
                raise Exception(f"TTS synthesis failed: {cancellation_details.error_details}")
            
            raise Exception("Unknown TTS error")
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise
    
    def create_ssml(
        self,
        text: str,
        rate: str = "medium",
        pitch: str = "medium",
        volume: str = "medium"
    ) -> str:
        """
        Create SSML markup for advanced speech control
        
        Args:
            text: Text content
            rate: Speech rate (x-slow, slow, medium, fast, x-fast)
            pitch: Pitch level (x-low, low, medium, high, x-high)
            volume: Volume level (silent, x-soft, soft, medium, loud, x-loud)
            
        Returns:
            SSML formatted string
        """
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-HK">
            <voice name="{settings.AZURE_SPEECH_VOICE}">
                <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        return ssml
    
    async def synthesize_with_emotion(
        self,
        text: str,
        emotion: str = "neutral",
        output_filename: Optional[str] = None
    ) -> str:
        """
        Synthesize speech with emotional expression
        
        Emotions: neutral, cheerful, sad, angry, excited, friendly, hopeful
        """
        emotion_map = {
            "cheerful": {"rate": "fast", "pitch": "+10%"},
            "sad": {"rate": "slow", "pitch": "-10%"},
            "angry": {"rate": "fast", "pitch": "medium"},
            "excited": {"rate": "fast", "pitch": "+10%"},
            "friendly": {"rate": "medium", "pitch": "+5%"},
            "hopeful": {"rate": "medium", "pitch": "+5%"},
            "neutral": {"rate": "medium", "pitch": "medium"}
        }
        
        params = emotion_map.get(emotion, emotion_map["neutral"])
        ssml = self.create_ssml(
            text=text,
            rate=params["rate"],
            pitch=params["pitch"],
            volume="medium"
        )
        
        return await self.synthesize_speech(text, output_filename, ssml)
    
    async def batch_synthesize(
        self,
        texts: List[Dict],
        prefix: str = "batch"
    ) -> List[str]:
        """
        Batch synthesize multiple text segments
        
        Args:
            texts: List of dicts with keys:
                   - text (str): Text content
                   - emotion (str, optional): Emotional tone
            prefix: Filename prefix
            
        Returns:
            List of generated audio file paths
        """
        results = []
        
        for idx, item in enumerate(texts):
            text = item.get("text", "")
            emotion = item.get("emotion", "neutral")
            filename = f"{prefix}_{idx:03d}.wav"
            
            try:
                path = await self.synthesize_with_emotion(text, emotion, filename)
                results.append(path)
            except Exception as e:
                logger.error(f"Failed to synthesize segment {idx}: {e}")
                results.append("")
        
        success_count = sum(1 for r in results if r)
        logger.info(f"Batch synthesis: {success_count}/{len(texts)} segments generated")
        return results


# Global TTS service instance
tts_service = TTSService()
