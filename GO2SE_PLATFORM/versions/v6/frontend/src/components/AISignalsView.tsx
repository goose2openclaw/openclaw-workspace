/**
 * 🪿 AI Signals View Component
 */

import { useState, useEffect } from 'react'
import { useStore, Signal } from '../stores/appStore'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

interface AISignal {
  symbol: string
  signal: string
  confidence: number
  strategy: string
  reason: string
  factors: { name: string; score: number }[]
  action: string
}

export function AISignalsView() {
  const [signals, setSignals] = useState<AISignal[]>([])
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)

  const fetchAISignals = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/ai/signals?limit=10&min_confidence=3.0`)
      const data = await res.json()
      setSignals(data.data?.signals || [])
    } catch (e) {
      console.error('Fetch AI signals error:', e)
    } finally {
      setLoading(false)
    }
  }

  const runAnalysis = async () => {
    setAnalyzing(true)
    try {
      const res = await fetch(`${API_BASE}/api/ai/reasoning`, { 
        method: 'POST' 
      })
      const data = await res.json()
      setSignals(data.data?.analysis || [])
    } catch (e) {
      console.error('Run analysis error:', e)
    } finally {
      setAnalyzing(false)
    }
  }

  useEffect(() => {
    fetchAISignals()
  }, [])

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 7) return '#10b981' // green
    if (confidence >= 5) return '#f59e0b' // yellow
    return '#6b7280' // gray
  }

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'buy': return '🟢'
      case 'sell': return '🔴'
      default: return '🟡'
    }
  }

  if (loading) {
    return <div className="loading">🧠 分析中...</div>
  }

  return (
    <div className="ai-signals-view">
      <div className="ai-header">
        <h2>🧠 AI 智能信号</h2>
        <button 
          className="analyze-btn"
          onClick={runAnalysis}
          disabled={analyzing}
        >
          {analyzing ? '🔄 分析中...' : '⚡ 重新分析'}
        </button>
      </div>

      <div className="ai-summary">
        <div className="summary-item">
          <span className="count">{signals.length}</span>
          <span className="label">信号总数</span>
        </div>
        <div className="summary-item buy">
          <span className="count">{signals.filter(s => s.signal === 'buy').length}</span>
          <span className="label">买入</span>
        </div>
        <div className="summary-item sell">
          <span className="count">{signals.filter(s => s.signal === 'sell').length}</span>
          <span className="label">卖出</span>
        </div>
        <div className="summary-item hold">
          <span className="count">{signals.filter(s => s.signal === 'hold').length}</span>
          <span className="label">观望</span>
        </div>
      </div>

      <div className="signals-list">
        {signals.map((signal, idx) => (
          <div key={idx} className="ai-signal-card">
            <div className="signal-top">
              <div className="signal-info">
                <span className="symbol">{signal.symbol}</span>
                <span className="strategy-badge">{signal.strategy}</span>
              </div>
              <div className="confidence-badge" style={{ 
                backgroundColor: getConfidenceColor(signal.confidence) 
              }}>
                {signal.confidence.toFixed(1)} / 10
              </div>
            </div>

            <div className="signal-middle">
              <span className="signal-type">
                {getSignalIcon(signal.signal)} {signal.signal.toUpperCase()}
              </span>
              <span className={`action-badge ${signal.action.toLowerCase()}`}>
                {signal.action === 'EXECUTE' ? '🚀 执行' : '👀 观望'}
              </span>
            </div>

            <div className="signal-reason">{signal.reason}</div>

            <div className="factors">
              {signal.factors?.map((factor, i) => (
                <span key={i} className="factor">
                  {factor.name} (+{factor.score})
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
