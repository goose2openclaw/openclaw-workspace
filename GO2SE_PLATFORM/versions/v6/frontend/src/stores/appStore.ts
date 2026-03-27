/**
 * 🪿 GO2SE 状态管理 (Zustand)
 */

import { create } from 'zustand'

// Types
export interface MarketData {
  symbol: string
  price: number
  change_24h: number
  volume_24h: number
  rsi: number
  bid: number
  ask: number
}

export interface Signal {
  id: number
  strategy: string
  symbol: string
  signal: 'buy' | 'sell' | 'hold'
  confidence: number
  reason: string
  executed: boolean
  created_at: string
}

export interface Trade {
  id: number
  symbol: string
  side: string
  amount: number
  price: number
  status: string
  pnl: number
  strategy: string
  created_at: string
}

export interface Stats {
  total_trades: number
  open_trades: number
  total_signals: number
  executed_signals: number
  win_rate?: number
  total_pnl?: number
  trading_mode?: string
  max_position?: number
  stop_loss?: number
  take_profit?: number
}

interface AppState {
  // Data
  markets: MarketData[]
  signals: Signal[]
  trades: Trade[]
  stats: Stats | null
  
  // UI State
  theme: 'light' | 'dark'
  activeTab: 'market' | 'signals' | 'trades' | 'positions'
  loading: boolean
  wsConnected: boolean
  
  // Actions
  setMarkets: (markets: MarketData[]) => void
  setSignals: (signals: Signal[]) => void
  setTrades: (trades: Trade[]) => void
  setStats: (stats: Stats) => void
  setTheme: (theme: 'light' | 'dark') => void
  setActiveTab: (tab: 'market' | 'signals' | 'trades' | 'positions') => void
  setLoading: (loading: boolean) => void
  setWsConnected: (connected: boolean) => void
  
  // Computed
  buySignals: () => Signal[]
  sellSignals: () => Signal[]
}

export const useStore = create<AppState>((set, get) => ({
  // Initial State
  markets: [],
  signals: [],
  trades: [],
  stats: null,
  
  theme: 'dark',
  activeTab: 'market',
  loading: true,
  wsConnected: false,
  
  // Actions
  setMarkets: (markets) => set({ markets }),
  setSignals: (signals) => set({ signals }),
  setTrades: (trades) => set({ trades }),
  setStats: (stats) => set({ stats }),
  setTheme: (theme) => set({ theme }),
  setActiveTab: (activeTab) => set({ activeTab }),
  setLoading: (loading) => set({ loading }),
  setWsConnected: (wsConnected) => set({ wsConnected }),
  
  // Computed
  buySignals: () => get().signals.filter(s => s.signal === 'buy'),
  sellSignals: () => get().signals.filter(s => s.signal === 'sell'),
}))
