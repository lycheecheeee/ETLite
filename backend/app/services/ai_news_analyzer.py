"""
AI News Analyzer Service
AI 分析財經新聞並生成節目腳本 - 使用 BigModel GLM (智譜AI)
"""
import asyncio
import json
import re
import logging
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.rss_service import rss_service

logger = logging.getLogger(__name__)


class AINewsAnalyzer:
    """Analyze news and generate podcast scripts using BigModel GLM"""

    def __init__(self):
        # 從配置獲取 LLM 設置
        llm_config = settings.get_llm_config()
        self.api_key = llm_config.get("api_key", "")
        self.base_url = llm_config.get("base_url", "")
        self.model = llm_config.get("model", "glm-4-flash")
        self.model_quality = llm_config.get("model_quality", "glm-4-air")
        self.model_quick = llm_config.get("model", "glm-4-flash")
        
        # TTS 配置
        tts_config = settings.get_tts_config()
        self.tts_api_url = tts_config.get("api_url", "")
        self.tts_api_key = tts_config.get("api_key", "")
        self.tts_voice_id = tts_config.get("voice_id", "")
        self.tts_concurrency = tts_config.get("concurrency", 8)
        self.tts_chunk_size = tts_config.get("chunk_size", 450)
        self.output_dir = Path(settings.OUTPUT_DIR) / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 驗證 API Key
        if not self.api_key:
            logger.warning("LLM API Key not configured. AI analyzer will use fallback responses.")
            self._client = None
        else:
            # 使用 AsyncOpenAI 客戶端（支持 BigModel API 格式）
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info(f"AI News Analyzer initialized with model: {self.model}")
        
        # 驗證 TTS 配置
        if not self.tts_api_key:
            logger.warning("TTS API Key not configured. Audio generation will be skipped.")
            self._tts_semaphore = None
        else:
            self._tts_semaphore = asyncio.Semaphore(self.tts_concurrency)
            logger.info(f"TTS Semaphore initialized with concurrency={self.tts_concurrency}")

    async def analyze_and_generate_script(
        self,
        news_items: List[Dict],
        focus_topic: str = "AI趨勢",
        host_name: str = "叻仔"
    ) -> Dict:
        """Analyze news and generate podcast scripts using BigModel GLM"""
        
        if not self._client:
            logger.warning("LLM client not initialized. Returning fallback script.")
            return self._get_fallback_script(focus_topic, host_name)
        
        # 准备新闻摘要
        news_context = "\n\n".join([
            f"{i+1}. {item.get('title', 'Unknown')}\n   {item.get('content', '')[:200]}..."
            for i, item in enumerate(news_items[:10])
        ])
        
        system_prompt = f"""你係{host_name}，一個專業嘅粵語財經節目主持人。

**任務：**
根據提供嘅財經新聞，生成一個完整嘅節目腳本

**節目結構：**
1. 開場問候 (30秒)
2. 新聞速遞 (2分鐘)
3. AI深度分析 (3-4分鐘)
4. 投資建議 (1分鐘)
5. 結語 (30秒)

**特別關注:** {focus_topic}

**風格要求:**
- 用廣東話口語
- 生動有趣
- 專業但實用

**輸出格式:** JSON
"""
        
        user_prompt = f"""
請根據以下財經新聞生成節目腳本:

{news_context}

**特別關注:** {focus_topic}
"""
        
        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.7
            )
            
            script_content = response.choices[0].message.content
            segments = self._parse_script(script_content, focus_topic, host_name)
            
            return {
                "title": f"AI趨勢日報 - {focus_topic}",
                "description": f"由 {host_name} 為你分析今日 AI 趨勢同投資機會",
                "duration_estimate": len(segments) * 60,
                "segments": segments,
                "full_script": script_content,
                "news_count": len(news_items)
            }
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return self._get_fallback_script(focus_topic, host_name)

    def _parse_script(self, script_content: str, focus_topic: str, host_name: str) -> List[Dict]:
        """Parse script text into structured segments"""
        segments = []
        lines = script_content.split("\n")
        current_segment = {"type": "unknown", "title": "", "content": ""}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if "開場" in line or "問候" in line or "第一部分" in line:
                if current_segment["content"].strip():
                    segments.append({
                        "type": current_segment["type"],
                        "title": current_segment["title"],
                        "content": current_segment["content"].strip()
                    })
                current_segment = {"type": "intro", "title": line, "content": ""}
            elif "新聞" in line or "速遞" in line or "第二部分" in line:
                if current_segment["content"].strip():
                    segments.append({
                        "type": current_segment["type"],
                        "title": current_segment["title"],
                        "content": current_segment["content"].strip()
                    })
                current_segment = {"type": "news_roundup", "title": line, "content": ""}
            elif "分析" in line or "深度" in line or "第三部分" in line:
                if current_segment["content"].strip():
                    segments.append({
                        "type": current_segment["type"],
                        "title": current_segment["title"],
                        "content": current_segment["content"].strip()
                    })
                current_segment = {"type": "ai_analysis", "title": line, "content": ""}
            elif "建議" in line or "啟示" in line or "第四部分" in line:
                if current_segment["content"].strip():
                    segments.append({
                        "type": current_segment["type"],
                        "title": current_segment["title"],
                        "content": current_segment["content"].strip()
                    })
                current_segment = {"type": "investment_advice", "title": line, "content": ""}
            elif "結語" in line or "結束" in line or "第五部分" in line:
                if current_segment["content"].strip():
                    segments.append({
                        "type": current_segment["type"],
                        "title": current_segment["title"],
                        "content": current_segment["content"].strip()
                    })
                current_segment = {"type": "closing", "title": line, "content": ""}
            else:
                current_segment["content"] += "\n" + line
        
        # Add last segment
        if current_segment["content"].strip():
            segments.append({
                "type": current_segment["type"],
                "title": current_segment["title"],
                "content": current_segment["content"].strip()
            })
        
        # Ensure minimum segments
        if len(segments) < 3:
            full_text = script_content.strip()
            chunks = [full_text[i:i+500] for i in range(0, len(full_text), 500)]
            segment_types = ["intro", "ai_analysis", "closing"]
            segments = []
            for i, chunk in enumerate(chunks):
                segments.append({
                    "type": segment_types[i] if i < len(segment_types) else "unknown",
                    "title": f"部分 {i+1}",
                    "content": chunk.strip()
                })
        
        return segments

    def _get_fallback_script(self, focus_topic: str, host_name: str) -> Dict:
        """Fallback script when AI is unavailable"""
        return {
            "title": f"AI趨勢日報 - {focus_topic}",
            "description": "財經新聞分析節目(示例)",
            "duration_estimate": 300,
            "segments": [
                {
                    "type": "intro",
                    "title": "開場問候",
                    "content": f"哈囉！我係{host_name}，歡迎收聽今日嘅 AI 趨勢分析節目。今日我哋會重點分析 {focus_topic} 相關嘅市場動態。"
                },
                {
                    "type": "news",
                    "title": "新聞速遞",
                    "content": "今日有幾則重要 AI 相關新聞.市場反應熱烈,科技股領漲大市."
                },
                {
                    "type": "analysis",
                    "title": "深度分析",
                    "content": f"講返 {focus_topic} 呢個話題,從技術面同市場都處於上升趨勢.基本面方面,行業增長強勁."
                },
                {
                    "type": "closing",
                    "title": "節目結語",
                    "content": f"多謝收聽今日嘅節目.聽日見！ {host_name} 為你繼續帶嚏更多 AI 趨勢分析.投資愉快!"
                }
            ],
            "full_script": "這是示例腳本內容...",
            "news_count": 0
        }


# Global analyzer instance
ai_analyzer = AINewsAnalyzer()
