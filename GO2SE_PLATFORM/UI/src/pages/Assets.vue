<template>
  <div class="page-container">
    <h1 class="page-title">{{ pageTitle }}</h1>
    <div class="placeholder">
      <span class="placeholder-icon">{{ pageIcon }}</span>
      <p>页面开发中...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageName',
  computed: {
    pageTitle() {
      return this.$route.meta.title || 'Page'
    },
    pageIcon() {
      const icons = {
        '首页纵览': '🏠', '热点纵览': '🔥', '参数仪表盘': '📊', '资产看板': '💰',
        '投资组合': '📈', '策略模型': '♟️', '声纳趋势': '📡', '预言机': '🔮',
        '生态工具': '🛠️', '脚本日志': '📝', '分享有礼': '🎁', '私募LP': '💎', '客服中心': '💬'
      }
      return icons[this.$route.meta.title] || '📄'
    }
  }
}
</script>

<style scoped>
.page-container { padding-bottom: 2rem; }
.page-title { @apply text-2xl font-bold mb-6; }
.placeholder { @apply flex flex-col items-center justify-center py-20 text-[var(--text-secondary)]; }
.placeholder-icon { @apply text-6xl mb-4; }
</style>
