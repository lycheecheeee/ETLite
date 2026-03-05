import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { Send, Mic, Sparkles, User, Bot, Volume2, Copy, ThumbsUp, RotateCcw } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  audioUrl?: string
  isPlaying?: boolean
}

const WELCOME_MESSAGE = "哈囉！我係叻仔，你嘅 AI 理財助手🎙️\n\n我可以幫你：\n• 解答投資疑難\n• 分析市場走勢\n• 提供理財建議\n• 傾下計都得！\n\n有咩幫到你呀？"

export function ChatWithLeungZai() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: WELCOME_MESSAGE,
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 模擬 AI 回應（之後可以接真實 API）
  const generateAIResponse = async (userMessage: string): Promise<string> => {
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000))
    
    const responses: Record<string, string[]> = {
      greeting: [
        "早晨啊！今日恒指高開，心情都好啲啦！",
        "哈囉！想知今日邊隻股票值得買？",
        "你好呀！有咩投資問題想問我？"
      ],
      market: [
        "今日恒指升 256 點，科技股領漲。騰訊升 3%，美團升 5%。短線睇好，但都要小心阻力位。",
        "市場情緒而家幾樂觀，成交額增加到 1200 億。建議關注科網股同內房股。",
        "外圍美股昨晚齊升，利好港股。不過要留意 18500 點阻力。"
      ],
      stock: [
        "騰訊 (0700) 而家報 368 元，PE 約 20 倍，估值合理。業績強勁，遊戲業務復甦，中長線睇好。",
        "美團 (3690) 突破 130 元關口，外賣業務增長穩定，新業務減虧，值得中線持有。",
        "阿里 (9988) 喺 80 元左右上落，等待新催化劑。雲計算業務係亮點。"
      ],
      advice: [
        "投資要分散風險，唔好将所有資金放入一隻股票。建議 60% 藍籌 + 40% 成長股。",
        "新手建議由指数基金開始，例如盈富基金 (2800)，費用低又分散風險。",
        "記住口訣：『唔好貪心，設好止蝕』。一般建議止蝕位設在买入價的 -8% 到 -10%。"
      ],
      default: [
        "明白你嘅問題。從技術分析黎睇，而家個市處於上升趨勢，但都要小心回調風險。",
        "呢個問題好好！我認為要考慮多個因素：宏觀經濟、公司基本面、技術指標。",
        "多謝你嘅提問！根據我嘅分析，建議你..."
      ]
    }

    // 簡單關鍵詞匹配
    const lowerMsg = userMessage.toLowerCase()
    let category = 'default'
    
    if (lowerMsg.includes('早晨') || lowerMsg.includes('你好') || lowerMsg.includes('哈囉')) {
      category = 'greeting'
    } else if (lowerMsg.includes('恒指') || lowerMsg.includes('大市') || lowerMsg.includes('市場')) {
      category = 'market'
    } else if (lowerMsg.includes('騰訊') || lowerMsg.includes('美團') || lowerMsg.includes('阿里') || lowerMsg.includes('股')) {
      category = 'stock'
    } else if (lowerMsg.includes('建議') || lowerMsg.includes('點樣') || lowerMsg.includes('應該')) {
      category = 'advice'
    }

    const options = responses[category]
    return options[Math.floor(Math.random() * options.length)]
  }

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    try {
      const aiResponse = await generateAIResponse(userMessage.content)
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error generating response:', error)
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const speakMessage = async (text: string) => {
    if (isSpeaking) return
    
    setIsSpeaking(true)
    
    // 使用 Cantonese AI TTS API
    try {
      const response = await fetch('https://cantonese.ai/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: 'sk-o0sqn7wHhgsSqHoNW0j58q0f0vwcms9',
          text: text,
          frame_rate: '24000',
          speed: 1,
          pitch: 0,
          language: 'cantonese',
          output_extension: 'wav',
          voice_id: '2725cf0f-efe2-4132-9e06-62ad84b2973d',
          should_return_timestamp: false
        })
      })

      if (response.ok) {
        const audioBlob = await response.blob()
        const audioUrl = URL.createObjectURL(audioBlob)
        const audio = new Audio(audioUrl)
        
        audio.play()
        audio.onended = () => {
          setIsSpeaking(false)
          URL.revokeObjectURL(audioUrl)
        }
      } else {
        setIsSpeaking(false)
      }
    } catch (error) {
      console.error('TTS Error:', error)
      setIsSpeaking(false)
    }
  }

  return (
    <div className="flex flex-col h-[600px] glass-card rounded-2xl overflow-hidden glow-border">
      {/* 頂部 */}
      <div className="bg-gradient-to-r from-primary to-secondary p-4 flex items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm">
          <Bot className="w-7 h-7 text-white" />
        </div>
        <div className="flex-1">
          <h2 className="text-lg font-bold text-white">叻仔 Leung Zai</h2>
          <p className="text-sm text-white/80">AI 粵語理財助手</p>
        </div>
        <div className="flex items-center gap-2 text-white/80 text-sm">
          <Sparkles className="w-4 h-4" />
          <span>在線</span>
        </div>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-background/50">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex gap-3 animate-slide-up",
              message.role === 'user' ? "flex-row-reverse" : ""
            )}
          >
            {/* 頭像 */}
            <div className={cn(
              "w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0",
              message.role === 'user' 
                ? "bg-gradient-to-br from-blue-500 to-purple-500" 
                : "bg-gradient-to-br from-primary to-secondary"
            )}>
              {message.role === 'user' ? (
                <User className="w-5 h-5 text-white" />
              ) : (
                <Bot className="w-5 h-5 text-white" />
              )}
            </div>

            {/* 消息內容 */}
            <div className={cn(
              "max-w-[70%] space-y-2",
              message.role === 'user' ? "items-end" : "items-start"
            )}>
              <div className={cn(
                "rounded-2xl px-4 py-3",
                message.role === 'user'
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted border border-border"
              )}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>

              {/* 操作按鈕 */}
              {message.role === 'assistant' && (
                <div className="flex items-center gap-2 pl-1">
                  <button
                    onClick={() => speakMessage(message.content)}
                    disabled={isSpeaking}
                    className="p-1.5 rounded-lg hover:bg-muted transition-colors"
                    title="朗讀"
                  >
                    <Volume2 className={cn("w-4 h-4", isSpeaking && "animate-pulse")} />
                  </button>
                  <button
                    onClick={() => copyToClipboard(message.content)}
                    className="p-1.5 rounded-lg hover:bg-muted transition-colors"
                    title="複製"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    className="p-1.5 rounded-lg hover:bg-muted transition-colors"
                    title="有用"
                  >
                    <ThumbsUp className="w-4 h-4" />
                  </button>
                </div>
              )}

              {/* 時間戳 */}
              <p className="text-xs text-muted-foreground px-1">
                {message.timestamp.toLocaleTimeString('zh-HK', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </p>
            </div>
          </div>
        ))}

        {/* 輸入中提示 */}
        {isTyping && (
          <div className="flex gap-3 animate-fade-in">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-muted rounded-2xl px-4 py-3">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 輸入區域 */}
      <div className="border-t border-border p-4 bg-background/80 backdrop-blur-sm">
        {/* 快捷問題 */}
        <div className="flex gap-2 mb-3 overflow-x-auto pb-2">
          {[
            "今日恒指点睇？",
            "騰訊值唔值得買？",
            "新手點開始投資？",
            "點樣分散風險？"
          ].map((question) => (
            <button
              key={question}
              onClick={() => setInput(question)}
              className="px-3 py-1.5 rounded-full bg-primary/10 text-primary text-sm whitespace-nowrap hover:bg-primary/20 transition-colors"
            >
              {question}
            </button>
          ))}
        </div>

        {/* 輸入框 */}
        <div className="flex gap-2 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="輸入你想問嘅問題..."
              rows={1}
              className="w-full resize-none rounded-xl bg-muted border border-border px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
            <button
              className="absolute right-2 bottom-2 p-2 rounded-lg hover:bg-primary/10 transition-colors"
              title="語音輸入（即將推出）"
            >
              <Mic className="w-5 h-5 text-muted-foreground" />
            </button>
          </div>

          <button
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className={cn(
              "w-12 h-12 rounded-xl flex items-center justify-center transition-all",
              input.trim() && !isTyping
                ? "bg-gradient-to-br from-primary to-secondary hover:scale-105 shadow-glow"
                : "bg-muted opacity-50 cursor-not-allowed"
            )}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-muted-foreground mt-2 text-center">
          叻仔提供嘅內容僅供參考，不構成投資建議
        </p>
      </div>
    </div>
  )
}
