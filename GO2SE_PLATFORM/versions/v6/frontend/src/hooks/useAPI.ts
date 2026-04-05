/**
 * 🪿 GO2SE API Hooks - 带重试+降级
 */

import { useCallback } from 'react'
import { useStore, MarketData, Signal, Trade, Stats } from '../stores/appStore'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8004'

// ────────────────────────────────────────────────────────────────
// 重试配置
// ────────────────────────────────────────────────────────────────
const MAX_RETRIES = 3
const BASE_DELAY_MS = 500

async function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// ────────────────────────────────────────────────────────────────
// 通用请求 (带重试)
// ────────────────────────────────────────────────────────────────
async function fetchWithRetry<T>(
  url: string,
  options = {},
  retries = MAX_RETRIES,
  delay = BASE_DELAY_MS
): Promise<T> {
  let lastError: Error | null = null
  
  for (let i = 0; i <= retries; i++) {
    try {
      const res = await fetch(url, { ...options, signal: AbortSignal.timeout(8000) })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      return (json.data ?? json) as T
    } catch (e) {
      lastError = e as Error
      if (i < retries) {
        await sleep(delay * Math.pow(2, i)) // 指数退避: 500ms → 1s → 2s
      }
    }
  }
  throw lastError
}

// ────────────────────────────────────────────────────────────────
// 降级数据 (API失败时使用)
// ────────────────────────────────────────────────────────────────
const FALLBACK_MARKETS: MarketData[] = [
  { symbol: 'BTC/USDT', price: 66500, change_24h: -0.8, volume_24h: 500000000, rsi: 43, bid: 66499, ask: 66500 },
  { symbol: 'ETH/USDT', price: 2000, change_24h: -1.2, volume_24h: 210000000, rsi: 40, bid: 1999, ask: 2000 },
  { symbol: 'SOL/USDT', price: 82, change_24h: -2.0, volume_24h: 98000000, rsi: 32, bid: 81.9, ask: 82 },
]

const FALLBACK_STATS: Stats = {
  total_trades: 0,
  open_trades: 0,
  total_signals: 0,
  executed_signals: 0,
  trading_mode: 'dry_run',
  max_position: 0.6,
  stop_loss: 0.1,
  take_profit: 0.3,
}

// ────────────────────────────────────────────────────────────────
// Hooks
// ────────────────────────────────────────────────────────────────
export function useMarketData() {
  const { markets, setMarkets, loading } = useStore()
  
  const fetchMarkets = useCallback(async () => {
    try {
      const data = await fetchWithRetry<MarketData[]>(`${API_BASE}/api/market`)
      setMarkets(data)
    } catch (e) {
      console.warn('⚠️ Market API失败, 使用降级数据:', e)
      setMarkets(FALLBACK_MARKETS)
    }
  }, [setMarkets])
  
  return { markets, fetchMarkets, loading }
}

export function useSignals() {
  const { signals, setSignals, setLoading } = useStore()
  
  const fetchSignals = useCallback(async (limit = 50) => {
    try {
      const data = await fetchWithRetry<Signal[]>(`${API_BASE}/api/signals?limit=${limit}`)
      setSignals(data)
    } catch (e) {
      console.warn('⚠️ Signals API失败, 使用空数据:', e)
      setSignals([])
    }
  }, [setSignals])
  
  const runStrategy = useCallback(async (strategy: string) => {
    try {
      return await fetchWithRetry(`${API_BASE}/api/signals/${strategy}/run`, 3)
    } catch (e) {
      console.error('策略执行失败:', e)
      return { error: '策略执行失败，请重试' }
    }
  }, [])
  
  return { signals, fetchSignals, runStrategy }
}

export function useTrades() {
  const { trades, setTrades } = useStore()
  
  const fetchTrades = useCallback(async (limit = 50) => {
    try {
      const data = await fetchWithRetry<Trade[]>(`${API_BASE}/api/trades?limit=${limit}`)
      setTrades(data)
    } catch (e) {
      console.warn('⚠️ Trades API失败:', e)
      setTrades([])
    }
  }, [setTrades])
  
  return { trades, fetchTrades }
}

export function useStats() {
  const { stats, setStats } = useStore()
  
  const fetchStats = useCallback(async () => {
    try {
      const data = await fetchWithRetry<Stats>(`${API_BASE}/api/stats`)
      setStats(data)
    } catch (e) {
      console.warn('⚠️ Stats API失败, 使用降级数据:', e)
      setStats(FALLBACK_STATS)
    }
  }, [setStats])
  
  return { stats, fetchStats }
}

export function useWebSocket() {
  const { wsConnected, setWsConnected, setMarkets, setSignals } = useStore()
  
  const connect = useCallback(() => {
    const wsUrl = `ws://${window.location.hostname}:8004/api/ws`
    let ws: WebSocket | null = null
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null
    
    const connectWS = () => {
      try {
        ws = new WebSocket(wsUrl)
        
        ws.onopen = () => {
          console.log('🔌 WS Connected')
          setWsConnected(true)
        }
        
        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            switch (message.type) {
              case 'market':
                if (message.data) setMarkets(message.data)
                break
              case 'signal':
                if (message.data) setSignals([message.data, ...useStore.getState().signals])
                break
            }
          } catch (e) {
            console.warn('WS消息解析失败:', e)
          }
        }
        
        ws.onclose = () => {
          console.log('🔌 WS Disconnected, 5秒后重连...')
          setWsConnected(false)
          reconnectTimer = setTimeout(connectWS, 5000)
        }
        
        ws.onerror = () => {
          setWsConnected(false)
        }
      } catch (e) {
        console.warn('WS连接失败，5秒后重试:', e)
        reconnectTimer = setTimeout(connectWS, 5000)
      }
    }
    
    connectWS()
    
    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer)
      ws?.close()
    }
  }, [setWsConnected, setMarkets, setSignals])
  
  return { wsConnected, connect }
}

// 自动刷新Hook
export function useAutoRefresh(interval = 15000) {
  const { fetchMarkets } = useMarketData()
  const { fetchSignals } = useSignals()
  const { fetchTrades } = useTrades()
  const { fetchStats } = useStats()
  const { loading, setLoading } = useStore()
  
  const refreshAll = useCallback(async () => {
    try {
      setLoading(true)
      await Promise.all([
        fetchMarkets(),
        fetchSignals(),
        fetchTrades(),
        fetchStats()
      ])
    } catch (e) {
      console.error('Refresh error:', e)
    } finally {
      setLoading(false)
    }
  }, [])
  
  return { refreshAll, loading }
}
