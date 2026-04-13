// Module Fix: Safe module access wrapper
(function() {
    'use strict';
    
    // Global safe call wrapper
    window.safeModuleCall = function(moduleName, method, arg) {
        var module = window[moduleName];
        if (module && typeof module[method] === 'function') {
            return module[method](arg);
        }
        console.warn('⚠️ Module not ready:', moduleName, '.', method);
        return false;
    };
    
    // Override inline onclick handlers after DOM is ready
    function patchInlineHandlers() {
        var elements = document.querySelectorAll('[onclick]');
        elements.forEach(function(el) {
            var onclick = el.getAttribute('onclick');
            if (!onclick) return;
            
            // Check if this is a module call
            var moduleMatch = onclick.match(/^(MacroMicro|TradingPanel|TradingModules|SevenTools|SecurityModule|WalletDeconstruct|EngineerModule|CustomizeModule|SettingsModule)\./);
            if (moduleMatch) {
                var moduleName = moduleMatch[1];
                var originalHandler = onclick;
                
                el.setAttribute('data-module-call', originalHandler);
                el.removeAttribute('onclick');
                
                el.addEventListener('click', function(e) {
                    if (typeof window[moduleName] === 'undefined') {
                        console.warn('⚠️ Waiting for module:', moduleName);
                        e.preventDefault();
                        return false;
                    }
                    // Module is ready, execute original handler
                    try {
                        eval(originalHandler);
                    } catch(err) {
                        console.error('❌ Handler error:', err.message);
                    }
                });
                
                console.log('✅ Patched handler for', moduleName);
            }
        });
    }
    
    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', patchInlineHandlers);
    } else {
        patchInlineHandlers();
    }
    
    console.log('🔧 Module safety wrapper loaded');
})();
