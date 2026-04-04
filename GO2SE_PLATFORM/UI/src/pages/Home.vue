<template>
  <AppLayout>
    <!-- 顶部快捷操作栏 -->
    <div class="quick-actions">
      <div class="mode-badge" :class="userModeClass">
        <span>{{ userModeIcon }}</span>
        <span>{{ userModeText }}</span>
      </div>
      <div class="balance-display">${{ formatNumber(balance) }}</div>
      <button class="btn btn-sm btn-buy" @click="showQuickTrade">⚡ 买</button>
      <button class="btn btn-sm btn-outline" @click="refreshAll">🔄</button>
      <button class="btn btn-sm btn-primary" @click="showAuthModal">模式</button>
    </div>

    <!-- 核心指标 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">💰 账户余额</div>
        <div class="stat-value">${{ formatNumber(balance) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">📈 总盈亏</div>
        <div class="stat-value" :class="totalPnl >= 0 ? 'positive' : 'negative'">
          {{ totalPnl >= 0 ? '+' : '' }}${{ formatNumber(Math.abs(totalPnl)) }}
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">🎯 胜率</div>
        <div class="stat-value">{{ winRate }}%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">📡 信号</div>
        <div class="stat-value">{{ signalCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">🔮 预言机</div>
        <div class="stat-value">{{ oracleCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">🛠️ 工具</div>
        <div class="stat-value">{{ toolCount }}</div>
      </div>
    </div>

    <!-- K线 + 订单簿 -->
    <div class="main-grid">
      <div class="card chart-card">
        <div class="card-header">
          <span class="card-title">📊 {{ selectedSymbol }}/USDT K线</span>
          <div class="chart-controls">
            <button v-for="tf in timeframes" :key="tf" class="chart-tf" :class="{ active: currentTf === tf }" @click="setTimeframe(tf)">{{ tf }}</button>
          </div>
        </div>
        <div class="chart-container">
          <canvas ref="candleChart" width="100%" height="280"></canvas>
        </div>
      </div>

      <div class="card orderbook-card">
        <div class="card-header">
          <span class="card-title">📚 订单簿</span>
        </div>
        <div class="orderbook">
          <div class="ob-side ob-ask">
            <div class="ob-title">卖出</div>
            <div v-for="(ask, i) in asks.slice(0, 5)" :key="'ask-'+i" class="ob-row">
              <span class="ob-price">{{ ask.price }}</span>
              <span class="ob-qty">{{ ask.qty }}</span>
            </div>
          </div>
          <div class="ob-side ob-bid">
            <div class="ob-title">买入</div>
            <div v-for="(bid, i) in bids.slice(0, 5)" :key="'bid-'+i" class="ob-row">
              <span class="ob-price">{{ bid.price }}</span>
              <span class="ob-qty">{{ bid.qty }}</span>
            </div>
          </div>
        </div>
        <div class="current-price">
          <div class="price-label">当前价格</div>
          <div class="price-value">${{ formatNumber(currentPrice) }}</div>
        </div>
      </div>
    </div>

    <!-- 北斗七鑫市场 -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">🔯 北斗七鑫</span>
      </div>
      <div class="market-grid">
        <div v-for="coin in topMarkets" :key="coin.symbol" class="market-card" @click="selectCoin(coin.symbol)">
          <span class="favorite-btn" @click.stop="toggleFavorite(coin.symbol)">{{ coin.favorite ? '⭐' : '☆' }}</span>
          <div class="market-icon">{{ coin.icon }}</div>
          <div class="market-name">{{ coin.symbol }}</div>
          <div class="market-price">${{ formatNumber(coin.price) }}</div>
          <div class="market-change" :class="coin.change >= 0 ? 'positive' : 'negative'">
            {{ coin.change >= 0 ? '+' : '' }}{{ coin.change.toFixed(2) }}%
          </div>
        </div>
      </div>
    </div>

    <!-- 实时信号 -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">📡 实时信号 (Binance)</span>
        <div class="flex gap-2">
          <select class="input" style="width: auto" v-model="sortBy" @change="sortSignals">
            <option value="conf">按置信度</option>
            <option value="change">按涨跌</option>
            <option value="coin">按币种</option>
          </select>
          <button class="btn btn-outline btn-sm" @click="refreshSignals">🔄</button>
        </div>
      </div>
      <table class="signals-table">
        <thead>
          <tr>
            <th>币种</th>
            <th>价格</th>
            <th>涨跌</th>
            <th>操作</th>
            <th>置信度</th>
            <th>收益</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="signal in signals" :key="signal.id" @click="showSignalDetail(signal)">
            <td>
              <div class="coin-badge">
                <span class="coin-icon">{{ signal.icon }}</span>
                <span>{{ signal.symbol }}</span>
              </div>
            </td>
            <td class="font-mono">${{ formatNumber(signal.price) }}</td>
            <td class="font-mono" :class="signal.change >= 0 ? 'positive' : 'negative'">
              {{ signal.change >= 0 ? '+' : '' }}{{ signal.change.toFixed(2) }}%
            </td>
            <td>
              <span class="action-badge" :class="signal.action.toLowerCase()">{{ signal.action }}</span>
            </td>
            <td>
              <div class="confidence-bar">
                <div class="confidence-fill" :class="getConfidenceClass(signal.confidence)" :style="{ width: signal.confidence + '%' }"></div>
              </div>
              <span class="confidence-value">{{ signal.confidence }}%</span>
            </td>
            <td class="font-mono" :class="signal.profit >= 0 ? 'positive' : 'negative'">
              {{ signal.profit >= 0 ? '+' : '' }}{{ signal.profit.toFixed(2) }}%
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'Home',
  components: { AppLayout },
  setup() {
    // 用户状态
    const userMode = ref('guest') // guest, subscriber, member, lp, expert
    const balance = ref(1000)
    const totalPnl = ref(767)
    const winRate = ref(68)
    const signalCount = ref(8)
    const oracleCount = ref(5)
    const toolCount = ref(8)

    // K线
    const selectedSymbol = ref('BTC')
    const currentTf = ref('1h')
    const timeframes = ['15m', '1h', '4h', '1d']
    const currentPrice = ref(75234.50)
    const candleChart = ref(null)

    // 订单簿
    const asks = ref([
      { price: '75235.50', qty: '0.523' },
      { price: '75236.00', qty: '0.234' },
      { price: '75237.20', qty: '0.812' },
      { price: '75238.50', qty: '0.156' },
      { price: '75240.00', qty: '0.421' },
    ])
    const bids = ref([
      { price: '75234.00', qty: '0.891' },
      { price: '75233.50', qty: '0.345' },
      { price: '75232.00', qty: '0.678' },
      { price: '75230.50', qty: '0.234' },
      { price: '75229.00', qty: '0.567' },
    ])

    // 市场
    const topMarkets = ref([
      { symbol: 'BTC', icon: '₿', price: 67432.50, change: 3.24, favorite: true },
      { symbol: 'ETH', icon: 'Ξ', price: 3521.80, change: 5.12, favorite: true },
      { symbol: 'BNB', icon: '◈', price: 587.30, change: 2.45, favorite: false },
      { symbol: 'SOL', icon: '◎', price: 142.60, change: 8.34, favorite: true },
      { symbol: 'XRP', icon: '✕', price: 0.5234, change: -1.23, favorite: false },
      { symbol: 'ADA', icon: '₳', price: 0.4521, change: 1.89, favorite: false },
      { symbol: 'DOGE', icon: 'Ð', price: 0.1234, change: -2.34, favorite: false },
    ])

    // 信号
    const sortBy = ref('conf')
    const signals = ref([
      { id: 1, symbol: 'BTC', icon: '₿', price: 67432.50, change: 3.24, action: 'BUY', confidence: 85, profit: 5.23 },
      { id: 2, symbol: 'ETH', icon: 'Ξ', price: 3521.80, change: 5.12, action: 'BUY', confidence: 72, profit: 3.45 },
      { id: 3, symbol: 'SOL', icon: '◎', price: 142.60, change: 8.34, action: 'BUY', confidence: 68, profit: -1.23 },
      { id: 4, symbol: 'BNB', icon: '◈', price: 587.30, change: 2.45, action: 'HOLD', confidence: 55, profit: 0.00 },
    ])

    // 计算属性
    const userModeClass = computed(() => {
      const classes = {
        guest: 'mode-guest',
        subscriber: 'mode-subscriber',
        member: 'mode-member',
        lp: 'mode-lp',
        expert: 'mode-expert',
      }
      return classes[userMode.value] || 'mode-guest'
    })

    const userModeText = computed(() => {
      const texts = {
        guest: '游客体验',
        subscriber: '订阅会员',
        member: '正式会员',
        lp: '私募LP',
        expert: '专家模式',
      }
      return texts[userMode.value] || '游客'
    })

    const userModeIcon = computed(() => {
      const icons = {
        guest: '👤',
        subscriber: '📦',
        member: '👑',
        lp: '🏛️',
        expert: '🎯',
      }
      return icons[userMode.value] || '👤'
    })

    // 方法
    const formatNumber = (num) => {
      return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    const getConfidenceClass = (confidence) => {
      if (confidence >= 70) return 'confidence-high'
      if (confidence >= 50) return 'confidence-mid'
      return 'confidence-low'
    }

    const setTimeframe = (tf) => {
      currentTf.value = tf
    }

    const selectCoin = (symbol) => {
      selectedSymbol.value = symbol
    }

    const toggleFavorite = (symbol) => {
      const coin = topMarkets.value.find(c => c.symbol === symbol)
      if (coin) coin.favorite = !coin.favorite
    }

    const showQuickTrade = () => {
      // 显示快速交易弹窗
    }

    const refreshAll = () => {
      // 刷新所有数据
    }

    const refreshSignals = () => {
      // 刷新信号
    }

    const sortSignals = () => {
      // 排序信号
    }

    const showSignalDetail = (signal) => {
      // 显示信号详情
    }

    const showAuthModal = () => {
      // 显示认证弹窗
    }

    onMounted(() => {
      // 初始化图表
    })

    return {
      userMode,
      userModeClass,
      userModeText,
      userModeIcon,
      balance,
      totalPnl,
      winRate,
      signalCount,
      oracleCount,
      toolCount,
      selectedSymbol,
      currentTf,
      timeframes,
      currentPrice,
      candleChart,
      asks,
      bids,
      topMarkets,
      signals,
      sortBy,
      formatNumber,
      getConfidenceClass,
      setTimeframe,
      selectCoin,
      toggleFavorite,
      showQuickTrade,
      refreshAll,
      refreshSignals,
      sortSignals,
      showSignalDetail,
      showAuthModal,
    }
  },
}
</script>

<style scoped>
.quick-actions {
  @apply flex items-center gap-3 mb-4;
}

.mode-badge {
  @apply flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold;
}

.mode-guest {
  @apply bg-[rgba(255,212,59,0.15)] text-[var(--warning)] border border-[rgba(255,212,59,0.3)];
}

.mode-subscriber {
  @apply bg-[rgba(0,187,249,0.15)] text-[var(--accent-secondary)] border border-[rgba(0,187,249,0.3)];
}

.mode-member {
  @apply bg-[rgba(157,78,221,0.15)] text-[var(--accent-purple)] border border-[rgba(157,78,221,0.3)];
}

.mode-lp {
  @apply bg-[rgba(255,215,0,0.15)] text-[var(--gold)] border border-[rgba(255,215,0,0.3)];
}

.mode-expert {
  @apply bg-[rgba(0,245,212,0.15)] text-[var(--accent-primary)] border border-[rgba(0,245,212,0.3)];
}

.balance-display {
  @apply font-mono text-sm text-[var(--accent-primary)];
}

.stats-grid {
  @apply grid grid-cols-6 gap-3 mb-4;
}

.main-grid {
  @apply grid grid-cols-3 gap-3 mb-4;
}

.chart-card {
  @apply col-span-2;
}

.orderbook-card {
  @apply col-span-1;
}

.card-header {
  @apply flex justify-between items-center mb-3;
}

.card-title {
  @apply text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider;
}

.chart-container {
  @apply relative rounded-lg overflow-hidden;
  background: var(--bg-elevated);
  height: 280px;
}

.chart-controls {
  @apply absolute top-3 left-3 z-10 flex gap-1;
}

.chart-tf {
  @apply px-2 py-1 text-xs rounded border bg-[var(--bg-elevated)] border-[var(--border-subtle)] text-[var(--text-muted)] cursor-pointer transition-all;
}

.chart-tf:hover,
.chart-tf.active {
  @apply bg-[var(--accent-primary)] text-[var(--bg-primary)] border-[var(--accent-primary)];
}

.orderbook {
  @apply grid grid-cols-2 gap-2 font-mono text-xs;
}

.ob-side {
  @apply p-2 rounded-lg;
}

.ob-ask {
  background: rgba(255, 71, 87, 0.08);
}

.ob-bid {
  background: rgba(0, 245, 160, 0.08);
}

.ob-title {
  @apply text-center text-xs font-bold mb-2;
}

.ob-ask .ob-title { @apply text-[var(--danger)]; }
.ob-bid .ob-title { @apply text-[var(--success)]; }

.ob-row {
  @apply flex justify-between py-0.5;
}

.ob-price {
  @apply z-10;
}

.ob-ask .ob-price { @apply text-[var(--danger)]; }
.ob-bid .ob-price { @apply text-[var(--success)]; }

.ob-qty {
  @apply text-[var(--text-secondary)] z-10;
}

.current-price {
  @apply mt-2 p-2 bg-[var(--bg-elevated)] rounded-lg text-center;
}

.price-label {
  @apply text-xs text-[var(--text-secondary)];
}

.price-value {
  @apply font-mono text-lg font-bold text-[var(--accent-primary)];
}

.market-grid {
  @apply grid grid-cols-7 gap-2;
}

.market-card {
  @apply bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded-lg p-3 text-center cursor-pointer transition-all hover:border-[var(--accent-primary)] hover:-translate-y-1 relative;
}

.favorite-btn {
  @apply absolute top-1 right-1 text-lg cursor-pointer opacity-40 transition-all;
}

.favorite-btn:hover,
.favorite-btn.active {
  @apply opacity-100 scale-110;
}

.favorite-btn.active {
  @apply text-[var(--gold)];
}

.market-icon {
  @apply text-2xl mb-1;
}

.market-name {
  @apply font-bold text-sm;
}

.market-price {
  @apply font-mono text-xs text-[var(--text-secondary)];
}

.market-change {
  @apply font-mono text-xs font-semibold;
}

.market-change.positive { @apply text-[var(--success)]; }
.market-change.negative { @apply text-[var(--danger)]; }

.signals-table {
  @apply w-full border-collapse;
}

.signals-table th {
  @apply text-left p-3 text-xs text-[var(--text-muted)] uppercase bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)];
}

.signals-table td {
  @apply p-3 border-b border-[var(--border-subtle)];
}

.signals-table tr:hover td {
  @apply bg-[var(--bg-elevated)] cursor-pointer;
}

.coin-badge {
  @apply flex items-center gap-2;
}

.coin-icon {
  @apply w-7 h-7 bg-[var(--bg-elevated)] rounded-full flex items-center justify-center font-bold text-xs text-[var(--accent-primary)];
}

.font-mono {
  font-family: 'JetBrains Mono', monospace;
}

.positive { @apply text-[var(--success)]; }
.negative { @apply text-[var(--danger)]; }

.action-badge {
  @apply px-2 py-1 rounded-full text-xs font-bold;
}

.action-badge.buy {
  @apply bg-[rgba(0,245,160,0.15)] text-[var(--success)];
}

.action-badge.sell {
  @apply bg-[rgba(255,71,87,0.15)] text-[var(--danger)];
}

.action-badge.hold {
  @apply bg-[rgba(255,212,59,0.15)] text-[var(--warning)];
}

.confidence-bar {
  @apply inline-block w-12 h-3 bg-[var(--bg-secondary)] rounded-full overflow-hidden vertical-align-middle border border-[var(--border-subtle)];
}

.confidence-fill {
  @apply h-full rounded-full;
}

.confidence-high { background: linear-gradient(90deg, #00f5a0, #00c896); }
.confidence-mid { background: linear-gradient(90deg, #ffd43b, #ffa500); }
.confidence-low { background: linear-gradient(90deg, #ff0000, #ff6b7a); }

.confidence-value {
  @apply font-bold text-sm ml-1;
}

.btn {
  @apply px-4 py-2 rounded-lg font-semibold cursor-pointer transition-all inline-flex items-center gap-2 border-none;
}

.btn-sm {
  @apply px-3 py-1.5 text-sm;
}

.btn-primary {
  @apply bg-gradient-to-r from-[var(--accent-primary)] to-[#00b8a3] text-[var(--bg-primary)];
}

.btn-outline {
  @apply bg-transparent border border-[var(--border-subtle)] text-[var(--text-secondary)];
}

.btn-outline:hover {
  @apply border-[var(--accent-primary)] text-[var(--accent-primary)];
}

.btn-buy {
  @apply bg-gradient-to-r from-[var(--success)] to-[#00c896] text-[var(--bg-primary)] font-bold;
}

.input {
  @apply px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] text-sm;
}

.flex { @apply flex; }
.gap-2 { gap: 0.5rem; }
</style>
