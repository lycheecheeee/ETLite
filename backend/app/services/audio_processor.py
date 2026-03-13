"""
Audio Processing Service
音頻處理服務 - 合併、剪輯、音效添加
使用 run_in_executor 避免阻塞事件循環
"""
import asyncio
import logging
from pydub import AudioSegment
from pathlib import Path
from typing import List, Optional
import uuid

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Process and merge audio segments with async support"""
    
    def __init__(self):
        self.jingles_dir = Path("audio/jingles")
        self.music_dir = Path("audio/music")
        self.output_dir = Path("audio/output")
        
        # Create directories
        for directory in [self.jingles_dir, self.music_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ AudioProcessor initialized")
    
    async def merge_segments(
        self,
        segments: List[str],
        output_filename: Optional[str] = None,
        add_jingles: bool = True,
        crossfade: int = 100
    ) -> str:
        """
        Merge multiple audio segments into one podcast
        
        Args:
            segments: List of audio file paths
            output_filename: Output filename
            add_jingles: Whether to add transition jingles
            crossfade: Crossfade duration in ms
            
        Returns:
            Path to merged audio file
        """
        if not output_filename:
            output_filename = f"merged_{uuid.uuid4()}.wav"
        
        output_path = self.output_dir / output_filename
        
        # Load all segments (使用 executor 避免阻塞)
        loop = asyncio.get_event_loop()
        audio_segments = []
        for segment_path in segments:
            if Path(segment_path).exists():
                audio = await loop.run_in_executor(
                    None,
                    lambda p=segment_path: AudioSegment.from_file(p)
                )
                audio_segments.append(audio)
        
        if not audio_segments:
            raise Exception("No valid audio segments found")
        
        # Add jingles between segments if requested
        final_segments = []
        if add_jingles:
            jingle_files = list(self.jingles_dir.glob("*.wav"))
            
            for idx, segment in enumerate(audio_segments):
                final_segments.append(segment)
                
                # Add jingle between segments (except after last one)
                if idx < len(audio_segments) - 1 and jingle_files:
                    jingle_path = jingle_files[idx % len(jingle_files)]
                    jingle = await loop.run_in_executor(
                        None,
                        lambda p=str(jingle_path): AudioSegment.from_file(p)
                    )
                    final_segments.append(jingle)
        else:
            final_segments = audio_segments
        
        # Merge segments with crossfade (使用 executor 避免阻塞)
        def _merge_and_export():
            merged = final_segments[0]
            for segment in final_segments[1:]:
                merged = merged.append(segment, crossfade=crossfade)
            
            merged.export(
                str(output_path),
                format="wav",
                parameters=["-acodec", "pcm_s16le", "-ar", "24000"]
            )
            return str(output_path)
        
        result = await loop.run_in_executor(None, _merge_and_export)
        logger.info(f"✅ Merged {len(segments)} segments: {output_path}")
        return result
    
    async def get_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds (async)"""
        loop = asyncio.get_event_loop()
        audio = await loop.run_in_executor(
            None,
            lambda: AudioSegment.from_file(audio_path)
        )
        return len(audio) / 1000.0
    
    async def add_background_music(
        self,
        voice_track: str,
        music_track: str,
        music_volume: float = -20.0
    ) -> str:
        """
        Add background music to voice track (async)
        
        Args:
            voice_track: Path to voice audio
            music_track: Path to background music
            music_volume: Music volume in dB (negative = quieter)
            
        Returns:
            Path to mixed audio
        """
        loop = asyncio.get_event_loop()
        
        def _mix_audio():
            voice = AudioSegment.from_file(voice_track)
            music = AudioSegment.from_file(music_track)
            
            # Adjust music volume
            music = music + music_volume
            
            # Loop music if shorter than voice
            if len(music) < len(voice):
                loops_needed = int(len(voice) / len(music)) + 1
                music = music * loops_needed
            
            # Trim music to match voice duration
            music = music[:len(voice)]
            
            # Mix voice and music
            mixed = voice.overlay(music)
            
            output_path = self.output_dir / f"mixed_{uuid.uuid4()}.wav"
            mixed.export(str(output_path), format="wav")
            return str(output_path)
        
        result = await loop.run_in_executor(None, _mix_audio)
        logger.info(f"✅ Added background music: {result}")
        return result
    
    async def trim_silence(
        self,
        audio_path: str,
        silence_threshold: int = -40,
        min_silence_length: int = 500
    ) -> str:
        """
        Remove silence from beginning and end of audio (async)
        
        Args:
            audio_path: Input audio path
            silence_threshold: dB threshold for silence detection
            min_silence_length: Minimum silence length in ms
            
        Returns:
            Path to trimmed audio
        """
        loop = asyncio.get_event_loop()
        
        def _trim():
            audio = AudioSegment.from_file(audio_path)
            
            # Detect and remove silence
            trimmed = audio.strip_silence(
                silence_len=min_silence_length,
                silence_thresh=silence_threshold
            )
            
            output_path = self.output_dir / f"trimmed_{uuid.uuid4()}.wav"
            trimmed.export(str(output_path), format="wav")
            return str(output_path)
        
        result = await loop.run_in_executor(None, _trim)
        logger.info(f"✅ Trimmed silence: {result}")
        return result
    
    async def normalize_audio(
        self,
        audio_path: str,
        target_dbfs: float = -16.0
    ) -> str:
        """
        Normalize audio volume (async)
        
        Args:
            audio_path: Input audio path
            target_dbfs: Target loudness in dBFS
            
        Returns:
            Path to normalized audio
        """
        loop = asyncio.get_event_loop()
        
        def _normalize():
            audio = AudioSegment.from_file(audio_path)
            
            # Calculate current loudness
            change_in_dbfs = target_dbfs - audio.dBFS
            
            # Apply gain
            normalized = audio.apply_gain(change_in_dbfs)
            
            output_path = self.output_dir / f"normalized_{uuid.uuid4()}.wav"
            normalized.export(str(output_path), format="wav")
            return str(output_path)
        
        result = await loop.run_in_executor(None, _normalize)
        logger.info(f"✅ Normalized audio: {result}")
        return result


# Global audio processor instance
audio_processor = AudioProcessor()
