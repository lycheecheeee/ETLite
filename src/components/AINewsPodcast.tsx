import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { Play, Pause, Download, Share2, Sparkles, Radio, Clock, Calendar, TrendingUp } from 'lucide-react'

interface NewsSegment {
  type: string
  title: string
  audio_url: string
  duration_estimate: number
}

interface PodcastData {
  title: string
  description: string
  focus_topic: string
  created_at: string
  total_duration: number
  segments: NewsSegment[]
  full_script: string
  news_count: number
  news_sources: string[]
}

const TOPIC_OPTIONS = [
  "AI趨勢",
  "科技股",
  "金融政策",
  "地緣政治",
  "加密貨幣",
  "房地產",
  "能源轉型",
  "消費趨勢"
]

const CATEGORY_OPTIONS = [
  { id: "rumour", label: "市場傳聞" },
  { id: "instant_news", label: "即時新聞" },
  { id: "tech", label: "科技" },
  { id: "stock", label: "股票" }
]

export function AINewsPodcast() {
  const [selectedTopic, setSelectedTopic] = useState("AI趨勢")
  const [selectedCategories, setSelectedCategories] = useState<string[]>(["rumour", "tech"])
  const [isGenerating, setIsGenerating] = useState(false)
  const [podcast, setPodcast] = useState<PodcastData | null>(null)
  const [currentSegment, setCurrentSegment] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    if (audioRef.current && podcast?.segments[currentSegment]) {
      if (isPlaying) {
        audioRef.current.play().catch(e => console.error('Playback error:', e))
      } else {
        audioRef.current.pause()
      }
    }
  }, [isPlaying, currentSegment])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => {
      // Progress tracking handled by timeupdate event
    }
    const handleEnded = () => {
      setIsPlaying(false)
      if (currentSegment < (podcast?.segments.length || 0) - 1) {
        setCurrentSegment(prev => prev + 1)
        setIsPlaying(true)
      }
    }

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('ended', handleEnded)
    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [currentSegment, podcast])

  const toggleCategory = (categoryId: string) => {
    setSelectedCategories(prev => 
      prev.includes(categoryId)
        ? prev.filter(c => c !== categoryId)
        : [...prev, categoryId]
    )
  }

  const generatePodcast = async () => {
    setIsGenerating(true)
    setPodcast(null)
    
    const backendUrl = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000'
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30秒超時

      const response = await fetch(`${backendUrl}/api/v1/news-podcast/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          focus_topic: selectedTopic,
          categories: selectedCategories,
          limit: 15
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)

      if (!response.ok) {
        console.warn('API response not ok:', response.status, response.statusText)
        throw new Error(`生成失敗 (${response.status})`)
      }
      
      const data = await response.json()
      setPodcast(data.podcast)
    } catch (error) {
      if (error.name === 'AbortError') {
        console.warn('Podcast generation timeout')
      } else {
        console.error('Failed to generate podcast:', error)
      }
      
      // Mock data for demo
      setTimeout(() => {
        setPodcast({
          title: `${selectedTopic}深度分析`,
          description: `最新${selectedTopic}相關新聞同市場動態分析`,
          focus_topic: selectedTopic,
          created_at: new Date().toISOString(),
          total_duration: 420,
          segments: [
            { type: "intro", title: "節目開場", audio_url: "", duration_estimate: 30 },
            { type: "news_roundup", title: "新聞速遞", audio_url: "", duration_estimate: 120 },
            { type: "ai_analysis", title: "AI 深度分析", audio_url: "", duration_estimate: 180 },
            { type: "investment_advice", title: "投資建議", audio_url: "", duration_estimate: 60 },
            { type: "closing", title: "節目完結", audio_url: "", duration_estimate: 30 }
          ],
          full_script: "這是示例腳本...",
          news_count: 12,
          news_sources: ["經濟通", "明報", "信報"]
        })
      }, 2000)
    } finally {
      setIsGenerating(false)
    }
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-6">
      {/* 控制面板 */}
      <div className="glass-card rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-2 mb-4">
          <Radio className="w-6 h-6 text-primary" />
          <h3 className="text-xl font-bold">自定義你的 AI 新聞節目</h3>
        </div>

        {/* 主題選擇 */}
        <div>
          <label className="block text-sm font-medium mb-2">重點話題</label>
          <div className="flex flex-wrap gap-2">
            {TOPIC_OPTIONS.map(topic => (
              <button
                key={topic}
                onClick={() => setSelectedTopic(topic)}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                  selectedTopic === topic
                    ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
                    : "bg-primary/10 hover:bg-primary/20"
                )}
              >
                {topic}
              </button>
            ))}
          </div>
        </div>

        {/* 分類選擇 */}
        <div>
          <label className="block text-sm font-medium mb-2">新聞來源</label>
          <div className="flex flex-wrap gap-2">
            {CATEGORY_OPTIONS.map(cat => (
              <button
                key={cat.id}
                onClick={() => toggleCategory(cat.id)}
                className={cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                  selectedCategories.includes(cat.id)
                    ? "bg-secondary text-secondary-foreground shadow-lg shadow-secondary/25"
                    : "bg-secondary/10 hover:bg-secondary/20"
                )}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* 生成按鈕 */}
        <button
          onClick={generatePodcast}
          disabled={isGenerating || selectedCategories.length === 0}
          className={cn(
            "w-full py-4 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-3",
            isGenerating
              ? "bg-gray-500 cursor-not-allowed"
              : "bg-gradient-to-r from-primary to-secondary hover:opacity-90 shadow-xl"
          )}
        >
          {isGenerating ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              AI 正在分析新聞並生成節目...
            </>
          ) : (
            <>
              <Sparkles className="w-6 h-6" />
              生成 AI 新聞播客
            </>
          )}
        </button>
      </div>

      {/* 載入狀態 */}
      {isGenerating && (
        <div className="glass-card rounded-xl p-8 text-center space-y-4">
          <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-r from-primary to-secondary flex items-center justify-center animate-pulse-glow">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold mb-2">AI 正在創作你的專屬節目</h3>
            <p className="text-muted-foreground">
              正在抓取最新新聞 → 分析趨勢 → 生成腳本 → 合成語音
            </p>
          </div>
        </div>
      )}

      {/* 隱藏的 audio 播放器 */}
      {podcast && podcast.segments[currentSegment] && (
        <audio
          ref={audioRef}
          src={`http://localhost:8000${podcast.segments[currentSegment].audio_url}`}
          preload="metadata"
        />
      )}

      {/* 節目詳情 */}
      {podcast && !isGenerating && (
        <div className="space-y-6 animate-fade-in">
          {/* 節目頭部 */}
          <div className="glass-card rounded-xl p-6 space-y-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-3 py-1 rounded-full bg-primary/20 text-primary text-sm font-medium">
                    {podcast.focus_topic}
                  </span>
                  <span className="px-3 py-1 rounded-full bg-secondary/20 text-secondary text-sm font-medium">
                    {podcast.news_count} 則新聞
                  </span>
                </div>
                <h2 className="text-2xl font-bold mb-2">{podcast.title}</h2>
                <p className="text-muted-foreground">{podcast.description}</p>
              </div>
              <div className="flex gap-2">
                <button className="p-3 rounded-lg hover:bg-primary/10 transition-colors">
                  <Download className="w-5 h-5" />
                </button>
                <button className="p-3 rounded-lg hover:bg-primary/10 transition-colors">
                  <Share2 className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                {formatDuration(podcast.total_duration)}
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                {new Date(podcast.created_at).toLocaleString('zh-HK')}
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                來源：{podcast.news_sources.join(', ')}
              </div>
            </div>
          </div>

          {/* 分段播放器 */}
          <div className="glass-card rounded-xl p-6 space-y-4">
            <h3 className="text-lg font-bold">節目分段</h3>
            <div className="space-y-3">
              {podcast.segments.map((segment, idx) => (
                <div
                  key={idx}
                  className={cn(
                    "p-4 rounded-lg border transition-all cursor-pointer",
                    currentSegment === idx
                      ? "bg-primary/10 border-primary"
                      : "border-border hover:bg-primary/5"
                  )}
                  onClick={() => {
                    setCurrentSegment(idx)
                    setIsPlaying(true)
                    if (audioRef.current) {
                      audioRef.current.currentTime = 0
                    }
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      <div className={cn(
                        "w-10 h-10 rounded-full flex items-center justify-center",
                        currentSegment === idx
                          ? "bg-primary text-primary-foreground"
                          : "bg-primary/20"
                      )}>
                        {currentSegment === idx && isPlaying ? (
                          <Pause className="w-5 h-5" />
                        ) : (
                          <Play className="w-5 h-5" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium">{segment.title}</p>
                        <p className="text-sm text-muted-foreground capitalize">
                          {segment.type.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-sm text-muted-foreground">
                        {formatDuration(segment.duration_estimate)}
                      </span>
                      {currentSegment === idx && isPlaying && (
                        <div className="flex items-end gap-0.5 justify-end mt-1 h-4">
                          {[...Array(3)].map((_, i) => (
                            <div
                              key={i}
                              className="w-1 bg-primary rounded-full animate-pulse"
                              style={{
                                height: `${Math.random() * 100}%`,
                                animationDelay: `${i * 150}ms`
                              }}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 完整腳本 */}
          <div className="glass-card rounded-xl p-6 space-y-4">
            <h3 className="text-lg font-bold">節目腳本</h3>
            <div className="prose prose-sm max-w-none bg-black/20 rounded-lg p-4 max-h-96 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-sm font-mono">
                {podcast.full_script}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
