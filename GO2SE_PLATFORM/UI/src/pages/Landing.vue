<template>
  <div class="landing" @click="enterApp">
    <div class="bg-mesh"></div>
    <div class="landing-content">
      <!-- Logo动画 -->
      <div class="logo-container">
        <div class="logo-glow"></div>
        <div class="logo">🪿</div>
      </div>

      <!-- 标题 -->
      <h1 class="title">Go2Se 护食的小白鹅</h1>
      <p class="subtitle">主动捡漏薅羊毛 | Crypto量化AI投资平台</p>

      <!-- 加载进度 -->
      <div class="loading-container" v-if="loading">
        <div class="loading-bar">
          <div class="loading-progress" :style="{ width: progress + '%' }"></div>
        </div>
        <p class="loading-text">{{ loadingText }}</p>
      </div>

      <!-- 点击进入 -->
      <p class="hint" v-else>点击任意处进入</p>
    </div>

    <!-- 版本信息 -->
    <div class="version">
      <span>GO2SE v9.2</span>
      <span>•</span>
      <span>2026.04.04</span>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Landing',
  emits: ['hidden'],
  setup(props, { emit }) {
    const router = useRouter()
    const progress = ref(0)
    const loading = ref(true)
    const loadingText = ref('初始化...')

    const steps = [
      { progress: 20, text: '加载配置...' },
      { progress: 40, text: '连接服务器...' },
      { progress: 60, text: '同步数据...' },
      { progress: 80, text: '渲染界面...' },
      { progress: 100, text: '准备就绪!' },
    ]

    const enterApp = () => {
      if (!loading.value) {
        emit('hidden')
        router.push('/focus')
      }
    }

    onMounted(() => {
      let i = 0
      const interval = setInterval(() => {
        if (i < steps.length) {
          progress.value = steps[i].progress
          loadingText.value = steps[i].text
          i++
        } else {
          clearInterval(interval)
          setTimeout(() => {
            loading.value = false
          }, 300)
        }
      }, 400)
    })

    return {
      progress,
      loading,
      loadingText,
      enterApp,
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
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
  overflow: hidden;
}

.bg-mesh {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(ellipse at 20% 20%, rgba(0, 245, 212, 0.08), transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(157, 78, 221, 0.06), transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(0, 187, 249, 0.04), transparent 70%);
  pointer-events: none;
}

.landing-content {
  text-align: center;
  z-index: 1;
}

.logo-container {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto 2rem;
}

.logo-glow {
  position: absolute;
  top: -20px;
  left: -20px;
  right: -20px;
  bottom: -20px;
  background: radial-gradient(circle, rgba(0, 245, 212, 0.3), transparent 70%);
  border-radius: 50%;
  animation: pulseGlow 2s ease-in-out infinite;
}

@keyframes pulseGlow {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

.logo {
  position: relative;
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-purple), var(--accent-secondary));
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  margin: 0 auto;
  animation: float 3s ease-in-out infinite, spin 8s linear infinite;
  box-shadow: 0 10px 40px rgba(0, 245, 212, 0.4);
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(5deg); }
}

@keyframes spin {
  0% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-15px) rotate(5deg); }
  50% { transform: translateY(0) rotate(0deg); }
  75% { transform: translateY(-15px) rotate(-5deg); }
  100% { transform: translateY(0) rotate(0deg); }
}

.title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 50%, var(--accent-purple) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
  animation: fadeIn 1s ease-out;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1.1rem;
  margin-bottom: 3rem;
  animation: fadeIn 1s ease-out 0.3s backwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.loading-container {
  margin-top: 2rem;
}

.loading-bar {
  width: 200px;
  height: 4px;
  background: var(--bg-elevated);
  border-radius: 2px;
  overflow: hidden;
  margin: 0 auto;
}

.loading-progress {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-purple));
  border-radius: 2px;
  transition: width 0.3s ease;
}

.loading-text {
  margin-top: 1rem;
  color: var(--text-muted);
  font-size: 0.85rem;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.hint {
  margin-top: 3rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); opacity: 0.5; }
  50% { transform: translateY(-10px); opacity: 1; }
}

.version {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.75rem;
}
</style>
