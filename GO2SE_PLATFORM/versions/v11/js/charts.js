/* GO2SE Platform v11 - Chart.js Configurations and Wrappers */

// Global Chart.js defaults
Chart.defaults.color = '#b0b0c0';
Chart.defaults.borderColor = '#2a2a3a';
Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

// ========== Chart Factory ==========
const ChartFactory = {
    instances: {},
    
    // Line Chart
    createLine(canvasId, labels, datasets, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: options.legend !== undefined ? options.legend : true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 30, 42, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#b0b0c0',
                    borderColor: '#3a3a4a',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(42, 42, 58, 0.5)',
                        drawBorder: false
                    },
                    ticks: {
                        maxRotation: 0
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(42, 42, 58, 0.5)',
                        drawBorder: false
                    },
                    beginAtZero: options.beginAtZero || false
                }
            }
        };
        
        const config = {
            type: 'line',
            data: {
                labels,
                datasets: datasets.map(ds => ({
                    label: ds.label,
                    data: ds.data,
                    borderColor: ds.color || '#00d4ff',
                    backgroundColor: ds.fill ? this.createGradient(ctx, ds.color || '#00d4ff') : 'transparent',
                    fill: ds.fill || false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: ds.color || '#00d4ff',
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 2,
                    borderWidth: options.lineWidth || 2
                }))
            },
            options: { ...defaultOptions, ...options }
        };
        
        this.instances[canvasId] = new Chart(ctx, config);
        return this.instances[canvasId];
    },
    
    // Bar Chart
    createBar(canvasId, labels, datasets, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: options.legend !== undefined ? options.legend : false
                }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    grid: {
                        color: 'rgba(42, 42, 58, 0.5)',
                        drawBorder: false
                    }
                }
            }
        };
        
        const config = {
            type: 'bar',
            data: {
                labels,
                datasets: datasets.map(ds => ({
                    label: ds.label,
                    data: ds.data,
                    backgroundColor: ds.color || '#00d4ff',
                    borderRadius: 4,
                    barThickness: options.barThickness || 20
                }))
            },
            options: { ...defaultOptions, ...options }
        };
        
        this.instances[canvasId] = new Chart(ctx, config);
        return this.instances[canvasId];
    },
    
    // Doughnut Chart
    createDoughnut(canvasId, labels, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    display: options.legend !== undefined ? options.legend : true,
                    position: 'right'
                }
            }
        };
        
        const config = {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: options.colors || [
                        '#00d4ff', '#7c3aed', '#10b981', '#f59e0b', '#ef4444'
                    ],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: { ...defaultOptions, ...options }
        };
        
        this.instances[canvasId] = new Chart(ctx, config);
        return this.instances[canvasId];
    },
    
    // Pie Chart
    createPie(canvasId, labels, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const config = {
            type: 'pie',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: options.colors || [
                        '#00d4ff', '#7c3aed', '#10b981', '#f59e0b', '#ef4444'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        };
        
        this.instances[canvasId] = new Chart(ctx, config);
        return this.instances[canvasId];
    },
    
    // Radar Chart
    createRadar(canvasId, labels, datasets, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const config = {
            type: 'radar',
            data: {
                labels,
                datasets: datasets.map((ds, i) => ({
                    label: ds.label,
                    data: ds.data,
                    borderColor: ds.color || '#00d4ff',
                    backgroundColor: this.createGradientRadar(ctx, ds.color || '#00d4ff'),
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: '#1e1e2a'
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(42, 42, 58, 0.5)'
                        },
                        angleLines: {
                            color: 'rgba(42, 42, 58, 0.5)'
                        },
                        pointLabels: {
                            color: '#b0b0c0'
                        }
                    }
                }
            }
        };
        
        this.instances[canvasId] = new Chart(ctx, config);
        return this.instances[canvasId];
    },
    
    // Area Chart (Line with fill)
    createArea(canvasId, labels, datasets, options = {}) {
        return this.createLine(canvasId, labels, datasets.map(ds => ({
            ...ds,
            fill: true
        })), options);
    },
    
    // Candlestick Chart (simulated with bar chart)
    createCandlestick(canvasId, candles, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
        }
        
        const config = {
            type: 'bar',
            data: {
                labels: candles.map(c => c.time),
                datasets: [
                    {
                        label: 'Open',
                        data: candles.map(c => c.open),
                        backgroundColor: 'transparent',
                        borderColor: 'transparent'
                    },
                    {
                        label: 'High',
                        data: candles.map(c => c.high),
                        backgroundColor: '#10b981',
                        barThickness: 1
                    },
                    {
                        label: 'Low',
                        data: candles.map(c => c.low),
                        backgroundColor: '#ef4444',
                        barThickness: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        };
        
        // Note: For real candlestick, use a library like lightweight-charts
        this.instances[canvasId] = new Chart(ctx, config);
        return this.instances[canvasId];
    },
    
    // Helper: Create gradient for fill
    createGradient(ctx, color) {
        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, ctx.height);
        gradient.addColorStop(0, color + '40');
        gradient.addColorStop(1, color + '00');
        return gradient;
    },
    
    // Helper: Create radar gradient
    createGradientRadar(ctx, color) {
        const gradient = ctx.getContext('2d').createRadialGradient(
            ctx.width / 2, ctx.height / 2, 0,
            ctx.width / 2, ctx.height / 2, ctx.width / 2
        );
        gradient.addColorStop(0, color + '60');
        gradient.addColorStop(1, color + '10');
        return gradient;
    },
    
    // Update existing chart
    update(canvasId, newData) {
        const chart = this.instances[canvasId];
        if (!chart) return;
        
        if (newData.labels) {
            chart.data.labels = newData.labels;
        }
        if (newData.datasets) {
            newData.datasets.forEach((ds, i) => {
                if (chart.data.datasets[i]) {
                    chart.data.datasets[i].data = ds.data;
                }
            });
        }
        chart.update();
    },
    
    // Destroy chart
    destroy(canvasId) {
        if (this.instances[canvasId]) {
            this.instances[canvasId].destroy();
            delete this.instances[canvasId];
        }
    },
    
    // Destroy all charts
    destroyAll() {
        Object.keys(this.instances).forEach(id => this.destroy(id));
    }
};

// ========== Chart Presets ==========
const ChartPresets = {
    // Portfolio Performance Chart
    portfolioPerformance(labels, data) {
        return ChartFactory.createArea('portfolio-chart', labels, [
            { label: '总资产', data, color: '#00d4ff' }
        ], { beginAtZero: false });
    },
    
    // Allocation Chart
    allocation(labels, data) {
        return ChartFactory.createDoughnut('allocation-chart', labels, data, {
            colors: ['#00d4ff', '#7c3aed', '#10b981', '#f59e0b', '#ef4444', '#06b6d4']
        });
    },
    
    // Signal Strength Chart
    signalStrength(labels, buyData, sellData) {
        return ChartFactory.createBar('signal-chart', labels, [
            { label: '买入信号', data: buyData, color: '#10b981' },
            { label: '卖出信号', data: sellData, color: '#ef4444' }
        ], { legend: true });
    },
    
    // Price Line Chart
    priceLine(labels, priceData, volumeData) {
        return ChartFactory.createLine('price-chart', labels, [
            { label: '价格', data: priceData, color: '#00d4ff' },
            { label: '成交量', data: volumeData, color: '#7c3aed', fill: true }
        ], { beginAtZero: false });
    },
    
    // Asset Allocation
    assetAllocation() {
        return ChartFactory.createDoughnut('asset-allocation-chart', 
            ['USDT', 'BTC', 'ETH', 'BNB', '其他'],
            [35, 25, 20, 12, 8]
        );
    },
    
    // P&L Waterfall
    pnlWaterfall(labels, data) {
        return ChartFactory.createBar('pnl-chart', labels, [
            { label: '盈亏', data, color: (ctx) => ctx.raw >= 0 ? '#10b981' : '#ef4444' }
        ]);
    }
};

// ========== Signal Chart ==========
const SignalChart = {
    init(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        
        // Simulated signal data
        const signals = [];
        for (let i = 0; i < 30; i++) {
            signals.push({
                time: `T${i}`,
                strength: Math.random() * 100,
                type: Math.random() > 0.5 ? 'buy' : 'sell'
            });
        }
        
        return ChartFactory.createLine(canvasId, 
            signals.map(s => s.time),
            [{
                label: '信号强度',
                data: signals.map(s => s.strength),
                color: '#00d4ff',
                fill: true
            }]
        );
    }
};

// ========== Equity Curve ==========
const EquityCurve = {
    init(canvasId, data = []) {
        if (!data.length) {
            // Generate sample data
            let value = 10000;
            data = [];
            for (let i = 0; i < 90; i++) {
                value *= (1 + (Math.random() - 0.45) * 0.02);
                data.push(value);
            }
        }
        
        const labels = data.map((_, i) => `Day ${i + 1}`);
        
        return ChartFactory.createArea(canvasId, labels, [
            { label: '资金曲线', data, color: '#10b981' }
        ], { beginAtZero: false });
    }
};

// ========== Risk Metrics Radar ==========
const RiskMetricsRadar = {
    init(canvasId) {
        const labels = ['收益率', '波动率', '流动性', '杠杆率', '相关性', '夏普比率'];
        
        return ChartFactory.createRadar(canvasId, labels, [
            { label: '当前', data: [75, 60, 85, 40, 55, 70], color: '#00d4ff' },
            { label: '目标', data: [80, 50, 90, 30, 60, 85], color: '#7c3aed' }
        ]);
    }
};

// Export
window.ChartFactory = ChartFactory;
window.ChartPresets = ChartPresets;
window.SignalChart = SignalChart;
window.EquityCurve = EquityCurve;
window.RiskMetricsRadar = RiskMetricsRadar;
