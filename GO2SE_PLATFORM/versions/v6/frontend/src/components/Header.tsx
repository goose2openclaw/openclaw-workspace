/**
 * 🪿 Header Component
 */

import { useStore } from '../stores/appStore'
import { Moon, Sun, RefreshCw } from 'lucide-react'

export function Header() {
  const { theme, setTheme, stats } = useStore()

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="logo">🪿 GO2SE</h1>
        <span className="subtitle">北斗七鑫量化平台</span>
      </div>
      
      <div className="header-center">
        <div className="status-badges">
          <span className="badge mode">
            模式: {stats?.trading_mode || 'dry_run'}
          </span>
          <span className="badge position">
            仓位: {((stats?.max_position || 0) * 100).toFixed(0)}%
          </span>
        </div>
      </div>
      
      <div className="header-right">
        <button className="icon-btn" onClick={toggleTheme} title="切换主题">
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
    </header>
  )
}
