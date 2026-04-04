<template>
  <AppLayout>
    <div class="market-movers">
      <div class="section-header">
        <h2>涨幅榜</h2>
        <div class="tab-nav">
          <button class="tab active">全部</button>
          <button class="tab">主流币</button>
          <button class="tab">山寨币</button>
        </div>
      </div>
      <div class="movers-table">
        <table>
          <thead>
            <tr>
              <th>币种</th>
              <th>价格</th>
              <th>24h涨跌</th>
              <th>7d涨跌</th>
              <th>成交量</th>
              <th>信号</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="coin in movers" :key="coin.symbol" @click="$router.push('/market/kline/' + coin.symbol)">
              <td>
                <div class="coin-cell">
                  <span class="coin-icon">{{ coin.icon }}</span>
                  <div>
                    <span class="coin-name">{{ coin.name }}</span>
                    <span class="coin-symbol">{{ coin.symbol }}</span>
                  </div>
                </div>
              </td>
              <td class="font-mono">${{ formatNumber(coin.price) }}</td>
              <td class="font-mono" :class="coin.change24h >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'">
                {{ coin.change24h >= 0 ? '+' : '' }}{{ coin.change24h.toFixed(2) }}%
              </td>
              <td class="font-mono" :class="coin.change7d >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'">
                {{ coin.change7d >= 0 ? '+' : '' }}{{ coin.change7d.toFixed(2) }}%
              </td>
              <td class="font-mono">${{ formatVolume(coin.volume) }}</td>
              <td><span class="signal-badge" :class="coin.signal.toLowerCase()">{{ coin.signal }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'MarketMovers',
  components: { AppLayout },
  setup() {
    const movers = ref([
      { symbol: 'SOL', name: 'Solana', icon: '◎', price: 142.60, change24h: 12.34, change7d: 28.45, volume: 3200000000, signal: 'BUY' },
      { symbol: 'PEPE', name: 'Pepe', icon: '🐸', price: 0.00001234, change24h: 45.67, change7d: 123.45, volume: 1200000000, signal: 'BUY' },
      { symbol: 'WIF', name: 'dogwifhat', icon: '🐶', price: 2.34, change24h: 23.45, change7d: 67.89, volume: 890000000, signal: 'BUY' },
      { symbol: 'AVAX', name: 'Avalanche', icon: '🔺', price: 35.60, change24h: 8.90, change7d: 15.67, volume: 560000000, signal: 'BUY' },
      { symbol: 'LINK', name: 'Chainlink', icon: '🔗', price: 14.20, change24h: 6.78, change7d: 12.34, volume: 420000000, signal: 'BUY' },
    ])

    const formatNumber = (num) => num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: num < 1 ? 6 : 2 })
    const formatVolume = (vol) => vol > 1e9 ? (vol/1e9).toFixed(2) + 'B' : (vol/1e6).toFixed(2) + 'M'

    return { movers, formatNumber, formatVolume }
  },
}
</script>

<style scoped>
.section-header { @apply flex justify-between items-center mb-4; }
.section-header h2 { @apply text-xl font-bold; }
.tab-nav { @apply flex gap-2; }
.tab { @apply px-4 py-2 rounded-lg text-sm bg-[var(--bg-elevated)] text-[var(--text-secondary)] cursor-pointer; }
.tab.active { @apply bg-[var(--accent-primary)] text-[var(--bg-primary)]; }
.movers-table { @apply bg-[var(--bg-card)] rounded-xl overflow-hidden; }
table { @apply w-full; }
th { @apply text-left px-4 py-3 text-xs text-[var(--text-muted)] uppercase bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)]; }
td { @apply px-4 py-3 border-b border-[var(--border-subtle)] cursor-pointer; }
tr:hover td { @apply bg-[var(--bg-elevated)]; }
.coin-cell { @apply flex items-center gap-3; }
.coin-icon { @apply text-xl; }
.coin-name { @apply font-bold block; }
.coin-symbol { @apply text-xs text-[var(--text-muted)]; }
.font-mono { font-family: 'JetBrains Mono', monospace; }
.text-\[var\(--success\)\] { color: var(--success); }
.text-\[var\(--danger\)\] { color: var(--danger); }
.signal-badge { @apply px-2 py-1 rounded-full text-xs font-bold; }
.signal-badge.buy { @apply bg-[rgba(0,245,160,0.15)] text-[var(--success)]; }
.signal-badge.sell { @apply bg-[rgba(255,71,87,0.15)] text-[var(--danger)]; }
.signal-badge.hold { @apply bg-[rgba(255,212,59,0.15)] text-[var(--warning)]; }
</style>
