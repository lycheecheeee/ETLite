import { useState } from 'react'
import { cn } from '@/lib/utils'
import { Brain, TrendingUp, Clock, CheckCircle2, ArrowRight } from 'lucide-react'

interface Question {
  id: string
  dimension: 'foundation' | 'mindset' | 'timeframe'
  question: string
  options: {
    label: string
    value: string
    description: string
  }[]
}

const questions: Question[] = [
  // 理財基礎
  {
    id: 'f1',
    dimension: 'foundation',
    question: '你對投資分析有幾熟悉？',
    options: [
      { label: '完全新手', value: 'beginner', description: '未開始投資，想學習基礎知識' },
      { label: '有啲經驗', value: 'intermediate', description: '跟隨市場消息，定期檢視持倉' },
      { label: '好熟悉', value: 'advanced', description: '主動管理，頻繁交易，識技術分析' },
    ],
  },
  {
    id: 'f2',
    dimension: 'foundation',
    question: '你平時點樣做投資決定？',
    options: [
      { label: '跟朋友/專家建議', value: 'beginner', description: '鍾意跟住別人嘅建議買入' },
      { label: '自己研究 + 參考意見', value: 'intermediate', description: '會自己做功課，同時參考專業分析' },
      { label: '獨立分析決策', value: 'advanced', description: '靠自己嘅分析同策略快速決策' },
    ],
  },
  // 人生心態
  {
    id: 'm1',
    dimension: 'mindset',
    question: '面對市場波動，你通常點反應？',
    options: [
      { label: '擔心虧損', value: 'conservative', description: '市跌會焦慮，傾向止蝕離場' },
      { label: '理性分析', value: 'balanced', description: '會分析係暫時調整定趨勢改變' },
      { label: '視為機會', value: 'aggressive', description: '趁低吸納，增加持倉' },
    ],
  },
  {
    id: 'm2',
    dimension: 'mindset',
    question: '你投資嘅主要目標係咩？',
    options: [
      { label: '保值為上', value: 'conservative', description: '唔想輸錢，穩定收益優先' },
      { label: '穩中求勝', value: 'balanced', description: '接受適度風險，追求平衡增長' },
      { label: '最大化回報', value: 'aggressive', description: '願意承擔高風險換取高回報' },
    ],
  },
  // 時間視角
  {
    id: 't1',
    dimension: 'timeframe',
    question: '你期望持有一隻股票幾耐？',
    options: [
      { label: '幾年甚至更長', value: 'long', description: '長線持有，唔理短期波動' },
      { label: '幾個月到一年', value: 'medium', description: '中期投資，捕捉板塊輪動' },
      { label: '幾日到幾星期', value: 'short', description: '短線操作，快進快出' },
    ],
  },
  {
    id: 't2',
    dimension: 'timeframe',
    question: '你幾耐檢查一次個投組？',
    options: [
      { label: '每月/每季', value: 'long', description: '長期追蹤，唔會日日睇' },
      { label: '每週', value: 'medium', description: '定期檢視，調整配置' },
      { label: '每日', value: 'short', description: '密切監察，隨時調整' },
    ],
  },
]

interface UserProfileTestProps {
  onComplete: (profile: Userprofile) => void
}

export interface UserProfile {
  foundation: 'beginner' | 'intermediate' | 'advanced'
  mindset: 'conservative' | 'balanced' | 'aggressive'
  timeframe: 'long' | 'medium' | 'short'
}

export function UserProfileTest({ onComplete }: UserProfileTestProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [showResult, setShowResult] = useState(false)

  const question = questions[currentQuestion]
  const progress = ((currentQuestion + 1) / questions.length) * 100

  const handleAnswer = (value: string) => {
    const newAnswers = { ...answers, [question.id]: value }
    setAnswers(newAnswers)

    if (currentQuestion < questions.length - 1) {
      setTimeout(() => setCurrentQuestion(currentQuestion + 1), 200)
    } else {
      // 計算結果
      const profile = calculateProfile(newAnswers)
      setTimeout(() => {
        setShowResult(true)
        setTimeout(() => onComplete(profile), 2000)
      }, 300)
    }
  }

  const calculateProfile = (ans: Record<string, string>): UserProfile => {
    const foundationScores = { beginner: 0, intermediate: 1, advanced: 2 }
    const mindsetScores = { conservative: 0, balanced: 1, aggressive: 2 }
    const timeframeScores = { long: 0, medium: 1, short: 2 }

    const fValues = [ans['f1'], ans['f2']].map(v => foundationScores[v as keyof typeof foundationScores])
    const mValues = [ans['m1'], ans['m2']].map(v => mindsetScores[v as keyof typeof mindsetScores])
    const tValues = [ans['t1'], ans['t2']].map(v => timeframeScores[v as keyof typeof timeframeScores])

    const getLevel = (scores: number[], type: 'foundation' | 'mindset' | 'timeframe') => {
      const avg = scores.reduce((a, b) => a + b, 0) / scores.length
      if (type === 'foundation') return avg < 0.8 ? 'beginner' : avg < 1.5 ? 'intermediate' : 'advanced'
      if (type === 'mindset') return avg < 0.8 ? 'conservative' : avg < 1.5 ? 'balanced' : 'aggressive'
      return avg < 0.8 ? 'long' : avg < 1.5 ? 'medium' : 'short'
    }

    return {
      foundation: getLevel(fValues, 'foundation'),
      mindset: getLevel(mValues, 'mindset'),
      timeframe: getLevel(tValues, 'timeframe'),
    }
  }

  const getDimensionIcon = (dimension: string) => {
    switch (dimension) {
      case 'foundation': return <Brain className="w-5 h-5" />
      case 'mindset': return <TrendingUp className="w-5 h-5" />
      case 'timeframe': return <Clock className="w-5 h-5" />
    }
  }

  const getDimensionLabel = (dimension: string) => {
    switch (dimension) {
      case 'foundation': return '理財基礎'
      case 'mindset': return '人生心態'
      case 'timeframe': return '時間視角'
    }
  }

  if (showResult) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        <div className="text-center space-y-6 animate-fade-in">
          <CheckCircle2 className="w-20 h-20 mx-auto text-primary animate-pulse-glow" />
          <h2 className="text-3xl font-bold glow-text">分析完成！</h2>
          <p className="text-muted-foreground">Net 仔正在為你準備個人化內容...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-slide-up">
      {/* 進度條 */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">
            問題 {currentQuestion + 1} / {questions.length}
          </span>
          <span className="text-primary">{Math.round(progress)}%</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-primary to-secondary transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* 問題卡片 */}
      <div className="glass-card rounded-2xl p-8 space-y-6 glow-border">
        <div className="flex items-center gap-3 text-primary">
          {getDimensionIcon(question.dimension)}
          <span className="text-sm font-medium">{getDimensionLabel(question.dimension)}</span>
        </div>

        <h2 className="text-2xl font-bold">{question.question}</h2>

        <div className="space-y-3">
          {question.options.map((option, idx) => (
            <button
              key={option.value}
              onClick={() => handleAnswer(option.value)}
              className={cn(
                "w-full text-left p-4 rounded-xl border transition-all duration-200 group",
                "hover:border-primary hover:bg-primary/10",
                "focus:outline-none focus:ring-2 focus:ring-primary"
              )}
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              <div className="flex items-start gap-3">
                <div className="w-5 h-5 rounded-full border-2 border-muted-foreground group-hover:border-primary flex items-center justify-center mt-0.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <div>
                  <div className="font-medium group-hover:text-primary transition-colors">
                    {option.label}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">
                    {option.description}
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 提示 */}
      <p className="text-center text-sm text-muted-foreground">
        根據你的答案，Net 仔會為你推薦最適合嘅內容策略
      </p>
    </div>
  )
}
