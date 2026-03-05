"""
TTS (Text-to-Speech) Service
語音合成服務 - 使用 Azure Cognitive Services
"""
import os
import azure.cognitiveservices.speech as speechsdk
from typing import Optional, BinaryIO
from pathlib import Path
import aiofiles
import uuid

from app.core.config import settings

class TTSService:
    """Azure TTS service for Cantonese speech synthesis"""
    
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY,
            region=settings.AZURE_SPEECH_REGION
        )
        self.speech_config.speech_synthesis_voice_name = settings.AZURE_SPEECH_VOICE
        self.output_dir = Path("audio/generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def synthesize_speech(
        self,
        text: str,
        output_filename: Optional[str] = None,
        ssml: Optional[str] = None
    ) -> str:
        """
        Synthesize speech from text
        
        Args:
            text: Text to convert to speech
            output_filename: Optional custom filename
            ssml: Optional SSML markup for advanced control
            
        Returns:
            Path to generated audio file
        """
        if not output_filename:
            output_filename = f"{uuid.uuid4()}.wav"
        
        output_path = self.output_dir / output_filename
        
        # Configure audio output
        audio_config = speechsdk.audio.AudioOutputConfig(
            filename=str(output_path)
        )
        
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )
        
        # Use SSML if provided, otherwise plain text
        if ssml:
            result = synthesizer.speak_ssml_async(ssml).get()
        else:
            result = synthesizer.speak_text_async(text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"✅ Speech synthesized: {output_path}")
            return str(output_path)
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"❌ Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.error_details:
                print(f"Error: {cancellation_details.error_details}")
            raise Exception(f"TTS synthesis failed: {cancellation_details.error_details}")
        
        raise Exception("Unknown TTS error")
    
    def create_ssml(
        self,
        text: str,
        rate: str = "medium",
        pitch: str = "medium",
        volume: str = "medium",
        emotion: Optional[str] = None
    ) -> str:
        """
        Create SSML markup for advanced speech control
        
        Args:
            text: Text content
            rate: Speech rate (x-slow, slow, medium, fast, x-fast)
            pitch: Pitch level (x-low, low, medium, high, x-high)
            volume: Volume level (silent, x-soft, soft, medium, loud, x-loud)
            emotion: Emotional tone (for supported voices)
            
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
            "cheerful": "+10%",  # Higher pitch
            "sad": "-10%",      # Lower pitch
            "angry": "fast",     # Faster rate
            "excited": "fast",
            "friendly": "+5%",
            "hopeful": "+5%",
            "neutral": "medium"
        }
        
        pitch_adjust = emotion_map.get(emotion, "medium")
        rate_adjust = "medium"
        
        # Adjust rate for certain emotions
        if emotion in ["angry", "excited"]:
            rate_adjust = "fast"
        elif emotion == "sad":
            rate_adjust = "slow"
        
        ssml = self.create_ssml(
            text=text,
            rate=rate_adjust,
            pitch=pitch_adjust if isinstance(pitch_adjust, str) and "%" not in str(pitch_adjust) else "medium",
            volume="medium"
        )
        
        return await self.synthesize_speech(text, output_filename, ssml)
    
    async def batch_synthesize(
        self,
        texts: list[dict],
        prefix: str = "batch"
    ) -> list[str]:
        """
        Batch synthesize multiple text segments
        
        Args:
            texts: List of dicts with 'text' and optional 'emotion' keys
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
                print(f"❌ Failed to synthesize segment {idx}: {e}")
                results.append(None)
        
        return results


# Global TTS service instance
tts_service = TTSService()
