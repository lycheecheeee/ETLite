import { useState } from 'react'
import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus, Building2, Globe2, Activity, FileText, MessageCircle } from 'lucide-react'

interface ContentAtom {
  id: string
  type: 'market_index' | 'stock' | 'macro' | 'company' | 'sentiment' | 'international' | 'sector'
  title: string
  content: string
  data?: any
  timestamp: string
  sentiment?: 'positive' | 'negative' | 'neutral'
}

const mockAtoms: ContentAtom[] = [
  {
    id: '1',
    type: 'market_index',
    title: '恒生指數',
    content: '恒指現報 18,256.45 點，升 256.78 點 (+1.43%)',
    data: { value: 18256.45, change: 256.78, changePercent: 1.43 },
    timestamp: '16:00',
    sentiment: 'positive',
  },
  {
    id: '2',
    type: 'stock',
    title: '騰訊控股 (0700)',
    content: '騰訊升 3.2% 至 368.40 元，成交額 15.6 億',
    data: { price: 368.40, change: 3.2, volume: '15.6 億' },
    timestamp: '16:00',
    sentiment: 'positive',
  },
  {
    id: '3',
    type: 'stock',
    title: '美團 -W(3690)',
    content: '美團升 5.1% 至 128.60 元，創近一個月新高',
    data: { price: 128.60, change: 5.1, volume: '8.2 億' },
    timestamp: '16:00',
    sentiment: 'positive',
  },
  {
    id: '4',
    type: 'macro',
    title: '中國 PMI 數據',
    content: '1 月製造業 PMI 50.8，連續 4 個月處於擴張區間',
    data: { value: 50.8, previous: 50.5 },
    timestamp: '09:30',
    sentiment: 'positive',
  },
  {
    id: '5',
    type: 'company',
    title: '小米業績預告',
    content: '小米預期全年業績增長 15-20%，電動車業務貢獻增加',
    data: { growth: '15-20%' },
    timestamp: '14:30',
    sentiment: 'positive',
  },
  {
    id: '6',
    type: 'international',
    title: '美股隔夜走勢',
    content: '道指升 0.8%，納指升 1.2%，標普升 1.0%',
    data: { dow: 0.8, nasdaq: 1.2, sp: 1.0 },
    timestamp: '昨日',
    sentiment: 'positive',
  },
  {
    id: '7',
    type: 'sentiment',
    title: '市場情緒指標',
    content: '恐懼貪婪指數：65 (貪婪)',
    data: { value: 65, level: '貪婪' },
    timestamp: '即時',
    sentiment: 'positive',
  },
  {
    id: '8',
    type: 'sector',
    title: '科技板塊',
    content: '科技股今日領漲，板塊指數升 2.8%',
    data: { change: 2.8 },
    timestamp: '16:00',
    sentiment: 'positive',
  },
]

interface ContentAtomsProps {
  mode?: 'traditional' | 'ai' | 'gamma'
}

export function ContentAtoms({ mode = 'ai' }: ContentAtomsProps) {
  const [selectedAtom, setSelectedAtom] = useState<string | null>(null)
  const atoms = mockAtoms

  const getAtomIcon = (type: string) => {
    switch (type) {
      case 'market_index': return <Activity className="w-4 h-4" />
      case 'stock': return <Building2 className="w-4 h-4" />
      case 'macro': return <Globe2 className="w-4 h-4" />
      case 'company': return <FileText className="w-4 h-4" />
      case 'sentiment': return <MessageCircle className="w-4 h-4" />
      case 'international': return <Globe2 className="w-4 h-4" />
      case 'sector': return <TrendingUp className="w-4 h-4" />
      default: return <Activity className="w-4 h-4" />
    }
  }

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-500 bg-green-500/10 border-green-500/30'
      case 'negative': return 'text-red-500 bg-red-500/10 border-red-500/30'
      case 'neutral': return 'text-gray-500 bg-gray-500/10 border-gray-500/30'
      default: return 'text-muted-foreground bg-muted/50 border-border'
    }
  }

  const getChangeIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="w-3 h-3 text-green-500" />
    if (change < 0) return <TrendingDown className="w-3 h-3 text-red-500" />
    return <Minus className="w-3 h-3 text-gray-500" />
  }

  // Gamma 模式：可拖拽重組
  if (mode === 'gamma') {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Gamma 模式 - 自由組合</h3>
          <p className="text-sm text-muted-foreground">拖曳原子重新排列你嘅資訊流</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {atoms.map((atom) => (
            <div
              key={atom.id}
              draggable
              className={cn(
                "glass-card rounded-xl p-4 cursor-move transition-all hover:scale-105 hover:border-primary",
                selectedAtom === atom.id && "border-primary ring-2 ring-primary/50"
              )}
              onClick={() => setSelectedAtom(atom.id)}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={cn("p-1.5 rounded-lg", getSentimentColor(atom.sentiment))}>
                    {getAtomIcon(atom.type)}
                  </div>
                  <span className="text-xs text-muted-foreground">{atom.timestamp}</span>
                </div>
                <div className="text-xs px-2 py-1 rounded-full bg-primary/20 text-primary">
                  {atom.type.replace('_', ' ').toUpperCase()}
                </div>
              </div>
              
              <h4 className="font-medium mb-1">{atom.title}</h4>
              <p className="text-sm text-muted-foreground">{atom.content}</p>
              
              {atom.data && (
                <div className="mt-3 pt-3 border-t border-border flex items-center gap-2">
                  {atom.data.change !== undefined && (
                    <>
                      {getChangeIcon(atom.data.change)}
                      <span className={cn(
                        "text-sm font-medium",
                        atom.data.change > 0 ? "text-green-500" : 
                        atom.data.change < 0 ? "text-red-500" : "text-gray-500"
                      )}>
                        {atom.data.change > 0 ? '+' : ''}{atom.data.change}%
                      </span>
                    </>
                  )}
                  {atom.data.value && (
                    <span className="text-sm font-medium">{atom.data.value.toLocaleString()}</span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  // AI 推薦模式：智能排序 + 視覺化
  if (mode === 'ai') {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">AI 推薦軌道</h3>
          <p className="text-sm text-muted-foreground">根據你的標籤自動排列</p>
        </div>
        
        <div className="relative min-h-[400px]">
          {/* 引力場背景 */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-primary/10 rounded-full blur-3xl animate-pulse" />
            <div className="absolute bottom-1/4 right-1/4 w-40 h-40 bg-secondary/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
          </div>

          {/* 星球狀原子分佈 */}
          <div className="relative grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {atoms.map((atom, idx) => {
              const size = idx === 0 ? 'large' : idx < 3 ? 'medium' : 'small'
              return (
                <div
                  key={atom.id}
                  className={cn(
                    "glass-card rounded-xl p-4 transition-all hover:scale-105 hover:border-primary hover:shadow-glow",
                    size === 'large' && "md:col-span-2 md:row-span-2 border-primary/50",
                    size === 'medium' && "border-secondary/30"
                  )}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className={cn("p-2 rounded-lg", getSentimentColor(atom.sentiment))}>
                        {getAtomIcon(atom.type)}
                      </div>
                      <span className="text-xs text-muted-foreground">{atom.timestamp}</span>
                    </div>
                    <div className="text-xs px-2 py-1 rounded-full bg-primary/20 text-primary">
                      {atom.type.replace('_', ' ').toUpperCase()}
                    </div>
                  </div>
                  
                  <h4 className={cn(
                    "font-medium mb-2",
                    size === 'large' && "text-xl"
                  )}>{atom.title}</h4>
                  
                  <p className={cn(
                    "text-muted-foreground",
                    size === 'large' && "text-base"
                  )}>{atom.content}</p>
                  
                  {atom.data && (
                    <div className="mt-4 pt-4 border-t border-border">
                      <div className="flex items-center gap-3 flex-wrap">
                        {atom.data.change !== undefined && (
                          <div className="flex items-center gap-1">
                            {getChangeIcon(atom.data.change)}
                            <span className={cn(
                              "font-medium",
                              atom.data.change > 0 ? "text-green-500" : 
                              atom.data.change < 0 ? "text-red-500" : "text-gray-500"
                            )}>
                              {atom.data.change > 0 ? '+' : ''}{atom.data.change}%
                            </span>
                          </div>
                        )}
                        {atom.data.value && (
                          <span className="font-medium">{atom.data.value.toLocaleString()}</span>
                        )}
                        {atom.data.volume && (
                          <span className="text-sm text-muted-foreground">Vol: {atom.data.volume}</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    )
  }

  // 傳統模式：線性列表
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">傳統軌道</h3>
        <p className="text-sm text-muted-foreground">時間順序排列</p>
      </div>
      
      <div className="space-y-3">
        {atoms.map((atom) => (
          <div
            key={atom.id}
            className="glass-card rounded-xl p-4 transition-all hover:border-primary"
          >
            <div className="flex items-start gap-3">
              <div className={cn("p-2 rounded-lg mt-1", getSentimentColor(atom.sentiment))}>
                {getAtomIcon(atom.type)}
              </div>
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{atom.title}</h4>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">{atom.timestamp}</span>
                    <div className="text-xs px-2 py-1 rounded-full bg-primary/20 text-primary">
                      {atom.type.replace('_', ' ').toUpperCase()}
                    </div>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">{atom.content}</p>
                {atom.data && (
                  <div className="flex items-center gap-3 flex-wrap">
                    {atom.data.change !== undefined && (
                      <div className="flex items-center gap-1">
                        {getChangeIcon(atom.data.change)}
                        <span className={cn(
                          "text-sm font-medium",
                          atom.data.change > 0 ? "text-green-500" : 
                          atom.data.change < 0 ? "text-red-500" : "text-gray-500"
                        )}>
                          {atom.data.change > 0 ? '+' : ''}{atom.data.change}%
                        </span>
                      </div>
                    )}
                    {atom.data.value && (
                      <span className="text-sm font-medium">{atom.data.value.toLocaleString()}</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
