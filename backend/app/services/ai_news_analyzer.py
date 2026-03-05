"""
AI News Analyzer Service
AI 分析財經新聞並生成節目腳本
"""
from typing import List, Dict, Optional
import aiohttp
from app.core.config import settings

class AINewsAnalyzer:
    """Analyze news and generate podcast scripts using AI"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    async def analyze_and_generate_script(
        self,
        news_items: List[Dict],
        focus_topic: str = "AI趨勢",
        host_name: str = "叻仔"
    ) -> Dict:
        """
        Analyze news and generate podcast script
        
        Args:
            news_items: List of news items from RSS
            focus_topic: Main topic to focus on (e.g., "AI趨勢")
            host_name: Host name
            
        Returns:
            Script with segments and analysis
        """
        
        # Prepare news context
        news_context = "\n\n".join([
            f"{i+1}. {item['title']}\n   {item['content'][:200]}..."
            for i, item in enumerate(news_items[:10])
        ])
        
        system_prompt = f"""
你係 {host_name}，一個專業嘅粵語財經節目主持人。

**任務：**
根據提供嘅財經新聞，生成一個 5-8 分鐘嘅 AI趨勢分析節目腳本。

**節目結構：**
1. 開場問候（30 秒）
2. 今日重點新聞速遞（2 分鐘）
3. AI趨勢深度分析（3-4 分鐘）
4. 投資建議同啟示（1 分鐘）
5. 結語（30 秒）

**風格要求：**
- 用廣東話口語（唔好書面語）
- 生動有趣，好似同朋友傾計
- 專業但不失幽默
- 適中使用 emoji 📈🤖💰
- 解釋複雜概念時用例子

**特別聚焦：**
- 重點分析同 AI 相關嘅新聞
- 連結到香港/中國市場
- 提供實用投資啟示
"""

        user_prompt = f"""
請根據以下財經新聞，生成一個完整嘅節目腳本：

{news_context}

**特別關注：** {focus_topic}

請按節目結構生成腳本，每個部分標明預計時間。
"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.7
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        script_content = data["choices"][0]["message"]["content"]
                        
                        # Parse script into segments
                        segments = self._parse_script(script_content)
                        
                        return {
                            "title": f"AI趨勢日報 - {focus_topic}",
                            "description": f"由 {host_name} 為你分析今日 AI趨勢同投資機會",
                            "duration_estimate": len(segments) * 60,  # Rough estimate
                            "segments": segments,
                            "full_script": script_content,
                            "news_count": len(news_items)
                        }
                    else:
                        print(f"[AI Analyzer] API Error: {response.status}")
                        return self._get_fallback_script(focus_topic)
                        
        except Exception as e:
            print(f"[AI Analyzer] Error: {e}")
            return self._get_fallback_script(focus_topic)
    
    def _parse_script(self, script_content: str) -> List[Dict]:
        """Parse script text into structured segments"""
        import re
        
        segments = []
        
        # Try to detect sections by common patterns
        section_patterns = [
            (r'(開場|問候 | 第一部分 | 1\.|intro)', 'intro'),
            (r'(新聞 | 速遞 | 第二部分 | 2\.|news)', 'news_roundup'),
            (r'(分析 | 深度 | 第三部分 | 3\.|analysis)', 'ai_analysis'),
            (r'(建議 | 啟示 | 第四部分 | 4\.|advice)', 'investment_advice'),
            (r'(結語 | 結束 | 第五部分 | 5\.|closing)', 'closing')
        ]
        
        lines = script_content.split('\n')
        current_segment = {"type": "unknown", "title": "", "content": ""}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header
            detected_type = None
            title_match = None
            
            for pattern, seg_type in section_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    detected_type = seg_type
                    # Extract title (everything after the number/marker)
                    title_match = re.sub(r'^\d+[\.\)]\s*', '', line)
                    break
            
            if detected_type:
                # Save previous segment if it has content
                if current_segment["content"].strip():
                    segments.append({
                        "type": current_segment["type"],
                        "title": current_segment["title"] or f"Segment {len(segments)+1}",
                        "content": current_segment["content"].strip()
                    })
                
                # Start new segment
                current_segment = {
                    "type": detected_type,
                    "title": title_match or detected_type.replace('_', ' ').title(),
                    "content": ""
                }
            else:
                # Add content to current segment
                current_segment["content"] += "\n" + line
        
        # Don't forget the last segment
        if current_segment["content"].strip():
            segments.append({
                "type": current_segment["type"],
                "title": current_segment["title"] or f"Segment {len(segments)+1}",
                "content": current_segment["content"].strip()
            })
        
        # Ensure we have at least some segments with proper structure
        if len(segments) < 3:
            # Fallback: split by length
            full_text = script_content.strip()
            chunks = [full_text[i:i+500] for i in range(0, len(full_text), 500)]
            
            segment_types = ['intro', 'ai_analysis', 'closing']
            segments = [
                {
                    "type": segment_types[i] if i < len(segment_types) else 'unknown',
                    "title": f"Part {i+1}",
                    "content": chunk.strip()
                }
                for i, chunk in enumerate(chunks)
            ]
        
        return segments
    
    def _get_fallback_script(self, focus_topic: str) -> Dict:
        """Fallback script when AI is unavailable"""
        return {
            "title": f"AI趨勢日報 - {focus_topic}",
            "description": "財經新聞分析節目",
            "duration_estimate": 300,
            "segments": [
                {
                    "type": "intro",
                    "content": f"哈囉！我係叻仔，歡迎收聽今日嘅 AI趨勢日報。"
                },
                {
                    "type": "news",
                    "content": "今日有幾單重要財經新聞，等我同大家分享一下..."
                },
                {
                    "type": "analysis",
                    "content": f"講返 {focus_topic}，呢個係而家好熱門嘅話題..."
                },
                {
                    "type": "closing",
                    "content": "多謝收聽，聽日見！"
                }
            ],
            "full_script": "Fallback script",
            "news_count": 0
        }


# Global analyzer instance
ai_analyzer = AINewsAnalyzer()
