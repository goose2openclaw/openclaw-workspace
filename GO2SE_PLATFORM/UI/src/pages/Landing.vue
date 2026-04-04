<template>
  <div class="landing" @click="hideLanding">
    <div class="bg-mesh"></div>
    <div class="landing-content">
      <div class="landing-logo">🪿</div>
      <h1 class="landing-title">Go2Se 护食的小白鹅</h1>
      <p class="landing-subtitle">主动捡漏薅羊毛 | Crypto量化AI投资平台</p>
      <p class="landing-hint">点击任意处进入</p>
    </div>
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
    const loadingText = ref('初始化...')

    const steps = [
      { progress: 20, text: '加载配置...' },
      { progress: 40, text: '连接服务器...' },
      { progress: 60, text: '同步数据...' },
      { progress: 80, text: '渲染界面...' },
      { progress: 100, text: '准备就绪!' },
    ]

    const hideLanding = () => {
      // 动画然后跳转
      const landing = document.querySelector('.landing')
      if (landing) {
        landing.classList.add('hidden')
        setTimeout(() => {
          router.push('/home')
        }, 500)
      }
    }

    onMounted(() => {
      // 模拟加载进度
      let i = 0
      const interval = setInterval(() => {
        if (i < steps.length) {
          loadingProgress.value = steps[i].progress
          loadingText.value = steps[i].text
          i++
        } else {
          clearInterval(interval)
        }
      }, 300)
    })

    return {
      loadingProgress,
      loadingText,
      hideLanding,
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
  transition: all 0.8s ease;
}

.landing.hidden {
  opacity: 0;
  visibility: hidden;
  transform: scale(0.8);
}

.bg-mesh {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(ellipse at 15% 15%, rgba(0, 245, 212, 0.06), transparent 50%),
    radial-gradient(ellipse at 85% 85%, rgba(157, 78, 221, 0.05), transparent 50%);
  pointer-events: none;
}

.landing-content {
  text-align: center;
  z-index: 1;
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
  margin: 0 auto 2rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.landing-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 50%, var(--accent-purple) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.landing-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
  margin-bottom: 2rem;
}

.landing-hint {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-top: 3rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
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
  transition: width 0.3s ease;
}

.loading-text {
  margin-top: 1rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}
</style>
