<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo">🪿</div>
      <h1 class="title">GO2SE</h1>
      <p class="subtitle">北斗七鑫量化投资平台</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="email" type="email" class="input" placeholder="请输入邮箱" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" class="input" placeholder="请输入密码" required />
        </div>
        <button type="submit" class="btn btn-primary w-full">登录</button>
      </form>
      
      <div class="login-footer">
        <span>还没有账号?</span>
        <router-link to="/register" class="link">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const email = ref('')
    const password = ref('')

    const handleLogin = () => {
      // TODO: 调用登录API
      router.push('/dashboard')
    }

    return { email, password, handleLogin }
  },
}
</script>

<style scoped>
.login-page {
  @apply min-h-screen flex items-center justify-center bg-[var(--bg-primary)];
  background: radial-gradient(ellipse at 15% 15%, rgba(0,245,212,0.06), transparent 50%),
              radial-gradient(ellipse at 85% 85%, rgba(157,78,221,0.05), transparent 50%);
}

.login-card {
  @apply w-full max-w-md p-8 rounded-2xl;
  @apply bg-[var(--bg-card)] border border-[var(--border-subtle)];
}

.logo { @apply text-6xl text-center mb-4; }
.title { @apply text-3xl font-bold text-center bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-purple)] bg-clip-text text-transparent; }
.subtitle { @apply text-center text-[var(--text-secondary)] mb-8; }

.login-form { @apply space-y-4; }
.form-group { @apply space-y-2; }
.form-group label { @apply text-sm text-[var(--text-secondary)]; }

.btn { @apply w-full justify-center; }
.btn-primary { @apply bg-gradient-to-r from-[var(--accent-primary)] to-[#00b8a3] text-[var(--bg-primary)]; }

.login-footer { @apply mt-6 text-center text-sm text-[var(--text-secondary)]; }
.link { @apply text-[var(--accent-primary)] ml-1 hover:underline; }
</style>
