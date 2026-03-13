import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { Send, Mic, Sparkles, User, Bot, Volume2, Copy, ThumbsUp } from 'lucide-react'

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

  // 呼叫真實 AI API
  const generateAIResponse = async (userMessage: string): Promise<{response: string, suggested: string[]}> => {
    const backendUrl = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000'
    
    try {
      // 呼叫後端 AI API
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10秒超時

      const response = await fetch(`${backendUrl}/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          context: messages.slice(-4).map(m => ({ role: m.role, content: m.content }))
        }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (response.ok) {
        const data = await response.json()
        return {
          response: data.response || '抱歉，我暫時無法回應。',
          suggested: data.suggested_questions || []
        }
      } else {
        console.warn('API response not ok:', response.status, response.statusText)
      }
    } catch (error: unknown) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.warn('API request timeout')
      } else {
        console.error('AI API Error:', error)
      }
    }

    // Fallback: 本地簡單回應
    await new Promise(resolve => setTimeout(resolve, 800))
    return {
      response: `多謝你嘅問題：「${userMessage}」\n\n我而家仲學習緊，暫時答得唔夠好。不如試下問：\n• 今日恒指點睇？\n• 騰訊值唔值得買？\n• 新手點開始投資？`,
      suggested: ["今日恒指點睇？", "邊隻股票值得買？", "點樣分散風險？"]
    }
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
      const { response, suggested } = await generateAIResponse(userMessage.content)
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // 添加建議問題（如果有）
      if (suggested && suggested.length > 0) {
        // 可以喺 UI 度顯示建議問題
        console.log('Suggested:', suggested)
      }
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
      const apiKey = import.meta.env.VITE_CANTONESE_AI_API_KEY
      const endpoint = import.meta.env.VITE_CANTONESE_AI_ENDPOINT || 'https://cantonese.ai/api/tts'
      
      if (!apiKey) {
        console.warn('Cantonese AI API key not configured')
        setIsSpeaking(false)
        return
      }

      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000) // 15秒超時

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey,
          text: text.substring(0, 500), // 限制文本長度
          frame_rate: '24000',
          speed: 1,
          pitch: 0,
          language: 'cantonese',
          output_extension: 'wav',
          voice_id: '2725cf0f-efe2-4132-9e06-62ad84b2973d',
          should_return_timestamp: false
        }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (response.ok) {
        const audioBlob = await response.blob()
        const audioUrl = URL.createObjectURL(audioBlob)
        const audio = new Audio(audioUrl)
        
        audio.play().catch(error => {
          console.error('Audio playback failed:', error)
          setIsSpeaking(false)
        })
        
        audio.onended = () => {
          setIsSpeaking(false)
          URL.revokeObjectURL(audioUrl)
        }
      } else {
        console.warn('TTS API response not ok:', response.status)
        setIsSpeaking(false)
      }
    } catch (error: unknown) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.warn('TTS request timeout')
      } else {
        console.error('TTS Error:', error)
      }
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
