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
        <div class="nav-item" :class="{ active: isRoute('/focus') }" @click="navigateTo('/focus')">
          <span class="nav-icon">🎯</span>
          <span class="nav-label">注意力板块</span>
        </div>

        <!-- B. 宏观微观 -->
        <div class="nav-item" :class="{ active: isRoute('/macro-micro') }" @click="navigateTo('/macro-micro')">
          <span class="nav-icon">🔭</span>
          <span class="nav-label">宏观微观</span>
        </div>

        <!-- C. 资产看板 -->
        <div class="nav-item has-sub" :class="{ active: isParentRoute('/assets') }" @click="toggleSubmenu('assets')">
          <span class="nav-icon">💰</span>
          <span class="nav-label">资产看板</span>
          <span class="sub-arrow">{{ openSubmenus.assets ? '▼' : '▶' }}</span>
        </div>
        <div class="nav-submenu" v-if="openSubmenus.assets">
          <div class="nav-subitem" @click.stop="navigateTo('/assets/c1')">c1 财产总额</div>
          <div class="nav-subitem" @click.stop="navigateTo('/assets/c2')">c2 收益详情</div>
          <div class="nav-subitem" @click.stop="navigateTo('/assets/c3')">c3 钱包架构</div>
          <div class="nav-subitem" @click.stop="navigateTo('/assets/c4')">c4 资产分配</div>
          <div class="nav-subitem" @click.stop="navigateTo('/assets/c5')">c5 模拟器</div>
        </div>

        <!-- D. 投资配置 -->
        <div class="nav-item has-sub" :class="{ active: isParentRoute('/invest') }" @click="toggleSubmenu('invest')">
          <span class="nav-icon">📊</span>
          <span class="nav-label">投资配置</span>
          <span class="sub-arrow">{{ openSubmenus.invest ? '▼' : '▶' }}</span>
        </div>
        <div class="nav-submenu" v-if="openSubmenus.invest">
          <div class="nav-subitem" @click.stop="navigateTo('/invest/rabbit')">🐰 打兔子</div>
          <div class="nav-subitem" @click.stop="navigateTo('/invest/mole')">🐹 打地鼠</div>
          <div class="nav-subitem" @click.stop="navigateTo('/invest/oracle')">🔮 走着瞧</div>
          <div class="nav-subitem" @click.stop="navigateTo('/invest/leader')">👑 跟大哥</div>
          <div class="nav-subitem" @click.stop="navigateTo('/invest/hitchhiker')">🍀 搭便车</div>
        </div>

        <!-- E. 打工配置 -->
        <div class="nav-item has-sub" :class="{ active: isParentRoute('/work') }" @click="toggleSubmenu('work')">
          <span class="nav-icon">💼</span>
          <span class="nav-label">打工配置</span>
          <span class="sub-arrow">{{ openSubmenus.work ? '▼' : '▶' }}</span>
        </div>
        <div class="nav-submenu" v-if="openSubmenus.work">
          <div class="nav-subitem" @click.stop="navigateTo('/work/wool')">💰 薅羊毛</div>
          <div class="nav-subitem" @click.stop="navigateTo('/work/poor')">👶 穷孩子</div>
        </div>

        <!-- F. 算力资源 -->
        <div class="nav-item" :class="{ active: isRoute('/compute') }" @click="navigateTo('/compute')">
          <span class="nav-icon">🖥️</span>
          <span class="nav-label">算力资源</span>
        </div>

        <!-- G. 信号输入 -->
        <div class="nav-item" :class="{ active: isRoute('/signals') }" @click="navigateTo('/signals')">
          <span class="nav-icon">📡</span>
          <span class="nav-label">信号输入</span>
        </div>

        <!-- H. 策略为王 -->
        <div class="nav-item has-sub" :class="{ active: isParentRoute('/strategies') }" @click="toggleSubmenu('strategies')">
          <span class="nav-icon">♟️</span>
          <span class="nav-label">策略为王</span>
          <span class="sub-arrow">{{ openSubmenus.strategies ? '▼' : '▶' }}</span>
        </div>
        <div class="nav-submenu" v-if="openSubmenus.strategies">
          <div class="nav-subitem" @click.stop="navigateTo('/strategies/h1')">h1 当前策略</div>
          <div class="nav-subitem" @click.stop="navigateTo('/strategies/h2')">h2 仿真模拟</div>
          <div class="nav-subitem" @click.stop="navigateTo('/strategies/h3')">h3 克隆策略</div>
          <div class="nav-subitem" @click.stop="navigateTo('/strategies/h4')">h4 策略介绍</div>
        </div>

        <!-- I. 安全机制 -->
        <div class="nav-item has-sub" :class="{ active: isParentRoute('/security') }" @click="toggleSubmenu('security')">
          <span class="nav-icon">🔒</span>
          <span class="nav-label">安全机制</span>
          <span class="sub-arrow">{{ openSubmenus.security ? '▼' : '▶' }}</span>
        </div>
        <div class="nav-submenu" v-if="openSubmenus.security">
          <div class="nav-subitem" @click.stop="navigateTo('/security/i1')">i1 资金安全</div>
          <div class="nav-subitem" @click.stop="navigateTo('/security/i2')">i2 后门管控</div>
          <div class="nav-subitem" @click.stop="navigateTo('/security/i3')">i3 防崩溃</div>
          <div class="nav-subitem" @click.stop="navigateTo('/security/i4')">i4 数据安全</div>
          <div class="nav-subitem" @click.stop="navigateTo('/security/i5')">i5 全向仿真</div>
          <div class="nav-subitem" @click.stop="navigateTo('/security/i6')">i6 版本适配</div>
          <div class="nav-subitem" @click.stop="navigateTo('/security/i7')">i7 审计日志</div>
        </div>

        <!-- J. 机器学习 -->
        <div class="nav-item has-sub" :class="{ active: isParentRoute('/ml') }" @click="toggleSubmenu('ml')">
          <span class="nav-icon">🤖</span>
          <span class="nav-label">机器学习</span>
          <span class="sub-arrow">{{ openSubmenus.ml ? '▼' : '▶' }}</span>
        </div>
        <div class="nav-submenu" v-if="openSubmenus.ml">
          <div class="nav-subitem" @click.stop="navigateTo('/ml/j1')">j1 竞品迭代</div>
          <div class="nav-subitem" @click.stop="navigateTo('/ml/j2')">j2 定制优化</div>
        </div>

        <!-- K. 私募LP -->
        <div class="nav-item has-sub" :class="{ active: isParentRoute('/private') }" @click="toggleSubmenu('private')">
          <span class="nav-icon">🏛️</span>
          <span class="nav-label">私募LP</span>
          <span class="sub-arrow">{{ openSubmenus.private ? '▼' : '▶' }}</span>
        </div>
        <div class="nav-submenu" v-if="openSubmenus.private">
          <div class="nav-subitem" @click.stop="navigateTo('/private/k1')">k1 私募部落</div>
          <div class="nav-subitem" @click.stop="navigateTo('/private/k2')">k2 平台LP</div>
        </div>

        <!-- L. 设置 -->
        <div class="nav-item has-sub" :class="{ active: isParentRoute('/settings') }" @click="toggleSubmenu('settings')">
          <span class="nav-icon">⚙️</span>
          <span class="nav-label">设置</span>
          <span class="sub-arrow">{{ openSubmenus.settings ? '▼' : '▶' }}</span>
        </div>
        <div class="nav-submenu" v-if="openSubmenus.settings">
          <div class="nav-subitem" @click.stop="navigateTo('/settings/l1')">l1 钱包架构</div>
          <div class="nav-subitem" @click.stop="navigateTo('/settings/l2')">l2 交易所机构</div>
          <div class="nav-subitem" @click.stop="navigateTo('/settings/l3')">l3 信息同步</div>
          <div class="nav-subitem" @click.stop="navigateTo('/settings/l4')">l4 OPC托管</div>
        </div>

        <!-- M. 脚本日志 -->
        <div class="nav-item has-sub" :class="{ active: isParentRoute('/scripts') }" @click="toggleSubmenu('scripts')">
          <span class="nav-icon">📝</span>
          <span class="nav-label">脚本日志</span>
          <span class="sub-arrow">{{ openSubmenus.scripts ? '▼' : '▶' }}</span>
        </div>
        <div class="nav-submenu" v-if="openSubmenus.scripts">
          <div class="nav-subitem" @click.stop="navigateTo('/scripts/m1')">m1 双脑备份</div>
          <div class="nav-subitem" @click.stop="navigateTo('/scripts/m2')">m2 最佳状态点</div>
          <div class="nav-subitem" @click.stop="navigateTo('/scripts/m3')">m3 日志输出</div>
        </div>

        <!-- N. 工程模式 -->
        <div class="nav-item has-sub" :class="{ active: isParentRoute('/engineering') }" @click="toggleSubmenu('engineering')">
          <span class="nav-icon">🔧</span>
          <span class="nav-label">工程模式</span>
          <span class="sub-arrow">{{ openSubmenus.engineering ? '▼' : '▶' }}</span>
        </div>
        <div class="nav-submenu" v-if="openSubmenus.engineering">
          <div class="nav-subitem" @click.stop="navigateTo('/engineering/n1')">n1 AI Debug</div>
          <div class="nav-subitem" @click.stop="navigateTo('/engineering/n2')">n2 终端Termux</div>
          <div class="nav-subitem" @click.stop="navigateTo('/engineering/n3')">n3 指令通道</div>
        </div>
      </nav>
    </aside>

    <!-- 内容区 -->
    <main class="content-area" :class="{ 'sidebar-collapsed': !sidebarExpanded }">
      <!-- 介绍区 -->
      <div class="intro-section" :class="{ collapsed: introCollapsed }">
        <div class="intro-toggle" @click="toggleIntro">
          <span v-if="introCollapsed">▼ 平台介绍</span>
          <span v-else>▲ 收起介绍</span>
        </div>
        <div class="intro-content" v-if="!introCollapsed">
          <div class="intro-card">
            <h3>🪿 GO2SE 北斗七鑫</h3>
            <p>主动捡漏薅羊毛 | Crypto量化AI投资平台</p>
          </div>
          <div class="intro-card">
            <h3>📊 市场概览</h3>
            <p>BTC $67,432 | ETH $3,521 | SOL $142</p>
          </div>
          <div class="intro-card">
            <h3>🔯 七大工具</h3>
            <p>打兔子/打地鼠/走着瞧/跟大哥/搭便车/薅羊毛/穷孩子</p>
          </div>
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
import { ref, computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'AppCanvas',
  setup() {
    const route = useRoute()
    const router = useRouter()

    const isExpanded = ref(true)
    const sidebarExpanded = ref(true)
    const introCollapsed = ref(false)
    const openSubmenus = reactive({
      assets: false,
      invest: false,
      work: false,
      strategies: false,
      security: false,
      ml: false,
      private: false,
      settings: false,
      scripts: false,
      engineering: false,
    })

    const currentRoute = computed(() => route.path)

    const isRoute = (path) => route.path === path

    const isParentRoute = (prefix) => route.path.startsWith(prefix)

    const toggleSidebar = () => {
      sidebarExpanded.value = !sidebarExpanded.value
      isExpanded.value = sidebarExpanded.value
    }

    const toggleIntro = () => {
      introCollapsed.value = !introCollapsed.value
    }

    const toggleSubmenu = (key) => {
      openSubmenus[key] = !openSubmenus[key]
    }

    const navigateTo = (path) => {
      router.push(path)
    }

    return {
      isExpanded,
      sidebarExpanded,
      introCollapsed,
      openSubmenus,
      currentRoute,
      isRoute,
      isParentRoute,
      toggleSidebar,
      toggleIntro,
      toggleSubmenu,
      navigateTo,
    }
  },
}
</script>

<style scoped>
.app-canvas { @apply flex min-h-screen pt-16; }

.sidebar {
  @apply w-64 bg-[var(--bg-secondary)] border-r border-[var(--border-subtle)] fixed left-0 top-16 bottom-0 overflow-y-auto transition-all duration-300;
}

.sidebar.collapsed { @apply w-16; }

.sidebar-toggle {
  @apply absolute top-4 -right-3 w-6 h-6 rounded-full bg-[var(--bg-elevated)] border border-[var(--border-subtle)] flex items-center justify-center cursor-pointer text-xs z-10;
}

.sidebar-nav { @apply pt-8 px-2; }

.nav-item {
  @apply flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all my-0.5 text-[var(--text-secondary)];
}

.nav-item:hover { background: rgba(0, 245, 212, 0.08); color: var(--text-primary); }
.nav-item.active { background: rgba(0, 245, 212, 0.12); color: var(--accent-primary); }

.nav-icon { @apply text-xl w-8 text-center flex-shrink-0; }

.nav-label { @apply text-sm font-medium whitespace-nowrap flex-1; }

.sidebar.collapsed .nav-label { @apply hidden; }
.sidebar.collapsed .sub-arrow { @apply hidden; }

.sub-arrow { @apply text-xs opacity-60; }

.nav-submenu {
  @apply pl-8 py-1 space-y-0.5;
}

.nav-subitem {
  @apply px-3 py-1.5 rounded text-sm text-[var(--text-muted)] cursor-pointer transition-colors;
}

.nav-subitem:hover { @apply text-[var(--accent-primary)] bg-[var(--bg-elevated)]; }

/* 内容区 */
.content-area {
  @apply flex-1 ml-64 p-4 transition-all duration-300;
}

.content-area.sidebar-collapsed { @apply ml-16; }

/* 介绍区 */
.intro-section { @apply mb-4 bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] overflow-hidden; }

.intro-toggle {
  @apply px-4 py-3 cursor-pointer text-sm text-[var(--text-secondary)] hover:text-[var(--accent-primary)] transition-colors;
}

.intro-content { @apply grid grid-cols-4 gap-3 p-4 pt-0; }

.intro-card { @apply bg-[var(--bg-elevated)] rounded-lg p-4; }
.intro-card h3 { @apply text-sm font-semibold mb-2 text-[var(--accent-primary)]; }
.intro-card p { @apply text-xs text-[var(--text-secondary)]; }

/* 主内容 */
.main-content { @apply min-h-[calc(100vh-16rem)]; }
</style>
