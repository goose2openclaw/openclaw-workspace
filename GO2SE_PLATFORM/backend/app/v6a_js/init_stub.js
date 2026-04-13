// CRITICAL: This must run BEFORE HTML parsing continues
// It creates stub functions that will be replaced when real modules load
(function() {
    'use strict';
    
    // Create stub functions for ALL modules
    var stubModules = ['MacroMicro', 'TradingPanel', 'TradingModules', 'SevenTools', 
                      'SecurityModule', 'WalletDeconstruct', 'EngineerModule', 
                      'CustomizeModule', 'SettingsModule'];
    
    stubModules.forEach(function(name) {
        // Create a stub that logs when called
        window[name] = {
            navigateLevel: function(lvl) {
                console.log('[STUB]', name, '.navigateLevel(', lvl, ') called - waiting for real module');
                // Retry after a short delay in case module just loaded
                setTimeout(function() {
                    if (window[name] && window[name]._real) {
                        window[name]._real.navigateLevel(lvl);
                    }
                }, 100);
            },
            init: function() { console.log('[STUB]', name, '.init called'); },
            closePanel: function() { console.log('[STUB]', name, '.closePanel called'); },
            renderPanel: function() { console.log('[STUB]', name, '.renderPanel called'); },
            _stub: true
        };
    });
    
    console.log('🔧 Module stubs created:', stubModules.join(', '));
    window._moduleStubs = {};
    
})();
