// GO2SE v11 - Pages Index Module
// Central page registry and loader

const Pages = {
    // Dashboard page
    dashboard: () => DashboardPage.template(),
    
    // Signals page
    signals: () => SignalsPage.template(),
    'signals-detail': () => '<div class="page-content"><h1>信号详情</h1><p>开发中...</p></div>',
    
    // Portfolio page
    portfolio: () => PortfolioPage.template(),
    'portfolio-history': () => '<div class="page-content"><h1>历史记录</h1><p>开发中...</p></div>',
    
    // Assets page
    assets: () => AssetPage.template(),
    'assets-detail': () => '<div class="page-content"><h1>资产详情</h1><p>开发中...</p></div>',
    
    // Wallet page
    wallet: () => WalletPage.template(),
    'wallet-transfer': () => WalletPage.template(),
    
    // Settings page
    settings: () => SettingsPage.template(),
    'settings-api': () => SettingsPage.template(),
    
    // Help page
    help: () => '<div class="page-content"><h1>帮助中心</h1><p>开发中...</p></div>',
    
    // Default / loading
    loading: () => '<div class="loading-spinner"><div class="spinner"></div></div>'
};

// Page initialization registry
Pages.init = function(template) {
    switch(template) {
        case 'dashboard':
            DashboardPage.load();
            break;
        case 'signals':
        case 'signals-detail':
            SignalsPage.load();
            break;
        case 'portfolio':
        case 'portfolio-history':
            PortfolioPage.load();
            break;
        case 'assets':
        case 'assets-detail':
            if (typeof AssetPage.init === 'function') {
                AssetPage.init();
            }
            break;
        case 'wallet':
        case 'wallet-transfer':
            WalletPage.load();
            break;
        case 'settings':
        case 'settings-api':
            SettingsPage.load();
            break;
        default:
            console.log('No init handler for:', template);
    }
};

// Export for module use
window.Pages = Pages;
