"""
Cantonese AI TTS Service
粵語 AI 語音合成服務 - 使用 cantonese.ai API
"""
import aiohttp
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
import uuid

from app.core.config import settings

class CantoneseTTSService:
    """Cantonese AI TTS service for high-quality Cantonese speech synthesis"""
    
    def __init__(self):
        self.api_url = settings.CANTONESE_AI_API_URL
        self.api_key = settings.CANTONESE_AI_API_KEY
        self.voice_id = settings.CANTONESE_AI_VOICE_ID
        self.output_dir = Path("audio/generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Default parameters
        self.default_params = {
            "frame_rate": "24000",
            "speed": 1.0,
            "pitch": 0,
            "language": "cantonese",
            "output_extension": "wav",
            "should_return_timestamp": False
        }
    
    async def synthesize_speech(
        self,
        text: str,
        output_filename: Optional[str] = None,
        voice_id: Optional[str] = None,
        speed: float = 1.0,
        pitch: int = 0
    ) -> str:
        """
        Synthesize speech using Cantonese AI API
        
        Args:
            text: Cantonese text to convert to speech
            output_filename: Optional custom filename
            voice_id: Optional voice ID override
            speed: Speech speed (0.5-2.0)
            pitch: Pitch adjustment (-100 to 100)
            
        Returns:
            Path to generated audio file
        """
        if not output_filename:
            output_filename = f"{uuid.uuid4()}.wav"
        
        output_path = self.output_dir / output_filename
        
        payload = {
            "api_key": self.api_key,
            "text": text,
            "frame_rate": self.default_params["frame_rate"],
            "speed": speed,
            "pitch": pitch,
            "language": self.default_params["language"],
            "output_extension": self.default_params["output_extension"],
            "voice_id": voice_id or self.voice_id,
            "should_return_timestamp": self.default_params["should_return_timestamp"]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        # Save audio file
                        audio_data = await response.read()
                        with open(output_path, 'wb') as f:
                            f.write(audio_data)
                        
                        print(f"[TTS] Speech synthesized: {output_path}")
                        print(f"[TTS] File size: {len(audio_data)} bytes")
                        return str(output_path)
                    else:
                        error_text = await response.text()
                        print(f"[TTS] API Error: {response.status}")
                        print(f"[TTS] Response: {error_text}")
                        raise Exception(f"Cantonese AI API error: {response.status} - {error_text}")
                        
        except aiohttp.ClientError as e:
            print(f"[TTS] Request failed: {e}")
            raise Exception(f"TTS request failed: {e}")
        except Exception as e:
            print(f"[TTS] Error: {e}")
            raise
    
    async def batch_synthesize(
        self,
        texts: list[Dict[str, Any]],
        prefix: str = "batch"
    ) -> list[str]:
        """
        Batch synthesize multiple text segments
        
        Args:
            texts: List of dicts with keys:
                   - text (str): Text content
                   - voice_id (str, optional): Voice ID override
                   - speed (float, optional): Speed override
                   - pitch (int, optional): Pitch override
            prefix: Filename prefix
            
        Returns:
            List of generated audio file paths
        """
        results = []
        
        # Process in parallel (max 5 concurrent requests)
        semaphore = asyncio.Semaphore(5)
        
        async def synthesize_with_semaphore(index: int, item: dict) -> Optional[str]:
            async with semaphore:
                try:
                    text = item.get("text", "")
                    voice_id = item.get("voice_id")
                    speed = item.get("speed", 1.0)
                    pitch = item.get("pitch", 0)
                    
                    filename = f"{prefix}_{index:03d}.wav"
                    path = await self.synthesize_speech(
                        text=text,
                        output_filename=filename,
                        voice_id=voice_id,
                        speed=speed,
                        pitch=pitch
                    )
                    return path
                except Exception as e:
                    print(f"[TTS] Failed to synthesize segment {index}: {e}")
                    return None
        
        # Create tasks
        tasks = [
            synthesize_with_semaphore(idx, item) 
            for idx, item in enumerate(texts)
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in results if r is not None)
        print(f"[TTS] Batch synthesis: {success_count}/{len(texts)} segments generated")
        
        return results
    
    async def get_available_voices(self) -> list[dict]:
        """
        Get list of available voices from API
        
        Returns:
            List of voice information
        """
        # TODO: Implement when API provides voice list endpoint
        return [
            {
                "voice_id": self.voice_id,
                "name": "Default Cantonese Voice",
                "language": "cantonese",
                "gender": "neutral"
            }
        ]


# Global TTS service instance
cantonese_tts = CantoneseTTSService()
