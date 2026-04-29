/**
 * GO2SE Genius 持续进化监控面板
 */

class EvolutionMonitor {
  constructor() {
    this.name = 'EvolutionMonitor';
    this.iteration = 0;
    this.history = [];
    this.API_BASE = 'http://localhost:8000';
    this.HERMES = 'http://localhost:8025';
    this.init();
  }

  init() {
    console.log('🔄 EvolutionMonitor启动...');
    this.render();
    this.startLoop();
  }

  startLoop() {
    // 每30秒更新一次
    setInterval(() => {
      this.checkStatus();
    }, 30000);
    
    // 每5分钟深度评测
    setInterval(() => {
      this.deepEvaluate();
    }, 300000);
    
    // 立即执行一次
    setTimeout(() => this.checkStatus(), 3000);
  }

  async checkStatus() {
    try {
      const [status, miro, hermes] = await Promise.all([
        fetch(`${this.API_BASE}/autonomous/status`).then(r => r.json()).catch(() => null),
        fetch(`${this.API_BASE}/autonomous/mirofish/status`).then(r => r.json()).catch(() => null),
        fetch(`${this.HERMES}/health`).then(r => r.json()).catch(() => null)
      ]);

      if (status) {
        this.updateStatusDisplay({ status, miro, hermes });
      }
    } catch (e) {
      console.warn('状态检查失败:', e.message);
    }
  }

  async deepEvaluate() {
    this.iteration++;
    console.log(`🔄 深度评测 #${this.iteration}...`);

    const result = {
      iteration: this.iteration,
      timestamp: Date.now(),
      scores: {},
      recommendations: []
    };

    try {
      // Mirofish评分
      const miro = await fetch(`${this.API_BASE}/autonomous/mirofish/status`).then(r => r.json()).catch(() => null);
      result.scores.mirofish = miro?.score || 0;

      // 交易统计
      const stats = await fetch(`${this.API_BASE}/api/stats`).then(r => r.json()).catch(() => null);
      result.scores.trades = stats?.data?.total_trades || 0;
      result.scores.signals = stats?.data?.total_signals || 0;

      // Hermes状态
      const hermes = await fetch(`${this.HERMES}/health`).then(r => r.json()).catch(() => null);
      result.scores.hermesLatency = hermes?.signals?.latency_ms || 0;

      // 分析建议
      if (result.scores.mirofish < 0.8) {
        result.recommendations.push({ type: 'optimize', priority: 'high', message: 'Mirofish评分偏低，建议调整策略权重' });
      }
      if (result.scores.signals === 0) {
        result.recommendations.push({ type: 'signal', priority: 'medium', message: '暂无信号生成，考虑激活策略' });
      }
      if (result.scores.hermesLatency > 200) {
        result.recommendations.push({ type: 'performance', priority: 'low', message: 'Hermes响应延迟偏高' });
      }

      this.history.push(result);
      if (this.history.length > 50) this.history.shift();

      this.updateEvolutionDisplay(result);
    } catch (e) {
      console.error('深度评测失败:', e);
    }
  }

  updateStatusDisplay({ status, miro, hermes }) {
    // 更新状态元素
    const statusEl = document.getElementById('systemStatus');
    if (statusEl) {
      statusEl.innerHTML = `
        <div class="status-item">
          <span class="status-label">系统</span>
          <span class="status-value status-${status?.status}">${status?.status || 'unknown'}</span>
        </div>
        <div class="status-item">
          <span class="status-label">Mirofish</span>
          <span class="status-value">${(miro?.score * 100).toFixed(1) || '?'}%</span>
        </div>
        <div class="status-item">
          <span class="status-label">Hermes</span>
          <span class="status-value">${hermes?.signals?.latency_ms || '?'}ms</span>
        </div>
      `;
    }
  }

  updateEvolutionDisplay(result) {
    const panel = document.getElementById('evolutionPanel');
    if (!panel) return;

    const latest = this.history.slice(-1)[0];
    if (!latest) return;

    panel.innerHTML = `
      <div class="evolution-container">
        <h3>🔄 进化状态</h3>
        <div class="evolution-metrics">
          <div class="metric">
            <span class="metric-label">循环次数</span>
            <span class="metric-value">${latest.iteration}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Mirofish</span>
            <span class="metric-value">${(latest.scores.mirofish * 100).toFixed(1)}%</span>
          </div>
          <div class="metric">
            <span class="metric-label">交易数</span>
            <span class="metric-value">${latest.scores.trades}</span>
          </div>
          <div class="metric">
            <span class="metric-label">信号数</span>
            <span class="metric-value">${latest.scores.signals}</span>
          </div>
        </div>
        ${latest.recommendations.length > 0 ? `
          <div class="evolution-recs">
            <h4>📋 优化建议</h4>
            ${latest.recommendations.map(r => `
              <div class="rec-item priority-${r.priority}">
                <span class="rec-icon">${r.priority === 'high' ? '🔴' : r.priority === 'medium' ? '🟡' : '🟢'}</span>
                <span class="rec-message">${r.message}</span>
              </div>
            `).join('')}
          </div>
        ` : '<div class="evolution-ok">✅ 所有指标正常</div>'}
      </div>
    `;
  }

  render() {
    let panel = document.getElementById('evolutionPanel');
    if (!panel) {
      panel = document.createElement('div');
      panel.id = 'evolutionPanel';
      
      const settingsSection = document.getElementById('settings');
      if (settingsSection) {
        settingsSection.insertBefore(panel, settingsSection.firstChild);
      }
    }
    
    // 添加样式
    if (!document.getElementById('evolutionStyles')) {
      const style = document.createElement('style');
      style.id = 'evolutionStyles';
      style.textContent = `
        #evolutionPanel {
          background: var(--card-bg);
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 20px;
          border: 1px solid var(--border-color);
        }
        .evolution-container h3 {
          margin: 0 0 16px 0;
          color: var(--primary);
        }
        .evolution-metrics {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 12px;
          margin-bottom: 16px;
        }
        .metric {
          background: var(--bg-secondary);
          padding: 12px;
          border-radius: 8px;
          text-align: center;
        }
        .metric-label {
          display: block;
          font-size: 11px;
          color: var(--text-dim);
          margin-bottom: 4px;
        }
        .metric-value {
          font-size: 18px;
          font-weight: 700;
          color: var(--primary);
        }
        .evolution-recs h4 {
          margin: 0 0 8px 0;
          font-size: 13px;
          color: var(--text-dim);
        }
        .rec-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px;
          background: var(--bg-secondary);
          border-radius: 6px;
          margin-bottom: 6px;
          font-size: 12px;
        }
        .evolution-ok {
          text-align: center;
          padding: 16px;
          color: var(--primary);
          font-size: 14px;
        }
      `;
      document.head.appendChild(style);
    }
  }
}

// 全局实例
const evolutionMonitor = new EvolutionMonitor();
window.EvolutionMonitor = EvolutionMonitor;
window.evolutionMonitor = evolutionMonitor;
