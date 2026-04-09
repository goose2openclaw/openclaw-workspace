/**
 * 🪿 GO2SE 主应用
 * Go2Se护食的小白鹅
 */

import { useState, useEffect, createContext, useContext } from 'react'
import { useStore } from './stores/appStore'
import { useAutoRefresh } from './hooks/useAPI'
import { LoadingScreen } from './components/LoadingScreen'
import { ErrorBoundary } from './components/ErrorBoundary'
import { Dashboard } from './views/Dashboard'
import { Market } from './views/Market'
import { Strategies } from './views/Strategies'
import { Signals } from './views/Signals'
import { Trades } from './views/Trades'
import { Wallet } from './views/Wallet'
import { Settings } from './views/Settings'
import { Alternatives } from './views/Alternatives'

// Theme Context
type Theme = 'dark' | 'light'
const ThemeContext = createContext<{ theme: Theme; setTheme: (t: Theme) => void }>({ 
  theme: 'dark', 
  setTheme: () => {} 
})
export const useTheme = () => useContext(ThemeContext)

type Section = 'overview' | 'market' | 'strategies' | 'signals' | 'trades' | 'wallet' | 'alternatives' | 'settings'

const navItems = [
  { id: 'overview', label: '总览', icon: '📊' },
  { id: 'market', label: '市场', icon: '📈' },
  { id: 'strategies', label: '策略', icon: '🧠' },
  { id: 'signals', label: '信号', icon: '🎯' },
  { id: 'trades', label: '交易', icon: '💰' },
  { id: 'wallet', label: '钱包', icon: '🔐' },
  { id: 'alternatives', label: '备选', icon: '🧩' },
  { id: 'settings', label: '设置', icon: '⚙️' },
]

function App() {
  const [activeSection, setActiveSection] = useState<Section>('overview')
  const [isLoading, setIsLoading] = useState(true)
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  
  const { wsConnected } = useStore()
  const { refreshAll, loading } = useAutoRefresh(15000)

  // 初始化加载数据
  useEffect(() => {
    refreshAll().then(() => setIsLoading(false))
  }, [])

  // 根据时间自动切换主题
  useEffect(() => {
    const hour = new Date().getHours()
    const isNight = hour < 6 || hour >= 18
    setTheme(isNight ? 'dark' : 'light')
  }, [])

  // 应用主题到HTML
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement).tagName === 'INPUT') return
      if (e.key >= '1' && e.key <= '8') {
        setActiveSection(navItems[parseInt(e.key) - 1]?.id as Section)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const currentNav = navItems.find(n => n.id === activeSection)

  if (isLoading) return <LoadingScreen />

  const renderPage = () => {
    switch (activeSection) {
      case 'overview': return <DashboardWithTheme />
      case 'market': return <Market />
      case 'strategies': return <Strategies />
      case 'signals': return <Signals />
      case 'trades': return <Trades />
      case 'wallet': return <Wallet />
      case 'alternatives': return <Alternatives />
      case 'settings': return <Settings />
      default: return <DashboardWithTheme />
    }
  }

  // 包装Dashboard以传递主题
  const DashboardWithTheme = () => (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <Dashboard />
    </ThemeContext.Provider>
  )

  return (
    <ErrorBoundary>
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <div className="app">
        {/* Header - 简洁版 */}
        <header style={{
          padding: '0 24px',
          background: theme === 'dark' ? 'rgba(12, 18, 34, 0.95)' : 'rgba(224, 242, 254, 0.95)',
          borderBottom: `1px solid ${theme === 'dark' ? '#1E293B' : '#E2E8F0'}`,
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}>
          <div style={{
            maxWidth: '1440px',
            margin: '0 auto',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: '56px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '1.5rem' }}>🪿</span>
              <span style={{ fontSize: '1.125rem', fontWeight: 700, color: theme === 'dark' ? '#F1F5F9' : '#0F172A' }}>
                Go2Se 护食
              </span>
            </div>
            <nav style={{ display: 'flex', gap: '4px' }}>
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveSection(item.id as Section)}
                  style={{
                    padding: '8px 14px',
                    border: 'none',
                    background: activeSection === item.id 
                      ? (theme === 'dark' ? '#00D4AA' : '#0891B2') 
                      : 'transparent',
                    color: activeSection === item.id 
                      ? '#FFFFFF' 
                      : (theme === 'dark' ? '#94A3B8' : '#64748B'),
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '0.8125rem',
                    fontWeight: 500,
                    transition: 'all 0.2s ease',
                  }}
                >
                  {item.icon} {item.label}
                </button>
              ))}
            </nav>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 10px',
                background: theme === 'dark' ? '#1E293B' : '#F1F5F9',
                borderRadius: '12px',
                fontSize: '0.6875rem',
              }}>
                <span style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: '#10B981',
                }} />
                <span style={{ color: theme === 'dark' ? '#94A3B8' : '#64748B' }}>
                  {wsConnected ? '在线' : '离线'}
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Main */}
        <main style={{
          minHeight: 'calc(100vh - 56px)',
        }}>
          {renderPage()}
        </main>
      </div>
    </ThemeContext.Provider>
    </ErrorBoundary>
  )
}

export default App
