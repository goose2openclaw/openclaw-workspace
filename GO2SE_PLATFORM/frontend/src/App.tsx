/**
 * 🪿 GO2SE V12 审美进化版
 * ========================
 * V6 7页架构 + V9 双重脑架构 + V12 美学进化
 * 
 * V12美学进化 (基于Polanyi隐性知识20轮迭代):
 * - R1: 视觉层次 - 增加渐变和层级
 * - R2: 色彩和谐 - 增强CSS变量系统
 * - R3: 空间节奏 - 4px基准网格
 * - R4: 交互直觉 - 增强hover/transition
 * - R5: 动态流畅 - @keyframes动画
 * - R6: 字体排版 - 明确字号变量
 * - R7: 卡片深度 - box-shadow层次
 * - R8: 边框处理 - 优雅边框+backdrop
 * - R9: 响应式 - @media断点
 * - R10: 暗色舒适 - 减少蓝光+径向渐变
 */

import { useState, useEffect, createContext, useContext, useCallback } from 'react'
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

// ============================================================================
// Theme Context
// ============================================================================
type Theme = 'dark' | 'light'
const ThemeContext = createContext<{ theme: Theme; setTheme: (t: Theme) => void }>({ 
  theme: 'dark', 
  setTheme: () => {} 
})
export const useTheme = () => useContext(ThemeContext)

// ============================================================================
// Dual Brain Context
// ============================================================================
interface BrainStatus {
  brain_id: string
  mode: string
  state: string
  health: number
  alive: boolean
}

interface WalletArchitecture {
  main: { balance: number }
  transfer: { balance: number }
  exchange: { balance: number }
  total: number
}

interface LobsterStatus {
  retro: number
  simulation: number
  optimization: number
}

interface DualBrainState {
  activeBrain: 'left' | 'right'
  activeMode: 'normal' | 'expert'
  leftBrain: BrainStatus
  rightBrain: BrainStatus
  wallet: WalletArchitecture
  lobster: LobsterStatus
  hermes: {
    iterations: number
    memory: number
    skills: number
  }
}

const DualBrainContext = createContext<{
  state: DualBrainState
  switchBrain: (target: 'left' | 'right') => Promise<void>
  switchMode: (mode: 'normal' | 'expert') => Promise<void>
  runRetro: () => Promise<void>
  runSimulation: () => Promise<void>
  runOptimization: () => Promise<void>
  runMirofish: () => Promise<void>
  runGstack: () => Promise<void>
  refresh: () => Promise<void>
}>({
  state: {
    activeBrain: 'left',
    activeMode: 'normal',
    leftBrain: { brain_id: 'left', mode: 'normal', state: 'active', health: 1.0, alive: true },
    rightBrain: { brain_id: 'right', mode: 'expert', state: 'standby', health: 1.0, alive: true },
    wallet: { main: { balance: 100000 }, transfer: { balance: 50000 }, exchange: { balance: 65000 }, total: 215000 },
    lobster: { retro: 0, simulation: 0, optimization: 0 },
    hermes: { iterations: 0, memory: 0, skills: 0 }
  },
  switchBrain: async () => {},
  switchMode: async () => {},
  runRetro: async () => {},
  runSimulation: async () => {},
  runOptimization: async () => {},
  runMirofish: async () => {},
  runGstack: async () => {},
  refresh: async () => {}
})

export const useDualBrain = () => useContext(DualBrainContext)

// ============================================================================
// API Client
// ============================================================================
const API_BASE = '/api'

const dualBrainAPI = {
  async getStatus() {
    try {
      const res = await fetch(`${API_BASE}/dual-brain/status`)
      return await res.json()
    } catch { return null }
  },
  async getWallet() {
    try {
      const res = await fetch(`${API_BASE}/dual-brain/wallet-status`)
      return await res.json()
    } catch { return null }
  },
  async getLobster() {
    try {
      const res = await fetch(`${API_BASE}/dual-brain/lobster/status`)
      return await res.json()
    } catch { return null }
  },
  async getHermes() {
    try {
      const res = await fetch(`${API_BASE}/hermes/status`)
      return await res.json()
    } catch { return null }
  },
  async switchBrain(target: string) {
    try {
      await fetch(`${API_BASE}/dual-brain/switch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target })
      })
    } catch {}
  },
  async switchMode(mode: string) {
    try {
      await fetch(`${API_BASE}/dual-brain/switch-mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode })
      })
    } catch {}
  },
  async runRetro() {
    try {
      await fetch(`${API_BASE}/dual-brain/lobster/retro`, { method: 'POST' })
    } catch {}
  },
  async runSimulation() {
    try {
      await fetch(`${API_BASE}/dual-brain/lobster/simulation`, { method: 'POST' })
    } catch {}
  },
  async runOptimization() {
    try {
      await fetch(`${API_BASE}/dual-brain/lobster/optimization`, { method: 'POST' })
    } catch {}
  },
  async runMirofish() {
    try {
      await fetch(`${API_BASE}/go2se/v9/scan-and-select`, { method: 'POST' })
    } catch {}
  },
  async runGstack() {
    try {
      await fetch(`${API_BASE}/hermes/iterate`, { method: 'POST' })
    } catch {}
  }
}

// ============================================================================
// Navigation
// ============================================================================
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

// ============================================================================
// Dual Brain Components
// ============================================================================

const BrainSwitcher: React.FC<{
  activeBrain: 'left' | 'right'
  leftBrain: BrainStatus
  rightBrain: BrainStatus
  onSwitch: (brain: 'left' | 'right') => void
}> = ({ activeBrain, leftBrain, rightBrain, onSwitch }) => {
  return (
    <div className="brain-switcher">
      <div className={`brain-indicator ${activeBrain === 'left' ? 'active' : ''}`} onClick={() => onSwitch('left')}>
        <span className="brain-icon">🧠</span>
        <span className="brain-label">左脑</span>
        <span className="brain-mode">{leftBrain.mode === 'normal' ? '普通' : '专家'}</span>
        <div className="health-bar">
          <div className="health-fill" style={{ width: `${leftBrain.health * 100}%` }} />
        </div>
      </div>
      
      <div className="switch-arrow">
        <button onClick={() => onSwitch(activeBrain === 'left' ? 'right' : 'left')}>
          ⬌
        </button>
      </div>
      
      <div className={`brain-indicator ${activeBrain === 'right' ? 'active' : ''}`} onClick={() => onSwitch('right')}>
        <span className="brain-icon">🧠</span>
        <span className="brain-label">右脑</span>
        <span className="brain-mode">{rightBrain.mode === 'normal' ? '普通' : '专家'}</span>
        <div className="health-bar">
          <div className="health-fill" style={{ width: `${rightBrain.health * 100}%` }} />
        </div>
      </div>
    </div>
  )
}

const WalletDisplay: React.FC<{ wallet: WalletArchitecture }> = ({ wallet }) => {
  return (
    <div className="wallet-display">
      <div className="wallet-flow">
        <div className="wallet-box main">
          <span className="wallet-label">主钱包</span>
          <span className="wallet-balance">${wallet.main.balance.toLocaleString()}</span>
        </div>
        <span className="wallet-arrow">→</span>
        <div className="wallet-box transfer">
          <span className="wallet-label">中转钱包</span>
          <span className="wallet-balance">${wallet.transfer.balance.toLocaleString()}</span>
        </div>
        <span className="wallet-arrow">→</span>
        <div className="wallet-box exchange">
          <span className="wallet-label">交易所</span>
          <span className="wallet-balance">${wallet.exchange.balance.toLocaleString()}</span>
        </div>
      </div>
      <div className="total-assets">
        总资产: <strong>${wallet.total.toLocaleString()}</strong>
      </div>
    </div>
  )
}

const LobsterPanel: React.FC<{
  lobster: LobsterStatus
  onRetro: () => void
  onSimulation: () => void
  onOptimization: () => void
  onMirofish: () => void
  onGstack: () => void
}> = ({ lobster, onRetro, onSimulation, onOptimization, onMirofish, onGstack }) => {
  return (
    <div className="lobster-panel">
      <div className="lobster-stats">
        <div className="stat">
          <span className="stat-label">复盘</span>
          <span className="stat-value">{lobster.retro}</span>
        </div>
        <div className="stat">
          <span className="stat-label">仿真</span>
          <span className="stat-value">{lobster.simulation}</span>
        </div>
        <div className="stat">
          <span className="stat-label">优化</span>
          <span className="stat-value">{lobster.optimization}</span>
        </div>
      </div>
      <div className="lobster-actions">
        <button onClick={onRetro}>📊 复盘</button>
        <button onClick={onSimulation}>🧠 仿真</button>
        <button onClick={onOptimization}>⚙️ 优化</button>
        <button onClick={onMirofish}>🔮 MiroFish</button>
        <button onClick={onGstack} className="primary">🧬 gstack</button>
      </div>
    </div>
  )
}

// ============================================================================
// Main App
// ============================================================================
function App() {
  const [activeSection, setActiveSection] = useState<Section>('overview')
  const [isLoading, setIsLoading] = useState(true)
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  
  // Dual Brain State
  const [dualBrainState, setDualBrainState] = useState<DualBrainState>({
    activeBrain: 'left',
    activeMode: 'normal',
    leftBrain: { brain_id: 'left', mode: 'normal', state: 'active', health: 1.0, alive: true },
    rightBrain: { brain_id: 'right', mode: 'expert', state: 'standby', health: 1.0, alive: true },
    wallet: { main: { balance: 100000 }, transfer: { balance: 50000 }, exchange: { balance: 65000 }, total: 215000 },
    lobster: { retro: 0, simulation: 0, optimization: 0 },
    hermes: { iterations: 0, memory: 0, skills: 0 }
  })

  const { wsConnected } = useStore()
  const { refreshAll, loading } = useAutoRefresh(15000)

  // 初始化加载数据
  useEffect(() => {
    refreshDualBrain()
    setIsLoading(false)
  }, [])

  // Dual Brain刷新
  const refreshDualBrain = useCallback(async () => {
    const [status, wallet, lobster, hermes] = await Promise.all([
      dualBrainAPI.getStatus(),
      dualBrainAPI.getWallet(),
      dualBrainAPI.getLobster(),
      dualBrainAPI.getHermes()
    ])

    if (status) {
      const bm = status.brain_manager || {}
      setDualBrainState(prev => ({
        ...prev,
        activeBrain: bm.active_brain || 'left',
        activeMode: bm.active_mode || 'normal',
        leftBrain: bm.left_brain || prev.leftBrain,
        rightBrain: bm.right_brain || prev.rightBrain,
        lobster: {
          retro: lobster?.retro_count || 0,
          simulation: lobster?.simulation_count || 0,
          optimization: lobster?.optimization_count || 0
        }
      }))
    }

    if (wallet) {
      setDualBrainState(prev => ({
        ...prev,
        wallet: {
          main: { balance: wallet.main_wallet?.balance || 100000 },
          transfer: { balance: wallet.transfer_wallet?.balance || 50000 },
          exchange: { balance: wallet.exchange_walllets ? Object.values(wallet.exchange_walllets).reduce((s: number, w: any) => s + w.balance, 0) : 65000 },
          total: wallet.total_assets || 215000
        }
      }))
    }

    if (hermes) {
      setDualBrainState(prev => ({
        ...prev,
        hermes: {
          iterations: hermes.stats?.total_iterations || 0,
          memory: (hermes.memory?.episodic_size || 0) + (hermes.memory?.semantic_size || 0),
          skills: hermes.memory?.skills_count || 0
        }
      }))
    }
  }, [])

  // 自动刷新
  useEffect(() => {
    const interval = setInterval(refreshDualBrain, 30000)
    return () => clearInterval(interval)
  }, [refreshDualBrain])

  // 脑切换
  const switchBrain = useCallback(async (target: 'left' | 'right') => {
    await dualBrainAPI.switchBrain(target)
    await refreshDualBrain()
  }, [refreshDualBrain])

  // 模式切换
  const switchMode = useCallback(async (mode: 'normal' | 'expert') => {
    await dualBrainAPI.switchMode(mode)
    await refreshDualBrain()
  }, [refreshDualBrain])

  // 龙虾/MiroFish/gstack操作
  const runRetro = useCallback(async () => {
    await dualBrainAPI.runRetro()
    await refreshDualBrain()
  }, [refreshDualBrain])

  const runSimulation = useCallback(async () => {
    await dualBrainAPI.runSimulation()
    await refreshDualBrain()
  }, [refreshDualBrain])

  const runOptimization = useCallback(async () => {
    await dualBrainAPI.runOptimization()
    await refreshDualBrain()
  }, [refreshDualBrain])

  const runMirofish = useCallback(async () => {
    await dualBrainAPI.runMirofish()
    await refreshDualBrain()
  }, [refreshDualBrain])

  const runGstack = useCallback(async () => {
    await dualBrainAPI.runGstack()
    await refreshDualBrain()
  }, [refreshDualBrain])

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

  // 键盘快捷键
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

  // Dual Brain Context Value
  const dualBrainContext = {
    state: dualBrainState,
    switchBrain,
    switchMode,
    runRetro,
    runSimulation,
    runOptimization,
    runMirofish,
    runGstack,
    refresh: refreshDualBrain
  }

  if (isLoading) return <LoadingScreen />

  const renderPage = () => {
    switch (activeSection) {
      case 'overview': return <DashboardWithDualBrain />
      case 'market': return <Market />
      case 'strategies': return <Strategies />
      case 'signals': return <Signals />
      case 'trades': return <Trades />
      case 'wallet': return <Wallet />
      case 'alternatives': return <Alternatives />
      case 'settings': return <Settings />
      default: return <DashboardWithDualBrain />
    }
  }

  // 包装Dashboard以传递主题和DualBrain
  const DashboardWithDualBrain = () => (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <DualBrainContext.Provider value={dualBrainContext}>
        <Dashboard />
      </DualBrainContext.Provider>
    </ThemeContext.Provider>
  )

  return (
    <ErrorBoundary>
      <div className="go2se-app">
        {/* Header */}
        <header className="app-header">
          <div className="header-left">
            <h1>🪿 GO2SE</h1>
            <span className="version-badge">V12</span>
          </div>
          
          {/* Dual Brain Status */}
          <div className="dual-brain-status">
            <BrainSwitcher
              activeBrain={dualBrainState.activeBrain}
              leftBrain={dualBrainState.leftBrain}
              rightBrain={dualBrainState.rightBrain}
              onSwitch={switchBrain}
            />
          </div>
          
          <div className="header-right">
            <span className={`status-indicator ${dualBrainState.activeBrain}`}>
              🧠 {dualBrainState.activeBrain === 'left' ? '左脑' : '右脑'}
              ({dualBrainState.activeMode === 'normal' ? '普通' : '专家'})
            </span>
          </div>
        </header>

        {/* Navigation */}
        <nav className="app-nav">
          {navItems.map(item => (
            <button
              key={item.id}
              className={activeSection === item.id ? 'active' : ''}
              onClick={() => setActiveSection(item.id as Section)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Main Content */}
        <main className="app-main">
          {renderPage()}
        </main>

        {/* Footer */}
        <footer className="app-footer">
          <div className="footer-left">
            <WalletDisplay wallet={dualBrainState.wallet} />
          </div>
          <div className="footer-center">
            <LobsterPanel
              lobster={dualBrainState.lobster}
              onRetro={runRetro}
              onSimulation={runSimulation}
              onOptimization={runOptimization}
              onMirofish={runMirofish}
              onGstack={runGstack}
            />
          </div>
          <div className="footer-right">
            <span>🧬 Hermes: 迭代{dualBrainState.hermes.iterations} | 记忆{dualBrainState.hermes.memory} | 技能{dualBrainState.hermes.skills}</span>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  )
}

export default App
