import { Signal } from './types';

interface SignalsProps {
  signals: Signal[];
}

export function Signals({ signals }: SignalsProps) {
  return (
    <div className="signals-section">
      <h2>📡 交易信号</h2>
      <div className="signals-list">
        {signals.length > 0 ? signals.slice(0, 10).map(signal => (
          <div key={signal.id} className={`card signal-card ${signal.type}`}>
            <span className="signal-type">
              {signal.type === 'buy' ? '🟢 买入' : '🔴 卖出'}
            </span>
            <span className="signal-symbol">{signal.symbol}</span>
            <span className="signal-strength">强度: {signal.strength}%</span>
          </div>
        )) : <div className="card">暂无信号</div>}
      </div>
    </div>
  );
}
