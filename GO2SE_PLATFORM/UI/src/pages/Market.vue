<template>
  <AppLayout>
    <div class="market-page">
      <div class="tab-nav">
        <router-link to="/market/top20" class="tab" :class="{ active: $route.path === '/market/top20' }">
          🐰 前20主流币
        </router-link>
        <router-link to="/market/movers" class="tab" :class="{ active: $route.path === '/market/movers' }">
          🐹 异动币
        </router-link>
        <router-link to="/market/exchanges" class="tab" :class="{ active: $route.path === '/market/exchanges' }">
          🏛️ 交易所
        </router-link>
      </div>

      <router-view />
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'Market',
  components: { AppLayout },
}
</script>

<style scoped>
.tab-nav {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 0.5rem;
  background: var(--bg-card);
  border-radius: 10px;
}

.tab {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.tab:hover {
  color: var(--text-primary);
  background: var(--bg-elevated);
}

.tab.active {
  color: var(--accent-primary);
  background: rgba(0, 245, 212, 0.1);
}
</style>
