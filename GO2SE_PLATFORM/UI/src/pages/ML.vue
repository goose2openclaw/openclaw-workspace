<template>
  <div class="page-container">
    <h1 class="page-title">{{ pageIcon }} {{ pageTitle }}</h1>
    <div class="placeholder-card">
      <p>页面开发中...</p>
      <div class="feature-list">
        <div v-for="(feature, i) in features" :key="i" class="feature-item">
          <span class="feature-icon">{{ feature.icon }}</span>
          <span>{{ feature.text }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageName',
  computed: {
    pageTitle() { return this.$route.meta.title || 'Page' },
    pageIcon() { return this.$route.meta.icon || '📄' },
    features() {
      const map = {
        '💰': ['财产总额', '收益详情', '钱包架构', '资产分配', '模拟器'],
        '💼': ['薅羊毛配置', '穷孩子配置', '安全机制'],
        '🖥️': ['节点状态', '响应度', '延时监控'],
        '📡': ['Oracle', 'API', '情绪', '仿真信号'],
        '♟️': ['策略组合', '仿真模拟', '克隆策略'],
        '🔒': ['资金安全', '后门管控', '防崩溃'],
        '🤖': ['竞品监控', '自主迭代', '因子退化'],
      }
      const icon = this.$route.meta.icon
      return (map[icon] || ['功能开发中']).map(t => ({ icon: '•', text: t }))
    }
  }
}
</script>

<style scoped>
.page-container { @apply pb-8; }
.page-title { @apply text-2xl font-bold mb-6; }
.placeholder-card { @apply bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-8 text-center text-[var(--text-secondary)]; }
.feature-list { @apply mt-6 space-y-3; }
.feature-item { @apply flex items-center justify-center gap-2; }
.feature-icon { @apply text-[var(--accent-primary)]; }
</style>
