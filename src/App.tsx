import { useState } from 'react'
import { cn } from '@/lib/utils'
import { PlayCircle, Radio, Atom, Sparkles, Menu, X, User, Settings, Bell, Mic2, MessageCircle, Newspaper } from 'lucide-react'
import { ErrorBoundary } from './components/ErrorBoundary'
import { UserProfileTest, type UserProfile } from './components/UserProfileTest'
import { PodcastPlayer } from './components/PodcastPlayer'
import { ContentAtoms } from './components/ContentAtoms'
import { GammaMode } from './components/GammaMode'
import { InteractiveRadio } from './components/InteractiveRadio'
import { ChatWithLeungZai } from './components/ChatWithLeungZai'
import { AINewsPodcast } from './components/AINewsPodcast'
import { SmartRadioPlayer } from './components/SmartRadioPlayer'

type Tab = 'profile' | 'chat' | 'radio' | 'smart-radio' | 'podcast' | 'news' | 'atoms' | 'gamma'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('profile')
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [showMobileMenu, setShowMobileMenu] = useState(false)

  const handleProfileComplete = (profile: UserProfile) => {
    setUserProfile(profile)
    setActiveTab('podcast')
  }

  const navItems = [
    { id: 'profile' as Tab, label: '個人化測試', icon: User },
    { id: 'chat' as Tab, label: '同叻仔傾計', icon: MessageCircle },
    { id: 'radio' as Tab, label: '互動電台', icon: Mic2 },
    { id: 'smart-radio' as Tab, label: 'AI 智能電台', icon: Sparkles },
    { id: 'news' as Tab, label: 'AI趨勢節目', icon: Newspaper },
    { id: 'podcast' as Tab, label: 'AI 播客', icon: PlayCircle },
    { id: 'atoms' as Tab, label: '內容原子', icon: Atom },
    { id: 'gamma' as Tab, label: 'Gamma 模式', icon: Sparkles },
  ]

  return (
    <ErrorBoundary>
      <div className="min-h-screen relative">
      {/* 宇宙背景 */}
      <div className="cosmic-bg" />
      
      {/* 頂部導航欄 */}
      <header className="sticky top-0 z-40 glass-card border-b border-border">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center animate-pulse-glow">
                <Radio className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold glow-text">Net 仔</h1>
                <p className="text-xs text-muted-foreground">AI 粵語理財播客</p>
              </div>
            </div>

            {/* 桌面端導航 */}
            <nav className="hidden md:flex items-center gap-1">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={cn(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                    activeTab === item.id
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-primary/10"
                  )}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </button>
              ))}
            </nav>

            {/* 右側功能 */}
            <div className="flex items-center gap-2">
              <button className="p-2 rounded-lg hover:bg-primary/10 transition-colors relative">
                <Bell className="w-5 h-5" />
                <div className="absolute top-1 right-1 w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              </button>
              <button className="p-2 rounded-lg hover:bg-primary/10 transition-colors">
                <Settings className="w-5 h-5" />
              </button>
              
              {/* 移動端菜單按鈕 */}
              <button
                onClick={() => setShowMobileMenu(!showMobileMenu)}
                className="md:hidden p-2 rounded-lg hover:bg-primary/10 transition-colors"
              >
                {showMobileMenu ? (
                  <X className="w-5 h-5" />
                ) : (
                  <Menu className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* 移動端菜單 */}
        {showMobileMenu && (
          <div className="md:hidden border-t border-border glass-card animate-slide-up">
            <nav className="p-4 space-y-2">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id)
                    setShowMobileMenu(false)
                  }}
                  className={cn(
                    "w-full px-4 py-3 rounded-lg text-left font-medium transition-all flex items-center gap-3",
                    activeTab === item.id
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-primary/10"
                  )}
                >
                  <item.icon className="w-5 h-5" />
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
        )}
      </header>

      {/* 主內容區 */}
      <main className="container mx-auto px-4 py-8 relative z-10">
        {/* 用戶狀態提示 */}
        {userProfile && activeTab !== 'profile' && (
          <div className="mb-6 glass-card rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-medium">你的投資畫像</p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span className="px-2 py-0.5 rounded-full bg-primary/20 text-primary">
                    {userProfile.foundation === 'beginner' ? '新手' : userProfile.foundation === 'intermediate' ? '中階' : '高階'}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-secondary/20 text-secondary">
                    {userProfile.mindset === 'conservative' ? '求穩型' : userProfile.mindset === 'balanced' ? '平衡型' : '進取型'}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-accent/20 text-accent">
                    {userProfile.timeframe === 'long' ? '長線' : userProfile.timeframe === 'medium' ? '中線' : '短線'}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setActiveTab('profile')}
              className="text-sm text-primary hover:underline"
            >
              重新測試
            </button>
          </div>
        )}

        {/* 內容區域 */}
        <div className="animate-fade-in">
          {activeTab === 'profile' && (
            <div className="py-8">
              {!userProfile ? (
                <>
                  <div className="text-center mb-8 space-y-2">
                    <h2 className="text-3xl font-bold glow-text">認識你自己，投資更精明</h2>
                    <p className="text-muted-foreground">
                      Net 仔會透過 6 條問題，了解你嘅理財風格，為你準備最適合嘅內容
                    </p>
                  </div>
                  <UserProfileTest onComplete={handleProfileComplete} />
                </>
              ) : (
                <div className="text-center py-16 space-y-6">
                  <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center animate-pulse-glow">
                    <User className="w-12 h-12 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold">你嘅投資畫像已建立</h2>
                  <p className="text-muted-foreground">
                    Net 仔已經記住你嘅偏好，隨時為你提供個人化內容
                  </p>
                  <button
                    onClick={() => setActiveTab('podcast')}
                    className="px-6 py-3 rounded-xl bg-gradient-to-r from-primary to-secondary font-medium hover:opacity-90 transition-opacity"
                  >
                    開始收聽 →
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-8 space-y-2">
                <h2 className="text-3xl font-bold glow-text">同叻仔傾計</h2>
                <p className="text-muted-foreground">
                  AI 粵語理財助手，有問必答，陪你投資路上不孤單
                </p>
              </div>
              <ChatWithLeungZai />
            </div>
          )}

          {activeTab === 'podcast' && (
            <div className="max-w-3xl mx-auto">
              <div className="text-center mb-8 space-y-2">
                <h2 className="text-3xl font-bold glow-text">今日財經播客</h2>
                <p className="text-muted-foreground">
                  AI 生成嘅個人化粵語理財內容，幫你快速掌握市場脈搏
                </p>
              </div>
              <PodcastPlayer userProfile={userProfile} />
            </div>
          )}

          {activeTab === 'radio' && (
            <div className="space-y-6">
              <div className="text-center mb-8 space-y-2">
                <h2 className="text-3xl font-bold glow-text">互動財經電台</h2>
                <p className="text-muted-foreground">
                  模擬真實電台體驗，多主持人對話 + 聽眾 Call-in 互動
                </p>
              </div>
              <InteractiveRadio userProfile={userProfile} />
            </div>
          )}

          {activeTab === 'smart-radio' && (
            <div className="max-w-5xl mx-auto">
              <div className="text-center mb-8 space-y-2">
                <h2 className="text-3xl font-bold glow-text">AI 智能電台</h2>
                <p className="text-muted-foreground">
                  LLM 實時生成主持對話 + Cantonese AI TTS 語音合成，真係識講嘢！
                </p>
              </div>
              <SmartRadioPlayer topic="AI趨勢" />
            </div>
          )}

          {activeTab === 'news' && (
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-8 space-y-2">
                <h2 className="text-3xl font-bold glow-text">AI趨勢節目</h2>
                <p className="text-muted-foreground">
                  抓取最新財經新聞，AI 深度分析趨勢，生成專業粵語播客
                </p>
              </div>
              <AINewsPodcast />
            </div>
          )}

          {activeTab === 'atoms' && (
            <div className="space-y-6">
              <div className="text-center mb-8 space-y-2">
                <h2 className="text-3xl font-bold glow-text">內容原子系統</h2>
                <p className="text-muted-foreground">
                  將複雜嘅金融資訊拆解為最小單位，靈活重組，随心搭配
                </p>
              </div>
              <ContentAtoms mode="ai" />
            </div>
          )}

          {activeTab === 'gamma' && (
            <div className="space-y-6">
              <div className="text-center mb-8 space-y-2">
                <h2 className="text-3xl font-bold glow-text">Gamma 模式</h2>
                <p className="text-muted-foreground">
                  完全自定義你嘅資訊宇宙，拖曳原子，創造屬於你嘅星系
                </p>
              </div>
              <GammaMode userProfile={userProfile} />
            </div>
          )}
        </div>
      </main>

      {/* 頁腳 */}
      <footer className="border-t border-border mt-16 py-8 relative z-10">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2026 Net 仔 - AI 粵語理財播客</p>
          <p className="mt-2">
            本內容僅供參考，不構成投資建議。投資涉及風險，入市須謹慎。
          </p>
        </div>
      </footer>
      </div>
    </ErrorBoundary>
  )
}

export default App
