<template>
  <div class="macro-micro-page">
    <h1 class="page-title">🔭 宏观微观</h1>

    <div class="dashboard-grid">
      <!-- 投资市场 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">🌐 投资市场</span>
        </div>
        <div class="market-list">
          <div v-for="coin in investMarket" :key="coin.symbol" class="market-item">
            <div class="coin-info">
              <span class="coin-icon">{{ coin.icon }}</span>
              <span class="coin-name">{{ coin.symbol }}</span>
            </div>
            <div class="coin-price">${{ formatNumber(coin.price) }}</div>
            <div class="coin-change" :class="coin.change >= 0 ? 'positive' : 'negative'">
              {{ coin.change >= 0 ? '+' : '' }}{{ coin.change.toFixed(2) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- 个人表现 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">👤 个人表现</span>
        </div>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">持仓</div>
            <div class="stat-value">3个</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">盈亏</div>
            <div class="stat-value positive">+$234</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">信号</div>
            <div class="stat-value">8个</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">胜率</div>
            <div class="stat-value">72%</div>
          </div>
        </div>
        <div class="total-pnl">
          <span>总收益:</span>
          <span class="positive">+12.3%</span>
        </div>
      </div>

      <!-- 打工市场 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">💼 打工市场</span>
        </div>
        <div class="work-stats">
          <div class="work-item">
            <span class="work-icon">💰</span>
            <span class="work-label">空投</span>
            <span class="work-value">5个待领取</span>
          </div>
          <div class="work-item">
            <span class="work-icon">👶</span>
            <span class="work-label">众包</span>
            <span class="work-value positive">$23收益</span>
          </div>
          <div class="work-item">
            <span class="work-icon">🖥️</span>
            <span class="work-label">算力</span>
            <span class="work-value">78%利用率</span>
          </div>
        </div>
      </div>

      <!-- 关注表现 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">⭐ 关注表现</span>
        </div>
        <div class="watch-list">
          <div v-for="coin in watchList" :key="coin.symbol" class="watch-item">
            <span class="coin-icon">{{ coin.icon }}</span>
            <span class="coin-name">{{ coin.symbol }}</span>
            <span class="watch-status" :class="coin.status">{{ coin.statusText }}</span>
            <span class="coin-change" :class="coin.change >= 0 ? 'positive' : 'negative'">
              {{ coin.change >= 0 ? '+' : '' }}{{ coin.change.toFixed(2) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <h3>⚡ 快捷操作</h3>
      <div class="action-buttons">
        <button class="action-btn" @click="$router.push('/invest')">
          <span class="action-icon">⚙️</span>
          <span>自主量化配置</span>
        </button>
        <button class="action-btn" @click="$router.push('/trading/live')">
          <span class="action-icon">📈</span>
          <span>直接下单</span>
        </button>
        <button class="action-btn" @click="$router.push('/trading/history')">
          <span class="action-icon">📊</span>
          <span>交易历史</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'MacroMicro',
  setup() {
    const investMarket = ref([
      { symbol: 'BTC', icon: '₿', price: 67432.50, change: 3.24 },
      { symbol: 'ETH', icon: 'Ξ', price: 3521.80, change: 5.12 },
      { symbol: 'SOL', icon: '◎', price: 142.60, change: 8.34 },
    ])

    const watchList = ref([
      { symbol: 'BTC', icon: '₿', status: 'watching', statusText: '关注中', change: -5.2 },
      { symbol: 'ETH', icon: 'Ξ', status: 'watching', statusText: '关注中', change: 3.4 },
      { symbol: 'PEPE', icon: '🐸', status: 'new', statusText: '新增关注', change: 45.67 },
    ])

    const formatNumber = (num) => num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

    return {
      investMarket,
      watchList,
      formatNumber,
    }
  },
}
</script>

<style scoped>
.macro-micro-page {
  @apply pb-8;
}

.page-title {
  @apply text-2xl font-bold mb-6;
}

.dashboard-grid {
  @apply grid grid-cols-2 gap-4 mb-6;
}

.card {
  @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4;
}

.card-header {
  @apply mb-4;
}

.card-title {
  @apply text-sm font-semibold text-[var(--text-secondary)] uppercase;
}

.market-list {
  @apply space-y-2;
}

.market-item {
  @apply flex items-center justify-between py-2 border-b border-[var(--border-subtle)];
}

.market-item:last-child {
  @apply border-b-0;
}

.coin-info {
  @apply flex items-center gap-2;
}

.coin-icon {
  @apply text-lg;
}

.coin-name {
  @apply font-bold text-sm;
}

.coin-price {
  @apply font-mono text-sm;
}

.coin-change {
  @apply font-mono text-sm font-semibold;
}

.positive { @apply text-[var(--success)]; }
.negative { @apply text-[var(--danger)]; }

.stats-grid {
  @apply grid grid-cols-4 gap-3 mb-4;
}

.stat-item {
  @apply text-center;
}

.stat-label {
  @apply text-xs text-[var(--text-muted)] mb-1;
}

.stat-value {
  @apply font-bold text-lg;
}

.total-pnl {
  @apply flex justify-between items-center pt-3 border-t border-[var(--border-subtle)] text-sm;
}

.work-stats {
  @apply space-y-3;
}

.work-item {
  @apply flex items-center gap-3;
}

.work-icon {
  @apply text-xl;
}

.work-label {
  @apply flex-1 text-sm;
}

.work-value {
  @apply font-mono text-sm;
}

.watch-list {
  @apply space-y-2;
}

.watch-item {
  @apply flex items-center gap-3 py-2;
}

.watch-status {
  @apply text-xs px-2 py-0.5 rounded-full;
}

.watch-status.watching {
  @apply bg-[rgba(0,245,212,0.1)] text-[var(--accent-primary)];
}

.watch-status.new {
  @apply bg-[rgba(157,78,221,0.1)] text-[var(--accent-purple)];
}

.quick-actions {
  @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4;
}

.quick-actions h3 {
  @apply text-sm font-semibold text-[var(--text-secondary)] mb-4;
}

.action-buttons {
  @apply flex gap-3;
}

.action-btn {
  @apply flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.action-icon {
  @apply text-xl;
}

.font-mono {
  font-family: 'JetBrains Mono', monospace;
}
</style>
