import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { 
  Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, 
  Mic2, Radio, Disc, Music, Sparkles, Activity
} from 'lucide-react'

interface SmartSegment {
  type: string
  title: string
  audio_url: string
  duration_estimate: number
  text: string
  host?: 'zicheng' | 'mina' | 'leungzai'
}

interface SmartRadioProps {
  topic?: string
}

export function SmartRadioPlayer({ topic = "AI趨勢" }: SmartRadioProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [segments, setSegments] = useState<SmartSegment[]>([])
  const [currentSegmentIndex, setCurrentSegmentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [volume, setVolume] = useState(0.8)
  const [isMuted, setIsMuted] = useState(false)
  
  const audioRef = useRef<HTMLAudioElement>(null)

  const currentSegment = segments[currentSegmentIndex]

  // 初始化時自動生成節目
  useEffect(() => {
    generateProgram()
  }, [topic])

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
      if (audio.currentTime >= audio.duration - 0.5 && currentSegmentIndex < segments.length - 1) {
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
  }, [currentSegmentIndex, segments])

  const generateProgram = async () => {
    setIsGenerating(true)
    setSegments([])
    setCurrentSegmentIndex(0)
    setCurrentTime(0)
    setIsPlaying(false)
    
    const backendUrl = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000'
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30秒超時

      const response = await fetch(`${backendUrl}/api/v1/news-podcast/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          focus_topic: topic,
          categories: ["rumour", "tech", "instant_news"],
          limit: 10
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        console.warn('API response not ok:', response.status, response.statusText)
        throw new Error(`生成失敗 (${response.status})`)
      }
      
      const data = await response.json()
      
      if (data.success && data.podcast) {
        // 為每個 segment 分配主持人
        const enhancedSegments = data.podcast.segments.map((seg: SmartSegment, idx: number) => ({
          ...seg,
          host: idx % 2 === 0 ? 'zicheng' : 'mina' as 'zicheng' | 'mina'
        }))
        
        setSegments(enhancedSegments)
      }
    } catch (error) {
      console.error('Failed to generate program:', error)
      // 使用示例數據
      setTimeout(() => {
        setSegments([
          {
            type: "intro",
            title: "開場問候",
            audio_url: "",
            duration_estimate: 30,
            text: `哈囉各位 Net 仔家族嘅朋友，早晨！我係子程。今日我哋會重點分析${topic}，帶畀大家最新嘅市場動態同投資機會。`,
            host: 'zicheng'
          },
          {
            type: "news",
            title: "重點新聞速遞",
            audio_url: "",
            duration_estimate: 120,
            text: `等我睇下今日有咩重要新聞... 首先係${topic}相關嘅消息，市場反應熱烈...`,
            host: 'mina'
          },
          {
            type: "analysis",
            title: "AI 深度分析",
            audio_url: "",
            duration_estimate: 180,
            text: `講返${topic}呢個話題，從技術面嚟睇，而家處於上升趨勢。基本面方面，行業增長強勁...`,
            host: 'zicheng'
          },
          {
            type: "advice",
            title: "投資建議",
            audio_url: "",
            duration_estimate: 60,
            text: `操作上，我建議可以分段建倉，唔好一次過追入。止蝕位設喺近期低位，目標價睇高一线...`,
            host: 'mina'
          },
          {
            type: "closing",
            title: "節目完結",
            audio_url: "",
            duration_estimate: 30,
            text: `好啦，今日嘅${topic}分析就到呢度。多謝收聽 Net 仔財經台，聽日見！`,
            host: 'zicheng'
          }
        ])
      }, 1500)
    } finally {
      setIsGenerating(false)
    }
  }

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
    if (currentSegmentIndex < segments.length - 1) {
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

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getHostColor = (host?: string) => {
    if (host === 'zicheng') return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
    if (host === 'mina') return 'text-pink-400 bg-pink-500/10 border-pink-500/30'
    return 'text-primary bg-primary/10 border-primary/30'
  }

  const getHostAvatar = (host?: string) => {
    if (host === 'zicheng') return '👨‍🎤'
    if (host === 'mina') return '👩‍🎤'
    return '🤖'
  }

  return (
    <div className="space-y-6">
      {/* 隱藏的 audio 元素 */}
      {currentSegment?.audio_url && (
        <audio 
          ref={audioRef} 
          src={`http://localhost:8000${currentSegment.audio_url}`}
          preload="metadata" 
        />
      )}

      {/* 載入狀態 */}
      {isGenerating && segments.length === 0 && (
        <div className="glass-card rounded-xl p-8 text-center space-y-4">
          <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-r from-primary to-secondary flex items-center justify-center animate-pulse-glow">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold mb-2">AI 正在創作你的專屬節目</h3>
            <p className="text-muted-foreground">
              抓取新聞 → LLM 分析 → 生成腳本 → TTS 合成語音
            </p>
          </div>
          <div className="max-w-md mx-auto">
            <div className="h-2 bg-primary/20 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-primary to-secondary animate-progress" style={{ width: '70%' }} />
            </div>
          </div>
        </div>
      )}

      {/* 播放器界面 */}
      {segments.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左側：播放器 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 當前播放卡片 */}
            <div className="glass-card rounded-2xl p-6 glow-border space-y-6">
              {/* LIVE 標誌 */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-500/20 border border-red-500/50 animate-pulse">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                    <span className="text-red-400 font-bold text-sm">LIVE</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Radio className="w-4 h-4" />
                    <span className="text-sm">Net 仔財經台 - {topic}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Disc className={cn("w-4 h-4", isPlaying && "animate-spin")} style={{ animationDuration: '3s' }} />
                  <span>第 {currentSegmentIndex + 1} 節 / 共 {segments.length} 節</span>
                </div>
              </div>

              {/* 主持人 + 封面 */}
              <div className="flex items-start gap-6">
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
                </div>

                <div className="flex-1 space-y-3">
                  <div className={cn("inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium", getHostColor(currentSegment.host))}>
                    <Mic2 className="w-4 h-4" />
                    {currentSegment.host === 'zicheng' ? '子程' : currentSegment.host === 'mina' ? '敏娜' : '叻仔'}
                  </div>
                  <h2 className="text-2xl font-bold">{currentSegment.title}</h2>
                  <p className="text-muted-foreground italic">"{currentSegment.text}"</p>
                </div>
              </div>

              {/* 進度條 */}
              <div className="space-y-2">
                <div className="h-3 bg-muted rounded-full cursor-pointer overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-primary to-secondary rounded-full transition-all"
                    style={{ width: `${(currentTime / currentSegment.duration_estimate) * 100}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-muted-foreground font-mono">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(currentSegment.duration_estimate)}</span>
                </div>
              </div>

              {/* 控制按鈕 */}
              <div className="flex items-center justify-center gap-4">
                <button onClick={playPrevious} disabled={currentSegmentIndex === 0} className="p-3 rounded-full hover:bg-primary/20 transition-colors disabled:opacity-30">
                  <SkipBack className="w-6 h-6" />
                </button>
                <button onClick={() => {}} className="p-2 rounded-full hover:bg-primary/20 transition-colors text-sm">-10s</button>
                <button onClick={togglePlay} className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center hover:scale-105 transition-transform shadow-glow">
                  {isPlaying ? <Pause className="w-10 h-10" /> : <Play className="w-10 h-10 ml-1" />}
                </button>
                <button onClick={() => {}} className="p-2 rounded-full hover:bg-primary/20 transition-colors text-sm">+10s</button>
                <button onClick={playNext} disabled={currentSegmentIndex === segments.length - 1} className="p-3 rounded-full hover:bg-primary/20 transition-colors disabled:opacity-30">
                  <SkipForward className="w-6 h-6" />
                </button>
              </div>

              {/* 音量控制 */}
              <div className="flex items-center gap-2 pt-4 border-t border-border">
                <button onClick={() => setIsMuted(!isMuted)}>
                  {isMuted ? <VolumeX className="w-5 h-5 text-muted-foreground" /> : <Volume2 className="w-5 h-5 text-muted-foreground" />}
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
            </div>

            {/* 節目列表 */}
            <div className="glass-card rounded-xl p-4 space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <Music className="w-5 h-5" />
                今日節目單
              </h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {segments.map((segment, idx) => (
                  <button
                    key={idx}
                    onClick={() => selectSegment(idx)}
                    className={cn(
                      "w-full p-3 rounded-lg border text-left transition-all hover:border-primary hover:bg-primary/10 flex items-center gap-3",
                      currentSegmentIndex === idx && "border-primary bg-primary/10"
                    )}
                  >
                    <div className={cn("w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0", getHostColor(segment.host))}>
                      {getHostAvatar(segment.host)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium truncate">{segment.title}</h4>
                      <p className="text-sm text-muted-foreground truncate">{segment.type}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-muted-foreground font-mono">
                        {formatTime(segment.duration_estimate)}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 右側：統計 */}
          <div className="space-y-6">
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
                  <span className="text-sm text-muted-foreground">❤️ 獲得 Like</span>
                  <span className="font-bold text-red-400">3,247</span>
                </div>
              </div>
            </div>

            {/* 重新生成按鈕 */}
            <button
              onClick={generateProgram}
              className="w-full py-4 rounded-xl bg-gradient-to-r from-primary to-secondary font-bold text-lg hover:opacity-90 transition-opacity flex items-center justify-center gap-3"
            >
              <Sparkles className="w-6 h-6" />
              重新生成節目
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
