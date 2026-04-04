<template>
  <div id="app" :data-theme="theme">
    <!-- 启动页 -->
    <Landing v-if="showLanding" @hidden="showLanding = false" />

    <!-- 主应用 -->
    <template v-else>
      <AppHeader />
      <AppCanvas />
    </template>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppCanvas from '@/components/AppCanvas.vue'
import Landing from '@/pages/Landing.vue'

export default {
  name: 'App',
  components: {
    AppHeader,
    AppCanvas,
    Landing,
  },
  setup() {
    const theme = ref('dark')
    const showLanding = ref(true)

    onMounted(() => {
      // 检查是否首次访问
      const visited = localStorage.getItem('go2se_visited')
      if (visited) {
        showLanding.value = false
      }

      // 5秒后自动隐藏
      setTimeout(() => {
        showLanding.value = false
        localStorage.setItem('go2se_visited', 'true')
      }, 5000)
    })

    return {
      theme,
      showLanding,
    }
  },
}
</script>

<style>
/* CSS Variables */
:root,
[data-theme="dark"] {
  --bg-primary: #07080c;
  --bg-secondary: #0c0f14;
  --bg-card: #10141c;
  --bg-elevated: #161c26;
  --accent-primary: #00f5d4;
  --accent-secondary: #00bbf9;
  --accent-purple: #9d4edd;
  --text-primary: #f0f2f5;
  --text-secondary: #8b8d94;
  --text-muted: #4a4c56;
  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-active: rgba(0, 245, 212, 0.3);
  --success: #00f5a0;
  --danger: #ff4757;
  --warning: #ffd43b;
  --gold: #ffd700;
}

[data-theme="light"] {
  --bg-primary: #f5f7fa;
  --bg-secondary: #ffffff;
  --bg-card: #ffffff;
  --bg-elevated: #f0f2f5;
  --accent-primary: #00a884;
  --accent-secondary: #0099cc;
  --accent-purple: #7c3aed;
  --text-primary: #1a1a2e;
  --text-secondary: #4a5568;
  --text-muted: #a0aec0;
  --border-subtle: rgba(0, 0, 0, 0.06);
  --border-active: rgba(0, 168, 132, 0.3);
  --success: #00a884;
  --danger: #e53e3e;
  --warning: #d69e2e;
  --gold: #b7791f;
}

[data-theme="matrix"] {
  --bg-primary: #0a0a0a;
  --bg-secondary: #0f0f0f;
  --bg-card: #1a1a1a;
  --bg-elevated: #252525;
  --accent-primary: #00ff00;
  --accent-secondary: #00cc00;
  --accent-purple: #00ff00;
  --text-primary: #00ff00;
  --text-secondary: #00cc00;
  --text-muted: #008800;
  --border-subtle: rgba(0, 255, 0, 0.1);
  --success: #00ff00;
  --danger: #ff0000;
  --warning: #ffff00;
  --gold: #ffff00;
}

/* Base Styles */
body {
  margin: 0;
  padding: 0;
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--text-muted);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>
