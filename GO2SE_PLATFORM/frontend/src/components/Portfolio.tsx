import { Performance, InvestmentTool, WorkTool } from './types';

interface PortfolioProps {
  performance: Performance | null;
}

export function Portfolio({ performance }: PortfolioProps) {
  const investmentPool = performance?.investment_pool || 80000;
  const workPool = performance?.work_pool || 20000;

  return (
    <div className="portfolio-section">
      <h2>💼 投资组合 V10</h2>
      <div className="card portfolio-summary">
        <div className="summary-row">
          <span>总资金</span>
          <span className="large">${performance?.total_capital?.toLocaleString() || '100,000'}</span>
        </div>
        <div className="summary-row">
          <span>投资池 (80%)</span>
          <span className="positive">${investmentPool.toLocaleString()}</span>
        </div>
        <div className="summary-row">
          <span>打工池 (20%)</span>
          <span className="positive">${workPool.toLocaleString()}</span>
        </div>
      </div>
      <div className="card allocation">
        <h4>📊 投资工具分配 (5个)</h4>
        <div className="allocation-bars">
          {Object.entries(performance?.investment_tools || {}).map(([id, tool]: [string, InvestmentTool]) => (
            <div key={id} className="allocation-row">
              <span>{tool.name}</span>
              <div className="bar-container">
                <div
                  className="bar"
                  style={{
                    width: `${(tool.allocation / investmentPool) * 100}%`,
                    backgroundColor: tool.color,
                    opacity: tool.status === 'disabled' ? 0.3 : 1
                  }}
                />
              </div>
              <span className={tool.status === 'disabled' ? 'disabled' : ''}>
                ${(tool.allocation || 0).toLocaleString()} ({tool.weight}%)
              </span>
            </div>
          ))}
        </div>
      </div>
      <div className="card allocation work-tools">
        <h4>💰 打工工具 (2个) - 现金流收集</h4>
        <div className="allocation-bars">
          {Object.entries(performance?.work_tools || {}).map(([id, tool]: [string, WorkTool]) => (
            <div key={id} className="allocation-row">
              <span>{tool.name}</span>
              <div className="bar-container">
                <div
                  className="bar"
                  style={{
                    width: `${(tool.allocation / workPool) * 100}%`,
                    backgroundColor: tool.color
                  }}
                />
              </div>
              <span>${(tool.allocation || 0).toLocaleString()} (现金流{tool.cashflow_rate * 100}%)</span>
            </div>
          ))}
        </div>
        <div className="cashflow-status">
          <span>💵 现金流池: ${(performance?.cashflow_pool || 0).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}
