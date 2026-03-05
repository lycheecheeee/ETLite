import { useState } from 'react'
import { cn } from '@/lib/utils'
import { Grid3X3, LayoutGrid, Move, Maximize2, Minimize2, Save, RotateCcw, Zap } from 'lucide-react'
import { ContentAtoms } from './ContentAtoms'

interface GammaModeProps {
  userProfile?: any
}

type ViewMode = 'grid' | 'list' | 'orbit' | 'custom'

export function GammaMode({ userProfile }: GammaModeProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('orbit')
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [atoms, setAtoms] = useState([
    { id: '1', type: 'market_index', visible: true, size: 'large' },
    { id: '2', type: 'stock', visible: true, size: 'medium' },
    { id: '3', type: 'macro', visible: true, size: 'small' },
    { id: '4', type: 'company', visible: true, size: 'medium' },
    { id: '5', type: 'sentiment', visible: true, size: 'small' },
    { id: '6', type: 'international', visible: true, size: 'small' },
  ])

  const toggleAtom = (id: string) => {
    setAtoms(atoms.map(atom => 
      atom.id === id ? { ...atom, visible: !atom.visible } : atom
    ))
  }

  const changeSize = (id: string, size: 'small' | 'medium' | 'large') => {
    setAtoms(atoms.map(atom => 
      atom.id === id ? { ...atom, size } : atom
    ))
  }

  const resetLayout = () => {
    setAtoms([
      { id: '1', type: 'market_index', visible: true, size: 'large' },
      { id: '2', type: 'stock', visible: true, size: 'medium' },
      { id: '3', type: 'macro', visible: true, size: 'small' },
      { id: '4', type: 'company', visible: true, size: 'medium' },
      { id: '5', type: 'sentiment', visible: true, size: 'small' },
      { id: '6', type: 'international', visible: true, size: 'small' },
    ])
  }

  return (
    <div className={cn(
      "space-y-6 transition-all",
      isFullscreen && "fixed inset-0 z-50 bg-background p-6 overflow-auto"
    )}>
      {/* 控制欄 */}
      <div className="glass-card rounded-xl p-4 glow-border">
        <div className="flex items-center justify-between flex-wrap gap-4">
          {/* 左側：標題 + 說明 */}
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-primary to-secondary">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-bold text-lg">Gamma 模式</h2>
              <p className="text-xs text-muted-foreground">完全自定義你嘅資訊宇宙</p>
            </div>
          </div>

          {/* 中間：視圖切換 */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                "px-3 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                viewMode === 'grid' 
                  ? "bg-primary text-primary-foreground" 
                  : "hover:bg-primary/10"
              )}
            >
              <Grid3X3 className="w-4 h-4" />
              網格
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                "px-3 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                viewMode === 'list' 
                  ? "bg-primary text-primary-foreground" 
                  : "hover:bg-primary/10"
              )}
            >
              <LayoutGrid className="w-4 h-4" />
              列表
            </button>
            <button
              onClick={() => setViewMode('orbit')}
              className={cn(
                "px-3 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                viewMode === 'orbit' 
                  ? "bg-primary text-primary-foreground" 
                  : "hover:bg-primary/10"
              )}
            >
              <Move className="w-4 h-4" />
              軌道
            </button>
          </div>

          {/* 右側：功能按鈕 */}
          <div className="flex items-center gap-2">
            <button
              onClick={resetLayout}
              className="p-2 rounded-lg hover:bg-primary/10 transition-colors"
              title="重置佈局"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 rounded-lg hover:bg-primary/10 transition-colors"
              title="設定"
            >
              <Maximize2 className="w-5 h-5" />
            </button>
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 rounded-lg hover:bg-primary/10 transition-colors"
              title={isFullscreen ? "退出全屏" : "全屏"}
            >
              {isFullscreen ? (
                <Minimize2 className="w-5 h-5" />
              ) : (
                <Maximize2 className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* 設定面板 */}
      {showSettings && (
        <div className="glass-card rounded-xl p-6 space-y-4 animate-slide-up">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">內容原子設定</h3>
            <button
              onClick={() => setShowSettings(false)}
              className="text-sm text-primary hover:underline"
            >
              完成
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {atoms.map((atom) => (
              <div
                key={atom.id}
                className={cn(
                  "p-3 rounded-lg border transition-all",
                  atom.visible ? "border-primary bg-primary/10" : "border-border opacity-50"
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">
                    {atom.type.toUpperCase()}
                  </span>
                  <button
                    onClick={() => toggleAtom(atom.id)}
                    className={cn(
                      "w-8 h-4 rounded-full transition-colors",
                      atom.visible ? "bg-primary" : "bg-muted"
                    )}
                  >
                    <div
                      className={cn(
                        "w-3 h-3 rounded-full bg-white transition-transform",
                        atom.visible ? "translate-x-4" : "translate-x-0.5"
                      )}
                    />
                  </button>
                </div>
                
                {atom.visible && (
                  <div className="flex gap-1">
                    {(['small', 'medium', 'large'] as const).map((size) => (
                      <button
                        key={size}
                        onClick={() => changeSize(atom.id, size)}
                        className={cn(
                          "flex-1 px-2 py-1 text-xs rounded transition-colors",
                          atom.size === size
                            ? "bg-primary text-primary-foreground"
                            : "hover:bg-primary/10"
                        )}
                      >
                        {size === 'small' ? 'S' : size === 'medium' ? 'M' : 'L'}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="pt-4 border-t border-border">
            <button className="w-full py-2 rounded-lg bg-gradient-to-r from-primary to-secondary text-primary-foreground font-medium hover:opacity-90 transition-opacity">
              儲存佈局
            </button>
          </div>
        </div>
      )}

      {/* 內容區域 */}
      <ContentAtoms mode={viewMode === 'orbit' ? 'ai' : viewMode === 'grid' ? 'gamma' : 'traditional'} />

      {/* 快捷提示 */}
      <div className="fixed bottom-6 right-6 glass-card rounded-full px-4 py-2 text-sm shadow-glow animate-pulse">
        💡 提示：拖曳原子重新排列，雙擊放大詳情
      </div>
    </div>
  )
}
