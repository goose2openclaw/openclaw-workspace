/**
 * 🪿 Market View Component
 */

import { useStore } from '../stores/appStore'

export function MarketView() {
  const { markets } = useStore()

  if (!markets.length) {
    return (
      <div className="empty-state">
        <p>暂无市场数据</p>
      </div>
    )
  }

  return (
    <div className="market-grid">
      {markets.map((market) => (
        <div key={market.symbol} className="market-card">
          <div className="card-header">
            <span className="symbol">{market.symbol.replace('/USDT', '')}</span>
            <span className={`change ${market.change_24h >= 0 ? 'up' : 'down'}`}>
              {market.change_24h >= 0 ? '▲' : '▼'} {market.change_24h?.toFixed(2)}%
            </span>
          </div>
          
          <div className="card-body">
            <div className="price">${market.price?.toLocaleString()}</div>
            <div className="volume">量: ${(market.volume_24h / 1000000).toFixed(2)}M</div>
          </div>
          
          <div className="card-footer">
            <div className="rsi">
              RSI: 
              <span className={
                market.rsi > 70 ? 'overbought' : 
                market.rsi < 30 ? 'oversold' : ''
              }>
                {market.rsi?.toFixed(1)}
              </span>
            </div>
            <div className="spread">
              价差: {((market.ask - market.bid) / market.price * 100).toFixed(3)}%
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
