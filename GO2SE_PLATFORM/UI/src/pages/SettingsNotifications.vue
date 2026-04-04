<template>
  <AppLayout>
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">{{ pageTitle }}</h1>
      </div>
      <div class="page-content">
        <div class="placeholder-card">
          <span class="placeholder-icon">{{ pageIcon }}</span>
          <p>页面开发中...</p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'PageName',
  components: { AppLayout },
  computed: {
    pageTitle() {
      return this.$route.meta.title || 'Page'
    },
    pageIcon() {
      const icons = { K线:'📊', Signal:'📡', Trading:'💹', Wallet:'💰', Settings:'⚡', Strategy:'⚙️' }
      return icons[this.$route.meta.parent] || '📄'
    }
  }
}
</script>

<style scoped>
.page-container { @apply pb-8; }
.page-header { @apply mb-6; }
.page-title { @apply text-2xl font-bold; }
.placeholder-card { @apply flex flex-col items-center justify-center py-20 text-[var(--text-secondary)]; }
.placeholder-icon { @apply text-6xl mb-4; }
</style>
