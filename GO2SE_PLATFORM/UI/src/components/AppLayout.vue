<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: !sidebarExpanded }">
      <!-- Logo -->
      <div class="logo-section" @click="toggleSidebar">
        <div class="logo-icon">🪿</div>
        <span class="logo-text">Go2Se 护食</span>
      </div>

      <!-- 导航 -->
      <nav class="nav-section">
        <!-- 首页纵览 -->
        <router-link to="/home" class="nav-item" :class="{ active: $route.path === '/home' }">
          <span class="nav-icon">🏠</span>
          <span class="nav-label">首页纵览</span>
        </router-link>

        <!-- 热点纵览 -->
        <router-link to="/hot" class="nav-item" :class="{ active: $route.path === '/hot' }">
          <span class="nav-icon">🔥</span>
          <span class="nav-label">热点纵览</span>
        </router-link>

        <!-- 参数仪表盘 -->
        <router-link to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }">
          <span class="nav-icon">📊</span>
          <span class="nav-label">参数仪表盘</span>
        </router-link>

        <!-- 资产看板 -->
        <router-link to="/assets" class="nav-item" :class="{ active: $route.path === '/assets' }">
          <span class="nav-icon">💰</span>
          <span class="nav-label">资产看板</span>
        </router-link>

        <!-- 北斗七鑫 -->
        <div class="nav-item has-submenu" @click="toggleSubmenu('beidou')" :class="{ active: isParentRoute('beidou') }">
          <span class="nav-icon">🔯</span>
          <span class="nav-label">北斗七鑫</span>
          <span class="submenu-arrow">{{ submenus.beidou ? '▼' : '▶' }}</span>
        </div>
        <div v-if="submenus.beidou" class="submenu">
          <router-link to="/market" class="submenu-item">📈 市场行情</router-link>
          <router-link to="/strategies/rabbit" class="submenu-item">🐰 打兔子</router-link>
          <router-link to="/strategies/mole" class="submenu-item">🐹 打地鼠</router-link>
          <router-link to="/strategies/oracle" class="submenu-item">🔮 走着瞧</router-link>
          <router-link to="/strategies/leader" class="submenu-item">👑 跟大哥</router-link>
          <router-link to="/strategies/hitchhiker" class="submenu-item">🍀 搭便车</router-link>
          <router-link to="/strategies/airdrop" class="submenu-item">💰 薅羊毛</router-link>
          <router-link to="/strategies/crowdsource" class="submenu-item">👶 穷孩子</router-link>
        </div>

        <!-- 投资组合 -->
        <router-link to="/portfolio" class="nav-item" :class="{ active: $route.path === '/portfolio' }">
          <span class="nav-icon">📈</span>
          <span class="nav-label">投资组合</span>
        </router-link>

        <!-- 策略模型 -->
        <router-link to="/strategies" class="nav-item" :class="{ active: isParentRoute('strategies') }">
          <span class="nav-icon">♟️</span>
          <span class="nav-label">策略模型</span>
        </router-link>

        <!-- 声纳趋势 -->
        <router-link to="/sonar" class="nav-item" :class="{ active: $route.path === '/sonar' }">
          <span class="nav-icon">📡</span>
          <span class="nav-label">声纳趋势</span>
        </router-link>

        <!-- 预言机 -->
        <router-link to="/oracle" class="nav-item" :class="{ active: $route.path === '/oracle' }">
          <span class="nav-icon">🔮</span>
          <span class="nav-label">预言机</span>
        </router-link>

        <!-- 生态工具 -->
        <router-link to="/ecosystem" class="nav-item" :class="{ active: $route.path === '/ecosystem' }">
          <span class="nav-icon">🛠️</span>
          <span class="nav-label">生态工具</span>
        </router-link>

        <!-- 脚本日志 -->
        <router-link to="/scripts" class="nav-item" :class="{ active: $route.path === '/scripts' }">
          <span class="nav-icon">📝</span>
          <span class="nav-label">脚本日志</span>
        </router-link>

        <!-- 交易记录 -->
        <router-link to="/trading/history" class="nav-item" :class="{ active: isParentRoute('trading') }">
          <span class="nav-icon">📊</span>
          <span class="nav-label">交易记录</span>
        </router-link>

        <!-- 分享有礼 -->
        <router-link to="/referral" class="nav-item" :class="{ active: $route.path === '/referral' }">
          <span class="nav-icon">🎁</span>
          <span class="nav-label">分享有礼</span>
        </router-link>

        <!-- 私募LP -->
        <router-link to="/private" class="nav-item" :class="{ active: $route.path === '/private' }">
          <span class="nav-icon">💎</span>
          <span class="nav-label">私募LP</span>
        </router-link>

        <!-- 客服中心 -->
        <router-link to="/support" class="nav-item" :class="{ active: $route.path === '/support' }">
          <span class="nav-icon">💬</span>
          <span class="nav-label">客服中心</span>
        </router-link>

        <!-- 设置中心 -->
        <router-link to="/settings" class="nav-item" :class="{ active: isParentRoute('settings') }">
          <span class="nav-icon">⚙️</span>
          <span class="nav-label">设置中心</span>
        </router-link>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 页面内容 (支持嵌套路由) -->
      <router-view />
    </main>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'AppLayout',
  setup() {
    const route = useRoute()
    const sidebarExpanded = ref(true)
    const submenus = ref({
      beidou: false,
      strategies: false,
      signals: false,
      trading: false,
      wallet: false,
      settings: false,
    })

    const toggleSidebar = () => {
      sidebarExpanded.value = !sidebarExpanded.value
    }

    const toggleSubmenu = (key) => {
      submenus.value[key] = !submenus.value[key]
    }

    const isParentRoute = (parent) => {
      return route.path.startsWith(`/${parent}`)
    }

    return {
      sidebarExpanded,
      submenus,
      toggleSidebar,
      toggleSubmenu,
      isParentRoute,
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
  overflow-y: auto;
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
  font-size: 1rem;
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
  padding: 0.65rem 1rem;
  margin: 0.15rem 0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
  text-decoration: none;
  position: relative;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background: var(--accent-primary);
  transform: scaleY(0);
  transition: transform 0.2s;
}

.nav-item:hover {
  background: rgba(0, 245, 212, 0.08);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(0, 245, 212, 0.12);
  color: var(--accent-primary);
}

.nav-item.active::before {
  transform: scaleY(1);
}

.nav-icon {
  font-size: 1.2rem;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
  font-size: 0.9rem;
  font-weight: 500;
}

.submenu-arrow {
  margin-left: auto;
  font-size: 0.65rem;
}

.submenu {
  margin-left: 2rem;
  padding-left: 0.5rem;
  border-left: 1px solid var(--border-subtle);
}

.submenu-item {
  display: block;
  padding: 0.4rem 0.75rem;
  margin: 0.1rem 0;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.8rem;
  border-radius: 6px;
}

.submenu-item:hover {
  background: rgba(0, 245, 212, 0.05);
  color: var(--accent-primary);
}

.main-content {
  flex: 1;
  margin-left: 220px;
  padding: 1rem;
  min-height: 100vh;
  transition: margin-left 0.3s;
}

.sidebar.collapsed + .main-content {
  margin-left: 68px;
}

/* 响应式 */
@media (max-width: 1400px) {
  .sidebar {
    width: 68px;
  }
  .logo-text,
  .nav-label,
  .submenu {
    display: none;
  }
  .main-content {
    margin-left: 68px;
  }
}

@media (max-width: 1024px) {
  .sidebar {
    width: 68px;
  }
  .logo-text,
  .nav-label {
    display: none;
  }
  .main-content {
    margin-left: 68px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  .main-content {
    margin-left: 0;
  }
}
</style>
