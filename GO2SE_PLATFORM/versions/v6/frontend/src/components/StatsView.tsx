/**
 * 🪿 Stats View Component
 */

import { useStore } from '../stores/appStore'

export function StatsView() {
  const { stats } = useStore()

  if (!stats) {
    return (
      <div className="empty-state">
        <p>加载统计中...</p>
      </div>
    )
  }

  const statCards = [
    { label: '总交易', value: stats.total_trades, icon: '📊' },
    { label: '持仓中', value: stats.open_trades, icon: '🔒' },
    { label: '信号总数', value: stats.total_signals, icon: '🎯' },
    { label: '已执行', value: stats.executed_signals, icon: '✅' },
    { label: '胜率', value: `${stats.win_rate || 0}%`, icon: '📈' },
    { label: '总盈亏', value: `${stats.total_pnl || 0}`, icon: '💰' },
  ]

  return (
    <div className="stats-view">
      <div className="stats-grid">
        {statCards.map((stat) => (
          <div key={stat.label} className="stat-card">
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-value">{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="config-section">
        <h3>⚙️ 当前配置</h3>
        <div className="config-grid">
          <div className="config-item">
            <span className="label">交易模式</span>
            <span className="value">{stats.trading_mode || 'dry_run'}</span>
          </div>
          <div className="config-item">
            <span className="label">最大仓位</span>
            <span className="value">{((stats.max_position || 0) * 100).toFixed(0)}%</span>
          </div>
          <div className="config-item">
            <span className="label">止损线</span>
            <span className="value">-{((stats.stop_loss || 0) * 100).toFixed(0)}%</span>
          </div>
          <div className="config-item">
            <span className="label">止盈线</span>
            <span className="value">+{((stats.take_profit || 0) * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}
