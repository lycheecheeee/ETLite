import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Download, Share2, Heart } from 'lucide-react'

interface PodcastEpisode {
  id: string
  title: string
  description: string
  duration: number
  audioUrl: string
  publishTime: string
  type: 'morning' | 'market_close' | 'before_sleep' | 'breaking'
}

const mockEpisodes: PodcastEpisode[] = [
  {
    id: '1',
    title: '晨早開市前瞻 - 恒指挑戰 18000 點',
    description: '分析隔夜美股走勢，今日港股關鍵支持位同阻力位，同埋介紹幾隻強勢股',
    duration: 420,
    audioUrl: '/dialogue/00_zicheng.wav',
    publishTime: '今日 08:30',
    type: 'morning',
  },
  {
    id: '2',
    title: '收市回顧 - 科技股領漲',
    description: '恒指全日升 256 點，騰訊升 3%，美團升 5%，分析明日走勢',
    duration: 360,
    audioUrl: '/dialogue/01_mina.wav',
    publishTime: '今日 17:00',
    type: 'market_close',
  },
  {
    id: '3',
    title: '睡前必睇 - 明日策略',
    description: '總結今日市場亮點，預聽明日重要數據同業績公佈',
    duration: 300,
    audioUrl: '/dialogue/02_zicheng.wav',
    publishTime: '今日 21:00',
    type: 'before_sleep',
  },
]

interface PodcastPlayerProps {
  userProfile?: any
}

export function PodcastPlayer({ userProfile }: PodcastPlayerProps) {
  const [currentEpisode, setCurrentEpisode] = useState<PodcastEpisode>(mockEpisodes[0])
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [volume, setVolume] = useState(0.8)
  const [isMuted, setIsMuted] = useState(false)
  const [isLiked, setIsLiked] = useState(false)
  
  const audioRef = useRef<HTMLAudioElement>(null)
  const progressRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume
    }
  }, [volume, isMuted])

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const handleEnded = () => setIsPlaying(false)

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [])

  const togglePlay = () => {
    if (!audioRef.current) return
    
    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressRef.current || !audioRef.current) return
    
    const rect = progressRef.current.getBoundingClientRect()
    const percent = (e.clientX - rect.left) / rect.width
    audioRef.current.currentTime = percent * currentEpisode.duration
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

  const getEpisodeTypeLabel = (type: string) => {
    switch (type) {
      case 'morning': return '🌅 晨早開市'
      case 'market_close': return '📊 收市回顧'
      case 'before_sleep': return '🌙 睡前必睇'
      case 'breaking': return '⚡ 突發快訊'
    }
  }

  return (
    <div className="space-y-6">
      {/* 隱藏的 audio 元素 */}
      <audio ref={audioRef} src={currentEpisode.audioUrl} preload="metadata" />

      {/* 當前播放 */}
      <div className="glass-card rounded-2xl p-6 glow-border space-y-6">
        {/* 專輯封面動畫 */}
        <div className="relative aspect-square max-w-xs mx-auto">
          <div className={cn(
            "absolute inset-0 rounded-full bg-gradient-to-br from-primary to-secondary opacity-20 blur-2xl",
            isPlaying && "animate-pulse-glow"
          )} />
          <div className={cn(
            "relative w-full h-full rounded-full bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center border-2 border-primary/50",
            isPlaying && "animate-spin",
            !isPlaying && "animate-pulse"
          )} style={{ animationDuration: '3s' }}>
            <div className="text-6xl">🎙️</div>
          </div>
          {/* 中心黑洞 */}
          <div className="absolute inset-0 m-auto w-16 h-16 rounded-full bg-background border-2 border-primary/30 flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-primary animate-pulse" />
          </div>
        </div>

        {/* 節目資訊 */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/20 text-primary text-sm">
            {getEpisodeTypeLabel(currentEpisode.type)}
          </div>
          <h2 className="text-xl font-bold">{currentEpisode.title}</h2>
          <p className="text-muted-foreground text-sm">{currentEpisode.description}</p>
          <p className="text-xs text-muted-foreground">{currentEpisode.publishTime}</p>
        </div>

        {/* 進度條 */}
        <div className="space-y-2">
          <div 
            ref={progressRef}
            className="h-2 bg-muted rounded-full cursor-pointer group"
            onClick={handleProgressClick}
          >
            <div 
              className="h-full bg-gradient-to-r from-primary to-secondary rounded-full relative transition-all"
              style={{ width: `${(currentTime / currentEpisode.duration) * 100}%` }}
            >
              <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-foreground border-2 border-primary opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(currentEpisode.duration)}</span>
          </div>
        </div>

        {/* 控制按鈕 */}
        <div className="flex items-center justify-center gap-4">
          <button 
            onClick={() => skip(-10)}
            className="p-2 rounded-full hover:bg-primary/20 transition-colors"
          >
            <SkipBack className="w-5 h-5" />
          </button>
          
          <button 
            onClick={togglePlay}
            className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center hover:scale-105 transition-transform shadow-glow"
          >
            {isPlaying ? (
              <Pause className="w-8 h-8" />
            ) : (
              <Play className="w-8 h-8 ml-1" />
            )}
          </button>
          
          <button 
            onClick={() => skip(10)}
            className="p-2 rounded-full hover:bg-primary/20 transition-colors"
          >
            <SkipForward className="w-5 h-5" />
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
              className="w-20 accent-primary"
            />
          </div>

          {/* 收藏、下載、分享 */}
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setIsLiked(!isLiked)}
              className={cn(
                "p-2 rounded-full hover:bg-primary/20 transition-colors",
                isLiked && "text-red-500"
              )}
            >
              <Heart className={cn("w-5 h-5", isLiked && "fill-current")} />
            </button>
            <button className="p-2 rounded-full hover:bg-primary/20 transition-colors">
              <Download className="w-5 h-5" />
            </button>
            <button className="p-2 rounded-full hover:bg-primary/20 transition-colors">
              <Share2 className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* 節目列表 */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold">今日節目</h3>
        {mockEpisodes.map((episode) => (
          <button
            key={episode.id}
            onClick={() => {
              setCurrentEpisode(episode)
              setIsPlaying(false)
              setCurrentTime(0)
            }}
            className={cn(
              "w-full p-4 rounded-xl border text-left transition-all hover:border-primary hover:bg-primary/10",
              currentEpisode.id === episode.id && "border-primary bg-primary/10"
            )}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">
                    {getEpisodeTypeLabel(episode.type)}
                  </span>
                </div>
                <h4 className="font-medium">{episode.title}</h4>
                <p className="text-sm text-muted-foreground line-clamp-1">{episode.description}</p>
              </div>
              <div className="text-right space-y-1">
                <div className="text-xs text-muted-foreground">
                  {formatTime(episode.duration)}
                </div>
                {currentEpisode.id === episode.id && isPlaying && (
                  <div className="flex items-center gap-1 text-primary">
                    <div className="w-1 h-3 bg-primary animate-pulse" style={{ animationDelay: '0ms' }} />
                    <div className="w-1 h-4 bg-primary animate-pulse" style={{ animationDelay: '150ms' }} />
                    <div className="w-1 h-2 bg-primary animate-pulse" style={{ animationDelay: '300ms' }} />
                  </div>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
