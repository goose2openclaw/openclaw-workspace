<template>
  <div class="assets-page">
    <h1 class="page-title">💰 资产看板</h1>

    <!-- 子导航 -->
    <div class="sub-nav">
      <button v-for="tab in tabs" :key="tab.id" 
              class="sub-nav-btn" 
              :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id">
        {{ tab.label }}
      </button>
    </div>

    <!-- C1: 财产总额 -->
    <div v-if="activeTab === 'c1'" class="tab-content">
      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-label">总资产 (USDT)</div>
          <div class="stat-value">$12,345.67</div>
          <div class="stat-change positive">+23.4% ↑</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">投资部分</div>
          <div class="stat-value">$10,000</div>
          <div class="stat-change positive">+15.2%</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">打工部分</div>
          <div class="stat-value">$2,345.67</div>
          <div class="stat-change positive">+$567.8</div>
        </div>
      </div>

      <!-- 资产趋势图 -->
      <div class="chart-container">
        <h3>资产趋势</h3>
        <div class="chart-placeholder">
          <div class="chart-line"></div>
        </div>
      </div>
    </div>

    <!-- C2: 收益详情 -->
    <div v-if="activeTab === 'c2'" class="tab-content">
      <div class="income-section">
        <h3>💹 投资收益</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>工具</th>
              <th>仓位</th>
              <th>收益</th>
              <th>收益率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in investIncome" :key="item.tool">
              <td>{{ item.tool }}</td>
              <td class="mono">${{ item.position }}</td>
              <td class="mono positive">+${{ item.profit }}</td>
              <td class="mono" :class="item.rate >= 0 ? 'positive' : 'negative'">
                {{ item.rate >= 0 ? '+' : '' }}{{ item.rate }}%
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="income-section">
        <h3>💼 打工收益</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>类型</th>
              <th>收益</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in workIncome" :key="item.type">
              <td>{{ item.type }}</td>
              <td class="mono positive">+${{ item.profit }}</td>
              <td><span class="status-badge success">{{ item.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- C3: 钱包架构 -->
    <div v-if="activeTab === 'c3'" class="tab-content">
      <div class="wallet-diagram">
        <div class="wallet-node main">
          <div class="node-icon">🏦</div>
          <div class="node-label">主钱包</div>
          <div class="node-amount">$10,000</div>
          <div class="node-status connected">已连接</div>
        </div>
        
        <div class="wallet-connections">
          <div class="connection-line"></div>
          <div class="connection-line"></div>
          <div class="connection-line"></div>
        </div>

        <div class="wallet-children">
          <div class="wallet-node sub">
            <div class="node-icon">🐰</div>
            <div class="node-label">打兔子</div>
            <div class="node-amount">$2,500</div>
          </div>
          <div class="wallet-node sub">
            <div class="node-icon">🐹</div>
            <div class="node-label">打地鼠</div>
            <div class="node-amount">$3,000</div>
          </div>
          <div class="wallet-node sub">
            <div class="node-icon">🔮</div>
            <div class="node-label">走着瞧</div>
            <div class="node-amount">$1,500</div>
          </div>
          <div class="wallet-node sub">
            <div class="node-icon">💰</div>
            <div class="node-label">薅羊毛</div>
            <div class="node-amount">$500</div>
          </div>
        </div>
      </div>
    </div>

    <!-- C4: 资产分配 -->
    <div v-if="activeTab === 'c4'" class="tab-content">
      <div class="allocation-section">
        <h3>📊 投资部分</h3>
        <div class="allocation-grid">
          <div v-for="tool in investTools" :key="tool.name" class="allocation-card">
            <div class="tool-header">
              <span class="tool-icon">{{ tool.icon }}</span>
              <span class="tool-name">{{ tool.name }}</span>
            </div>
            <div class="tool-allocation">
              <div class="allocation-bar">
                <div class="allocation-fill" :style="{ width: tool.percent + '%' }"></div>
              </div>
              <span class="allocation-percent">{{ tool.percent }}%</span>
            </div>
            <div class="tool-amount">${{ tool.amount }}</div>
          </div>
        </div>
      </div>

      <div class="allocation-section">
        <h3>💼 打工部分</h3>
        <div class="allocation-grid">
          <div class="allocation-card">
            <div class="tool-header">
              <span class="tool-icon">💰</span>
              <span class="tool-name">薅羊毛</span>
            </div>
            <div class="allocation-bar">
              <div class="allocation-fill" style="width: 60%"></div>
            </div>
            <span class="allocation-percent">3%</span>
          </div>
          <div class="allocation-card">
            <div class="tool-header">
              <span class="tool-icon">👶</span>
              <span class="tool-name">穷孩子</span>
            </div>
            <div class="allocation-bar">
              <div class="allocation-fill" style="width: 40%"></div>
            </div>
            <span class="allocation-percent">2%</span>
          </div>
        </div>
      </div>

      <div class="allocation-section">
        <h3>🔒 保证金</h3>
        <div class="margin-info">
          <div class="margin-item">
            <span>跟大哥保证金:</span>
            <span class="mono">$500</span>
          </div>
          <div class="margin-item">
            <span>搭便车保证金:</span>
            <span class="mono">$300</span>
          </div>
        </div>
      </div>

      <div class="allocation-section">
        <h3>📥 暂存平台</h3>
        <div class="platform-options">
          <label class="platform-option">
            <input type="radio" name="platform" value="riskfree" />
            <span>无风险套利</span>
          </label>
          <label class="platform-option">
            <input type="radio" name="platform" value="guaranteed" />
            <span>保本套利</span>
          </label>
        </div>
      </div>
    </div>

    <!-- C5: 模拟器 -->
    <div v-if="activeTab === 'c5'" class="tab-content">
      <div class="simulator-tabs">
        <button class="sim-btn" :class="{ active: simTab === 'backtest' }" @click="simTab = 'backtest'">回测交易</button>
        <button class="sim-btn" :class="{ active: simTab === 'paper' }" @click="simTab = 'paper'">模拟交易</button>
        <button class="sim-btn" :class="{ active: simTab === 'simulation' }" @click="simTab = 'simulation'">全向仿真</button>
      </div>

      <div class="simulator-content">
        <div v-if="simTab === 'backtest'" class="sim-panel">
          <h3>📊 回测交易</h3>
          <p>基于历史数据进行策略回测</p>
          <div class="sim-result">
            <div class="result-item">
              <span>胜率:</span>
              <span class="mono positive">72.5%</span>
            </div>
            <div class="result-item">
              <span>收益:</span>
              <span class="mono positive">+23.4%</span>
            </div>
          </div>
        </div>

        <div v-if="simTab === 'paper'" class="sim-panel">
          <h3>📝 模拟交易</h3>
          <p>使用模拟资金进行实时交易</p>
          <button class="btn btn-primary">开始模拟</button>
        </div>

        <div v-if="simTab === 'simulation'" class="sim-panel">
          <h3>🔮 全向仿真</h3>
          <p>预测未来不同时段的资产表现</p>
          <div class="sim-config">
            <div class="config-item">
              <label>时间段:</label>
              <select v-model="simPeriod">
                <option value="1d">1天后</option>
                <option value="1w">1周后</option>
                <option value="1m">1月后</option>
              </select>
            </div>
          </div>
          <div class="sim-recommend">
            <h4>推荐配置</h4>
            <div class="recommend-item">
              <span>打兔子:</span>
              <span>40%</span>
            </div>
            <div class="recommend-item">
              <span>打地鼠:</span>
              <span>30%</span>
            </div>
            <div class="recommend-item">
              <span>走着瞧:</span>
              <span>20%</span>
            </div>
            <button class="btn btn-outline" @click="applyConfig">应用配置</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'Assets',
  setup() {
    const activeTab = ref('c1')
    const simTab = ref('backtest')
    const simPeriod = ref('1m')

    const tabs = [
      { id: 'c1', label: 'c1 财产总额' },
      { id: 'c2', label: 'c2 收益详情' },
      { id: 'c3', label: 'c3 钱包架构' },
      { id: 'c4', label: 'c4 资产分配' },
      { id: 'c5', label: 'c5 模拟器' },
    ]

    const investIncome = [
      { tool: '🐰 打兔子', position: '2500', profit: '234.5', rate: 9.4 },
      { tool: '🐹 打地鼠', position: '3000', profit: '456.7', rate: 15.2 },
      { tool: '🔮 走着瞧', position: '1500', profit: '123.4', rate: 8.2 },
      { tool: '👑 跟大哥', position: '1500', profit: '89.0', rate: 5.9 },
      { tool: '🍀 搭便车', position: '1000', profit: '67.8', rate: 6.8 },
    ]

    const workIncome = [
      { type: '💰 薅羊毛', profit: '23.5', status: '已到账' },
      { type: '👶 穷孩子', profit: '12.3', status: '处理中' },
    ]

    const investTools = [
      { name: '打兔子', icon: '🐰', percent: 25, amount: '2500' },
      { name: '打地鼠', icon: '🐹', percent: 20, amount: '3000' },
      { name: '走着瞧', icon: '🔮', percent: 15, amount: '1500' },
      { name: '跟大哥', icon: '👑', percent: 15, amount: '1500' },
      { name: '搭便车', icon: '🍀', percent: 10, amount: '1000' },
    ]

    const applyConfig = () => {
      // 应用推荐配置
    }

    return {
      activeTab,
      simTab,
      simPeriod,
      tabs,
      investIncome,
      workIncome,
      investTools,
      applyConfig,
    }
  },
}
</script>

<style scoped>
.assets-page { @apply pb-8; }

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

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.stats-grid { @apply grid grid-cols-3 gap-4 mb-6; }

.stat-card {
  @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4;
}

.stat-card.primary {
  @apply bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-purple)] text-white border-none;
}

.stat-label { @apply text-sm opacity-80 mb-2; }

.stat-value { @apply text-2xl font-bold font-mono; }

.stat-change { @apply text-sm mt-2; }
.stat-change.positive { @apply text-[var(--success)]; }
.stat-card.primary .stat-change { @apply text-white/80; }

.chart-container { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4; }
.chart-container h3 { @apply text-sm font-semibold mb-4; }
.chart-placeholder { @apply h-40 bg-[var(--bg-elevated)] rounded-lg relative overflow-hidden; }
.chart-line {
  @apply absolute inset-0;
  background: linear-gradient(90deg, var(--accent-primary) 0%, var(--accent-purple) 50%, var(--accent-secondary) 100%);
  opacity: 0.3;
}

.data-table { @apply w-full bg-[var(--bg-card)] rounded-xl overflow-hidden mb-6; }
.data-table th { @apply text-left px-4 py-3 text-xs text-[var(--text-muted)] uppercase bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)]; }
.data-table td { @apply px-4 py-3 border-b border-[var(--border-subtle)]; }
.data-table tr:last-child td { @apply border-b-0; }

.mono { font-family: 'JetBrains Mono', monospace; }
.positive { @apply text-[var(--success)]; }
.negative { @apply text-[var(--danger)]; }

.status-badge { @apply px-2 py-0.5 rounded-full text-xs; }
.status-badge.success { @apply bg-[rgba(0,245,160,0.15)] text-[var(--success)]; }

.wallet-diagram { @apply flex flex-col items-center gap-4 py-8; }

.wallet-node { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4 text-center; }
.wallet-node.main { @apply w-48; }
.wallet-node.sub { @apply w-36; }

.node-icon { @apply text-3xl mb-2; }
.node-label { @apply text-sm font-semibold; }
.node-amount { @apply font-mono text-lg mt-2; }
.node-status { @apply text-xs mt-2; }
.node-status.connected { @apply text-[var(--success)]; }

.wallet-children { @apply flex gap-4 flex-wrap justify-center; }

.allocation-section { @apply mb-6; }
.allocation-section h3 { @apply text-sm font-semibold mb-4 text-[var(--accent-primary)]; }

.allocation-grid { @apply grid grid-cols-5 gap-3; }

.allocation-card { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-3; }

.tool-header { @apply flex items-center gap-2 mb-3; }
.tool-icon { @apply text-lg; }
.tool-name { @apply text-sm font-semibold; }

.allocation-bar { @apply h-2 bg-[var(--bg-elevated)] rounded-full overflow-hidden mb-1; }
.allocation-fill { @apply h-full bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-purple)]; }
.allocation-percent { @apply text-xs text-[var(--text-secondary)]; }
.tool-amount { @apply font-mono text-sm mt-2; }

.margin-info { @apply bg-[var(--bg-card)] rounded-xl p-4 space-y-2; }
.margin-item { @apply flex justify-between; }

.platform-options { @apply flex gap-4; }
.platform-option { @apply flex items-center gap-2 cursor-pointer; }

.simulator-tabs { @apply flex gap-2 mb-6; }

.sim-btn {
  @apply px-4 py-2 rounded-lg text-sm font-medium cursor-pointer transition-all;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
}

.sim-btn:hover { @apply border-[var(--accent-primary)]; }
.sim-btn.active { @apply bg-[var(--accent-primary)] text-[var(--bg-primary)] border-[var(--accent-primary)]; }

.sim-panel { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-6; }
.sim-panel h3 { @apply text-lg font-semibold mb-2; }
.sim-panel p { @apply text-sm text-[var(--text-secondary)] mb-4; }

.sim-result { @apply flex gap-6; }
.result-item { @apply flex items-center gap-2; }

.sim-config { @apply mb-4; }
.config-item { @apply flex items-center gap-2; }
.config-item label { @apply text-sm; }
.config-item select { @apply bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded px-2 py-1; }

.sim-recommend { @apply bg-[var(--bg-elevated)] rounded-xl p-4; }
.sim-recommend h4 { @apply text-sm font-semibold mb-3; }
.recommend-item { @apply flex justify-between py-1; }

.btn { @apply px-4 py-2 rounded-lg font-semibold cursor-pointer transition-all inline-flex items-center gap-2 border-none; }
.btn-primary { background: linear-gradient(135deg, var(--accent-primary), #00b8a3); color: var(--bg-primary); }
.btn-outline { background: transparent; border: 1px solid var(--border-subtle); color: var(--text-secondary); }
.btn-outline:hover { border-color: var(--accent-primary); color: var(--accent-primary); }
</style>
