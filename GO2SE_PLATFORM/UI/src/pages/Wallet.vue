<template>
  <AppLayout>
    <div class="page-placeholder">
      <h2>{{ pageName }}</h2>
      <p>页面开发中...</p>
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'PageName',
  components: { AppLayout },
  computed: {
    pageName() {
      return this.$route.name || 'Page'
    }
  }
}
</script>

<style scoped>
.page-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  color: var(--text-secondary);
}
</style>
