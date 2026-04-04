/**
 * GO2SE Asset Page Module
 * 资产看板页面
 */

class AssetPage {
  constructor() {
    this.charts = {};
    this.refreshInterval = 30000; // 30秒刷新
  }

  template() {
    return `
    <div class="asset-page">
      <div class="page-header">
        <h1>💰 资产看板</h1>
        <div class="header-actions">
          <button class="btn-refresh" onclick="AssetPage.loadAssets()">🔄 刷新</button>
        </div>
      </div>
      
      <div class="asset-summary">
        <div class="summary-card">
          <div class="summary-label">总资产</div>
          <div class="summary-value" id="asset-total">$0.00</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">可用现金</div>
          <div class="summary-value" id="asset-cash">$0.00</div>
        </div>
        <div class="summary-card">
          <div class="summary-label">已锁定</div>
          <div class="summary-value" id="asset-locked">$0.00</div>
        </div>
      </div>
      
      <div class="asset-grid">
        <div class="card chart-card">
          <h3>📊 资产分布</h3>
          <canvas id="portfolio-pie"></canvas>
        </div>
        <div class="card chart-card">
          <h3>📈 收益曲线</h3>
          <canvas id="profit-line"></canvas>
        </div>
      </div>
      
      <div class="card risk-card">
        <h3>🛡️ 风险仪表</h3>
        <div id="risk-gauge" class="risk-gauge"></div>
      </div>
    </div>
    `;
  }

  async init() {
    await this.loadAssets();
    this.initCharts();
    this.startAutoRefresh();
  }

  async loadAssets() {
    try {
      const data = await window.GO2SE.getAssets();
      this.updateAssetDisplay(data);
    } catch (error) {
      console.error('Failed to load assets:', error);
    }
  }

  updateAssetDisplay(data) {
    // 更新财产总额
    const totalEl = document.getElementById('asset-total');
    if (totalEl) {
      totalEl.textContent = `$${data.total?.toLocaleString() || 0}`;
    }

    // 更新24h变化
    const changeEl = document.getElementById('asset-change');
    if (changeEl && data.change24h !== undefined) {
      const sign = data.change24h >= 0 ? '+' : '';
      changeEl.textContent = `${sign}$${data.change24h?.toLocaleString()} (${sign}${data.changePercent?.toFixed(2)}%)`;
      changeEl.className = data.change24h >= 0 ? 'positive' : 'negative';
    }

    // 更新工具分配
    const byTool = data.byTool || {};
    Object.entries(byTool).forEach(([tool, amount]) => {
      const el = document.getElementById(`asset-${tool}`);
      if (el) {
        el.textContent = `$${amount?.toLocaleString()}`;
      }
    });
  }

  initCharts() {
    this.initPortfolioPieChart();
    this.initProfitLineChart();
    this.initRiskGauge();
  }

  initPortfolioPieChart() {
    const canvas = document.getElementById('portfolio-pie');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const data = window.GO2SEStore.get('assets.byTool') || {};
    
    // 饼图实现
    // ...
  }

  initProfitLineChart() {
    const canvas = document.getElementById('profit-line');
    if (!canvas) return;

    // 折线图实现
    // ...
  }

  initRiskGauge() {
    const gauge = document.getElementById('risk-gauge');
    if (!gauge) return;

    // 仪表盘实现
    // ...
  }

  startAutoRefresh() {
    setInterval(() => {
      this.loadAssets();
    }, this.refreshInterval);
  }
}

// 导出
window.AssetPage = AssetPage;
