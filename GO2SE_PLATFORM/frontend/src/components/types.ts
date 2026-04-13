// Shared types for GO2SE components

export interface PortfolioStats {
  totalValue: number;
  dailyPnL: number;
  totalPnL: number;
  positions: number;
  winRate: number;
}

export interface MarketData {
  symbol: string;
  price: number;
  change24h: number;
  volume?: number;
}

export interface LayerScore {
  A: number;
  B: number;
  C: number;
  D: number;
  E: number;
}

export type Layer = 'A' | 'B' | 'C' | 'D' | 'E';

export interface Tool {
  id: string;
  name: string;
  emoji: string;
  position: number;
  stopLoss: number;
  takeProfit: number;
  status: 'active' | 'paused' | 'disabled';
  dailyPnL: number;
  totalPnL: number;
  trades: number;
}

export interface Signal {
  id: string;
  type: 'buy' | 'sell';
  symbol: string;
  strength: number;
  timestamp?: number;
}

export interface Performance {
  total_capital: number;
  investment_pool: number;
  work_pool: number;
  investment_tools: Record<string, InvestmentTool>;
  work_tools?: Record<string, WorkTool>;
  cashflow_pool?: number;
  daily_return?: number;
  total_return?: number;
}

export interface InvestmentTool {
  name: string;
  allocation: number;
  weight: number;
  color: string;
  status: 'active' | 'disabled';
}

export interface WorkTool {
  name: string;
  allocation: number;
  weight: number;
  color: string;
  cashflow_rate: number;
}

export interface AdaptiveDecision {
  summary: {
    action: string;
    direction: string;
    confidence: number;
  };
  tools?: Tool[];
  signals?: Signal[];
}
