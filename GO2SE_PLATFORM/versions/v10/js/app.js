/**
 * GO2SE v9 - Main Application Logic
 * 处理启动动画、主题切换、导航、交互等
 */

(function() {
  'use strict';

  // ========== Splash Screen Animation ==========
  function initSplash() {
    const splash = document.getElementById('splash');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const app = document.getElementById('app');
    
    let progress = 0;
    const messages = [
      '红掌拨清波ing...',
      '初始化中...',
      '加载策略...',
      '连接市场...',
      '启动AI...',
      '准备就绪!'
    ];
    
    const interval = setInterval(() => {
      progress += Math.random() * 15 + 5;
      if (progress > 100) progress = 100;
      
      progressFill.style.width = progress + '%';
      progressText.textContent = messages[Math.floor(progress / 20)] + ' ' + Math.floor(progress) + '%';
      
      if (progress >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          splash.classList.add('fade-out');
          setTimeout(() => {
            splash.classList.add('hidden');
            app.classList.remove('hidden');
            app.style.opacity = '0';
            app.style.transition = 'opacity 0.5s ease';
            setTimeout(() => {
              app.style.opacity = '1';
            }, 50);
          }, 400);
        }, 300);
      }
    }, 150);
  }

  // ========== Theme Switcher ==========
  function initThemeSwitcher() {
    const themeBtns = document.querySelectorAll('.theme-btn');
    const html = document.documentElement;
    
    // 从localStorage恢复主题
    const savedTheme = localStorage.getItem('go2se-theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
    updateThemeButtons(savedTheme);
    
    themeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const theme = btn.dataset.theme;
        html.setAttribute('data-theme', theme);
        localStorage.setItem('go2se-theme', theme);
        updateThemeButtons(theme);
      });
    });
    
    function updateThemeButtons(activeTheme) {
      themeBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === activeTheme);
      });
    }
  }

  // ========== Language Switcher ==========
  function initLanguageSwitcher() {
    const langBtns = document.querySelectorAll('.lang-btn');
    
    langBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const lang = btn.dataset.lang;
        langBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        localStorage.setItem('go2se-lang', lang);
        // 实际项目应该切换语言文件
        console.log('Language switched to:', lang);
      });
    });
  }

  // ========== Breathing Light ==========
  function initBreathingLight() {
    const light = document.getElementById('breathingLight');
    const dot = light.querySelector('.light-dot');
    const ring = light.querySelector('.light-ring');
    
    // 模拟不同状态
    const states = [
      { color: '#10B981', speed: 2000, label: '系统正常' },
      { color: '#F59E0B', speed: 1000, label: '信息通知' },
      { color: '#EF4444', speed: 300, label: '紧急预警' }
    ];
    
    let stateIndex = 0;
    
    light.addEventListener('click', () => {
      stateIndex = (stateIndex + 1) % states.length;
      const state = states[stateIndex];
      dot.style.background = state.color;
      ring.style.borderColor = state.color;
      ring.style.animationDuration = state.speed + 'ms';
      light.title = state.label;
      
      // 显示通知面板
      showNotificationPanel();
    });
    
    // 自动切换状态（模拟）
    setInterval(() => {
      stateIndex = (stateIndex + 1) % states.length;
      const state = states[stateIndex];
      dot.style.background = state.color;
      ring.style.borderColor = state.color;
      ring.style.animationDuration = state.speed + 'ms';
      light.title = state.label;
    }, 10000);
  }

  // ========== Member Dropdown ==========
  function initMemberDropdown() {
    const memberBtn = document.getElementById('memberBtn');
    const dropdown = document.getElementById('memberDropdown');
    
    memberBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('show');
    });
    
    document.addEventListener('click', () => {
      dropdown.classList.remove('show');
    });
    
    dropdown.querySelectorAll('.dropdown-item').forEach(item => {
      item.addEventListener('click', () => {
        const type = item.dataset.type;
        if (type === 'login' || item.classList.contains('login-item')) {
          showLoginModal();
        } else {
          console.log('Selected member type:', type);
          dropdown.classList.remove('show');
        }
      });
    });
  }

  // ========== Notification Panel ==========
  function initNotificationPanel() {
    const notifBtn = document.getElementById('notificationBtn');
    const notifPanel = document.getElementById('notificationPanel');
    const panelClose = document.getElementById('panelClose');
    
    notifBtn.addEventListener('click', () => {
      notifPanel.classList.toggle('hidden');
    });
    
    panelClose.addEventListener('click', () => {
      notifPanel.classList.add('hidden');
    });
    
    // 点击外部关闭
    document.addEventListener('click', (e) => {
      if (!notifPanel.contains(e.target) && !notifBtn.contains(e.target)) {
        notifPanel.classList.add('hidden');
      }
    });
  }

  function showNotificationPanel() {
    const notifPanel = document.getElementById('notificationPanel');
    notifPanel.classList.remove('hidden');
  }

  // ========== Sidebar Navigation ==========
  function initSidebar() {
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    const contentArea = document.getElementById('contentArea');
    
    sidebarItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const sectionId = item.dataset.section;
        const section = document.getElementById(sectionId);
        
        if (section) {
          // 更新激活状态
          sidebarItems.forEach(i => i.classList.remove('active'));
          item.classList.add('active');
          
          // 滚动到对应section
          const offset = 80;
          const elementPosition = section.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.pageYOffset - offset;
          
          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });
        }
      });
    });
    
    // 滚动时更新sidebar高亮
    const sections = document.querySelectorAll('.content-section');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          sidebarItems.forEach(item => {
            item.classList.toggle('active', item.dataset.section === id);
          });
        }
      });
    }, { threshold: 0.3 });
    
    sections.forEach(section => observer.observe(section));
  }

  // ========== Pin Button ==========
  function initPinButton() {
    const pinBtn = document.getElementById('pinBtn');
    let pinnedSection = null;
    
    pinBtn.addEventListener('click', () => {
      const activeItem = document.querySelector('.sidebar-item.active');
      if (activeItem) {
        const sectionId = activeItem.dataset.section;
        
        if (pinnedSection === sectionId) {
          // 取消置顶
          pinnedSection = null;
          pinBtn.textContent = '📌 置顶';
          pinBtn.style.background = '';
          pinBtn.style.color = '';
        } else {
          // 置顶
          pinnedSection = sectionId;
          pinBtn.textContent = '📌 已置顶';
          pinBtn.style.background = 'var(--accent-warning)';
          pinBtn.style.color = 'var(--bg-primary)';
        }
      }
    });
  }

  // ========== Investment Mode Toggle ==========
  function initInvestmentMode() {
    const modeBtns = document.querySelectorAll('.mode-btn');
    const styleBtns = document.querySelectorAll('.style-btn');
    
    modeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        modeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        console.log('Investment mode:', btn.dataset.mode);
      });
    });
    
    styleBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const parent = btn.closest('.style-selector') || btn.closest('.strategy-style');
        if (parent) {
          parent.querySelectorAll('.style-btn').forEach(b => b.classList.remove('active'));
        }
        btn.classList.add('active');
        console.log('Investment style:', btn.dataset.style);
      });
    });
  }

  // ========== Sliders ==========
  function initSliders() {
    const sliders = document.querySelectorAll('input[type="range"]');
    
    sliders.forEach(slider => {
      const updateSliderStyle = () => {
        const value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
        slider.style.background = `linear-gradient(to right, var(--accent-primary) ${value}%, var(--bg-secondary) ${value}%)`;
      };
      
      slider.addEventListener('input', updateSliderStyle);
      updateSliderStyle();
    });
  }

  // ========== Allocation Tabs ==========
  function initAllocationTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const content = document.getElementById('allocationContent');
    
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const tab = btn.dataset.tab;
        console.log('Switched to allocation tab:', tab);
        // 实际应该切换内容
      });
    });
  }

  // ========== Simulator Tabs ==========
  function initSimulatorTabs() {
    const simTabs = document.querySelectorAll('.sim-tab');
    
    simTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        simTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const simType = tab.dataset.sim;
        console.log('Switched to simulator:', simType);
        // 实际应该切换内容
      });
    });
  }

  // ========== Strategy Style Selector ==========
  function initStrategyStyle() {
    const styleBtns = document.querySelectorAll('.strategy-style .style-btn');
    
    styleBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        styleBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const style = btn.dataset.style;
        console.log('Strategy style changed:', style);
        // 触发策略重新计算
      });
    });
  }

  // ========== AI Apply Buttons ==========
  function initAIApply() {
    const applyBtns = document.querySelectorAll('.ai-apply');
    
    applyBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const sliderItem = btn.closest('.ai-slider-item');
        const label = sliderItem.querySelector('label').textContent;
        const value = sliderItem.querySelector('input[type="range"]').value;
        console.log('Applying AI recommendation:', label, value + '%');
        
        // 显示应用成功提示
        btn.textContent = '✓ 已应用';
        btn.style.background = 'var(--accent-success)';
        setTimeout(() => {
          btn.textContent = '应用';
          btn.style.background = '';
        }, 1500);
      });
    });
  }

  // ========== Login Modal (Placeholder) ==========
  function showLoginModal() {
    // 创建一个简单的登录提示
    const modal = document.createElement('div');
    modal.className = 'login-modal';
    modal.innerHTML = `
      <div class="modal-overlay"></div>
      <div class="modal-content">
        <h3>登录 GO2SE</h3>
        <p>正在跳转登录页面...</p>
        <button class="modal-close">×</button>
      </div>
    `;
    modal.style.cssText = `
      position: fixed;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    `;
    document.body.appendChild(modal);
    
    modal.querySelector('.modal-close').addEventListener('click', () => {
      modal.remove();
    });
    
    modal.querySelector('.modal-overlay').addEventListener('click', () => {
      modal.remove();
    });
    
    setTimeout(() => modal.remove(), 2000);
  }

  // ========== Attention Grid ==========
  function initAttentionGrid() {
    const grid = document.getElementById('attentionGrid');
    const addPinBtn = document.getElementById('addPinBtn');
    const clearPinsBtn = document.getElementById('clearPinsBtn');
    
    // 添加新卡片
    addPinBtn.addEventListener('click', () => {
      const newCard = document.createElement('div');
      newCard.className = 'attention-card pinned';
      newCard.innerHTML = `
        <div class="card-tag">📌 新置顶</div>
        <h4>自定义热点</h4>
        <p class="card-meta">${new Date().toLocaleString()}</p>
      `;
      grid.insertBefore(newCard, grid.firstChild);
    });
    
    // 清除已置顶
    clearPinsBtn.addEventListener('click', () => {
      grid.querySelectorAll('.attention-card.pinned').forEach(card => card.remove());
    });
    
    // 点击卡片
    grid.addEventListener('click', (e) => {
      const card = e.target.closest('.attention-card');
      if (card) {
        card.querySelector('.card-tag').textContent = '📌 已点击';
        console.log('Clicked attention card');
      }
    });
  }

  // ========== Rollback Buttons ==========
  function initRollback() {
    const rollbackBtns = document.querySelectorAll('.rollback-btn');
    
    rollbackBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const date = btn.textContent.replace('回滚到 ', '');
        if (confirm(`确定要回滚到 ${date} 吗？`)) {
          console.log('Rolling back to:', date);
          btn.textContent = '回滚中...';
          setTimeout(() => {
            btn.textContent = '✓ 已回滚';
            btn.style.background = 'var(--accent-success)';
            btn.style.color = 'white';
          }, 1000);
        }
      });
    });
  }

  // ========== Debug Panel ==========
  function initDebugPanel() {
    const debugRun = document.querySelector('.debug-run');
    const debugInput = document.querySelector('.debug-input');
    
    if (debugRun && debugInput) {
      debugRun.addEventListener('click', () => {
        const problem = debugInput.value || '系统自动诊断';
        console.log('Running MiroFish diagnosis for:', problem);
        
        debugRun.textContent = '诊断中...';
        debugRun.disabled = true;
        
        setTimeout(() => {
          debugRun.textContent = 'MiroFish仿真诊断';
          debugRun.disabled = false;
          
          const result = document.querySelector('.debug-result');
          if (result) {
            result.querySelector('.debug-status').textContent = '✓ 诊断完成';
            result.querySelector('.debug-finding').textContent = 
              `分析完成，发现3个潜在问题，已自动修复2个，建议人工审查1个`;
          }
        }, 2000);
      });
    }
  }

  // ========== Terminal Preview ==========
  function initTerminal() {
    const termBtn = document.querySelector('.term-btn');
    
    if (termBtn) {
      termBtn.addEventListener('click', () => {
        // 实际应该打开完整终端
        alert('终端功能开发中...\n预计v9.1版本上线');
      });
    }
  }

  // ========== Copy Referral Link ==========
  function initReferralLink() {
    const copyBtn = document.querySelector('.copy-btn');
    const linkInput = document.querySelector('.referral-link input');
    
    if (copyBtn && linkInput) {
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(linkInput.value).then(() => {
          copyBtn.textContent = '✓ 已复制';
          setTimeout(() => {
            copyBtn.textContent = '复制';
          }, 1500);
        });
      });
    }
  }

  // ========== Create Quant盘 ==========
  function initQuant盘() {
    const createBtn = document.querySelector('.盘-create');
    const nameInput = document.querySelector('.盘-name');
    
    if (createBtn && nameInput) {
      createBtn.addEventListener('click', () => {
        const name = nameInput.value.trim();
        if (!name) {
          nameInput.style.borderColor = 'var(--accent-danger)';
          setTimeout(() => {
            nameInput.style.borderColor = '';
          }, 1000);
          return;
        }
        
        createBtn.textContent = '创建中...';
        setTimeout(() => {
          createBtn.textContent = '✓ 创建成功';
          createBtn.style.background = 'var(--accent-success)';
          nameInput.value = '';
          setTimeout(() => {
            createBtn.textContent = '创建量化盘';
            createBtn.style.background = '';
          }, 2000);
        }, 1500);
      });
    }
  }

  // ========== Partner Add ==========
  function initPartnerAdd() {
    const partnerBtns = document.querySelectorAll('.partner-btn');
    
    partnerBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const partnerItem = btn.closest('.partner-item');
        const partnerName = partnerItem.querySelector('.partner-name').textContent;
        
        btn.textContent = '加入中...';
        btn.disabled = true;
        
        setTimeout(() => {
          btn.textContent = '已加入';
          btn.style.background = 'var(--accent-success)';
          partnerItem.querySelector('.partner-name').textContent = partnerName + ' ✓';
        }, 1500);
      });
    });
  }

  // ========== Clone Strategy ==========
  function initCloneStrategy() {
    const cloneBtns = document.querySelectorAll('.clone-btn');
    
    cloneBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const cloneItem = btn.closest('.clone-item');
        const stratName = cloneItem.querySelector('.clone-strat').textContent;
        
        btn.textContent = '克隆中...';
        
        setTimeout(() => {
          btn.textContent = '已克隆';
          btn.style.background = 'var(--accent-success)';
          setTimeout(() => {
            btn.textContent = '克隆';
            btn.style.background = '';
          }, 2000);
        }, 1500);
      });
    });
  }

  // ========== Customize Expert Mode ==========
  function initCustomizeExpert() {
    const customizeBtn = document.querySelector('.customize-btn');
    
    if (customizeBtn) {
      customizeBtn.addEventListener('click', () => {
        customizeBtn.textContent = '生成中...';
        customizeBtn.disabled = true;
        
        setTimeout(() => {
          customizeBtn.textContent = '✓ 专家模式已生成';
          customizeBtn.style.background = 'var(--accent-success)';
          
          setTimeout(() => {
            customizeBtn.textContent = '生成自定义专家模式 →';
            customizeBtn.style.background = '';
            customizeBtn.disabled = false;
          }, 2000);
        }, 2500);
      });
    }
  }

  // ========== Save Expert Params ==========
  function initSaveParams() {
    const saveBtn = document.querySelector('.param-save');
    
    if (saveBtn) {
      saveBtn.addEventListener('click', () => {
        const params = [];
        document.querySelectorAll('.param-row').forEach(row => {
          const label = row.querySelector('label').textContent;
          const value = row.querySelector('input[type="range"]').value;
          params.push({ [label]: value });
        });
        
        console.log('Saving expert params:', params);
        
        saveBtn.textContent = '保存中...';
        setTimeout(() => {
          saveBtn.textContent = '✓ 已保存';
          saveBtn.style.background = 'var(--accent-success)';
          setTimeout(() => {
            saveBtn.textContent = '保存参数';
            saveBtn.style.background = '';
          }, 1500);
        }, 1000);
      });
    }
  }

  // ========== IM Badge Update ==========
  function updateIMBadge() {
    const badge = document.getElementById('imBadge');
    if (badge) {
      // 模拟新消息
      setInterval(() => {
        const current = parseInt(badge.textContent) || 0;
        if (current > 0 && Math.random() > 0.8) {
          badge.textContent = current - 1;
          if (parseInt(badge.textContent) === 0) {
            badge.style.display = 'none';
          }
        }
      }, 30000);
    }
  }

  // ========== Self Check ==========
  function initSelfCheck() {
    const checkBtn = document.querySelector('.check-btn');
    
    if (checkBtn) {
      checkBtn.addEventListener('click', () => {
        checkBtn.textContent = '自检中...';
        checkBtn.disabled = true;
        
        setTimeout(() => {
          document.querySelectorAll('.check-item').forEach((item, i) => {
            setTimeout(() => {
              item.querySelector('.check-icon').textContent = '✓';
              item.querySelector('.check-icon').style.color = 'var(--accent-success)';
            }, i * 300);
          });
          
          setTimeout(() => {
            checkBtn.textContent = '自检完成';
            checkBtn.style.background = 'var(--accent-success)';
            setTimeout(() => {
              checkBtn.textContent = '立即自检';
              checkBtn.style.background = '';
              checkBtn.disabled = false;
            }, 1500);
          }, 1500);
        }, 1500);
      });
    }
  }

  // ========== Portfolio Chart (Simple Canvas) ==========
  function initPortfolioChart() {
    const canvas = document.getElementById('portfolioCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = 200;
    canvas.height = 100;
    
    // 简单饼图
    const data = [
      { label: '打兔子', value: 25, color: '#00D4AA' },
      { label: '打地鼠', value: 20, color: '#7C3AED' },
      { label: '走着瞧', value: 15, color: '#F59E0B' },
      { label: '跟大哥', value: 15, color: '#EC4899' },
      { label: '搭便车', value: 10, color: '#06B6D4' },
      { label: '其他', value: 15, color: '#84CC16' }
    ];
    
    let startAngle = 0;
    data.forEach(item => {
      const sliceAngle = (item.value / 100) * 2 * Math.PI;
      ctx.fillStyle = item.color;
      ctx.beginPath();
      ctx.moveTo(100, 50);
      ctx.arc(100, 50, 45, startAngle, startAngle + sliceAngle);
      ctx.closePath();
      ctx.fill();
      startAngle += sliceAngle;
    });
  }

  // ========== Keyboard Shortcuts ==========
  function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // ESC关闭面板
      if (e.key === 'Escape') {
        document.getElementById('notificationPanel').classList.add('hidden');
        document.getElementById('memberDropdown').classList.remove('show');
      }
      
      // Ctrl+R 刷新 (阻止默认)
      if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        location.reload();
      }
    });
  }

  // ========== Initialize All ==========
  function init() {
    initSplash();
    initThemeSwitcher();
    initLanguageSwitcher();
    initBreathingLight();
    initMemberDropdown();
    initNotificationPanel();
    initSidebar();
    initPinButton();
    initInvestmentMode();
    initSliders();
    initAllocationTabs();
    initSimulatorTabs();
    initStrategyStyle();
    initAIApply();
    initAttentionGrid();
    initRollback();
    initDebugPanel();
    initTerminal();
    initReferralLink();
    initQuant盘();
    initPartnerAdd();
    initCloneStrategy();
    initCustomizeExpert();
    initSaveParams();
    updateIMBadge();
    initSelfCheck();
    initPortfolioChart();
    initKeyboardShortcuts();
    
    console.log('🪿 GO2SE v9 initialized successfully');
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
initSidebarSubmenu();
  }

})();

// ========== Expert Mode Toggle ==========
function initExpertMode() {
  const modeBtns = document.querySelectorAll('.mode-btn');
  const ninjaItems = document.querySelectorAll('.ninja-only');
  
  modeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const mode = btn.dataset.mode;
      modeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      if (mode === 'expert') {
        // Show engineering mode
        ninjaItems.forEach(item => {
          item.style.display = '';
          item.querySelectorAll('.sidebar-item').forEach(si => {
            si.style.display = '';
          });
        });
        console.log('🥷 工程模式已激活');
      } else {
        // Hide engineering mode
        ninjaItems.forEach(item => {
          item.style.display = 'none';
          item.querySelectorAll('.sidebar-item').forEach(si => {
            si.style.display = 'none';
          });
        });
        console.log('普通模式: 工程模式已隐藏');
      }
    });
  });
  
  // Check initial state
  const activeMode = document.querySelector('.mode-btn.active');
  if (activeMode && activeMode.dataset.mode === 'expert') {
    ninjaItems.forEach(item => {
      item.style.display = '';
      item.querySelectorAll('.sidebar-item').forEach(si => {
        si.style.display = '';
      });
    });
  }
}

// Add to init
document.addEventListener('DOMContentLoaded', initExpertMode);
// Sidebar 子菜单功能
function initSidebarSubmenu() {
  const sidebarItems = document.querySelectorAll('.sidebar-item[data-section]');
  const contentArea = document.getElementById('contentArea');
  
  sidebarItems.forEach(item => {
    item.addEventListener('click', (e) => {
      const sectionId = item.dataset.section;
      
      // 如果有子菜单，则切换展开状态
      if (item.dataset.hasChildren) {
        e.preventDefault();
        const submenu = document.getElementById(`submenu-${sectionId}`);
        if (submenu) {
          submenu.classList.toggle('expanded');
          item.classList.toggle('expanded');
        }
        // 仍然滚动到主section
        scrollToSection(sectionId);
      } else {
        scrollToSection(sectionId);
      }
      
      // 更新激活状态
      sidebarItems.forEach(i => i.classList.remove('active'));
      item.classList.add('active');
    });
  });
  
  // 滚动时更新高亮
  const sections = document.querySelectorAll('.content-section[id]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        sidebarItems.forEach(item => {
          item.classList.toggle('active', item.dataset.section === id);
        });
      }
    });
  }, { threshold: 0.3 });
  
  sections.forEach(section => observer.observe(section));
}

function scrollToSection(sectionId) {
  const section = document.getElementById(sectionId);
  if (section) {
    const offset = 80;
    const elementPosition = section.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;
    
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  }
}

// 导出供主JS调用
window.initSidebarSubmenu = initSidebarSubmenu;
