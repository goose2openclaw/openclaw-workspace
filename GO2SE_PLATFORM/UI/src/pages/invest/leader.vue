<template>
  <div class="sub-page">
    <h2>{{ pageTitle }}</h2>
    <div class="placeholder">
      <p>invest/leader - 页面开发中...</p>
    </div>
  </div>
</template>
<script>
export default {
  name: 'PageLEADER',
  computed: {
    pageTitle() { return this.$route.path }
  }
}
</script>
<style scoped>
.sub-page { padding-bottom: 2rem; }
h2 { font-size: 1.25rem; font-weight: bold; margin-bottom: 1rem; }
.placeholder { background: var(--bg-card); border-radius: 0.75rem; padding: 2rem; text-align: center; color: var(--text-secondary); }
</style>
