/**
 * 🪿 GO2SE Monitor - 监控核心
 * 参考 OpenClaw Control Center 模板
 */

import { appendFile, mkdir } from "node:fs/promises"
import { join } from "node:path"
import { engine } from "./trading_engine"
import { getDb } from "./database"
import { Signal, Trade, Position } from "../models/models"

const RUNTIME_DIR = join(process.cwd(), "runtime")
const TIMELINE_LOG = join(RUNTIME_DIR, "timeline.log")
const MONITOR_LOG = join(RUNTIME_DIR, "monitor.log")

interface MonitorSnapshot {
  timestamp: string
  markets: any[]
  signals: any[]
  trades: any[]
  positions: any[]
  stats: any
}

interface MonitorAlerts {
  level: 'info' | 'warning' | 'danger'
  message: string
  details?: any
}

export async function runMonitorOnce(): Promise<void> {
  const db = getDb()
  
  // 获取快照数据
  const snapshot: MonitorSnapshot = {
    timestamp: new Date().toISOString(),
    markets: [], // 从交易引擎获取
    signals: db.query(Signal).all(),
    trades: db.query(Trade).all(),
    positions: db.query(Position).filter(Position.amount > 0).all(),
    stats: await computeStats(db)
  }

  // 生成告警
  const alerts = generateAlerts(snapshot)

  // 记录日志
  await mkdir(RUNTIME_DIR, { recursive: true })
  await appendFile(
    MONITOR_LOG,
    `${new Date().toISOString()} | signals=${snapshot.signals.length} | trades=${snapshot.trades.length} | alerts=${alerts.length}\n`,
    "utf8"
  )

  // 更新数据库
  await saveMonitorSnapshot(snapshot)

  console.log("[go2se-monitor]", {
    timestamp: snapshot.timestamp,
    signals: snapshot.signals.length,
    trades: snapshot.trades.length,
    positions: snapshot.positions.length,
    alerts: alerts.map(a => a.message)
  })

  return snapshot
}

function generateAlerts(snapshot: MonitorSnapshot): MonitorAlerts[] {
  const alerts: MonitorAlerts[] = []
  
  // 1. 仓位检查
  const totalPosition = snapshot.positions.reduce((acc, p) => acc + p.amount, 0)
  if (totalPosition > 0.8) {
    alerts.push({
      level: 'danger',
      message: '仓位超过80%'
    })
  }

  // 2. 日内亏损检查
  const todayTrades = snapshot.trades.filter(t => {
    const tradeDate = new Date(t.created_at).toDateString()
    return tradeDate === new Date().toDateString()
  })
  const todayPnl = todayTrades.reduce((acc, t) => acc + (t.pnl || 0), 0)
  if (todayPnl < -0.3) {
    alerts.push({
      level: 'danger',
      message: '日内亏损超过30%'
    })
  }

  // 3. 信号过多
  const buySignals = snapshot.signals.filter(s => s.signal === 'buy')
  if (buySignals.length > 10) {
    alerts.push({
      level: 'warning',
      message: `买入信号过多: ${buySignals.length}个`
    })
  }

  // 4. API连接检查
  if (!engine.isConnected) {
    alerts.push({
      level: 'danger',
      message: '交易所API未连接'
    })
  }

  return alerts
}

async function computeStats(db: any): Promise<any> {
  const totalTrades = db.query(Trade).count()
  const openTrades = db.query(Trade).filter(Trade.status === 'open').count()
  const totalSignals = db.query(Signal).count()
  const executedSignals = db.query(Signal).filter(Signal.executed === true).count()

  return {
    total_trades: totalTrades,
    open_trades: openTrades,
    total_signals: totalSignals,
    executed_signals: executedSignals,
    execution_rate: totalSignals > 0 ? (executedSignals / totalSignals * 100).toFixed(1) : 0
  }
}

async function saveMonitorSnapshot(snapshot: MonitorSnapshot): Promise<void> {
  // 保存到监控日志
  const db = getDb()
  
  // 更新最新统计
  const { stats } = snapshot
  // 可以添加更多监控数据存储逻辑
}

export function monitorIntervalMs(): number {
  return 30000 // 30秒
}
