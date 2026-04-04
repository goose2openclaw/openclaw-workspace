/**
 * GO2SE Main Entry
 * =================
 * Vue3 + Pinia + Router + GO2SE Integration
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './styles/main.css'

// GO2SE Integration Layer
import GO2SE from '../integration/index.js'

const app = createApp(App)
const pinia = createPinia()

// 初始化 GO2SE Integration
GO2SE.init(app, pinia, router, {
  autoConnect: true,
})

app.use(pinia)
app.use(router)

app.mount('#app')

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err, info);
};
