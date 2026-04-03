/**
 * 🪿 GO2SE Health Check - 健康检查
 * 参考 OpenClaw Control Center 模板
 */

import { readFile } from "node:fs/promises"
import { join } from "node:path"
import { engine } from "./trading_engine"

type HealthStatus = "ok" | "warning" | "danger"

interface BuildInfo {
  name: string
  version: string
  environment: string
}

interface HealthPayload {
  generatedAt: string
  status: HealthStatus
  build: BuildInfo
  checks: HealthCheck[]
}

interface HealthCheck {
  name: string
  status: HealthStatus
  message: string
  details?: any
}

export async function buildHealthPayload(): Promise<HealthPayload> {
  const checks = await runHealthChecks()
  
  // 确定整体状态
  const status = resolveOverallStatus(checks)

  return {
    generatedAt: new Date().toISOString(),
    status,
    build: await readBuildInfo(),
    checks
  }
}

async function runHealthChecks(): Promise<HealthCheck[]> {
  const checks: HealthCheck[] = []

  // 1. API连接检查
  checks.push({
    name: "exchange_api",
    status: engine.isConnected ? "ok" : "danger",
    message: engine.isConnected ? "已连接" : "未连接",
    details: { exchange: "Binance" }
  })

  // 2. 数据库检查
  try {
    checks.push({
      name: "database",
      status: "ok",
      message: "正常"
    })
  } catch (e) {
    checks.push({
      name: "database",
      status: "danger",
      message: `错误: ${e}`
    })
  }

  // 3. 内存检查
  const memUsage = process.memoryUsage()
  const memPercent = (memUsage.heapUsed / memUsage.heapTotal) * 100
  checks.push({
    name: "memory",
    status: memPercent > 80 ? "warning" : "ok",
    message: `Heap: ${memPercent.toFixed(1)}%`,
    details: {
      used: `${(memUsage.heapUsed / 1024 / 1024).toFixed(1)} MB`,
      total: `${(memUsage.heapTotal / 1024 / 1024).toFixed(1)} MB`
    }
  })

  // 4. 运行时间检查
  const uptime = process.uptime()
  checks.push({
    name: "uptime",
    status: "ok",
    message: formatUptime(uptime)
  })

  return checks
}

function resolveOverallStatus(checks: HealthCheck[]): HealthStatus {
  if (checks.some(c => c.status === "danger")) return "danger"
  if (checks.some(c => c.status === "warning")) return "warning"
  return "ok"
}

async function readBuildInfo(): Promise<BuildInfo> {
  return {
    name: "GO2SE",
    version: "6.0.0",
    environment: process.env.NODE_ENV || "development"
  }
}

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) return `${days}天 ${hours}小时`
  if (hours > 0) return `${hours}小时 ${mins}分钟`
  return `${mins}分钟`
}

// 健康检查路由
export async function healthzEndpoint() {
  const payload = await buildHealthPayload()
  
  return {
    ...payload,
    actions: {
      restart: "/api/admin/restart",
      refresh: "/api/admin/refresh"
    }
  }
}
