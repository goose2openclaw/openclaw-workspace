<template>
  <AppLayout>
    <div class="market-top20">
      <div class="stats-row">
        <div class="stat-card">
          <span class="stat-label">总市值</span>
          <span class="stat-value">$2.34T</span>
          <span class="stat-change positive">+2.34%</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">BTC占比</span>
          <span class="stat-value">52.4%</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">上涨币种</span>
          <span class="stat-value positive">15/20</span>
        </div>
      </div>
      
      <div class="coin-grid">
        <div v-for="coin in topCoins" :key="coin.symbol" class="coin-card" @click="$router.push('/market/kline/' + coin.symbol)">
          <div class="coin-header">
            <span class="coin-icon">{{ coin.icon }}</span>
            <div class="coin-info">
              <span class="coin-name">{{ coin.name }}</span>
              <span class="coin-symbol">{{ coin.symbol }}</span>
            </div>
          </div>
          <div class="coin-price">${{ formatNumber(coin.price) }}</div>
          <div class="coin-change" :class="coin.change >= 0 ? 'positive' : 'negative'">
            {{ coin.change >= 0 ? '+' : '' }}{{ coin.change.toFixed(2) }}%
          </div>
          <div class="coin-signal">
            <span class="signal-badge" :class="coin.signal.toLowerCase()">{{ coin.signal }}</span>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'MarketTop20',
  components: { AppLayout },
  setup() {
    const topCoins = ref([
      { symbol: 'BTC', name: 'Bitcoin', icon: '₿', price: 67432.50, change: 3.24, signal: 'BUY' },
      { symbol: 'ETH', name: 'Ethereum', icon: 'Ξ', price: 3521.80, change: 5.12, signal: 'BUY' },
      { symbol: 'BNB', name: 'BNB', icon: '◈', price: 587.30, change: 2.45, signal: 'BUY' },
      { symbol: 'SOL', name: 'Solana', icon: '◎', price: 142.60, change: 8.34, signal: 'BUY' },
      { symbol: 'XRP', name: 'Ripple', icon: '✕', price: 0.5234, change: -1.23, signal: 'HOLD' },
    ])

    const formatNumber = (num) => num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

    return { topCoins, formatNumber }
  },
}
</script>

<style scoped>
.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4; }
.stat-label { @apply text-xs text-[var(--text-muted)] block mb-1; }
.stat-value { @apply text-xl font-bold font-mono block; }
.stat-value.positive { @apply text-[var(--success)]; }
.stat-change { @apply text-sm font-mono; }
.stat-change.positive { @apply text-[var(--success)]; }
.coin-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.coin-card { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4 cursor-pointer transition-all duration-200 hover:border-[var(--accent-primary)] hover:-translate-y-1; }
.coin-header { @apply flex items-center gap-3 mb-3; }
.coin-icon { @apply text-2xl; }
.coin-info { @apply flex flex-col; }
.coin-name { @apply font-bold; }
.coin-symbol { @apply text-xs text-[var(--text-muted)]; }
.coin-price { @apply font-mono text-lg font-bold mb-1; }
.coin-change { @apply font-mono text-sm font-semibold; }
.coin-change.positive { @apply text-[var(--success)]; }
.coin-change.negative { @apply text-[var(--danger)]; }
.coin-signal { @apply mt-2; }
.signal-badge { @apply px-2 py-1 rounded-full text-xs font-bold; }
.signal-badge.buy { @apply bg-[rgba(0,245,160,0.15)] text-[var(--success)]; }
.signal-badge.sell { @apply bg-[rgba(255,71,87,0.15)] text-[var(--danger)]; }
.signal-badge.hold { @apply bg-[rgba(255,212,59,0.15)] text-[var(--warning)]; }
</style>
