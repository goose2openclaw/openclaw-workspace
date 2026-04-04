/* GO2SE Platform v11 - Router Module */

// Router is already defined in app.js
// This file extends the router with additional utilities

Router.extend = function(extensions) {
    Object.assign(this, extensions);
};

// History management
Router.History = {
    stack: ['dashboard'],
    maxSize: 50,
    
    push(page) {
        if (this.stack[this.stack.length - 1] !== page) {
            this.stack.push(page);
            if (this.stack.length > this.maxSize) {
                this.stack.shift();
            }
        }
    },
    
    back() {
        if (this.stack.length > 1) {
            this.stack.pop();
            return this.stack[this.stack.length - 1];
        }
        return null;
    },
    
    canBack() {
        return this.stack.length > 1;
    }
};

// Deep link generator
Router.generateLink = function(page, params = {}) {
    const query = Object.entries(params)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join('&');
    return `#${page}${query ? '?' + query : ''}`;
};

// Parse current route with params
Router.parseRoute = function() {
    const hash = window.location.hash.slice(1);
    const [path, queryString] = hash.split('?');
    const params = {};
    
    if (queryString) {
        queryString.split('&').forEach(pair => {
            const [key, value] = pair.split('=');
            params[decodeURIComponent(key)] = decodeURIComponent(value);
        });
    }
    
    return {
        page: path || 'dashboard',
        params
    };
};

// Prefetch pages
Router.prefetch = function(pages = []) {
    pages.forEach(page => {
        if (!this.routes[page]) return;
        // Preload page content in memory
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = `js/pages/${page}.js`;
        document.head.appendChild(link);
    });
};

// Navigate with transition
Router.navigateWithTransition = function(page) {
    Router.History.push(page);
    
    const content = document.getElementById('page-content');
    content.style.opacity = '0';
    content.style.transform = 'translateX(20px)';
    
    setTimeout(() => {
        this.navigate(page);
    }, 200);
};

// Navigate with data
Router.navigateWithData = function(page, data) {
    sessionStorage.setItem('pageData_' + page, JSON.stringify(data));
    this.navigate(page);
};

// Get passed data
Router.getPassedData = function(page) {
    const data = sessionStorage.getItem('pageData_' + page);
    return data ? JSON.parse(data) : null;
};

// Clear passed data
Router.clearPassedData = function(page) {
    sessionStorage.removeItem('pageData_' + page);
};
