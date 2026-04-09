// EARLY LOAD: Module stub functions to prevent "not defined" errors
// This loads BEFORE other scripts to ensure functions are always available

window.TradingModules = window.TradingModules || { 
    navigateToLevel: function(l) { console.log('TradingModules pending...', l); },
    navigateLevel: function(l) { console.log('TradingModules pending...', l); },
    init: function() { console.log('TradingModules pending init...'); }
};

window.TradingPanel = window.TradingPanel || { 
    navigateLevel: function(l) { console.log('TradingPanel pending...', l); },
    init: function() { console.log('TradingPanel pending init...'); },
    closePanel: function() {}
};

window.MacroMicro = window.MacroMicro || { 
    navigateLevel: function(l) { console.log('MacroMicro pending...', l); },
    init: function() { console.log('MacroMicro pending init...'); },
    closePanel: function() {}
};

// NOTE: Module stubs removed - real modules are loaded from separate JS files
// and will override these if they exist

console.log('🔧 Early helpers loaded');
