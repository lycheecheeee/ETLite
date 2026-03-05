import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({ error, errorInfo })
    
    // 可以在這裡添加錯誤日誌服務
    // logErrorToService(error, errorInfo)
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen flex items-center justify-center p-4">
          <div className="glass-card rounded-xl p-8 max-w-md w-full text-center space-y-6">
            <div className="w-16 h-16 mx-auto rounded-full bg-red-500/20 flex items-center justify-center">
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
            
            <div>
              <h1 className="text-2xl font-bold mb-2">哎呀，出現咗啲問題</h1>
              <p className="text-muted-foreground">
                我哋嘅程式遇到咗一啲意外錯誤。你可以試下重新整理頁面，或者聯繫我哋嘅技術支援。
              </p>
            </div>

            <div className="space-y-3">
              <button
                onClick={this.handleReload}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-primary to-secondary font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-5 h-5" />
                重新整理頁面
              </button>
              
              <button
                onClick={() => this.setState({ hasError: false })}
                className="w-full py-3 rounded-xl bg-primary/10 hover:bg-primary/20 transition-colors"
              >
                試下繼續使用
              </button>
            </div>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="text-left">
                <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
                  錯誤詳情（開發模式）
                </summary>
                <pre className="mt-2 p-3 rounded-lg bg-black/20 text-xs overflow-auto max-h-40">
                  {this.state.error.toString()}
                  {this.state.errorInfo && '\n' + this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}