<template>
  <div class="focus-page">
    <!-- Tab导航 -->
    <div class="tab-nav">
      <button class="tab" :class="{ active: activeTab === 'hot' }" @click="activeTab = 'hot'">🔥 热点速递</button>
      <button class="tab" :class="{ active: activeTab === 'diy' }" @click="activeTab = 'diy'">⭐ DIY置顶</button>
      <button class="tab" :class="{ active: activeTab === 'favorites' }" @click="activeTab = 'favorites'">💖 收藏夹</button>
      <button class="tab" :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">📜 历史记录</button>
    </div>

    <!-- 热点速递 -->
    <div v-if="activeTab === 'hot'" class="tab-content">
      <div class="hot-grid">
        <div v-for="coin in hotCoins" :key="coin.symbol" class="hot-card" @click="selectCoin(coin)">
          <div class="hot-rank" v-if="coin.rank">{{ coin.rank }}</div>
          <span class="favorite-btn" @click.stop="toggleFavorite(coin.symbol)" :class="{ active: coin.favorite }">
            {{ coin.favorite ? '⭐' : '☆' }}
          </span>
          <div class="coin-icon">{{ coin.icon }}</div>
          <div class="coin-name">{{ coin.symbol }}</div>
          <div class="coin-price">${{ formatNumber(coin.price) }}</div>
          <div class="coin-change" :class="coin.change >= 0 ? 'positive' : 'negative'">
            {{ coin.change >= 0 ? '+' : '' }}{{ coin.change.toFixed(2) }}%
          </div>
          <div class="coin-signal" :class="coin.signal.toLowerCase()">
            {{ coin.signal }}
          </div>
        </div>
      </div>
    </div>

    <!-- DIY置顶 -->
    <div v-if="activeTab === 'diy'" class="tab-content">
      <div class="diy-section">
        <div class="empty-state" v-if="diyItems.length === 0">
          <span class="empty-icon">📌</span>
          <p>暂无置顶内容</p>
          <button class="btn btn-outline" @click="addDIYItem">添加置顶</button>
        </div>
        <div v-else class="diy-list">
          <div v-for="item in diyItems" :key="item.id" class="diy-item">
            <div class="diy-icon">{{ item.icon }}</div>
            <div class="diy-info">
              <div class="diy-title">{{ item.title }}</div>
              <div class="diy-subtitle">{{ item.subtitle }}</div>
            </div>
            <button class="diy-remove" @click="removeDIYItem(item.id)">×</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 收藏夹 -->
    <div v-if="activeTab === 'favorites'" class="tab-content">
      <div class="favorites-grid">
        <div v-for="coin in favorites" :key="coin.symbol" class="favorite-card">
          <span class="favorite-btn active" @click="removeFavorite(coin.symbol)">⭐</span>
          <div class="coin-icon">{{ coin.icon }}</div>
          <div class="coin-name">{{ coin.symbol }}</div>
          <div class="coin-price">${{ formatNumber(coin.price) }}</div>
          <div class="coin-change" :class="coin.change >= 0 ? 'positive' : 'negative'">
            {{ coin.change >= 0 ? '+' : '' }}{{ coin.change.toFixed(2) }}%
          </div>
        </div>
      </div>
    </div>

    <!-- 历史记录 -->
    <div v-if="activeTab === 'history'" class="tab-content">
      <table class="history-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>币种</th>
            <th>操作</th>
            <th>价格</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in history" :key="item.id">
            <td>{{ item.time }}</td>
            <td>
              <div class="coin-badge">
                <span class="coin-icon-sm">{{ item.icon }}</span>
                <span>{{ item.symbol }}</span>
              </div>
            </td>
            <td>
              <span class="action-badge" :class="item.action.toLowerCase()">{{ item.action }}</span>
            </td>
            <td class="font-mono">${{ formatNumber(item.price) }}</td>
            <td>
              <span class="status-badge" :class="item.status">{{ item.status }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'Focus',
  setup() {
    const activeTab = ref('hot')

    const hotCoins = ref([
      { symbol: 'PEPE', icon: '🐸', price: 0.00001234, change: 45.67, signal: 'BUY', rank: 1, favorite: false },
      { symbol: 'WIF', icon: '🐶', price: 2.34, change: 23.45, signal: 'BUY', rank: 2, favorite: true },
      { symbol: 'BONK', icon: '🐕', price: 0.0234, change: 18.90, signal: 'BUY', rank: 3, favorite: false },
      { symbol: 'SOL', icon: '◎', price: 142.60, change: 12.34, signal: 'BUY', rank: 4, favorite: true },
      { symbol: 'BTC', icon: '₿', price: 67432.50, change: 3.24, signal: 'HOLD', rank: null, favorite: true },
      { symbol: 'ETH', icon: 'Ξ', price: 3521.80, change: 5.12, signal: 'BUY', rank: null, favorite: false },
    ])

    const favorites = ref([
      { symbol: 'BTC', icon: '₿', price: 67432.50, change: 3.24 },
      { symbol: 'ETH', icon: 'Ξ', price: 3521.80, change: 5.12 },
      { symbol: 'SOL', icon: '◎', price: 142.60, change: 8.34 },
    ])

    const diyItems = ref([])

    const history = ref([
      { id: 1, time: '10:30', symbol: 'BTC', icon: '₿', action: 'BUY', price: 67432.50, status: 'completed' },
      { id: 2, time: '10:25', symbol: 'ETH', icon: 'Ξ', action: 'SELL', price: 3521.80, status: 'completed' },
      { id: 3, time: '10:20', symbol: 'SOL', icon: '◎', action: 'BUY', price: 142.60, status: 'pending' },
    ])

    const formatNumber = (num) => num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: num < 1 ? 6 : 2 })

    const selectCoin = (coin) => {
      // 跳转到K线页面
    }

    const toggleFavorite = (symbol) => {
      const coin = hotCoins.value.find(c => c.symbol === symbol)
      if (coin) {
        coin.favorite = !coin.favorite
        if (coin.favorite) {
          favorites.value.push(coin)
        } else {
          favorites.value = favorites.value.filter(c => c.symbol !== symbol)
        }
      }
    }

    const removeFavorite = (symbol) => {
      favorites.value = favorites.value.filter(c => c.symbol !== symbol)
      const coin = hotCoins.value.find(c => c.symbol === symbol)
      if (coin) coin.favorite = false
    }

    const addDIYItem = () => {
      // 添加置顶
    }

    const removeDIYItem = (id) => {
      diyItems.value = diyItems.value.filter(item => item.id !== id)
    }

    return {
      activeTab,
      hotCoins,
      favorites,
      diyItems,
      history,
      formatNumber,
      selectCoin,
      toggleFavorite,
      removeFavorite,
      addDIYItem,
      removeDIYItem,
    }
  },
}
</script>

<style scoped>
.focus-page {
  @apply pb-8;
}

.tab-nav {
  @apply flex gap-2 mb-6 p-1 bg-[var(--bg-card)] rounded-xl;
}

.tab {
  @apply flex-1 px-4 py-2.5 rounded-lg text-sm font-medium cursor-pointer transition-all;
  background: transparent;
  color: var(--text-secondary);
}

.tab:hover {
  color: var(--text-primary);
  background: var(--bg-elevated);
}

.tab.active {
  color: var(--accent-primary);
  background: rgba(0, 245, 212, 0.1);
}

.tab-content {
  @apply animate-fadeIn;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.hot-grid {
  @apply grid grid-cols-6 gap-3;
}

.hot-card {
  @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4 text-center cursor-pointer relative transition-all hover:border-[var(--accent-primary)] hover:-translate-y-1;
}

.hot-rank {
  @apply absolute top-2 left-2 text-xs font-bold text-[var(--accent-purple)];
}

.favorite-btn {
  @apply absolute top-2 right-2 text-lg cursor-pointer opacity-40 transition-all;
}

.favorite-btn:hover,
.favorite-btn.active {
  @apply opacity-100;
}

.favorite-btn.active {
  @apply text-[var(--gold)];
}

.coin-icon {
  @apply text-3xl mb-2;
}

.coin-name {
  @apply font-bold text-sm;
}

.coin-price {
  @apply font-mono text-xs text-[var(--text-secondary)] mt-1;
}

.coin-change {
  @apply font-mono text-sm font-semibold mt-1;
}

.positive { @apply text-[var(--success)]; }
.negative { @apply text-[var(--danger)]; }

.coin-signal {
  @apply mt-2 px-2 py-0.5 rounded-full text-xs font-bold;
}

.coin-signal.buy {
  @apply bg-[rgba(0,245,160,0.15)] text-[var(--success)];
}

.coin-signal.sell {
  @apply bg-[rgba(255,71,87,0.15)] text-[var(--danger)];
}

.coin-signal.hold {
  @apply bg-[rgba(255,212,59,0.15)] text-[var(--warning)];
}

.empty-state {
  @apply flex flex-col items-center justify-center py-20 text-[var(--text-secondary)];
}

.empty-icon {
  @apply text-6xl mb-4;
}

.btn {
  @apply px-4 py-2 rounded-lg font-semibold cursor-pointer transition-all inline-flex items-center gap-2 border-none mt-4;
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

.favorites-grid {
  @apply grid grid-cols-4 gap-3;
}

.favorite-card {
  @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-4 text-center relative;
}

.history-table {
  @apply w-full bg-[var(--bg-card)] rounded-xl overflow-hidden;
}

.history-table th {
  @apply text-left px-4 py-3 text-xs text-[var(--text-muted)] uppercase bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)];
}

.history-table td {
  @apply px-4 py-3 border-b border-[var(--border-subtle)];
}

.coin-badge {
  @apply flex items-center gap-2;
}

.coin-icon-sm {
  @apply w-6 h-6 bg-[var(--bg-elevated)] rounded-full flex items-center justify-center font-bold text-xs text-[var(--accent-primary)];
}

.font-mono {
  font-family: 'JetBrains Mono', monospace;
}

.action-badge {
  @apply px-2 py-0.5 rounded-full text-xs font-bold;
}

.action-badge.buy {
  @apply bg-[rgba(0,245,160,0.15)] text-[var(--success)];
}

.action-badge.sell {
  @apply bg-[rgba(255,71,87,0.15)] text-[var(--danger)];
}

.status-badge {
  @apply px-2 py-0.5 rounded-full text-xs;
}

.status-badge.completed {
  @apply bg-[rgba(0,245,160,0.15)] text-[var(--success)];
}

.status-badge.pending {
  @apply bg-[rgba(255,212,59,0.15)] text-[var(--warning)];
}
</style>
