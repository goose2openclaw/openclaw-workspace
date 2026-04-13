/**
 * 🎯 推荐中心 V3 - 三位一体自适应决策系统
 * 
 * 核心竞争优势:
 * 1. AI动态权重调整 ← 仿真结果实时修正
 * 2. 做多做空灵活切换 ← 市场信号驱动
 * 3. 仿真参数校准 ← 真实市场数据持续输入
 */

import { useState, useEffect, useCallback } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8004";

interface ToolItem {
  id: string;
  name: string;
  direction: string;
  normalized_weight: number;
  sim_confidence: number;
  sim_wr: string;
  sim_sharpe: number;
  recommendation: string;
}

interface AdaptiveDecision {
  market_data: Record<string, number>;
  decision: { direction: string; market_confidence: number; long_confidence: number; short_confidence: number };
  weighted_metrics: { weighted_return: number; weighted_sharpe: number; weighted_confidence: number };
  go2se_tools: ToolItem[];
  quant_strategies: ToolItem[];
  summary: { action: string; confidence: string; top_tool: string; top_weight: string; weighted_return_estimate: string; weighted_sharpe_estimate: string };
  system: string;
  core_advantage: string;
}

export default function RecommendationHub() {
  const [data, setData] = useState<AdaptiveDecision | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'adaptive' | 'tools' | 'compare'>('adaptive');

  const fetchDecision = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/quant/adaptive-decision`);
      if (res.ok) {
        const d = await res.json();
        setData(d);
        setLastUpdate(new Date().toLocaleTimeString());
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchDecision(); }, [fetchDecision]);

  const signalColor = data?.decision.direction === 'LONG' ? '#10B981' 
    : data?.decision.direction === 'SHORT' ? '#EF4444' 
    : '#9CA3AF';

  const m = data?.market_data || {};
  const dec = data?.decision || { direction: 'HOLD', market_confidence: 0, long_confidence: 0, short_confidence: 0 };
  const wm = data?.weighted_metrics || { weighted_return: 0, weighted_sharpe: 0, weighted_confidence: 0 };

  return (
    <div style={{ padding: 0 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
        <h2 style={{ margin: 0 }}>🎯 三位一体自适应决策</h2>
        <div style={{ display: 'flex', gap: 4, background: 'rgba(255,255,255,0.05)', padding: 4, borderRadius: 10 }}>
          {(['adaptive', 'tools', 'compare'] as const).map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{ padding: '8px 14px', border: 'none', borderRadius: 8, background: activeTab === tab ? 'linear-gradient(135deg, #3B82F6, #1D4ED8)' : 'transparent', color: activeTab === tab ? 'white' : '#9CA3AF', cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
              {tab === 'adaptive' ? '🧠 自适应' : tab === 'tools' ? '🐰 GO2SE' : '📊 量化'}
            </button>
          ))}
        </div>
        <button onClick={fetchDecision} disabled={loading} style={{ padding: '6px 14px', border: 'none', borderRadius: 8, background: loading ? '#374151' : 'linear-gradient(135deg, #10B981, #059669)', color: 'white', cursor: loading ? 'not-allowed' : 'pointer', fontSize: 12, fontWeight: 600 }}>
          {loading ? '更新中...' : '🔄 刷新'}
        </button>
        <span style={{ fontSize: 11, color: '#6B7280' }}>更新: {lastUpdate}</span>
      </div>

      {/* Core Advantage Banner */}
      <div style={{ padding: '10px 16px', background: 'linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.15))', borderRadius: 12, marginBottom: 16, border: '1px solid rgba(59,130,246,0.2)' }}>
        <div style={{ fontSize: 11, color: '#A78BFA', marginBottom: 4 }}>🎯 核心竞争优势</div>
        <div style={{ fontSize: 13, color: '#E5E7EB' }}>{data?.core_advantage || '加载中...'}</div>
        <div style={{ fontSize: 11, color: '#6B7280', marginTop: 4, fontFamily: 'monospace' }}>公式: true_confidence = sim_wr × market_conf × dir_coef × sharpe_factor</div>
      </div>

      {/* Decision Bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '12px 16px', background: signalColor + '15', border: `1px solid ${signalColor}30`, borderRadius: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 12, color: '#9CA3AF' }}>决策</span>
          <span style={{ fontSize: 20, fontWeight: 700, padding: '4px 14px', borderRadius: 8, background: signalColor + '22', color: signalColor }}>
            {dec.direction} {data?.summary.action?.split(' ')[1] || ''}
          </span>
          <span style={{ fontSize: 12, color: '#6B7280' }}>置信度: {(dec.market_confidence * 100).toFixed(1)}%</span>
        </div>
        <div style={{ flex: 1, height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3, display: 'flex', minWidth: 100, overflow: 'hidden' }}>
          <div style={{ width: dec.long_confidence * 100, background: '#10B981', height: '100%', transition: 'width 0.3s' }}></div>
          <div style={{ width: dec.short_confidence * 100, background: '#EF4444', height: '100%', transition: 'width 0.3s' }}></div>
        </div>
        <span style={{ fontSize: 11, color: '#6B7280' }}>做多{(dec.long_confidence * 100).toFixed(0)}% | 做空{(dec.short_confidence * 100).toFixed(0)}%</span>
      </div>

      {/* Market Data */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: 8, marginBottom: 16 }}>
        {[
          { label: '24h涨跌', value: `${m.change_24h > 0 ? '+' : ''}${m.change_24h?.toFixed(2) || 0}%`, color: m.change_24h > 0 ? '#10B981' : '#EF4444' },
          { label: 'RSI', value: `${m.rsi?.toFixed(1) || 0}`, color: m.rsi > 70 ? '#EF4444' : m.rsi < 30 ? '#10B981' : '#9CA3AF' },
          { label: 'MACD', value: `${m.macd_hist?.toFixed(0) || 0}`, color: m.macd_hist > 0 ? '#10B981' : '#EF4444' },
          { label: '成交量比', value: `${m.volume_ratio?.toFixed(2) || 0}x`, color: m.volume_ratio > 1.5 ? '#3B82F6' : '#9CA3AF' },
          { label: '波动率', value: `${((m.volatility || 0) * 100).toFixed(1)}%`, color: m.volatility > 0.07 ? '#F59E0B' : '#9CA3AF' },
        ].map(item => (
          <div key={item.label} style={{ background: 'rgba(255,255,255,0.04)', borderRadius: 10, padding: '10px 12px', textAlign: 'center' }}>
            <div style={{ fontSize: 11, color: '#6B7280' }}>{item.label}</div>
            <div style={{ fontSize: 16, fontWeight: 700, color: item.color }}>{item.value}</div>
          </div>
        ))}
      </div>

      {/* Weighted Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: 8, marginBottom: 20 }}>
        {[
          { label: '加权收益(仿真)', value: `${(wm.weighted_return * 100).toFixed(1)}%`, color: '#10B981' },
          { label: '加权夏普(仿真)', value: wm.weighted_sharpe.toFixed(2), color: '#A78BFA' },
          { label: '加权置信(仿真)', value: `${(wm.weighted_confidence * 100).toFixed(1)}%`, color: '#3B82F6' },
        ].map(item => (
          <div key={item.label} style={{ background: 'rgba(255,255,255,0.04)', borderRadius: 10, padding: '10px 12px' }}>
            <div style={{ fontSize: 11, color: '#6B7280' }}>{item.label}</div>
            <div style={{ fontSize: 18, fontWeight: 700, color: item.color }}>{item.value}</div>
          </div>
        ))}
      </div>

      {/* Adaptive Tab */}
      {activeTab === 'adaptive' && data && (
        <div>
          <h3 style={{ margin: '0 0 12px 0' }}>🐰 GO2SE 五大工具 (仿真校准权重)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 10, marginBottom: 20 }}>
            {data.go2se_tools.map(tool => (
              <div key={tool.id} style={{ background: 'rgba(255,255,255,0.04)', border: `1px solid ${dec.direction === 'LONG' ? 'rgba(16,185,129,0.3)' : dec.direction === 'SHORT' ? 'rgba(239,68,68,0.3)' : 'rgba(255,255,255,0.08)'}`, borderRadius: 12, padding: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <span style={{ fontWeight: 700, fontSize: 14, flex: 1 }}>{tool.name}</span>
                  <span style={{ fontSize: 12, padding: '2px 8px', borderRadius: 6, background: tool.recommendation.includes('LONG') ? 'rgba(16,185,129,0.2)' : tool.recommendation.includes('SHORT') ? 'rgba(239,68,68,0.2)' : 'rgba(156,163,175,0.2)', color: tool.recommendation.includes('LONG') ? '#10B981' : tool.recommendation.includes('SHORT') ? '#EF4444' : '#9CA3AF' }}>
                    {tool.recommendation}
                  </span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, fontSize: 12 }}>
                  <div style={{ textAlign: 'center', padding: 6, background: 'rgba(255,255,255,0.03)', borderRadius: 6 }}>
                    <div style={{ color: '#6B7280', fontSize: 10 }}>权重</div>
                    <div style={{ color: '#3B82F6', fontWeight: 700 }}>{(tool.normalized_weight * 100).toFixed(1)}%</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: 6, background: 'rgba(255,255,255,0.03)', borderRadius: 6 }}>
                    <div style={{ color: '#6B7280', fontSize: 10 }}>仿真胜率</div>
                    <div style={{ color: '#10B981', fontWeight: 700 }}>{tool.sim_wr}</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: 6, background: 'rgba(255,255,255,0.03)', borderRadius: 6 }}>
                    <div style={{ color: '#6B7280', fontSize: 10 }}>仿真置信</div>
                    <div style={{ color: '#A78BFA', fontWeight: 700 }}>{(tool.sim_confidence * 100).toFixed(0)}%</div>
                  </div>
                </div>
                <div style={{ marginTop: 8, fontSize: 11, color: '#6B7280' }}>
                  仿真夏普: <b style={{ color: '#A78BFA' }}>{tool.sim_sharpe}</b>
                </div>
              </div>
            ))}
          </div>

          <h3 style={{ margin: '0 0 12px 0' }}>📊 十大量化策略 (仿真校准权重)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 8 }}>
            {data.quant_strategies.map(strat => (
              <div key={strat.id} style={{ background: 'rgba(255,255,255,0.04)', borderRadius: 10, padding: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                  <span style={{ fontWeight: 600, fontSize: 13, flex: 1 }}>{strat.name}</span>
                  <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, background: strat.direction === 'SHORT' ? 'rgba(239,68,68,0.2)' : strat.direction === 'REDUCE' ? 'rgba(245,158,11,0.2)' : 'rgba(16,185,129,0.2)', color: strat.direction === 'SHORT' ? '#EF4444' : strat.direction === 'REDUCE' ? '#F59E0B' : '#10B981' }}>
                    {strat.direction}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: 8, fontSize: 11 }}>
                  <span>权重: <b style={{ color: '#3B82F6' }}>{(strat.normalized_weight * 100).toFixed(1)}%</b></span>
                  <span>胜率: <b style={{ color: '#10B981' }}>{strat.sim_wr}</b></span>
                  <span>置信: <b style={{ color: '#A78BFA' }}>{(strat.sim_confidence * 100).toFixed(0)}%</b></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* GO2SE Tools Tab */}
      {activeTab === 'tools' && data && (
        <div>
          <h3 style={{ margin: '0 0 12px 0' }}>🐰 GO2SE 五大工具详情</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 12 }}>
            {data.go2se_tools.map(tool => (
              <div key={tool.id} style={{ background: 'rgba(255,255,255,0.04)', borderRadius: 12, padding: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <span style={{ fontSize: 24 }}>{tool.name.split(' ')[0]}</span>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 15 }}>{tool.name.split(' ')[1]}</div>
                    <div style={{ fontSize: 12, color: '#6B7280' }}>仿真胜率: {tool.sim_wr} | 夏普: {tool.sim_sharpe}</div>
                  </div>
                  <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                    <div style={{ fontSize: 18, fontWeight: 700, color: '#3B82F6' }}>{(tool.normalized_weight * 100).toFixed(1)}%</div>
                    <div style={{ fontSize: 10, color: '#6B7280' }}>权重</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 4, height: 6, borderRadius: 3, overflow: 'hidden' }}>
                  <div style={{ width: `${tool.sim_confidence * 100 * 3}%`, background: '#10B981', transition: 'width 0.3s' }}></div>
                  <div style={{ width: `${(1 - tool.sim_confidence) * 100 * 3}%`, background: 'rgba(255,255,255,0.1)' }}></div>
                </div>
                <div style={{ marginTop: 8, fontSize: 11, color: '#6B7280' }}>
                  仿真置信度: {(tool.sim_confidence * 100).toFixed(1)}% | 方向: {tool.recommendation}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Compare Tab */}
      {activeTab === 'compare' && data && (
        <div>
          <h3 style={{ margin: '0 0 12px 0' }}>⚖️ 仿真校准前后对比</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12, marginBottom: 20 }}>
            {[
              { label: '校准后加权收益', value: `${(wm.weighted_return * 100).toFixed(1)}%`, note: '仿真参数', color: '#10B981' },
              { label: '校准后加权夏普', value: wm.weighted_sharpe.toFixed(2), note: '风险调整', color: '#A78BFA' },
              { label: '校准后加权置信', value: `${(wm.weighted_confidence * 100).toFixed(1)}%`, note: '综合判断', color: '#3B82F6' },
              { label: 'TOP工具', value: data.summary.top_tool, note: data.summary.top_weight, color: '#F59E0B' },
            ].map(item => (
              <div key={item.label} style={{ background: 'rgba(255,255,255,0.04)', borderRadius: 10, padding: 14 }}>
                <div style={{ fontSize: 11, color: '#6B7280' }}>{item.label}</div>
                <div style={{ fontSize: 22, fontWeight: 700, color: item.color }}>{item.value}</div>
                <div style={{ fontSize: 10, color: '#6B7280' }}>{item.note}</div>
              </div>
            ))}
          </div>
          
          <h4 style={{ margin: '0 0 8px 0' }}>📊 策略排名 (按仿真校准权重)</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {[...data.go2se_tools.map(t => ({ ...t, source: 'GO2SE' as const })), ...data.quant_strategies.map(s => ({ ...s, source: '量化' as const, name: s.name }))]
              .sort((a, b) => b.normalized_weight - a.normalized_weight)
              .slice(0, 12)
              .map((item, i) => (
                <div key={i} style={{ display: 'grid', gridTemplateColumns: '30px 50px 1fr 60px 60px 80px', gap: 8, alignItems: 'center', padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: 8, fontSize: 12 }}>
                  <span style={{ fontWeight: 700, color: '#6B7280' }}>#{i + 1}</span>
                  <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, background: item.source === 'GO2SE' ? 'rgba(59,130,246,0.2)' : 'rgba(139,92,246,0.2)', color: item.source === 'GO2SE' ? '#60A5FA' : '#A78BFA', textAlign: 'center' }}>{item.source}</span>
                  <span style={{ fontWeight: 600 }}>{item.name}</span>
                  <span style={{ color: '#3B82F6', fontWeight: 600 }}>{(item.normalized_weight * 100).toFixed(1)}%</span>
                  <span style={{ color: '#10B981' }}>{item.sim_wr}</span>
                  <span style={{ color: '#6B7280' }}>置信: {(item.sim_confidence * 100).toFixed(0)}%</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
