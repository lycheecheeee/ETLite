"""
Test News Podcast with Mock TTS
測試新聞播客生成（使用模擬 TTS）
"""
import asyncio
import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.rss_service import rss_service
from app.services.ai_news_analyzer import ai_analyzer


async def test_news_podcast_mock():
    """Test news podcast generation with mock TTS"""
    
    print("=" * 60)
    print("🎙️ 測試 AI 新聞播客生成（模擬 TTS 模式）")
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
            print(f"      來源：{news.get('source', '未知')}")
            print(f"      時間：{news.get('published', '未知')}")
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
        print(f"   描述：{script['description']}")
        print(f"   分段數：{len(script['segments'])}")
        
        total_chars = sum(len(seg['content']) for seg in script['segments'])
        print(f"   總字數：{total_chars}")
        print(f"   預計時長：{sum(len(seg['content']) * 0.06 for seg in script['segments']):.1f}秒")
        
        # Show all segments
        print(f"\n📝 節目分段詳情:")
        for idx, segment in enumerate(script['segments'], 1):
            print(f"\n   [{idx}] {segment['type'].upper()} - {segment.get('title', '無標題')}")
            print(f"       內容：{segment['content'][:150]}{'...' if len(segment['content']) > 150 else ''}")
        
        # Save script to file
        output_file = "backend/app/static/audio/test_script.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        print(f"\n💾 腳本已保存到：{output_file}")
        
    except Exception as e:
        print(f"❌ AI 腳本生成失敗：{e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ LLM 新聞分析完成！")
    print("=" * 60)
    print("\n⚠️  TTS 合成需要配置 API Key:")
    print("   - Cantonese AI: CANTONESE_AI_API_KEY")
    print("   - 或 Azure TTS: AZURE_SPEECH_KEY")
    print("\n💡 提示：前端會自動調用 TTS API 生成真實語音")
    print("   啟動後端服務：cd backend && uvicorn app.main:app --reload")


if __name__ == "__main__":
    # Set Windows encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    asyncio.run(test_news_podcast_mock())
