/**
 * 🪿 Trades View Component
 */

import { useStore } from '../stores/appStore'

export function TradesView() {
  const { trades } = useStore()

  if (!trades.length) {
    return (
      <div className="empty-state">
        <p>暂无交易记录</p>
      </div>
    )
  }

  return (
    <div className="trades-list">
      <table className="trades-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>交易对</th>
            <th>方向</th>
            <th>数量</th>
            <th>价格</th>
            <th>状态</th>
            <th>盈亏</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={trade.id}>
              <td>{new Date(trade.created_at).toLocaleDateString()}</td>
              <td>{trade.symbol}</td>
              <td>
                <span className={`side ${trade.side}`}>
                  {trade.side === 'buy' ? '🟢 买入' : '🔴 卖出'}
                </span>
              </td>
              <td>{trade.amount}</td>
              <td>${trade.price?.toFixed(2)}</td>
              <td>
                <span className={`status ${trade.status}`}>
                  {trade.status}
                </span>
              </td>
              <td>
                <span className={`pnl ${trade.pnl >= 0 ? 'profit' : 'loss'}`}>
                  {trade.pnl >= 0 ? '+' : ''}{trade.pnl?.toFixed(2)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
