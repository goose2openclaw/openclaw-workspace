<template>
  <div class="hot-page">
    <h1 class="page-title">🔥 热点纵览</h1>

    <div class="hot-grid">
      <!-- 我的收藏 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">⭐ 我的收藏</span>
        </div>
        <div class="market-grid">
          <div v-for="coin in favorites" :key="coin.symbol" class="market-card">
            <span class="favorite-btn active" @click="removeFavorite(coin.symbol)">⭐</span>
            <div class="market-icon">{{ coin.icon }}</div>
            <div class="market-name">{{ coin.symbol }}</div>
            <div class="market-price">${{ formatNumber(coin.price) }}</div>
            <div class="market-change" :class="coin.change >= 0 ? 'positive' : 'negative'">
              {{ coin.change >= 0 ? '+' : '' }}{{ coin.change.toFixed(2) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- 我的持仓 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">💰 我的持仓</span>
          <button class="btn btn-outline btn-sm" @click="refreshPortfolio">🔄</button>
        </div>
        <div class="positions-list">
          <div v-for="pos in positions" :key="pos.symbol" class="position-item">
            <div class="position-coin">
              <span class="coin-icon">{{ pos.icon }}</span>
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

      <!-- 热点币种 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">🔥 热点币种</span>
        </div>
        <div class="market-grid">
          <div v-for="coin in hotCoins" :key="coin.symbol" class="market-card hot">
            <div class="hot-rank">{{ coin.rank }}</div>
            <div class="market-icon">{{ coin.icon }}</div>
            <div class="market-name">{{ coin.symbol }}</div>
            <div class="market-change" :class="coin.change >= 0 ? 'positive' : 'negative'">
              {{ coin.change >= 0 ? '+' : '' }}{{ coin.change.toFixed(2) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- 热门信号 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">⚡ 热门信号</span>
        </div>
        <table class="signals-table">
          <thead>
            <tr>
              <th>币种</th>
              <th>操作</th>
              <th>置信度</th>
              <th>来源</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="signal in hotSignals" :key="signal.id">
              <td>
                <div class="coin-badge">
                  <span class="coin-icon">{{ signal.icon }}</span>
                  <span>{{ signal.symbol }}</span>
                </div>
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
              <td>{{ signal.source }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 热点事件 -->
      <div class="card">
        <div class="card-header">
          <span class="card-title">🔮 热点事件</span>
        </div>
        <div class="oracle-grid">
          <div v-for="event in hotEvents" :key="event.id" class="oracle-card">
            <div class="event-title">{{ event.title }}</div>
            <div class="event-probability">{{ event.probability }}%</div>
            <div class="event-volume">${{ formatVolume(event.volume) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'Hot',
  setup() {
    const favorites = ref([
      { symbol: 'BTC', icon: '₿', price: 67432.50, change: 3.24 },
      { symbol: 'ETH', icon: 'Ξ', price: 3521.80, change: 5.12 },
      { symbol: 'SOL', icon: '◎', price: 142.60, change: 8.34 },
    ])

    const positions = ref([
      { symbol: 'BTC', icon: '₿', pnl: 5.23 },
      { symbol: 'ETH', icon: 'Ξ', pnl: 3.45 },
      { symbol: 'SOL', icon: '◎', pnl: -1.23 },
    ])

    const hotCoins = ref([
      { symbol: 'PEPE', icon: '🐸', change: 45.67, rank: 1 },
      { symbol: 'WIF', icon: '🐶', change: 23.45, rank: 2 },
      { symbol: 'BONK', icon: '🐕', change: 18.90, rank: 3 },
      { symbol: 'SOL', icon: '◎', change: 12.34, rank: 4 },
    ])

    const hotSignals = ref([
      { id: 1, symbol: 'PEPE', icon: '🐸', action: 'BUY', confidence: 82, source: 'MiroFish' },
      { id: 2, symbol: 'WIF', icon: '🐶', action: 'BUY', confidence: 75, source: 'Sonar' },
      { id: 3, symbol: 'BONK', icon: '🐕', action: 'HOLD', confidence: 60, source: 'Sentiment' },
    ])

    const hotEvents = ref([
      { id: 1, title: 'BTC突破$100000?', probability: 72, volume: 5200000 },
      { id: 2, title: 'ETH升级成功?', probability: 85, volume: 3200000 },
      { id: 3, title: '机构入场?', probability: 45, volume: 1800000 },
    ])

    const formatNumber = (num) => num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    const formatVolume = (vol) => vol > 1e6 ? (vol/1e6).toFixed(1) + 'M' : vol.toLocaleString()
    const getConfidenceClass = (conf) => conf >= 70 ? 'confidence-high' : conf >= 50 ? 'confidence-mid' : 'confidence-low'
    const removeFavorite = (symbol) => { favorites.value = favorites.value.filter(c => c.symbol !== symbol) }
    const refreshPortfolio = () => {}

    return { favorites, positions, hotCoins, hotSignals, hotEvents, formatNumber, formatVolume, getConfidenceClass, removeFavorite, refreshPortfolio }
  },
}
</script>

<style scoped>
.hot-page { padding-bottom: 2rem; }
.page-title { @apply text-2xl font-bold mb-6; }
.hot-grid { @apply space-y-4; }
.card { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4; }
.card-header { @apply flex justify-between items-center mb-3; }
.card-title { @apply text-sm font-semibold text-[var(--text-secondary)] uppercase; }
.market-grid { @apply grid grid-cols-4 gap-3; }
.market-card { @apply bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded-lg p-3 text-center relative; }
.market-card.hot { @apply border-[var(--accent-purple)]; }
.hot-rank { @apply absolute top-1 left-1 text-xs font-bold text-[var(--accent-purple)]; }
.favorite-btn { @apply absolute top-1 right-1 text-lg cursor-pointer; }
.favorite-btn.active { @apply text-[var(--gold)]; }
.market-icon { @apply text-2xl mb-1; }
.market-name { @apply font-bold text-sm; }
.market-price { @apply font-mono text-xs text-[var(--text-secondary)]; }
.market-change { @apply font-mono text-xs font-semibold; }
.positive { @apply text-[var(--success)]; }
.negative { @apply text-[var(--danger)]; }
.positions-list { @apply space-y-2; }
.position-item { @apply flex justify-between items-center p-3 bg-[var(--bg-elevated)] rounded-lg; }
.position-coin { @apply flex items-center gap-2; }
.coin-icon { @apply w-8 h-8 bg-[var(--bg-card)] rounded-full flex items-center justify-center font-bold text-xs text-[var(--accent-primary)]; }
.coin-name { @apply font-bold; }
.signals-table { @apply w-full border-collapse; }
.signals-table th { @apply text-left p-2 text-xs text-[var(--text-muted)] uppercase border-b border-[var(--border-subtle)]; }
.signals-table td { @apply p-2 border-b border-[var(--border-subtle)]; }
.coin-badge { @apply flex items-center gap-2; }
.coin-icon-sm { @apply w-6 h-6 bg-[var(--bg-elevated)] rounded-full flex items-center justify-center font-bold text-xs text-[var(--accent-primary)]; }
.action-badge { @apply px-2 py-0.5 rounded-full text-xs font-bold; }
.action-badge.buy { @apply bg-[rgba(0,245,160,0.15)] text-[var(--success)]; }
.action-badge.sell { @apply bg-[rgba(255,71,87,0.15)] text-[var(--danger)]; }
.action-badge.hold { @apply bg-[rgba(255,212,59,0.15)] text-[var(--warning)]; }
.confidence-bar { @apply inline-block w-10 h-2 bg-[var(--bg-secondary)] rounded-full overflow-hidden vertical-align-middle; }
.confidence-fill { @apply h-full rounded-full; }
.confidence-high { background: linear-gradient(90deg, #00f5a0, #00c896); }
.confidence-mid { background: linear-gradient(90deg, #ffd43b, #ffa500); }
.confidence-low { background: linear-gradient(90deg, #ff0000, #ff6b7a); }
.confidence-value { @apply font-bold text-sm ml-1; }
.oracle-grid { @apply grid grid-cols-3 gap-3; }
.oracle-card { @apply bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded-lg p-3; }
.event-title { @apply font-semibold text-sm mb-1; }
.event-probability { @apply font-mono text-lg font-bold text-[var(--accent-primary)]; }
.event-volume { @apply font-mono text-xs text-[var(--text-muted)]; }
.btn { @apply px-3 py-1.5 rounded-lg font-semibold cursor-pointer transition-all inline-flex items-center gap-1 border-none text-sm; }
.btn-sm { @apply px-2 py-1 text-xs; }
.btn-outline { @apply bg-transparent border border-[var(--border-subtle)] text-[var(--text-secondary)]; }
.btn-outline:hover { @apply border-[var(--accent-primary)] text-[var(--accent-primary)]; }
</style>
