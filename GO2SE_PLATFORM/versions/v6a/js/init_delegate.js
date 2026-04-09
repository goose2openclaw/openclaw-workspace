// Event Delegation - Handles data-module attributes
// This MUST load LAST after all modules are defined
(function() {
    'use strict';
    
    function handleModuleClick(e) {
        // Find the element with data-module attribute
        var target = e.target.closest('[data-module]');
        if (!target) return;
        
        var moduleName = target.getAttribute('data-module');
        var method = target.getAttribute('data-method');
        var arg = target.getAttribute('data-arg');
        
        if (!moduleName || !method) return;
        
        console.log('🖱️ Click:', moduleName, method, arg);
        
        // Parse argument if it's a number
        var argValue = arg;
        if (arg && !isNaN(arg)) {
            argValue = parseInt(arg, 10);
        }
        
        // Check if module exists and has the method
        if (window[moduleName] && typeof window[moduleName][method] === 'function') {
            console.log('✅ Calling:', moduleName, method, argValue);
            window[moduleName][method](argValue);
        } else {
            console.warn('⚠️ Module not ready:', moduleName, method, 'typeof:', typeof window[moduleName]);
            e.preventDefault();
        }
    }
    
    // Add event delegation when DOM is ready
    function init() {
        console.log('🔧 Event delegation init');
        document.addEventListener('click', handleModuleClick);
        console.log('✅ Event delegation active for data-module');
    }
    
    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
