/**
 * 🪿 GO2SE L6 Analytics Module - 数据分析完整页面
 * ================================================
 * 严格遵循v13版面构造
 * 8大功能: 概览 / 工具绩效 / 月报 / 历史 / 风险 / 对比 / 回测 / 系统
 */
(function() {
    'use strict';

    const AnalyticsModule = {
        state: {
            level: 1,
            period: '30d',
            activeTab: 'overview',
            historyPage: 1,
            historyFilter: 'all',
            sortField: 'time',
            sortDir: 'desc',
            data: null,
            history: [],
            historyStats: null,
            loading: false,
            tabs: [
                { id: 'overview',      label: '📊 概览',     icon: '📊' },
                { id: 'tools',         label: '🛠️ 工具绩效', icon: '🛠️' },
                { id: 'monthly',       label: '📅 月报',     icon: '📅' },
                { id: 'history',      label: '📜 历史',     icon: '📜' },
                { id: 'risk',         label: '🛡️ 风险',     icon: '🛡️' },
                { id: 'comparison',   label: '📈 对比',     icon: '📈' },
                { id: 'backtest',     label: '🔬 回测',     icon: '🔬' },
                { id: 'system',       label: '⚙️ 系统',     icon: '⚙️' }
            ]
        },

        API_BASE: 'http://localhost:8004/api',

        init: function() {
            this.bindEvents();
            this.render();
        },

        bindEvents: function() {
            const self = this;
            document.addEventListener('click', function(e) {
                // Tab switching
                const tabBtn = e.target.closest('[data-analytics-tab]');
                if (tabBtn) {
                    self.state.activeTab = tabBtn.dataset.analyticsTab;
                    self.renderTabContent();
                    return;
                }
                // Period switch
                const periodBtn = e.target.closest('[data-period]');
                if (periodBtn) {
                    self.state.period = periodBtn.dataset.period;
                    self.renderTabContent();
                    return;
                }
                // History filter
                const histBtn = e.target.closest('[data-history-filter]');
                if (histBtn) {
                    self.state.historyFilter = histBtn.dataset.historyFilter;
                    self.state.historyPage = 1;
                    self.renderHistory();
                    return;
                }
                // Pagination
                const pgBtn = e.target.closest('[data-history-page]');
                if (pgBtn) {
                    const dir = pgBtn.dataset.historyPage;
                    if (dir === 'prev') self.state.historyPage = Math.max(1, self.state.historyPage - 1);
                    else if (dir === 'next') self.state.historyPage++;
                    else self.state.historyPage = parseInt(pgBtn.dataset.historyPage);
                    self.renderHistory();
                    return;
                }
                // Sort
                const sortBtn = e.target.closest('[data-sort]');
                if (sortBtn) {
                    const f = sortBtn.dataset.sort;
                    if (self.state.sortField === f) {
                        self.state.sortDir = self.state.sortDir === 'asc' ? 'desc' : 'asc';
                    } else {
                        self.state.sortField = f;
                        self.state.sortDir = 'desc';
                    }
                    self.renderHistory();
                    return;
                }
            });
        },

        navigateLevel: function(level) {
            this.state.level = level;
            if (level === 6) {
                this.loadData();
                document.getElementById('analyticsPanelContainer').style.display = 'block';
                this.render();
                this.startAutoRefresh();
            } else {
                document.getElementById('analyticsPanelContainer').style.display = 'none';
            }
        },

        closePanel: function() {
            this.navigateLevel(1);
        },

        loadData: function() {
            const self = this;
            this.state.loading = true;

            Promise.all([
                fetch(this.API_BASE + '/analytics/overview').then(r => r.json()).catch(() => null),
                fetch(this.API_BASE + '/history?page=1&page_size=50').then(r => r.json()).catch(() => null),
                fetch(this.API_BASE + '/history/stats').then(r => r.json()).catch(() => null)
            ]).then(function([analytics, historyResp, histStats]) {
                self.state.data = analytics;
                self.state.history = historyResp && historyResp.history ? historyResp.history : [];
                self.state.historyStats = histStats;
                self.state.loading = false;
                self.renderTabContent();
            });
        },

        startAutoRefresh: function() {
            const self = this;
            if (this._refreshTimer) clearInterval(this._refreshTimer);
            this._refreshTimer = setInterval(function() {
                if (self.state.level === 6) self.loadData();
            }, 30000);
        },

        // ── Render ──────────────────────────────────────────────────────
        render: function() {
            const c = document.getElementById('analyticsPanelContainer');
            if (!c) return;
            const lv = this.state.level;
            const labels = {1:'总览',2:'详情',3:'设置',4:'执行',5:'历史',6:'分析'};
            const colors = {1:'#00d4aa',2:'#7c3aed',3:'#f59e0b',4:'#ef4444',5:'#3b82f6',6:'#ec4899'};
            const icons  = {1:'📊',2:'🔍',3:'⚙️',4:'▶️',5:'📜',6:'📈'};

            c.innerHTML = `
            <div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.97); z-index:9000; overflow:auto;">
              <div style="max-width:1100px; margin:0 auto; padding:20px;">

                <!-- Header -->
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                  <div>
                    <span style="font-size:28px;">📈</span>
                    <span style="font-size:20px; font-weight:700; color:#fff; margin-left:8px;">L6 数据分析</span>
                    <span style="font-size:11px; background:#ec4899; color:#fff; padding:2px 8px; border-radius:20px; margin-left:10px; font-weight:600;">ANALYTICS</span>
                    <span style="font-size:11px; color:rgba(255,255,255,0.4); margin-left:10px;">|</span>
                    <span style="font-size:12px; color:rgba(255,255,255,0.5); margin-left:10px;">实时数据 · 30秒自动刷新</span>
                  </div>
                  <div style="display:flex; gap:10px; align-items:center;">
                    <button onclick="AnalyticsModule.loadData()" style="padding:6px 14px; background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); color:#fff; border-radius:6px; cursor:pointer; font-size:12px;">🔄 刷新</button>
                    <button onclick="AnalyticsModule.closePanel()" style="background:none; border:none; color:#888; font-size:28px; cursor:pointer; line-height:1;">✕</button>
                  </div>
                </div>

                <!-- Breadcrumb -->
                <div style="display:flex; gap:6px; margin-bottom:20px; flex-wrap:wrap;">
                  ${[1,2,3,4,5,6].map(l => `
                    <button onclick="AnalyticsModule.navigateLevel(${l})" style="
                      padding:6px 14px;
                      background:${lv===l ? colors[l] : 'rgba(255,255,255,0.08)'};
                      color:${lv===l ? '#000' : 'rgba(255,255,255,0.7)'};
                      border:1px solid ${lv===l ? colors[l] : 'rgba(255,255,255,0.15)'};
                      border-radius:6px; cursor:pointer; font-size:12px; font-weight:${lv===l?'700':'400'};
                      ${l>=5?'box-shadow: 0 0 8px rgba(236,72,153,0.3);':''}
                    ">${icons[l]} ${labels[l]}${l>=5?' ✦':''}</button>
                  `).join('<span style="color:rgba(255,255,255,0.3); line-height:32px;">›</span>')}
                </div>

                <!-- Tab Bar -->
                <div style="display:flex; gap:4px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0; margin-bottom:20px; flex-wrap:wrap;">
                  ${this.state.tabs.map(t => `
                    <button data-analytics-tab="${t.id}" style="
                      padding:10px 16px;
                      background:${this.state.activeTab===t.id?'rgba(236,72,153,0.15)':'transparent'};
                      border:none;
                      border-bottom:2px solid ${this.state.activeTab===t.id?'#ec4899':'transparent'};
                      color:${this.state.activeTab===t.id?'#ec4899':'rgba(255,255,255,0.55)'};
                      cursor:pointer; font-size:13px; font-weight:${this.state.activeTab===t.id?'700':'400'};
                      transition:all 0.2s;
                      white-space:nowrap;
                    ">${t.icon} ${t.label}</button>
                  `).join('')}
                </div>

                <!-- Tab Content -->
                <div id="analyticsTabContent">${this.state.loading ? this.renderLoading() : ''}</div>

              </div>
            </div>`;

            if (!this.state.loading) this.renderTabContent();
        },

        renderLoading: function() {
            return `<div style="text-align:center; padding:60px; color:#888;">
              <div style="font-size:32px; margin-bottom:16px;">⏳</div>
              <div style="color:#555;">加载中...</div>
            </div>`;
        },

        renderTabContent: function() {
            const c = document.getElementById('analyticsTabContent');
            if (!c) return;
            switch (this.state.activeTab) {
                case 'overview':    c.innerHTML = this.renderOverview(); break;
                case 'tools':       c.innerHTML = this.renderTools(); break;
                case 'monthly':     c.innerHTML = this.renderMonthly(); break;
                case 'history':     c.innerHTML = this.renderHistory(); break;
                case 'risk':        c.innerHTML = this.renderRisk(); break;
                case 'comparison':  c.innerHTML = this.renderComparison(); break;
                case 'backtest':    c.innerHTML = this.renderBacktest(); break;
                case 'system':      c.innerHTML = this.renderSystem(); break;
            }
        },

        // ── Tab: 概览 ────────────────────────────────────────────────────
        renderOverview: function() {
            const d = this.state.data || {};
            const hs = this.state.historyStats || {};
            const cards = [
                { label: '总收益',      value: this.fmtMoney(d.total_profit),             color: '#00d4aa', icon: '💰' },
                { label: '收益率',      value: (d.return_rate||0)+'%',                   color: '#00d4aa', icon: '📈' },
                { label: '最大回撤',     value: (d.max_drawdown||0)+'%',                  color: '#ef4444', icon: '📉' },
                { label: '夏普比率',     value: d.sharpe_ratio||'—',                       color: '#7c3aed', icon: '🎯' },
                { label: '交易次数',    value: d.trade_count||0,                         color: '#3b82f6', icon: '🔢' },
                { label: '胜率',        value: (d.win_rate||0)+'%',                       color: '#f59e0b', icon: '✅' },
                { label: '平均单笔',    value: this.fmtMoney(d.avg_profit_per_trade),    color: '#06b6d4', icon: '⚖️' },
                { label: '今日操作',    value: hs.today_ops||0,                           color: '#8b5cf6', icon: '⚡' },
            ];
            return `
            <div>
              <!-- KPI Cards Grid -->
              <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px,1fr)); gap:12px; margin-bottom:24px;">
                ${cards.map(c => `
                <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:16px; position:relative; overflow:hidden;">
                  <div style="position:absolute; top:0; right:0; width:60px; height:60px; background:linear-gradient(135deg, ${c.color}22, transparent); border-radius:0 12px 0 60px;"></div>
                  <div style="font-size:11px; color:rgba(255,255,255,0.5); margin-bottom:8px; font-weight:500;">${c.icon} ${c.label}</div>
                  <div style="font-size:24px; font-weight:700; color:${c.color}; font-family:'JetBrains Mono',monospace;">${c.value}</div>
                </div>`).join('')}
              </div>

              <!-- Quick Chart: 月度收益趋势 -->
              <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:20px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                  <div style="font-size:14px; font-weight:600;">📊 月度收益趋势</div>
                  <div style="font-size:11px; color:#555;">${(d.monthly_profit||[]).length}个月数据</div>
                </div>
                <div style="display:flex; align-items:flex-end; gap:8px; height:120px;">
                  ${(d.monthly_profit||[]).map(m => {
                    const vals = (d.monthly_profit||[]).map(x=>x.profit);
                    const max = Math.max(...vals, 1);
                    const h = Math.max(4, Math.abs(m.profit)/max*100);
                    const pos = m.profit >= 0;
                    return `<div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:4px;">
                      <div style="font-size:10px; color:#555;">${this.fmtMoney(m.profit)}</div>
                      <div style="width:100%; height:${h}px; background:${pos?'linear-gradient(180deg,#00d4aa,#00a884)':'linear-gradient(180deg,#ef4444,#dc2626)'}; border-radius:4px 4px 0 0; min-height:4px;"></div>
                      <div style="font-size:10px; color:rgba(255,255,255,0.5);">${(m.month||'').slice(5)}</div>
                    </div>`;}).join('')}
                </div>
              </div>

              <!-- 7工具收益分布 -->
              <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:20px;">
                <div style="font-size:14px; font-weight:600; margin-bottom:16px;">🛠️ 工具收益分布</div>
                ${Object.entries(d.profit_by_tool||{}).map(([tool, info]) => {
                  const total = d.total_profit||1;
                  const pct = ((info.profit/total)*100).toFixed(1);
                  const color = info.profit>=0?'#00d4aa':'#ef4444';
                  return `<div style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                      <span style="color:rgba(255,255,255,0.8);">${tool}</span>
                      <span style="color:${color}; font-family:'JetBrains Mono',monospace;">${this.fmtMoney(info.profit)} <span style="color:#555;">(${pct}%)</span></span>
                    </div>
                    <div style="height:6px; background:rgba(255,255,255,0.08); border-radius:3px; overflow:hidden;">
                      <div style="height:100%; width:${pct}%; background:${color}; border-radius:3px;"></div>
                    </div>
                    <div style="font-size:10px; color:#555; margin-top:2px;">${info.trades}笔 · ${info.win_rate}%胜率</div>
                  </div>`;}).join('')}
              </div>
            </div>`;
        },

        // ── Tab: 工具绩效 ────────────────────────────────────────────────
        renderTools: function() {
            const d = this.state.data || {};
            const pbt = d.profit_by_tool || {};
            const toolOrder = ['打兔子','打地鼠','走着瞧','跟大哥','搭便车','薅羊毛','穷孩子'];
            const toolIcons = {'打兔子':'🐰','打地鼠':'🐹','走着瞧':'🔮','跟大哥':'👑','搭便车':'🍀','薅羊毛':'💰','穷孩子':'👶'};
            const toolDesc  = {'打兔子':'EMA趋势·MACD','打地鼠':'布林带·波动率','走着瞧':'MiroFish预测','跟大哥':'KOL跟随','搭便车':'跟单分成','薅羊毛':'空投猎手','穷孩子':'EvoMap众包'};
            const colors = ['#00d4aa','#7c3aed','#f59e0b','#3b82f6','#ec4899','#06b6d4','#84cc16'];
            const tools = toolOrder.map((t,i) => ({ name:t, icon:toolIcons[t], desc:toolDesc[t], info:pbt[t], color:colors[i] }));
            const maxProfit = Math.max(...tools.map(t => Math.abs(t.info?.profit||0)), 1);

            return `
            <div>
              <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(300px,1fr)); gap:16px;">
                ${tools.map(t => {
                  const profit = t.info?.profit||0;
                  const trades = t.info?.trades||0;
                  const wr = t.info?.win_rate||0;
                  const barW = (Math.abs(profit)/maxProfit*100).toFixed(1);
                  const pos = profit>=0;
                  return `
                  <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                      <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:24px;">${t.icon}</span>
                        <div>
                          <div style="font-size:14px; font-weight:600; color:#fff;">${t.name}</div>
                          <div style="font-size:10px; color:#555;">${t.desc}</div>
                        </div>
                      </div>
                      <div style="text-align:right;">
                        <div style="font-size:18px; font-weight:700; color:${pos?'#00d4aa':'#ef4444'}; font-family:'JetBrains Mono',monospace;">${this.fmtMoney(profit)}</div>
                        <div style="font-size:11px; color:#555;">${trades}笔 · ${wr}%胜</div>
                      </div>
                    </div>
                    <div style="height:6px; background:rgba(255,255,255,0.08); border-radius:3px; overflow:hidden;">
                      <div style="height:100%; width:${barW}%; background:${t.color}; border-radius:3px; transition:width 0.6s ease;"></div>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top:6px;">
                      <span style="font-size:10px; color:#555;">收益占比</span>
                      <span style="font-size:10px; color:${t.color}; font-weight:600;">${barW}%</span>
                    </div>
                  </div>`;}).join('')}
              </div>
            </div>`;
        },

        // ── Tab: 月报 ────────────────────────────────────────────────────
        renderMonthly: function() {
            const d = this.state.data || {};
            const monthly = d.monthly_profit || [];
            const total = monthly.reduce((s,m)=>s+m.profit,0);
            const avg = monthly.length ? total/monthly.length : 0;
            const best = monthly.length ? monthly.reduce((a,b)=>a.profit>b.profit?a:b) : null;
            const worst = monthly.length ? monthly.reduce((a,b)=>a.profit<b.profit?a:b) : null;

            return `
            <div>
              <!-- Stat summary -->
              <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:20px;">
                ${[
                  {label:'累计收益', value:this.fmtMoney(total), color:total>=0?'#00d4aa':'#ef4444'},
                  {label:'月均收益', value:this.fmtMoney(avg), color:avg>=0?'#00d4aa':'#ef4444'},
                  {label:'盈利月数', value:monthly.filter(m=>m.profit>0).length+'/'+monthly.length, color:'#7c3aed'}
                ].map(s => `
                <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:14px; text-align:center;">
                  <div style="font-size:11px; color:#555; margin-bottom:6px;">${s.label}</div>
                  <div style="font-size:22px; font-weight:700; color:${s.color}; font-family:'JetBrains Mono',monospace;">${s.value}</div>
                </div>`).join('')}
              </div>

              <!-- Bar chart -->
              <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:20px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:16px;">
                  <div style="font-size:14px; font-weight:600;">📅 月度收益明细</div>
                  <div style="font-size:11px; color:#555;">单位: USDT</div>
                </div>
                ${monthly.map((m,i) => {
                  const vals = monthly.map(x=>Math.abs(x.profit));
                  const max = Math.max(...vals,1);
                  const h = Math.max(6, (Math.abs(m.profit)/max)*160);
                  const pos = m.profit>=0;
                  return `
                  <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                    <div style="width:50px; font-size:11px; color:#555; text-align:right; flex-shrink:0;">${m.month?.slice(5)}月</div>
                    <div style="flex:1; display:flex; align-items:center; gap:8px;">
                      <div style="width:${(Math.abs(m.profit)/max*100).toFixed(1)}%; max-width:100%; height:${h}px; background:${pos?'linear-gradient(90deg,#00d4aa88,#00d4aa)':'linear-gradient(90deg,#ef444488,#ef4444)'}; border-radius:0 4px 4px 0; min-width:4px;"></div>
                    </div>
                    <div style="width:80px; font-size:12px; font-family:'JetBrains Mono',monospace; color:${pos?'#00d4aa':'#ef4444'}; text-align:right; flex-shrink:0;">${this.fmtMoney(m.profit)}</div>
                  </div>`;}).join('')}
              </div>

              <!-- Best/Worst -->
              ${best&&worst?`
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                <div style="background:rgba(0,212,170,0.08); border:1px solid rgba(0,212,170,0.2); border-radius:10px; padding:14px;">
                  <div style="font-size:11px; color:#00d4aa; margin-bottom:6px;">🏆 最佳月份</div>
                  <div style="font-size:14px; color:#fff; font-weight:600;">${best.month}</div>
                  <div style="font-size:18px; color:#00d4aa; font-weight:700; font-family:'JetBrains Mono',monospace;">${this.fmtMoney(best.profit)}</div>
                </div>
                <div style="background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.2); border-radius:10px; padding:14px;">
                  <div style="font-size:11px; color:#ef4444; margin-bottom:6px;">📉 最差月份</div>
                  <div style="font-size:14px; color:#fff; font-weight:600;">${worst.month}</div>
                  <div style="font-size:18px; color:#ef4444; font-weight:700; font-family:'JetBrains Mono',monospace;">${this.fmtMoney(worst.profit)}</div>
                </div>
              </div>`:''}
            </div>`;
        },

        // ── Tab: 历史 ────────────────────────────────────────────────────
        renderHistory: function() {
            const self = this;
            const page = this.state.historyPage;
            const filter = this.state.historyFilter;
            const sortF = this.state.sortField;
            const sortD = this.state.sortDir;
            const pageSize = 10;

            let hist = this.state.history.filter(function(h) {
                if (filter==='all') return true;
                if (filter==='success') return h.success;
                if (filter==='failed') return !h.success;
                return true;
            });

            hist.sort(function(a,b) {
                let av = a[sortF]||'', bv = b[sortF]||'';
                if (typeof av === 'string') av = av.toLowerCase(), bv = bv.toLowerCase();
                return sortD==='asc' ? (av>bv?1:-1) : (av<bv?1:-1);
            });

            const totalPages = Math.max(1, Math.ceil(hist.length/pageSize));
            const paged = hist.slice((page-1)*pageSize, page*pageSize);
            const hs = this.state.historyStats || {};

            return `
            <div>
              <!-- Stats row -->
              <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px,1fr)); gap:10px; margin-bottom:16px;">
                ${[
                  {label:'总操作', value:hs.total||0, color:'#fff'},
                  {label:'成功', value:hs.success||0, color:'#00d4aa'},
                  {label:'失败', value:(hs.failed||0), color:'#ef4444'},
                  {label:'成功率', value:(hs.success_rate||0)+'%', color:'#7c3aed'},
                  {label:'本周操作', value:hs.week_ops||0, color:'#f59e0b'}
                ].map(s => `
                <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:10px; text-align:center;">
                  <div style="font-size:10px; color:#555; margin-bottom:4px;">${s.label}</div>
                  <div style="font-size:18px; font-weight:700; color:${s.color}; font-family:'JetBrains Mono',monospace;">${s.value}</div>
                </div>`).join('')}
              </div>

              <!-- Filters -->
              <div style="display:flex; gap:6px; margin-bottom:12px; flex-wrap:wrap;">
                ${['all','success','failed'].map(f => `
                  <button data-history-filter="${f}" style="padding:5px 12px; background:${this.state.historyFilter===f?'#ec4899':'rgba(255,255,255,0.06)'}; color:${this.state.historyFilter===f?'#000':'rgba(255,255,255,0.6)'}; border:1px solid ${this.state.historyFilter===f?'#ec4899':'rgba(255,255,255,0.1)'}; border-radius:20px; cursor:pointer; font-size:11px;">${f==='all'?'全部':f==='success'?'✅成功':'❌失败'}</button>
                `).join('')}
              </div>

              <!-- Table -->
              <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; overflow:hidden;">
                <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; font-size:12px;">
                  <thead>
                    <tr style="background:rgba(255,255,255,0.04);">
                      ${[
                        {f:'time',label:'时间'},
                        {f:'action',label:'操作'},
                        {f:'tool',label:'工具'},
                        {f:'amount',label:'金额'},
                        {f:'status',label:'状态'},
                        {f:'success',label:'结果'}
                      ].map(h => `
                        <th data-sort="${h.f}" style="padding:10px 12px; text-align:left; color:rgba(255,255,255,0.5); font-weight:600; cursor:pointer; white-space:nowrap; border-bottom:1px solid rgba(255,255,255,0.06); ${self.state.sortField===h.f?'color:#ec4899;':''}">
                          ${h.label} ${self.state.sortField===h.f?(self.state.sortDir==='asc'?'↑':'↓'):''}
                        </th>`).join('')}
                    </tr>
                  </thead>
                  <tbody>
                    ${paged.length===0?'<tr><td colspan="6" style="text-align:center; padding:40px; color:#555;">暂无记录</td></tr>':paged.map(h => `
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04); transition:background 0.15s;" onmouseover="this.style.background='rgba(255,255,255,0.03)'" onmouseout="this.style.background='transparent'">
                      <td style="padding:9px 12px; color:#555; font-size:11px; font-family:'JetBrains Mono',monospace; white-space:nowrap;">${h.time||''}</td>
                      <td style="padding:9px 12px; color:#fff; font-weight:500;">${h.action||''}</td>
                      <td style="padding:9px 12px; color:#888;">${h.tool||'—'}</td>
                      <td style="padding:9px 12px; font-family:'JetBrains Mono',monospace; color:${(h.amount||0)>=0?'#00d4aa':'#ef4444'};">${this.fmtMoney(h.amount||0)}</td>
                      <td style="padding:9px 12px;"><span style="padding:2px 8px; border-radius:20px; font-size:10px; font-weight:600; background:${h.success?'rgba(0,212,170,0.15); color:#00d4aa;':'rgba(239,68,68,0.15); color:#ef4444;'}">${h.status||(h.success?'成功':'失败')}</span></td>
                      <td style="padding:9px 12px; color:${h.success?'#00d4aa':'#ef4444'};">${h.success?'✅':'❌'}</td>
                    </tr>`).join('')}
                  </tbody>
                </table>
                </div>

                <!-- Pagination -->
                <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 16px; border-top:1px solid rgba(255,255,255,0.06);">
                  <div style="font-size:11px; color:#555;">第${page}/${totalPages}页 · 共${hist.length}条</div>
                  <div style="display:flex; gap:6px;">
                    <button data-history-page="prev" style="padding:5px 12px; background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); color:#fff; border-radius:6px; cursor:pointer; font-size:11px;">‹ 上一页</button>
                    ${[1,2,3].filter(p => p<=totalPages).map(p => `
                      <button data-history-page="${p}" style="padding:5px 10px; background:${page===p?'#ec4899':'rgba(255,255,255,0.08)'}; color:${page===p?'#000':'#fff'}; border:1px solid ${page===p?'#ec4899':'rgba(255,255,255,0.15)'}; border-radius:6px; cursor:pointer; font-size:11px;">${p}</button>
                    `).join('')}
                    ${totalPages>3?`<span style="color:#555; padding:0 4px;">...</span>`:''}
                    <button data-history-page="next" style="padding:5px 12px; background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); color:#fff; border-radius:6px; cursor:pointer; font-size:11px;">下一页 ›</button>
                  </div>
                </div>
              </div>
            </div>`;
        },

        // ── Tab: 风险 ────────────────────────────────────────────────────
        renderRisk: function() {
            const d = this.state.data || {};
            const rm = d.risk_metrics || {};
            const metrics = [
                {label:'VaR (95%)', value: this.fmtMoney(rm.var_95||0), desc:'每日最大损失', color:'#ef4444'},
                {label:'波动率', value:(rm.volatility||0)+'%', desc:'年化波动率', color:'#f59e0b'},
                {label:'Beta', value:rm.beta||'—', desc:'相对BTC波动', color:'#7c3aed'},
                {label:'Sortino比率', value:rm.sortino_ratio||'—', desc:'下行风险调整', color:'#00d4aa'},
                {label:'夏普比率', value:d.sharpe_ratio||'—', desc:'风险调整收益', color:'#3b82f6'},
                {label:'最大回撤', value:(d.max_drawdown||0)+'%', desc:'历史最大回撤', color:'#ec4899'}
            ];
            return `
            <div>
              <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr)); gap:12px; margin-bottom:20px;">
                ${metrics.map(m => `
                <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:16px;">
                  <div style="font-size:11px; color:#555; margin-bottom:8px;">${m.label}</div>
                  <div style="font-size:22px; font-weight:700; color:${m.color}; font-family:'JetBrains Mono',monospace;">${m.value}</div>
                  <div style="font-size:10px; color:#444; margin-top:4px;">${m.desc}</div>
                </div>`).join('')}
              </div>

              <!-- Risk gauge visualization -->
              <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:20px;">
                <div style="font-size:14px; font-weight:600; margin-bottom:16px;">📊 风险仪表盘</div>
                ${[
                  {label:'收益稳定性', val: Math.min(100, (d.win_rate||0)*1.2), color:'#00d4aa'},
                  {label:'资金安全', val: Math.min(100, 100-(d.max_drawdown||0)*4), color:'#3b82f6'},
                  {label:'波动控制', val: Math.min(100, 100-(rm.volatility||0)*3), color:'#f59e0b'},
                  {label:'风险调整', val: Math.min(100, (d.sharpe_ratio||0)*30), color:'#7c3aed'}
                ].map(g => `
                <div style="margin-bottom:14px;">
                  <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:6px;">
                    <span style="color:#888;">${g.label}</span>
                    <span style="color:${g.color}; font-weight:600;">${Math.round(g.val)}%</span>
                  </div>
                  <div style="height:8px; background:rgba(255,255,255,0.08); border-radius:4px; overflow:hidden;">
                    <div style="height:100%; width:${Math.min(100,g.val)}%; background:${g.color}; border-radius:4px; box-shadow:0 0 8px ${g.color}66;"></div>
                  </div>
                </div>`).join('')}
              </div>
            </div>`;
        },

        // ── Tab: 对比 ────────────────────────────────────────────────────
        renderComparison: function() {
            const d = this.state.data || {};
            const go2se = d.return_rate||0;
            const market = 18.5;
            const alpha = (go2se - market).toFixed(1);
            const period = this.state.period;
            const periods = { '7d':5, '30d':18.5, '90d':32, '1y':78 };
            const marketVals = { '7d':3.2, '30d':18.5, '90d':28, '1y':65 };
            const curMarket = marketVals[period]||18.5;

            return `
            <div>
              <!-- Period Selector -->
              <div style="display:flex; gap:6px; margin-bottom:20px;">
                ${['7d','30d','90d','1y'].map(p => `
                  <button data-period="${p}" style="padding:6px 14px; background:${this.state.period===p?'#ec4899':'rgba(255,255,255,0.06)'}; color:${this.state.period===p?'#000':'rgba(255,255,255,0.6)'}; border:1px solid ${this.state.period===p?'#ec4899':'rgba(255,255,255,0.1)'}; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600;">${p}</button>
                `).join('')}
              </div>

              <!-- Comparison cards -->
              <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px,1fr)); gap:12px; margin-bottom:20px;">
                ${[
                  {label:'GO2SE收益率', value:go2se.toFixed(1)+'%', color:'#00d4aa', icon:'🪿'},
                  {label:'BTC基准收益', value:curMarket.toFixed(1)+'%', color:'#f59e0b', icon:'📋'},
                  {label:'Alpha超额', value:(alpha>=0?'+':'')+alpha+'%', color:alpha>=0?'#00d4aa':'#ef4444', icon:'🎯'},
                  {label:'跑赢基准', value:((go2se-curMarket)/curMarket*100).toFixed(1)+'%', color:'#7c3aed', icon:'🏆'}
                ].map(c => `
                <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:16px;">
                  <div style="font-size:11px; color:#555; margin-bottom:8px;">${c.icon} ${c.label}</div>
                  <div style="font-size:26px; font-weight:700; color:${c.color}; font-family:'JetBrains Mono',monospace;">${c.value}</div>
                </div>`).join('')}
              </div>

              <!-- Visual bar comparison -->
              <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:20px;">
                <div style="font-size:14px; font-weight:600; margin-bottom:16px;">⚖️ 收益对比</div>
                ${[
                  {label:'GO2SE', val:go2se, color:'#00d4aa'},
                  {label:'BTC市场', val:curMarket, color:'#f59e0b'}
                ].map(b => {
                  const max = Math.max(go2se, curMarket)*1.2||100;
                  return `
                  <div style="margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:6px;">
                      <span style="color:#888;">${b.label}</span>
                      <span style="color:${b.color}; font-weight:600; font-family:'JetBrains Mono',monospace;">${b.val.toFixed(1)}%</span>
                    </div>
                    <div style="height:16px; background:rgba(255,255,255,0.06); border-radius:8px; overflow:hidden;">
                      <div style="height:100%; width:${(b.val/max*100).toFixed(1)}%; background:${b.color}; border-radius:8px; box-shadow:0 0 10px ${b.color}66;"></div>
                    </div>
                  </div>`;}).join('')}
              </div>
            </div>`;
        },

        // ── Tab: 回测 ────────────────────────────────────────────────────
        renderBacktest: function() {
            // 嵌入30天回测核心数据
            const reports = [
              {
                name:'v15 (quad-brain)', period:'30天', mode:'激进',
                result:'+19.36%', wr:'100%', dd:'0.00%', trades:6, verdict:'✅ 极佳',
                color:'#00d4aa', Mi:'1.200'
              },
              {
                name:'vv6 (normal)', period:'30天', mode:'普通',
                result:'+17.30%', wr:'100%', dd:'-0.88%', trades:6, verdict:'✅ 优秀',
                color:'#00d4aa', Mi:'1.320'
              },
              {
                name:'vv6 (expert)', period:'30天', mode:'专家',
                result:'+6.32%', wr:'50%', dd:'-8.56%', trades:12, verdict:'⚠️ 牛市逆势',
                color:'#f59e0b', Mi:'1.285'
              }
            ];
            return `
            <div>
              <div style="margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
                <div style="font-size:14px; font-weight:600;">🔬 30天回测数据矩阵</div>
                <div style="font-size:11px; color:#555;">数据基于模拟 · 仅供参考</div>
              </div>

              <!-- Report Cards -->
              <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px,1fr)); gap:14px; margin-bottom:20px;">
                ${reports.map(r => `
                <div style="background:rgba(255,255,255,0.04); border:1px solid ${r.color}44; border-radius:12px; padding:16px; position:relative; overflow:hidden;">
                  <div style="position:absolute; top:0; left:0; right:0; height:3px; background:${r.color};"></div>
                  <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                    <div>
                      <div style="font-size:13px; font-weight:700; color:#fff;">${r.name}</div>
                      <div style="font-size:11px; color:#555;">${r.period} · ${r.mode}模式 · Mi=${r.Mi}</div>
                    </div>
                    <div style="text-align:right;">
                      <div style="font-size:20px; font-weight:700; color:${r.color}; font-family:'JetBrains Mono',monospace;">${r.result}</div>
                      <div style="font-size:11px; color:${r.color};">${r.verdict}</div>
                    </div>
                  </div>
                  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;">
                    ${[
                      {l:'胜率',v:r.wr},
                      {l:'最大回撤',v:r.dd},
                      {l:'交易次数',v:r.trades+'笔'}
                    ].map(m => `
                    <div style="background:rgba(255,255,255,0.04); border-radius:6px; padding:8px; text-align:center;">
                      <div style="font-size:10px; color:#555; margin-bottom:2px;">${m.l}</div>
                      <div style="font-size:14px; font-weight:700; color:#fff; font-family:'JetBrains Mono',monospace;">${m.v}</div>
                    </div>`).join('')}
                  </div>
                </div>`).join('')}
              </div>

              <!-- Regime distribution -->
              <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:20px;">
                <div style="font-size:14px; font-weight:600; margin-bottom:12px;">🌡️ 市场状态分布 (30天/720小时)</div>
                <div style="display:flex; gap:6px; height:24px; border-radius:6px; overflow:hidden; margin-bottom:8px;">
                  ${[
                    {l:'多头',w:28.2,c:'#00d4aa'},
                    {l:'空头',w:25.8,c:'#ef4444'},
                    {l:'中性',w:34.0,c:'#6b7280'},
                    {l:'波动',w:12.0,c:'#f59e0b'}
                  ].map(r => `<div style="width:${r.w}%; background:${r.c}; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:700; color:#000;">${r.l}${r.w>=12?' '+r.w+'%':''}</div>`).join('')}
                </div>
                <div style="font-size:11px; color:#555; text-align:center;">牛市专家模式做空逆势 → 3笔做空全部触止损 | 普通模式100%胜率</div>
              </div>
            </div>`;
        },

        // ── Tab: 系统 ────────────────────────────────────────────────────
        renderSystem: function() {
            const self = this;
            const systems = [
              { name:'v6a (前端)', port:8000, type:'frontend', desc:'主界面 · HTML' },
              { name:'v6i', port:8001, type:'agent', desc:'专家模式 · 自主循环' },
              { name:'vv6', port:8006, type:'snapshot', desc:'v6i快照 · 普通模式' },
              { name:'v13 (后端)', port:8004, type:'backend', desc:'7鑫系统 · FastAPI' },
              { name:'v15', port:8015, type:'quad-brain', desc:'四脑引擎 · decision v3' }
            ];
            return `
            <div>
              <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px,1fr)); gap:14px;">
                ${systems.map(s => `
                <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:16px;">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                    <div>
                      <div style="font-size:14px; font-weight:700; color:#fff; margin-bottom:4px;">${s.name}</div>
                      <div style="font-size:11px; color:#555;">${s.desc}</div>
                      <div style="font-size:11px; color:#444; font-family:'JetBrains Mono',monospace; margin-top:4px;">:${s.port}</div>
                    </div>
                    <div class="api-status-badge offline" id="sys-badge-${s.port}" style="font-size:11px; padding:4px 10px;">
                      <span class="api-dot-sm"></span> 检测中
                    </div>
                  </div>
                  <div style="display:flex; gap:6px;">
                    <button onclick="AnalyticsModule.checkSystem(${s.port},'${s.name}')" style="flex:1; padding:6px; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); color:#fff; border-radius:6px; cursor:pointer; font-size:11px;">🔄 检测</button>
                    <button onclick="AnalyticsModule.showSystemLog('${s.name}',${s.port})" style="flex:1; padding:6px; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); color:#fff; border-radius:6px; cursor:pointer; font-size:11px;">📋 日志</button>
                  </div>
                </div>`).join('')}
              </div>
            </div>`;
        },

        checkSystem: function(port, name) {
            const badge = document.getElementById('sys-badge-'+port);
            if (!badge) return;
            badge.innerHTML = '<span class="api-dot-sm"></span> 检测中';
            badge.className = 'api-status-badge offline';

            const url = port===8000 ? 'http://localhost:'+port+'/' : 'http://localhost:'+port+'/health';
            fetch(url, { signal: AbortSignal.timeout(3000) })
                .then(r => { badge.innerHTML = '<span class="api-dot-sm"></span> 在线'; badge.className = 'api-status-badge online'; })
                .catch(() => { badge.innerHTML = '<span class="api-dot-sm"></span> 离线'; badge.className = 'api-status-badge offline'; });
        },

        showSystemLog: function(name, port) {
            alert('📋 ' + name + ' 日志\n\n端口: ' + port + '\n功能: 即将推出\n可使用: curl http://localhost:' + port + '/health 查看状态');
        },

        // ── Util ─────────────────────────────────────────────────────────
        fmtMoney: function(v) {
            if (v === null || v === undefined) return '—';
            const n = parseFloat(v);
            if (isNaN(n)) return '—';
            return (n >= 0 ? '+$' : '-$') + Math.abs(n).toFixed(2);
        }
    };

    window.AnalyticsModule = AnalyticsModule;
    AnalyticsModule.init();
})();
