/**
 * VV6 Auth Module - 登录注册模块
 */

class VV6Auth {
  constructor() {
    this.API_BASE = 'http://localhost:8000';
    this.currentUser = null;
    this.isLoggedIn = false;
    this.init();
  }

  init() {
    this.checkAuthStatus();
  }

  // 检查登录状态
  async checkAuthStatus() {
    const token = localStorage.getItem('vv6_token');
    if (token) {
      try {
        const res = await fetch(`${this.API_BASE}/api/auth/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const user = await res.json();
          this.currentUser = user;
          this.isLoggedIn = true;
          this.updateUI();
          return true;
        }
      } catch (e) {}
    }
    this.showLoginModal();
    return false;
  }

  // 显示登录/注册弹窗
  showLoginModal(type = 'login') {
    const modal = document.getElementById('authModal') || this.createModal();
    modal.querySelector('.auth-content').innerHTML = this.getAuthForm(type);
    modal.classList.add('active');
    this.bindAuthEvents(modal);
  }

  // 创建弹窗
  createModal() {
    const modal = document.createElement('div');
    modal.id = 'authModal';
    modal.className = 'auth-modal';
    modal.innerHTML = `
      <div class="auth-overlay"></div>
      <div class="auth-content"></div>
    `;
    document.body.appendChild(modal);
    
    // 添加样式
    if (!document.getElementById('authStyles')) {
      const style = document.createElement('style');
      style.id = 'authStyles';
      style.textContent = `
        .auth-modal {
          display: none;
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 10000;
          align-items: center;
          justify-content: center;
        }
        .auth-modal.active { display: flex; }
        .auth-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.8);
        }
        .auth-content {
          position: relative;
          background: var(--bg-secondary);
          border: 1px solid var(--border-color);
          border-radius: 16px;
          padding: 32px;
          width: 90%;
          max-width: 400px;
          box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .auth-header {
          text-align: center;
          margin-bottom: 24px;
        }
        .auth-header h2 {
          font-size: 24px;
          color: var(--primary);
          margin: 0 0 8px 0;
        }
        .auth-header p {
          color: var(--text-dim);
          font-size: 14px;
          margin: 0;
        }
        .auth-form {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .form-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .form-group label {
          font-size: 13px;
          color: var(--text-dim);
        }
        .form-group input {
          padding: 12px 16px;
          background: var(--bg-primary);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          color: var(--text);
          font-size: 14px;
        }
        .form-group input:focus {
          outline: none;
          border-color: var(--primary);
        }
        .auth-btn {
          padding: 14px;
          background: var(--primary);
          color: #000;
          border: none;
          border-radius: 8px;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }
        .auth-btn:hover { opacity: 0.9; }
        .auth-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .auth-footer {
          text-align: center;
          margin-top: 20px;
          font-size: 13px;
          color: var(--text-dim);
        }
        .auth-footer a {
          color: var(--primary);
          cursor: pointer;
          text-decoration: none;
        }
        .auth-footer a:hover { text-decoration: underline; }
        .auth-error {
          background: rgba(255,0,0,0.1);
          border: 1px solid rgba(255,0,0,0.3);
          border-radius: 8px;
          padding: 12px;
          color: #ff6b6b;
          font-size: 13px;
          display: none;
        }
        .auth-error.show { display: block; }
        .auth-close {
          position: absolute;
          top: 16px;
          right: 16px;
          background: none;
          border: none;
          color: var(--text-dim);
          font-size: 24px;
          cursor: pointer;
        }
      `;
      document.head.appendChild(style);
    }
    
    return modal;
  }

  // 获取表单HTML
  getAuthForm(type) {
    if (type === 'login') {
      return `
        <button class="auth-close" onclick="vv6Auth.closeModal()">&times;</button>
        <div class="auth-header">
          <h2>🦞</h2>
          <h2>登录 vv6</h2>
          <p>GO2SE Genius 交易系统</p>
        </div>
        <div class="auth-error" id="authError"></div>
        <form class="auth-form" onsubmit="vv6Auth.handleLogin(event)">
          <div class="form-group">
            <label>用户名 / 邮箱</label>
            <input type="text" name="username" required placeholder="输入用户名或邮箱">
          </div>
          <div class="form-group">
            <label>密码</label>
            <input type="password" name="password" required placeholder="输入密码">
          </div>
          <button type="submit" class="auth-btn">登录</button>
        </form>
        <div class="auth-footer">
          还没有账号? <a onclick="vv6Auth.showLoginModal('register')">立即注册</a>
        </div>
      `;
    } else {
      return `
        <button class="auth-close" onclick="vv6Auth.closeModal()">&times;</button>
        <div class="auth-header">
          <h2>🦞</h2>
          <h2>注册 vv6</h2>
          <p>创建 GO2SE Genius 账号</p>
        </div>
        <div class="auth-error" id="authError"></div>
        <form class="auth-form" onsubmit="vv6Auth.handleRegister(event)">
          <div class="form-group">
            <label>用户名</label>
            <input type="text" name="username" required placeholder="设置用户名" minlength="3">
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input type="email" name="email" required placeholder="输入邮箱地址">
          </div>
          <div class="form-group">
            <label>密码</label>
            <input type="password" name="password" required placeholder="设置密码" minlength="6">
          </div>
          <div class="form-group">
            <label>确认密码</label>
            <input type="password" name="confirmPassword" required placeholder="确认密码">
          </div>
          <button type="submit" class="auth-btn">注册</button>
        </form>
        <div class="auth-footer">
          已有账号? <a onclick="vv6Auth.showLoginModal('login')">立即登录</a>
        </div>
      `;
    }
  }

  // 绑定事件
  bindAuthEvents(modal) {
    modal.querySelector('.auth-overlay').onclick = () => this.closeModal();
  }

  // 关闭弹窗
  closeModal() {
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.remove('active');
  }

  // 处理登录
  async handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const btn = form.querySelector('.auth-btn');
    const errorEl = document.getElementById('authError');
    
    const username = form.username.value;
    const password = form.password.value;
    
    btn.disabled = true;
    btn.textContent = '登录中...';
    errorEl.classList.remove('show');
    
    try {
      const res = await fetch(`${this.API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await res.json();
      
      if (res.ok) {
        localStorage.setItem('vv6_token', data.token);
        this.currentUser = data.user || { username };
        this.isLoggedIn = true;
        this.closeModal();
        this.updateUI();
      } else {
        errorEl.textContent = data.message || '登录失败';
        errorEl.classList.add('show');
      }
    } catch (e) {
      errorEl.textContent = '网络错误，请重试';
      errorEl.classList.add('show');
    }
    
    btn.disabled = false;
    btn.textContent = '登录';
  }

  // 处理注册
  async handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const btn = form.querySelector('.auth-btn');
    const errorEl = document.getElementById('authError');
    
    const username = form.username.value;
    const email = form.email.value;
    const password = form.password.value;
    const confirmPassword = form.confirmPassword.value;
    
    if (password !== confirmPassword) {
      errorEl.textContent = '两次密码输入不一致';
      errorEl.classList.add('show');
      return;
    }
    
    btn.disabled = true;
    btn.textContent = '注册中...';
    errorEl.classList.remove('show');
    
    try {
      const res = await fetch(`${this.API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });
      
      const data = await res.json();
      
      if (res.ok) {
        localStorage.setItem('vv6_token', data.token);
        this.currentUser = data.user || { username, email };
        this.isLoggedIn = true;
        this.closeModal();
        this.updateUI();
      } else {
        errorEl.textContent = data.message || '注册失败';
        errorEl.classList.add('show');
      }
    } catch (e) {
      errorEl.textContent = '网络错误，请重试';
      errorEl.classList.add('show');
    }
    
    btn.disabled = false;
    btn.textContent = '注册';
  }

  // 登出
  logout() {
    localStorage.removeItem('vv6_token');
    this.currentUser = null;
    this.isLoggedIn = false;
    this.updateUI();
    this.showLoginModal();
  }

  // 更新UI
  updateUI() {
    const statusEl = document.getElementById('backendStatus');
    const statusIndicator = document.querySelector('.vv6-status');
    
    if (this.isLoggedIn && this.currentUser) {
      if (statusIndicator) {
        statusIndicator.innerHTML = `
          <span class="vv6-status-dot" style="background: var(--primary);"></span>
          <span style="color: var(--primary);">${this.currentUser.username || '已登录'}</span>
          <button onclick="vv6Auth.logout()" style="
            margin-left: 8px;
            padding: 2px 8px;
            background: transparent;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            color: var(--text-dim);
            font-size: 11px;
            cursor: pointer;
          ">退出</button>
        `;
      }
    }
  }
}

// 全局实例
const vv6Auth = new VV6Auth();
window.vv6Auth = vv6Auth;
