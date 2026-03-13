"""
Test News Podcast Generation
測試新聞播客生成功能
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.rss_service import rss_service
from app.services.ai_news_analyzer import ai_analyzer
from app.services.cantonese_tts_service import cantonese_tts


async def test_news_podcast():
    """Test complete news podcast generation pipeline"""
    
    print("=" * 60)
    print("🎙️ 測試 AI 新聞播客生成")
    print("=" * 60)
    
    # Step 1: Fetch RSS news
    print("\n📰 步驟 1: 抓取 RSS 新聞...")
    try:
        news_items = await rss_service.get_latest_news(
            categories=["rumour", "tech"],
            total_limit=5
        )
        print(f"✅ 成功抓取 {len(news_items)} 則新聞")
        for i, news in enumerate(news_items[:3], 1):
            print(f"   {i}. {news['title']}")
    except Exception as e:
        print(f"❌ RSS 抓取失敗：{e}")
        return
    
    # Step 2: Generate script with AI
    print("\n🤖 步驟 2: AI 生成節目腳本...")
    try:
        script = await ai_analyzer.analyze_and_generate_script(
            news_items=news_items,
            focus_topic="AI趨勢",
            host_name="叻仔"
        )
        print(f"✅ 腳本生成成功")
        print(f"   標題：{script['title']}")
        print(f"   分段數：{len(script['segments'])}")
        print(f"   總字數：{sum(len(seg['content']) for seg in script['segments'])}")
        
        # Show first segment
        if script['segments']:
            print(f"\n   第一段內容:")
            print(f"   {script['segments'][0]['content'][:200]}...")
    except Exception as e:
        print(f"❌ AI 腳本生成失敗：{e}")
        return
    
    # Step 3: Synthesize speech with Cantonese AI TTS
    print("\n🔊 步驟 3: Cantonese AI TTS 語音合成...")
    try:
        audio_files = []
        for idx, segment in enumerate(script['segments'][:2]):  # Test first 2 segments
            filename = f"test_segment_{idx+1}.wav"
            print(f"   合成第 {idx+1} 段：{segment['type']}...")
            
            audio_path = await cantonese_tts.synthesize_speech(
                text=segment['content'],
                output_filename=filename,
                speed=1.0,
                pitch=0
            )
            
            audio_files.append(audio_path)
            print(f"   ✅ 合成成功：{audio_path}")
        
        print(f"\n✅ 語音合成完成！共 {len(audio_files)} 個音頻文件")
        
    except Exception as e:
        print(f"❌ TTS 合成失敗：{e}")
        print("   提示：請確保已配置 CANTONESE_AI_API_KEY 環境變量")
        return
    
    print("\n" + "=" * 60)
    print("✅ 測試完成！")
    print("=" * 60)
    print("\n生成的音頻文件位於：backend/app/static/audio/")
    print("啟動後端服務後，可在前端收聽")


if __name__ == "__main__":
    # Set Windows encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    asyncio.run(test_news_podcast())
