<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GO2SE - Onboarding</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-primary: #0A0E17;
      --bg-secondary: #111827;
      --accent-primary: #00D4AA;
      --accent-secondary: #7C3AED;
      --accent-warning: #F59E0B;
      --text-primary: #F9FAFB;
      --text-secondary: #9CA3AF;
      --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: 'DM Sans', sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .onboarding {
      width: 100%;
      max-width: 800px;
      padding: 40px;
    }
    
    .step-indicator {
      display: flex;
      justify-content: center;
      gap: 12px;
      margin-bottom: 48px;
    }
    
    .step-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--bg-secondary);
      border: 2px solid var(--text-secondary);
      transition: all 0.3s var(--ease-out-expo);
    }
    
    .step-dot.active {
      background: var(--accent-primary);
      border-color: var(--accent-primary);
      transform: scale(1.2);
    }
    
    .step-dot.completed {
      background: var(--accent-primary);
      border-color: var(--accent-primary);
    }
    
    .step-content {
      display: none;
      animation: fadeIn 0.5s var(--ease-out-expo);
    }
    
    .step-content.active {
      display: block;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .step-card {
      background: var(--bg-secondary);
      border-radius: 24px;
      padding: 48px;
      text-align: center;
      border: 1px solid rgba(255,255,255,0.1);
    }
    
    .step-icon {
      font-size: 64px;
      margin-bottom: 24px;
    }
    
    .step-title {
      font-family: 'Sora', sans-serif;
      font-size: 28px;
      font-weight: 600;
      margin-bottom: 16px;
      background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .step-desc {
      color: var(--text-secondary);
      font-size: 16px;
      line-height: 1.6;
      margin-bottom: 32px;
    }
    
    .step-options {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }
    
    .option-card {
      background: var(--bg-primary);
      border: 2px solid transparent;
      border-radius: 16px;
      padding: 24px;
      cursor: pointer;
      transition: all 0.3s var(--ease-out-expo);
    }
    
    .option-card:hover {
      border-color: var(--accent-primary);
      transform: translateY(-4px);
    }
    
    .option-card.selected {
      border-color: var(--accent-primary);
      background: rgba(0, 212, 170, 0.1);
    }
    
    .option-icon {
      font-size: 32px;
      margin-bottom: 12px;
    }
    
    .option-title {
      font-weight: 600;
      margin-bottom: 8px;
    }
    
    .option-desc {
      font-size: 12px;
      color: var(--text-secondary);
    }
    
    .step-nav {
      display: flex;
      justify-content: space-between;
      margin-top: 32px;
    }
    
    .nav-btn {
      padding: 14px 32px;
      border: none;
      border-radius: 12px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s var(--ease-out-expo);
    }
    
    .nav-btn.primary {
      background: var(--accent-primary);
      color: var(--bg-primary);
    }
    
    .nav-btn.primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 212, 170, 0.3);
    }
    
    .nav-btn.secondary {
      background: var(--bg-primary);
      color: var(--text-secondary);
    }
    
    .nav-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none !important;
    }
    
    .progress-bar {
      height: 4px;
      background: var(--bg-secondary);
      border-radius: 2px;
      margin-bottom: 32px;
      overflow: hidden;
    }
    
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
      transition: width 0.5s var(--ease-out-expo);
    }
    
    /* Welcome specific */
    .welcome-goose {
      width: 120px;
      height: 120px;
      margin: 0 auto 32px;
      animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
    }
    
    /* Step 2: Experience */
    .experience-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }
    
    .experience-card {
      background: var(--bg-primary);
      border: 2px solid transparent;
      border-radius: 16px;
      padding: 24px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s var(--ease-out-expo);
    }
    
    .experience-card:hover {
      border-color: var(--accent-primary);
    }
    
    .experience-card.selected {
      border-color: var(--accent-primary);
      background: rgba(0, 212, 170, 0.1);
    }
    
    .experience-level {
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }
    
    .experience-icon {
      font-size: 40px;
      margin-bottom: 12px;
    }
    
    .experience-name {
      font-weight: 600;
    }
    
    /* Step 3: Goals */
    .goals-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
    }
    
    .goal-card {
      background: var(--bg-primary);
      border: 2px solid transparent;
      border-radius: 16px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      cursor: pointer;
      transition: all 0.3s var(--ease-out-expo);
    }
    
    .goal-card:hover {
      border-color: var(--accent-primary);
    }
    
    .goal-card.selected {
      border-color: var(--accent-primary);
      background: rgba(0, 212, 170, 0.1);
    }
    
    .goal-icon {
      font-size: 32px;
    }
    
    .goal-text h4 {
      font-size: 14px;
      margin-bottom: 4px;
    }
    
    .goal-text p {
      font-size: 12px;
      color: var(--text-secondary);
    }
    
    /* Step 4: Account */
    .account-form {
      max-width: 400px;
      margin: 0 auto;
    }
    
    .form-group {
      margin-bottom: 20px;
      text-align: left;
    }
    
    .form-label {
      display: block;
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 8px;
      color: var(--text-secondary);
    }
    
    .form-input {
      width: 100%;
      padding: 14px 16px;
      background: var(--bg-primary);
      border: 2px solid var(--border-color);
      border-radius: 12px;
      color: var(--text-primary);
      font-size: 16px;
      transition: border-color 0.3s;
    }
    
    .form-input:focus {
      outline: none;
      border-color: var(--accent-primary);
    }
    
    .form-checkbox {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 24px;
    }
    
    .form-checkbox input {
      width: 20px;
      height: 20px;
      accent-color: var(--accent-primary);
    }
    
    .form-checkbox label {
      font-size: 14px;
      color: var(--text-secondary);
    }
    
    /* Step 5: Complete */
    .complete-icon {
      font-size: 80px;
      margin-bottom: 24px;
    }
    
    .complete-title {
      font-size: 32px;
      font-weight: 700;
      margin-bottom: 16px;
    }
    
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin: 32px 0;
    }
    
    .summary-card {
      background: var(--bg-primary);
      border-radius: 12px;
      padding: 20px;
      text-align: center;
    }
    
    .summary-icon {
      font-size: 24px;
      margin-bottom: 8px;
    }
    
    .summary-value {
      font-size: 20px;
      font-weight: 600;
      color: var(--accent-primary);
    }
    
    .summary-label {
      font-size: 12px;
      color: var(--text-secondary);
    }
    
    .start-btn {
      padding: 18px 48px;
      background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
      border: none;
      border-radius: 16px;
      font-size: 18px;
      font-weight: 600;
      color: var(--bg-primary);
      cursor: pointer;
      transition: all 0.3s var(--ease-out-expo);
    }
    
    .start-btn:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 32px rgba(0, 212, 170, 0.4);
    }
    
    /* Skip link */
    .skip-link {
      text-align: center;
      margin-top: 24px;
    }
    
    .skip-link a {
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 14px;
      transition: color 0.3s;
    }
    
    .skip-link a:hover {
      color: var(--text-primary);
    }
  </style>
</head>
<body>
  <div class="onboarding">
    <div class="progress-bar">
      <div class="progress-fill" id="progressFill" style="width: 20%;"></div>
    </div>
    
    <div class="step-indicator">
      <div class="step-dot active" data-step="1"></div>
      <div class="step-dot" data-step="2"></div>
      <div class="step-dot" data-step="3"></div>
      <div class="step-dot" data-step="4"></div>
      <div class="step-dot" data-step="5"></div>
    </div>
    
    <!-- Step 1: Welcome -->
    <div class="step-content active" id="step1">
      <div class="step-card">
        <div class="welcome-goose">
          <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
            <ellipse cx="60" cy="65" rx="35" ry="28" fill="#00D4AA"/>
            <circle cx="85" cy="40" r="18" fill="#00D4AA"/>
            <circle cx="90" cy="36" r="4" fill="#0A0E17"/>
            <path d="M98 42 L108 44 L98 48 Z" fill="#F59E0B"/>
          </svg>
        </div>
        <h1 class="step-title">欢迎来到 GO2SE</h1>
        <p class="step-desc">
          AI驱动的加密货币量化投资平台<br>
          让我们用3分钟了解你的需求，为你定制最佳体验
        </p>
        <div class="step-nav">
          <div></div>
          <button class="nav-btn primary" onclick="nextStep()">开始设置 →</button>
        </div>
        <div class="skip-link">
          <a href="#" onclick="skipOnboarding()">跳过引导，直接进入</a>
        </div>
      </div>
    </div>
    
    <!-- Step 2: Experience Level -->
    <div class="step-content" id="step2">
      <div class="step-card">
        <div class="step-icon">📊</div>
        <h2 class="step-title">你的投资经验？</h2>
        <p class="step-desc">我们会根据你的经验水平推荐合适的工具和策略</p>
        
        <div class="experience-grid">
          <div class="experience-card" data-value="newbie" onclick="selectExperience(this)">
            <div class="experience-level">Level 1</div>
            <div class="experience-icon">🌱</div>
            <div class="experience-name">新手小白</div>
          </div>
          <div class="experience-card" data-value="basic" onclick="selectExperience(this)">
            <div class="experience-level">Level 2</div>
            <div class="experience-icon">📈</div>
            <div class="experience-name">有经验</div>
          </div>
          <div class="experience-card" data-value="pro" onclick="selectExperience(this)">
            <div class="experience-level">Level 3</div>
            <div class="experience-icon">🚀</div>
            <div class="experience-name">专业投资者</div>
          </div>
        </div>
        
        <div class="step-nav">
          <button class="nav-btn secondary" onclick="prevStep()">← 上一步</button>
          <button class="nav-btn primary" onclick="nextStep()" id="step2Next" disabled>下一步 →</button>
        </div>
      </div>
    </div>
    
    <!-- Step 3: Goals -->
    <div class="step-content" id="step3">
      <div class="step-card">
        <div class="step-icon">🎯</div>
        <h2 class="step-title">你的投资目标？</h2>
        <p class="step-desc">可多选，我们会为你定制专属策略组合</p>
        
        <div class="goals-grid">
          <div class="goal-card" data-value="stable" onclick="toggleGoal(this)">
            <div class="goal-icon">🛡️</div>
            <div class="goal-text">
              <h4>稳定收益</h4>
              <p>追求低风险、持续回报</p>
            </div>
          </div>
          <div class="goal-card" data-value="growth" onclick="toggleGoal(this)">
            <div class="goal-icon">📈</div>
            <div class="goal-text">
              <h4>资产增值</h4>
              <p>长期持有，价值投资</p>
            </div>
          </div>
          <div class="goal-card" data-value="hunting" onclick="toggleGoal(this)">
            <div class="goal-icon">🐹</div>
            <div class="goal-text">
              <h4>套利狩猎</h4>
              <p>抓住市场机会获利</p>
            </div>
          </div>
          <div class="goal-card" data-value="airdrop" onclick="toggleGoal(this)">
            <div class="goal-icon">💰</div>
            <div class="goal-text">
              <h4>空投薅羊毛</h4>
              <p>捕获新项目空投机会</p>
            </div>
          </div>
        </div>
        
        <div class="step-nav">
          <button class="nav-btn secondary" onclick="prevStep()">← 上一步</button>
          <button class="nav-btn primary" onclick="nextStep()" id="step3Next" disabled>下一步 →</button>
        </div>
      </div>
    </div>
    
    <!-- Step 4: Account -->
    <div class="step-content" id="step4">
      <div class="step-card">
        <div class="step-icon">🔐</div>
        <h2 class="step-title">创建你的账户</h2>
        <p class="step-desc">已有账户？<a href="#" style="color: var(--accent-primary);">登录</a></p>
        
        <div class="account-form">
          <div class="form-group">
            <label class="form-label">邮箱</label>
            <input type="email" class="form-input" placeholder="your@email.com" id="emailInput">
          </div>
          <div class="form-group">
            <label class="form-label">密码</label>
            <input type="password" class="form-input" placeholder="至少8位字符" id="passwordInput">
          </div>
          <div class="form-checkbox">
            <input type="checkbox" id="termsCheck">
            <label for="termsCheck">我同意 GO2SE <a href="#" style="color: var(--accent-primary);">服务条款</a> 和 <a href="#" style="color: var(--accent-primary);">隐私政策</a></label>
          </div>
        </div>
        
        <div class="step-nav">
          <button class="nav-btn secondary" onclick="prevStep()">← 上一步</button>
          <button class="nav-btn primary" onclick="completeOnboarding()" id="step4Next" disabled>完成 →</button>
        </div>
      </div>
    </div>
    
    <!-- Step 5: Complete -->
    <div class="step-content" id="step5">
      <div class="step-card">
        <div class="complete-icon">🎉</div>
        <h2 class="complete-title">准备就绪！</h2>
        <p class="step-desc">我们已根据你的需求配置好了专属体验</p>
        
        <div class="summary-grid">
          <div class="summary-card">
            <div class="summary-icon">📊</div>
            <div class="summary-value" id="summaryExp">专业投资者</div>
            <div class="summary-label">经验水平</div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">🎯</div>
            <div class="summary-value" id="summaryGoals">3个目标</div>
            <div class="summary-label">投资目标</div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">🛡️</div>
            <div class="summary-value">基础风控</div>
            <div class="summary-label">安全等级</div>
          </div>
        </div>
        
        <button class="start-btn" onclick="startApp()">开始使用 GO2SE 🪿</button>
      </div>
    </div>
  </div>

  <script>
    let currentStep = 1;
    const totalSteps = 5;
    let userData = {
      experience: null,
      goals: []
    };
    
    function updateUI() {
      // Update progress bar
      const progress = (currentStep / totalSteps) * 100;
      document.getElementById('progressFill').style.width = progress + '%';
      
      // Update step dots
      document.querySelectorAll('.step-dot').forEach((dot, i) => {
        dot.classList.remove('active', 'completed');
        if (i + 1 < currentStep) dot.classList.add('completed');
        if (i + 1 === currentStep) dot.classList.add('active');
      });
      
      // Update step content
      document.querySelectorAll('.step-content').forEach((content, i) => {
        content.classList.toggle('active', i + 1 === currentStep);
      });
    }
    
    function nextStep() {
      if (currentStep < totalSteps) {
        currentStep++;
        updateUI();
      }
    }
    
    function prevStep() {
      if (currentStep > 1) {
        currentStep--;
        updateUI();
      }
    }
    
    function selectExperience(el) {
      document.querySelectorAll('.experience-card').forEach(c => c.classList.remove('selected'));
      el.classList.add('selected');
      userData.experience = el.dataset.value;
      document.getElementById('step2Next').disabled = false;
    }
    
    function toggleGoal(el) {
      el.classList.toggle('selected');
      const value = el.dataset.value;
      const idx = userData.goals.indexOf(value);
      if (idx > -1) {
        userData.goals.splice(idx, 1);
      } else {
        userData.goals.push(value);
      }
      document.getElementById('step3Next').disabled = userData.goals.length === 0;
    }
    
    function checkForm() {
      const email = document.getElementById('emailInput').value;
      const password = document.getElementById('passwordInput').value;
      const terms = document.getElementById('termsCheck').checked;
      document.getElementById('step4Next').disabled = !(email && password.length >= 8 && terms);
    }
    
    document.getElementById('emailInput').addEventListener('input', checkForm);
    document.getElementById('passwordInput').addEventListener('input', checkForm);
    document.getElementById('termsCheck').addEventListener('change', checkForm);
    
    function completeOnboarding() {
      // Update summary
      const expMap = { newbie: '新手', basic: '有经验', pro: '专业投资者' };
      document.getElementById('summaryExp').textContent = expMap[userData.experience];
      document.getElementById('summaryGoals').textContent = userData.goals.length + '个目标';
      
      currentStep = 5;
      updateUI();
    }
    
    function startApp() {
      localStorage.setItem('go2se_onboarding_done', JSON.stringify(userData));
      window.location.href = 'index.html';
    }
    
    function skipOnboarding() {
      window.location.href = 'index.html';
    }
  </script>
</body>
</html>
