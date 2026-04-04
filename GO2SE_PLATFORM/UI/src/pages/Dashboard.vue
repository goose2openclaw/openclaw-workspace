<template>
  <AppLayout>
    <template #actions>
      <button class="btn btn-outline" @click="refreshData">
        🔄 刷新
      </button>
    </template>

    <!-- 核心指标 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">总资产</div>
        <div class="stat-value">${{ formatNumber(totalAssets) }}</div>
        <div class="stat-change" :class="assetsChange >= 0 ? 'positive' : 'negative'">
          {{ assetsChange >= 0 ? '+' : '' }}{{ assetsChange.toFixed(2) }}%
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">今日收益</div>
        <div class="stat-value" :class="todayProfit >= 0 ? 'positive' : 'negative'">
          {{ todayProfit >= 0 ? '+' : '' }}${{ formatNumber(todayProfit) }}
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">胜率</div>
        <div class="stat-value">{{ winRate }}%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">活跃信号</div>
        <div class="stat-value">{{ activeSignals }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">持仓数</div>
        <div class="stat-value">{{ positions }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Sharpe</div>
        <div class="stat-value">{{ sharpe }}</div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="dashboard-grid">
      <!-- K线图 -->
      <div class="card chart-card">
        <div class="card-header">
          <span class="card-title">K线走势</span>
          <div class="chart-controls">
            <button
              v-for="tf in timeframes"
              :key="tf"
              class="chart-tf"
              :class="{ active: currentTf === tf }"
              @click="changeTf(tf)"
            >
              {{ tf }}
            </button>
          </div>
        </div>
        <div class="chart-container" id="main-chart"></div>
      </div>

      <!-- 信号列表 -->
      <div class="card signals-card">
        <div class="card-header">
          <span class="card-title">最新信号</span>
          <router-link to="/signals/list" class="card-link">查看全部 →</router-link>
        </div>
        <table class="signals-table">
          <thead>
            <tr>
              <th>币种</th>
              <th>信号</th>
              <th>置信度</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="signal in recentSignals" :key="signal.id" @click="showSignalDetail(signal.id)">
              <td>
                <div class="coin-badge">
                  <span class="coin-icon">{{ signal.symbol[0] }}</span>
                  <span>{{ signal.symbol }}</span>
                </div>
              </td>
              <td>
                <span class="action-badge" :class="signal.action.toLowerCase()">
                  {{ signal.action }}
                </span>
              </td>
              <td>
                <div class="confidence-bar">
                  <div
                    class="confidence-fill"
                    :class="getConfidenceClass(signal.confidence)"
                    :style="{ width: signal.confidence + '%' }"
                  ></div>
                </div>
                <span class="confidence-value">{{ signal.confidence }}%</span>
              </td>
              <td>{{ signal.time }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 持仓概览 -->
      <div class="card positions-card">
        <div class="card-header">
          <span class="card-title">持仓概览</span>
          <router-link to="/trading/positions" class="card-link">详情 →</router-link>
        </div>
        <div class="positions-list">
          <div v-for="pos in topPositions" :key="pos.symbol" class="position-item">
            <div class="position-coin">
              <span class="coin-icon">{{ pos.symbol[0] }}</span>
              <span class="coin-name">{{ pos.symbol }}</span>
            </div>
            <div class="position-info">
              <span class="position-pnl" :class="pos.pnl >= 0 ? 'positive' : 'negative'">
                {{ pos.pnl >= 0 ? '+' : '' }}{{ pos.pnl.toFixed(2) }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 风控状态 -->
      <div class="card risk-card">
        <div class="card-header">
          <span class="card-title">风控状态</span>
          <router-link to="/settings/risk" class="card-link">配置 →</router-link>
        </div>
        <div class="risk-indicators">
          <div v-for="rule in riskRules" :key="rule.id" class="risk-item">
            <span class="risk-name">{{ rule.name }}</span>
            <span class="risk-status" :class="rule.status">{{ rule.value }}</span>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'Dashboard',
  components: { AppLayout },
  setup() {
    const totalAssets = ref(10000)
    const assetsChange = ref(3.24)
    const todayProfit = ref(156.78)
    const winRate = ref(72.5)
    const activeSignals = ref(25)
    const positions = ref(8)
    const sharpe = ref(2.34)

    const timeframes = ['1m', '5m', '15m', '1h', '4h', '1D']
    const currentTf = ref('1h')

    const recentSignals = ref([
      { id: 1, symbol: 'BTC', action: 'BUY', confidence: 85, time: '2分钟前' },
      { id: 2, symbol: 'ETH', action: 'BUY', confidence: 72, time: '5分钟前' },
      { id: 3, symbol: 'SOL', action: 'SELL', confidence: 68, time: '12分钟前' },
      { id: 4, symbol: 'BNB', action: 'HOLD', confidence: 55, time: '20分钟前' },
    ])

    const topPositions = ref([
      { symbol: 'BTC', pnl: 5.23 },
      { symbol: 'ETH', pnl: 3.45 },
      { symbol: 'SOL', pnl: -1.23 },
      { symbol: 'BNB', pnl: 2.11 },
    ])

    const riskRules = ref([
      { id: 1, name: '仓位限制', value: '65%', status: 'safe' },
      { id: 2, name: '日亏损熔断', value: '8%', status: 'safe' },
      { id: 3, name: '单笔风险', value: '2.3%', status: 'safe' },
      { id: 4, name: '波动止损', value: '5.1%', status: 'warning' },
    ])

    const formatNumber = (num) => {
      return num.toLocaleString('en-US', { maximumFractionDigits: 2 })
    }

    const getConfidenceClass = (confidence) => {
      if (confidence >= 70) return 'confidence-high'
      if (confidence >= 50) return 'confidence-mid'
      return 'confidence-low'
    }

    const changeTf = (tf) => {
      currentTf.value = tf
      // 重新加载K线数据
    }

    const refreshData = () => {
      // 刷新数据
    }

    const showSignalDetail = (id) => {
      // 显示信号详情弹窗
    }

    onMounted(() => {
      // 初始化K线图
    })

    return {
      totalAssets,
      assetsChange,
      todayProfit,
      winRate,
      activeSignals,
      positions,
      sharpe,
      timeframes,
      currentTf,
      recentSignals,
      topPositions,
      riskRules,
      formatNumber,
      getConfidenceClass,
      changeTf,
      refreshData,
      showSignalDetail,
    }
  },
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
}

.chart-card {
  grid-column: 1;
  grid-row: 1 / 3;
}

.signals-card {
  grid-column: 2;
  grid-row: 1;
}

.positions-card {
  grid-column: 2;
  grid-row: 2;
}

.risk-card {
  grid-column: 1 / 3;
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 1rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.card-link {
  font-size: 0.8rem;
  color: var(--accent-primary);
  text-decoration: none;
}

.chart-controls {
  display: flex;
  gap: 0.25rem;
}

.chart-tf {
  padding: 0.25rem 0.5rem;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  color: var(--text-muted);
  font-size: 0.7rem;
  cursor: pointer;
}

.chart-tf.active {
  background: var(--accent-primary);
  color: var(--bg-primary);
  border-color: var(--accent-primary);
}

.chart-container {
  height: 300px;
  background: var(--bg-elevated);
  border-radius: 8px;
}

.signals-table {
  width: 100%;
  border-collapse: collapse;
}

.signals-table th {
  text-align: left;
  padding: 0.5rem;
  font-size: 0.7rem;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
}

.signals-table td {
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid var(--border-subtle);
}

.signals-table tr {
  cursor: pointer;
}

.signals-table tr:hover {
  background: var(--bg-elevated);
}

.coin-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.coin-icon {
  width: 28px;
  height: 28px;
  background: var(--bg-elevated);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.7rem;
  color: var(--accent-primary);
}

.action-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: 700;
}

.action-badge.buy {
  background: rgba(0, 245, 160, 0.15);
  color: var(--success);
}

.action-badge.sell {
  background: rgba(255, 71, 87, 0.15);
  color: var(--danger);
}

.action-badge.hold {
  background: rgba(255, 212, 59, 0.15);
  color: var(--warning);
}

.confidence-bar {
  width: 60px;
  height: 10px;
  background: var(--bg-secondary);
  border-radius: 5px;
  display: inline-block;
  vertical-align: middle;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  border-radius: 5px;
}

.confidence-high { background: linear-gradient(90deg, #00f5a0, #00c896); }
.confidence-mid { background: linear-gradient(90deg, #ffd43b, #ffa500); }
.confidence-low { background: linear-gradient(90deg, #ff0000, #ff6b7a); }

.confidence-value {
  font-weight: 700;
  font-size: 0.9rem;
  margin-left: 0.5rem;
}

.positions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.position-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--bg-elevated);
  border-radius: 8px;
}

.position-coin {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.position-pnl.positive { color: var(--success); }
.position-pnl.negative { color: var(--danger); }

.risk-indicators {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.risk-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--bg-elevated);
  border-radius: 8px;
}

.risk-name {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.risk-status {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
}

.risk-status.safe { color: var(--success); }
.risk-status.warning { color: var(--warning); }
.risk-status.danger { color: var(--danger); }

.btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.btn-outline:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}
</style>
