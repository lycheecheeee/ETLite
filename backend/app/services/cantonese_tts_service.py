"""
Cantonese AI TTS Service
粵語語音合成服務 - 支持速率限制和正確的異步處理
API 文檔: https://docs.cantonese.ai/text-to-speech
"""
import asyncio
import aiohttp
import base64
import logging
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Cantonese AI TTS API Endpoint
CANTONESE_AI_TTS_URL = "https://cantonese.ai/api/tts"

# Default Voice ID (示例，可以喺 https://cantonese.ai/voices 換其他聲音)
DEFAULT_VOICE_ID = "2725cf0f-efe2-4132-9e06-62ad84b2973d"


class CantoneseTTSService:
    """Cantonese AI TTS service with rate limiting and proper async handling
    
    API 文檔: https://docs.cantonese.ai/text-to-speech
    
    參數說明:
    - api_key: API 密鑰 (必需)
    - text: 要轉換的文本 (必需, 最多5000字)
    - voice_id: 聲音 ID (可選，默認使用系統默認聲音)
    - frame_rate: 音頻幀率 (可選, "16000"/"24000"/"44100", 默認 "24000")
    - speed: 語速 (可選, 0.5-3.0, 默認 1.0)
    - pitch: 音調調整 (可選, -12 到 +12 半音, 默認 0)
    - language: 語言 (可選, "cantonese"/"english"/"mandarin", 默認 "cantonese")
    - output_extension: 輸出格式 (可選, "wav"/"mp3", 默認 "wav")
    - should_return_timestamp: 是否返回時間戳 (可選, 默認 false)
    - should_enhance: 是否增強音頻 (可選, 默認 false)
    - should_use_turbo_model: 是否使用快速模型 (可選, 默認 false)
    """
    
    def __init__(self):
        # 從配置獲取 TTS 設置
        tts_config = settings.get_tts_config()
        self.api_url = tts_config.get("api_url", CANTONESE_AI_TTS_URL)
        self.api_key = tts_config.get("api_key", "")
        self.voice_id = tts_config.get("voice_id", DEFAULT_VOICE_ID)
        self.concurrency = tts_config.get("concurrency", 8)
        self.chunk_size = tts_config.get("chunk_size", 500)  # API 最多支援 5000 字
        self.output_dir = Path(settings.OUTPUT_DIR) / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 驗證 API Key
        if not self.api_key:
            logger.warning("⚠️ Cantonese AI API Key not configured. TTS will return mock audio.")
            logger.warning("⚠️ Get your API key from: https://cantonese.ai/api-keys")
            self._semaphore = None
            return
        
        # 創建 semaphore 控制並發 (Pro = 10 req/min, 設 8 留 buffer)
        self._semaphore = asyncio.Semaphore(self.concurrency)
        logger.info(f"✅ Cantonese TTS initialized:")
        logger.info(f"   - API URL: {self.api_url}")
        logger.info(f"   - Voice ID: {self.voice_id}")
        logger.info(f"   - Concurrency: {self.concurrency}")
        logger.info(f"   - Output dir: {self.output_dir}")
        
        # 創建共享 session 用於批量 TTS 請求復用連接池
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """獲取或創建 aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60)
            )
            logger.info("🔊 Created new aiohttp session")
        return self._session
    
    async def close(self):
        """關閉 session"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("🔇 Closed aiohttp session")
    
    async def synthesize_speech(
        self,
        text: str,
        output_filename: Optional[str] = None,
        speed: float = 1.0,
        pitch: int = 0,
        language: str = "cantonese",
        output_format: str = "wav",
        return_timestamp: bool = True,
        use_turbo: bool = False,
        enhance: bool = False
    ) -> Dict[str, Any]:
        """
        Synthesize speech using Cantonese AI TTS with rate limiting
        
        Args:
            text: Text to convert to speech (max 5000 chars)
            output_filename: Optional custom filename
            speed: Speech speed (0.5-3.0, default 1.0)
            pitch: Pitch adjustment in semitones (-12 to +12, default 0)
            language: Language code ("cantonese", "english", "mandarin")
            output_format: Audio format ("wav", "mp3")
            return_timestamp: Whether to return timestamps
            use_turbo: Use faster turbo model
            enhance: Apply audio enhancement
            
        Returns:
            Dict with 'audio_path', 'timestamps', 'srt_timestamp' (if return_timestamp=True)
        """
        if not self._semaphore:
            logger.error("❌ TTS service not initialized - API key missing")
            return {"audio_path": "", "error": "API key not configured"}
        
        if not output_filename:
            output_filename = f"{uuid.uuid4().hex[:8]}.{output_format}"
        
        output_path = self.output_dir / output_filename
        
        # 截斷過長文本 (API 最多 5000 字)
        if len(text) > 5000:
            logger.warning(f"⚠️ Text too long ({len(text)} chars), truncating to 5000")
            text = text[:5000]
        
        # 構建 API 請求
        request_body = {
            "api_key": self.api_key,
            "text": text,
            "voice_id": self.voice_id,
            "frame_rate": "24000",
            "speed": max(0.5, min(3.0, speed)),  # 確保喺 0.5-3.0 範圍內
            "pitch": max(-12, min(12, pitch)),    # 確保喺 -12 到 +12 範圍內
            "language": language,
            "output_extension": output_format,
            "should_return_timestamp": return_timestamp,
            "should_enhance": enhance,
            "should_use_turbo_model": use_turbo
        }
        
        # 使用 Semaphore 控制並發
        async with self._semaphore:
            session = await self._get_session()
            
            try:
                async with session.post(
                    self.api_url,
                    headers={"Content-Type": "application/json"},
                    json=request_body,
                    timeout=aiohttp.ClientTimeout(total=120)  # 較長 timeout 用於長文本
                ) as response:
                    if response.status == 200:
                        # 檢查 Content-Type 判斷響應類型
                        content_type = response.headers.get("Content-Type", "")
                        
                        if "application/json" in content_type or return_timestamp:
                            # JSON 響應 (帶時間戳)
                            data = await response.json()
                            
                            # 解碼並保存音頻
                            if "file" in data:
                                audio_data = base64.b64decode(data["file"])
                                output_path.write_bytes(audio_data)
                                
                                result = {
                                    "audio_path": str(output_path),
                                    "request_id": data.get("request_id", ""),
                                    "timestamps": data.get("timestamps", []),
                                    "srt_timestamp": data.get("srt_timestamp", "")
                                }
                                
                                logger.info(f"✅ TTS synthesized: {output_path} ({len(text)} chars)")
                                return result
                            else:
                                error_msg = data.get("error", "Unknown error")
                                logger.error(f"❌ TTS API error: {error_msg}")
                                return {"audio_path": "", "error": error_msg}
                        else:
                            # 直接返回音頻文件
                            audio_data = await response.read()
                            output_path.write_bytes(audio_data)
                            
                            logger.info(f"✅ TTS synthesized (direct): {output_path} ({len(text)} chars)")
                            return {"audio_path": str(output_path)}
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ TTS API error {response.status}: {error_text}")
                        return {"audio_path": "", "error": f"HTTP {response.status}: {error_text}"}
                        
            except asyncio.TimeoutError:
                logger.error("❌ TTS request timeout")
                return {"audio_path": "", "error": "Request timeout"}
            except aiohttp.ClientError as e:
                logger.error(f"❌ TTS request failed: {e}")
                return {"audio_path": "", "error": str(e)}
            except Exception as e:
                logger.error(f"❌ TTS error: {e}")
                return {"audio_path": "", "error": str(e)}
    
    async def batch_synthesize(
        self,
        texts: List[Dict],
        prefix: str = "batch"
    ) -> List[Dict[str, Any]]:
        """
        Batch synthesize multiple text segments with rate limiting
        
        Args:
            texts: List of dicts with keys:
                   - text (str): Text content
                   - output_filename (str, optional): Output filename
                   - speed (float, optional): Speech speed (0.5-3.0)
                   - pitch (int, optional): Pitch adjustment (-12 to +12)
                   - language (str, optional): Language code
            prefix: Filename prefix for results
        
        Returns:
            List of result dicts with 'audio_path', 'timestamps', etc.
        """
        results = []
        
        for idx, item in enumerate(texts):
            text = item.get("text", "")
            output_filename = f"{prefix}_{idx:03d}.wav"
            
            try:
                result = await self.synthesize_speech(
                    text=text,
                    output_filename=output_filename,
                    speed=item.get("speed", 1.0),
                    pitch=item.get("pitch", 0),
                    language=item.get("language", "cantonese")
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to synthesize segment {idx}: {e}")
                results.append({"audio_path": "", "error": str(e)})
        
        success_count = sum(1 for r in results if r.get("audio_path"))
        logger.info(f"Batch synthesis: {success_count}/{len(texts)} segments generated")
        return results
    
    async def synthesize_simple(
        self,
        text: str,
        output_filename: Optional[str] = None,
        speed: float = 1.0,
        pitch: int = 0
    ) -> str:
        """
        Simple synthesis that returns only the audio path
        (For backward compatibility)
        
        Args:
            text: Text to convert to speech
            output_filename: Optional custom filename
            speed: Speech speed (0.5-3.0)
            pitch: Pitch adjustment (-12 to +12)
            
        Returns:
            Path to generated audio file (empty string on error)
        """
        result = await self.synthesize_speech(
            text=text,
            output_filename=output_filename,
            speed=speed,
            pitch=pitch,
            return_timestamp=False
        )
        return result.get("audio_path", "")
    
    async def get_available_voices(self) -> List[Dict]:
        """
        Get list of available voices from Cantonese AI
        
        Visit https://cantonese.ai/voices to browse available voices
        
        Returns:
            List of voice information
        """
        # Cantonese AI 沒有提供 voice list API
        # 需要手動去 https://cantonese.ai/voices 選擇聲音
        return [
            {
                "voice_id": self.voice_id,
                "name": "Configured Voice",
                "language": "cantonese",
                "source": "cantonese.ai",
                "voices_url": "https://cantonese.ai/voices"
            }
        ]


# Global TTS service instance
cantonese_tts = CantoneseTTSService()
