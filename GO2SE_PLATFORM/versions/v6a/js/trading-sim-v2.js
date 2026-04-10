// ==========================================================================
// GO2SE v6a - 交易仿真模块 V2
// 完整仿真引擎：回测 / Paper交易 / 实时仿真
// ==========================================================================

window.TradingSimV2 = {
    // ========================
    // 状态管理
    // ========================
    state: {
        mode: 'overview',      // overview | backtest | paper | live | history | settings
        tab: 'simulation',    // simulation | signals | portfolio
        // 仿真配置
        config: {
            initialCapital: 10000,
            currentCapital: 10000,
            maxPosition: 0.2,        // 单笔最大仓位 20%
            stopLoss: 0.05,          // 止损 5%
            takeProfit: 0.15,         // 止盈 15%
            commission: 0.001,        // 手续费 0.1%
            slippage: 0.0005,         // 滑点 0.05%
            leverage: 1,              // 杠杆
            riskPerTrade: 0.02        // 每笔风险 2%
        },
        // 持仓
        positions: [],
        // 历史交易
        trades: [],
        // 信号
        signals: [],
        // 仿真结果
        results: {
            totalTrades: 0,
            winningTrades: 0,
            losingTrades: 0,
            winRate: 0,
            totalPnL: 0,
            totalPnLPercent: 0,
            maxDrawdown: 0,
            sharpeRatio: 0,
            avgWin: 0,
            avgLoss: 0,
            profitFactor: 0,
            avgHoldingTime: 0
        },
        // 回测配置
        backtest: {
            startDate: '',
            endDate: '',
            symbols: ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
            strategies: ['trend_following', 'mean_reversion', 'grid_trading'],
            selectedStrategy: 'trend_following',
            interval: '1h'
        },
        // 行情数据
        prices: {},
        // 计时器
        timers: {},
        // API基础URL
        API_BASE: 'http://localhost:8004/api'
    },

    // ========================
    // 工具配置 (7大工具)
    // ========================
    tools: {
        rabbit: { name: '🐰 打兔子', allocation: 0.25, stopLoss: 0.05, takeProfit: 0.08 },
        mole: { name: '🐹 打地鼠', allocation: 0.20, stopLoss: 0.08, takeProfit: 0.15 },
        oracle: { name: '🔮 走着瞧', allocation: 0.15, stopLoss: 0.05, takeProfit: 0.10 },
        leader: { name: '👑 跟大哥', allocation: 0.15, stopLoss: 0.03, takeProfit: 0.06 },
        hitchhiker: { name: '🍀 搭便车', allocation: 0.10, stopLoss: 0.05, takeProfit: 0.08 },
        airdrop: { name: '💰 薅羊毛', allocation: 0.03, stopLoss: 0.02, takeProfit: 0.20 },
        crowdsource: { name: '👶 穷孩子', allocation: 0.02, stopLoss: 0.01, takeProfit: 0.30 }
    },

    // ========================
    // 初始化
    // ========================
    init: function() {
        console.log('🔮 TradingSimV2 initialized');
        this.loadState();
        this.fetchPrices();
        this.fetchSignals();
        this.startLiveUpdates();
        this.render();
    },

    // ========================
    // 状态持久化
    // ========================
    saveState: function() {
        localStorage.setItem('TradingSimV2', JSON.stringify({
            config: this.state.config,
            positions: this.state.positions,
            trades: this.state.trades,
            results: this.state.results
        }));
    },

    loadState: function() {
        var saved = localStorage.getItem('TradingSimV2');
        if (saved) {
            var data = JSON.parse(saved);
            this.state.config = data.config || this.state.config;
            this.state.positions = data.positions || [];
            this.state.trades = data.trades || [];
            this.state.results = data.results || this.state.results;
            this.recalculateResults();
        }
    },

    // ========================
    // 模式切换
    // ========================
    setMode: function(mode) {
        this.state.mode = mode;
        this.render();
    },

    setTab: function(tab) {
        this.state.tab = tab;
        this.render();
    },

    // ========================
    // 行情数据获取
    // ========================
    fetchPrices: function() {
        var self = this;
        // 模拟行情数据 (实际应调用API)
        // 打兔子: 前20主流加密货币
        this.state.prices = {
            // 主流币 (打兔子 - 25%仓位)
            BTCUSDT: { price: 75145.50, change: 3.62, high24h: 76500, low24h: 74200, volume: 28500000000, tool: 'rabbit' },
            ETHUSDT: { price: 3215.80, change: 2.85, high24h: 3280, low24h: 3150, volume: 15200000000, tool: 'rabbit' },
            BNBUSDT: { price: 598.20, change: 1.23, high24h: 605, low24h: 592, volume: 1200000000, tool: 'rabbit' },
            SOLUSDT: { price: 178.45, change: 5.42, high24h: 185, low24h: 170, volume: 8500000000, tool: 'rabbit' },
            XRPUSDT: { price: 0.5823, change: 1.45, high24h: 0.60, low24h: 0.57, volume: 1200000000, tool: 'rabbit' },
            ADAUSDT: { price: 0.4521, change: 2.12, high24h: 0.47, low24h: 0.44, volume: 450000000, tool: 'rabbit' },
            DOGEUSDT: { price: 0.1256, change: 3.85, high24h: 0.13, low24h: 0.12, volume: 890000000, tool: 'rabbit' },
            AVAXUSDT: { price: 35.42, change: 4.21, high24h: 36.5, low24h: 34.8, volume: 520000000, tool: 'rabbit' },
            DOTUSDT: { price: 7.23, change: 1.92, high24h: 7.45, low24h: 7.10, volume: 320000000, tool: 'rabbit' },
            LINKUSDT: { price: 14.56, change: 2.78, high24h: 14.9, low24h: 14.2, volume: 410000000, tool: 'rabbit' },
            MATICUSDT: { price: 0.7234, change: 1.56, high24h: 0.75, low24h: 0.71, volume: 280000000, tool: 'rabbit' },
            LTCUSDT: { price: 83.25, change: 1.34, high24h: 85.0, low24h: 82.0, volume: 350000000, tool: 'rabbit' },
            UNIUSDT: { price: 9.87, change: 2.45, high24h: 10.1, low24h: 9.65, volume: 180000000, tool: 'rabbit' },
            ATOMUSDT: { price: 8.92, change: 1.78, high24h: 9.15, low24h: 8.75, volume: 210000000, tool: 'rabbit' },
            // 主流币 (打兔子)
            ETCUSDT: { price: 26.45, change: 2.15, high24h: 27.0, low24h: 25.9, volume: 195000000, tool: 'rabbit' },
            XLMUSDT: { price: 0.1089, change: 1.23, high24h: 0.112, low24h: 0.107, volume: 92000000, tool: 'rabbit' },
            BCHUSDT: { price: 478.50, change: 2.67, high24h: 490, low24h: 470, volume: 280000000, tool: 'rabbit' },
            ALGOUSDT: { price: 0.1823, change: 1.45, high24h: 0.188, low24h: 0.179, volume: 78000000, tool: 'rabbit' },
            VETUSDT: { price: 0.0234, change: 1.89, high24h: 0.024, low24h: 0.023, volume: 65000000, tool: 'rabbit' },
            ICPUSDT: { price: 12.34, change: 3.21, high24h: 12.7, low24h: 12.0, volume: 145000000, tool: 'rabbit' },
            // Meme币/新币 (打地鼠 - 20%仓位)
            PEPEUSDT: { price: 0.00001234, change: 12.5, high24h: 0.000014, low24h: 0.000011, volume: 520000000, tool: 'mole' },
            SHIBUSDT: { price: 0.00002567, change: 8.3, high24h: 0.000028, low24h: 0.000024, volume: 380000000, tool: 'mole' },
            FLOKIUSDT: { price: 0.0001823, change: 15.2, high24h: 0.00020, low24h: 0.00017, volume: 250000000, tool: 'mole' }
        };
    },

    fetchSignals: function() {
        var self = this;
        // 模拟信号数据 - 打兔子覆盖前20主流币
        this.state.signals = [
            // 打兔子信号 (主流币)
            { id: 1, symbol: 'BTCUSDT', tool: 'rabbit', type: 'EMA金叉', confidence: 92, action: 'BUY', price: 75145.50, target: 78000, stop: 73500, time: new Date().toISOString() },
            { id: 2, symbol: 'ETHUSDT', tool: 'rabbit', type: 'MACD多头', confidence: 88, action: 'BUY', price: 3215.80, target: 3400, stop: 3100, time: new Date().toISOString() },
            { id: 3, symbol: 'BNBUSDT', tool: 'rabbit', type: '趋势确认', confidence: 85, action: 'BUY', price: 598.20, target: 630, stop: 580, time: new Date().toISOString() },
            { id: 4, symbol: 'SOLUSDT', tool: 'rabbit', type: 'RSI超买', confidence: 82, action: 'BUY', price: 178.45, target: 195, stop: 168, time: new Date().toISOString() },
            { id: 5, symbol: 'XRPUSDT', tool: 'rabbit', type: '成交量放大', confidence: 80, action: 'BUY', price: 0.5823, target: 0.62, stop: 0.55, time: new Date().toISOString() },
            { id: 6, symbol: 'ADAUSDT', tool: 'rabbit', type: '布林带中轨支撑', confidence: 78, action: 'BUY', price: 0.4521, target: 0.48, stop: 0.43, time: new Date().toISOString() },
            { id: 7, symbol: 'DOGEUSDT', tool: 'rabbit', type: 'Meme热潮', confidence: 75, action: 'BUY', price: 0.1256, target: 0.14, stop: 0.11, time: new Date().toISOString() },
            { id: 8, symbol: 'AVAXUSDT', tool: 'rabbit', type: '趋势跟踪', confidence: 82, action: 'BUY', price: 35.42, target: 38.5, stop: 33.0, time: new Date().toISOString() },
            { id: 9, symbol: 'LINKUSDT', tool: 'rabbit', type: 'AI板块联动', confidence: 79, action: 'BUY', price: 14.56, target: 15.5, stop: 13.8, time: new Date().toISOString() },
            { id: 10, symbol: 'DOTUSDT', tool: 'rabbit', type: '技术突破', confidence: 77, action: 'BUY', price: 7.23, target: 7.70, stop: 6.85, time: new Date().toISOString() },
            { id: 11, symbol: 'MATICUSDT', tool: 'rabbit', type: 'Polygon生态', confidence: 74, action: 'BUY', price: 0.7234, target: 0.78, stop: 0.68, time: new Date().toISOString() },
            { id: 12, symbol: 'LTCUSDT', tool: 'rabbit', type: '减半行情', confidence: 81, action: 'BUY', price: 83.25, target: 90.0, stop: 78.0, time: new Date().toISOString() },
            { id: 13, symbol: 'ATOMUSDT', tool: 'rabbit', type: 'Cosmos生态', confidence: 76, action: 'BUY', price: 8.92, target: 9.50, stop: 8.40, time: new Date().toISOString() },
            { id: 14, symbol: 'UNIUSDT', tool: 'rabbit', type: 'DeFi复苏', confidence: 73, action: 'BUY', price: 9.87, target: 10.50, stop: 9.30, time: new Date().toISOString() },
            { id: 15, symbol: 'ICPUSDT', tool: 'rabbit', type: 'AI叙事', confidence: 71, action: 'BUY', price: 12.34, target: 13.50, stop: 11.50, time: new Date().toISOString() },
            // 打地鼠信号 (Meme/新币)
            { id: 16, symbol: 'PEPEUSDT', tool: 'mole', type: 'Meme热潮', confidence: 68, action: 'BUY', price: 0.00001234, target: 0.000015, stop: 0.000010, time: new Date().toISOString() },
            { id: 17, symbol: 'SHIBUSDT', tool: 'mole', type: '社区热度', confidence: 65, action: 'BUY', price: 0.00002567, target: 0.000030, stop: 0.000020, time: new Date().toISOString() },
            { id: 18, symbol: 'FLOKIUSDT', tool: 'mole', type: 'Viral传播', confidence: 70, action: 'BUY', price: 0.0001823, target: 0.00022, stop: 0.00015, time: new Date().toISOString() }
        ];
    },

    startLiveUpdates: function() {
        var self = this;
        // 每3秒更新行情
        this.state.timers.price = setInterval(function() {
            self.updatePrices();
        }, 3000);

        // 检查止损止盈
        this.state.timers.risk = setInterval(function() {
            self.checkStopLossTakeProfit();
        }, 5000);
    },

    updatePrices: function() {
        var symbols = Object.keys(this.state.prices);
        var self = this;
        symbols.forEach(function(symbol) {
            var p = self.state.prices[symbol];
            var change = (Math.random() - 0.5) * 0.002; // ±0.1% 波动
            p.price = p.price * (1 + change);
            p.change = parseFloat((Math.random() * 6 - 1).toFixed(2));
        });

        // 检查是否有持仓需要更新
        if (self.state.mode === 'paper' || self.state.mode === 'live') {
            self.updatePositionValues();
        }

        // 重新渲染（仅更新价格）
        if (self.state.tab === 'simulation') {
            self.renderPriceGrid();
        }
    },

    // ========================
    // 风险管理
    // ========================
    checkStopLossTakeProfit: function() {
        var self = this;
        var toClose = [];

        this.state.positions.forEach(function(pos, idx) {
            var currentPrice = self.state.prices[pos.symbol] ? self.state.prices[pos.symbol].price : pos.entryPrice;
            var pnlPercent = (currentPrice - pos.entryPrice) / pos.entryPrice * 100;
            var pnl = pos.quantity * (currentPrice - pos.entryPrice);

            // 更新当前值
            pos.currentPrice = currentPrice;
            pos.unrealizedPnL = pnl;
            pos.unrealizedPnLPercent = pnlPercent;

            // 检查止损
            if (pnlPercent <= -self.state.config.stopLoss * 100) {
                pos.reason = 'STOP_LOSS';
                toClose.push(idx);
            }
            // 检查止盈
            else if (pnlPercent >= self.state.config.takeProfit * 100) {
                pos.reason = 'TAKE_PROFIT';
                toClose.push(idx);
            }
        });

        // 平仓
        toClose.forEach(function(idx) {
            self.closePosition(idx);
        });

        // 保存状态
        if (toClose.length > 0) {
            this.saveState();
            this.render();
        }
    },

    // ========================
    // 交易操作
    // ========================
    openPosition: function(symbol, quantity, direction, entryPrice) {
        var price = entryPrice || this.state.prices[symbol].price;
        var posValue = price * quantity;
        var commission = posValue * this.state.config.commission;

        var position = {
            id: Date.now(),
            symbol: symbol,
            direction: direction, // LONG / SHORT
            quantity: quantity,
            entryPrice: price,
            currentPrice: price,
            posValue: posValue,
            commission: commission,
            unrealizedPnL: 0,
            unrealizedPnLPercent: 0,
            stopLoss: price * (1 - this.state.config.stopLoss),
            takeProfit: price * (1 + this.state.config.takeProfit),
            openTime: new Date().toISOString(),
            tool: this.detectTool(symbol),
            reason: null
        };

        this.state.positions.push(position);
        this.saveState();
        this.render();
        this.showToast('📈 持仓已开: ' + symbol + ' x ' + quantity);

        return position;
    },

    closePosition: function(index) {
        var pos = this.state.positions[index];
        var currentPrice = this.state.prices[pos.symbol].price;
        var pnl = pos.direction === 'LONG'
            ? (currentPrice - pos.entryPrice) * pos.quantity
            : (pos.entryPrice - currentPrice) * pos.quantity;
        var commission = pos.posValue * this.state.config.commission;
        var netPnL = pnl - commission * 2; // 开仓+平仓手续费

        // 记录交易
        var trade = {
            id: Date.now(),
            symbol: pos.symbol,
            direction: pos.direction,
            quantity: pos.quantity,
            entryPrice: pos.entryPrice,
            exitPrice: currentPrice,
            pnl: netPnL,
            pnlPercent: (netPnL / pos.posValue) * 100,
            commission: commission * 2,
            holdingTime: this.formatHoldingTime(new Date(pos.openTime), new Date()),
            openTime: pos.openTime,
            closeTime: new Date().toISOString(),
            tool: pos.tool,
            reason: pos.reason || 'MANUAL'
        };

        this.state.trades.push(trade);
        this.state.positions.splice(index, 1);

        // 更新资金
        this.state.config.currentCapital += netPnL;

        // 重新计算结果
        this.recalculateResults();
        this.saveState();
        this.render();

        this.showToast((netPnL >= 0 ? '✅ ' : '❌ ') + pos.symbol + ' 平仓: ' + (netPnL >= 0 ? '+' : '') + netPnL.toFixed(2) + ' (' + pos.reason + ')');
    },

    closeAllPositions: function() {
        while (this.state.positions.length > 0) {
            this.closePosition(0);
        }
    },

    // ========================
    // 头寸更新
    // ========================
    updatePositionValues: function() {
        var self = this;
        this.state.positions.forEach(function(pos) {
            var currentPrice = self.state.prices[pos.symbol].price;
            pos.currentPrice = currentPrice;
            var pnl = pos.direction === 'LONG'
                ? (currentPrice - pos.entryPrice) * pos.quantity
                : (pos.entryPrice - currentPrice) * pos.quantity;
            pos.unrealizedPnL = pnl;
            pos.unrealizedPnLPercent = (pnl / pos.posValue) * 100;
        });
    },

    // ========================
    // 结果计算
    // ========================
    recalculateResults: function() {
        var trades = this.state.trades;
        if (trades.length === 0) {
            this.state.results = {
                totalTrades: 0, winningTrades: 0, losingTrades: 0,
                winRate: 0, totalPnL: 0, totalPnLPercent: 0,
                maxDrawdown: 0, sharpeRatio: 0,
                avgWin: 0, avgLoss: 0, profitFactor: 0, avgHoldingTime: 0
            };
            return;
        }

        var wins = trades.filter(function(t) { return t.pnl > 0; });
        var losses = trades.filter(function(t) { return t.pnl <= 0; });
        var totalPnL = trades.reduce(function(s, t) { return s + t.pnl; }, 0);

        // 计算最大回撤
        var peak = this.state.config.initialCapital;
        var maxDrawdown = 0;
        var capital = this.state.config.initialCapital;
        trades.forEach(function(t) {
            capital += t.pnl;
            if (capital > peak) peak = capital;
            var dd = (peak - capital) / peak * 100;
            if (dd > maxDrawdown) maxDrawdown = dd;
        });

        // 计算盈利/亏损比
        var avgWin = wins.length > 0 ? wins.reduce(function(s, t) { return s + t.pnl; }, 0) / wins.length : 0;
        var avgLoss = losses.length > 0 ? Math.abs(losses.reduce(function(s, t) { return s + t.pnl; }, 0) / losses.length) : 0;

        this.state.results = {
            totalTrades: trades.length,
            winningTrades: wins.length,
            losingTrades: losses.length,
            winRate: (wins.length / trades.length * 100).toFixed(1),
            totalPnL: totalPnL,
            totalPnLPercent: (totalPnL / this.state.config.initialCapital * 100).toFixed(2),
            maxDrawdown: maxDrawdown.toFixed(2),
            sharpeRatio: this.calculateSharpeRatio(trades),
            avgWin: avgWin.toFixed(2),
            avgLoss: avgLoss.toFixed(2),
            profitFactor: avgLoss > 0 ? (avgWin / avgLoss).toFixed(2) : '∞',
            avgHoldingTime: this.calculateAvgHoldingTime(trades)
        };
    },

    calculateSharpeRatio: function(trades) {
        if (trades.length < 2) return 0;
        var returns = trades.map(function(t) { return t.pnlPercent / 100; });
        var avg = returns.reduce(function(s, r) { return s + r; }, 0) / returns.length;
        var variance = returns.reduce(function(s, r) { return s + Math.pow(r - avg, 2); }, 0) / returns.length;
        var stdDev = Math.sqrt(variance);
        return stdDev > 0 ? (avg / stdDev * Math.sqrt(252)).toFixed(2) : 0;
    },

    calculateAvgHoldingTime: function(trades) {
        if (trades.length === 0) return '0h';
        var totalMs = trades.reduce(function(s, t) {
            return s + (new Date(t.closeTime) - new Date(t.openTime));
        }, 0);
        return this.formatHoldingTime(new Date(0), new Date(totalMs));
    },

    formatHoldingTime: function(start, end) {
        var ms = end - start;
        var hours = Math.floor(ms / 3600000);
        var mins = Math.floor((ms % 3600000) / 60000);
        if (hours > 24) {
            var days = Math.floor(hours / 24);
            return days + 'd ' + (hours % 24) + 'h';
        }
        return hours + 'h ' + mins + 'm';
    },

    // ========================
    // 工具检测
    // ========================
    detectTool: function(symbol) {
        // 根据symbol特征检测工具
        // 打兔子: 前20主流加密货币
        var rabbitCoins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'LINK', 'MATIC', 'LTC', 'UNI', 'ATOM', 'ETC', 'XLM', 'BCH', 'ALGO', 'VET', 'ICP'];
        // 打地鼠: Meme币/新币
        var moleCoins = ['PEPE', 'SHIB', 'FLOKI', 'BONK', 'WIF', 'MAGA'];
        // 走着瞧: 预测市场
        var oracleCoins = ['BTC', 'ETH'];

        for (var i = 0; i < rabbitCoins.length; i++) {
            if (symbol.indexOf(rabbitCoins[i]) !== -1) return 'rabbit';
        }
        for (var i = 0; i < moleCoins.length; i++) {
            if (symbol.indexOf(moleCoins[i]) !== -1) return 'mole';
        }
        return 'rabbit';
    },

    // ========================
    // 回测功能
    // ========================
    runBacktest: function() {
        var config = this.state.backtest;
        var self = this;

        this.showToast('🔄 回测运行中...');

        // 模拟回测过程
        setTimeout(function() {
            var results = self.generateBacktestResults(config);
            self.displayBacktestResults(results);
        }, 1500);
    },

    generateBacktestResults: function(config) {
        var results = [];
        var symbols = config.symbols || ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'];

        symbols.forEach(function(symbol) {
            var trades = Math.floor(Math.random() * 50 + 20);
            var wins = Math.floor(trades * (0.4 + Math.random() * 0.3));
            var totalWin = 0, totalLoss = 0;

            for (var i = 0; i < wins; i++) {
                totalWin += Math.random() * 500 + 100;
            }
            for (var i = 0; i < trades - wins; i++) {
                totalLoss += Math.random() * 300 + 50;
            }

            var pnl = totalWin - totalLoss;
            var winRate = (wins / trades * 100).toFixed(1);

            results.push({
                symbol: symbol,
                trades: trades,
                winRate: winRate,
                pnl: pnl.toFixed(2),
                pnlPercent: (pnl / 10000 * 100).toFixed(2),
                maxDD: (Math.random() * 15 + 5).toFixed(1),
                sharpe: (Math.random() * 1.5 + 0.5).toFixed(2)
            });
        });

        return results;
    },

    displayBacktestResults: function(results) {
        var html = '<div class="backtest-results">';
        html += '<h3>📊 回测结果</h3>';
        html += '<table class="backtest-table">';
        html += '<thead><tr><th>交易对</th><th>交易次数</th><th>胜率</th><th>收益</th><th>收益率</th><th>最大回撤</th><th>夏普比率</th></tr></thead>';
        html += '<tbody>';

        results.forEach(function(r) {
            html += '<tr>';
            html += '<td>' + r.symbol + '</td>';
            html += '<td>' + r.trades + '</td>';
            html += '<td class="' + (parseFloat(r.winRate) > 50 ? 'positive' : 'negative') + '">' + r.winRate + '%</td>';
            html += '<td class="' + (parseFloat(r.pnl) > 0 ? 'positive' : 'negative') + '">$' + r.pnl + '</td>';
            html += '<td class="' + (parseFloat(r.pnlPercent) > 0 ? 'positive' : 'negative') + '">' + r.pnlPercent + '%</td>';
            html += '<td class="negative">' + r.maxDD + '%</td>';
            html += '<td>' + r.sharpe + '</td>';
            html += '</tr>';
        });

        html += '</tbody></table>';
        html += '<button class="btn-primary" onclick="TradingSimV2.setMode(\'overview\')">返回总览</button>';
        html += '</div>';

        document.getElementById('simContent').innerHTML = html;
    },

    // ========================
    // 信号执行
    // ========================
    executeSignal: function(signalId) {
        var signal = this.state.signals.find(function(s) { return s.id === signalId; });
        if (!signal) return;

        var self = this;
        var quantity = this.calculatePositionSize(signal.price);

        if (signal.action === 'BUY') {
            this.openPosition(signal.symbol, quantity, 'LONG', signal.price);
        } else {
            this.openPosition(signal.symbol, quantity, 'SHORT', signal.price);
        }
    },

    calculatePositionSize: function(price) {
        var capital = this.state.config.currentCapital;
        var riskAmount = capital * this.state.config.riskPerTrade;
        var stopDistance = this.state.config.stopLoss;
        return Math.floor((riskAmount / stopDistance) / price * 10000) / 10000;
    },

    // ========================
    // 渲染
    // ========================
    render: function() {
        var html = this.getHeader();
        html += this.getTabBar();

        switch (this.state.tab) {
            case 'simulation':
                html += this.getSimulationPanel();
                break;
            case 'signals':
                html += this.getSignalsPanel();
                break;
            case 'portfolio':
                html += this.getPortfolioPanel();
                break;
        }

        document.getElementById('simContent').innerHTML = html;
        this.renderPriceGrid();
    },

    getHeader: function() {
        return '<div class="sim-header">' +
            '<h2>🔮 交易仿真</h2>' +
            '<div class="mode-switcher">' +
            '<button class="' + (this.state.mode === 'overview' ? 'active' : '') + '" onclick="TradingSimV2.setMode(\'overview\')">总览</button>' +
            '<button class="' + (this.state.mode === 'backtest' ? 'active' : '') + '" onclick="TradingSimV2.setMode(\'backtest\')">回测</button>' +
            '<button class="' + (this.state.mode === 'paper' ? 'active' : '') + '" onclick="TradingSimV2.setMode(\'paper\')">Paper</button>' +
            '<button class="' + (this.state.mode === 'history' ? 'active' : '') + '" onclick="TradingSimV2.setMode(\'history\')">历史</button>' +
            '<button class="' + (this.state.mode === 'settings' ? 'active' : '') + '" onclick="TradingSimV2.setMode(\'settings\')">设置</button>' +
            '</div>' +
            '</div>';
    },

    getTabBar: function() {
        return '<div class="sim-tabs">' +
            '<button class="' + (this.state.tab === 'simulation' ? 'active' : '') + '" onclick="TradingSimV2.setTab(\'simulation\')">📊 仿真</button>' +
            '<button class="' + (this.state.tab === 'signals' ? 'active' : '') + '" onclick="TradingSimV2.setTab(\'signals\')">📡 信号</button>' +
            '<button class="' + (this.state.tab === 'portfolio' ? 'active' : '') + '" onclick="TradingSimV2.setTab(\'portfolio\')">💼 持仓</button>' +
            '</div>';
    },

    getSimulationPanel: function() {
        var r = this.state.results;
        var c = this.state.config;

        return '<div class="sim-panel">' +
            // 资金卡片
            '<div class="capital-cards">' +
            '<div class="capital-card">' +
            '<div class="label">初始资金</div>' +
            '<div class="value">$ ' + c.initialCapital.toLocaleString() + '</div>' +
            '</div>' +
            '<div class="capital-card ' + (c.currentCapital >= c.initialCapital ? 'positive' : 'negative') + '">' +
            '<div class="label">当前资金</div>' +
            '<div class="value">$ ' + c.currentCapital.toLocaleString() + '</div>' +
            '</div>' +
            '<div class="capital-card ' + (r.totalPnL >= 0 ? 'positive' : 'negative') + '">' +
            '<div class="label">总收益</div>' +
            '<div class="value">' + (r.totalPnL >= 0 ? '+' : '') + '$ ' + r.totalPnL.toFixed(2) + '</div>' +
            '</div>' +
            '<div class="capital-card ' + (r.totalPnLPercent >= 0 ? 'positive' : 'negative') + '">' +
            '<div class="label">收益率</div>' +
            '<div class="value">' + (r.totalPnLPercent >= 0 ? '+' : '') + r.totalPnLPercent + '%</div>' +
            '</div>' +
            '</div>' +

            // 统计数据
            '<div class="stats-grid">' +
            '<div class="stat-card"><div class="stat-label">交易次数</div><div class="stat-value">' + r.totalTrades + '</div></div>' +
            '<div class="stat-card"><div class="stat-label">胜率</div><div class="stat-value ' + (r.winRate >= 50 ? 'positive' : 'negative') + '">' + r.winRate + '%</div></div>' +
            '<div class="stat-card"><div class="stat-label">盈利次数</div><div class="stat-value positive">' + r.winningTrades + '</div></div>' +
            '<div class="stat-card"><div class="stat-label">亏损次数</div><div class="stat-value negative">' + r.losingTrades + '</div></div>' +
            '<div class="stat-card"><div class="stat-label">最大回撤</div><div class="stat-value negative">' + r.maxDrawdown + '%</div></div>' +
            '<div class="stat-card"><div class="stat-label">夏普比率</div><div class="stat-value">' + r.sharpeRatio + '</div></div>' +
            '<div class="stat-card"><div class="stat-label">盈亏比</div><div class="stat-value">' + r.profitFactor + '</div></div>' +
            '<div class="stat-card"><div class="stat-label">平均持仓</div><div class="stat-value">' + r.avgHoldingTime + '</div></div>' +
            '</div>' +

            // 行情表格
            '<div class="price-section">' +
            '<h3>实时行情</h3>' +
            '<div id="priceGrid" class="price-grid"></div>' +
            '</div>' +
            '</div>';
    },

    renderPriceGrid: function() {
        var html = '<table class="price-table"><thead><tr><th>交易对</th><th>价格</th><th>24h涨跌</th><th>操作</th></tr></thead><tbody>';

        var self = this;
        Object.keys(this.state.prices).forEach(function(symbol) {
            var p = self.state.prices[symbol];
            var hasPosition = self.state.positions.some(function(pos) { return pos.symbol === symbol; });
            var priceStr = symbol.indexOf('USDT') !== -1 && symbol !== 'USDT' ? p.price.toFixed(2) : p.price.toFixed(6);

            html += '<tr>' +
                '<td><strong>' + symbol.replace('USDT', '') + '</strong>/USDT</td>' +
                '<td class="price">$' + priceStr + '</td>' +
                '<td class="' + (p.change >= 0 ? 'positive' : 'negative') + '">' + (p.change >= 0 ? '+' : '') + p.change.toFixed(2) + '%</td>' +
                '<td>';

            if (!hasPosition) {
                html += '<button class="btn-sm btn-buy" onclick="TradingSimV2.quickBuy(\'' + symbol + '\')">买入</button> ';
                html += '<button class="btn-sm btn-sell" onclick="TradingSimV2.quickSell(\'' + symbol + '\')">卖出</button>';
            } else {
                html += '<span class="badge">已持仓</span>';
            }

            html += '</td></tr>';
        });

        html += '</tbody></table>';
        var el = document.getElementById('priceGrid');
        if (el) el.innerHTML = html;
    },

    quickBuy: function(symbol) {
        var price = this.state.prices[symbol].price;
        var quantity = this.calculatePositionSize(price);
        this.openPosition(symbol, quantity, 'LONG', price);
    },

    quickSell: function(symbol) {
        var price = this.state.prices[symbol].price;
        var quantity = this.calculatePositionSize(price);
        this.openPosition(symbol, quantity, 'SHORT', price);
    },

    getSignalsPanel: function() {
        var html = '<div class="signals-panel"><h3>📡 AI交易信号</h3>';

        this.state.signals.forEach(function(sig) {
            html += '<div class="signal-card ' + sig.action.toLowerCase() + '">' +
                '<div class="signal-header">' +
                '<span class="signal-symbol">' + sig.symbol.replace('USDT', '') + '</span>' +
                '<span class="signal-action ' + sig.action.toLowerCase() + '">' + sig.action + '</span>' +
                '<span class="signal-confidence">' + sig.confidence + '%</span>' +
                '</div>' +
                '<div class="signal-detail">' +
                '<span class="signal-type">' + sig.tool + ': ' + sig.type + '</span>' +
                '</div>' +
                '<div class="signal-prices">' +
                '<span>现价: $' + sig.price.toFixed(2) + '</span>' +
                '<span>目标: $' + sig.target.toFixed(2) + '</span>' +
                '<span>止损: $' + sig.stop.toFixed(2) + '</span>' +
                '</div>' +
                '<button class="btn-primary" onclick="TradingSimV2.executeSignal(' + sig.id + ')">执行信号</button>' +
                '</div>';
        });

        html += '</div>';
        return html;
    },

    getPortfolioPanel: function() {
        var html = '<div class="portfolio-panel"><h3>💼 持仓 & 历史</h3>';

        // 持仓
        html += '<div class="positions-section">';
        html += '<h4>当前持仓 (' + this.state.positions.length + ')</h4>';

        if (this.state.positions.length === 0) {
            html += '<div class="empty-state">暂无持仓</div>';
        } else {
            html += '<table class="positions-table"><thead><tr><th>交易对</th><th>方向</th><th>数量</th><th>入场价</th><th>当前价</th><th>浮盈</th><th>操作</th></tr></thead><tbody>';

            this.state.positions.forEach(function(pos, idx) {
                html += '<tr>' +
                    '<td>' + pos.symbol.replace('USDT', '') + '</td>' +
                    '<td class="' + pos.direction.toLowerCase() + '">' + pos.direction + '</td>' +
                    '<td>' + pos.quantity.toFixed(4) + '</td>' +
                    '<td>$' + pos.entryPrice.toFixed(2) + '</td>' +
                    '<td>$' + pos.currentPrice.toFixed(2) + '</td>' +
                    '<td class="' + (pos.unrealizedPnL >= 0 ? 'positive' : 'negative') + '">' +
                    (pos.unrealizedPnL >= 0 ? '+' : '') + '$' + pos.unrealizedPnL.toFixed(2) +
                    ' (' + pos.unrealizedPnLPercent.toFixed(2) + '%)' +
                    '</td>' +
                    '<td><button class="btn-sm btn-close" onclick="TradingSimV2.closePosition(' + idx + ')">平仓</button></td>' +
                    '</tr>';
            });

            html += '</tbody></table>';
        }

        html += '</div>';

        // 历史交易
        html += '<div class="history-section">';
        html += '<h4>历史交易 (' + this.state.trades.length + ')</h4>';

        if (this.state.trades.length === 0) {
            html += '<div class="empty-state">暂无交易记录</div>';
        } else {
            var recentTrades = this.state.trades.slice(-10).reverse();
            html += '<table class="history-table"><thead><tr><th>时间</th><th>交易对</th><th>方向</th><th>数量</th><th>入场</th><th>出场</th><th>盈亏</th><th>原因</th></tr></thead><tbody>';

            recentTrades.forEach(function(t) {
                var time = new Date(t.closeTime).toLocaleString();
                html += '<tr>' +
                    '<td>' + time + '</td>' +
                    '<td>' + t.symbol.replace('USDT', '') + '</td>' +
                    '<td class="' + t.direction.toLowerCase() + '">' + t.direction + '</td>' +
                    '<td>' + t.quantity.toFixed(4) + '</td>' +
                    '<td>$' + t.entryPrice.toFixed(2) + '</td>' +
                    '<td>$' + t.exitPrice.toFixed(2) + '</td>' +
                    '<td class="' + (t.pnl >= 0 ? 'positive' : 'negative') + '">' +
                    (t.pnl >= 0 ? '+' : '') + '$' + t.pnl.toFixed(2) + '</td>' +
                    '<td>' + t.reason + '</td>' +
                    '</tr>';
            });

            html += '</tbody></table>';
        }

        html += '</div></div>';
        return html;
    },

    // ========================
    // Toast 提示
    // ========================
    showToast: function(message) {
        var toast = document.getElementById('simToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'simToast';
            toast.className = 'sim-toast';
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.className = 'sim-toast show';
        setTimeout(function() {
            toast.className = 'sim-toast';
        }, 3000);
    },

    // ========================
    // 销毁
    // ========================
    destroy: function() {
        Object.keys(this.state.timers).forEach(function(key) {
            clearInterval(this.state.timers[key]);
        }.bind(this));
    }
};

// 自动初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { TradingSimV2.init(); });
} else {
    TradingSimV2.init();
}
