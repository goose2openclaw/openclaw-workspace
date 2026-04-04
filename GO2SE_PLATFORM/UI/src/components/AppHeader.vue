<template>
  <header class="app-header">
    <!-- Logo区域 -->
    <div class="logo-area" @click="goHome">
      <div class="logo-animation">🪿</div>
      <div class="logo-text">
        <span class="brand">GO2SE</span>
        <span class="slogan">北斗七鑫量化</span>
      </div>
    </div>

    <!-- 控制区 -->
    <div class="control-area">
      <!-- 颜色选择 -->
      <div class="theme-selector">
        <button class="theme-btn" :class="{ active: theme === 'dark' }" @click="setTheme('dark')" title="深色">🌙</button>
        <button class="theme-btn" :class="{ active: theme === 'light' }" @click="setTheme('light')" title="浅色">☀️</button>
        <button class="theme-btn" :class="{ active: theme === 'matrix' }" @click="setTheme('matrix')" title="极客">🌈</button>
      </div>

      <!-- 语言选择 -->
      <div class="lang-selector">
        <select v-model="currentLang" @change="changeLang">
          <option value="zh">中文</option>
          <option value="en">English</option>
        </select>
      </div>

      <!-- 状态呼吸灯 (Alert Aggregation) -->
      <div class="status-indicator" :class="currentAlert.level" @click="toggleAlertDropdown">
        <span class="status-dot"></span>
        <span class="status-icon">{{ currentAlert.icon }}</span>
        <span class="status-text">{{ currentAlert.text }}</span>
        
        <!-- Alert下拉菜单 -->
        <div class="alert-dropdown" v-if="alertDropdownOpen">
          <div class="alert-header">
            <span>提醒中心</span>
            <span class="alert-count">{{ alerts.length }}条</span>
          </div>
          <div class="alert-list">
            <div v-for="alert in alerts" :key="alert.id" 
                 class="alert-item" 
                 :class="alert.level"
                 @click.stop="routeToAlert(alert)">
              <span class="alert-icon">{{ alert.icon }}</span>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-desc">{{ alert.desc }}</div>
              </div>
              <span class="alert-time">{{ alert.time }}</span>
            </div>
          </div>
          <div class="alert-footer" @click.stop="clearAllAlerts">
            清除全部
          </div>
        </div>
      </div>

      <!-- IM状态 -->
      <div class="im-status" @click="openIM">
        <span class="im-icon">💬</span>
        <span class="im-badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
      </div>

      <!-- 会员架构 -->
      <div class="member-badge" :class="memberClass" @click="showMemberInfo">
        <span class="member-icon">{{ memberIcon }}</span>
        <span class="member-text">{{ memberText }}</span>
      </div>

      <!-- 登录/注册 -->
      <div class="auth-buttons">
        <button class="btn btn-outline" @click="showLogin">登录</button>
        <button class="btn btn-primary" @click="showRegister">注册</button>
      </div>
    </div>
  </header>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'AppHeader',
  setup() {
    const theme = ref('dark')
    const currentLang = ref('zh')
    const unreadCount = ref(3)
    const memberType = ref('member') // guest, subscriber, member, lp, expert
    const alertDropdownOpen = ref(false)

    // Alert系统
    const alerts = ref([
      { id: 1, level: 'critical', icon: '🚨', title: '系统崩溃', desc: '服务中断', time: '1分钟前', route: '/security' },
      { id: 2, level: 'warning', icon: '⚠️', title: '风控警告', desc: '2个待处理', time: '5分钟前', route: '/risk' },
      { id: 3, level: 'info', icon: '💬', title: '新消息', desc: '3条未读', time: '10分钟前', route: '/im' },
      { id: 4, level: 'success', icon: '✅', title: '空投到账', desc: '$23.5已到账', time: '30分钟前', route: '/assets' },
    ])

    const currentAlert = computed(() => {
      // 按优先级返回最高级别alert
      const levels = { critical: 1, warning: 2, info: 3, success: 4 }
      const sorted = [...alerts.value].sort((a, b) => levels[a.level] - levels[b.level])
      const top = sorted[0]
      if (!top) return { level: 'success', icon: '✅', text: '系统正常' }
      
      const icons = { critical: '🚨', warning: '⚠️', info: '💬', success: '✅' }
      return { level: top.level, icon: icons[top.level], text: top.title }
    })

    const memberIcon = computed(() => {
      const icons = { guest: '👤', subscriber: '📦', member: '👑', lp: '🏛️', expert: '🎯' }
      return icons[memberType.value] || '👤'
    })

    const memberText = computed(() => {
      const texts = { guest: '游客', subscriber: '订阅', member: '会员', lp: '私募LP', expert: '专家' }
      return texts[memberType.value] || '游客'
    })

    const memberClass = computed(() => `member-${memberType.value}`)

    const setTheme = (t) => {
      theme.value = t
      document.documentElement.setAttribute('data-theme', t)
    }

    const changeLang = () => {}

    const goHome = () => {}

    const toggleAlertDropdown = () => {
      alertDropdownOpen.value = !alertDropdownOpen.value
    }

    const routeToAlert = (alert) => {
      alertDropdownOpen.value = false
      // 路由跳转
    }

    const clearAllAlerts = () => {
      alerts.value = []
      alertDropdownOpen.value = false
    }

    const openIM = () => {}

    const showMemberInfo = () => {}

    const showLogin = () => {}

    const showRegister = () => {}

    // 点击外部关闭
    const handleClickOutside = (e) => {
      if (alertDropdownOpen.value && !e.target.closest('.status-indicator')) {
        alertDropdownOpen.value = false
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      theme,
      currentLang,
      unreadCount,
      memberType,
      memberIcon,
      memberText,
      memberClass,
      alerts,
      currentAlert,
      alertDropdownOpen,
      setTheme,
      changeLang,
      goHome,
      toggleAlertDropdown,
      routeToAlert,
      clearAllAlerts,
      openIM,
      showMemberInfo,
      showLogin,
      showRegister,
    }
  },
}
</script>

<style scoped>
.app-header {
  @apply fixed top-0 left-0 right-0 h-16 bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)] z-50;
  @apply flex items-center justify-between px-4;
}

.logo-area {
  @apply flex items-center gap-3 cursor-pointer;
}

.logo-animation {
  @apply w-12 h-12 rounded-xl flex items-center justify-center text-3xl;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-purple));
  animation: logoFloat 3s ease-in-out infinite, logoGlow 2s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-8px) rotate(5deg); }
}

@keyframes logoGlow {
  0%, 100% { box-shadow: 0 0 20px rgba(0, 245, 212, 0.3); }
  50% { box-shadow: 0 0 40px rgba(0, 245, 212, 0.6); }
}

.logo-text { @apply flex flex-col; }

.brand {
  @apply text-xl font-bold;
  background: linear-gradient(135deg, var(--text-primary), var(--accent-primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.slogan { @apply text-xs text-[var(--text-muted)]; }

.control-area { @apply flex items-center gap-4; }

/* 主题选择器 */
.theme-selector { @apply flex gap-1 bg-[var(--bg-elevated)] p-1 rounded-lg; }

.theme-btn {
  @apply px-2 py-1 rounded text-sm cursor-pointer border-none transition-all;
  background: transparent;
  color: var(--text-muted);
}

.theme-btn:hover { color: var(--text-primary); }
.theme-btn.active { background: var(--accent-primary); color: var(--bg-primary); }

/* 语言选择 */
.lang-selector select {
  @apply bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded px-2 py-1 text-sm;
  color: var(--text-primary);
}

/* 状态呼吸灯 */
.status-indicator {
  @apply relative flex items-center gap-2 px-3 py-1.5 rounded-full cursor-pointer;
}

.status-dot {
  @apply w-2 h-2 rounded-full;
}

.status-icon { @apply text-sm; }
.status-text { @apply text-xs; }

.status-indicator.critical .status-dot { background: var(--danger); animation: breathe 0.5s ease-in-out infinite; }
.status-indicator.warning .status-dot { background: var(--warning); animation: breathe 1s ease-in-out infinite; }
.status-indicator.info .status-dot { background: var(--accent-secondary); animation: breathe 2s ease-in-out infinite; }
.status-indicator.success .status-dot { background: var(--success); animation: breathe 3s ease-in-out infinite; }

@keyframes breathe {
  0%, 100% { opacity: 0.4; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.1); }
}

/* Alert Dropdown */
.alert-dropdown {
  @apply absolute top-full right-0 mt-2 w-80 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl shadow-xl overflow-hidden;
}

.alert-header {
  @apply flex justify-between items-center px-4 py-3 bg-[var(--bg-elevated)] border-b border-[var(--border-subtle)] text-sm font-semibold;
}

.alert-count { @apply text-[var(--accent-primary)]; }

.alert-list { @apply max-h-80 overflow-y-auto; }

.alert-item {
  @apply flex items-start gap-3 px-4 py-3 border-b border-[var(--border-subtle)] cursor-pointer transition-colors;
}

.alert-item:hover { @apply bg-[var(--bg-elevated)]; }
.alert-item:last-child { @apply border-b-0; }

.alert-icon { @apply text-xl mt-0.5; }

.alert-content { @apply flex-1; }

.alert-title { @apply text-sm font-semibold; }
.alert-desc { @apply text-xs text-[var(--text-secondary)] mt-0.5; }
.alert-time { @apply text-xs text-[var(--text-muted)]; }

.alert-item.critical .alert-icon { @apply text-[var(--danger)]; }
.alert-item.warning .alert-icon { @apply text-[var(--warning)]; }
.alert-item.info .alert-icon { @apply text-[var(--accent-secondary)]; }
.alert-item.success .alert-icon { @apply text-[var(--success)]; }

.alert-footer {
  @apply text-center py-3 text-sm text-[var(--text-secondary)] cursor-pointer bg-[var(--bg-elevated)] border-t border-[var(--border-subtle)];
}

.alert-footer:hover { @apply text-[var(--accent-primary)]; }

/* IM状态 */
.im-status { @apply relative cursor-pointer p-2 rounded-lg hover:bg-[var(--bg-elevated)]; }
.im-icon { @apply text-xl; }
.im-badge {
  @apply absolute -top-1 -right-1 w-5 h-5 rounded-full bg-[var(--danger)] text-white text-xs flex items-center justify-center;
}

/* 会员Badge */
.member-badge { @apply flex items-center gap-2 px-3 py-1.5 rounded-full border cursor-pointer transition-all; }
.member-guest { @apply bg-[rgba(255,212,59,0.15)] border-[rgba(255,212,59,0.3)] text-[var(--warning)]; }
.member-subscriber { @apply bg-[rgba(0,187,249,0.15)] border-[rgba(0,187,249,0.3)] text-[var(--accent-secondary)]; }
.member-member { @apply bg-[rgba(157,78,221,0.15)] border-[rgba(157,78,221,0.3)] text-[var(--accent-purple)]; }
.member-lp { @apply bg-[rgba(255,215,0,0.15)] border-[rgba(255,215,0,0.3)] text-[var(--gold)]; }
.member-expert { @apply bg-[rgba(0,245,212,0.15)] border-[rgba(0,245,212,0.3)] text-[var(--accent-primary)]; }
.member-icon { @apply text-sm; }
.member-text { @apply text-sm font-semibold; }

/* 按钮 */
.btn { @apply px-4 py-2 rounded-lg font-semibold cursor-pointer transition-all inline-flex items-center gap-2 border-none; }
.btn-primary { background: linear-gradient(135deg, var(--accent-primary), #00b8a3); color: var(--bg-primary); }
.btn-outline { background: transparent; border: 1px solid var(--border-subtle); color: var(--text-secondary); }
.btn-outline:hover { border-color: var(--accent-primary); color: var(--accent-primary); }
</style>
