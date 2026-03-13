"""
Cantonese AI TTS Integration Example
粵語 AI TTS 集成示例
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.cantonese_tts_service import cantonese_tts

async def example_single_synthesis():
    """Example: Single text synthesis"""
    print("=" * 60)
    print("Example 1: Single Text Synthesis")
    print("=" * 60)
    
    text = "早晨！我係子程，歡迎收聽 Net 仔財經早新聞"
    
    try:
        audio_path = await cantonese_tts.synthesize_speech(
            text=text,
            output_filename="example_morning_news.wav"
        )
        print(f"Generated: {audio_path}")
        
        # Test with different parameters
        audio_path_fast = await cantonese_tts.synthesize_speech(
            text="恒指今日大升 500 點，科技股領漲！",
            output_filename="example_market_surge.wav",
            speed=1.2  # Faster for exciting news
        )
        print(f"Generated (fast): {audio_path_fast}")
        
        audio_path_slow = await cantonese_tts.synthesize_speech(
            text="分析師建議謹慎部署，注意風險管理",
            output_filename="example_caution.wav",
            speed=0.9  # Slower for serious content
        )
        print(f"Generated (slow): {audio_path_slow}")
        
        print("\nSuccess! Check the 'audio/generated' folder for output files.")
        
    except Exception as e:
        print(f"Error: {e}")

async def example_batch_synthesis():
    """Example: Batch synthesis for podcast segments"""
    print("\n" + "=" * 60)
    print("Example 2: Batch Synthesis for Podcast")
    print("=" * 60)
    
    # Simulate a podcast script with multiple segments
    segments = [
        {
            "text": "早晨！我係子程，歡迎收聽 Net 仔財經早新聞",
            "speed": 1.0,
            "pitch": 0
        },
        {
            "text": "今日恒指高開 256 點，成交額增加至 1200 億",
            "speed": 1.1,
            "pitch": 5
        },
        {
            "text": "騰訊業績超預期，股價升 3% 至 368 元",
            "speed": 1.2,
            "pitch": 10
        },
        {
            "text": "專家建議投資者謹慎追入，注意技術指標超買",
            "speed": 0.9,
            "pitch": -5
        },
        {
            "text": "多謝收聽，聽日見！",
            "speed": 1.0,
            "pitch": 5
        }
    ]
    
    try:
        results = await cantonese_tts.batch_synthesize(
            texts=segments,
            prefix="podcast_example"
        )
        
        successful = [r for r in results if r is not None]
        failed = [r for r in results if r is None]
        
        print(f"Successfully generated: {len(successful)} segments")
        if failed:
            print(f"Failed: {len(failed)} segments")
        
        print("\nPodcast segments ready for merging!")
        
    except Exception as e:
        print(f"Error: {e}")

async def example_with_custom_voice():
    """Example: Using custom voice parameters"""
    print("\n" + "=" * 60)
    print("Example 3: Custom Voice Parameters")
    print("=" * 60)
    
    # Different emotional tones
    texts = [
        {"text": "好消息！恒指突破兩萬點大關", "speed": 1.3, "pitch": 15},
        {"text": "壞消息... 美股昨晚大跌 3%", "speed": 0.8, "pitch": -10},
        {"text": "市場分析師認為短期會繼續波動", "speed": 1.0, "pitch": 0},
    ]
    
    try:
        for idx, item in enumerate(texts):
            filename = f"emotion_example_{idx+1}.wav"
            audio_path = await cantonese_tts.synthesize_speech(
                text=item["text"],
                output_filename=filename,
                speed=item["speed"],
                pitch=item["pitch"]
            )
            print(f"Generated {filename} with speed={item['speed']}, pitch={item['pitch']}")
        
        print("\nEmotional variations created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run all examples"""
    print("\n🎙️ Cantonese AI TTS Integration Examples")
    print("粵語 AI 語音合成示例\n")
    
    # Run examples
    await example_single_synthesis()
    await example_batch_synthesis()
    await example_with_custom_voice()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check 'audio/generated/' folder for output files")
    print("2. Use audio_processor.py to merge segments")
    print("3. Integrate with podcast_generator.py for full automation")

if __name__ == "__main__":
    asyncio.run(main())
