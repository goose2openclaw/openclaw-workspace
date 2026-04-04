<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: !sidebarExpanded }">
      <!-- Logo -->
      <div class="logo-section" @click="toggleSidebar">
        <div class="logo-icon">🪿</div>
        <span class="logo-text">GO2SE</span>
      </div>

      <!-- 导航 -->
      <nav class="nav-section">
        <!-- 总览 -->
        <router-link to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }">
          <span class="nav-icon">📊</span>
          <span class="nav-label">总览</span>
        </router-link>

        <!-- 市场 (可展开) -->
        <div class="nav-item has-submenu" @click="toggleSubmenu('market')" :class="{ active: isParentRoute('market') }">
          <span class="nav-icon">📈</span>
          <span class="nav-label">市场</span>
          <span class="submenu-arrow">{{ submenus.market ? '▼' : '▶' }}</span>
        </div>
        <div v-if="submenus.market" class="submenu">
          <router-link to="/market/top20" class="submenu-item">前20主流币</router-link>
          <router-link to="/market/movers" class="submenu-item">异动币</router-link>
          <router-link to="/market/exchanges" class="submenu-item">交易所</router-link>
        </div>

        <!-- 策略 (可展开) -->
        <div class="nav-item has-submenu" @click="toggleSubmenu('strategies')" :class="{ active: isParentRoute('strategies') }">
          <span class="nav-icon">⚙️</span>
          <span class="nav-label">策略</span>
          <span class="submenu-arrow">{{ submenus.strategies ? '▼' : '▶' }}</span>
        </div>
        <div v-if="submenus.strategies" class="submenu">
          <router-link to="/strategies/rabbit" class="submenu-item">🐰 打兔子</router-link>
          <router-link to="/strategies/mole" class="submenu-item">🐹 打地鼠</router-link>
          <router-link to="/strategies/oracle" class="submenu-item">🔮 走着瞧</router-link>
          <router-link to="/strategies/leader" class="submenu-item">👑 跟大哥</router-link>
          <router-link to="/strategies/hitchhiker" class="submenu-item">🍀 搭便车</router-link>
          <router-link to="/strategies/airdrop" class="submenu-item">💰 薅羊毛</router-link>
          <router-link to="/strategies/crowdsource" class="submenu-item">👶 穷孩子</router-link>
        </div>

        <!-- 信号 (可展开) -->
        <div class="nav-item has-submenu" @click="toggleSubmenu('signals')" :class="{ active: isParentRoute('signals') }">
          <span class="nav-icon">📡</span>
          <span class="nav-label">信号</span>
          <span class="submenu-arrow">{{ submenus.signals ? '▼' : '▶' }}</span>
        </div>
        <div v-if="submenus.signals" class="submenu">
          <router-link to="/signals/list" class="submenu-item">信号列表</router-link>
          <router-link to="/signals/mirofish" class="submenu-item">🧠 MiroFish</router-link>
          <router-link to="/signals/sonar" class="submenu-item">📡 声纳库</router-link>
        </div>

        <!-- 交易 (可展开) -->
        <router-link to="/trading/positions" class="nav-item" :class="{ active: isParentRoute('trading') }">
          <span class="nav-icon">💹</span>
          <span class="nav-label">交易</span>
        </router-link>

        <!-- 钱包 (可展开) -->
        <router-link to="/wallet/assets" class="nav-item" :class="{ active: isParentRoute('wallet') }">
          <span class="nav-icon">💰</span>
          <span class="nav-label">钱包</span>
        </router-link>

        <!-- 设置 (可展开) -->
        <router-link to="/settings/trading" class="nav-item" :class="{ active: isParentRoute('settings') }">
          <span class="nav-icon">⚡</span>
          <span class="nav-label">设置</span>
        </router-link>
      </nav>

      <!-- 会员等级 -->
      <div class="sidebar-footer">
        <div class="member-badge">
          <span class="member-icon">🏆</span>
          <span class="member-text">{{ memberLevel }}</span>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 面包屑 -->
      <div v-if="breadcrumbs.length > 1" class="breadcrumbs">
        <template v-for="(crumb, index) in breadcrumbs" :key="crumb.path">
          <router-link :to="crumb.path" class="breadcrumb-link">{{ crumb.title }}</router-link>
          <span v-if="index < breadcrumbs.length - 1" class="breadcrumb-sep">/</span>
        </template>
      </div>

      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">{{ pageTitle }}</h1>
        <div class="page-actions">
          <slot name="actions"></slot>
        </div>
      </div>

      <!-- 页面内容 -->
      <div class="page-content">
        <slot></slot>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'AppLayout',
  setup() {
    const route = useRoute()
    const sidebarExpanded = ref(true)
    const submenus = ref({
      market: false,
      strategies: false,
      signals: false,
      trading: false,
      wallet: false,
      settings: false,
    })

    const memberLevel = ref('🧑‍💻 游客')

    const toggleSidebar = () => {
      sidebarExpanded.value = !sidebarExpanded.value
    }

    const toggleSubmenu = (key) => {
      submenus.value[key] = !submenus.value[key]
    }

    const isParentRoute = (parent) => {
      return route.path.startsWith(`/${parent}`)
    }

    const pageTitle = computed(() => {
      return route.meta.title || 'GO2SE'
    })

    const breadcrumbs = computed(() => {
      const crumbs = [{ path: '/dashboard', title: '首页' }]
      if (route.meta.parent) {
        crumbs.push({ path: `/${route.meta.parent.toLowerCase()}`, title: route.meta.parent })
      }
      crumbs.push({ path: route.path, title: pageTitle.value })
      return crumbs
    })

    return {
      sidebarExpanded,
      submenus,
      memberLevel,
      toggleSidebar,
      toggleSubmenu,
      isParentRoute,
      pageTitle,
      breadcrumbs,
    }
  },
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  position: fixed;
  height: 100vh;
}

.sidebar.collapsed {
  width: 68px;
}

.logo-section {
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-purple));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  flex-shrink: 0;
}

.logo-text {
  font-weight: 800;
  font-size: 1.25rem;
  white-space: nowrap;
  background: linear-gradient(135deg, var(--text-primary), var(--accent-primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-section {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  margin: 0.2rem 0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
  position: relative;
  text-decoration: none;
}

.nav-item:hover {
  background: rgba(0, 245, 212, 0.08);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(0, 245, 212, 0.12);
  color: var(--accent-primary);
}

.nav-icon {
  font-size: 1.2rem;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
  font-size: 1rem;
  font-weight: 500;
}

.submenu-arrow {
  margin-left: auto;
  font-size: 0.7rem;
}

.submenu {
  margin-left: 2rem;
  padding-left: 0.5rem;
  border-left: 1px solid var(--border-subtle);
}

.submenu-item {
  display: block;
  padding: 0.5rem 1rem;
  margin: 0.2rem 0;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
  border-radius: 6px;
}

.submenu-item:hover {
  background: rgba(0, 245, 212, 0.05);
  color: var(--accent-primary);
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-subtle);
}

.member-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--bg-elevated);
  border-radius: 10px;
}

.member-icon {
  font-size: 1.2rem;
}

.member-text {
  font-size: 0.85rem;
  font-weight: 600;
}

.main-content {
  flex: 1;
  margin-left: 220px;
  padding: 1.5rem;
  min-height: 100vh;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}

.breadcrumb-link {
  color: var(--text-secondary);
  text-decoration: none;
}

.breadcrumb-link:hover {
  color: var(--accent-primary);
}

.breadcrumb-sep {
  color: var(--text-muted);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
}

.page-actions {
  display: flex;
  gap: 0.75rem;
}

.page-content {
  /* 内容区 */
}
</style>
