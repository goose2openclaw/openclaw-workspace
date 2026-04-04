/* GO2SE Platform v11 - Reusable Components */

// ========== Modal Component ==========
const Modal = {
    show(title, content, options = {}) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        
        const buttons = options.buttons || [
            { text: '取消', class: 'btn-secondary', action: 'close' },
            { text: '确定', class: 'btn-primary', action: 'confirm' }
        ];
        
        overlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="modal-close">×</button>
                </div>
                <div class="modal-body">${content}</div>
                <div class="modal-footer">
                    ${buttons.map(btn => `
                        <button class="btn ${btn.class}" data-action="${btn.action}">${btn.text}</button>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Bind events
        overlay.querySelector('.modal-close').addEventListener('click', () => this.close(overlay));
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) this.close(overlay);
        });
        
        buttons.forEach(btn => {
            overlay.querySelector(`[data-action="${btn.action}"]`).addEventListener('click', () => {
                if (btn.action === 'close') {
                    this.close(overlay);
                } else if (btn.onClick) {
                    btn.onClick();
                } else {
                    this.close(overlay);
                    if (options.onConfirm) options.onConfirm();
                }
            });
        });
        
        // Animation
        requestAnimationFrame(() => overlay.classList.add('open'));
        
        return overlay;
    },
    
    close(overlay) {
        overlay.classList.remove('open');
        setTimeout(() => overlay.remove(), 300);
    }
};

// ========== Confirm Dialog ==========
const Confirm = {
    show(message, onConfirm, onCancel) {
        Modal.show('确认操作', `<p>${message}</p>`, {
            buttons: [
                { text: '取消', class: 'btn-secondary', action: 'cancel', onClick: onCancel },
                { text: '确认', class: 'btn-primary', action: 'confirm', onClick: onConfirm }
            ]
        });
    }
};

// ========== Alert Component ==========
const Alert = {
    show(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert ${type}`;
        
        const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
        
        alert.innerHTML = `
            <span class="alert-icon">${icons[type]}</span>
            <div class="alert-content">
                <div class="alert-message">${message}</div>
            </div>
        `;
        
        return alert;
    }
};

// ========== Dropdown Component ==========
const Dropdown = {
    create(trigger, items, onSelect) {
        const dropdown = document.createElement('div');
        dropdown.className = 'dropdown';
        
        dropdown.innerHTML = `<div class="dropdown-menu"></div>`;
        
        const menu = dropdown.querySelector('.dropdown-menu');
        items.forEach(item => {
            if (item.divider) {
                menu.innerHTML += '<div class="dropdown-divider"></div>';
            } else {
                const el = document.createElement('div');
                el.className = 'dropdown-item';
                el.innerHTML = `
                    ${item.icon ? `<span>${item.icon}</span>` : ''}
                    <span>${item.label}</span>
                `;
                el.addEventListener('click', () => {
                    onSelect(item);
                    dropdown.classList.remove('open');
                });
                menu.appendChild(el);
            }
        });
        
        trigger.parentNode.insertBefore(dropdown, trigger.nextSibling);
        dropdown.insertBefore(trigger, dropdown.firstChild);
        
        trigger.addEventListener('click', () => {
            dropdown.classList.toggle('open');
        });
        
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });
        
        return dropdown;
    }
};

// ========== Tabs Component ==========
const Tabs = {
    init(container) {
        const tabs = container.querySelectorAll('.tab');
        const contents = container.querySelectorAll('.tab-content');
        
        tabs.forEach((tab, index) => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                
                tab.classList.add('active');
                if (contents[index]) {
                    contents[index].classList.add('active');
                }
            });
        });
    }
};

// ========== Pagination Component ==========
const Pagination = {
    create(options = {}) {
        const { total = 1, current = 1, onChange } = options;
        const container = document.createElement('div');
        container.className = 'pagination';
        
        const totalPages = Math.ceil(total);
        
        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.innerHTML = '‹';
        prevBtn.disabled = current <= 1;
        prevBtn.addEventListener('click', () => {
            if (current > 1 && onChange) onChange(current - 1);
        });
        container.appendChild(prevBtn);
        
        // Page numbers
        const maxVisible = 5;
        let start = Math.max(1, current - Math.floor(maxVisible / 2));
        let end = Math.min(totalPages, start + maxVisible - 1);
        
        if (end - start + 1 < maxVisible) {
            start = Math.max(1, end - maxVisible + 1);
        }
        
        if (start > 1) {
            const firstBtn = document.createElement('button');
            firstBtn.textContent = '1';
            firstBtn.addEventListener('click', () => onChange && onChange(1));
            container.appendChild(firstBtn);
            
            if (start > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.textContent = '...';
                ellipsis.style.padding = '0 8px';
                container.appendChild(ellipsis);
            }
        }
        
        for (let i = start; i <= end; i++) {
            const btn = document.createElement('button');
            btn.textContent = i;
            if (i === current) btn.classList.add('active');
            btn.addEventListener('click', () => onChange && onChange(i));
            container.appendChild(btn);
        }
        
        if (end < totalPages) {
            if (end < totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.textContent = '...';
                ellipsis.style.padding = '0 8px';
                container.appendChild(ellipsis);
            }
            
            const lastBtn = document.createElement('button');
            lastBtn.textContent = totalPages;
            lastBtn.addEventListener('click', () => onChange && onChange(totalPages));
            container.appendChild(lastBtn);
        }
        
        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.innerHTML = '›';
        nextBtn.disabled = current >= totalPages;
        nextBtn.addEventListener('click', () => {
            if (current < totalPages && onChange) onChange(current + 1);
        });
        container.appendChild(nextBtn);
        
        return container;
    }
};

// ========== Search Component ==========
const Search = {
    create(placeholder = '搜索...', onSearch) {
        const container = document.createElement('div');
        container.className = 'search-box';
        
        container.innerHTML = `
            <span class="search-icon">🔍</span>
            <input type="text" class="search-input" placeholder="${placeholder}">
        `;
        
        const input = container.querySelector('input');
        let timeout;
        
        input.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                if (onSearch) onSearch(input.value);
            }, 300);
        });
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && onSearch) {
                clearTimeout(timeout);
                onSearch(input.value);
            }
        });
        
        return container;
    }
};

// ========== Filter Component ==========
const Filter = {
    create(filters, onFilter) {
        const container = document.createElement('div');
        container.className = 'filter-bar';
        
        filters.forEach(filter => {
            const group = document.createElement('div');
            group.className = 'filter-group';
            
            if (filter.label) {
                const label = document.createElement('span');
                label.className = 'filter-label';
                label.textContent = filter.label;
                group.appendChild(label);
            }
            
            if (filter.type === 'select') {
                const select = document.createElement('select');
                select.className = 'filter-input form-select';
                filter.options.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt.value;
                    option.textContent = opt.label;
                    select.appendChild(option);
                });
                select.addEventListener('change', () => onFilter(filter.name, select.value));
                group.appendChild(select);
            } else if (filter.type === 'date') {
                const input = document.createElement('input');
                input.type = 'date';
                input.className = 'filter-input';
                input.addEventListener('change', () => onFilter(filter.name, input.value));
                group.appendChild(input);
            } else {
                const input = document.createElement('input');
                input.type = 'text';
                input.className = 'filter-input';
                input.placeholder = filter.placeholder || '';
                input.addEventListener('input', () => onFilter(filter.name, input.value));
                group.appendChild(input);
            }
            
            container.appendChild(group);
        });
        
        return container;
    }
};

// ========== Loading Spinner ==========
const Spinner = {
    create(size = 'md') {
        const spinner = document.createElement('div');
        spinner.className = `spinner${size === 'sm' ? '-sm' : size === 'lg' ? '-lg' : ''}`;
        return spinner;
    },
    
    show(message = '加载中...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner spinner-lg"></div>
            <p>${message}</p>
        `;
        document.body.appendChild(overlay);
        return overlay;
    },
    
    hide(overlay) {
        overlay.remove();
    }
};

// ========== Empty State ==========
const EmptyState = {
    create(icon = '📭', title = '暂无数据', message = '') {
        const state = document.createElement('div');
        state.className = 'empty-state';
        state.innerHTML = `
            <div class="empty-state-icon">${icon}</div>
            <div class="empty-state-title">${title}</div>
            ${message ? `<p>${message}</p>` : ''}
        `;
        return state;
    }
};

// ========== Progress Ring ==========
const ProgressRing = {
    create(value, options = {}) {
        const { size = 100, strokeWidth = 8, color = 'var(--accent-primary)' } = options;
        
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', size);
        svg.setAttribute('height', size);
        svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
        
        const radius = (size - strokeWidth) / 2;
        const circumference = radius * 2 * Math.PI;
        
        svg.innerHTML = `
            <circle
                cx="${size/2}" cy="${size/2}" r="${radius}"
                fill="none"
                stroke="var(--bg-tertiary)"
                stroke-width="${strokeWidth}"
            />
            <circle
                cx="${size/2}" cy="${size/2}" r="${radius}"
                fill="none"
                stroke="${color}"
                stroke-width="${strokeWidth}"
                stroke-linecap="round"
                stroke-dasharray="${circumference}"
                stroke-dashoffset="${circumference - (value / 100) * circumference}"
                transform="rotate(-90 ${size/2} ${size/2})"
                style="transition: stroke-dashoffset 0.5s ease"
            />
        `;
        
        return svg;
    }
};

// ========== Tooltip ==========
const Tooltip = {
    create(target, content, position = 'top') {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = content;
        tooltip.setAttribute('data-tooltip', content);
        target.setAttribute('data-tooltip', content);
        return tooltip;
    }
};

// ========== Table Builder ==========
const Table = {
    create(columns, data, options = {}) {
        const container = document.createElement('div');
        container.className = 'table-container';
        
        const table = document.createElement('table');
        
        // Header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col.label;
            if (col.width) th.style.width = col.width;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Body
        const tbody = document.createElement('tbody');
        data.forEach(row => {
            const tr = document.createElement('tr');
            columns.forEach(col => {
                const td = document.createElement('td');
                if (col.render) {
                    td.innerHTML = col.render(row[col.key], row);
                } else {
                    td.textContent = row[col.key];
                }
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        
        container.appendChild(table);
        return container;
    }
};

// Export components
window.Modal = Modal;
window.Confirm = Confirm;
window.Alert = Alert;
window.Dropdown = Dropdown;
window.Tabs = Tabs;
window.Pagination = Pagination;
window.Search = Search;
window.Filter = Filter;
window.Spinner = Spinner;
window.EmptyState = EmptyState;
window.ProgressRing = ProgressRing;
window.Tooltip = Tooltip;
window.Table = Table;
