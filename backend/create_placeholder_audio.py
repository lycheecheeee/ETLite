#!/usr/bin/env python3
"""
Create placeholder WAV files for testing
"""
import wave
import os
from pathlib import Path

def create_placeholder_wav(filename, duration_seconds=1.0, sample_rate=44100):
    """Create a minimal WAV file with silence"""
    # Calculate the number of samples
    num_samples = int(duration_seconds * sample_rate)
    
    # Create a simple sine wave for testing (optional)
    import struct
    frequency = 440  # A4 note
    
    # Create WAV file
    wav_file = wave.open(filename, 'w')
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(sample_rate)
    
    # Write silence data (or simple tone)
    for i in range(num_samples):
        # Simple sine wave
        value = int(32767 * 0.1 * (i % 100) / 100)  # Very quiet
        wav_file.writeframes(struct.pack('<h', value))
    
    wav_file.close()
    print(f"Created: {filename}")

def main():
    # Target directory
    target_dir = Path("backend/app/static/audio/dialogue")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to create
    audio_files = [
        "00_zicheng.wav",
        "01_mina.wav", 
        "02_zicheng.wav",
        "03_mina.wav",
        "04_zicheng.wav",
        "05_mina.wav",
        "06_zicheng.wav",
        "07_mina.wav"
    ]
    
    print("Creating placeholder audio files...")
    for filename in audio_files:
        filepath = target_dir / filename
        if not filepath.exists():
            create_placeholder_wav(str(filepath), duration_seconds=2.0)
        else:
            print(f"File exists: {filename}")
    
    print("✅ Placeholder audio files created successfully!")

if __name__ == "__main__":
    main()