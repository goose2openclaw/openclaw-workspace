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

      <!-- 状态呼吸灯 -->
      <div class="status-indicator" :class="systemStatus">
        <span class="status-dot"></span>
        <span class="status-text">{{ statusText }}</span>
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
import { ref, computed } from 'vue'

export default {
  name: 'AppHeader',
  setup() {
    const theme = ref('dark')
    const currentLang = ref('zh')
    const systemStatus = ref('online') // online, offline, warning
    const unreadCount = ref(3)
    const memberType = ref('guest') // guest, subscriber, member, lp, expert

    const statusText = computed(() => {
      const texts = {
        online: '系统正常',
        offline: '系统异常',
        warning: '维护中'
      }
      return texts[systemStatus.value] || '未知'
    })

    const memberIcon = computed(() => {
      const icons = {
        guest: '👤',
        subscriber: '📦',
        member: '👑',
        lp: '🏛️',
        expert: '🎯'
      }
      return icons[memberType.value] || '👤'
    })

    const memberText = computed(() => {
      const texts = {
        guest: '游客',
        subscriber: '订阅会员',
        member: '正式会员',
        lp: '私募LP',
        expert: '专家'
      }
      return texts[memberType.value] || '游客'
    })

    const memberClass = computed(() => `member-${memberType.value}`)

    const setTheme = (t) => {
      theme.value = t
      document.documentElement.setAttribute('data-theme', t)
    }

    const changeLang = () => {
      // 触发语言切换事件
    }

    const goHome = () => {
      // 跳转首页
    }

    const openIM = () => {
      // 打开IM
    }

    const showMemberInfo = () => {
      // 显示会员信息
    }

    const showLogin = () => {
      // 显示登录
    }

    const showRegister = () => {
      // 显示注册
    }

    return {
      theme,
      currentLang,
      systemStatus,
      statusText,
      unreadCount,
      memberType,
      memberIcon,
      memberText,
      memberClass,
      setTheme,
      changeLang,
      goHome,
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

.logo-text {
  @apply flex flex-col;
}

.brand {
  @apply text-xl font-bold;
  background: linear-gradient(135deg, var(--text-primary), var(--accent-primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.slogan {
  @apply text-xs text-[var(--text-muted)];
}

.control-area {
  @apply flex items-center gap-4;
}

/* 主题选择器 */
.theme-selector {
  @apply flex gap-1 bg-[var(--bg-elevated)] p-1 rounded-lg;
}

.theme-btn {
  @apply px-2 py-1 rounded text-sm cursor-pointer border-none transition-all;
  background: transparent;
  color: var(--text-muted);
}

.theme-btn:hover {
  color: var(--text-primary);
}

.theme-btn.active {
  background: var(--accent-primary);
  color: var(--bg-primary);
}

/* 语言选择 */
.lang-selector select {
  @apply bg-[var(--bg-elevated)] border border-[var(--border-subtle)] rounded px-2 py-1 text-sm;
  color: var(--text-primary);
}

/* 状态呼吸灯 */
.status-indicator {
  @apply flex items-center gap-2 px-3 py-1.5 rounded-full;
}

.status-dot {
  @apply w-2 h-2 rounded-full;
}

.status-indicator.online .status-dot {
  background: var(--success);
  animation: breathe 2s ease-in-out infinite;
}

.status-indicator.offline .status-dot {
  background: var(--danger);
}

.status-indicator.warning .status-dot {
  background: var(--warning);
  animation: breathe 1s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { opacity: 0.4; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.1); }
}

.status-text {
  @apply text-xs text-[var(--text-secondary)];
}

/* IM状态 */
.im-status {
  @apply relative cursor-pointer p-2 rounded-lg hover:bg-[var(--bg-elevated)];
}

.im-icon {
  @apply text-xl;
}

.im-badge {
  @apply absolute -top-1 -right-1 w-5 h-5 rounded-full bg-[var(--danger)] text-white text-xs flex items-center justify-center;
}

/* 会员Badge */
.member-badge {
  @apply flex items-center gap-2 px-3 py-1.5 rounded-full border cursor-pointer transition-all;
}

.member-guest {
  @apply bg-[rgba(255,212,59,0.15)] border-[rgba(255,212,59,0.3)] text-[var(--warning)];
}

.member-subscriber {
  @apply bg-[rgba(0,187,249,0.15)] border-[rgba(0,187,249,0.3)] text-[var(--accent-secondary)];
}

.member-member {
  @apply bg-[rgba(157,78,221,0.15)] border-[rgba(157,78,221,0.3)] text-[var(--accent-purple)];
}

.member-lp {
  @apply bg-[rgba(255,215,0,0.15)] border-[rgba(255,215,0,0.3)] text-[var(--gold)];
}

.member-expert {
  @apply bg-[rgba(0,245,212,0.15)] border-[rgba(0,245,212,0.3)] text-[var(--accent-primary)];
}

.member-icon {
  @apply text-sm;
}

.member-text {
  @apply text-sm font-semibold;
}

/* 按钮 */
.btn {
  @apply px-4 py-2 rounded-lg font-semibold cursor-pointer transition-all inline-flex items-center gap-2 border-none;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-primary), #00b8a3);
  color: var(--bg-primary);
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
</style>
