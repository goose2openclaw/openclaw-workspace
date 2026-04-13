import { Tool } from './types';

interface ToolsProps {
  tools: Tool[];
}

export function Tools({ tools }: ToolsProps) {
  return (
    <div className="tools-section">
      <h2>🎛️ 北斗七鑫投资工具</h2>
      <div className="tools-grid">
        {tools.map(tool => (
          <div key={tool.id} className={`card tool-card ${tool.status}`}>
            <div className="tool-header">
              <span className="tool-emoji">{tool.emoji}</span>
              <span className="tool-name">{tool.name}</span>
              <span className={`status-badge ${tool.status}`}>
                {tool.status === 'active' ? '运行中' : tool.status === 'paused' ? '暂停' : '关闭'}
              </span>
            </div>
            <div className="tool-config">
              <div className="config-row"><span>仓位:</span><span className="value">{tool.position}%</span></div>
              <div className="config-row"><span>止损:</span><span className="value danger">{tool.stopLoss}%</span></div>
              <div className="config-row"><span>止盈:</span><span className="value success">{tool.takeProfit}%</span></div>
            </div>
            <div className="tool-stats">
              <div className="stat">
                <span className="label">日盈亏</span>
                <span className={`value ${tool.dailyPnL >= 0 ? 'positive' : 'negative'}`}>
                  {tool.dailyPnL >= 0 ? '+' : ''}{tool.dailyPnL.toFixed(2)}
                </span>
              </div>
              <div className="stat">
                <span className="label">总盈亏</span>
                <span className={`value ${tool.totalPnL >= 0 ? 'positive' : 'negative'}`}>
                  {tool.totalPnL >= 0 ? '+' : ''}{tool.totalPnL.toFixed(2)}
                </span>
              </div>
              <div className="stat">
                <span className="label">交易数</span>
                <span className="value">{tool.trades}</span>
              </div>
            </div>
            <div className="tool-actions">
              <button className="btn-small">配置</button>
              <button className={`btn-small ${tool.status === 'active' ? 'warning' : 'success'}`}>
                {tool.status === 'active' ? '暂停' : '启动'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
