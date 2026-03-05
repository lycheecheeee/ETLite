import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { 
  Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, 
  Mic2, Phone, MessageCircle, Heart, Share2, Download,
  Radio, Disc, Music, Send, Sparkles
} from 'lucide-react'

interface AudioSegment {
  id: string
  host: 'zicheng' | 'mina'
  title: string
  content: string
  audioFile: string
  duration: number
  type: 'intro' | 'market' | 'stock' | 'interaction' | 'closing'
  transcript: string
}

const radioSegments: AudioSegment[] = [
  {
    id: '1',
    host: 'zicheng',
    title: '開場 - 晨早開市前瞻',
    content: '各位 Net 仔家族嘅朋友，早晨！我係子程。今日恒指高開 256 點，科技股領漲，我哋即刻睇下今日有咩焦點...',
    audioFile: '/dialogue/00_zicheng.wav',
    duration: 15.6,
    type: 'intro',
    transcript: '早晨！我係子程，歡迎收聽 Net 仔財經早新聞...'
  },
  {
    id: '2',
    host: 'mina',
    title: '個股分析 - 騰訊業績',
    content: '多謝子程。我係敏娜。騰訊尋晚公佈業績，全年盈利增長 25%，遊戲業務強勁...',
    audioFile: '/dialogue/01_mina.wav',
    duration: 4.0,
    type: 'stock',
    transcript: '多謝子程。騰訊業績超預期...'
  },
  {
    id: '3',
    host: 'zicheng',
    title: '板塊輪動 - 科技股',
    content: '講到科技股，今日阿里巴巴都升埋一份，科網股集體反彈...',
    audioFile: '/dialogue/02_zicheng.wav',
    duration: 11.7,
    type: 'market',
    transcript: '科技股今日全線上漲...'
  },
  {
    id: '4',
    host: 'mina',
    title: '聽眾互動環節',
    content: '而家到我哋嘅互動時間啦！收到 WhatsApp 消息，陳先生問：「而家追入騰訊合唔合適？」',
    audioFile: '/dialogue/03_mina.wav',
    duration: 9.1,
    type: 'interaction',
    transcript: '聽眾來電：而家追入騰訊合適嗎？'
  },
  {
    id: '5',
    host: 'zicheng',
    title: '專家回應',
    content: '陳先生好問題。我個人建議係...短期技術指標顯示超買，但長線基本面仍然向好...',
    audioFile: '/dialogue/04_zicheng.wav',
    duration: 10.3,
    type: 'interaction',
    transcript: '子程回應：建議分段建倉...'
  },
  {
    id: '6',
    host: 'mina',
    title: '快速市場情報',
    content: '插播一則快訊：人行宣佈降準 0.25 個百分點，釋放流動性約 5000 億...',
    audioFile: '/dialogue/05_mina.wav',
    duration: 2.8,
    type: 'market',
    transcript: '人行降準利好股市...'
  },
  {
    id: '7',
    host: 'zicheng',
    title: '午後策略',
    content: '收到呢個消息，預計午後恒指會進一步上試 18500 點阻力位...',
    audioFile: '/dialogue/06_zicheng.wav',
    duration: 13.3,
    type: 'market',
    transcript: '午後展望：上試阻力位...'
  },
  {
    id: '8',
    host: 'mina',
    title: '結語 + 預告',
    content: '好啦，今日早節節目去到呢度。下午 5 點我哋再為大家帶來收市回顧，記得繼續收聽 Net 仔啦！',
    audioFile: '/dialogue/07_mina.wav',
    duration: 7.5,
    type: 'closing',
    transcript: '多謝收聽，下午見！'
  },
]

interface InteractiveRadioProps {
  userProfile?: any
}

export function InteractiveRadio({ userProfile }: InteractiveRadioProps) {
  const [currentSegmentIndex, setCurrentSegmentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [volume, setVolume] = useState(0.8)
  const [isMuted, setIsMuted] = useState(false)
  const [showInteraction, setShowInteraction] = useState(false)
  const [userMessage, setUserMessage] = useState('')
  const [messages, setMessages] = useState<Array<{
    id: string
    user: string
    message: string
    replied: boolean
  }>>([
    { id: '1', user: '陳先生', message: '而家追入騰訊 (0700) 合唔合適？目標價幾多？', replied: true },
    { id: '2', user: '投資新手', message: '想問下 MPF 應該點分配？28 歲全買股票基金得唔得？', replied: false },
    { id: '3', user: '退休人士', message: '有 500 萬現金，想收息為主，有咩推薦？', replied: false },
  ])
  const [activeTab, setActiveTab] = useState<'live' | 'chat' | 'questions'>('live')
  
  const audioRef = useRef<HTMLAudioElement>(null)
  const progressInterval = useRef<number>()

  const currentSegment = radioSegments[currentSegmentIndex]

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume
    }
  }, [volume, isMuted])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => {
      setCurrentTime(audio.currentTime)
      
      // 自動播放下一段
      if (audio.currentTime >= audio.duration - 0.5 && currentSegmentIndex < radioSegments.length - 1) {
        setTimeout(() => playNext(), 500)
      }
    }

    const handleEnded = () => {
      setIsPlaying(false)
    }

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [currentSegmentIndex])

  const togglePlay = () => {
    if (!audioRef.current) return
    
    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const playNext = () => {
    if (currentSegmentIndex < radioSegments.length - 1) {
      setCurrentSegmentIndex(currentSegmentIndex + 1)
      setCurrentTime(0)
      setIsPlaying(true)
      setTimeout(() => audioRef.current?.play(), 100)
    }
  }

  const playPrevious = () => {
    if (currentSegmentIndex > 0) {
      setCurrentSegmentIndex(currentSegmentIndex - 1)
      setCurrentTime(0)
      setIsPlaying(true)
      setTimeout(() => audioRef.current?.play(), 100)
    }
  }

  const selectSegment = (index: number) => {
    setCurrentSegmentIndex(index)
    setCurrentTime(0)
    setIsPlaying(true)
    setTimeout(() => audioRef.current?.play(), 100)
  }

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!audioRef.current) return
    
    const rect = audioRef.current.getBoundingClientRect()
    const percent = (e.clientX - rect.left) / rect.width
    audioRef.current.currentTime = percent * currentSegment.duration
  }

  const skip = (seconds: number) => {
    if (!audioRef.current) return
    audioRef.current.currentTime += seconds
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const sendMessage = () => {
    if (!userMessage.trim()) return
    
    setMessages([
      ...messages,
      { id: Date.now().toString(), user: '你', message: userMessage, replied: false }
    ])
    setUserMessage('')
    
    // 模擬 AI 回應
    setTimeout(() => {
      setMessages(prev => prev.map((msg, idx) => 
        idx === prev.length - 1 
          ? { ...msg, replied: true }
          : msg
      ))
    }, 2000)
  }

  const getHostColor = (host: string) => {
    return host === 'zicheng' ? 'text-blue-400 bg-blue-500/10 border-blue-500/30' : 'text-pink-400 bg-pink-500/10 border-pink-500/30'
  }

  const getHostAvatar = (host: string) => {
    return host === 'zicheng' ? '👨‍🎤' : '👩‍🎤'
  }

  return (
    <div className="space-y-6">
      {/* 隱藏的 audio 元素 */}
      <audio ref={audioRef} src={currentSegment.audioFile} preload="metadata" />

      {/* 電台主界面 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左側：播放器 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 當前播放卡片 */}
          <div className="glass-card rounded-2xl p-6 glow-border space-y-6">
            {/* LIVE 標誌 + 電台資訊 */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-500/20 border border-red-500/50 animate-pulse">
                  <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                  <span className="text-red-400 font-bold text-sm">LIVE</span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Radio className="w-4 h-4" />
                  <span className="text-sm">Net 仔財經台</span>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Disc className={cn("w-4 h-4", isPlaying && "animate-spin")} style={{ animationDuration: '3s' }} />
                <span>第 {currentSegmentIndex + 1} 節 / 共 {radioSegments.length} 節</span>
              </div>
            </div>

            {/* 主持人 + 專輯封面 */}
            <div className="flex items-start gap-6">
              {/* 動態專輯封面 */}
              <div className="relative w-32 h-32 flex-shrink-0">
                <div className={cn(
                  "absolute inset-0 rounded-full bg-gradient-to-br from-primary to-secondary opacity-30 blur-2xl",
                  isPlaying && "animate-pulse-glow"
                )} />
                <div className={cn(
                  "relative w-full h-full rounded-full bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center border-2 border-primary/50 text-5xl",
                  isPlaying ? "animate-spin" : "animate-pulse"
                )} style={{ animationDuration: '4s' }}>
                  {getHostAvatar(currentSegment.host)}
                </div>
                {/* 音波動畫 */}
                {isPlaying && (
                  <div className="absolute inset-0 m-auto w-20 h-20 rounded-full border-2 border-primary/30 flex items-center justify-center">
                    <div className="flex items-end gap-1 h-8">
                      {[...Array(5)].map((_, i) => (
                        <div
                          key={i}
                          className="w-1.5 bg-primary rounded-full animate-pulse"
                          style={{
                            height: `${Math.random() * 100}%`,
                            animationDelay: `${i * 100}ms`,
                            animationDuration: '0.5s'
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 節目資訊 */}
              <div className="flex-1 space-y-3">
                <div className={cn("inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium", getHostColor(currentSegment.host))}>
                  <Mic2 className="w-4 h-4" />
                  {currentSegment.host === 'zicheng' ? '子程' : '敏娜'} 主持
                </div>
                <h2 className="text-2xl font-bold">{currentSegment.title}</h2>
                <p className="text-muted-foreground">{currentSegment.content}</p>
                
                {/* 即時的文字轉播 */}
                <div className="flex items-start gap-2 text-sm italic text-muted-foreground bg-muted/30 rounded-lg p-3">
                  <MessageCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>"{currentSegment.transcript}"</span>
                </div>
              </div>
            </div>

            {/* 進度條 */}
            <div className="space-y-2">
              <div 
                className="h-3 bg-muted rounded-full cursor-pointer group relative overflow-hidden"
                onClick={handleProgressClick}
              >
                {/* 背景動畫 */}
                <div className="absolute inset-0 opacity-20">
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-pulse" style={{ width: '50%', left: `${(currentTime / currentSegment.duration) * 50}%` }} />
                </div>
                
                <div 
                  className="h-full bg-gradient-to-r from-primary to-secondary rounded-full relative transition-all"
                  style={{ width: `${(currentTime / currentSegment.duration) * 100}%` }}
                >
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-foreground border-2 border-primary shadow-lg opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
              <div className="flex justify-between text-xs text-muted-foreground font-mono">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(currentSegment.duration)}</span>
              </div>
            </div>

            {/* 控制按鈕 */}
            <div className="flex items-center justify-center gap-4">
              <button 
                onClick={playPrevious}
                disabled={currentSegmentIndex === 0}
                className="p-3 rounded-full hover:bg-primary/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <SkipBack className="w-6 h-6" />
              </button>
              
              <button 
                onClick={() => skip(-10)}
                className="p-2 rounded-full hover:bg-primary/20 transition-colors text-sm"
              >
                -10s
              </button>
              
              <button 
                onClick={togglePlay}
                className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center hover:scale-105 transition-transform shadow-glow"
              >
                {isPlaying ? (
                  <Pause className="w-10 h-10" />
                ) : (
                  <Play className="w-10 h-10 ml-1" />
                )}
              </button>
              
              <button 
                onClick={() => skip(10)}
                className="p-2 rounded-full hover:bg-primary/20 transition-colors text-sm"
              >
                +10s
              </button>
              
              <button 
                onClick={playNext}
                disabled={currentSegmentIndex === radioSegments.length - 1}
                className="p-3 rounded-full hover:bg-primary/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <SkipForward className="w-6 h-6" />
              </button>
            </div>

            {/* 額外功能 */}
            <div className="flex items-center justify-between pt-4 border-t border-border">
              {/* 音量控制 */}
              <div className="flex items-center gap-2">
                <button onClick={() => setIsMuted(!isMuted)}>
                  {isMuted || volume === 0 ? (
                    <VolumeX className="w-5 h-5 text-muted-foreground" />
                  ) : (
                    <Volume2 className="w-5 h-5 text-muted-foreground" />
                  )}
                </button>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={isMuted ? 0 : volume}
                  onChange={(e) => setVolume(parseFloat(e.target.value))}
                  className="w-24 accent-primary"
                />
              </div>

              {/* 互動按鈕 */}
              <div className="flex items-center gap-3">
                <button 
                  onClick={() => setShowInteraction(!showInteraction)}
                  className={cn(
                    "px-4 py-2 rounded-full flex items-center gap-2 transition-all",
                    showInteraction ? "bg-primary text-primary-foreground" : "hover:bg-primary/20"
                  )}
                >
                  <Phone className="w-4 h-4" />
                  <span className="text-sm font-medium">即時互動</span>
                </button>
                <button className="p-2 rounded-full hover:bg-primary/20 transition-colors">
                  <Heart className="w-5 h-5" />
                </button>
                <button className="p-2 rounded-full hover:bg-primary/20 transition-colors">
                  <Share2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          {/* 節目列表 */}
          <div className="glass-card rounded-xl p-4 space-y-3">
            <h3 className="font-semibold flex items-center gap-2">
              <Music className="w-5 h-5" />
              今日節目單
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {radioSegments.map((segment, idx) => (
                <button
                  key={segment.id}
                  onClick={() => selectSegment(idx)}
                  className={cn(
                    "w-full p-3 rounded-lg border text-left transition-all hover:border-primary hover:bg-primary/10 flex items-center gap-3",
                    currentSegmentIndex === idx && "border-primary bg-primary/10"
                  )}
                >
                  <div className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
                    getHostColor(segment.host)
                  )}>
                    {getHostAvatar(segment.host)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium truncate">{segment.title}</h4>
                    <p className="text-sm text-muted-foreground truncate">{segment.content}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-xs text-muted-foreground font-mono">
                      {formatTime(segment.duration)}
                    </div>
                    {currentSegmentIndex === idx && isPlaying && (
                      <div className="flex items-center gap-0.5 justify-end mt-1">
                        <div className="w-0.5 h-3 bg-primary animate-pulse" style={{ animationDelay: '0ms' }} />
                        <div className="w-0.5 h-4 bg-primary animate-pulse" style={{ animationDelay: '150ms' }} />
                        <div className="w-0.5 h-2 bg-primary animate-pulse" style={{ animationDelay: '300ms' }} />
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 右側：互動區 */}
        <div className="space-y-6">
          {/* 互動面板 */}
          <div className="glass-card rounded-xl overflow-hidden">
            {/* Tab 切換 */}
            <div className="flex border-b border-border">
              <button
                onClick={() => setActiveTab('live')}
                className={cn(
                  "flex-1 px-4 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2",
                  activeTab === 'live' ? "bg-primary/10 text-primary" : "hover:bg-muted/50"
                )}
              >
                <Sparkles className="w-4 h-4" />
                即時互動
              </button>
              <button
                onClick={() => setActiveTab('chat')}
                className={cn(
                  "flex-1 px-4 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2",
                  activeTab === 'chat' ? "bg-primary/10 text-primary" : "hover:bg-muted/50"
                )}
              >
                <MessageCircle className="w-4 h-4" />
                討論區 ({messages.length})
              </button>
              <button
                onClick={() => setActiveTab('questions')}
                className={cn(
                  "flex-1 px-4 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2",
                  activeTab === 'questions' ? "bg-primary/10 text-primary" : "hover:bg-muted/50"
                )}
              >
                <Phone className="w-4 h-4" />
                 unanswered ({messages.filter(m => !m.replied).length})
              </button>
            </div>

            {/* Live 互動 */}
            {activeTab === 'live' && (
              <div className="p-4 space-y-4 h-96 overflow-y-auto">
                <div className="text-center py-8 space-y-4">
                  <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center animate-pulse-glow">
                    <Phone className="w-10 h-10 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold">Call-in 熱線</h3>
                    <p className="text-sm text-muted-foreground">即刻打電話落嚟同主持人交流</p>
                  </div>
                  <button className="w-full py-3 rounded-xl bg-gradient-to-r from-primary to-secondary font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2">
                    <Phone className="w-5 h-5" />
                    立即 Call-in
                  </button>
                  <p className="text-xs text-muted-foreground">
                    * 模擬功能，實際應用需接入語音通話 API
                  </p>
                </div>

                {/* 正在等待 */}
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-muted-foreground">排隊中的聽眾</h4>
                  <div className="space-y-2">
                    {[1, 2, 3].map((num) => (
                      <div key={num} className="flex items-center gap-3 p-3 rounded-lg bg-muted/30">
                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm">
                          {num}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium">聽眾 {String.fromCharCode(64 + num)}</div>
                          <div className="text-xs text-muted-foreground">等候中...</div>
                        </div>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse" />
                          約 2 分鐘
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* 討論區 */}
            {activeTab === 'chat' && (
              <div className="p-4 h-96 flex flex-col">
                <div className="flex-1 overflow-y-auto space-y-3 mb-4">
                  {messages.map((msg) => (
                    <div key={msg.id} className="space-y-2">
                      <div className="flex items-start gap-2">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                          {msg.user[0]}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-sm">{msg.user}</span>
                            <span className="text-xs text-muted-foreground">剛剛</span>
                          </div>
                          <p className="text-sm mt-1">{msg.message}</p>
                          {msg.replied && (
                            <div className="mt-2 ml-4 p-2 rounded-lg bg-primary/10 border-l-2 border-primary">
                              <p className="text-sm text-muted-foreground">
                                🎙️ <strong>子程回應：</strong>多謝你嘅提問，就你嘅情況，我建議...
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* 輸入框 */}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={userMessage}
                    onChange={(e) => setUserMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="發送訊息畀主持人..."
                    className="flex-1 px-4 py-2 rounded-lg bg-muted border border-border focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <button
                    onClick={sendMessage}
                    className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}

            {/* unanswered 問題 */}
            {activeTab === 'questions' && (
              <div className="p-4 h-96 overflow-y-auto space-y-3">
                {messages.filter(m => !m.replied).map((msg) => (
                  <div key={msg.id} className="p-3 rounded-lg border border-border hover:border-primary transition-colors">
                    <div className="flex items-start gap-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-secondary to-primary flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                        {msg.user[0]}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-sm">{msg.user}</span>
                          <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400">待回答</span>
                        </div>
                        <p className="text-sm">{msg.message}</p>
                        <button className="mt-2 text-xs text-primary hover:underline flex items-center gap-1">
                          <Phone className="w-3 h-3" />
                          邀請 Call-in
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                {messages.filter(m => !m.replied).length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <CheckCircle2 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>所有問題已回答</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* 統計數據 */}
          <div className="glass-card rounded-xl p-4 space-y-3">
            <h3 className="font-semibold flex items-center gap-2">
              <Activity className="w-5 h-5" />
              即時統計
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">📻 在線收聽</span>
                <span className="font-bold text-primary">2,458</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">💬 今日留言</span>
                <span className="font-bold text-secondary">856</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">📞 Call-in 排隊</span>
                <span className="font-bold text-accent">12</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">❤️ 獲得 Like</span>
                <span className="font-bold text-red-400">3,247</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function CheckCircle2(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  )
}

function Activity(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  )
}
