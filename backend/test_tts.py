"""
TTS Service Test Script
測試 TTS 語音生成功能
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tts_service import tts_service

async def test_basic_tts():
    """Test basic text-to-speech"""
    print("🎙️ Testing basic TTS...")
    
    text = "早晨！我係子程，歡迎收聽 Net 仔財經早新聞"
    
    try:
        audio_path = await tts_service.synthesize_speech(
            text=text,
            output_filename="test_basic.wav"
        )
        print(f"✅ Basic TTS successful: {audio_path}")
        return True
    except Exception as e:
        print(f"❌ Basic TTS failed: {e}")
        return False

async def test_emotional_tts():
    """Test emotional speech synthesis"""
    print("\n🎭 Testing emotional TTS...")
    
    emotions = ["cheerful", "professional", "excited", "friendly"]
    texts = [
        "恒指今日大升 500 點！",
        "分析師建議謹慎部署",
        "騰訊業績超預期，股價急升！",
        "多謝你嘅提問，我哋而家分析一下"
    ]
    
    results = []
    for emotion, text in zip(emotions, texts):
        try:
            filename = f"test_{emotion}.wav"
            audio_path = await tts_service.synthesize_with_emotion(
                text=text,
                emotion=emotion,
                output_filename=filename
            )
            print(f"  ✅ {emotion}: {audio_path}")
            results.append(True)
        except Exception as e:
            print(f"  ❌ {emotion} failed: {e}")
            results.append(False)
    
    return all(results)

async def test_batch_synthesis():
    """Test batch synthesis"""
    print("\n📦 Testing batch synthesis...")
    
    segments = [
        {"text": "早晨！我係子程", "emotion": "cheerful"},
        {"text": "今日恒指高開 256 點", "emotion": "professional"},
        {"text": "騰訊業績非常強勁", "emotion": "excited"},
        {"text": "建議投資者謹慎追入", "emotion": "friendly"}
    ]
    
    try:
        results = await tts_service.batch_synthesize(
            texts=segments,
            prefix="test_batch"
        )
        
        success_count = sum(1 for r in results if r is not None)
        print(f"  ✅ Batch synthesis: {success_count}/{len(segments)} segments generated")
        return success_count == len(segments)
    except Exception as e:
        print(f"  ❌ Batch synthesis failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("Net 仔 TTS Service - Test Suite")
    print("=" * 60)
    
    # Check if Azure key is configured
    if not os.getenv("AZURE_SPEECH_KEY"):
        print("\n⚠️  AZURE_SPEECH_KEY not set!")
        print("Please create backend/.env file with your Azure Speech key")
        print("\nYou can get a free key from:")
        print("https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices")
        return
    
    # Run tests
    test1 = await test_basic_tts()
    test2 = await test_emotional_tts()
    test3 = await test_batch_synthesis()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"  Basic TTS:        {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  Emotional TTS:    {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  Batch Synthesis:  {'✅ PASS' if test3 else '❌ FAIL'}")
    print("=" * 60)
    
    if all([test1, test2, test3]):
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    asyncio.run(main())
