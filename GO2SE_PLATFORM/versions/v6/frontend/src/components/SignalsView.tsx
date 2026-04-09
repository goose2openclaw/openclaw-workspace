/**
 * 🪿 Signals View Component
 */

import { useStore, Signal } from '../stores/appStore'

const signalConfig = {
  buy: { icon: '🟢', color: '#10b981', label: '买入' },
  sell: { icon: '🔴', color: '#ef4444', label: '卖出' },
  hold: { icon: '🟡', color: '#f59e0b', label: '观望' },
}

function SignalCard({ signal }: { signal: Signal }) {
  const config = signalConfig[signal.signal]
  
  return (
    <div 
      className="signal-card"
      style={{ borderLeftColor: config.color }}
    >
      <div className="signal-header">
        <span className="strategy">{signal.strategy}</span>
        <span 
          className="signal-type"
          style={{ color: config.color }}
        >
          {config.icon} {config.label}
        </span>
      </div>
      
      <div className="signal-body">
        <span className="symbol">{signal.symbol}</span>
        <span className="confidence">
          置信度: {signal.confidence?.toFixed(1)}/10
        </span>
      </div>
      
      <div className="signal-reason">{signal.reason}</div>
      
      <div className="signal-footer">
        <span className="time">
          {new Date(signal.created_at).toLocaleString()}
        </span>
        {signal.executed && (
          <span className="executed">✅ 已执行</span>
        )}
      </div>
    </div>
  )
}

export function SignalsView() {
  const { signals } = useStore()
  
  const buySignals = signals.filter(s => s.signal === 'buy')
  const sellSignals = signals.filter(s => s.signal === 'sell')

  if (!signals.length) {
    return (
      <div className="empty-state">
        <p>暂无信号</p>
      </div>
    )
  }

  return (
    <div className="signals-view">
      <div className="signals-summary">
        <div className="summary-card buy">
          <span className="count">{buySignals.length}</span>
          <span className="label">买入信号</span>
        </div>
        <div className="summary-card sell">
          <span className="count">{sellSignals.length}</span>
          <span className="label">卖出信号</span>
        </div>
      </div>

      <div className="signals-list">
        {signals.map((signal) => (
          <SignalCard key={signal.id} signal={signal} />
        ))}
      </div>
    </div>
  )
}
