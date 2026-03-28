/**
 * 策略测试脚本
 * 测试7大策略的信号生成
 */

import { StrategyManager, type MarketData, BaseStrategy } from './openclaw-control-center/src/strategies';

// 模拟市场数据
const mockMarkets: MarketData[] = [
  { pair: 'BTC/USDT', price: 75145, change24h: 0.0362, volume24h: 28500000000, volatility: 0.042, trend: 'bullish' },
  { pair: 'ETH/USDT', price: 3280, change24h: 0.0512, volume24h: 15200000000, volatility: 0.058, trend: 'bullish' },
  { pair: 'XRP/USDT', price: 2.85, change24h: 0.0823, volume24h: 8500000000, volatility: 0.095, trend: 'bullish' },
  { pair: 'SOL/USDT', price: 142, change24h: -0.0234, volume24h: 3200000000, volatility: 0.065, trend: 'sideways' },
  { pair: 'BNB/USDT', price: 585, change24h: 0.0156, volume24h: 1800000000, volatility: 0.038, trend: 'bullish' },
  { pair: 'ADA/USDT', price: 0.92, change24h: 0.1245, volume24h: 1200000000, volatility: 0.112, trend: 'bullish' },
  { pair: 'DOGE/USDT', price: 0.32, change24h: -0.0876, volume24h: 2500000000, volatility: 0.125, trend: 'bearish' },
  { pair: 'AVAX/USDT', price: 42, change24h: 0.0678, volume24h: 890000000, volatility: 0.078, trend: 'bullish' },
  { pair: 'DOT/USDT', price: 18.5, change24h: 0.0432, volume24h: 450000000, volatility: 0.055, trend: 'bullish' },
  { pair: 'LINK/USDT', price: 24.8, change24h: -0.0156, volume24h: 380000000, volatility: 0.048, trend: 'sideways' },
  { pair: 'MATIC/USDT', price: 1.12, change24h: 0.0934, volume24h: 520000000, volatility: 0.102, trend: 'bullish' },
  { pair: 'UNI/USDT', price: 12.5, change24h: 0.0289, volume24h: 210000000, volatility: 0.052, trend: 'bullish' },
  { pair: 'ATOM/USDT', price: 14.2, change24h: -0.0345, volume24h: 320000000, volatility: 0.068, trend: 'bearish' },
  { pair: 'LTC/USDT', price: 125, change24h: 0.0567, volume24h: 580000000, volatility: 0.072, trend: 'bullish' },
  { pair: 'FIL/USDT', price: 8.5, change24h: 0.1123, volume24h: 420000000, volatility: 0.115, trend: 'bullish' },
];

async function testStrategies() {
  console.log('🪿 GO2SE 策略测试\n');
  console.log('='.repeat(60));
  
  const manager = new StrategyManager();
  
  // 显示策略摘要
  console.log('\n📋 策略配置:');
  console.log('-'.repeat(40));
  const allStrats = manager.getAllStrategies();
  for (const item of allStrats) {
    const s = item.strategy;
    console.log(`  ${s.getAlias()} (${item.name})`);
    console.log(`    算力: ${s.getConfig().allocationPercent}% | 风险: ${s.getConfig().riskLevel}`);
    console.log(`    置信度: ≥${s.getConfig().minConfidence} | 最大仓位: ${s.getConfig().maxPositionPercent}%`);
    console.log();
  }
  
  // 扫描所有策略
  console.log('\n🔍 市场扫描中...');
  console.log(`  测试数据: ${mockMarkets.length} 个交易对\n`);
  
  const allSignals = await manager.scanAll(mockMarkets);
  
  console.log('📡 信号汇总 (按置信度排序):');
  console.log('-'.repeat(60));
  
  if (allSignals.length === 0) {
    console.log('  暂无信号');
  } else {
    for (const signal of allSignals.slice(0, 10)) {
      const emoji = signal.signal === 'buy' ? '🟢' : signal.signal === 'sell' ? '🔴' : '⚪';
      console.log(`  ${emoji} ${signal.pair} | ${signal.signal.toUpperCase()} | 置信度: ${signal.confidence}/10`);
      console.log(`     原因: ${signal.reason}`);
      if (signal.amount) {
        console.log(`     仓位: ${signal.amount}% | 止损: ${signal.stopLoss?.toFixed(4)} | 止盈: ${signal.takeProfit?.toFixed(4)}`);
      }
      console.log();
    }
  }
  
  // 按策略分组统计
  console.log('📊 按策略统计:');
  console.log('-'.repeat(40));
  const byStrategy = new Map<string, number>();
  for (const s of allSignals) {
    const name = s.source.split('-')[0];
    byStrategy.set(name, (byStrategy.get(name) || 0) + 1);
  }
  for (const [name, count] of byStrategy) {
    const strat = manager.getStrategy(name as any);
    console.log(`  ${strat?.getAlias()}: ${count} 个信号`);
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('✅ 策略测试完成\n');
}

testStrategies().catch(console.error);
