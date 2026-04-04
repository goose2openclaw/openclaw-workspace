<template>
  <div class="engineering-page">
    <h1 class="page-title">🔧 工程模式</h1>

    <!-- 子导航 -->
    <div class="sub-nav">
      <button v-for="tab in tabs" :key="tab.id" 
              class="sub-nav-btn" 
              :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id">
        {{ tab.label }}
      </button>
    </div>

    <!-- N1: AI Debug -->
    <div v-if="activeTab === 'n1'" class="tab-content">
      <div class="debug-header">
        <h2>🤖 AI 自动Debug</h2>
        <p>基于MiroFish仿真和自我诊断的自主迭代系统</p>
      </div>

      <div class="debug-grid">
        <!-- 问题输入 -->
        <div class="debug-panel">
          <h3>📝 问题描述</h3>
          <textarea v-model="debugProblem" 
                    class="debug-input" 
                    placeholder="描述你遇到的问题..."
                    rows="6"></textarea>
          <div class="debug-options">
            <label class="option-item">
              <input type="checkbox" v-model="useMirofish" />
              <span>启用MiroFish仿真</span>
            </label>
            <label class="option-item">
              <input type="checkbox" v-model="autoDiagnose" />
              <span>自动诊断</span>
            </label>
            <label class="option-item">
              <input type="checkbox" v-model="selfHeal" />
              <span>自我修复</span>
            </label>
          </div>
          <button class="btn btn-primary" @click="startDebug">
            🔍 开始分析
          </button>
        </div>

        <!-- 分析结果 -->
        <div class="debug-panel">
          <h3>🔬 分析结果</h3>
          <div v-if="!debugResult" class="empty-state">
            <span class="empty-icon">🤖</span>
            <p>等待问题输入...</p>
          </div>
          <div v-else class="debug-result">
            <div class="result-section">
              <h4>问题诊断</h4>
              <div class="result-item" v-for="(item, i) in debugResult.diagnosis" :key="i">
                <span class="result-icon">{{ item.icon }}</span>
                <span>{{ item.text }}</span>
              </div>
            </div>
            <div class="result-section">
              <h4>修复建议</h4>
              <div class="result-item" v-for="(item, i) in debugResult.fixes" :key="i">
                <span class="result-icon">{{ item.icon }}</span>
                <span>{{ item.text }}</span>
              </div>
            </div>
            <div class="result-section">
              <h4>自我迭代</h4>
              <div class="iteration-status">
                <span class="status-badge" :class="debugResult.status">{{ debugResult.statusText }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 诊断历史 -->
      <div class="debug-history">
        <h3>📜 诊断历史</h3>
        <table class="history-table">
          <thead>
            <tr>
              <th>时间</th>
              <th>问题</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in debugHistory" :key="item.id">
              <td>{{ item.time }}</td>
              <td>{{ item.problem }}</td>
              <td><span class="status-badge" :class="item.status">{{ item.statusText }}</span></td>
              <td><button class="btn-sm" @click="viewDebug(item)">查看</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- N2: 终端Termux -->
    <div v-if="activeTab === 'n2'" class="tab-content">
      <div class="terminal-container">
        <div class="terminal-header">
          <span class="terminal-title">🖥️ Terminal</span>
          <div class="terminal-actions">
            <button class="term-btn" @click="clearTerminal">清除</button>
            <button class="term-btn" @click="downloadLogs">导出日志</button>
          </div>
        </div>
        <div class="terminal-output" ref="terminalOutput">
          <div v-for="(line, i) in terminalLines" :key="i" class="terminal-line" :class="line.type">
            <span class="line-prompt" v-if="line.type === 'input'">$</span>
            <span class="line-content">{{ line.text }}</span>
          </div>
        </div>
        <div class="terminal-input-row">
          <span class="prompt">$</span>
          <input v-model="terminalInput" 
                 class="terminal-input" 
                 placeholder="输入命令..."
                 @keyup.enter="executeCommand" />
        </div>
      </div>

      <div class="quick-commands">
        <h3>⚡ 快捷命令</h3>
        <div class="command-grid">
          <button v-for="cmd in quickCommands" :key="cmd.name" 
                  class="command-btn" 
                  @click="runQuickCommand(cmd.cmd)">
            <span class="cmd-icon">{{ cmd.icon }}</span>
            <span class="cmd-name">{{ cmd.name }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- N3: 数据指令通道 -->
    <div v-if="activeTab === 'n3'" class="tab-content">
      <div class="channel-header">
        <h2>📡 数据指令通道</h2>
        <p>双向数据通道 - OpenClaw ↔ Claude Codex</p>
      </div>

      <div class="channel-grid">
        <!-- 发送通道 -->
        <div class="channel-panel">
          <h3>📤 发送指令</h3>
          <div class="channel-form">
            <div class="form-group">
              <label>目标</label>
              <select v-model="channelTarget">
                <option value="openclaw">OpenClaw</option>
                <option value="codex">Claude Codex</option>
                <option value="both">两者</option>
              </select>
            </div>
            <div class="form-group">
              <label>指令类型</label>
              <select v-model="channelType">
                <option value="query">查询</option>
                <option value="command">命令</option>
                <option value="config">配置</option>
                <option value="debug">调试</option>
              </select>
            </div>
            <div class="form-group">
              <label>指令内容</label>
              <textarea v-model="channelContent" rows="4" placeholder="输入指令..."></textarea>
            </div>
            <button class="btn btn-primary" @click="sendChannelCommand">
              🚀 发送指令
            </button>
          </div>
        </div>

        <!-- 接收通道 -->
        <div class="channel-panel">
          <h3>📥 接收数据</h3>
          <div class="channel-log">
            <div v-for="(msg, i) in channelMessages" :key="i" class="message-item" :class="msg.direction">
              <div class="msg-header">
                <span class="msg-direction">{{ msg.direction === 'in' ? '⬅️' : '➡️' }}</span>
                <span class="msg-source">{{ msg.source }}</span>
                <span class="msg-time">{{ msg.time }}</span>
              </div>
              <div class="msg-content">{{ msg.content }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 通道状态 -->
      <div class="channel-status">
        <h3>📊 通道状态</h3>
        <div class="status-grid">
          <div class="status-item">
            <span class="status-name">OpenClaw</span>
            <span class="status-indicator online">在线</span>
          </div>
          <div class="status-item">
            <span class="status-name">Claude Codex</span>
            <span class="status-indicator online">在线</span>
          </div>
          <div class="status-item">
            <span class="status-name">延迟</span>
            <span class="status-value">12ms</span>
          </div>
          <div class="status-item">
            <span class="status-name">消息数</span>
            <span class="status-value">1,234</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'

export default {
  name: 'Engineering',
  setup() {
    const activeTab = ref('n1')
    const tabs = [
      { id: 'n1', label: 'n1 AI Debug' },
      { id: 'n2', label: 'n2 终端Termux' },
      { id: 'n3', label: 'n3 指令通道' },
    ]

    // N1: AI Debug
    const debugProblem = ref('')
    const useMirofish = ref(true)
    const autoDiagnose = ref(true)
    const selfHeal = ref(false)

    const debugResult = ref(null)

    const debugHistory = ref([
      { id: 1, time: '10:30', problem: 'API响应超时', status: 'fixed', statusText: '已修复' },
      { id: 2, time: '09:45', problem: '数据库连接失败', status: 'analyzing', statusText: '分析中' },
      { id: 3, time: '昨天', problem: '内存泄漏', status: 'fixed', statusText: '已修复' },
    ])

    const startDebug = () => {
      debugResult.value = {
        diagnosis: [
          { icon: '🔍', text: '检测到API响应时间超过阈值' },
          { icon: '📊', text: '负载测试显示并发能力不足' },
          { icon: '⚠️', text: '缺少连接池管理' },
        ],
        fixes: [
          { icon: '🔧', text: '增加连接池大小至50' },
          { icon: '⚡', text: '启用请求缓存' },
          { icon: '📈', text: '配置自动扩容' },
        ],
        status: 'analyzing',
        statusText: '分析中...',
      }
    }

    const viewDebug = (item) => {}

    // N2: Terminal
    const terminalLines = ref([
      { type: 'system', text: 'Terminal已就绪 - GO2SE v9.3' },
      { type: 'output', text: 'Last login: Sat Apr  4 03:46:00 on ttys001' },
    ])
    const terminalInput = ref('')
    const terminalOutput = ref(null)

    const quickCommands = [
      { name: '系统状态', icon: '📊', cmd: 'openclaw status' },
      { name: '健康检查', icon: '💚', cmd: 'curl localhost:8004/api/stats' },
      { name: '进程列表', icon: '📋', cmd: 'ps aux | grep uvicorn' },
      { name: '磁盘使用', icon: '💾', cmd: 'df -h' },
      { name: '内存状态', icon: '🧠', cmd: 'free -h' },
      { name: '日志查看', icon: '📜', cmd: 'tail -20 go2se.log' },
    ]

    const executeCommand = () => {
      if (!terminalInput.value.trim()) return
      terminalLines.value.push({ type: 'input', text: terminalInput.value })
      // 模拟执行
      terminalLines.value.push({ type: 'output', text: `执行: ${terminalInput.value}` })
      terminalInput.value = ''
    }

    const runQuickCommand = (cmd) => {
      terminalInput.value = cmd
      executeCommand()
    }

    const clearTerminal = () => {
      terminalLines.value = [{ type: 'system', text: 'Terminal已清除' }]
    }

    const downloadLogs = () => {}

    // N3: 数据指令通道
    const channelTarget = ref('both')
    const channelType = ref('query')
    const channelContent = ref('')
    const channelMessages = ref([
      { direction: 'in', source: 'OpenClaw', time: '10:30', content: '系统状态: 正常' },
      { direction: 'out', source: 'Claude Codex', time: '10:29', content: '执行命令: status check' },
      { direction: 'in', source: 'OpenClaw', time: '10:28', content: '健康检查: 通过' },
    ])

    const sendChannelCommand = () => {
      if (!channelContent.value.trim()) return
      channelMessages.value.push({
        direction: 'out',
        source: 'Me',
        time: new Date().toLocaleTimeString(),
        content: channelContent.value,
      })
      channelContent.value = ''
    }

    return {
      activeTab,
      tabs,
      // N1
      debugProblem,
      useMirofish,
      autoDiagnose,
      selfHeal,
      debugResult,
      debugHistory,
      startDebug,
      viewDebug,
      // N2
      terminalLines,
      terminalInput,
      terminalOutput,
      quickCommands,
      executeCommand,
      runQuickCommand,
      clearTerminal,
      downloadLogs,
      // N3
      channelTarget,
      channelType,
      channelContent,
      channelMessages,
      sendChannelCommand,
    }
  },
}
</script>

<style scoped>
.engineering-page { @apply pb-8; }
.page-title { @apply text-2xl font-bold mb-6; }

.sub-nav { @apply flex gap-2 mb-6 p-1 bg-[var(--bg-card)] rounded-xl; }
.sub-nav-btn {
  @apply flex-1 px-4 py-2 rounded-lg text-sm font-medium cursor-pointer transition-all;
  background: transparent;
  color: var(--text-secondary);
}
.sub-nav-btn:hover { @apply text-[var(--text-primary)] bg-[var(--bg-elevated)]; }
.sub-nav-btn.active { @apply text-[var(--accent-primary)] bg-[rgba(0,245,212,0.1)]; }

.tab-content { @apply animate-fadeIn; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Debug */
.debug-header { @apply mb-6; }
.debug-header h2 { @apply text-xl font-bold mb-2; }
.debug-header p { @apply text-sm text-[var(--text-secondary)]; }

.debug-grid { @apply grid grid-cols-2 gap-4 mb-6; }
.debug-panel { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4; }
.debug-panel h3 { @apply text-sm font-semibold mb-4 text-[var(--accent-primary)]; }

.debug-input {
  @apply w-full bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded-lg p-3 text-sm resize-none;
  color: var(--text-primary);
}

.debug-options { @apply flex gap-4 my-4; }
.option-item { @apply flex items-center gap-2 cursor-pointer text-sm; }

.btn { @apply px-4 py-2 rounded-lg font-semibold cursor-pointer transition-all inline-flex items-center gap-2 border-none; }
.btn-primary { background: linear-gradient(135deg, var(--accent-primary), #00b8a3); color: var(--bg-primary); }

.empty-state { @apply flex flex-col items-center justify-center py-12 text-[var(--text-muted)]; }
.empty-icon { @apply text-4xl mb-2; }

.debug-result { @apply space-y-4; }
.result-section h4 { @apply text-sm font-semibold mb-2 text-[var(--text-secondary)]; }
.result-item { @apply flex items-center gap-2 py-1; }
.result-icon { @apply text-lg; }

.iteration-status { @apply mt-2; }
.status-badge { @apply px-3 py-1 rounded-full text-sm; }
.status-badge.fixed { @apply bg-[rgba(0,245,160,0.15)] text-[var(--success)]; }
.status-badge.analyzing { @apply bg-[rgba(255,212,59,0.15)] text-[var(--warning)]; }
.status-badge.error { @apply bg-[rgba(255,71,87,0.15)] text-[var(--danger)]; }

.history-table { @apply w-full bg-[var(--bg-card)] rounded-xl overflow-hidden; }
.history-table th { @apply text-left px-4 py-3 text-xs text-[var(--text-muted)] uppercase bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)]; }
.history-table td { @apply px-4 py-3 border-b border-[var(--border-subtle)]; }

.btn-sm { @apply px-2 py-1 rounded text-xs bg-[var(--bg-elevated)] cursor-pointer; }

/* Terminal */
.terminal-container { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl overflow-hidden mb-6; }
.terminal-header { @apply flex justify-between items-center px-4 py-2 bg-[var(--bg-elevated)] border-b border-[var(--border-subtle)]; }
.terminal-title { @apply text-sm font-semibold; }
.terminal-actions { @apply flex gap-2; }
.term-btn { @apply px-2 py-1 rounded text-xs bg-[var(--bg-secondary)] cursor-pointer; }

.terminal-output { @apply h-80 overflow-y-auto p-4 font-mono text-sm; }
.terminal-line { @apply flex items-start gap-2 py-0.5; }
.terminal-line.input { @apply text-[var(--accent-primary)]; }
.terminal-line.output { @apply text-[var(--text-secondary)]; }
.terminal-line.system { @apply text-[var(--text-muted)]; }
.line-prompt { @apply font-bold; }
.line-content { @apply whitespace-pre-wrap; }

.terminal-input-row { @apply flex items-center gap-2 px-4 py-2 bg-[var(--bg-elevated)] border-t border-[var(--border-subtle)]; }
.prompt { @apply font-mono text-[var(--accent-primary)]; }
.terminal-input {
  @apply flex-1 bg-transparent border-none outline-none font-mono text-sm;
  color: var(--text-primary);
}

.quick-commands h3 { @apply text-sm font-semibold mb-4; }
.command-grid { @apply grid grid-cols-6 gap-3; }
.command-btn { @apply flex flex-col items-center gap-2 p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] cursor-pointer transition-all hover:border-[var(--accent-primary)]; }
.cmd-icon { @apply text-2xl; }
.cmd-name { @apply text-xs text-[var(--text-secondary)]; }

/* Channel */
.channel-header { @apply mb-6; }
.channel-header h2 { @apply text-xl font-bold mb-2; }
.channel-header p { @apply text-sm text-[var(--text-secondary)]; }

.channel-grid { @apply grid grid-cols-2 gap-4 mb-6; }
.channel-panel { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4; }
.channel-panel h3 { @apply text-sm font-semibold mb-4 text-[var(--accent-primary)]; }

.channel-form { @apply space-y-4; }
.form-group { @apply space-y-1; }
.form-group label { @apply text-xs text-[var(--text-secondary)]; }
.form-group select,
.form-group textarea {
  @apply w-full bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded-lg p-2 text-sm;
  color: var(--text-primary);
}

.channel-log { @apply max-h-60 overflow-y-auto space-y-2; }
.message-item { @apply bg-[var(--bg-elevated)] rounded-lg p-3; }
.message-item.in { @apply border-l-2 border-[var(--accent-primary)]; }
.message-item.out { @apply border-l-2 border-[var(--accent-secondary)]; }
.msg-header { @apply flex items-center gap-2 text-xs text-[var(--text-muted)] mb-1; }
.msg-content { @apply text-sm; }

.channel-status h3 { @apply text-sm font-semibold mb-4; }
.status-grid { @apply grid grid-cols-4 gap-3; }
.status-item { @apply flex justify-between items-center bg-[var(--bg-card)] rounded-lg p-3; }
.status-name { @apply text-sm text-[var(--text-secondary)]; }
.status-indicator { @apply text-xs px-2 py-0.5 rounded-full; }
.status-indicator.online { @apply bg-[rgba(0,245,160,0.15)] text-[var(--success)]; }
.status-value { @apply font-mono text-sm; }
</style>
