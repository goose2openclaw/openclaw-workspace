<template>
  <div class="landing">
    <div class="landing-logo">🪿</div>
    <h1 class="landing-title">GO2SE</h1>
    <p class="landing-subtitle">北斗七鑫量化投资平台</p>
    <div class="loading-bar">
      <div class="loading-progress" :style="{ width: loadingProgress + '%' }"></div>
    </div>
    <p class="loading-text">{{ loadingText }}</p>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Landing',
  setup() {
    const router = useRouter()
    const loadingProgress = ref(0)
    const loadingText = ref('初始化组件...')

    const steps = [
      { progress: 20, text: '加载配置...' },
      { progress: 40, text: '连接服务器...' },
      { progress: 60, text: '同步数据...' },
      { progress: 80, text: '渲染界面...' },
      { progress: 100, text: '准备就绪!' },
    ]

    onMounted(() => {
      let i = 0
      const interval = setInterval(() => {
        if (i < steps.length) {
          loadingProgress.value = steps[i].progress
          loadingText.value = steps[i].text
          i++
        } else {
          clearInterval(interval)
          setTimeout(() => {
            router.push('/dashboard')
          }, 500)
        }
      }, 400)
    })

    return {
      loadingProgress,
      loadingText,
    }
  },
}
</script>

<style scoped>
.landing {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.landing-logo {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-purple), var(--accent-secondary));
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  margin-bottom: 2rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.landing-title {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 50%, var(--accent-purple) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.landing-subtitle {
  color: var(--text-secondary);
  font-size: 1.2rem;
  margin-bottom: 3rem;
}

.loading-bar {
  width: 200px;
  height: 4px;
  background: var(--bg-elevated);
  border-radius: 2px;
  overflow: hidden;
}

.loading-progress {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-purple));
  transition: width 0.3s ease;
}

.loading-text {
  margin-top: 1rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}
</style>
