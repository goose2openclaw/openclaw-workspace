/* GO2SE Platform v11 - Interaction Handlers */

// ========== Drag and Drop ==========
const DragDrop = {
    init() {
        document.querySelectorAll('[draggable]').forEach(el => {
            el.addEventListener('dragstart', this.handleDragStart);
            el.addEventListener('dragend', this.handleDragEnd);
        });
        
        document.querySelectorAll('[droptarget]').forEach(el => {
            el.addEventListener('dragover', this.handleDragOver);
            el.addEventListener('drop', this.handleDrop);
            el.addEventListener('dragleave', this.handleDragLeave);
        });
    },
    
    handleDragStart(e) {
        e.target.classList.add('dragging');
        e.dataTransfer.setData('text/plain', e.target.dataset.id || '');
        e.dataTransfer.effectAllowed = 'move';
    },
    
    handleDragEnd(e) {
        e.target.classList.remove('dragging');
    },
    
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('drag-over');
    },
    
    handleDragLeave(e) {
        e.currentTarget.classList.remove('drag-over');
    },
    
    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-over');
        
        const data = e.dataTransfer.getData('text/plain');
        if (e.currentTarget.dataset.onDrop) {
            const handler = new Function(e.currentTarget.dataset.onDrop + '(data)');
            handler(data);
        }
    }
};

// ========== Resize Handler ==========
const ResizeHandler = {
    observers: [],
    
    init() {
        this.update();
        window.addEventListener('resize', () => this.update());
    },
    
    update() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.notify();
    },
    
    observe(callback) {
        this.observers.push(callback);
    },
    
    notify() {
        this.observers.forEach(cb => cb(this.width, this.height));
    }
};

// ========== Scroll Handler ==========
const ScrollHandler = {
    init() {
        window.addEventListener('scroll', this.throttle(() => {
            this.scrollY = window.scrollY;
            this.scrollPercent = (this.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
        }, 100));
    },
    
    throttle(fn, wait) {
        let lastTime = 0;
        return function(...args) {
            const now = Date.now();
            if (now - lastTime >= wait) {
                lastTime = now;
                fn.apply(this, args);
            }
        };
    }
};

// ========== Copy to Clipboard ==========
const Clipboard = {
    async copy(text) {
        try {
            await navigator.clipboard.writeText(text);
            Toast.success('已复制到剪贴板');
            return true;
        } catch (err) {
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            Toast.success('已复制到剪贴板');
            return true;
        }
    }
};

// ========== Local Storage ==========
const Storage = {
    set(key, value) {
        try {
            localStorage.setItem('go2se_' + key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Storage error:', e);
            return false;
        }
    },
    
    get(key, defaultValue = null) {
        try {
            const value = localStorage.getItem('go2se_' + key);
            return value ? JSON.parse(value) : defaultValue;
        } catch (e) {
            return defaultValue;
        }
    },
    
    remove(key) {
        localStorage.removeItem('go2se_' + key);
    },
    
    clear() {
        Object.keys(localStorage)
            .filter(key => key.startsWith('go2se_'))
            .forEach(key => localStorage.removeItem(key));
    }
};

// ========== Theme Manager ==========
const ThemeManager = {
    themes: ['dark', 'light', 'neon', 'ocean', 'sunset', 'forest'],
    
    init() {
        const saved = Storage.get('theme', 'dark');
        this.setTheme(saved);
    },
    
    setTheme(theme) {
        if (!this.themes.includes(theme)) theme = 'dark';
        
        document.body.className = `skin-${theme}`;
        Storage.set('theme', theme);
        GO2SE.config.theme = theme;
    },
    
    getTheme() {
        return GO2SE.config.theme;
    },
    
    cycleTheme() {
        const current = this.themes.indexOf(this.getTheme());
        const next = (current + 1) % this.themes.length;
        this.setTheme(this.themes[next]);
        Toast.info(`主题已切换为: ${this.getTheme()}`);
    }
};

// ========== Notification Manager ==========
const NotificationManager = {
    queue: [],
    
    init() {
        this.load();
    },
    
    add(notification) {
        const id = Date.now();
        this.queue.push({ ...notification, id, read: false, timestamp: new Date() });
        this.save();
        this.updateBadge();
    },
    
    markRead(id) {
        const notif = this.queue.find(n => n.id === id);
        if (notif) {
            notif.read = true;
            this.save();
            this.updateBadge();
        }
    },
    
    markAllRead() {
        this.queue.forEach(n => n.read = true);
        this.save();
        this.updateBadge();
    },
    
    clear() {
        this.queue = [];
        this.save();
        this.updateBadge();
    },
    
    updateBadge() {
        const badge = document.getElementById('notification-badge');
        const unread = this.queue.filter(n => !n.read).length;
        badge.textContent = unread;
        badge.style.display = unread > 0 ? 'flex' : 'none';
    },
    
    save() {
        Storage.set('notifications', this.queue);
    },
    
    load() {
        this.queue = Storage.get('notifications', []);
        this.updateBadge();
    }
};

// ========== Refresh Manager ==========
const RefreshManager = {
    intervals: {},
    
    add(name, callback, interval = 30000) {
        if (this.intervals[name]) {
            clearInterval(this.intervals[name]);
        }
        this.intervals[name] = setInterval(callback, interval);
    },
    
    remove(name) {
        if (this.intervals[name]) {
            clearInterval(this.intervals[name]);
            delete this.intervals[name];
        }
    },
    
    removeAll() {
        Object.keys(this.intervals).forEach(name => this.remove(name));
    }
};

// ========== Export Manager ==========
const ExportManager = {
    toCSV(data, filename) {
        if (!data.length) return;
        
        const headers = Object.keys(data[0]);
        const csv = [
            headers.join(','),
            ...data.map(row => headers.map(h => `"${row[h]}"`).join(','))
        ].join('\n');
        
        this.download(csv, filename + '.csv', 'text/csv');
    },
    
    toJSON(data, filename) {
        const json = JSON.stringify(data, null, 2);
        this.download(json, filename + '.json', 'application/json');
    },
    
    download(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
};

// ========== Form Serializer ==========
const FormSerializer = {
    serialize(form) {
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        return data;
    },
    
    fill(form, data) {
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = data[key];
            }
        });
    },
    
    clear(form) {
        form.querySelectorAll('input, select, textarea').forEach(el => {
            if (el.type === 'checkbox' || el.type === 'radio') {
                el.checked = false;
            } else {
                el.value = '';
            }
        });
    }
};

// ========== Debounce & Throttle ==========
const Helpers = {
    debounce(fn, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn.apply(this, args), wait);
        };
    },
    
    throttle(fn, wait) {
        let lastTime = 0;
        return function(...args) {
            const now = Date.now();
            if (now - lastTime >= wait) {
                lastTime = now;
                fn.apply(this, args);
            }
        };
    },
    
    formatNumber(num, decimals = 2) {
        if (num === null || num === undefined) return '-';
        return Number(num).toLocaleString('zh-CN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },
    
    formatPercent(num, decimals = 2) {
        if (num === null || num === undefined) return '-';
        return (Number(num) * 100).toFixed(decimals) + '%';
    },
    
    formatCurrency(num, currency = 'USD') {
        if (num === null || num === undefined) return '-';
        return Number(num).toLocaleString('zh-CN', {
            style: 'currency',
            currency
        });
    },
    
    formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },
    
    truncate(str, length = 20) {
        if (!str) return '';
        if (str.length <= length) return str;
        return str.slice(0, length) + '...';
    }
};

// ========== Error Handler ==========
const ErrorHandler = {
    init() {
        window.addEventListener('error', (e) => {
            this.handle(e.error);
        });
        
        window.addEventListener('unhandledrejection', (e) => {
            this.handle(e.reason);
        });
    },
    
    handle(error) {
        console.error('Application Error:', error);
        Toast.error(error.message || '发生未知错误');
    }
};

// ========== Initialize All Interactions ==========
document.addEventListener('DOMContentLoaded', () => {
    DragDrop.init();
    ResizeHandler.init();
    ScrollHandler.init();
    ThemeManager.init();
    NotificationManager.init();
    ErrorHandler.init();
});

// Export
window.DragDrop = DragDrop;
window.ResizeHandler = ResizeHandler;
window.ScrollHandler = ScrollHandler;
window.Clipboard = Clipboard;
window.Storage = Storage;
window.ThemeManager = ThemeManager;
window.NotificationManager = NotificationManager;
window.RefreshManager = RefreshManager;
window.ExportManager = ExportManager;
window.FormSerializer = FormSerializer;
window.Helpers = Helpers;
window.ErrorHandler = ErrorHandler;
