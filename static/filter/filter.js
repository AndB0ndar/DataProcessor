// ===== Filter Component JavaScript =====

class FilterManager {
    constructor(options = {}) {
        this.filterContainer = options.filterContainer || document.querySelector('.filter');
        this.contentPanel = options.contentPanel || document.getElementById('logsContent');
        this.searchInput = options.searchInput || document.getElementById('searchLogs');
        this.autoScrollCheckbox = options.autoScrollCheckbox || document.getElementById('autoScroll');
        this.clearButton = options.clearButton || document.getElementById('clearLogsBtn');
        this.exportButton = options.exportButton || document.getElementById('exportLogsBtn');
        
        // Counters
        this.infoCount = options.infoCount || document.getElementById('infoCount');
        this.warningCount = options.warningCount || document.getElementById('warningCount');
        this.errorCount = options.errorCount || document.getElementById('errorCount');
        this.debugCount = options.debugCount || document.getElementById('debugCount');
        
        this.currentFilter = 'all';
        this.currentSearch = '';
        this.autoScrollEnabled = true;
        this.items = [];
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadInitialData();
        this.updateCounters();
    }
    
    bindEvents() {
        // Filter buttons
        const filterButtons = this.filterContainer.querySelectorAll('.filter__button');
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleFilterChange(e.target);
            });
        });
        
        // Search input
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.handleSearchChange(e.target.value);
            });
        }
        
        // Auto scroll checkbox
        if (this.autoScrollCheckbox) {
            this.autoScrollCheckbox.addEventListener('change', (e) => {
                this.autoScrollEnabled = e.target.checked;
            });
        }
        
        // Clear button
        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => {
                this.handleClear();
            });
        }
        
        // Export button
        if (this.exportButton) {
            this.exportButton.addEventListener('click', () => {
                this.handleExport();
            });
        }
    }
    
    handleFilterChange(button) {
        const level = button.dataset.level;
        
        // Update active state
        const allButtons = this.filterContainer.querySelectorAll('.filter__button');
        allButtons.forEach(btn => btn.classList.remove('filter__button--active'));
        button.classList.add('filter__button--active');
        
        this.currentFilter = level;
        this.applyFilters();
    }
    
    handleSearchChange(searchTerm) {
        this.currentSearch = searchTerm.toLowerCase().trim();
        this.applyFilters();
    }
    
    applyFilters() {
        const items = this.contentPanel.querySelectorAll('.content-panel__item');
        
        items.forEach(item => {
            const level = item.dataset.level;
            const message = item.querySelector('.content-panel__message').textContent.toLowerCase();
            const timestamp = item.querySelector('.content-panel__timestamp').textContent.toLowerCase();
            
            const levelMatch = this.currentFilter === 'all' || level === this.currentFilter;
            const searchMatch = !this.currentSearch || 
                               message.includes(this.currentSearch) || 
                               timestamp.includes(this.currentSearch);
            
            if (levelMatch && searchMatch) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
        
        this.scrollToBottom();
    }
    
    addItem(itemData) {
        const item = this.createItemElement(itemData);
        this.contentPanel.appendChild(item);
        this.items.push(itemData);
        
        this.updateCounters();
        this.scrollToBottom();
    }
    
    createItemElement(data) {
        const item = document.createElement('div');
        item.className = `content-panel__item`;
        item.dataset.level = data.level;
        
        item.innerHTML = `
            <div class="content-panel__timestamp">${this.formatTimestamp(data.timestamp)}</div>
            <div class="content-panel__badge content-panel__badge--${data.level}">${data.level.toUpperCase()}</div>
            <div class="content-panel__message">${this.escapeHtml(data.message)}</div>
        `;
        
        return item;
    }
    
    handleClear() {
        if (confirm('Вы уверены, что хотите очистить все логи?')) {
            this.contentPanel.innerHTML = '';
            this.items = [];
            this.updateCounters();
        }
    }
    
    handleExport() {
        const data = {
            timestamp: new Date().toISOString(),
            filters: {
                level: this.currentFilter,
                search: this.currentSearch
            },
            logs: this.items
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { 
            type: 'application/json' 
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `logs-export-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    updateCounters() {
        const counts = {
            info: 0,
            warning: 0,
            error: 0,
            debug: 0
        };
        
        this.items.forEach(item => {
            if (counts.hasOwnProperty(item.level)) {
                counts[item.level]++;
            }
        });
        
        if (this.infoCount) this.infoCount.textContent = counts.info;
        if (this.warningCount) this.warningCount.textContent = counts.warning;
        if (this.errorCount) this.errorCount.textContent = counts.error;
        if (this.debugCount) this.debugCount.textContent = counts.debug;
    }
    
    scrollToBottom() {
        if (this.autoScrollEnabled && this.contentPanel) {
            this.contentPanel.scrollTop = this.contentPanel.scrollHeight;
        }
    }
    
    formatTimestamp(timestamp) {
        if (timestamp instanceof Date) {
            return timestamp.toLocaleString('ru-RU');
        }
        return timestamp;
    }
    
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    loadInitialData() {
        // Пример начальных данных для демонстрации
        const initialData = [
            {
                timestamp: new Date(),
                level: 'info',
                message: 'Система инициализирована'
            },
            {
                timestamp: new Date(Date.now() - 1000),
                level: 'warning',
                message: 'Обнаружена неоптимальная конфигурация'
            },
            {
                timestamp: new Date(Date.now() - 2000),
                level: 'error',
                message: 'Ошибка загрузки модуля обработки'
            },
            {
                timestamp: new Date(Date.now() - 3000),
                level: 'debug',
                message: 'Отладочная информация: память 256MB'
            }
        ];
        
        initialData.forEach(data => this.addItem(data));
    }
    
    // Public methods for external use
    addLog(level, message) {
        this.addItem({
            timestamp: new Date(),
            level: level,
            message: message
        });
    }
    
    setFilter(level) {
        const button = this.filterContainer.querySelector(`[data-level="${level}"]`);
        if (button) {
            this.handleFilterChange(button);
        }
    }
    
    setSearch(term) {
        if (this.searchInput) {
            this.searchInput.value = term;
            this.handleSearchChange(term);
        }
    }
}

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', function() {
    const filterManager = new FilterManager();
    
    // Пример добавления логов через внешние события
    setTimeout(() => {
        filterManager.addLog('info', 'Загрузка данных завершена успешно');
    }, 2000);
    
    setTimeout(() => {
        filterManager.addLog('warning', 'Обнаружены дублирующиеся записи');
    }, 4000);
    
    // Глобальный доступ для демонстрации
    window.filterManager = filterManager;
});

// ===== Advanced Filter Features =====

// Дебаунс для поиска (опционально)
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Расширенный класс с дополнительными функциями
class AdvancedFilterManager extends FilterManager {
    constructor(options = {}) {
        super(options);
        this.debouncedSearch = debounce(this.handleSearchChange.bind(this), 300);
        this.highlightedItems = new Set();
        
        this.initAdvancedFeatures();
    }
    
    initAdvancedFeatures() {
        // Дебаунс для поиска
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.debouncedSearch(e.target.value);
            });
        }
        
        // Сохранение состояния в localStorage
        this.loadState();
        window.addEventListener('beforeunload', () => this.saveState());
    }
    
    handleSearchChange(searchTerm) {
        this.currentSearch = searchTerm.toLowerCase().trim();
        
        // Убираем предыдущее выделение
        this.removeHighlights();
        
        if (this.currentSearch) {
            this.highlightSearchTerms();
        }
        
        this.applyFilters();
    }
    
    highlightSearchTerms() {
        const items = this.contentPanel.querySelectorAll('.content-panel__item');
        const searchTerm = this.currentSearch;
        
        items.forEach(item => {
            const messageElement = item.querySelector('.content-panel__message');
            const originalText = messageElement.textContent;
            
            if (originalText.toLowerCase().includes(searchTerm)) {
                const highlightedText = originalText.replace(
                    new RegExp(searchTerm, 'gi'),
                    match => `<mark class="filter__highlight">${match}</mark>`
                );
                
                messageElement.innerHTML = highlightedText;
                this.highlightedItems.add(messageElement);
            }
        });
    }
    
    removeHighlights() {
        this.highlightedItems.forEach(element => {
            if (element.innerHTML.includes('<mark')) {
                element.innerHTML = element.textContent;
            }
        });
        this.highlightedItems.clear();
    }
    
    saveState() {
        const state = {
            filter: this.currentFilter,
            search: this.currentSearch,
            autoScroll: this.autoScrollEnabled
        };
        
        localStorage.setItem('filterManagerState', JSON.stringify(state));
    }
    
    loadState() {
        const saved = localStorage.getItem('filterManagerState');
        if (saved) {
            try {
                const state = JSON.parse(saved);
                this.currentFilter = state.filter || 'all';
                this.currentSearch = state.search || '';
                this.autoScrollEnabled = state.autoScroll !== false;
                
                // Применяем восстановленные настройки
                if (this.searchInput) {
                    this.searchInput.value = this.currentSearch;
                }
                if (this.autoScrollCheckbox) {
                    this.autoScrollCheckbox.checked = this.autoScrollEnabled;
                }
                
                const activeButton = this.filterContainer.querySelector(`[data-level="${this.currentFilter}"]`);
                if (activeButton) {
                    this.handleFilterChange(activeButton);
                }
            } catch (e) {
                console.warn('Failed to load filter state:', e);
            }
        }
    }
}

// Альтернативная инициализация с расширенными функциями
document.addEventListener('DOMContentLoaded', function() {
    // Используйте AdvancedFilterManager для расширенных функций
    const advancedFilterManager = new AdvancedFilterManager();
    window.filterManager = advancedFilterManager;
});
