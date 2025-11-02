// ===== Folder Tree Manager =====
class FolderTreeManager {
    constructor(options = {}) {
        this.container = options.container || document.querySelector('.folder-tree');
        this.viewToggle = options.viewToggle || document.querySelector('.filter__view-toggle');
        this.searchInput = options.searchInput || document.getElementById('searchResults');
        this.sortSelect = options.sortSelect || document.getElementById('sortResults');
        this.refreshButton = options.refreshButton || document.getElementById('refreshBtn');
        this.cleanupButton = options.cleanupButton || document.getElementById('cleanupBtn');
        
        this.currentView = 'grid'; // 'grid' | 'list'
        this.currentSort = 'date-desc';
        this.currentSearch = '';
        this.selectedItem = null;
        this.expandedFolders = new Set();
        
        this.data = [];
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadSampleData();
        this.render();
    }
    
    bindEvents() {
        // View toggle buttons
        if (this.viewToggle) {
            this.viewToggle.addEventListener('click', (e) => {
                const button = e.target.closest('.filter__view-button');
                if (button) {
                    this.handleViewChange(button.dataset.view);
                }
            });
        }
        
        // Search input
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.handleSearchChange(e.target.value);
            });
        }
        
        // Sort select
        if (this.sortSelect) {
            this.sortSelect.addEventListener('change', (e) => {
                this.handleSortChange(e.target.value);
            });
        }
        
        // Refresh button
        if (this.refreshButton) {
            this.refreshButton.addEventListener('click', () => {
                this.handleRefresh();
            });
        }
        
        // Cleanup button
        if (this.cleanupButton) {
            this.cleanupButton.addEventListener('click', () => {
                this.handleCleanup();
            });
        }
        
        // Delegate events for folder tree items
        this.container.addEventListener('click', (e) => {
            const item = e.target.closest('.folder-tree__item');
            const toggle = e.target.closest('.folder-tree__toggle');
            const actionButton = e.target.closest('.folder-tree__actions .button');
            
            if (item) {
                this.handleItemClick(item, e);
            }
            
            if (toggle) {
                this.handleToggleClick(toggle, item);
            }
            
            if (actionButton) {
                this.handleActionClick(actionButton, item);
            }
        });
    }
    
    handleViewChange(view) {
        this.currentView = view;
        
        // Update active button state
        const buttons = this.viewToggle.querySelectorAll('.filter__view-button');
        buttons.forEach(btn => btn.classList.remove('filter__view-button--active'));
        const activeButton = this.viewToggle.querySelector(`[data-view="${view}"]`);
        if (activeButton) {
            activeButton.classList.add('filter__view-button--active');
        }
        
        this.render();
    }
    
    handleSearchChange(searchTerm) {
        this.currentSearch = searchTerm.toLowerCase().trim();
        this.render();
    }
    
    handleSortChange(sortValue) {
        this.currentSort = sortValue;
        this.render();
    }
    
    handleRefresh() {
        // Simulate API call
        this.showLoadingState();
        
        setTimeout(() => {
            this.loadSampleData();
            this.render();
            this.hideLoadingState();
            
            // Show success message
            this.showNotification('Данные успешно обновлены', 'success');
        }, 1000);
    }
    
    handleCleanup() {
        const oldItems = this.data.filter(item => {
            const itemDate = new Date(item.modified);
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            return itemDate < thirtyDaysAgo;
        });
        
        if (oldItems.length === 0) {
            this.showNotification('Нет старых файлов для очистки', 'info');
            return;
        }
        
        // Show confirmation dialog
        this.showCleanupConfirmation(oldItems);
    }
    
    handleItemClick(item, event) {
        // Don't trigger if clicking on actions or toggle
        if (event.target.closest('.folder-tree__actions') || 
            event.target.closest('.folder-tree__toggle')) {
            return;
        }
        
        const itemId = item.dataset.id;
        const itemData = this.findItemById(itemId);
        
        if (!itemData) return;
        
        // Toggle selection
        if (this.selectedItem === itemId) {
            this.selectedItem = null;
            item.classList.remove('folder-tree__item--selected');
        } else {
            // Remove selection from previous item
            const previouslySelected = this.container.querySelector('.folder-tree__item--selected');
            if (previouslySelected) {
                previouslySelected.classList.remove('folder-tree__item--selected');
            }
            
            this.selectedItem = itemId;
            item.classList.add('folder-tree__item--selected');
        }
        
        // If it's a folder, toggle expansion on double click
        if (event.detail === 2 && itemData.type === 'folder') {
            this.toggleFolder(itemId);
        }
    }
    
    handleToggleClick(toggle, item) {
        const itemId = item.dataset.id;
        this.toggleFolder(itemId);
    }
    
    handleActionClick(button, item) {
        const itemId = item.dataset.id;
        const itemData = this.findItemById(itemId);
        const action = button.textContent.trim().toLowerCase();
        
        switch (action) {
            case 'открыть':
                this.openItem(itemData);
                break;
            case 'удалить':
                this.deleteItem(itemData);
                break;
            case 'скачать':
                this.downloadItem(itemData);
                break;
            case 'переименовать':
                this.renameItem(itemData);
                break;
        }
    }
    
    toggleFolder(folderId) {
        if (this.expandedFolders.has(folderId)) {
            this.expandedFolders.delete(folderId);
        } else {
            this.expandedFolders.add(folderId);
        }
        this.render();
    }
    
    openItem(item) {
        if (item.type === 'folder') {
            this.toggleFolder(item.id);
            this.showNotification(`Папка "${item.name}" открыта`, 'success');
        } else {
            this.showNotification(`Файл "${item.name}" открыт`, 'success');
        }
    }
    
    deleteItem(item) {
        // Use the dialog manager from previous example
        if (window.dialogManager) {
            window.dialogManager.showConfirm(
                'Удаление',
                `Вы уверены, что хотите удалить "${item.name}"?`,
                'warning'
            ).then(confirmed => {
                if (confirmed) {
                    this.removeItemById(item.id);
                    this.render();
                    this.showNotification(`"${item.name}" удален`, 'success');
                }
            });
        } else {
            // Fallback to native confirm
            if (confirm(`Удалить "${item.name}"?`)) {
                this.removeItemById(item.id);
                this.render();
                this.showNotification(`"${item.name}" удален`, 'success');
            }
        }
    }
    
    downloadItem(item) {
        this.showNotification(`Начато скачивание "${item.name}"`, 'info');
        // Simulate download
        setTimeout(() => {
            this.showNotification(`"${item.name}" успешно скачан`, 'success');
        }, 2000);
    }
    
    renameItem(item) {
        const newName = prompt('Введите новое имя:', item.name);
        if (newName && newName.trim() !== '') {
            const originalName = item.name;
            item.name = newName.trim();
            this.render();
            this.showNotification(`"${originalName}" переименован в "${item.name}"`, 'success');
        }
    }
    
    // Data management methods
    findItemById(id, items = this.data) {
        for (const item of items) {
            if (item.id === id) return item;
            if (item.children) {
                const found = this.findItemById(id, item.children);
                if (found) return found;
            }
        }
        return null;
    }
    
    removeItemById(id, items = this.data) {
        for (let i = 0; i < items.length; i++) {
            if (items[i].id === id) {
                return items.splice(i, 1)[0];
            }
            if (items[i].children) {
                const removed = this.removeItemById(id, items[i].children);
                if (removed) return removed;
            }
        }
        return null;
    }
    
    filterItems(items = this.data) {
        if (!this.currentSearch) return items;
        
        return items.filter(item => {
            const matches = item.name.toLowerCase().includes(this.currentSearch);
            
            // If it's a folder and has children, check children too
            if (item.children && item.children.length > 0) {
                item.children = this.filterItems(item.children);
                return matches || item.children.length > 0;
            }
            
            return matches;
        });
    }
    
    sortItems(items = this.data) {
        const sorted = [...items];
        
        sorted.sort((a, b) => {
            switch (this.currentSort) {
                case 'date-desc':
                    return new Date(b.modified) - new Date(a.modified);
                case 'date-asc':
                    return new Date(a.modified) - new Date(b.modified);
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'status':
                    return (a.status || '').localeCompare(b.status || '');
                default:
                    return 0;
            }
        });
        
        // Sort children recursively
        sorted.forEach(item => {
            if (item.children && item.children.length > 0) {
                item.children = this.sortItems(item.children);
            }
        });
        
        return sorted;
    }
    
    // Rendering methods
    render() {
        const filteredData = this.filterItems();
        const sortedData = this.sortItems(filteredData);
        
        this.container.className = 'folder-tree';
        this.container.classList.add(`folder-tree--${this.currentView}`);
        
        if (sortedData.length === 0) {
            this.renderEmptyState();
        } else {
            this.container.innerHTML = this.renderItems(sortedData);
        }
    }
    
    renderItems(items, level = 0) {
        return items.map(item => {
            const isExpanded = this.expandedFolders.has(item.id);
            const hasChildren = item.children && item.children.length > 0;
            const isSelected = this.selectedItem === item.id;
            
            const itemClasses = [
                'folder-tree__item',
                isSelected && 'folder-tree__item--selected',
                !hasChildren && item.type === 'folder' && 'folder-tree__item--empty'
            ].filter(Boolean).join(' ');
            
            return `
                <div class="${itemClasses}" data-id="${item.id}">
                    ${hasChildren ? `
                        <button class="folder-tree__toggle ${isExpanded ? 'folder-tree__toggle--expanded' : ''}">
                            ▶
                        </button>
                    ` : '<div style="width: 24px;"></div>'}
                    
                    <div class="folder-tree__icon folder-tree__icon--${item.type}">
                        ${this.getIconForType(item.type)}
                    </div>
                    
                    <div class="folder-tree__info">
                        <div class="folder-tree__name">${this.escapeHtml(item.name)}</div>
                        <div class="folder-tree__meta">
                            <span class="folder-tree__size">${this.formatFileSize(item.size)}</span>
                            <span class="folder-tree__date">${this.formatDate(item.modified)}</span>
                            ${item.status ? `<span class="folder-tree__status folder-tree__status--${item.status}">${this.getStatusText(item.status)}</span>` : ''}
                        </div>
                    </div>
                    
                    <div class="folder-tree__actions">
                        ${this.renderActions(item)}
                    </div>
                </div>
                ${hasChildren && isExpanded ? `
                    <div class="folder-tree__children">
                        ${this.renderItems(item.children, level + 1)}
                    </div>
                ` : ''}
            `;
        }).join('');
    }
    
    renderActions(item) {
        const actions = [];
        
        if (item.type === 'folder') {
            actions.push('<button class="button button--small button--secondary">Открыть</button>');
        } else {
            actions.push('<button class="button button--small button--primary">Скачать</button>');
        }
        
        actions.push('<button class="button button--small button--secondary">Переименовать</button>');
        actions.push('<button class="button button--small button--danger">Удалить</button>');
        
        return actions.join('');
    }
    
    renderEmptyState() {
        this.container.innerHTML = `
            <div class="folder-tree__empty">
                <div class="folder-tree__empty-icon">📁</div>
                <div class="folder-tree__empty-text">Папки не найдены</div>
                <p>Попробуйте изменить параметры поиска или обновить данные</p>
                <button class="button button--primary" onclick="folderTreeManager.handleRefresh()">
                    Обновить данные
                </button>
            </div>
        `;
    }
    
    // Utility methods
    getIconForType(type) {
        const icons = {
            folder: '📁',
            file: '📄',
            archive: '🗜️',
            image: '🖼️'
        };
        return icons[type] || '📄';
    }
    
    getStatusText(status) {
        const statusTexts = {
            success: 'Активна',
            warning: 'Внимание',
            error: 'Ошибка',
            info: 'Инфо'
        };
        return statusTexts[status] || status;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatDate(date) {
        return new Date(date).toLocaleDateString('ru-RU');
    }
    
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    showLoadingState() {
        this.container.innerHTML = `
            <div class="folder-tree__empty">
                <div class="folder-tree__empty-icon">⏳</div>
                <div class="folder-tree__empty-text">Загрузка данных...</div>
            </div>
        `;
    }
    
    hideLoadingState() {
        // Handled by render()
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.innerHTML = `
            <div class="notification__content">
                <span class="notification__message">${message}</span>
                <button class="notification__close">&times;</button>
            </div>
        `;
        
        // Add styles if not already added
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 1001;
                    animation: notificationSlideIn 0.3s ease;
                }
                .notification__content {
                    background: white;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    min-width: 300px;
                }
                .notification--success { border-left: 4px solid #10B981; }
                .notification--error { border-left: 4px solid #EF4444; }
                .notification--warning { border-left: 4px solid #F59E0B; }
                .notification--info { border-left: 4px solid #3B82F6; }
                .notification__close {
                    background: none;
                    border: none;
                    font-size: 1.2rem;
                    cursor: pointer;
                    margin-left: auto;
                }
                @keyframes notificationSlideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'notificationSlideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
        
        // Close on button click
        notification.querySelector('.notification__close').addEventListener('click', () => {
            notification.remove();
        });
    }
    
    showCleanupConfirmation(oldItems) {
        const totalSize = oldItems.reduce((sum, item) => sum + item.size, 0);
        const message = `
            <p>Будет удалено ${oldItems.length} старых файлов и папок.</p>
            <p>Общий размер: <strong>${this.formatFileSize(totalSize)}</strong></p>
            <p style="color: #EF4444; margin-top: 1rem;">Это действие нельзя отменить.</p>
        `;
        
        if (window.dialogManager) {
            window.dialogManager.showConfirm(
                'Очистка старых файлов',
                message,
                'warning'
            ).then(confirmed => {
                if (confirmed) {
                    this.performCleanup(oldItems);
                }
            });
        } else {
            if (confirm(`Удалить ${oldItems.length} старых файлов?`)) {
                this.performCleanup(oldItems);
            }
        }
    }
    
    performCleanup(oldItems) {
        oldItems.forEach(item => {
            this.removeItemById(item.id);
        });
        
        this.render();
        this.showNotification(`Удалено ${oldItems.length} старых файлов`, 'success');
    }
    
    // Sample data for demonstration
    loadSampleData() {
        this.data = [
            {
                id: '1',
                name: 'project-backup-2024',
                type: 'folder',
                size: 256000000,
                modified: new Date('2024-01-15'),
                status: 'success',
                children: [
                    {
                        id: '1-1',
                        name: 'src',
                        type: 'folder',
                        size: 128000000,
                        modified: new Date('2024-01-14'),
                        children: [
                            {
                                id: '1-1-1',
                                name: 'main.js',
                                type: 'file',
                                size: 1024000,
                                modified: new Date('2024-01-14')
                            }
                        ]
                    },
                    {
                        id: '1-2',
                        name: 'package.json',
                        type: 'file',
                        size: 2048,
                        modified: new Date('2024-01-13')
                    }
                ]
            },
            {
                id: '2',
                name: 'archive-2023',
                type: 'archive',
                size: 512000000,
                modified: new Date('2023-12-20'),
                status: 'warning'
            },
            {
                id: '3',
                name: 'screenshots',
                type: 'folder',
                size: 128000000,
                modified: new Date('2024-01-10'),
                children: [
                    {
                        id: '3-1',
                        name: 'dashboard.png',
                        type: 'image',
                        size: 2560000,
                        modified: new Date('2024-01-10')
                    }
                ]
            }
        ];
    }
}

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', function() {
    const folderTreeManager = new FolderTreeManager();
    window.folderTreeManager = folderTreeManager;
    
    // Make it globally available for HTML onclick handlers
    window.folderTreeManager = folderTreeManager;
});

