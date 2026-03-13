"""
Test Cantonese AI TTS with Real API
測試 Cantonese AI TTS 真實語音合成
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.cantonese_tts_service import cantonese_tts


async def test_tts():
    """Test TTS synthesis with real API"""
    
    print("=" * 60)
    print("🔊 測試 Cantonese AI TTS 語音合成")
    print("=" * 60)
    print(f"\n使用 Voice ID: {cantonese_tts.voice_id}")
    print("（Mina 把聲）\n")
    
    # Test text
    test_texts = [
        "哈囉各位 Net 仔家族嘅朋友，早晨！我係敏娜。",
        "今日恒指高開 256 點，科技股領漲。",
        "講返 AI趨勢呢個話題，從技術面嚟睇，而家處於上升趨勢。"
    ]
    
    try:
        audio_files = []
        
        for idx, text in enumerate(test_texts, 1):
            print(f"\n📝 合成第 {idx} 段：")
            print(f"   文字：{text}")
            
            filename = f"test_mina_segment_{idx}.wav"
            audio_path = await cantonese_tts.synthesize_speech(
                text=text,
                output_filename=filename
            )
            
            audio_files.append(audio_path)
            print(f"   ✅ 成功！文件：{audio_path}")
        
        print("\n" + "=" * 60)
        print("✅ TTS 測試完成！")
        print("=" * 60)
        print(f"\n生成咗 {len(audio_files)} 個音頻文件:")
        for path in audio_files:
            file_size = os.path.getsize(path)
            print(f"   - {path} ({file_size:,} bytes)")
        
        print("\n💡 啟動後端服務後，可以喺前端收聽：")
        print("   cd backend && uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"\n❌ TTS 測試失敗：{e}")
        print("\n請檢查:")
        print("   1. CANTONESE_AI_API_KEY 是否正確")
        print("   2. 網絡連接是否正常")
        print("   3. API 服務是否運行中")


if __name__ == "__main__":
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    asyncio.run(test_tts())
