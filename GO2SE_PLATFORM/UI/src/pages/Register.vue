<template>
  <div class="register-page">
    <div class="register-card">
      <div class="logo">🪿</div>
      <h1 class="title">注册 GO2SE</h1>
      <p class="subtitle">开启量化投资之旅</p>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="email" type="email" class="input" placeholder="请输入邮箱" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" class="input" placeholder="请设置密码" required />
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input v-model="confirmPassword" type="password" class="input" placeholder="请确认密码" required />
        </div>
        <div class="form-group checkbox">
          <input v-model="agree" type="checkbox" id="agree" required />
          <label for="agree">我同意 <span class="link">服务条款</span> 和 <span class="link">隐私政策</span></label>
        </div>
        <button type="submit" class="btn btn-primary w-full" :disabled="!agree">注册</button>
      </form>
      
      <div class="register-footer">
        <span>已有账号?</span>
        <router-link to="/login" class="link">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const email = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const agree = ref(false)

    const handleRegister = () => {
      if (password.value !== confirmPassword.value) {
        alert('两次密码输入不一致')
        return
      }
      // TODO: 调用注册API
      router.push('/dashboard')
    }

    return { email, password, confirmPassword, agree, handleRegister }
  },
}
</script>

<style scoped>
.register-page {
  @apply min-h-screen flex items-center justify-center bg-[var(--bg-primary)];
  background: radial-gradient(ellipse at 15% 15%, rgba(0,245,212,0.06), transparent 50%),
              radial-gradient(ellipse at 85% 85%, rgba(157,78,221,0.05), transparent 50%);
}

.register-card {
  @apply w-full max-w-md p-8 rounded-2xl;
  @apply bg-[var(--bg-card)] border border-[var(--border-subtle)];
}

.logo { @apply text-6xl text-center mb-4; }
.title { @apply text-3xl font-bold text-center; }
.subtitle { @apply text-center text-[var(--text-secondary)] mb-8; }

.register-form { @apply space-y-4; }
.form-group { @apply space-y-2; }
.form-group label { @apply text-sm text-[var(--text-secondary)]; }
.form-group.checkbox { @apply flex items-center gap-2; }
.form-group.checkbox input { @apply w-4 h-4; }
.form-group.checkbox label { @apply text-sm cursor-pointer; }
.link { @apply text-[var(--accent-primary)] hover:underline; }

.btn { @apply w-full justify-center; }
.btn-primary { @apply bg-gradient-to-r from-[var(--accent-primary)] to-[#00b8a3] text-[var(--bg-primary)]; }
.btn-primary:disabled { @apply opacity-50 cursor-not-allowed; }

.register-footer { @apply mt-6 text-center text-sm text-[var(--text-secondary)]; }
.link { @apply text-[var(--accent-primary)] ml-1 hover:underline; }
</style>
