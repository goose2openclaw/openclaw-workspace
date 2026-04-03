/**
 * 🪿 GO2SE Notification Center - 通知中心
 * 参考 OpenClaw Control Center 模板
 */

import { appendFile, mkdir } from "node:fs/promises"
import { join } from "node:path"

type NotificationLevel = "info" | "success" | "warning" | "danger"

interface Notification {
  id: string
  level: NotificationLevel
  title: string
  message: string
  timestamp: string
  read: boolean
  action?: {
    label: string
    url: string
  }
}

const RUNTIME_DIR = join(process.cwd(), "runtime")
const NOTIFICATIONS_LOG = join(RUNTIME_DIR, "notifications.log")

// 内存中的通知存储
let notifications: Notification[] = []
let notificationId = 0

export async function addNotification(
  level: NotificationLevel,
  title: string,
  message: string,
  action?: { label: string; url: string }
): Promise<Notification> {
  const notification: Notification = {
    id: `notif-${++notificationId}`,
    level,
    title,
    message,
    timestamp: new Date().toISOString(),
    read: false,
    action
  }

  notifications.unshift(notification)
  
  // 只保留最近100条
  if (notifications.length > 100) {
    notifications = notifications.slice(0, 100)
  }

  // 写入日志
  await logNotification(notification)

  return notification
}

async function logNotification(notif: Notification): Promise<void> {
  try {
    await mkdir(RUNTIME_DIR, { recursive: true })
    await appendFile(
      NOTIFICATIONS_LOG,
      `${notif.timestamp} | [${notif.level.toUpperCase()}] ${notif.title}: ${notif.message}\n`,
      "utf8"
    )
  } catch (e) {
    console.error("[notification] log error:", e)
  }
}

export function getNotifications(options?: {
  limit?: number
  unreadOnly?: boolean
  level?: NotificationLevel
}): Notification[] {
  let result = [...notifications]

  if (options?.unreadOnly) {
    result = result.filter(n => !n.read)
  }

  if (options?.level) {
    result = result.filter(n => n.level === options.level)
  }

  if (options?.limit) {
    result = result.slice(0, options.limit)
  }

  return result
}

export function markAsRead(id: string): void {
  const notif = notifications.find(n => n.id === id)
  if (notif) {
    notif.read = true
  }
}

export function markAllAsRead(): void {
  notifications.forEach(n => n.read = true)
}

export function clearNotifications(): void {
  notifications = []
}

// 便捷方法
export const notify = {
  info: (title: string, message: string) => addNotification("info", title, message),
  success: (title: string, message: string) => addNotification("success", title, message),
  warning: (title: string, message: string) => addNotification("warning", title, message),
  danger: (title: string, message: string) => addNotification("danger", title, message),
  
  trade: (symbol: string, side: string, pnl: number) => 
    addNotification(
      pnl > 0 ? "success" : "danger",
      `交易${side === 'buy' ? '买入' : '卖出'}`,
      `${symbol} ${pnl > 0 ? '盈利' : '亏损'} ${Math.abs(pnl).toFixed(2)} USDT`
    ),
  
  signal: (count: number) => 
    addNotification(
      count > 5 ? "warning" : "info",
      "新信号",
      `发现 ${count} 个交易信号`
    ),
    
  risk: (message: string) => 
    addNotification("danger", "风控告警", message),
    
  error: (error: string) => 
    addNotification("danger", "系统错误", error)
}

// 通知模板
export const NotificationTemplates = {
  tradeExecuted: (symbol: string, side: string, amount: number, price: number) => ({
    title: "交易执行",
    message: `${side.toUpperCase()} ${amount} ${symbol} @ $${price}`,
    level: "success" as NotificationLevel
  }),
  
  signalGenerated: (strategy: string, symbol: string, confidence: number) => ({
    title: "信号生成",
    message: `${strategy}: ${symbol} 置信度 ${confidence.toFixed(1)}`,
    level: confidence >= 7 ? "success" as NotificationLevel : "info" as NotificationLevel
  }),
  
  riskTriggered: (rule: string, value: number, threshold: number) => ({
    title: "风控触发",
    message: `${rule}: ${value.toFixed(1)}% > ${threshold.toFixed(1)}%`,
    level: "danger" as NotificationLevel
  }),
  
  dailySummary: (trades: number, pnl: number) => ({
    title: "日终报告",
    message: `完成 ${trades} 笔交易，盈亏 ${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)} USDT`,
    level: pnl >= 0 ? "success" as NotificationLevel : "warning" as NotificationLevel
  })
}
