import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('🪿 ErrorBoundary caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback
      return (
        <div style={{
          padding: '2rem',
          textAlign: 'center',
          background: '#1a1a2e',
          color: '#fff',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🐔</div>
          <h2 style={{ color: '#ff6b6b', marginBottom: '1rem' }}>页面出了点问题</h2>
          <p style={{ color: '#888', marginBottom: '1.5rem' }}>
            {this.state.error?.message || '未知错误'}
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '0.75rem 2rem',
              background: '#00d4aa',
              color: '#000',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1rem',
              cursor: 'pointer'
            }}
          >
            🔄 重新加载
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
