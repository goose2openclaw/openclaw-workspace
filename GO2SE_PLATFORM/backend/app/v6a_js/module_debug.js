// Debug module interaction - load after all modules
(function() {
    'use strict';
    
    window.debugModule = function(moduleName) {
        var module = window[moduleName];
        console.log('=== Module Debug:', moduleName, '===');
        console.log('  Type:', typeof module);
        console.log('  Has navigateLevel:', typeof module?.navigateLevel);
        console.log('  Has renderPanel:', typeof module?.renderPanel);
        console.log('  Has init:', typeof module?.init);
        console.log('  State:', module?.state);
        
        // Check container
        var containerId = moduleName.replace('Panel', '').toLowerCase() + 'PanelContainer';
        if (moduleName === 'MacroMicro') containerId = 'macroMicroPanelContainer';
        if (moduleName === 'TradingPanel' || moduleName === 'TradingModules') containerId = 'tradingPanelContainer';
        if (moduleName === 'WalletDeconstruct') containerId = 'walletDeconstructContainer';
        
        var container = document.getElementById(containerId);
        console.log('  Container:', containerId, container ? 'EXISTS' : 'MISSING');
        
        // Try to call navigateLevel(1)
        if (typeof module?.navigateLevel === 'function') {
            console.log('  Calling navigateLevel(1)...');
            module.navigateLevel(1);
        }
        
        return false;
    };
    
    // Auto-test after DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            console.log('=== Module Debug Ready ===');
            console.log('Call debugModule("MacroMicro") to test');
        }, 500);
    });
})();
