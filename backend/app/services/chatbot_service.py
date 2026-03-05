"""
Leung Zai Chatbot Service
叻仔 AI 聊天服務 - 使用 OpenAI/LangChain
"""
from typing import Optional, List, Dict
import aiohttp
from app.core.config import settings

class ChatbotService:
    """AI Chatbot service for intelligent conversations"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        # 叻仔的人設
        self.system_prompt = """
你係叻仔 (Leung Zai)，一個專業嘅粵語理財助手。

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
- 提醒用戶投資涉及風險
"""
    
    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_profile: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Generate AI response
        
        Args:
            user_message: User's input message
            conversation_history: Previous conversation context
            user_profile: User's investment profile
            
        Returns:
            Dictionary with 'response' and 'suggested_questions'
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
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": messages,
                        "max_tokens": 500,
                        "temperature": 0.7,
                        "presence_penalty": 0.3,
                        "frequency_penalty": 0.3
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        ai_response = data["choices"][0]["message"]["content"]
                        
                        # 生成建議問題
                        suggested = await self._generate_suggested_questions(user_message)
                        
                        return {
                            "response": ai_response,
                            "suggested_questions": suggested,
                            "confidence": "high"
                        }
                    else:
                        error_text = await response.text()
                        print(f"[Chatbot] API Error: {response.status}")
                        print(f"[Chatbot] Response: {error_text}")
                        
                        # 降級回應
                        return {
                            "response": self._get_fallback_response(user_message),
                            "suggested_questions": ["今日恒指點睇？", "邊隻股票值得買？"],
                            "confidence": "low"
                        }
                        
        except Exception as e:
            print(f"[Chatbot] Error: {e}")
            return {
                "response": self._get_fallback_response(user_message),
                "suggested_questions": ["今日恒指點睇？", "點樣分散風險？"],
                "confidence": "fallback"
            }
    
    async def _generate_suggested_questions(self, user_message: str) -> List[str]:
        """Generate follow-up questions based on context"""
        
        # 簡單關鍵詞匹配
        if any(kw in user_message.lower() for kw in ['恒指', '大市', '指數']):
            return ["阻力位喺邊？", "支持位喺邊？", "外圍點睇？"]
        elif any(kw in user_message.lower() for kw in ['騰訊', '0700']):
            return ["目標價幾多？", "止蝕位設幾多？", "業績點睇？"]
        elif any(kw in user_message.lower() for kw in ['新手', '開始']):
            return ["應該買咩基金？", "幾多資金開始好？", "要學咩知識？"]
        elif any(kw in user_message.lower() for kw in ['風險', '分散']):
            return ["點樣配置資產？", "幾多隻股票合適？", "止蝕點設？"]
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


# Global chatbot instance
chatbot = ChatbotService()
