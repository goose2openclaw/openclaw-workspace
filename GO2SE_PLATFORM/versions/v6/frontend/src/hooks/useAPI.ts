/**
 * 🪿 GO2SE API Hooks
 */

import { useCallback } from 'react'
import { useStore, MarketData, Signal, Trade, Stats } from '../stores/appStore'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// 通用请求
async function fetchAPI<T>(endpoint: string): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`)
  if (!res.ok) throw new Error(`API Error: ${res.status}`)
  const data = await res.json()
  return data.data || data
}

// Hooks
export function useMarketData() {
  const { markets, setMarkets, loading, setLoading } = useStore()
  
  const fetchMarkets = useCallback(async () => {
    try {
      const data = await fetchAPI<MarketData[]>('/api/market')
      setMarkets(data)
    } catch (e) {
      console.error('Fetch markets error:', e)
    }
  }, [setMarkets])
  
  return { markets, fetchMarkets, loading }
}

export function useSignals() {
  const { signals, setSignals, setLoading } = useStore()
  
  const fetchSignals = useCallback(async (limit = 50) => {
    try {
      const data = await fetchAPI<Signal[]>(`/api/signals?limit=${limit}`)
      setSignals(data)
    } catch (e) {
      console.error('Fetch signals error:', e)
    }
  }, [setSignals])
  
  const runStrategy = useCallback(async (strategy: string) => {
    const res = await fetch(`${API_BASE}/api/signals/${strategy}/run`, { method: 'POST' })
    return res.json()
  }, [])
  
  return { signals, fetchSignals, runStrategy }
}

export function useTrades() {
  const { trades, setTrades } = useStore()
  
  const fetchTrades = useCallback(async (limit = 50) => {
    try {
      const data = await fetchAPI<Trade[]>(`/api/trades?limit=${limit}`)
      setTrades(data)
    } catch (e) {
      console.error('Fetch trades error:', e)
    }
  }, [setTrades])
  
  return { trades, fetchTrades }
}

export function useStats() {
  const { stats, setStats } = useStore()
  
  const fetchStats = useCallback(async () => {
    try {
      const data = await fetchAPI<Stats>('/api/stats')
      setStats(data)
    } catch (e) {
      console.error('Fetch stats error:', e)
    }
  }, [setStats])
  
  return { stats, fetchStats }
}

export function useWebSocket() {
  const { wsConnected, setWsConnected, setMarkets, setSignals } = useStore()
  
  const connect = useCallback(() => {
    const ws = new WebSocket(`ws://${window.location.hostname}:5000/ws`)
    
    ws.onopen = () => {
      console.log('🔌 WS Connected')
      setWsConnected(true)
    }
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      
      switch (message.type) {
        case 'market':
          setMarkets(message.data)
          break
        case 'signal':
          setSignals([message.data, ...useStore.getState().signals])
          break
      }
    }
    
    ws.onclose = () => {
      console.log('🔌 WS Disconnected')
      setWsConnected(false)
    }
    
    ws.onerror = (e) => {
      console.error('WS Error:', e)
    }
    
    return ws
  }, [setWsConnected, setMarkets, setSignals])
  
  return { wsConnected, connect }
}

// 自动刷新Hook
export function useAutoRefresh(interval = 10000) {
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
