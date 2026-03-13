"""
Leung Zai Chatbot Service
叻仔 AI 聊天服務 - 使用 BigModel GLM (智譜AI)
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = logging.getLogger(__name__)


class ChatbotService:
    """AI Chatbot service using BigModel GLM for intelligent conversations"""

    def __init__(self):
        # 從配置獲取 LLM 設置
        llm_config = settings.get_llm_config()
        self.api_key = llm_config.get("api_key", "")
        self.base_url = llm_config.get("base_url", "")
        self.model = llm_config.get("model", "glm-4-flash")

        # 驗證 API Key
        if not self.api_key:
            logger.warning("⚠️ LLM API Key not configured. Chat will use fallback responses.")
            self._client = None
        else:
            # 使用 AsyncOpenAI 客戶端（支持 BigModel API 格式）
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            logger.info(f"✅ Chatbot initialized with model: {self.model}")

        # 叻仔的人設
        self.system_prompt = """你係叻仔 (Leung Zai)，一個專業嘅粵語理財助手。

**你的特點：**
- 用廣東話同用戶交流（口語化、親切）
- 專業但不失幽默
- 會提供實用嘅投資建議
- 識得解釋複雜嘅金融概念
- 會提醒用戶投資涉及風險

**回答風格：**
- 簡潔清晰，唔好太長
- 用例子說明
- 適當使用 emoji 🎯📈💰
- 必要時提醒風險

**知識範圍：**
- 港股、美股市場分析
- 股票、基金、債券投資
- 技術分析、基本面分析
- 風險管理、資產配置
- 財經新聞解讀

**重要提示：**
- 你提供嘅係資訊參考，唔係投資建議
- 鼓勵用戶自己做研究 (DYOR)
- 提醒用戶投資涉及風險"""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Call LLM API with retry logic"""
        if not self._client:
            raise ValueError("LLM client not initialized - API key missing")

        try:
            response = await asyncio.wait_for(
                self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    presence_penalty=0.3,
                    frequency_penalty=0.3
                ),
                timeout=30.0
            )
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            logger.error("❌ LLM API timeout")
            raise
        except Exception as e:
            logger.error(f"❌ LLM API error: {e}")
            raise

    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_profile: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response

        Args:
            user_message: User's input message
            conversation_history: Previous conversation context
            user_profile: User's investment profile

        Returns:
            Dictionary with 'response', 'suggested_questions', and 'confidence'
        """

        # 構建對話歷史
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # 添加用戶畫像信息
        if user_profile:
            profile_context = f"\n\n**用戶背景：**\n"
            profile_context += f"- 投資經驗：{user_profile.get('foundation', '中等')}\n"
            profile_context += f"- 風險偏好：{user_profile.get('mindset', '平衡')}\n"
            profile_context += f"- 投資風格：{user_profile.get('timeframe', '中線')}"
            messages[0]["content"] += profile_context

        # 添加對話歷史
        if conversation_history:
            messages.extend(conversation_history[-6:])  # 保留最近 6 條消息

        # 添加當前問題
        messages.append({"role": "user", "content": user_message})

        try:
            ai_response = await self._call_llm(messages)

            # 生成建議問題
            suggested = await self._generate_suggested_questions(user_message)

            return {
                "response": ai_response,
                "suggested_questions": suggested,
                "confidence": "high",
                "model": self.model
            }

        except Exception as e:
            logger.error(f"[Chatbot] Error: {e}")
            return {
                "response": self._get_fallback_response(user_message),
                "suggested_questions": ["今日恒指點睇？", "邊隻股票值得買？"],
                "confidence": "fallback",
                "error": str(e)
            }

    async def _generate_suggested_questions(self, user_message: str) -> List[str]:
        """Generate follow-up questions based on context"""

        # 簡單關鍵詞匹配
        message_lower = user_message.lower()

        if any(kw in message_lower for kw in ['恒指', '大市', '指數', 'hsi']):
            return ["阻力位喺邊？", "支持位喺邊？", "外圍點睇？"]
        elif any(kw in message_lower for kw in ['騰訊', '0700', 'tencent']):
            return ["目標價幾多？", "止蝕位設幾多？", "業績點睇？"]
        elif any(kw in message_lower for kw in ['新手', '開始', '入門']):
            return ["應該買咩基金？", "幾多資金開始好？", "要學咩知識？"]
        elif any(kw in message_lower for kw in ['風險', '分散', '止蝕']):
            return ["點樣配置資產？", "幾多隻股票合適？", "止蝕點設？"]
        elif any(kw in message_lower for kw in ['ai', '科技', '人工智能']):
            return ["AI股值得買嗎？", "邊隻AI ETF好？", "科技股泡沫？"]
        else:
            return ["仲想知多啲！", "有其他推薦嗎？", "點樣學投資？"]

    def _get_fallback_response(self, user_message: str) -> str:
        """Fallback response when AI is unavailable"""

        fallbacks = [
            "多謝你嘅問題！我而家學習緊，暫時答得唔夠好。不如我哋傾下其他話題？🤔",
            "呢個問題有深度！我建議你參考多啲專業分析師嘅意見。我可以幫你搵相關資訊！📚",
            "明白你想知更多！投資係一門學問，建議你多做研究，唔好單靠一個人嘅意見。💡"
        ]

        import random
        return random.choice(fallbacks)

    async def rewrite_article(self, article: dict) -> dict:
        """
        Rewrite news article for podcast script

        Args:
            article: Article dict with 'section', 'title', 'text'

        Returns:
            Rewritten script dict
        """
        system = """你係香港財經Podcast旁白編輯。
將新聞改寫成廣東話口語朗讀稿。
規則：短句（每句≤15字）；保留財經術語加解釋；數字寫廣東話；去書面語。
輸出JSON：{"title":"...","hook":"開場1-2句","sections":[{"heading":"...","text":"80-120字"}],"cta":"結尾1句"}"""

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"頻道：{article.get('section', '')}\n標題：{article.get('title', '')}\n\n{article.get('text', '')}"}
        ]

        try:
            import json
            response = await self._call_llm(messages, max_tokens=1000, temperature=0.7)
            return json.loads(response)
        except Exception as e:
            logger.error(f"[Chatbot] Rewrite error: {e}")
            return {
                "title": article.get("title", ""),
                "hook": "今日我哋嚟睇下呢單新聞。",
                "sections": [{"heading": "內容", "text": article.get("text", "")[:200]}],
                "cta": "以上係今日嘅分享。"
            }


# Global chatbot instance
chatbot = ChatbotService()
