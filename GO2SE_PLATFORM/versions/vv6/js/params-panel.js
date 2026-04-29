/**
 * VV6 Parameters Panel - 可调参数展示面板
 * 所有推荐可调的数据都展示在UI里
 */

class ParamsPanelVV6 {
  constructor() {
    this.name = 'ParamsPanel';
    this.version = '1.0';
    this.params = this.getDefaultParams();
    this.listeners = [];
    
    this.init();
  }

  init() {
    console.log('⚙️ ParamsPanel启动...');
    this.render();
    this.loadFromStorage();
  }

  // 默认参数
  getDefaultParams() {
    return {
      // 信号参数
      signal: {
        confidence: { value: 80, min: 50, max: 100, step: 5, label: '信号置信度', unit: '%' },
        positionPct: { value: 10, min: 1, max: 50, step: 1, label: '仓位比例', unit: '%' },
        stopLossPct: { value: 3.0, min: 0.5, max: 10, step: 0.5, label: '止损比例', unit: '%' },
        takeProfitPct: { value: 6.0, min: 1, max: 30, step: 0.5, label: '止盈比例', unit: '%' }
      },
      // 市场参数
      market: {
        fearGreedWeight: { value: 30, min: 0, max: 100, step: 10, label: '恐慌指数权重', unit: '%' },
        trendWeight: { value: 40, min: 0, max: 100, step: 10, label: '趋势权重', unit: '%' },
        volumeWeight: { value: 30, min: 0, max: 100, step: 10, label: '成交量权重', unit: '%' }
      },
      // 风险参数
      risk: {
        maxDrawdown: { value: 15, min: 5, max: 50, step: 5, label: '最大回撤', unit: '%' },
        maxPosition: { value: 30, min: 10, max: 80, step: 5, label: '最大持仓', unit: '%' },
        riskPerTrade: { value: 2, min: 0.5, max: 5, step: 0.5, label: '单笔风险', unit: '%' }
      },
      // 策略参数
      strategy: {
        shortMA: { value: 20, min: 5, max: 50, step: 5, label: '短期均线', unit: '日' },
        longMA: { value: 50, min: 20, max: 200, step: 10, label: '长期均线', unit: '日' },
        rsiThreshold: { value: 30, min: 20, max: 50, step: 5, label: 'RSI超卖', unit: '' },
        rsiOverbought: { value: 70, min: 50, max: 80, step: 5, label: 'RSI超买', unit: '' }
      },
      // 自动化参数
      auto: {
        autoMode: { value: true, type: 'boolean', label: '自动处理模式' },
        autoRefreshInterval: { value: 30, min: 10, max: 300, step: 10, label: '刷新间隔', unit: '秒' },
        alertThreshold: { value: 5, min: 1, max: 20, step: 1, label: '警报阈值', unit: '' }
      }
    };
  }

  // 渲染面板
  render() {
    // 检查是否已存在
    let panel = document.getElementById('paramsPanel');
    if (panel) panel.remove();

    // 创建面板
    panel = document.createElement('div');
    panel.id = 'paramsPanel';
    panel.innerHTML = this.generateHTML();
    
    // 添加到settings区域
    const settingsSection = document.getElementById('settings');
    if (settingsSection) {
      settingsSection.insertBefore(panel, settingsSection.firstChild);
    }
    
    // 绑定事件
    this.bindEvents();
  }

  // 生成HTML
  generateHTML() {
    let html = `
      <div class="params-container" style="
        background: var(--card-bg);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
      ">
        <h3 style="margin: 0 0 16px 0;color: var(--primary);">⚙️ 可调参数面板</h3>
    `;

    for (const [category, params] of Object.entries(this.params)) {
      html += `
        <div class="param-category" style="
          margin-bottom: 20px;
          padding: 12px;
          background: var(--bg-secondary);
          border-radius: 8px;
        ">
          <h4 style="
            margin: 0 0 12px 0;
            font-size: 13px;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 1px;
          ">${this.getCategoryName(category)}</h4>
          <div class="param-grid" style="
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
          ">
      `;

      for (const [key, param] of Object.entries(params)) {
        if (param.type === 'boolean') {
          html += this.renderBoolean(key, param, category);
        } else {
          html += this.renderSlider(key, param, category);
        }
      }

      html += '</div></div>';
    }

    html += `
      <div style="display:flex;gap:12px;margin-top:16px;">
        <button onclick="paramsPanelVV6.saveToStorage()" style="
          padding: 8px 16px;
          background: var(--primary);
          color: #000;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
        ">💾 保存设置</button>
        <button onclick="paramsPanelVV6.resetToDefault()" style="
          padding: 8px 16px;
          background: transparent;
          color: var(--text-dim);
          border: 1px solid var(--border-color);
          border-radius: 6px;
          cursor: pointer;
        ">🔄 重置默认</button>
      </div>
    </div>`;

    return html;
  }

  // 渲染布尔类型
  renderBoolean(key, param, category) {
    const checked = this.params[category][key].value ? 'checked' : '';
    return `
      <label style="
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px;
        background: var(--bg-primary);
        border-radius: 6px;
        cursor: pointer;
      ">
        <input type="checkbox" id="param_${category}_${key}" ${checked} 
          onchange="paramsPanelVV6.updateParam('${category}', '${key}', this.checked)"
          style="width:18px;height:18px;cursor:pointer;">
        <span style="font-size:13px;">${param.label}</span>
      </label>
    `;
  }

  // 渲染滑块
  renderSlider(key, param, category) {
    const p = this.params[category][key];
    return `
      <div style="padding:8px;background:var(--bg-primary);border-radius:6px;">
        <div style="
          display: flex;
          justify-content: space-between;
          margin-bottom: 6px;
          font-size: 12px;
        ">
          <span>${param.label}</span>
          <span id="val_${category}_${key}" style="
            color: var(--primary);
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
          ">${param.value}${param.unit || ''}</span>
        </div>
        <input type="range" 
          id="param_${category}_${key}"
          min="${param.min}" 
          max="${param.max}" 
          step="${param.step}"
          value="${param.value}"
          oninput="paramsPanelVV6.updateParam('${category}', '${key}', parseFloat(this.value))"
          onchange="paramsPanelVV6.onParamChange('${category}', '${key}', parseFloat(this.value))"
          style="
            width: 100%;
            height: 6px;
            -webkit-appearance: none;
            background: var(--bg-secondary);
            border-radius: 3px;
            outline: none;
          "
        >
      </div>
    `;
  }

  // 获取分类名称
  getCategoryName(category) {
    const names = {
      signal: '📡 信号参数',
      market: '📊 市场参数',
      risk: '🛡️ 风险参数',
      strategy: '📈 策略参数',
      auto: '🤖 自动化参数'
    };
    return names[category] || category;
  }

  // 绑定事件
  bindEvents() {
    // 添加自定义滑块样式
    const style = document.createElement('style');
    style.textContent = `
      input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 16px;
        height: 16px;
        background: var(--primary);
        border-radius: 50%;
        cursor: pointer;
      }
      input[type="range"]::-webkit-slider-runnable-track {
        height: 6px;
        border-radius: 3px;
      }
    `;
    document.head.appendChild(style);
  }

  // 更新参数
  updateParam(category, key, value) {
    this.params[category][key].value = value;
    
    // 更新显示值
    const valEl = document.getElementById(`val_${category}_${key}`);
    if (valEl) {
      const param = this.params[category][key];
      valEl.textContent = value + (param.unit || '');
    }
  }

  // 参数变化回调
  onParamChange(category, key, value) {
    console.log(`⚙️ 参数变化: ${category}.${key} = ${value}`);
    
    // 应用参数到系统
    this.applyParam(category, key, value);
    
    // 通知监听器
    this.listeners.forEach(cb => cb({category, key, value}));
  }

  // 应用参数
  applyParam(category, key, value) {
    switch(`${category}.${key}`) {
      case 'auto.autoMode':
        if (window.autoHandlerVV6) {
          autoHandlerVV6.autoMode = value;
        }
        break;
      case 'auto.autoRefreshInterval':
        if (window.VV6Bridge) {
          VV6Bridge.stopAutoRefresh();
          VV6Bridge.startAutoRefresh(value * 1000);
        }
        break;
      case 'signal.confidence':
        // 更新API调用时的参数
        break;
    }
  }

  // 添加监听器
  addListener(cb) {
    this.listeners.push(cb);
  }

  // 保存到localStorage
  saveToStorage() {
    const data = {};
    for (const [cat, params] of Object.entries(this.params)) {
      data[cat] = {};
      for (const [key, param] of Object.entries(params)) {
        data[cat][key] = param.value;
      }
    }
    localStorage.setItem('vv6_params', JSON.stringify(data));
    this.showToast('✅ 设置已保存');
  }

  // 从localStorage加载
  loadFromStorage() {
    try {
      const saved = localStorage.getItem('vv6_params');
      if (saved) {
        const data = JSON.parse(saved);
        for (const [cat, params] of Object.entries(data)) {
          if (this.params[cat]) {
            for (const [key, value] of Object.entries(params)) {
              if (this.params[cat][key]) {
                this.params[cat][key].value = value;
              }
            }
          }
        }
      }
    } catch (e) {
      console.warn('加载参数失败:', e);
    }
  }

  // 重置为默认
  resetToDefault() {
    localStorage.removeItem('vv6_params');
    this.params = this.getDefaultParams();
    this.render();
    this.showToast('🔄 已重置为默认');
  }

  // 显示提示
  showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: var(--primary);
      color: #000;
      padding: 10px 20px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      z-index: 10000;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
  }

  // 获取所有参数
  getAllParams() {
    return this.params;
  }
}

// 全局实例
const paramsPanelVV6 = new ParamsPanelVV6();
window.ParamsPanelVV6 = ParamsPanelVV6;
window.paramsPanelVV6 = paramsPanelVV6;
