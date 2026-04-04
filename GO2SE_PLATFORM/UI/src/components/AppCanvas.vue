<template>
  <div class="app-canvas" :class="{ expanded: isExpanded }">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: !sidebarExpanded }">
      <!-- 折叠按钮 -->
      <div class="sidebar-toggle" @click="toggleSidebar">
        <span v-if="sidebarExpanded">◀</span>
        <span v-else>▶</span>
      </div>

      <!-- 导航 -->
      <nav class="sidebar-nav">
        <!-- A. 注意力板块 -->
        <div class="nav-item" :class="{ active: currentRoute === '/focus' }" @click="navigateTo('/focus')">
          <span class="nav-icon">🎯</span>
          <span class="nav-label">注意力板块</span>
        </div>

        <!-- B. 宏观微观 -->
        <div class="nav-item" :class="{ active: currentRoute === '/macro-micro' }" @click="navigateTo('/macro-micro')">
          <span class="nav-icon">🔭</span>
          <span class="nav-label">宏观微观</span>
        </div>

        <!-- C. 资产看板 -->
        <div class="nav-item" :class="{ active: currentRoute.startsWith('/assets') }" @click="navigateTo('/assets')">
          <span class="nav-icon">💰</span>
          <span class="nav-label">资产看板</span>
        </div>

        <!-- D. 投资配置 -->
        <div class="nav-item" :class="{ active: currentRoute.startsWith('/invest') }" @click="navigateTo('/invest')">
          <span class="nav-icon">📊</span>
          <span class="nav-label">投资配置</span>
        </div>

        <!-- E. 打工配置 -->
        <div class="nav-item" :class="{ active: currentRoute.startsWith('/work') }" @click="navigateTo('/work')">
          <span class="nav-icon">💼</span>
          <span class="nav-label">打工配置</span>
        </div>

        <!-- F. 算力资源 -->
        <div class="nav-item" :class="{ active: currentRoute.startsWith('/compute') }" @click="navigateTo('/compute')">
          <span class="nav-icon">🖥️</span>
          <span class="nav-label">算力资源</span>
        </div>

        <!-- G. 信号输入 -->
        <div class="nav-item" :class="{ active: currentRoute.startsWith('/signals') }" @click="navigateTo('/signals')">
          <span class="nav-icon">📡</span>
          <span class="nav-label">信号输入</span>
        </div>

        <!-- H. 策略为王 -->
        <div class="nav-item" :class="{ active: currentRoute.startsWith('/strategies') }" @click="navigateTo('/strategies')">
          <span class="nav-icon">♟️</span>
          <span class="nav-label">策略为王</span>
        </div>

        <!-- I. 安全机制 -->
        <div class="nav-item" :class="{ active: currentRoute.startsWith('/security') }" @click="navigateTo('/security')">
          <span class="nav-icon">🔒</span>
          <span class="nav-label">安全机制</span>
        </div>

        <!-- J. 机器学习 -->
        <div class="nav-item" :class="{ active: currentRoute.startsWith('/ml') }" @click="navigateTo('/ml')">
          <span class="nav-icon">🤖</span>
          <span class="nav-label">机器学习</span>
        </div>
      </nav>
    </aside>

    <!-- 内容区 -->
    <main class="content-area">
      <!-- 介绍区 (可折叠) -->
      <div class="intro-section" :class="{ collapsed: introCollapsed }">
        <div class="intro-toggle" @click="toggleIntro">
          <span v-if="introCollapsed">▼ 平台介绍</span>
          <span v-else">▲ 收起介绍</span>
        </div>

        <div class="intro-content" v-if="!introCollapsed">
          <!-- 平台介绍 -->
          <div class="intro-card">
            <h3>🪿 GO2SE 北斗七鑫</h3>
            <p>主动捡漏薅羊毛 | Crypto量化AI投资平台</p>
          </div>

          <!-- 市场介绍 -->
          <div class="intro-card">
            <h3>📊 市场概览</h3>
            <p>BTC $67,432 | ETH $3,521 | SOL $142</p>
          </div>

          <!-- 北斗七鑫特点 -->
          <div class="intro-card">
            <h3>🔯 七大工具</h3>
            <p>打兔子/打地鼠/走着瞧/跟大哥/搭便车/薅羊毛/穷孩子</p>
          </div>

          <!-- 竞品对比 -->
          <div class="intro-card">
            <h3>🏆 竞品对比</h3>
            <p>胜率 +15% | 收益 +23% | 成本 -40%</p>
          </div>
        </div>
      </div>

      <!-- 主内容 -->
      <div class="main-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'AppCanvas',
  setup() {
    const route = useRoute()
    const router = useRouter()

    const isExpanded = ref(true)
    const sidebarExpanded = ref(true)
    const introCollapsed = ref(false)

    const currentRoute = computed(() => route.path)

    const toggleSidebar = () => {
      sidebarExpanded.value = !sidebarExpanded.value
      isExpanded.value = sidebarExpanded.value
    }

    const toggleIntro = () => {
      introCollapsed.value = !introCollapsed.value
    }

    const navigateTo = (path) => {
      router.push(path)
    }

    return {
      isExpanded,
      sidebarExpanded,
      introCollapsed,
      currentRoute,
      toggleSidebar,
      toggleIntro,
      navigateTo,
    }
  },
}
</script>

<style scoped>
.app-canvas {
  @apply flex min-h-screen pt-16;
}

.sidebar {
  @apply w-64 bg-[var(--bg-secondary)] border-r border-[var(--border-subtle)] fixed left-0 top-16 bottom-0 overflow-y-auto transition-all duration-300;
}

.sidebar.collapsed {
  @apply w-16;
}

.sidebar-toggle {
  @apply absolute top-4 -right-3 w-6 h-6 rounded-full bg-[var(--bg-elevated)] border border-[var(--border-subtle)] flex items-center justify-center cursor-pointer text-xs z-10;
}

.sidebar-nav {
  @apply pt-8 px-2;
}

.nav-item {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all my-0.5 text-[var(--text-secondary)];
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
  @apply text-xl w-8 text-center flex-shrink-0;
}

.nav-label {
  @apply text-sm font-medium whitespace-nowrap;
}

.sidebar.collapsed .nav-label {
  @apply hidden;
}

/* 内容区 */
.content-area {
  @apply flex-1 ml-64 p-4 transition-all duration-300;
}

.sidebar.collapsed + .content-area {
  @apply ml-16;
}

/* 介绍区 */
.intro-section {
  @apply mb-4 bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] overflow-hidden;
}

.intro-toggle {
  @apply px-4 py-3 cursor-pointer text-sm text-[var(--text-secondary)] hover:text-[var(--accent-primary)] transition-colors;
}

.intro-content {
  @apply grid grid-cols-4 gap-3 p-4 pt-0;
}

.intro-card {
  @apply bg-[var(--bg-elevated)] rounded-lg p-4;
}

.intro-card h3 {
  @apply text-sm font-semibold mb-2 text-[var(--accent-primary)];
}

.intro-card p {
  @apply text-xs text-[var(--text-secondary)];
}

/* 主内容 */
.main-content {
  @apply min-h-[calc(100vh-16rem)];
}
</style>
